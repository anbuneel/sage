#!/usr/bin/env python3
"""
SAGE Loan Scenario Test Suite

Automated tests for verifying eligibility rules against known scenarios.
Run with: python scripts/test_scenarios.py
"""

import httpx
import asyncio
from dataclasses import dataclass
from typing import Literal

API_BASE = "http://localhost:8000/api"


@dataclass
class TestScenario:
    """A test scenario with expected results."""
    name: str
    scenario: dict
    expected_homeready: bool
    expected_home_possible: bool
    notes: str = ""


# =============================================================================
# OFFICIAL SOURCES FOR VERIFICATION
# =============================================================================
#
# FANNIE MAE HOMEREADY:
#   Selling Guide Chapter B5-6: HomeReady Mortgage
#   https://selling-guide.fanniemae.com/Selling-Guide/Origination-thru-Closing/Subpart-B5-Unique-Eligibility-Underwriting-Considerations/Chapter-B5-6-HomeReady-Mortgage/
#
#   Key Sections:
#   - B5-6-01: Loan and Borrower Eligibility
#   - B5-6-02: Underwriting Considerations (credit, DTI, LTV)
#   - B5-6-03: Pricing and Delivery
#
# FREDDIE MAC HOME POSSIBLE:
#   Single-Family Seller/Servicer Guide Section 4501
#   https://guide.freddiemac.com/app/guide/section/4501
#
#   Key Sections:
#   - 4501.5: Eligibility Requirements
#   - 4501.9: Additional Requirements
#   - 5201: Credit Assessment
#
# =============================================================================

# Test scenarios based on official guidelines
TEST_SCENARIOS = [
    # =========================================================================
    # SHOULD PASS BOTH
    # =========================================================================
    TestScenario(
        name="Ideal borrower - passes both",
        scenario={
            "credit_score": 720,
            "annual_income": 75000,
            "is_first_time_buyer": True,
            "loan_amount": 350000,
            "property_value": 400000,  # LTV = 87.5%
            "loan_term_years": 30,
            "monthly_debt_payments": 500,
            "property_type": "single_family",
            "property_state": "CA",
            "property_county": "Los Angeles",
            "occupancy": "primary",
        },
        expected_homeready=True,
        expected_home_possible=True,
        # VERIFY: All values comfortably within limits for both programs
        notes="Strong credit, good LTV, reasonable DTI",
    ),
    TestScenario(
        name="Minimum viable HomeReady - credit 620",
        scenario={
            "credit_score": 620,
            "annual_income": 80000,
            "is_first_time_buyer": True,
            "loan_amount": 300000,
            "property_value": 350000,
            "loan_term_years": 30,
            "monthly_debt_payments": 400,
            "property_type": "single_family",
            "property_state": "TX",
            "property_county": "Harris",
            "occupancy": "primary",
        },
        expected_homeready=True,
        expected_home_possible=False,  # Needs 660 min credit
        # VERIFY AGAINST:
        #   HomeReady min credit: Fannie Mae B5-6-02 states 620 minimum
        #   Home Possible min credit: Freddie Mac 4501.5 states 660 minimum
        notes="620 credit passes HomeReady but fails Home Possible (660 min)",
    ),
    TestScenario(
        name="Max LTV 97% - passes both",
        scenario={
            "credit_score": 700,
            "annual_income": 90000,
            "is_first_time_buyer": True,
            "loan_amount": 388000,
            "property_value": 400000,  # LTV = 97%
            "loan_term_years": 30,
            "monthly_debt_payments": 600,
            "property_type": "single_family",
            "property_state": "FL",
            "property_county": "Miami-Dade",
            "occupancy": "primary",
        },
        expected_homeready=True,
        expected_home_possible=True,
        # VERIFY AGAINST:
        #   HomeReady max LTV: Fannie Mae B5-6-01 states 97% for 1-unit primary
        #   Home Possible max LTV: Freddie Mac 4501.5 states 97%
        notes="97% LTV is the maximum allowed for both programs",
    ),

    # =========================================================================
    # SHOULD FAIL BOTH
    # =========================================================================
    TestScenario(
        name="LTV too high (98%) - fails both",
        scenario={
            "credit_score": 750,
            "annual_income": 100000,
            "is_first_time_buyer": True,
            "loan_amount": 392000,
            "property_value": 400000,  # LTV = 98%
            "loan_term_years": 30,
            "monthly_debt_payments": 500,
            "property_type": "single_family",
            "property_state": "CA",
            "property_county": "San Diego",
            "occupancy": "primary",
        },
        expected_homeready=False,
        expected_home_possible=False,
        # VERIFY AGAINST:
        #   HomeReady max LTV: Fannie Mae B5-6-01 states 97% max for 1-unit
        #   Home Possible max LTV: Freddie Mac 4501.5 states 97% max
        notes="98% LTV exceeds 97% max for both programs",
    ),
    TestScenario(
        name="Credit too low (580) - fails both",
        scenario={
            "credit_score": 580,
            "annual_income": 70000,
            "is_first_time_buyer": True,
            "loan_amount": 250000,
            "property_value": 300000,
            "loan_term_years": 30,
            "monthly_debt_payments": 300,
            "property_type": "single_family",
            "property_state": "AZ",
            "property_county": "Maricopa",
            "occupancy": "primary",
        },
        expected_homeready=False,  # Needs 620
        expected_home_possible=False,  # Needs 660
        # VERIFY AGAINST:
        #   HomeReady min credit: Fannie Mae B5-6-02 states 620 minimum
        #   Home Possible min credit: Freddie Mac 4501.5 states 660 minimum
        notes="580 credit below both minimums (620/660)",
    ),
    TestScenario(
        name="Investment property - fails both",
        scenario={
            "credit_score": 750,
            "annual_income": 150000,
            "is_first_time_buyer": False,
            "loan_amount": 300000,
            "property_value": 400000,
            "loan_term_years": 30,
            "monthly_debt_payments": 500,
            "property_type": "single_family",
            "property_state": "NV",
            "property_county": "Clark",
            "occupancy": "investment",
        },
        expected_homeready=False,
        expected_home_possible=False,
        # VERIFY AGAINST:
        #   HomeReady occupancy: Fannie Mae B5-6-01 requires principal residence
        #   Home Possible occupancy: Freddie Mac 4501.5 requires primary residence
        notes="Both programs require primary residence occupancy",
    ),
    TestScenario(
        name="DTI too high (55%) - fails both",
        scenario={
            "credit_score": 720,
            "annual_income": 60000,  # $5000/mo
            "is_first_time_buyer": True,
            "loan_amount": 350000,
            "property_value": 400000,
            "loan_term_years": 30,
            "monthly_debt_payments": 1500,  # High existing debt
            "property_type": "single_family",
            "property_state": "WA",
            "property_county": "King",
            "occupancy": "primary",
        },
        expected_homeready=False,  # Max 50%
        expected_home_possible=False,  # Max 45%
        # VERIFY AGAINST:
        #   HomeReady max DTI: Fannie Mae B5-6-02 states 50% max (DU may allow higher)
        #   Home Possible max DTI: Freddie Mac 4501.5 states 45% max (43% for LPA)
        notes="High DTI fails both (HomeReady max 50%, Home Possible max 45%)",
    ),

    # =========================================================================
    # EDGE CASES - HOMEREADY ONLY
    # =========================================================================
    TestScenario(
        name="Credit 640 - HomeReady only",
        scenario={
            "credit_score": 640,
            "annual_income": 85000,
            "is_first_time_buyer": True,
            "loan_amount": 320000,
            "property_value": 380000,
            "loan_term_years": 30,
            "monthly_debt_payments": 500,
            "property_type": "single_family",
            "property_state": "CO",
            "property_county": "Denver",
            "occupancy": "primary",
        },
        expected_homeready=True,  # 620 min
        expected_home_possible=False,  # 660 min
        # VERIFY AGAINST:
        #   HomeReady min credit: Fannie Mae B5-6-02 states 620 minimum
        #   Home Possible min credit: Freddie Mac 4501.5 states 660 minimum
        #   640 is between these thresholds
        notes="640 credit: passes HomeReady (620), fails Home Possible (660)",
    ),
    TestScenario(
        name="DTI 48% - HomeReady only",
        scenario={
            "credit_score": 700,
            "annual_income": 72000,  # $6000/mo
            "is_first_time_buyer": True,
            "loan_amount": 300000,
            "property_value": 350000,
            "loan_term_years": 30,
            "monthly_debt_payments": 1100,  # Results in ~48% DTI
            "property_type": "single_family",
            "property_state": "OR",
            "property_county": "Multnomah",
            "occupancy": "primary",
        },
        expected_homeready=True,  # Max 50%
        expected_home_possible=False,  # Max 45%
        # VERIFY AGAINST:
        #   HomeReady max DTI: Fannie Mae B5-6-02 states 50% max
        #   Home Possible max DTI: Freddie Mac 4501.5 states 45% max
        #   48% is between these thresholds
        notes="48% DTI: passes HomeReady (50% max), fails Home Possible (45% max)",
    ),

    # =========================================================================
    # PROPERTY TYPE TESTS
    # =========================================================================
    TestScenario(
        name="Condo - passes both",
        scenario={
            "credit_score": 700,
            "annual_income": 80000,
            "is_first_time_buyer": True,
            "loan_amount": 280000,
            "property_value": 320000,
            "loan_term_years": 30,
            "monthly_debt_payments": 400,
            "property_type": "condo",
            "property_state": "IL",
            "property_county": "Cook",
            "occupancy": "primary",
        },
        expected_homeready=True,
        expected_home_possible=True,
        # VERIFY AGAINST:
        #   HomeReady property types: Fannie Mae B5-6-01 allows condos
        #   Home Possible property types: Freddie Mac 4501.5 allows condos
        notes="Condos are eligible for both programs",
    ),
    TestScenario(
        name="2-unit property - passes both",
        scenario={
            "credit_score": 720,
            "annual_income": 95000,
            "is_first_time_buyer": False,
            "loan_amount": 400000,
            "property_value": 500000,
            "loan_term_years": 30,
            "monthly_debt_payments": 600,
            "property_type": "2_unit",
            "property_state": "MA",
            "property_county": "Suffolk",
            "occupancy": "primary",
        },
        expected_homeready=True,
        expected_home_possible=True,
        # VERIFY AGAINST:
        #   HomeReady property types: Fannie Mae B5-6-01 allows 2-4 units (owner-occupied)
        #   Home Possible property types: Freddie Mac 4501.5 allows 2-4 units (owner-occupied)
        #   Note: LTV limits may differ for multi-unit properties
        notes="2-unit with owner occupancy is eligible",
    ),
]


async def run_scenario(client: httpx.AsyncClient, test: TestScenario) -> dict:
    """Run a single test scenario and return results."""
    try:
        response = await client.post(
            f"{API_BASE}/check-loan",
            json=test.scenario,
            timeout=30.0,
        )
        response.raise_for_status()
        result = response.json()

        # Parse products array from API response
        products = result.get("products", [])
        homeready_result = next((p for p in products if p["product_name"] == "HomeReady"), {})
        home_possible_result = next((p for p in products if p["product_name"] == "Home Possible"), {})

        homeready_eligible = homeready_result.get("eligible", False)
        home_possible_eligible = home_possible_result.get("eligible", False)

        homeready_pass = homeready_eligible == test.expected_homeready
        home_possible_pass = home_possible_eligible == test.expected_home_possible

        return {
            "name": test.name,
            "passed": homeready_pass and home_possible_pass,
            "homeready": {
                "expected": test.expected_homeready,
                "actual": homeready_eligible,
                "pass": homeready_pass,
                "violations": homeready_result.get("violations", []),
            },
            "home_possible": {
                "expected": test.expected_home_possible,
                "actual": home_possible_eligible,
                "pass": home_possible_pass,
                "violations": home_possible_result.get("violations", []),
            },
            "notes": test.notes,
            "error": None,
        }
    except Exception as e:
        return {
            "name": test.name,
            "passed": False,
            "error": str(e),
        }


async def run_all_tests():
    """Run all test scenarios and print results."""
    print("=" * 70)
    print("SAGE Loan Scenario Test Suite")
    print("=" * 70)
    print()

    async with httpx.AsyncClient() as client:
        # Check if API is running
        try:
            health = await client.get(f"{API_BASE}/health", timeout=5.0)
            health.raise_for_status()
            print("[PASS] API is running\n")
        except Exception as e:
            print(f"[FAIL] API not available at {API_BASE}")
            print(f"  Error: {e}")
            print("\n  Make sure the backend is running:")
            print("  cd backend && uvicorn app.main:app --reload")
            return

        results = []
        for test in TEST_SCENARIOS:
            result = await run_scenario(client, test)
            results.append(result)

        # Print results
        passed = 0
        failed = 0

        for result in results:
            if result.get("error"):
                print(f"[FAIL] {result['name']}")
                print(f"  ERROR: {result['error']}")
                failed += 1
                continue

            if result["passed"]:
                print(f"[PASS] {result['name']}")
                passed += 1
            else:
                print(f"[FAIL] {result['name']}")
                failed += 1

                # Show details for failures
                hr = result["homeready"]
                hp = result["home_possible"]

                if not hr["pass"]:
                    print(f"  HomeReady: expected {hr['expected']}, got {hr['actual']}")
                    if hr.get("violations"):
                        for v in hr["violations"][:2]:
                            print(f"    - {v.get('rule', 'Unknown')}: {v.get('message', '')}")

                if not hp["pass"]:
                    print(f"  Home Possible: expected {hp['expected']}, got {hp['actual']}")
                    if hp.get("violations"):
                        for v in hp["violations"][:2]:
                            print(f"    - {v.get('rule', 'Unknown')}: {v.get('message', '')}")

            if result.get("notes"):
                print(f"  Note: {result['notes']}")
            print()

        # Summary
        print("=" * 70)
        print(f"Results: {passed} passed, {failed} failed, {len(results)} total")
        print("=" * 70)

        if failed == 0:
            print("\n[PASS] All tests passed!")
        else:
            print(f"\n[FAIL] {failed} test(s) failed - review rules engine")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
