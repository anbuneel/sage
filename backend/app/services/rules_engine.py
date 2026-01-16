# backend/app/services/rules_engine.py
"""
SAGE Eligibility Rules Engine

This module implements the eligibility rules for Fannie Mae HomeReady and
Freddie Mac Home Possible mortgage products.

Rules are sourced from:
- Fannie Mae Selling Guide B5-6-01 (Loan and Borrower Eligibility)
- Fannie Mae Selling Guide B5-6-02 (Underwriting Methods and Requirements)
- Freddie Mac Guide 4501 (Home Possible Mortgages)
- Freddie Mac Guide 4501.5 (Underwriting Requirements)

Author: SAGE Rules Engine Agent
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# =============================================================================
# Data Classes (Using dataclasses to avoid Pydantic import conflicts)
# =============================================================================

@dataclass
class LoanScenario:
    """Input scenario for eligibility check."""
    credit_score: int
    annual_income: float
    is_first_time_buyer: bool
    loan_amount: float
    property_value: float
    loan_term_years: int
    monthly_debt_payments: float
    property_type: str
    property_state: str
    property_county: str
    occupancy: str = "primary"


@dataclass
class RuleViolation:
    """A single rule violation with citation."""
    rule_name: str
    rule_description: str
    actual_value: str
    required_value: str
    citation: str


@dataclass
class FixSuggestion:
    """An actionable suggestion to fix a violation."""
    description: str
    impact: str
    difficulty: str  # "easy" | "moderate" | "hard"


@dataclass
class ProductResult:
    """Eligibility result for a single product."""
    product_name: str
    gse: str
    eligible: bool
    violations: list = field(default_factory=list)


@dataclass
class EligibilityResult:
    """Complete eligibility result for all products."""
    scenario: LoanScenario
    calculated_ltv: float
    calculated_dti: float
    products: list = field(default_factory=list)
    recommendation: str = ""
    fix_suggestions: list = field(default_factory=list)


# =============================================================================
# Constants and Configuration
# =============================================================================

class PropertyType(Enum):
    """Supported property types."""
    SINGLE_FAMILY = "single_family"
    CONDO = "condo"
    PUD = "pud"
    TWO_UNIT = "2_unit"
    THREE_UNIT = "3_unit"
    FOUR_UNIT = "4_unit"
    MANUFACTURED = "manufactured"
    COOP = "coop"


class Occupancy(Enum):
    """Occupancy types."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    INVESTMENT = "investment"


# 2025/2026 Conforming Loan Limits
# Source: FHFA announcements
LOAN_LIMITS = {
    "base_2025": 806500,
    "base_2026": 832750,
    "high_cost_2025": 1209750,
    "high_cost_2026": 1249125,
}

# Current year limit to use (can be configured)
CURRENT_BASE_LIMIT = LOAN_LIMITS["base_2026"]
CURRENT_HIGH_COST_LIMIT = LOAN_LIMITS["high_cost_2026"]

# HomeReady eligible property types (Citation: Fannie Mae B5-6-01)
HOMEREADY_PROPERTY_TYPES = {
    "single_family", "condo", "pud", "2_unit", "3_unit", "4_unit", "manufactured", "coop"
}

# Home Possible eligible property types (Citation: Freddie Mac 4501.3)
HOME_POSSIBLE_PROPERTY_TYPES = {
    "single_family", "condo", "coop", "manufactured", "2_unit", "3_unit", "4_unit"
}


# =============================================================================
# Rules Engine Implementation
# =============================================================================

class RulesEngine:
    """
    Eligibility rules engine for HomeReady and Home Possible products.

    This engine evaluates loan scenarios against GSE guidelines and generates:
    1. Eligibility status for each product
    2. Detailed rule violations with citations
    3. Actionable fix suggestions

    Usage:
        engine = RulesEngine()
        result = engine.check_eligibility(scenario)
    """

    def __init__(self, base_loan_limit: int = CURRENT_BASE_LIMIT,
                 high_cost_limit: int = CURRENT_HIGH_COST_LIMIT):
        """
        Initialize the rules engine.

        Args:
            base_loan_limit: Conforming loan limit for base areas
            high_cost_limit: Conforming loan limit for high-cost areas
        """
        self.base_loan_limit = base_loan_limit
        self.high_cost_limit = high_cost_limit

    def calculate_ltv(self, loan_amount: float, property_value: float) -> float:
        """
        Calculate Loan-to-Value ratio.

        Args:
            loan_amount: Principal loan amount
            property_value: Appraised property value

        Returns:
            LTV as a decimal (e.g., 0.875 for 87.5%)
        """
        if property_value <= 0:
            return 1.0
        return loan_amount / property_value

    def calculate_dti(self, scenario: LoanScenario) -> float:
        """
        Calculate Debt-to-Income ratio.

        This calculation includes:
        - Monthly housing expense (principal, interest, taxes, insurance estimate)
        - Existing monthly debt payments

        Args:
            scenario: The loan scenario

        Returns:
            DTI as a decimal (e.g., 0.45 for 45%)

        Citation: Fannie Mae B3-6-02, Freddie Mac 5401.2
        """
        monthly_income = scenario.annual_income / 12

        if monthly_income <= 0:
            return 1.0

        # Estimate monthly housing payment (P&I + taxes + insurance)
        # Using simple calculation: assume 6% rate for estimation
        estimated_rate = 0.06
        monthly_rate = estimated_rate / 12
        num_payments = scenario.loan_term_years * 12

        # Monthly P&I calculation
        if monthly_rate > 0:
            monthly_pi = scenario.loan_amount * (
                monthly_rate * (1 + monthly_rate) ** num_payments
            ) / ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_pi = scenario.loan_amount / num_payments

        # Estimate taxes and insurance (approximately 1.5% of property value annually)
        monthly_taxes_insurance = (scenario.property_value * 0.015) / 12

        # Total monthly housing expense
        monthly_housing = monthly_pi + monthly_taxes_insurance

        # Total monthly debt obligations
        total_monthly_debt = monthly_housing + scenario.monthly_debt_payments

        return total_monthly_debt / monthly_income

    def check_eligibility(self, scenario: LoanScenario) -> EligibilityResult:
        """
        Main entry point for eligibility checking.

        Checks eligibility for both HomeReady and Home Possible products,
        then generates recommendations and fix suggestions.

        Args:
            scenario: The loan scenario to evaluate

        Returns:
            Complete EligibilityResult with all details
        """
        # Calculate key ratios
        ltv = self.calculate_ltv(scenario.loan_amount, scenario.property_value)
        dti = self.calculate_dti(scenario)

        # Check both products
        homeready_result = self.check_homeready(scenario, ltv, dti)
        home_possible_result = self.check_home_possible(scenario, ltv, dti)

        products = [homeready_result, home_possible_result]

        # Collect all violations for fix suggestions
        all_violations = homeready_result.violations + home_possible_result.violations

        # Generate fix suggestions
        fix_suggestions = self.generate_fix_suggestions(scenario, all_violations, ltv, dti)

        # Generate recommendation
        recommendation = self._generate_recommendation(
            homeready_result, home_possible_result, scenario
        )

        return EligibilityResult(
            scenario=scenario,
            calculated_ltv=round(ltv, 4),
            calculated_dti=round(dti, 4),
            products=products,
            recommendation=recommendation,
            fix_suggestions=fix_suggestions
        )

    def check_homeready(self, scenario: LoanScenario,
                        ltv: Optional[float] = None,
                        dti: Optional[float] = None) -> ProductResult:
        """
        Check eligibility for Fannie Mae HomeReady.

        HomeReady Requirements (Citation: Fannie Mae B5-6-01, B5-6-02):
        - Min credit score: 620
        - Max DTI: 50%
        - Max LTV: 97% (1-unit primary residence)
        - Income limit: <= 80% AMI (not checked here - requires AMI lookup)
        - Occupancy: Primary residence only
        - Property types: SFR, Condo, PUD, 2-4 unit, Manufactured, Co-op

        Args:
            scenario: The loan scenario
            ltv: Pre-calculated LTV (optional)
            dti: Pre-calculated DTI (optional)

        Returns:
            ProductResult with eligibility status and violations
        """
        violations = []

        # Calculate ratios if not provided
        if ltv is None:
            ltv = self.calculate_ltv(scenario.loan_amount, scenario.property_value)
        if dti is None:
            dti = self.calculate_dti(scenario)

        # Rule 1: Minimum Credit Score (Citation: B5-6-02)
        # HomeReady minimum is 620
        min_credit_score = 620
        if scenario.credit_score < min_credit_score:
            violations.append(RuleViolation(
                rule_name="min_credit_score",
                rule_description="Minimum credit score requirement",
                actual_value=str(scenario.credit_score),
                required_value=f">= {min_credit_score}",
                citation="Fannie Mae Selling Guide B5-6-02"
            ))

        # Rule 2: Maximum DTI (Citation: B5-6-02)
        # HomeReady allows up to 50% DTI
        max_dti = 0.50
        if dti > max_dti:
            violations.append(RuleViolation(
                rule_name="max_dti",
                rule_description="Maximum debt-to-income ratio",
                actual_value=f"{dti * 100:.1f}%",
                required_value=f"<= {max_dti * 100:.0f}%",
                citation="Fannie Mae Selling Guide B5-6-02"
            ))

        # Rule 3: Maximum LTV (Citation: B5-6-01)
        # 97% for 1-unit primary residence with DU
        # 95% for manually underwritten or manufactured housing
        if scenario.property_type == "manufactured":
            max_ltv = 0.95
            ltv_citation = "Fannie Mae Selling Guide B5-6-01 (Manufactured Housing)"
        elif scenario.property_type in ("2_unit", "3_unit", "4_unit"):
            max_ltv = 0.95  # Multi-unit has lower max LTV
            ltv_citation = "Fannie Mae Selling Guide B5-6-01 (Multi-unit)"
        else:
            max_ltv = 0.97
            ltv_citation = "Fannie Mae Selling Guide B5-6-01"

        if ltv > max_ltv:
            violations.append(RuleViolation(
                rule_name="max_ltv",
                rule_description="Maximum loan-to-value ratio",
                actual_value=f"{ltv * 100:.1f}%",
                required_value=f"<= {max_ltv * 100:.0f}%",
                citation=ltv_citation
            ))

        # Rule 4: Occupancy (Citation: B5-6-01)
        # Must be primary residence
        if scenario.occupancy.lower() != "primary":
            violations.append(RuleViolation(
                rule_name="occupancy",
                rule_description="Property must be primary residence",
                actual_value=scenario.occupancy,
                required_value="primary",
                citation="Fannie Mae Selling Guide B5-6-01"
            ))

        # Rule 5: Property Type (Citation: B5-6-01)
        if scenario.property_type.lower() not in HOMEREADY_PROPERTY_TYPES:
            violations.append(RuleViolation(
                rule_name="property_type",
                rule_description="Eligible property type",
                actual_value=scenario.property_type,
                required_value=", ".join(sorted(HOMEREADY_PROPERTY_TYPES)),
                citation="Fannie Mae Selling Guide B5-6-01"
            ))

        # Rule 6: Loan Amount (Citation: B5-6-01)
        # Must not exceed conforming loan limit
        # Note: High-cost area determination requires county lookup
        if scenario.loan_amount > self.high_cost_limit:
            violations.append(RuleViolation(
                rule_name="loan_limit",
                rule_description="Maximum conforming loan amount",
                actual_value=f"${scenario.loan_amount:,.0f}",
                required_value=f"<= ${self.high_cost_limit:,}",
                citation="Fannie Mae Selling Guide B5-6-01, FHFA Loan Limits"
            ))

        # Rule 7: Fixed-rate requirement for high LTV (Citation: B5-6-01)
        # LTV > 95% requires fixed-rate loan up to 30 years
        # (We assume all loans are fixed-rate for this check)
        if ltv > 0.95 and scenario.loan_term_years > 30:
            violations.append(RuleViolation(
                rule_name="loan_term",
                rule_description="Maximum loan term for high LTV",
                actual_value=f"{scenario.loan_term_years} years",
                required_value="<= 30 years",
                citation="Fannie Mae Selling Guide B5-6-01"
            ))

        eligible = len(violations) == 0

        return ProductResult(
            product_name="HomeReady",
            gse="fannie_mae",
            eligible=eligible,
            violations=violations
        )

    def check_home_possible(self, scenario: LoanScenario,
                            ltv: Optional[float] = None,
                            dti: Optional[float] = None) -> ProductResult:
        """
        Check eligibility for Freddie Mac Home Possible.

        Home Possible Requirements (Citation: Freddie Mac 4501, 4501.5):
        - Min credit score: 660 (for 1-unit fixed-rate purchase)
        - Max DTI: 45% (43% for LPA)
        - Max LTV: 97%
        - Income limit: <= 80% AMI (not checked here - requires AMI lookup)
        - Occupancy: Primary residence only
        - Property types: SFR, Condo, Co-op, Manufactured

        Args:
            scenario: The loan scenario
            ltv: Pre-calculated LTV (optional)
            dti: Pre-calculated DTI (optional)

        Returns:
            ProductResult with eligibility status and violations
        """
        violations = []

        # Calculate ratios if not provided
        if ltv is None:
            ltv = self.calculate_ltv(scenario.loan_amount, scenario.property_value)
        if dti is None:
            dti = self.calculate_dti(scenario)

        # Rule 1: Minimum Credit Score (Citation: 4501.5)
        # Varies by transaction type:
        # - 660 for 1-unit fixed-rate purchase
        # - 680 for 1-unit ARMs or no-cash-out refinance
        # - 700 for 2-4 unit properties
        # - 680 for manufactured homes
        if scenario.property_type in ("2_unit", "3_unit", "4_unit"):
            min_credit_score = 700
            score_citation = "Freddie Mac Guide 4501.5 (2-4 unit)"
        elif scenario.property_type == "manufactured":
            min_credit_score = 680
            score_citation = "Freddie Mac Guide 4501.5 (Manufactured Home)"
        else:
            min_credit_score = 660
            score_citation = "Freddie Mac Guide 4501.5"

        if scenario.credit_score < min_credit_score:
            violations.append(RuleViolation(
                rule_name="min_credit_score",
                rule_description="Minimum credit score requirement",
                actual_value=str(scenario.credit_score),
                required_value=f">= {min_credit_score}",
                citation=score_citation
            ))

        # Rule 2: Maximum DTI (Citation: 4501.5)
        # Home Possible allows up to 45% DTI (43% for LPA Accept)
        max_dti = 0.45
        if dti > max_dti:
            violations.append(RuleViolation(
                rule_name="max_dti",
                rule_description="Maximum debt-to-income ratio",
                actual_value=f"{dti * 100:.1f}%",
                required_value=f"<= {max_dti * 100:.0f}%",
                citation="Freddie Mac Guide 4501.5, 5401.2"
            ))

        # Rule 3: Maximum LTV (Citation: 4501.7)
        # 97% for 1-unit primary residence
        # 95% for manufactured housing
        if scenario.property_type == "manufactured":
            max_ltv = 0.95
            ltv_citation = "Freddie Mac Guide 4501.7, 5703.8 (Manufactured Home)"
        elif scenario.property_type in ("2_unit", "3_unit", "4_unit"):
            max_ltv = 0.95  # Multi-unit has lower max LTV
            ltv_citation = "Freddie Mac Guide 4501.7 (Multi-unit)"
        else:
            max_ltv = 0.97
            ltv_citation = "Freddie Mac Guide 4501.7"

        if ltv > max_ltv:
            violations.append(RuleViolation(
                rule_name="max_ltv",
                rule_description="Maximum loan-to-value ratio",
                actual_value=f"{ltv * 100:.1f}%",
                required_value=f"<= {max_ltv * 100:.0f}%",
                citation=ltv_citation
            ))

        # Rule 4: Occupancy (Citation: 4501.4)
        # Must be primary residence
        if scenario.occupancy.lower() != "primary":
            violations.append(RuleViolation(
                rule_name="occupancy",
                rule_description="Property must be primary residence",
                actual_value=scenario.occupancy,
                required_value="primary",
                citation="Freddie Mac Guide 4501.4"
            ))

        # Rule 5: Property Type (Citation: 4501.3)
        if scenario.property_type.lower() not in HOME_POSSIBLE_PROPERTY_TYPES:
            violations.append(RuleViolation(
                rule_name="property_type",
                rule_description="Eligible property type",
                actual_value=scenario.property_type,
                required_value=", ".join(sorted(HOME_POSSIBLE_PROPERTY_TYPES)),
                citation="Freddie Mac Guide 4501.3"
            ))

        # Rule 6: Loan Amount (Citation: 4203.1)
        # Must not exceed conforming loan limit
        if scenario.loan_amount > self.high_cost_limit:
            violations.append(RuleViolation(
                rule_name="loan_limit",
                rule_description="Maximum conforming loan amount",
                actual_value=f"${scenario.loan_amount:,.0f}",
                required_value=f"<= ${self.high_cost_limit:,}",
                citation="Freddie Mac Guide 4203.1, FHFA Loan Limits"
            ))

        eligible = len(violations) == 0

        return ProductResult(
            product_name="Home Possible",
            gse="freddie_mac",
            eligible=eligible,
            violations=violations
        )

    def generate_fix_suggestions(self, scenario: LoanScenario,
                                 violations: list,
                                 ltv: float,
                                 dti: float) -> list:
        """
        Generate actionable fix suggestions based on violations.

        This method analyzes the violations and generates specific,
        actionable recommendations with estimated impacts.

        Args:
            scenario: The loan scenario
            violations: List of all violations from both products
            ltv: Calculated LTV ratio
            dti: Calculated DTI ratio

        Returns:
            List of FixSuggestion objects
        """
        suggestions = []
        seen_rules = set()  # Avoid duplicate suggestions

        monthly_income = scenario.annual_income / 12

        for violation in violations:
            if violation.rule_name in seen_rules:
                continue
            seen_rules.add(violation.rule_name)

            if violation.rule_name == "min_credit_score":
                # Credit score improvement suggestion
                current_score = scenario.credit_score
                target_score = 660  # Home Possible minimum
                points_needed = target_score - current_score

                if points_needed > 0:
                    suggestions.append(FixSuggestion(
                        description=f"Improve credit score by {points_needed} points to reach {target_score}",
                        impact=f"Would meet Home Possible minimum credit requirement",
                        difficulty="moderate" if points_needed <= 30 else "hard"
                    ))

                    # Additional tip for larger gaps
                    if current_score < 620:
                        suggestions.append(FixSuggestion(
                            description=f"Improve credit score by {620 - current_score} points to reach 620",
                            impact="Would meet HomeReady minimum credit requirement",
                            difficulty="moderate" if (620 - current_score) <= 30 else "hard"
                        ))

            elif violation.rule_name == "max_dti":
                # DTI reduction suggestions
                # HomeReady max is 50%, Home Possible max is 45%
                target_dti_hp = 0.45  # Home Possible target
                target_dti_hr = 0.50  # HomeReady target

                # Calculate debt reduction needed for Home Possible
                current_debt_ratio = dti
                if current_debt_ratio > target_dti_hp:
                    # Monthly payment reduction needed
                    max_total_debt_hp = monthly_income * target_dti_hp
                    current_total_debt = monthly_income * current_debt_ratio
                    monthly_reduction_hp = current_total_debt - max_total_debt_hp

                    # Estimate total debt payoff (assuming avg rate of 7% over 5 years)
                    # Rough estimate: monthly payment * 50 = approximate total debt
                    debt_payoff_hp = monthly_reduction_hp * 50

                    suggestions.append(FixSuggestion(
                        description=f"Reduce monthly debt payments by ${monthly_reduction_hp:,.0f}/month",
                        impact=f"Would reduce DTI from {dti * 100:.1f}% to {target_dti_hp * 100:.0f}% (Home Possible eligible)",
                        difficulty="moderate"
                    ))

                    suggestions.append(FixSuggestion(
                        description=f"Pay off approximately ${debt_payoff_hp:,.0f} in debt",
                        impact=f"Would reduce DTI to meet Home Possible requirement",
                        difficulty="moderate" if debt_payoff_hp <= 10000 else "hard"
                    ))

                # If only over HomeReady limit (50%), suggest smaller reduction
                if current_debt_ratio > target_dti_hr and current_debt_ratio <= target_dti_hp + 0.10:
                    max_total_debt_hr = monthly_income * target_dti_hr
                    current_total_debt = monthly_income * current_debt_ratio
                    monthly_reduction_hr = current_total_debt - max_total_debt_hr

                    if monthly_reduction_hr > 0:
                        suggestions.append(FixSuggestion(
                            description=f"Reduce monthly debt by ${monthly_reduction_hr:,.0f}/month for HomeReady",
                            impact=f"Would reduce DTI from {dti * 100:.1f}% to {target_dti_hr * 100:.0f}%",
                            difficulty="easy" if monthly_reduction_hr <= 200 else "moderate"
                        ))

            elif violation.rule_name == "max_ltv":
                # LTV reduction suggestions (increase down payment)
                target_ltv = 0.97
                if scenario.property_type == "manufactured":
                    target_ltv = 0.95

                current_down = scenario.property_value - scenario.loan_amount
                target_loan = scenario.property_value * target_ltv
                additional_down = scenario.loan_amount - target_loan

                if additional_down > 0:
                    suggestions.append(FixSuggestion(
                        description=f"Increase down payment by ${additional_down:,.0f}",
                        impact=f"Would reduce LTV from {ltv * 100:.1f}% to {target_ltv * 100:.0f}%",
                        difficulty="easy" if additional_down <= 5000 else
                                   "moderate" if additional_down <= 20000 else "hard"
                    ))

                    # Alternative: lower purchase price
                    max_purchase = scenario.loan_amount / target_ltv
                    price_reduction = scenario.property_value - max_purchase

                    if price_reduction > 0:
                        suggestions.append(FixSuggestion(
                            description=f"Negotiate purchase price reduction of ${price_reduction:,.0f}",
                            impact=f"Would achieve {target_ltv * 100:.0f}% LTV with current down payment",
                            difficulty="moderate"
                        ))

            elif violation.rule_name == "occupancy":
                suggestions.append(FixSuggestion(
                    description="HomeReady and Home Possible require primary residence occupancy",
                    impact="Consider conventional financing options for investment or second homes",
                    difficulty="hard"
                ))

            elif violation.rule_name == "property_type":
                suggestions.append(FixSuggestion(
                    description="Consider a different property type that is eligible",
                    impact="Single-family homes, condos, and PUDs are eligible for both programs",
                    difficulty="hard"
                ))

            elif violation.rule_name == "loan_limit":
                over_limit = scenario.loan_amount - self.high_cost_limit
                suggestions.append(FixSuggestion(
                    description=f"Reduce loan amount by ${over_limit:,.0f}",
                    impact=f"Would bring loan under ${self.high_cost_limit:,} conforming limit",
                    difficulty="hard"
                ))

                suggestions.append(FixSuggestion(
                    description="Consider jumbo loan products instead",
                    impact="Jumbo loans have different eligibility requirements",
                    difficulty="moderate"
                ))

        # Sort suggestions by difficulty (easy first)
        difficulty_order = {"easy": 0, "moderate": 1, "hard": 2}
        suggestions.sort(key=lambda s: difficulty_order.get(s.difficulty, 1))

        return suggestions

    def _generate_recommendation(self, homeready: ProductResult,
                                 home_possible: ProductResult,
                                 scenario: LoanScenario) -> str:
        """
        Generate a summary recommendation based on results.

        Args:
            homeready: HomeReady eligibility result
            home_possible: Home Possible eligibility result
            scenario: The loan scenario

        Returns:
            Human-readable recommendation string
        """
        both_eligible = homeready.eligible and home_possible.eligible
        hr_only = homeready.eligible and not home_possible.eligible
        hp_only = home_possible.eligible and not homeready.eligible
        neither = not homeready.eligible and not home_possible.eligible

        if both_eligible:
            # Compare benefits
            if scenario.credit_score >= 700:
                return (
                    "Congratulations! You are eligible for both HomeReady (Fannie Mae) and "
                    "Home Possible (Freddie Mac). With your credit score of "
                    f"{scenario.credit_score}, you may qualify for better pricing through "
                    "either program. Compare lender offerings for both programs to find "
                    "the best rate and terms."
                )
            else:
                return (
                    "Congratulations! You are eligible for both HomeReady (Fannie Mae) and "
                    "Home Possible (Freddie Mac). Both programs offer similar benefits including "
                    "low down payment options and reduced mortgage insurance costs. "
                    "Shop multiple lenders to compare rates."
                )

        elif hr_only:
            return (
                "You are eligible for Fannie Mae HomeReady but not Freddie Mac Home Possible. "
                f"HomeReady has a lower credit score requirement (620 vs 660) and allows up to "
                "50% DTI (vs 45%). Work with a lender who offers HomeReady to proceed."
            )

        elif hp_only:
            return (
                "You are eligible for Freddie Mac Home Possible but not Fannie Mae HomeReady. "
                "Home Possible offers similar benefits including low down payment and income "
                "limit flexibility. Work with a lender who offers Home Possible to proceed."
            )

        else:  # neither
            # Analyze which is closer to eligibility
            hr_violations = len(homeready.violations)
            hp_violations = len(home_possible.violations)

            if hr_violations <= hp_violations:
                return (
                    f"You are not currently eligible for either program. HomeReady (Fannie Mae) "
                    f"has {hr_violations} violation(s) and Home Possible (Freddie Mac) has "
                    f"{hp_violations} violation(s). Review the fix suggestions below - "
                    "HomeReady may be easier to qualify for with its more flexible requirements."
                )
            else:
                return (
                    f"You are not currently eligible for either program. Home Possible has "
                    f"{hp_violations} violation(s) compared to HomeReady's {hr_violations}. "
                    "Review the fix suggestions below to see how you can become eligible."
                )


# =============================================================================
# Convenience Functions
# =============================================================================

def check_loan_eligibility(
    credit_score: int,
    annual_income: float,
    is_first_time_buyer: bool,
    loan_amount: float,
    property_value: float,
    loan_term_years: int = 30,
    monthly_debt_payments: float = 0,
    property_type: str = "single_family",
    property_state: str = "",
    property_county: str = "",
    occupancy: str = "primary"
) -> EligibilityResult:
    """
    Convenience function to check eligibility without creating objects.

    This function creates the LoanScenario and RulesEngine internally.

    Args:
        credit_score: Borrower's credit score
        annual_income: Gross annual income
        is_first_time_buyer: Whether borrower is first-time buyer
        loan_amount: Requested loan amount
        property_value: Property appraised value
        loan_term_years: Loan term in years (default 30)
        monthly_debt_payments: Monthly debt obligations (default 0)
        property_type: Type of property (default "single_family")
        property_state: State abbreviation
        property_county: County name
        occupancy: Occupancy type (default "primary")

    Returns:
        EligibilityResult with full details
    """
    scenario = LoanScenario(
        credit_score=credit_score,
        annual_income=annual_income,
        is_first_time_buyer=is_first_time_buyer,
        loan_amount=loan_amount,
        property_value=property_value,
        loan_term_years=loan_term_years,
        monthly_debt_payments=monthly_debt_payments,
        property_type=property_type,
        property_state=property_state,
        property_county=property_county,
        occupancy=occupancy
    )

    engine = RulesEngine()
    return engine.check_eligibility(scenario)


# =============================================================================
# Module Testing
# =============================================================================

if __name__ == "__main__":
    # Example usage and basic test
    print("SAGE Rules Engine - Test Run")
    print("=" * 60)

    # Test scenario 1: Eligible for both
    result = check_loan_eligibility(
        credit_score=720,
        annual_income=85000,
        is_first_time_buyer=True,
        loan_amount=350000,
        property_value=400000,
        monthly_debt_payments=400,
        property_type="single_family",
        property_state="CA",
        property_county="Los Angeles"
    )

    print("\nTest 1: High credit score, low DTI")
    print(f"  LTV: {result.calculated_ltv * 100:.1f}%")
    print(f"  DTI: {result.calculated_dti * 100:.1f}%")
    print(f"  HomeReady Eligible: {result.products[0].eligible}")
    print(f"  Home Possible Eligible: {result.products[1].eligible}")
    print(f"  Recommendation: {result.recommendation[:100]}...")

    # Test scenario 2: Low credit score
    result2 = check_loan_eligibility(
        credit_score=610,
        annual_income=65000,
        is_first_time_buyer=True,
        loan_amount=250000,
        property_value=275000,
        monthly_debt_payments=600,
        property_type="single_family",
        property_state="TX",
        property_county="Harris"
    )

    print("\nTest 2: Low credit score")
    print(f"  Credit Score: 610")
    print(f"  HomeReady Eligible: {result2.products[0].eligible}")
    print(f"  Home Possible Eligible: {result2.products[1].eligible}")
    if result2.products[0].violations:
        print(f"  HomeReady Violations: {[v.rule_name for v in result2.products[0].violations]}")
    if result2.fix_suggestions:
        print(f"  First Fix Suggestion: {result2.fix_suggestions[0].description}")

    # Test scenario 3: High DTI
    result3 = check_loan_eligibility(
        credit_score=680,
        annual_income=60000,
        is_first_time_buyer=False,
        loan_amount=320000,
        property_value=350000,
        monthly_debt_payments=1200,
        property_type="condo",
        property_state="FL",
        property_county="Miami-Dade"
    )

    print("\nTest 3: High DTI")
    print(f"  DTI: {result3.calculated_dti * 100:.1f}%")
    print(f"  HomeReady Eligible: {result3.products[0].eligible}")
    print(f"  Home Possible Eligible: {result3.products[1].eligible}")
    if result3.fix_suggestions:
        print(f"  Fix Suggestions ({len(result3.fix_suggestions)}):")
        for i, sug in enumerate(result3.fix_suggestions[:3], 1):
            print(f"    {i}. {sug.description} ({sug.difficulty})")

    print("\n" + "=" * 60)
    print("All tests completed.")
