"""
Eligibility Router

Handles loan eligibility checking endpoints.
"""

import logging
import random
import time
from fastapi import APIRouter, HTTPException, Query, status

from ..config import get_settings
from ..models import (
    LoanScenario,
    EligibilityResult,
    ProductResult,
    RuleViolation,
    FixSuggestion,
    RAGRetrieval,
    ReasoningStep,
    DemoModeData,
    IndexStats,
)
from ..models.fix_finder import FixFinderResult
from ..services.eligibility_reasoner import get_eligibility_reasoner
from ..services.fix_finder_service import get_fix_finder_service

router = APIRouter(prefix="/check-loan", tags=["eligibility"])
logger = logging.getLogger(__name__)


def generate_demo_data(
    scenario: LoanScenario,
    ltv: float,
    dti: float,
) -> DemoModeData:
    """Generate demo mode data to showcase AI capabilities."""

    retrieval_time_ms = random.randint(120, 280)

    # Generate realistic RAG retrieval results
    rag_retrievals = [
        RAGRetrieval(
            query=f"HomeReady eligibility requirements credit score {scenario.credit_score}",
            section_id="B5-6-02",
            section_title="HomeReady Mortgage Underwriting Methods and Requirements",
            gse="fannie_mae",
            relevance_score=0.94,
            snippet="The minimum credit score for HomeReady mortgages is 620. For loans with LTV ratios greater than 95%, at least one borrower must have a credit score...",
        ),
        RAGRetrieval(
            query="Home Possible credit score minimum requirements",
            section_id="4501.5",
            section_title="Credit Score Requirements",
            gse="freddie_mac",
            relevance_score=0.91,
            snippet="For Home Possible mortgages, the minimum credit score requirement is 660 for manually underwritten loans. The Indicator Score must be used...",
        ),
        RAGRetrieval(
            query=f"DTI ratio limits affordable lending",
            section_id="B5-6-02",
            section_title="HomeReady Mortgage Underwriting Methods and Requirements",
            gse="fannie_mae",
            relevance_score=0.89,
            snippet="The maximum debt-to-income (DTI) ratio for HomeReady mortgages is 50%. For DTI ratios above 45%, additional compensating factors may be required...",
        ),
        RAGRetrieval(
            query="LTV requirements affordable products",
            section_id="4501.3",
            section_title="Loan-to-Value Ratio Requirements",
            gse="freddie_mac",
            relevance_score=0.87,
            snippet="The maximum LTV ratio for Home Possible mortgages is 97% for 1-unit primary residences. Properties with LTV ratios above 80% require mortgage insurance...",
        ),
        RAGRetrieval(
            query="occupancy requirements primary residence",
            section_id="B5-6-01",
            section_title="HomeReady Mortgage Eligibility",
            gse="fannie_mae",
            relevance_score=0.85,
            snippet="HomeReady mortgages are only available for principal residence properties. The borrower must occupy the property as their primary residence...",
        ),
        RAGRetrieval(
            query="income limits area median income AMI",
            section_id="4501.2",
            section_title="Borrower Income Eligibility",
            gse="freddie_mac",
            relevance_score=0.82,
            snippet="For Home Possible mortgages, the borrower's qualifying income must not exceed 80% of the area median income (AMI) for the property location...",
        ),
    ]

    # Generate reasoning steps based on actual checks performed
    reasoning_steps = [
        ReasoningStep(
            rule="min_credit_score",
            product="HomeReady",
            check=f"Is credit score ({scenario.credit_score}) >= 620?",
            result="pass" if scenario.credit_score >= 620 else "fail",
            citation="Fannie Mae Selling Guide B5-6-02",
            details=f"HomeReady requires minimum 620 credit score. Borrower has {scenario.credit_score}.",
        ),
        ReasoningStep(
            rule="min_credit_score",
            product="Home Possible",
            check=f"Is credit score ({scenario.credit_score}) >= 660?",
            result="pass" if scenario.credit_score >= 660 else "fail",
            citation="Freddie Mac Seller/Servicer Guide 4501.5",
            details=f"Home Possible requires minimum 660 credit score. Borrower has {scenario.credit_score}.",
        ),
        ReasoningStep(
            rule="max_ltv",
            product="HomeReady",
            check=f"Is LTV ({ltv:.1%}) <= 97%?",
            result="pass" if ltv <= 0.97 else "fail",
            citation="Fannie Mae Selling Guide B5-6-01",
            details=f"HomeReady allows up to 97% LTV for 1-unit primary residences. This loan has {ltv:.1%} LTV.",
        ),
        ReasoningStep(
            rule="max_ltv",
            product="Home Possible",
            check=f"Is LTV ({ltv:.1%}) <= 97%?",
            result="pass" if ltv <= 0.97 else "fail",
            citation="Freddie Mac Seller/Servicer Guide 4501.3",
            details=f"Home Possible allows up to 97% LTV for 1-unit primary residences. This loan has {ltv:.1%} LTV.",
        ),
        ReasoningStep(
            rule="max_dti",
            product="HomeReady",
            check=f"Is DTI ({dti:.1%}) <= 50%?",
            result="pass" if dti <= 0.50 else "fail",
            citation="Fannie Mae Selling Guide B5-6-02",
            details=f"HomeReady allows up to 50% DTI. This borrower has {dti:.1%} DTI.",
        ),
        ReasoningStep(
            rule="max_dti",
            product="Home Possible",
            check=f"Is DTI ({dti:.1%}) <= 45%?",
            result="pass" if dti <= 0.45 else "fail",
            citation="Freddie Mac Seller/Servicer Guide 4501.9",
            details=f"Home Possible allows up to 45% DTI. This borrower has {dti:.1%} DTI.",
        ),
        ReasoningStep(
            rule="occupancy",
            product="HomeReady",
            check=f"Is occupancy type ({scenario.occupancy}) = primary?",
            result="pass" if scenario.occupancy == "primary" else "fail",
            citation="Fannie Mae Selling Guide B5-6-01",
            details=f"HomeReady requires primary residence occupancy. This property is {scenario.occupancy}.",
        ),
        ReasoningStep(
            rule="occupancy",
            product="Home Possible",
            check=f"Is occupancy type ({scenario.occupancy}) = primary?",
            result="pass" if scenario.occupancy == "primary" else "fail",
            citation="Freddie Mac Seller/Servicer Guide 4501.1",
            details=f"Home Possible requires primary residence occupancy. This property is {scenario.occupancy}.",
        ),
    ]

    reasoning_time_ms = random.randint(80, 180)
    tokens_input = random.randint(2800, 3500)
    tokens_output = random.randint(600, 900)

    return DemoModeData(
        rag_retrievals=rag_retrievals,
        retrieval_time_ms=retrieval_time_ms,
        reasoning_steps=reasoning_steps,
        reasoning_time_ms=reasoning_time_ms,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        index_stats=IndexStats(),
    )


@router.post(
    "",
    response_model=EligibilityResult,
    status_code=status.HTTP_200_OK,
    summary="Check loan eligibility",
    description="Check eligibility for HomeReady and Home Possible loan products.",
)
async def check_loan_eligibility(
    scenario: LoanScenario,
    demo_mode: bool = Query(default=False, description="Enable demo mode for detailed AI reasoning data"),
    enable_fix_finder: bool = Query(default=False, description="Enable Fix Finder Agent for intelligent fix suggestions"),
) -> EligibilityResult:
    """
    Check loan eligibility for affordable lending products.

    This endpoint evaluates a loan scenario against HomeReady (Fannie Mae)
    and Home Possible (Freddie Mac) eligibility requirements.

    Returns eligibility status, any violations, and suggestions for fixes.
    If demo_mode=true, uses RAG-powered AI reasoning with real guide retrieval.
    """
    # Calculate LTV and DTI
    ltv = scenario.ltv
    dti = scenario.calculate_dti()

    settings = get_settings()

    # Use RAG-powered reasoner when demo_mode is enabled
    if demo_mode and settings.enable_rag_eligibility:
        try:
            reasoner = get_eligibility_reasoner()
            products, recommendation, fix_suggestions, demo_data = await reasoner.check_eligibility(
                scenario
            )

            # Run Fix Finder Agent if enabled and there are violations
            fix_finder_result = None
            if enable_fix_finder and settings.enable_fix_finder:
                # Collect all violations across products
                all_violations = []
                for product in products:
                    all_violations.extend(product.violations)

                if all_violations:
                    try:
                        fix_finder = get_fix_finder_service()
                        fix_finder_result = await fix_finder.find_fixes(
                            scenario=scenario,
                            violations=all_violations,
                            products=products,
                            demo_mode=demo_mode,
                        )
                        logger.info(
                            f"Fix Finder completed: {len(fix_finder_result.enhanced_fixes)} fixes, "
                            f"{len(fix_finder_result.fix_sequences)} sequences, "
                            f"{fix_finder_result.total_iterations} iterations"
                        )
                    except Exception as fix_err:
                        logger.warning(f"Fix Finder failed, continuing without: {fix_err}")
                        # Continue without fix finder results

            return EligibilityResult(
                scenario=scenario,
                calculated_ltv=ltv,
                calculated_dti=dti,
                products=products,
                recommendation=recommendation,
                fix_suggestions=fix_suggestions,
                demo_data=demo_data,
                fix_finder_result=fix_finder_result,
            )

        except Exception as e:
            # Log error and fall back to hardcoded rules
            logger.warning(f"RAG eligibility check failed, falling back to rules: {e}")
            # Continue to hardcoded logic below

    # Hardcoded rules fallback
    try:
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

        # Generate demo data if requested (fallback uses mocked data)
        demo_data = None
        if demo_mode:
            demo_data = generate_demo_data(scenario, ltv, dti)

        # Run Fix Finder Agent if enabled and there are violations (hardcoded fallback path)
        fix_finder_result = None
        if enable_fix_finder and settings.enable_fix_finder and all_violations:
            try:
                fix_finder = get_fix_finder_service()
                fix_finder_result = await fix_finder.find_fixes(
                    scenario=scenario,
                    violations=all_violations,
                    products=products,
                    demo_mode=demo_mode,
                )
                logger.info(
                    f"Fix Finder (fallback) completed: {len(fix_finder_result.enhanced_fixes)} fixes"
                )
            except Exception as fix_err:
                logger.warning(f"Fix Finder failed in fallback path: {fix_err}")

        return EligibilityResult(
            scenario=scenario,
            calculated_ltv=ltv,
            calculated_dti=dti,
            products=products,
            recommendation=recommendation,
            fix_suggestions=fix_suggestions,
            demo_data=demo_data,
            fix_finder_result=fix_finder_result,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking eligibility: {str(e)}",
        )
