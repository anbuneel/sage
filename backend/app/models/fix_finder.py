"""
Fix Finder Models

Models for the ReAct-based Fix Finder Agent that iteratively analyzes loan violations
and finds intelligent fixes by querying GSE guides for compensating factors.
"""

from typing import Literal
from pydantic import BaseModel, Field


class GuideCitation(BaseModel):
    """A citation from a GSE guide section."""

    section_id: str = Field(..., description="Guide section identifier (e.g., 'B5-6-02', '4501.5')")
    gse: Literal["fannie_mae", "freddie_mac"] = Field(..., description="Source GSE")
    snippet: str = Field(..., description="Relevant text snippet from the section")
    relevance_score: float = Field(..., ge=0, le=1, description="How relevant this citation is (0-1)")


class CompensatingFactor(BaseModel):
    """A compensating factor that could offset a violation."""

    factor_type: str = Field(..., description="Type of compensating factor (e.g., 'reserves', 'residual_income')")
    description: str = Field(..., description="Description of the compensating factor")
    requirement: str = Field(..., description="What's required to use this factor")
    citations: list[GuideCitation] = Field(default_factory=list, description="Guide citations for this factor")


class EnhancedFixSuggestion(BaseModel):
    """
    An enhanced fix suggestion with confidence scores, citations, and compensating factors.

    Extends the basic FixSuggestion with additional intelligence from RAG analysis.
    """

    description: str = Field(..., description="What the borrower should do")
    impact: str = Field(..., description="How this fix would help")
    difficulty: Literal["easy", "moderate", "hard"] = Field(
        ..., description="How difficult this fix is to implement"
    )
    confidence: float = Field(
        ..., ge=0, le=1, description="Confidence score that this fix will resolve the issue (0-1)"
    )
    priority_order: int = Field(..., ge=1, description="Suggested order to attempt fixes (1 = highest priority)")
    estimated_timeline: str = Field(
        ..., description="Estimated time to implement (e.g., 'Immediate', '1-2 weeks', '3-6 months')"
    )
    unlocks_products: list[Literal["HomeReady", "Home Possible"]] = Field(
        default_factory=list, description="Which products this fix could unlock eligibility for"
    )
    citations: list[GuideCitation] = Field(
        default_factory=list, description="Guide citations supporting this fix"
    )
    compensating_factors: list[CompensatingFactor] = Field(
        default_factory=list, description="Compensating factors that could help"
    )
    trade_offs: list[str] = Field(
        default_factory=list, description="Potential downsides or trade-offs of this fix"
    )


class SimulationResult(BaseModel):
    """Result of a what-if scenario simulation."""

    scenario_description: str = Field(..., description="What was changed in this simulation")
    parameter_changes: dict[str, str] = Field(
        default_factory=dict, description="Parameters that were modified"
    )
    homeready_eligible: bool = Field(..., description="Would be eligible for HomeReady")
    home_possible_eligible: bool = Field(..., description="Would be eligible for Home Possible")
    violations_resolved: list[str] = Field(
        default_factory=list, description="List of violation rule names that would be resolved"
    )
    remaining_violations: list[str] = Field(
        default_factory=list, description="List of violation rule names that would remain"
    )
    feasibility: Literal["easy", "moderate", "hard", "very_hard"] = Field(
        ..., description="How feasible this scenario change is"
    )


class FixSequence(BaseModel):
    """A multi-step path to eligibility with ordered fixes."""

    sequence_name: str = Field(..., description="Name of this fix sequence (e.g., 'Quick Path', 'Best Value')")
    description: str = Field(..., description="Overall description of this approach")
    steps: list[EnhancedFixSuggestion] = Field(..., description="Ordered list of fixes to apply")
    total_effort: Literal["low", "medium", "high", "very_high"] = Field(
        ..., description="Total effort required for this sequence"
    )
    effort_vs_benefit_score: float = Field(
        ..., ge=0, le=10, description="Score balancing effort vs benefit (10 = best)"
    )
    products_unlocked: list[Literal["HomeReady", "Home Possible"]] = Field(
        default_factory=list, description="Which products this sequence unlocks"
    )
    estimated_total_timeline: str = Field(
        ..., description="Estimated total time to complete this sequence"
    )


class ToolCall(BaseModel):
    """A single tool call made by the ReAct agent."""

    tool_name: Literal["query_guides", "simulate_scenario", "compare_products"] = Field(
        ..., description="Name of the tool called"
    )
    arguments: dict = Field(default_factory=dict, description="Arguments passed to the tool")
    result_summary: str = Field(..., description="Summary of what the tool returned")


class ReactStep(BaseModel):
    """A single step in the ReAct reasoning loop."""

    step_number: int = Field(..., ge=1, description="Which iteration this is (1-indexed)")
    observation: str = Field(..., description="What the agent observed from the previous action")
    reasoning: str = Field(..., description="The agent's thinking about what to do next")
    action: str = Field(..., description="What action the agent decided to take")
    tool_calls: list[ToolCall] = Field(default_factory=list, description="Tools called in this step")
    findings: list[str] = Field(default_factory=list, description="Key findings from this step")


class FixFinderResult(BaseModel):
    """Complete result from the Fix Finder Agent."""

    # Enhanced fixes with full intelligence
    enhanced_fixes: list[EnhancedFixSuggestion] = Field(
        default_factory=list, description="Enhanced fix suggestions with confidence and citations"
    )

    # Multi-step paths to eligibility
    fix_sequences: list[FixSequence] = Field(
        default_factory=list, description="Multi-step fix sequences with effort/benefit analysis"
    )

    # What-if simulation results
    simulations: list[SimulationResult] = Field(
        default_factory=list, description="What-if scenario simulation results"
    )

    # Recommended path
    recommended_path: str = Field(
        default="", description="The recommended approach based on analysis"
    )

    # Product comparison insights
    product_comparison: dict[str, str] = Field(
        default_factory=dict, description="Insights comparing HomeReady vs Home Possible requirements"
    )

    # ReAct trace for demo mode transparency
    react_trace: list[ReactStep] = Field(
        default_factory=list, description="ReAct reasoning trace (demo mode only)"
    )

    # Performance metrics
    total_iterations: int = Field(default=0, description="Total ReAct iterations performed")
    total_time_ms: int = Field(default=0, description="Total processing time in milliseconds")
    tokens_used: int = Field(default=0, description="Total tokens consumed")
