"""
Eligibility Reasoner Service

RAG-powered loan eligibility analysis using Claude to reason over GSE guide excerpts.
Replaces hardcoded rules with AI-driven analysis that cites actual guide sections.
"""

import asyncio
import json
import logging
import time
from typing import Any
from functools import lru_cache

import anthropic

from ..config import get_settings
from ..models import (
    LoanScenario,
    RAGRetrieval,
    ReasoningStep,
    DemoModeData,
    IndexStats,
    ProductResult,
    RuleViolation,
    FixSuggestion,
)
from .pinecone_service import get_pinecone_service
from .embedding_service import get_embedding_service
from .llm_usage_service import record_usage

logger = logging.getLogger(__name__)


# Focused queries for each eligibility rule category
ELIGIBILITY_QUERIES = {
    "credit_score": [
        "HomeReady minimum credit score requirements eligibility",
        "Home Possible minimum credit score requirements eligibility",
    ],
    "ltv": [
        "HomeReady maximum LTV loan-to-value ratio requirements {property_type}",
        "Home Possible maximum LTV loan-to-value ratio requirements {property_type}",
    ],
    "dti": [
        "HomeReady maximum DTI debt-to-income ratio requirements",
        "Home Possible maximum DTI debt-to-income ratio requirements",
    ],
    "occupancy": [
        "HomeReady occupancy requirements primary residence",
        "Home Possible occupancy requirements primary residence",
    ],
    "property_type": [
        "HomeReady eligible property types {property_type}",
        "Home Possible eligible property types {property_type}",
    ],
    "income_limit": [
        "HomeReady income limits area median income AMI",
        "Home Possible income limits area median income AMI",
    ],
}

SYSTEM_PROMPT = """You are SAGE, an expert mortgage eligibility analyst. Your job is to analyze loan scenarios against GSE (Fannie Mae and Freddie Mac) affordable lending product guidelines.

You have access to excerpts from the official GSE guides. Analyze the loan scenario against these excerpts to determine eligibility for:
- HomeReady (Fannie Mae)
- Home Possible (Freddie Mac)

RULES FOR ANALYSIS:
1. Check each requirement (credit score, LTV, DTI, occupancy, property type, income limits) against the provided guide excerpts
2. ONLY cite guide sections that are actually provided in the context
3. Be precise about actual thresholds mentioned in the excerpts
4. If a requirement isn't clear from the excerpts, note it as "unable to verify from provided excerpts"
5. Provide specific, actionable fix suggestions for any failures

OUTPUT FORMAT:
You must respond with valid JSON matching this exact schema:
{
  "homeready": {
    "eligible": boolean,
    "confidence": "high" | "medium" | "low",
    "rules_checked": [
      {
        "rule_name": "min_credit_score" | "max_ltv" | "max_dti" | "occupancy" | "property_type" | "income_limit",
        "requirement": "Description of requirement from guide",
        "actual_value": "The loan's actual value",
        "result": "pass" | "fail" | "unable_to_verify",
        "citation": "Guide section reference (e.g., B5-6-02)",
        "explanation": "Brief explanation of the check"
      }
    ]
  },
  "home_possible": {
    "eligible": boolean,
    "confidence": "high" | "medium" | "low",
    "rules_checked": [...]
  },
  "recommendation": "Overall recommendation text",
  "fix_suggestions": [
    {
      "description": "What to do",
      "impact": "How it helps",
      "difficulty": "easy" | "moderate" | "hard"
    }
  ]
}

Respond ONLY with the JSON object, no additional text."""


class EligibilityReasonerService:
    """RAG-powered eligibility analysis service."""

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.anthropic_api_key
        self._model = settings.anthropic_model
        self._timeout = getattr(settings, "rag_eligibility_timeout", 30)
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

    async def retrieve_eligibility_context(
        self,
        scenario: LoanScenario,
        top_k_per_query: int = 3,
    ) -> tuple[list[dict[str, Any]], list[RAGRetrieval], int]:
        """
        Retrieve relevant guide sections for eligibility analysis.

        Runs parallel queries for each rule category, filtered by GSE.

        Returns:
            Tuple of (raw_chunks, rag_retrievals for demo, retrieval_time_ms)
        """
        start_time = time.time()

        # Build queries with scenario context
        property_type_label = scenario.property_type.replace("_", " ")
        queries = []

        for category, query_templates in ELIGIBILITY_QUERIES.items():
            for template in query_templates:
                query = template.format(property_type=property_type_label)
                # Determine GSE filter based on query content
                gse_filter = "fannie_mae" if "HomeReady" in template else "freddie_mac"
                queries.append((category, query, gse_filter))

        # Run all queries in parallel
        async def run_query(category: str, query: str, gse_filter: str):
            try:
                query_vector = await self._embedding.embed_text(query)
                results = await self._pinecone.query(
                    vector=query_vector,
                    top_k=top_k_per_query,
                    filter={"gse": {"$eq": gse_filter}},
                )
                return [(category, query, gse_filter, r) for r in results]
            except Exception as e:
                logger.warning(f"Query failed for {category}/{gse_filter}: {e}")
                return []

        tasks = [run_query(cat, q, gse) for cat, q, gse in queries]
        all_results = await asyncio.gather(*tasks)

        # Flatten and deduplicate results
        seen_ids = set()
        raw_chunks = []
        rag_retrievals = []

        for result_list in all_results:
            for category, query, gse_filter, chunk in result_list:
                chunk_id = chunk.get("id", "")
                if chunk_id in seen_ids:
                    continue
                seen_ids.add(chunk_id)

                metadata = chunk.get("metadata", {})
                raw_chunks.append(chunk)

                # Build RAGRetrieval for demo mode
                rag_retrievals.append(
                    RAGRetrieval(
                        query=query,
                        section_id=metadata.get("section", chunk_id),
                        section_title=metadata.get("title", "GSE Guide Section"),
                        gse=metadata.get("gse", gse_filter),
                        relevance_score=min(chunk.get("score", 0.5), 1.0),
                        snippet=metadata.get("text", "")[:300],
                    )
                )

        retrieval_time_ms = int((time.time() - start_time) * 1000)

        # Sort by relevance score
        rag_retrievals.sort(key=lambda x: x.relevance_score, reverse=True)

        return raw_chunks, rag_retrievals[:12], retrieval_time_ms  # Limit to top 12

    def build_analysis_prompt(
        self,
        scenario: LoanScenario,
        context_chunks: list[dict[str, Any]],
    ) -> str:
        """Build the user prompt with loan data and retrieved context."""

        # Format loan scenario
        ltv = scenario.ltv
        dti = scenario.calculate_dti()

        loan_info = f"""LOAN SCENARIO:
- Credit Score: {scenario.credit_score}
- Annual Income: ${scenario.annual_income:,.0f}
- First-Time Buyer: {scenario.is_first_time_buyer}
- Loan Amount: ${scenario.loan_amount:,.0f}
- Property Value: ${scenario.property_value:,.0f}
- Calculated LTV: {ltv:.1%}
- Monthly Debt Payments: ${scenario.monthly_debt_payments:,.0f}
- Calculated DTI: {dti:.1%}
- Property Type: {scenario.property_type.replace('_', ' ').title()}
- Property Location: {scenario.property_county}, {scenario.property_state}
- Occupancy: {scenario.occupancy.title()}
"""

        # Format context chunks by GSE
        fannie_context = []
        freddie_context = []

        for i, chunk in enumerate(context_chunks):
            metadata = chunk.get("metadata", {})
            gse = metadata.get("gse", "")
            section = metadata.get("section", f"Section {i + 1}")
            title = metadata.get("title", "")
            text = metadata.get("text", "")[:800]  # Limit text length

            formatted = f"[{section}] {title}\n{text}"

            if gse == "fannie_mae":
                fannie_context.append(formatted)
            else:
                freddie_context.append(formatted)

        context_str = "GSE GUIDE EXCERPTS:\n\n"
        if fannie_context:
            context_str += "=== FANNIE MAE (HomeReady) ===\n"
            context_str += "\n---\n".join(fannie_context)
            context_str += "\n\n"
        if freddie_context:
            context_str += "=== FREDDIE MAC (Home Possible) ===\n"
            context_str += "\n---\n".join(freddie_context)

        return f"""{loan_info}

{context_str}

Analyze this loan scenario against the provided guide excerpts and determine eligibility for HomeReady and Home Possible. Respond with JSON only."""

    async def analyze_with_claude(
        self,
        prompt: str,
    ) -> tuple[dict[str, Any], int, int, int]:
        """
        Call Claude with the analysis prompt.

        Returns:
            Tuple of (parsed_response, reasoning_time_ms, tokens_in, tokens_out)
        """
        client = self._ensure_client()
        start_time = time.time()

        try:
            response = await asyncio.to_thread(
                client.messages.create,
                model=self._model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            reasoning_time_ms = int((time.time() - start_time) * 1000)
            tokens_in = response.usage.input_tokens
            tokens_out = response.usage.output_tokens

            # Parse JSON response
            response_text = response.content[0].text.strip()

            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                # Remove markdown code block markers
                lines = response_text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                response_text = "\n".join(lines)

            parsed = json.loads(response_text)
            return parsed, reasoning_time_ms, tokens_in, tokens_out

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            raise ValueError(f"Invalid JSON response from Claude: {e}")
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            raise

    def _convert_to_results(
        self,
        analysis: dict[str, Any],
        scenario: LoanScenario,
    ) -> tuple[list[ProductResult], str, list[FixSuggestion], list[ReasoningStep]]:
        """Convert Claude's analysis to ProductResult objects."""

        products = []
        reasoning_steps = []

        for product_key, product_data in [
            ("homeready", analysis.get("homeready", {})),
            ("home_possible", analysis.get("home_possible", {})),
        ]:
            product_name = "HomeReady" if product_key == "homeready" else "Home Possible"
            gse = "fannie_mae" if product_key == "homeready" else "freddie_mac"

            violations = []
            rules_checked = product_data.get("rules_checked", [])

            for rule in rules_checked:
                rule_name = rule.get("rule_name", "unknown")
                result = rule.get("result", "pass")

                # Build reasoning step for demo mode
                reasoning_steps.append(
                    ReasoningStep(
                        rule=rule_name,
                        product=product_name,
                        check=rule.get("requirement", "Unknown requirement"),
                        result="pass" if result == "pass" else "fail",
                        citation=rule.get("citation", ""),
                        details=rule.get("explanation", ""),
                    )
                )

                # Add violation if failed
                if result == "fail":
                    violations.append(
                        RuleViolation(
                            rule_name=rule_name,
                            rule_description=rule.get("requirement", "Eligibility requirement"),
                            actual_value=rule.get("actual_value", "N/A"),
                            required_value=rule.get("requirement", "See guide"),
                            citation=rule.get("citation", f"{gse.replace('_', ' ').title()} Guide"),
                        )
                    )

            products.append(
                ProductResult(
                    product_name=product_name,
                    gse=gse,
                    eligible=product_data.get("eligible", len(violations) == 0),
                    violations=violations,
                )
            )

        # Convert fix suggestions
        fix_suggestions = []
        for suggestion in analysis.get("fix_suggestions", []):
            difficulty = suggestion.get("difficulty", "moderate")
            if difficulty not in ["easy", "moderate", "hard"]:
                difficulty = "moderate"

            fix_suggestions.append(
                FixSuggestion(
                    description=suggestion.get("description", ""),
                    impact=suggestion.get("impact", ""),
                    difficulty=difficulty,
                )
            )

        recommendation = analysis.get(
            "recommendation",
            "Analysis complete. Review the results for each product.",
        )

        return products, recommendation, fix_suggestions, reasoning_steps

    async def check_eligibility(
        self,
        scenario: LoanScenario,
    ) -> tuple[
        list[ProductResult],
        str,
        list[FixSuggestion],
        DemoModeData,
    ]:
        """
        Main entry point for RAG-powered eligibility checking.

        Returns:
            Tuple of (products, recommendation, fix_suggestions, demo_data)
        """
        # Step 1: Retrieve relevant context
        raw_chunks, rag_retrievals, retrieval_time_ms = await self.retrieve_eligibility_context(
            scenario
        )

        if not raw_chunks:
            logger.warning("No context retrieved from Pinecone")
            raise ValueError("Unable to retrieve guide context for analysis")

        # Step 2: Build prompt
        prompt = self.build_analysis_prompt(scenario, raw_chunks)

        # Step 3: Analyze with Claude
        analysis, reasoning_time_ms, tokens_in, tokens_out = await self.analyze_with_claude(prompt)

        # Step 4: Convert to result objects
        products, recommendation, fix_suggestions, reasoning_steps = self._convert_to_results(
            analysis, scenario
        )

        # Step 5: Build demo data
        demo_data = DemoModeData(
            rag_retrievals=rag_retrievals,
            retrieval_time_ms=retrieval_time_ms,
            reasoning_steps=reasoning_steps,
            reasoning_time_ms=reasoning_time_ms,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            index_stats=IndexStats(),
        )

        # Record LLM usage for tracking
        await record_usage(
            service_name="eligibility_reasoner",
            model_name=self._model,
            model_provider="anthropic",
            request_type="reasoning",
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            duration_ms=retrieval_time_ms + reasoning_time_ms,
            success=True,
        )

        return products, recommendation, fix_suggestions, demo_data


@lru_cache
def get_eligibility_reasoner() -> EligibilityReasonerService:
    """Get cached eligibility reasoner instance."""
    return EligibilityReasonerService()
