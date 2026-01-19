"""
Fix Finder Service

A ReAct-based (Reason + Act) agent that iteratively analyzes loan violations and finds
intelligent fixes by querying GSE guides for compensating factors and simulating what-if scenarios.
"""

import asyncio
import json
import logging
import time
from functools import lru_cache
from typing import Any

import anthropic

from ..config import get_settings
from ..models.loan import LoanScenario, ProductResult, RuleViolation
from ..models.fix_finder import (
    GuideCitation,
    CompensatingFactor,
    EnhancedFixSuggestion,
    SimulationResult,
    FixSequence,
    ToolCall,
    ReactStep,
    FixFinderResult,
)
from .pinecone_service import get_pinecone_service
from .embedding_service import get_embedding_service
from .llm_usage_service import record_usage

logger = logging.getLogger(__name__)


# Tool definitions for Claude to use in the ReAct loop
TOOLS = [
    {
        "name": "query_guides",
        "description": "Search the GSE guides for information about compensating factors, exceptions, or alternative requirements that could help resolve a loan eligibility violation. Use this to find official guidance on how to work around specific rule failures.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant guide sections. Be specific about the violation type and what compensating factors or exceptions you're looking for.",
                },
                "gse_filter": {
                    "type": "string",
                    "enum": ["fannie_mae", "freddie_mac", "both"],
                    "description": "Which GSE's guides to search. Use 'fannie_mae' for HomeReady, 'freddie_mac' for Home Possible, or 'both' for general guidance.",
                },
                "focus_area": {
                    "type": "string",
                    "enum": ["compensating_factors", "exceptions", "alternative_requirements", "general"],
                    "description": "What aspect to focus the search on.",
                },
            },
            "required": ["query", "gse_filter"],
        },
    },
    {
        "name": "simulate_scenario",
        "description": "Test a what-if scenario by simulating changes to the loan parameters and checking if it would resolve eligibility violations. Use this to quantify the impact of potential fixes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "changes": {
                    "type": "object",
                    "description": "Key-value pairs of loan parameters to modify. Valid keys: credit_score, annual_income, loan_amount, property_value, monthly_debt_payments.",
                    "additionalProperties": {"type": "number"},
                },
                "description": {
                    "type": "string",
                    "description": "Brief description of what this simulation represents (e.g., 'Pay down $5,000 in debt').",
                },
            },
            "required": ["changes", "description"],
        },
    },
    {
        "name": "compare_products",
        "description": "Compare the requirements between HomeReady (Fannie Mae) and Home Possible (Freddie Mac) for a specific rule or requirement area. Use this to identify which product might be easier to qualify for given specific violations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "requirement_area": {
                    "type": "string",
                    "enum": ["credit_score", "ltv", "dti", "income_limits", "property_type", "occupancy", "reserves"],
                    "description": "Which requirement area to compare between the two products.",
                },
            },
            "required": ["requirement_area"],
        },
    },
]


SYSTEM_PROMPT = """You are SAGE Fix Finder, an expert mortgage loan restructuring agent. Your job is to analyze loan eligibility violations and find intelligent ways to fix them.

PROCESS: Use the ReAct pattern (Reason + Act):
1. OBSERVE: Review the current loan violations and any previous findings
2. THINK: Reason about what information you need to find better fixes
3. ACT: Use tools to gather compensating factors, test scenarios, or compare products
4. REPEAT: Continue until you have enough information (max 3 iterations)

TOOLS AVAILABLE:
- query_guides: Search GSE guides for compensating factors, exceptions, and alternative requirements
- simulate_scenario: Test what-if changes to see if they resolve violations
- compare_products: Compare HomeReady vs Home Possible requirements

PRIORITIZATION GUIDELINES:
1. Easy fixes over hard ones (e.g., documenting existing reserves vs. paying down $50K in debt)
2. Fixes that unlock BOTH products over just one
3. Quick fixes over long-term ones
4. Low-cost fixes over expensive ones
5. Fixes with official compensating factor support in the guides

OUTPUT: After gathering information, provide your analysis in JSON format with:
- enhanced_fixes: List of fixes with confidence scores (0-1), priority order, estimated timeline, which products they unlock, citations, and any trade-offs
- fix_sequences: Multi-step paths to eligibility, ordered by effort-vs-benefit
- recommended_path: Your top recommendation based on the analysis
- product_comparison: Key differences between HomeReady and Home Possible for this scenario

Be specific and actionable. Cite guide sections when possible. Quantify impacts (e.g., "Reducing debt by $200/month would lower DTI from 52% to 48%")."""


class FixFinderService:
    """ReAct-based agent for finding intelligent loan fixes."""

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.anthropic_api_key
        self._model = settings.anthropic_model
        self._max_iterations = getattr(settings, "fix_finder_max_iterations", 3)
        self._timeout = getattr(settings, "fix_finder_timeout", 15)
        self._client: anthropic.Anthropic | None = None
        self._pinecone = get_pinecone_service()
        self._embedding = get_embedding_service()

    def _ensure_client(self) -> anthropic.Anthropic:
        """Initialize Anthropic client if not already done."""
        if self._client is None:
            if not self._api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    def _format_product_status(self, products: list[ProductResult]) -> str:
        """Format product eligibility status safely."""
        lines = []
        for product in products:
            status = "Eligible" if product.eligible else "Ineligible"
            lines.append(f"- {product.product_name}: {status}")
        return "\n".join(lines) if lines else "- No products evaluated"

    def _flatten_to_string_dict(self, data: dict[str, Any]) -> dict[str, str]:
        """Flatten a dict with potentially nested values to dict[str, str]."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = value
            elif isinstance(value, dict):
                # Flatten nested dict to string
                result[key] = json.dumps(value)
            elif isinstance(value, list):
                result[key] = ", ".join(str(v) for v in value)
            else:
                result[key] = str(value)
        return result

    async def _execute_query_guides(
        self,
        query: str,
        gse_filter: str,
        focus_area: str = "general",
        top_k: int = 4,
    ) -> tuple[list[dict[str, Any]], str]:
        """Execute the query_guides tool to search GSE guides."""
        try:
            query_vector = await self._embedding.embed_text(query)

            # Build filter based on GSE
            pinecone_filter = None
            if gse_filter != "both":
                pinecone_filter = {"gse": {"$eq": gse_filter}}

            results = await self._pinecone.query(
                vector=query_vector,
                top_k=top_k,
                filter=pinecone_filter,
            )

            # Format results
            citations = []
            result_text_parts = []

            for r in results:
                metadata = r.get("metadata", {})
                section = metadata.get("section", r.get("id", "Unknown"))
                title = metadata.get("title", "")
                text = metadata.get("text", "")[:600]
                gse = metadata.get("gse", "unknown")
                score = r.get("score", 0)

                citations.append({
                    "section_id": section,
                    "gse": gse,
                    "snippet": text,
                    "relevance_score": min(score, 1.0),
                })

                gse_label = "Fannie Mae" if gse == "fannie_mae" else "Freddie Mac"
                result_text_parts.append(f"[{gse_label} {section}] {title}\n{text}")

            result_summary = "\n---\n".join(result_text_parts) if result_text_parts else "No relevant sections found."

            return citations, result_summary

        except Exception as e:
            logger.warning(f"query_guides failed: {e}")
            return [], f"Search failed: {str(e)}"

    def _execute_simulate_scenario(
        self,
        scenario: LoanScenario,
        changes: dict[str, float],
        description: str,
    ) -> tuple[SimulationResult, str]:
        """Execute the simulate_scenario tool to test what-if changes."""
        # Create modified scenario with changes
        scenario_data = scenario.model_dump()

        for key, value in changes.items():
            if key in scenario_data:
                scenario_data[key] = value

        # Recalculate LTV and DTI
        modified_loan_amount = scenario_data.get("loan_amount", scenario.loan_amount)
        modified_property_value = scenario_data.get("property_value", scenario.property_value)
        modified_income = scenario_data.get("annual_income", scenario.annual_income)
        modified_debt = scenario_data.get("monthly_debt_payments", scenario.monthly_debt_payments)
        modified_credit = scenario_data.get("credit_score", scenario.credit_score)

        modified_ltv = modified_loan_amount / modified_property_value
        monthly_income = modified_income / 12

        # Rough mortgage payment estimate (6% rate)
        rate = 0.06 / 12
        n = 30 * 12
        if rate > 0:
            mortgage_payment = modified_loan_amount * (rate * (1 + rate) ** n) / ((1 + rate) ** n - 1)
        else:
            mortgage_payment = modified_loan_amount / n

        modified_dti = (modified_debt + mortgage_payment) / monthly_income

        # Check eligibility for both products
        homeready_violations = []
        home_possible_violations = []

        # Credit score
        if modified_credit < 620:
            homeready_violations.append("min_credit_score")
        if modified_credit < 660:
            home_possible_violations.append("min_credit_score")

        # LTV
        if modified_ltv > 0.97:
            homeready_violations.append("max_ltv")
            home_possible_violations.append("max_ltv")

        # DTI
        if modified_dti > 0.50:
            homeready_violations.append("max_dti")
        if modified_dti > 0.45:
            home_possible_violations.append("max_dti")

        # Occupancy (can't be changed via this tool)
        if scenario.occupancy != "primary":
            homeready_violations.append("occupancy")
            home_possible_violations.append("occupancy")

        # Determine feasibility based on magnitude of changes
        total_change_magnitude = sum(abs(v) for v in changes.values())
        if total_change_magnitude < 5000:
            feasibility = "easy"
        elif total_change_magnitude < 20000:
            feasibility = "moderate"
        elif total_change_magnitude < 50000:
            feasibility = "hard"
        else:
            feasibility = "very_hard"

        # Build simulation result
        param_changes = {k: f"{v:,.0f}" if isinstance(v, (int, float)) else str(v) for k, v in changes.items()}

        simulation = SimulationResult(
            scenario_description=description,
            parameter_changes=param_changes,
            homeready_eligible=len(homeready_violations) == 0,
            home_possible_eligible=len(home_possible_violations) == 0,
            violations_resolved=[],  # Will be filled by comparing with original
            remaining_violations=list(set(homeready_violations + home_possible_violations)),
            feasibility=feasibility,
        )

        # Build result summary
        hr_status = "Eligible" if simulation.homeready_eligible else f"Ineligible ({', '.join(homeready_violations)})"
        hp_status = "Eligible" if simulation.home_possible_eligible else f"Ineligible ({', '.join(home_possible_violations)})"

        result_summary = f"""Simulation: {description}
Changes: {param_changes}
Modified LTV: {modified_ltv:.1%}, Modified DTI: {modified_dti:.1%}
HomeReady: {hr_status}
Home Possible: {hp_status}
Feasibility: {feasibility}"""

        return simulation, result_summary

    async def _execute_compare_products(
        self,
        requirement_area: str,
    ) -> tuple[dict[str, str], str]:
        """Execute the compare_products tool to compare HomeReady vs Home Possible."""
        # Query for both products
        query = f"{requirement_area} requirements eligibility HomeReady Home Possible comparison"

        try:
            query_vector = await self._embedding.embed_text(query)

            # Get Fannie Mae results
            fannie_results = await self._pinecone.query(
                vector=query_vector,
                top_k=2,
                filter={"gse": {"$eq": "fannie_mae"}},
            )

            # Get Freddie Mac results
            freddie_results = await self._pinecone.query(
                vector=query_vector,
                top_k=2,
                filter={"gse": {"$eq": "freddie_mac"}},
            )

            comparison = {}
            result_parts = []

            # Extract HomeReady info
            for r in fannie_results:
                metadata = r.get("metadata", {})
                text = metadata.get("text", "")[:400]
                comparison["homeready"] = text
                result_parts.append(f"HomeReady ({requirement_area}):\n{text}")
                break

            # Extract Home Possible info
            for r in freddie_results:
                metadata = r.get("metadata", {})
                text = metadata.get("text", "")[:400]
                comparison["home_possible"] = text
                result_parts.append(f"Home Possible ({requirement_area}):\n{text}")
                break

            result_summary = "\n\n".join(result_parts) if result_parts else "No comparison data found."
            return comparison, result_summary

        except Exception as e:
            logger.warning(f"compare_products failed: {e}")
            return {}, f"Comparison failed: {str(e)}"

    async def _process_tool_calls(
        self,
        tool_calls: list[dict],
        scenario: LoanScenario,
    ) -> tuple[list[ToolCall], list[dict], list[GuideCitation], list[SimulationResult]]:
        """Process tool calls from Claude and execute them."""
        processed_calls = []
        tool_results = []
        all_citations = []
        all_simulations = []

        for tc in tool_calls:
            tool_name = tc.get("name", "")
            tool_input = tc.get("input", {})
            tool_id = tc.get("id", "")

            result_summary = ""

            if tool_name == "query_guides":
                citations, result_summary = await self._execute_query_guides(
                    query=tool_input.get("query", ""),
                    gse_filter=tool_input.get("gse_filter", "both"),
                    focus_area=tool_input.get("focus_area", "general"),
                )
                all_citations.extend([
                    GuideCitation(
                        section_id=c["section_id"],
                        gse=c["gse"],
                        snippet=c["snippet"],
                        relevance_score=c["relevance_score"],
                    )
                    for c in citations
                ])

            elif tool_name == "simulate_scenario":
                simulation, result_summary = self._execute_simulate_scenario(
                    scenario=scenario,
                    changes=tool_input.get("changes", {}),
                    description=tool_input.get("description", ""),
                )
                all_simulations.append(simulation)

            elif tool_name == "compare_products":
                comparison, result_summary = await self._execute_compare_products(
                    requirement_area=tool_input.get("requirement_area", ""),
                )

            processed_calls.append(
                ToolCall(
                    tool_name=tool_name,
                    arguments=tool_input,
                    result_summary=result_summary[:500],  # Truncate for trace
                )
            )

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": result_summary,
            })

        return processed_calls, tool_results, all_citations, all_simulations

    async def _run_react_loop(
        self,
        scenario: LoanScenario,
        violations: list[RuleViolation],
        products: list[ProductResult],
        demo_mode: bool = False,
    ) -> tuple[dict[str, Any], list[ReactStep], list[GuideCitation], list[SimulationResult], int]:
        """
        Run the ReAct loop to find intelligent fixes.

        Returns:
            Tuple of (final_analysis, react_trace, all_citations, all_simulations, tokens_used)
        """
        client = self._ensure_client()

        # Build initial prompt with loan details and violations
        violation_list = "\n".join([
            f"- {v.rule_name}: {v.rule_description} (actual: {v.actual_value}, required: {v.required_value}, source: {v.citation})"
            for v in violations
        ])

        ltv = scenario.ltv
        dti = scenario.calculate_dti()

        initial_prompt = f"""LOAN SCENARIO:
- Credit Score: {scenario.credit_score}
- Annual Income: ${scenario.annual_income:,.0f}
- Loan Amount: ${scenario.loan_amount:,.0f}
- Property Value: ${scenario.property_value:,.0f}
- LTV: {ltv:.1%}
- Monthly Debt: ${scenario.monthly_debt_payments:,.0f}
- DTI: {dti:.1%}
- Property Type: {scenario.property_type}
- Occupancy: {scenario.occupancy}

CURRENT VIOLATIONS:
{violation_list}

PRODUCT STATUS:
{self._format_product_status(products)}

Please analyze these violations and find the best fixes. Use the tools to:
1. Search for compensating factors or exceptions that could help
2. Simulate what-if scenarios to quantify fix impacts
3. Compare requirements between HomeReady and Home Possible

Proceed with your analysis."""

        messages = [{"role": "user", "content": initial_prompt}]
        react_trace = []
        all_citations = []
        all_simulations = []
        tokens_in = 0
        tokens_out = 0

        for iteration in range(self._max_iterations):
            try:
                # Add timeout to prevent hanging
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.messages.create,
                        model=self._model,
                        max_tokens=2048,
                        system=SYSTEM_PROMPT,
                        tools=TOOLS,
                        messages=messages,
                    ),
                    timeout=30  # 30 second timeout per iteration
                )

                tokens_in += response.usage.input_tokens
                tokens_out += response.usage.output_tokens

                # Check if Claude wants to use tools
                tool_calls = []
                text_content = ""

                for block in response.content:
                    if block.type == "tool_use":
                        tool_calls.append({
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        })
                    elif block.type == "text":
                        text_content = block.text

                # Build react step
                step = ReactStep(
                    step_number=iteration + 1,
                    observation=f"Iteration {iteration + 1}: Analyzing violations and determining next action",
                    reasoning=text_content[:500] if text_content else "Processing tool calls...",
                    action="tool_calls" if tool_calls else "final_analysis",
                    tool_calls=[],
                    findings=[],
                )

                if tool_calls:
                    # Execute tools
                    processed_calls, tool_results, new_citations, new_simulations = await self._process_tool_calls(
                        tool_calls, scenario
                    )

                    step.tool_calls = processed_calls
                    step.findings = [tc.result_summary[:200] for tc in processed_calls]
                    all_citations.extend(new_citations)
                    all_simulations.extend(new_simulations)

                    # Add assistant response and tool results to messages
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": tool_results})

                react_trace.append(step)

                # If no tool calls, Claude is done - get final analysis
                if not tool_calls or response.stop_reason == "end_turn":
                    # Parse final response
                    final_analysis = self._parse_final_response(text_content)
                    return final_analysis, react_trace, all_citations, all_simulations, tokens_in, tokens_out

            except asyncio.TimeoutError:
                logger.warning(f"ReAct iteration {iteration + 1} timed out after 30s")
                react_trace.append(
                    ReactStep(
                        step_number=iteration + 1,
                        observation="Iteration timed out",
                        reasoning="Claude API call exceeded 30 second timeout",
                        action="timeout",
                        tool_calls=[],
                        findings=[],
                    )
                )
                break
            except Exception as e:
                logger.error(f"ReAct iteration {iteration + 1} failed: {e}", exc_info=True)
                react_trace.append(
                    ReactStep(
                        step_number=iteration + 1,
                        observation=f"Error in iteration: {str(e)}",
                        reasoning="Falling back to basic analysis",
                        action="error_recovery",
                        tool_calls=[],
                        findings=[],
                    )
                )
                break

        # If we've exhausted iterations, ask for final analysis
        try:
            messages.append({
                "role": "user",
                "content": "Please provide your final analysis now with enhanced_fixes, fix_sequences, and recommended_path. Respond with JSON only.",
            })

            # Add timeout to final analysis call
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.messages.create,
                    model=self._model,
                    max_tokens=2048,
                    system=SYSTEM_PROMPT,
                    messages=messages,
                ),
                timeout=45  # 45 second timeout for final analysis
            )

            tokens_in += response.usage.input_tokens
            tokens_out += response.usage.output_tokens

            # Safely extract text content
            text_content = "{}"
            if response.content:
                for block in response.content:
                    if hasattr(block, 'text'):
                        text_content = block.text
                        break

            final_analysis = self._parse_final_response(text_content)
            return final_analysis, react_trace, all_citations, all_simulations, tokens_in, tokens_out

        except asyncio.TimeoutError:
            logger.warning("Final analysis timed out after 45s")
            return {}, react_trace, all_citations, all_simulations, tokens_in, tokens_out
        except Exception as e:
            logger.error(f"Final analysis failed: {e}", exc_info=True)
            return {}, react_trace, all_citations, all_simulations, tokens_in, tokens_out

    def _parse_final_response(self, text: str) -> dict[str, Any]:
        """Parse Claude's final response into structured data."""
        try:
            # Handle markdown code blocks
            if "```" in text:
                lines = text.split("\n")
                json_lines = []
                in_block = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_block = not in_block
                        continue
                    if in_block or (not in_block and line.strip().startswith("{")):
                        json_lines.append(line)
                text = "\n".join(json_lines)

            # Find JSON object in text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)

            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse final response as JSON: {e}")
            return {}

    def _build_enhanced_fixes(
        self,
        analysis: dict[str, Any],
        all_citations: list[GuideCitation],
        violations: list[RuleViolation],
    ) -> list[EnhancedFixSuggestion]:
        """Build EnhancedFixSuggestion objects from Claude's analysis."""
        enhanced_fixes = []

        raw_fixes = analysis.get("enhanced_fixes", [])

        for i, fix in enumerate(raw_fixes):
            if not isinstance(fix, dict):
                continue

            # Map difficulty
            difficulty = fix.get("difficulty", "moderate")
            if difficulty not in ["easy", "moderate", "hard"]:
                difficulty = "moderate"

            # Find relevant citations
            fix_citations = []
            for citation in all_citations:
                if any(
                    kw.lower() in citation.snippet.lower()
                    for kw in fix.get("description", "").split()[:5]
                ):
                    fix_citations.append(citation)

            # Map unlocks_products - Claude uses "products_unlocked" or "unlocks_products"
            unlocks = fix.get("unlocks_products", []) or fix.get("products_unlocked", [])
            if isinstance(unlocks, str):
                unlocks = [unlocks] if unlocks else []
            elif not isinstance(unlocks, list):
                unlocks = []
            valid_products = [p for p in unlocks if p in ["HomeReady", "Home Possible"]]

            # Handle trade_offs - Claude sometimes returns string instead of list
            trade_offs = fix.get("trade_offs", [])
            if isinstance(trade_offs, str):
                trade_offs = [trade_offs] if trade_offs else []
            elif not isinstance(trade_offs, list):
                trade_offs = []

            # Get description - Claude uses "description" or "fix" field
            description = fix.get("description", "") or fix.get("fix", "") or "No description provided"

            # Get impact - Claude sometimes uses "quantified_impact"
            impact = fix.get("impact", "") or fix.get("quantified_impact", "") or "Impact not specified"

            # Get priority - Claude uses "priority" not "priority_order"
            priority = fix.get("priority_order", fix.get("priority", i + 1))

            enhanced_fixes.append(
                EnhancedFixSuggestion(
                    description=description,
                    impact=impact,
                    difficulty=difficulty,
                    confidence=min(max(float(fix.get("confidence", 0.7)), 0), 1),
                    priority_order=int(priority),
                    estimated_timeline=fix.get("estimated_timeline", "Varies") or "Varies",
                    unlocks_products=valid_products,
                    citations=fix_citations[:3],  # Limit citations per fix
                    compensating_factors=[],  # Could be enhanced later
                    trade_offs=trade_offs,
                )
            )

        return enhanced_fixes

    def _build_fix_sequences(
        self,
        analysis: dict[str, Any],
        enhanced_fixes: list[EnhancedFixSuggestion],
    ) -> list[FixSequence]:
        """Build FixSequence objects from Claude's analysis."""
        sequences = []

        raw_sequences = analysis.get("fix_sequences", [])

        for seq in raw_sequences:
            if not isinstance(seq, dict):
                continue

            # Map total_effort
            effort = seq.get("total_effort", "medium")
            if effort not in ["low", "medium", "high", "very_high"]:
                effort = "medium"

            # Map products_unlocked
            unlocks = seq.get("products_unlocked", [])
            valid_products = [p for p in unlocks if p in ["HomeReady", "Home Possible"]]

            # Build steps from enhanced fixes or raw step data
            steps = []
            raw_steps = seq.get("steps", [])
            for step in raw_steps:
                if isinstance(step, dict):
                    step_difficulty = step.get("difficulty", "moderate")
                    if step_difficulty not in ["easy", "moderate", "hard"]:
                        step_difficulty = "moderate"

                    steps.append(
                        EnhancedFixSuggestion(
                            description=step.get("description", ""),
                            impact=step.get("impact", ""),
                            difficulty=step_difficulty,
                            confidence=min(max(step.get("confidence", 0.7), 0), 1),
                            priority_order=step.get("priority_order", len(steps) + 1),
                            estimated_timeline=step.get("estimated_timeline", "Varies"),
                            unlocks_products=[],
                            citations=[],
                            compensating_factors=[],
                            trade_offs=[],
                        )
                    )

            if steps:
                sequences.append(
                    FixSequence(
                        sequence_name=seq.get("sequence_name", f"Path {len(sequences) + 1}"),
                        description=seq.get("description", ""),
                        steps=steps,
                        total_effort=effort,
                        effort_vs_benefit_score=min(max(seq.get("effort_vs_benefit_score", 5), 0), 10),
                        products_unlocked=valid_products,
                        estimated_total_timeline=seq.get("estimated_total_timeline", "Varies"),
                    )
                )

        return sequences

    async def find_fixes(
        self,
        scenario: LoanScenario,
        violations: list[RuleViolation],
        products: list[ProductResult],
        demo_mode: bool = False,
    ) -> FixFinderResult:
        """
        Main entry point for the Fix Finder Agent.

        Uses ReAct loop to iteratively analyze violations and find intelligent fixes.

        Args:
            scenario: The loan scenario being analyzed
            violations: List of rule violations to fix
            products: Product eligibility results
            demo_mode: Whether to include full ReAct trace

        Returns:
            FixFinderResult with enhanced fixes, sequences, and simulations
        """
        start_time = time.time()

        try:
            # Run the ReAct loop
            analysis, react_trace, all_citations, all_simulations, tokens_in, tokens_out = await self._run_react_loop(
                scenario, violations, products, demo_mode
            )
            tokens_used = tokens_in + tokens_out

            # Build enhanced fixes
            enhanced_fixes = self._build_enhanced_fixes(analysis, all_citations, violations)

            # Build fix sequences
            fix_sequences = self._build_fix_sequences(analysis, enhanced_fixes)

            # Get product comparison - flatten nested dicts to strings
            raw_comparison = analysis.get("product_comparison", {})
            product_comparison = self._flatten_to_string_dict(raw_comparison)

            # Get recommended path - convert dict to string if needed
            raw_path = analysis.get("recommended_path", "")
            if isinstance(raw_path, dict):
                # Extract main recommendation from nested dict
                recommended_path = raw_path.get("primary_recommendation", "")
                if not recommended_path:
                    recommended_path = json.dumps(raw_path)[:500]
            else:
                recommended_path = str(raw_path) if raw_path else ""

            total_time_ms = int((time.time() - start_time) * 1000)

            # Record LLM usage for tracking
            await record_usage(
                service_name="fix_finder",
                model_name=self._model,
                model_provider="anthropic",
                request_type="fix_finding",
                tokens_input=tokens_in,
                tokens_output=tokens_out,
                duration_ms=total_time_ms,
                success=True,
            )

            return FixFinderResult(
                enhanced_fixes=enhanced_fixes,
                fix_sequences=fix_sequences,
                simulations=all_simulations,
                recommended_path=recommended_path,
                product_comparison=product_comparison,
                react_trace=react_trace if demo_mode else [],
                total_iterations=len(react_trace),
                total_time_ms=total_time_ms,
                tokens_used=tokens_used,
            )

        except Exception as e:
            logger.error(f"Fix Finder failed: {e}")
            total_time_ms = int((time.time() - start_time) * 1000)

            # Record failed LLM usage
            await record_usage(
                service_name="fix_finder",
                model_name=self._model,
                model_provider="anthropic",
                request_type="fix_finding",
                tokens_input=0,
                tokens_output=0,
                duration_ms=total_time_ms,
                success=False,
                error_message=str(e),
            )

            # Return empty result on failure
            return FixFinderResult(
                enhanced_fixes=[],
                fix_sequences=[],
                simulations=[],
                recommended_path="Analysis failed. Please review basic fix suggestions.",
                product_comparison={},
                react_trace=[],
                total_iterations=0,
                total_time_ms=total_time_ms,
                tokens_used=0,
            )


@lru_cache
def get_fix_finder_service() -> FixFinderService:
    """Get cached Fix Finder service instance."""
    return FixFinderService()
