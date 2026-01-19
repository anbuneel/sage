"""
Loan and Eligibility Models

Models for loan scenarios and eligibility checking.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal
from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from .fix_finder import FixFinderResult


class LoanScenario(BaseModel):
    """Input model for eligibility check."""

    # Borrower
    credit_score: int = Field(..., ge=300, le=850, description="Credit score (300-850)")
    annual_income: float = Field(..., gt=0, description="Annual income in dollars")
    is_first_time_buyer: bool = Field(..., description="Whether borrower is first-time buyer")

    # Loan
    loan_amount: float = Field(..., gt=0, description="Loan amount in dollars")
    property_value: float = Field(..., gt=0, description="Property value in dollars")
    loan_term_years: Literal[15, 20, 30] = Field(default=30, description="Loan term in years")

    # Debt (for DTI calculation)
    monthly_debt_payments: float = Field(
        ..., ge=0, description="Monthly debt payments (car, student loans, etc.)"
    )

    # Property
    property_type: Literal[
        "single_family", "condo", "pud", "2_unit", "3_unit", "4_unit", "manufactured"
    ] = Field(..., description="Type of property")
    property_state: str = Field(..., min_length=2, max_length=2, description="State abbreviation")
    property_county: str = Field(..., min_length=1, description="County name")
    occupancy: Literal["primary", "secondary", "investment"] = Field(
        default="primary", description="Occupancy type"
    )

    @field_validator("property_state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Ensure state is uppercase."""
        return v.upper()

    @property
    def ltv(self) -> float:
        """Calculate Loan-to-Value ratio."""
        return self.loan_amount / self.property_value

    @property
    def monthly_income(self) -> float:
        """Calculate monthly income."""
        return self.annual_income / 12

    def calculate_dti(self, estimated_monthly_payment: float | None = None) -> float:
        """
        Calculate Debt-to-Income ratio.

        If estimated_monthly_payment is not provided, uses a rough estimate
        based on loan amount and term.
        """
        if estimated_monthly_payment is None:
            # Rough estimate: assume 6% rate for estimation purposes
            rate = 0.06 / 12
            n = self.loan_term_years * 12
            if rate > 0:
                estimated_monthly_payment = (
                    self.loan_amount * (rate * (1 + rate) ** n) / ((1 + rate) ** n - 1)
                )
            else:
                estimated_monthly_payment = self.loan_amount / n

        total_monthly_debt = self.monthly_debt_payments + estimated_monthly_payment
        return total_monthly_debt / self.monthly_income


class RuleViolation(BaseModel):
    """A single rule violation."""

    rule_name: str = Field(..., description="Rule identifier (e.g., 'max_dti')")
    rule_description: str = Field(..., description="Human-readable rule description")
    actual_value: str = Field(..., description="The actual value that violated the rule")
    required_value: str = Field(..., description="The required value to pass the rule")
    citation: str = Field(..., description="GSE guide citation (e.g., 'Fannie Mae B5-6-02')")


class FixSuggestion(BaseModel):
    """A suggestion for how to fix eligibility issues."""

    description: str = Field(..., description="What the borrower should do")
    impact: str = Field(..., description="How this fix would help")
    difficulty: Literal["easy", "moderate", "hard"] = Field(
        ..., description="How difficult this fix is to implement"
    )


class ProductResult(BaseModel):
    """Eligibility result for a single loan product."""

    product_name: Literal["HomeReady", "Home Possible"] = Field(
        ..., description="Loan product name"
    )
    gse: Literal["fannie_mae", "freddie_mac"] = Field(
        ..., description="Government-Sponsored Enterprise"
    )
    eligible: bool = Field(..., description="Whether eligible for this product")
    violations: list[RuleViolation] = Field(
        default_factory=list, description="List of rule violations if not eligible"
    )


class RAGRetrieval(BaseModel):
    """A single RAG retrieval result for demo mode."""

    query: str = Field(..., description="The search query used")
    section_id: str = Field(..., description="Guide section identifier")
    section_title: str = Field(..., description="Title of the section")
    gse: Literal["fannie_mae", "freddie_mac"] = Field(..., description="Source GSE")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score (0-1)")
    snippet: str = Field(..., description="Text snippet from the section")


class ReasoningStep(BaseModel):
    """A single step in the reasoning chain for demo mode."""

    rule: str = Field(..., description="Rule being checked")
    product: Literal["HomeReady", "Home Possible"] = Field(..., description="Product being evaluated")
    check: str = Field(..., description="What is being checked")
    result: Literal["pass", "fail"] = Field(..., description="Result of the check")
    citation: str = Field(..., description="Guide citation")
    details: str = Field(..., description="Detailed explanation")


class IndexStats(BaseModel):
    """Statistics about the indexed guides."""

    total_pages: int = Field(default=4866, description="Total pages indexed")
    total_sections: int = Field(default=1203, description="Total sections indexed")
    total_vectors: int = Field(default=6174, description="Total vectors in the index")


class ParsedInput(BaseModel):
    """Parsed natural language input for demo mode."""

    raw_text: str = Field(..., description="Original input text")
    extracted_fields: dict[str, str | int | float | bool] = Field(
        default_factory=dict, description="Extracted field values"
    )


class DemoModeData(BaseModel):
    """Additional data returned in demo mode to showcase AI capabilities."""

    parsed_input: ParsedInput | None = Field(None, description="Parsed NL input if applicable")
    rag_retrievals: list[RAGRetrieval] = Field(
        default_factory=list, description="RAG retrieval results"
    )
    retrieval_time_ms: int = Field(default=0, description="Time taken for RAG retrieval")
    reasoning_steps: list[ReasoningStep] = Field(
        default_factory=list, description="Reasoning chain steps"
    )
    reasoning_time_ms: int = Field(default=0, description="Time taken for reasoning")
    tokens_input: int = Field(default=0, description="Input tokens used")
    tokens_output: int = Field(default=0, description="Output tokens used")
    index_stats: IndexStats = Field(
        default_factory=IndexStats,
        description="Index statistics"
    )


class EligibilityResult(BaseModel):
    """Complete eligibility check result."""

    scenario: LoanScenario = Field(..., description="The input scenario (echoed back)")
    calculated_ltv: float = Field(..., ge=0, le=2, description="Calculated LTV ratio")
    calculated_dti: float = Field(..., ge=0, le=2, description="Calculated DTI ratio")
    products: list[ProductResult] = Field(..., description="Results for each product")
    recommendation: str = Field(..., description="Summary recommendation")
    fix_suggestions: list[FixSuggestion] = Field(
        default_factory=list, description="Suggestions for becoming eligible"
    )
    demo_data: DemoModeData | None = Field(
        None, description="Demo mode data (only present when demo_mode=true)"
    )
    fix_finder_result: "FixFinderResult | None" = Field(
        None, description="Fix Finder Agent results (only present when enable_fix_finder=true and violations exist)"
    )
