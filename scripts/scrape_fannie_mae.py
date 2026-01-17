#!/usr/bin/env python3
"""
Scrape Fannie Mae Selling Guide from the web.

This script fetches all sections from the Fannie Mae Selling Guide website
and saves them as structured text files for embedding into Pinecone.

Usage:
    python scrape_fannie_mae.py
"""

import os
import re
import time
import json
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

# Base URL
BASE_URL = "https://selling-guide.fanniemae.com"

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "fannie_mae_guide"

# Rate limiting
REQUEST_DELAY = 1.0  # seconds between requests

# All section URLs from the table of contents
# Format: (section_id, url_path, title)
SECTIONS = [
    # Part A: Doing Business with Fannie Mae
    ("A1-1-01", "/sel/a1-1-01/application-and-approval-sellerservicer", "Application and Approval of Seller/Servicer"),
    ("A2-1-01", "/sel/a2-1-01/contractual-obligations-sellersservicers", "Contractual Obligations for Sellers/Servicers"),
    ("A2-1-02", "/sel/a2-1-02/nature-mortgage-transaction", "Nature of Mortgage Transaction"),
    ("A2-1-03", "/sel/a2-1-03/indemnification-losses", "Indemnification for Losses"),
    ("A2-2-01", "/sel/a2-2-01/representations-and-warranties-overview", "Representations and Warranties Overview"),
    ("A2-2-02", "/sel/a2-2-02/delivery-information-and-delivery-option-specific-representations-and-warranties", "Delivery Information and Delivery-Option Specific R&W"),
    ("A2-2-03", "/sel/a2-2-03/document-warranties", "Document Warranties"),
    ("A2-2-04", "/sel/a2-2-04/limited-waiver-and-enforcement-relief-representations-and-warranties", "Limited Waiver and Enforcement Relief"),
    ("A2-2-05", "/sel/a2-2-05/invalidation-limited-waiver-representations-and-warranties", "Invalidation of Limited Waiver"),
    ("A2-2-06", "/sel/a2-2-06/representations-and-warranties-property-value", "Representations and Warranties on Property Value"),
    ("A2-2-07", "/sel/a2-2-07/life-loan-representations-and-warranties", "Life-of-Loan Representations and Warranties"),
    ("A2-3.1-01", "/sel/a2-3.1-01/lender-breach-contract", "Lender Breach of Contract"),
    ("A2-3.1-02", "/sel/a2-3.1-02/sanctions-suspensions-and-terminations", "Sanctions, Suspensions, and Terminations"),
    ("A2-3.2-01", "/sel/a2-3.2-01/loan-repurchases-and-make-whole-payments-requested-fannie-mae", "Loan Repurchases and Make Whole Payments"),
    ("A2-3.2-02", "/sel/a2-3.2-02/enforcement-relief-breaches-certain-representations-and-warranties-related-underwriting-and", "Enforcement Relief for Breaches"),
    ("A2-3.2-03", "/sel/a2-3.2-03/remedies-framework", "Remedies Framework"),
    ("A2-3.3-01", "/sel/a2-3.3-01/compensatory-fees", "Compensatory Fees"),
    ("A2-4.1-01", "/sel/a2-4.1-01/establishing-loan-files", "Establishing Loan Files"),
    ("A2-4.1-02", "/sel/a2-4.1-02/ownership-and-retention-loan-files-and-records", "Ownership and Retention of Loan Files"),
    ("A2-4.1-03", "/sel/a2-4.1-03/electronic-records-signatures-and-transactions", "Electronic Records, Signatures, and Transactions"),
    ("A2-4.1-04", "/sel/a2-4.1-04/notarization-standards", "Notarization Standards"),
    ("A2-5-01", "/sel/a2-5-01/fannie-mae-trade-name-and-trademarks", "Fannie Mae Trade Name and Trademarks"),
    ("A3-1-01", "/sel/a3-1-01/fannie-maes-technology-products", "Fannie Mae's Technology Products"),
    ("A3-2-01", "/sel/a3-2-01/compliance-laws", "Compliance With Laws"),
    ("A3-2-02", "/sel/a3-2-02/responsible-lending-practices", "Responsible Lending Practices"),
    ("A3-3-01", "/sel/a3-3-01/outsourcing-mortgage-processing-and-third-party-originations", "Outsourcing of Mortgage Processing"),
    ("A3-3-02", "/sel/a3-3-02/concurrent-servicing-transfers", "Concurrent Servicing Transfers"),
    ("A3-3-03", "/sel/a3-3-03/other-servicing-arrangements", "Other Servicing Arrangements"),
    ("A3-3-04", "/sel/a3-3-04/document-custodians", "Document Custodians"),
    ("A3-3-05", "/sel/a3-3-05/custody-mortgage-documents", "Custody of Mortgage Documents"),
    ("A3-4-01", "/sel/a3-4-01/confidentiality-information", "Confidentiality of Information"),
    ("A3-4-02", "/sel/a3-4-02/data-quality-and-integrity", "Data Quality and Integrity"),
    ("A3-4-03", "/sel/a3-4-03/preventing-detecting-and-reporting-mortgage-fraud", "Preventing, Detecting, and Reporting Mortgage Fraud"),
    ("A3-5-01", "/sel/a3-5-01/fidelity-bond-and-errors-and-omissions-coverage-provisions", "Fidelity Bond and E&O Coverage Provisions"),
    ("A3-5-02", "/sel/a3-5-02/fidelity-bond-policy-requirements", "Fidelity Bond Policy Requirements"),
    ("A3-5-03", "/sel/a3-5-03/errors-and-omissions-policy-requirements", "Errors and Omissions Policy Requirements"),
    ("A3-5-04", "/sel/a3-5-04/reporting-fidelity-bond-and-errors-and-omissions-events", "Reporting Fidelity Bond and E&O Events"),
    ("A4-1-01", "/sel/a4-1-01/maintaining-sellerservicer-eligibility", "Maintaining Seller/Servicer Eligibility"),
    ("A4-1-02", "/sel/a4-1-02/submission-financial-statements-and-reports", "Submission of Financial Statements and Reports"),
    ("A4-1-03", "/sel/a4-1-03/report-changes-sellerservicers-organization", "Report of Changes in Organization"),
    ("A4-1-04", "/sel/a4-1-04/submission-irrevocable-limited-powers-attorney", "Submission of Irrevocable Limited Powers of Attorney"),

    # Part B: Origination Through Closing - Subpart B1
    ("B1-1-01", "/sel/b1-1-01/contents-application-package", "Contents of the Application Package"),
    ("B1-1-02", "/sel/b1-1-02/blanket-authorization-form", "Blanket Authorization Form"),
    ("B1-1-03", "/sel/b1-1-03/allowable-age-credit-documents-and-federal-income-tax-returns", "Allowable Age of Credit Documents and Tax Returns"),

    # Part B: Eligibility - B2-1
    ("B2-1.1-01", "/sel/b2-1.1-01/occupancy-types", "Occupancy Types"),
    ("B2-1.2-01", "/sel/b2-1.2-01/loan-value-ltv-ratios", "Loan-to-Value (LTV) Ratios"),
    ("B2-1.2-02", "/sel/b2-1.2-02/combined-loan-value-cltv-ratios", "Combined Loan-to-Value (CLTV) Ratios"),
    ("B2-1.2-03", "/sel/b2-1.2-03/home-equity-combined-loan-value-hcltv-ratios", "Home Equity CLTV (HCLTV) Ratios"),
    ("B2-1.2-04", "/sel/b2-1.2-04/subordinate-financing", "Subordinate Financing"),
    ("B2-1.3-01", "/sel/b2-1.3-01/purchase-transactions", "Purchase Transactions"),
    ("B2-1.3-02", "/sel/b2-1.3-02/limited-cash-out-refinance-transactions", "Limited Cash-Out Refinance Transactions"),
    ("B2-1.3-03", "/sel/b2-1.3-03/cash-out-refinance-transactions", "Cash-Out Refinance Transactions"),
    ("B2-1.3-04", "/sel/b2-1.3-04/prohibited-refinancing-practices", "Prohibited Refinancing Practices"),
    ("B2-1.3-05", "/sel/b2-1.3-05/payoff-installment-land-contract-requirements", "Payoff of Installment Land Contract Requirements"),
    ("B2-1.4-01", "/sel/b2-1.4-01/fixed-rate-loans", "Fixed-Rate Loans"),
    ("B2-1.4-02", "/sel/b2-1.4-02/adjustable-rate-mortgages-arms", "Adjustable-Rate Mortgages (ARMs)"),
    ("B2-1.4-03", "/sel/b2-1.4-03/convertible-arms", "Convertible ARMs"),
    ("B2-1.4-04", "/sel/b2-1.4-04/temporary-interest-rate-buydowns", "Temporary Interest Rate Buydowns"),
    ("B2-1.5-01", "/sel/b2-1.5-01/loan-limits", "Loan Limits"),
    ("B2-1.5-02", "/sel/b2-1.5-02/loan-eligibility", "Loan Eligibility"),
    ("B2-1.5-03", "/sel/b2-1.5-03/legal-requirements", "Legal Requirements"),
    ("B2-1.5-04", "/sel/b2-1.5-04/escrow-accounts", "Escrow Accounts"),
    ("B2-1.5-05", "/sel/b2-1.5-05/principal-curtailments", "Principal Curtailments"),

    # B2-2: Borrower Eligibility
    ("B2-2-01", "/sel/b2-2-01/general-borrower-eligibility-requirements", "General Borrower Eligibility Requirements"),
    ("B2-2-02", "/sel/b2-2-02/non-us-citizen-borrower-eligibility-requirements", "Non–U.S. Citizen Borrower Eligibility"),
    ("B2-2-03", "/sel/b2-2-03/multiple-financed-properties-same-borrower", "Multiple Financed Properties for Same Borrower"),
    ("B2-2-04", "/sel/b2-2-04/guarantors-co-signers-or-non-occupant-borrowers-subject-transaction", "Guarantors, Co-Signers, or Non-Occupant Borrowers"),
    ("B2-2-05", "/sel/b2-2-05/inter-vivos-revocable-trusts", "Inter Vivos Revocable Trusts"),
    ("B2-2-06", "/sel/b2-2-06/homeownership-education-and-housing-counseling", "Homeownership Education and Housing Counseling"),

    # B2-3: Property Eligibility
    ("B2-3-01", "/sel/b2-3-01/general-property-eligibility", "General Property Eligibility"),
    ("B2-3-02", "/sel/b2-3-02/special-property-eligibility-and-underwriting-considerations-factory-built-housing", "Special Property Eligibility: Factory-Built Housing"),
    ("B2-3-03", "/sel/b2-3-03/special-property-eligibility-and-underwriting-considerations-leasehold-estates", "Special Property Eligibility: Leasehold Estates"),
    ("B2-3-04", "/sel/b2-3-04/special-property-eligibility-considerations", "Special Property Eligibility Considerations"),
    ("B2-3-05", "/sel/b2-3-05/properties-affected-disaster", "Properties Affected by a Disaster"),

    # B3: Underwriting Borrowers
    ("B3-1-01", "/sel/b3-1-01/comprehensive-risk-assessment", "Comprehensive Risk Assessment"),
    ("B3-2-01", "/sel/b3-2-01/general-information-du", "General Information on DU"),
    ("B3-2-02", "/sel/b3-2-02/du-validation-service", "DU Validation Service"),
    ("B3-2-03", "/sel/b3-2-03/risk-factors-evaluated-du", "Risk Factors Evaluated by DU"),
    ("B3-2-04", "/sel/b3-2-04/du-documentation-requirements", "DU Documentation Requirements"),
    ("B3-2-05", "/sel/b3-2-05/approveeligible-recommendations", "Approve/Eligible Recommendations"),
    ("B3-2-06", "/sel/b3-2-06/approveineligible-recommendations", "Approve/Ineligible Recommendations"),
    ("B3-2-07", "/sel/b3-2-07/refer-caution-recommendations", "Refer with Caution Recommendations"),
    ("B3-2-08", "/sel/b3-2-08/out-scope-recommendations", "Out of Scope Recommendations"),
    ("B3-2-09", "/sel/b3-2-09/erroneous-credit-report-data", "Erroneous Credit Report Data"),
    ("B3-2-10", "/sel/b3-2-10/accuracy-du-data-du-tolerances-and-errors-credit-report", "Accuracy of DU Data, DU Tolerances, and Credit Report Errors"),
    ("B3-2-11", "/sel/b3-2-11/du-underwriting-findings-report", "DU Underwriting Findings Report"),

    # B3-3: Income Assessment
    ("B3-3.1-01", "/sel/b3-3.1-01/general-income-information", "General Income Information"),
    ("B3-3.1-02", "/sel/b3-3.1-02/standards-employment-documentation", "Standards for Employment Documentation"),
    ("B3-3.1-03", "/sel/b3-3.1-03/base-pay-salary-or-hourly-bonus-and-overtime-income", "Base Pay, Bonus, and Overtime Income"),
    ("B3-3.1-04", "/sel/b3-3.1-04/commission-income", "Commission Income"),
    ("B3-3.1-05", "/sel/b3-3.1-05/secondary-employment-income-second-job-and-multiple-jobs-and-seasonal-income", "Secondary Employment and Seasonal Income"),
    ("B3-3.1-06", "/sel/b3-3.1-06/requirements-and-uses-irs-ives-request-transcript-tax-return-form-4506-c", "Requirements and Uses of IRS IVES Form 4506-C"),
    ("B3-3.1-07", "/sel/b3-3.1-07/verbal-verification-employment", "Verbal Verification of Employment"),
    ("B3-3.1-08", "/sel/b3-3.1-08/rental-income", "Rental Income"),
    ("B3-3.1-09", "/sel/b3-3.1-09/other-sources-income", "Other Sources of Income"),
    ("B3-3.1-10", "/sel/b3-3.1-10/income-calculator", "Income Calculator"),
    ("B3-3.2-01", "/sel/b3-3.2-01/underwriting-factors-and-documentation-self-employed-borrower", "Underwriting Factors for Self-Employed Borrower"),
    ("B3-3.2-02", "/sel/b3-3.2-02/business-structures", "Business Structures"),
    ("B3-3.2-03", "/sel/b3-3.2-03/irs-forms-quick-reference", "IRS Forms Quick Reference"),

    # B3-4: Asset Assessment
    ("B3-4.1-01", "/sel/b3-4.1-01/minimum-reserve-requirements", "Minimum Reserve Requirements"),
    ("B3-4.1-02", "/sel/b3-4.1-02/interested-party-contributions-ipcs", "Interested Party Contributions (IPCs)"),
    ("B3-4.2-01", "/sel/b3-4.2-01/verification-deposits-and-assets", "Verification of Deposits and Assets"),
    ("B3-4.2-02", "/sel/b3-4.2-02/depository-accounts", "Depository Accounts"),
    ("B3-4.3-04", "/sel/b3-4.3-04/personal-gifts", "Personal Gifts"),
    ("B3-4.3-06", "/sel/b3-4.3-06/grants-and-lender-contributions", "Grants and Lender Contributions"),

    # B3-5: Credit Assessment
    ("B3-5.1-01", "/sel/b3-5.1-01/general-requirements-credit-scores", "General Requirements for Credit Scores"),
    ("B3-5.1-02", "/sel/b3-5.1-02/determining-credit-score-mortgage-loan", "Determining Credit Score for Mortgage Loan"),
    ("B3-5.2-01", "/sel/b3-5.2-01/requirements-credit-reports", "Requirements for Credit Reports"),
    ("B3-5.2-02", "/sel/b3-5.2-02/types-credit-reports", "Types of Credit Reports"),
    ("B3-5.3-01", "/sel/b3-5.3-01/number-and-age-accounts", "Number and Age of Accounts"),
    ("B3-5.3-02", "/sel/b3-5.3-02/payment-history", "Payment History"),
    ("B3-5.3-07", "/sel/b3-5.3-07/significant-derogatory-credit-events-waiting-periods-and-re-establishing-credit", "Significant Derogatory Credit Events"),

    # B3-6: Liability Assessment
    ("B3-6-01", "/sel/b3-6-01/general-information-liabilities", "General Information on Liabilities"),
    ("B3-6-02", "/sel/b3-6-02/debt-income-ratios", "Debt-to-Income Ratios"),
    ("B3-6-03", "/sel/b3-6-03/monthly-housing-expense-subject-property", "Monthly Housing Expense for Subject Property"),
    ("B3-6-04", "/sel/b3-6-04/qualifying-payment-requirements", "Qualifying Payment Requirements"),
    ("B3-6-05", "/sel/b3-6-05/monthly-debt-obligations", "Monthly Debt Obligations"),
    ("B3-6-06", "/sel/b3-6-06/qualifying-impact-other-real-estate-owned", "Qualifying Impact of Other Real Estate Owned"),

    # B5-6: HomeReady Mortgage (CRITICAL for our use case)
    ("B5-6-01", "/sel/b5-6-01/homeready-mortgage-loan-and-borrower-eligibility", "HomeReady Mortgage Loan and Borrower Eligibility"),
    ("B5-6-02", "/sel/b5-6-02/homeready-mortgage-underwriting-methods-and-requirements", "HomeReady Mortgage Underwriting Methods and Requirements"),
    ("B5-6-03", "/sel/b5-6-03/homeready-mortgage-loan-pricing-mortgage-insurance-and-special-feature-codes", "HomeReady Mortgage Pricing, Mortgage Insurance, Special Feature Codes"),

    # B5-7: High LTV Refinance
    ("B5-7-01", "/sel/b5-7-01/high-ltv-refinance-loan-and-borrower-eligibility", "High LTV Refinance Loan and Borrower Eligibility"),
    ("B5-7-02", "/sel/b5-7-02/high-ltv-refinance-underwriting-documentation-and-collateral-requirements-new-loan", "High LTV Refinance Underwriting, Documentation, Collateral"),

    # B5-1: High-Balance
    ("B5-1-01", "/sel/b5-1-01/high-balance-mortgage-loan-eligibility-and-underwriting", "High-Balance Mortgage Loan Eligibility and Underwriting"),

    # B5-2: Manufactured Housing
    ("B5-2-01", "/sel/b5-2-01/manufactured-housing", "Manufactured Housing"),
    ("B5-2-02", "/sel/b5-2-02/manufactured-housing-loan-eligibility", "Manufactured Housing Loan Eligibility"),

    # B4: Underwriting Property
    ("B4-1.1-01", "/sel/b4-1.1-01/definition-market-value", "Definition of Market Value"),
    ("B4-1.4-10", "/sel/b4-1.4-10/value-acceptance", "Value Acceptance"),
    ("B4-2.1-01", "/sel/b4-2.1-01/general-information-project-standards", "General Information on Project Standards"),
    ("B4-2.2-01", "/sel/b4-2.2-01/limited-review-process", "Limited Review Process"),
    ("B4-2.2-02", "/sel/b4-2.2-02/full-review-process", "Full Review Process"),

    # Part D: Quality Control
    ("D1-1-01", "/sel/d1-1-01/lender-quality-control-programs-plans-and-processes", "Lender Quality Control Programs, Plans, Processes"),
    ("D1-2-01", "/sel/d1-2-01/lender-prefunding-quality-control-review-process", "Lender Prefunding Quality Control Review Process"),
    ("D1-3-01", "/sel/d1-3-01/lender-post-closing-quality-control-review-process", "Lender Post-Closing Quality Control Review Process"),

    # Part E: Quick Reference
    ("E-1-01", "/sel/e-1-01/references-fannie-maes-website", "References to Fannie Mae's Website"),
    ("E-1-02", "/sel/e-1-02/list-contacts", "List of Contacts"),
]


def fetch_page(url: str) -> Optional[str]:
    """Fetch a page and return HTML content."""
    try:
        response = httpx.get(url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def extract_content(html: str) -> dict:
    """Extract main content from a Selling Guide page."""
    soup = BeautifulSoup(html, 'lxml')

    # Find the main content area
    # The guide typically has content in article or main tags
    content_area = soup.find('article') or soup.find('main') or soup.find('div', class_='content')

    if not content_area:
        # Fallback: get body
        content_area = soup.find('body')

    if not content_area:
        return {"title": "", "content": "", "html": html}

    # Get title
    title_elem = soup.find('h1')
    title = title_elem.get_text(strip=True) if title_elem else ""

    # Remove script and style elements
    for elem in content_area.find_all(['script', 'style', 'nav', 'header', 'footer']):
        elem.decompose()

    # Get text content
    text = content_area.get_text(separator='\n', strip=True)

    # Clean up excessive whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)

    return {
        "title": title,
        "content": text,
        "html": str(content_area),
    }


def save_section(section_id: str, title: str, content: str, url: str):
    """Save a section to a text file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create filename
    safe_id = section_id.replace('.', '-')
    filename = f"{safe_id}.txt"
    filepath = OUTPUT_DIR / filename

    # Format content with metadata
    output = f"""# {section_id}: {title}
Source: {url}
Section ID: {section_id}

---

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)

    return filepath


def scrape_all_sections():
    """Scrape all sections from the Selling Guide."""
    print("=" * 60)
    print("Fannie Mae Selling Guide Scraper")
    print("=" * 60)
    print(f"\nTotal sections to scrape: {len(SECTIONS)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Track progress
    success = 0
    failed = []

    for i, (section_id, url_path, title) in enumerate(SECTIONS):
        url = urljoin(BASE_URL, url_path)
        print(f"[{i+1}/{len(SECTIONS)}] Fetching {section_id}: {title[:50]}...")

        html = fetch_page(url)
        if not html:
            failed.append((section_id, url))
            continue

        # Extract content
        data = extract_content(html)

        # Use extracted title if available, otherwise use provided title
        final_title = data['title'] or title

        # Save
        filepath = save_section(section_id, final_title, data['content'], url)
        print(f"  Saved: {filepath.name} ({len(data['content']):,} chars)")

        success += 1

        # Rate limiting
        time.sleep(REQUEST_DELAY)

    print()
    print("=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Successful: {success}/{len(SECTIONS)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed sections:")
        for section_id, url in failed:
            print(f"  - {section_id}: {url}")

    # Save metadata
    metadata = {
        "source": "Fannie Mae Selling Guide",
        "base_url": BASE_URL,
        "total_sections": len(SECTIONS),
        "successful": success,
        "failed": [{"id": s, "url": u} for s, u in failed],
        "scrape_date": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(OUTPUT_DIR / "_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\nMetadata saved to: {OUTPUT_DIR / '_metadata.json'}")


def scrape_single_section(section_id: str):
    """Scrape a single section for testing."""
    section = None
    for s in SECTIONS:
        if s[0] == section_id:
            section = s
            break

    if not section:
        print(f"Section {section_id} not found")
        return

    section_id, url_path, title = section
    url = urljoin(BASE_URL, url_path)

    print(f"Fetching {section_id}: {title}")
    print(f"URL: {url}")

    html = fetch_page(url)
    if not html:
        print("Failed to fetch")
        return

    data = extract_content(html)

    print(f"\nTitle: {data['title']}")
    print(f"Content length: {len(data['content'])} chars")
    print("\nFirst 1000 chars:")
    print("-" * 40)
    print(data['content'][:1000])


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Scrape single section for testing
        scrape_single_section(sys.argv[1])
    else:
        # Scrape all sections
        scrape_all_sections()
