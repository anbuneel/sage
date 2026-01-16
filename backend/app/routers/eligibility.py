"""
Eligibility Router

Handles loan eligibility checking endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from ..models import (
    LoanScenario,
    EligibilityResult,
    ProductResult,
    RuleViolation,
    FixSuggestion,
)

router = APIRouter(prefix="/check-loan", tags=["eligibility"])


@router.post(
    "",
    response_model=EligibilityResult,
    status_code=status.HTTP_200_OK,
    summary="Check loan eligibility",
    description="Check eligibility for HomeReady and Home Possible loan products.",
)
async def check_loan_eligibility(scenario: LoanScenario) -> EligibilityResult:
    """
    Check loan eligibility for affordable lending products.

    This endpoint evaluates a loan scenario against HomeReady (Fannie Mae)
    and Home Possible (Freddie Mac) eligibility requirements.

    Returns eligibility status, any violations, and suggestions for fixes.
    """
    try:
        # Calculate LTV and DTI
        ltv = scenario.ltv
        dti = scenario.calculate_dti()

        # Mock eligibility results
        # TODO: Replace with actual RulesEngine integration
        homeready_violations = []
        home_possible_violations = []

        # Check credit score
        if scenario.credit_score < 620:
            homeready_violations.append(
                RuleViolation(
                    rule_name="min_credit_score",
                    rule_description="Minimum credit score requirement",
                    actual_value=str(scenario.credit_score),
                    required_value=">= 620",
                    citation="Fannie Mae B5-6-02",
                )
            )
        if scenario.credit_score < 660:
            home_possible_violations.append(
                RuleViolation(
                    rule_name="min_credit_score",
                    rule_description="Minimum credit score requirement",
                    actual_value=str(scenario.credit_score),
                    required_value=">= 660",
                    citation="Freddie Mac 4501.5",
                )
            )

        # Check LTV
        if ltv > 0.97:
            violation = RuleViolation(
                rule_name="max_ltv",
                rule_description="Maximum LTV ratio",
                actual_value=f"{ltv:.1%}",
                required_value="<= 97%",
                citation="Fannie Mae B5-6-01 / Freddie Mac 4501.5",
            )
            homeready_violations.append(violation)
            home_possible_violations.append(violation)

        # Check DTI
        if dti > 0.50:
            homeready_violations.append(
                RuleViolation(
                    rule_name="max_dti",
                    rule_description="Maximum DTI ratio",
                    actual_value=f"{dti:.1%}",
                    required_value="<= 50%",
                    citation="Fannie Mae B5-6-02",
                )
            )
        if dti > 0.45:
            home_possible_violations.append(
                RuleViolation(
                    rule_name="max_dti",
                    rule_description="Maximum DTI ratio",
                    actual_value=f"{dti:.1%}",
                    required_value="<= 45%",
                    citation="Freddie Mac 4501.5",
                )
            )

        # Check occupancy
        if scenario.occupancy != "primary":
            violation = RuleViolation(
                rule_name="occupancy",
                rule_description="Primary residence required",
                actual_value=scenario.occupancy,
                required_value="primary",
                citation="Fannie Mae B5-6-01 / Freddie Mac 4501.5",
            )
            homeready_violations.append(violation)
            home_possible_violations.append(violation)

        # Build product results
        products = [
            ProductResult(
                product_name="HomeReady",
                gse="fannie_mae",
                eligible=len(homeready_violations) == 0,
                violations=homeready_violations,
            ),
            ProductResult(
                product_name="Home Possible",
                gse="freddie_mac",
                eligible=len(home_possible_violations) == 0,
                violations=home_possible_violations,
            ),
        ]

        # Generate recommendation
        if all(p.eligible for p in products):
            recommendation = (
                "Great news! This scenario is eligible for both HomeReady and Home Possible. "
                "Consider comparing rates and fees from lenders offering both products."
            )
        elif any(p.eligible for p in products):
            eligible_product = next(p for p in products if p.eligible)
            recommendation = (
                f"This scenario is eligible for {eligible_product.product_name}. "
                "Review the violations for the other product to see what changes might expand options."
            )
        else:
            recommendation = (
                "This scenario is not currently eligible for either product. "
                "See the fix suggestions below for ways to become eligible."
            )

        # Generate fix suggestions based on violations
        fix_suggestions = []
        all_violations = homeready_violations + home_possible_violations

        if any(v.rule_name == "max_dti" for v in all_violations):
            fix_suggestions.append(
                FixSuggestion(
                    description="Pay down existing debt to reduce monthly payments",
                    impact=f"Reducing monthly debt by $200 would lower DTI to {(dti - 0.03):.1%}",
                    difficulty="moderate",
                )
            )
            fix_suggestions.append(
                FixSuggestion(
                    description="Consider a smaller loan amount",
                    impact="A 5% smaller loan would reduce the monthly payment and DTI",
                    difficulty="easy",
                )
            )

        if any(v.rule_name == "min_credit_score" for v in all_violations):
            fix_suggestions.append(
                FixSuggestion(
                    description="Work on improving credit score before applying",
                    impact="A higher credit score may also qualify for better rates",
                    difficulty="hard",
                )
            )

        if any(v.rule_name == "max_ltv" for v in all_violations):
            fix_suggestions.append(
                FixSuggestion(
                    description="Increase down payment to lower LTV",
                    impact=f"An additional ${(ltv - 0.97) * scenario.property_value:,.0f} down would bring LTV to 97%",
                    difficulty="moderate",
                )
            )

        return EligibilityResult(
            scenario=scenario,
            calculated_ltv=ltv,
            calculated_dti=dti,
            products=products,
            recommendation=recommendation,
            fix_suggestions=fix_suggestions,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking eligibility: {str(e)}",
        )
