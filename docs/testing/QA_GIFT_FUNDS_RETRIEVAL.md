# QA Test: Gift Funds Documentation Retrieval

> Test Date: January 2026
> Status: **ISSUE IDENTIFIED** - Fannie Mae content not retrieved

## Test Case

**Query:** "How do I document gift funds?"

This is a common underwriting question used by Fannie Mae as their demo example for AskPoli (see Quality Insider Newsletter, March 2025).

---

## Expected Behavior

SAGE should return gift fund documentation requirements from **both GSEs**:
- Fannie Mae Selling Guide section B3-4.3-04 (Personal Gifts)
- Freddie Mac Seller/Servicer Guide section 5501 or equivalent

---

## Actual Behavior

SAGE returned **Freddie Mac content only** and explicitly stated:

> "The context provided does not include specific Fannie Mae gift fund documentation requirements for comparison"

This is a **retrieval failure** since the Fannie Mae Selling Guide is indexed (4,866 pages total).

---

## Comparison: AskPoli vs SAGE

### AskPoli's Answer (Fannie Mae)

**Documentation Requirements:**
- Gifts must be evidenced by a letter signed by the donor (gift letter)
- When sourced by a trust/estate, gift letter must be signed by donor and list trust/estate name

**Gift letter must include:**
- Actual or maximum dollar amount of the gift
- Donor's statement that no repayment is expected
- Donor's name, address, telephone number, and **relationship to borrower**

**Pooled Funds Special Case:**
- Certification that donor lived with borrower for past 12 months
- Documents demonstrating shared residency history

**DU Integration Note:**
- If gift amount differs from underwriting amount, may need to resubmit to DU per B3-2-10

### SAGE's Answer (Freddie Mac Only)

**Gift Letter Requirements:**
- Must be signed by the donor
- For trusts/estates, signed by trustee or authorized representative
- Must state donor's name and that funds are from a Related Person
- Must include donor's mailing address and telephone number
- Must state actual or maximum amount
- Must establish funds are a gift (no repayment)

**Evidence of Receipt (detailed):**
- Bank statements, canceled gift check, withdrawal/deposit slips
- Cashier's check or wire transfer to settlement agent
- Third-party money transfer apps (with documentation)
- Gift of equity on Settlement/Closing Disclosure

**Special Gift Categories:**
- Wedding gifts: marriage license + deposit within 90 days
- Graduation gifts: evidence of graduation + deposit within 90 days
- Agency gifts/grants: program documentation + no repayment + receipt evidence

---

## Gap Analysis

| Aspect | AskPoli | SAGE | Gap |
|--------|---------|------|-----|
| **GSE Covered** | Fannie Mae | Freddie Mac | SAGE missing Fannie Mae |
| **Gift Letter Requirements** | Complete | Complete (Freddie) | Different terminology |
| **Donor Relationship** | Explicitly required | "Related Person" mentioned | Less clear in SAGE |
| **Pooled Funds/Shared Residency** | Covered | Not mentioned | Missing edge case |
| **Evidence of Receipt** | Not detailed | Very detailed | SAGE stronger here |
| **Special Gift Types** | Not mentioned | Wedding/graduation covered | SAGE stronger here |
| **DU Integration Notes** | Included | Not mentioned | Missing operational detail |

---

## Quality Assessment

| Metric | Rating | Notes |
|--------|--------|-------|
| **Factual Accuracy** | ✅ High | Freddie Mac content appears correct |
| **Completeness** | ⚠️ Partial | Missing Fannie Mae entirely |
| **Dual-GSE Promise** | ❌ Not Delivered | Core value proposition failed |
| **Actionability** | ⚠️ Mixed | Good for Freddie Mac, zero for Fannie Mae |

---

## Root Cause Investigation

### Confirmed Root Cause: PDF Parsing Error

**Status:** ✅ Root cause identified

The issue is a **PDF parsing error** in the Fannie Mae Selling Guide extraction:

1. **The file `B3-4-3-04.txt` exists** but contains **WRONG CONTENT**:
   - Expected: Personal Gifts documentation (gift letter requirements, donor verification)
   - Actual: Interested Party Contributions (IPCs), Interest Rate Buydowns, Payment Abatements

2. **The title line reveals the parsing bug:**
   ```
   # B3-4.3-04: Personal Gifts and B3-4.3-05, Gifts of Equity are met;
   ```
   This is clearly a **sentence fragment**, not a section title. The regex matched a cross-reference to B3-4.3-04 within another section's content.

3. **The correct content exists in `_full_text.txt`** (lines 14687-14779):
   - Section header: `B3-4.3-04, Personal Gifts (09/06/2023)`
   - Complete gift letter requirements matching AskPoli exactly
   - But `_full_text.txt` is **excluded from ingestion** (line 113: `if file_path.name.startswith("_"): continue`)

### Technical Details

**Parser regex** (`scripts/parse_fannie_mae_pdf.py:59`):
```python
pattern = re.compile(r'\n([A-E]\d+-\d+(?:\.\d+)?-\d+)[,:\s]+\s*([^\n\(]+)', re.MULTILINE)
```

This regex matches any occurrence of section IDs in the text, including cross-references. When B3-4.3-04 appeared in a cross-reference within IPC content, the parser incorrectly created a "section" starting from that point.

**Ingestion script** (`scripts/ingest_guides.py:111-114`):
```python
for file_path in guide_dir.glob("*.txt"):
    if file_path.name.startswith("_"):
        continue  # Skips _full_text.txt
```

### Verification Evidence

**B3-4-3-04.txt actual content (first 10 lines):**
```
# B3-4.3-04: Personal Gifts and B3-4.3-05, Gifts of Equity are met;
Source: Fannie Mae Selling Guide (PDF)
Section ID: B3-4.3-04

---

B3-4.3-04, Personal Gifts and B3-4.3-05, Gifts of Equity are met;
A legitimate pro-rated real estate tax credit in places where real estate taxes are paid in arrears; and
Fees for standby commitments (refer to Interest Rate Buydowns section below).
Undisclosed IPCs
```

**_full_text.txt correct content (lines 14747-14754):**
```
Documentation Requirements
Gifts must be evidenced by a letter signed by the donor, called a gift letter...

The gift letter must:
specify the actual or the maximum dollar amount of the gift;
include the donor's statement that no repayment is expected; and
indicate the donor's name, address, telephone number, and relationship to the borrower.
```

This matches AskPoli's answer **exactly**.

---

## Recommendations

### Immediate Fix (Required)

1. **Re-parse B3-4.3-04 section correctly**
   - Manually extract the correct Personal Gifts content from `_full_text.txt` (lines 14687-14779)
   - Overwrite `B3-4-3-04.txt` with the correct content
   - Re-ingest into Pinecone

2. **Audit other sections for similar parsing errors**
   - Search for section files where title contains sentence fragments ("; and", "are met", etc.)
   - Cross-reference with `_full_text.txt` to verify content accuracy

### Long-term Improvements

3. **Improve PDF parser regex**
   - Add logic to detect cross-references vs actual section headers
   - Validate that section titles don't contain sentence fragments
   - Consider using section date format as validation: `(MM/DD/YYYY)`

4. **Add content validation to ingestion**
   - Flag sections where title looks like a sentence fragment
   - Compare section content length against expected ranges
   - Validate that key terms appear in expected sections (e.g., "gift letter" in B3-4.3-04)

5. **Consider curated answers for high-volume topics**
   - Gift funds is AskPoli's demo question - clearly high-traffic
   - Hybrid approach: RAG + verified "golden answers" for top 20 underwriting questions

### Testing Recommendations

6. **Create regression test suite**
   - Query for known high-volume topics (gift funds, income verification, DTI calculations)
   - Verify both GSE responses contain expected content
   - Compare against AskPoli answers for Fannie Mae coverage

---

## Affected Files

| File | Status | Issue | Resolution |
|------|--------|-------|------------|
| `data/fannie_mae_guide/B3-4-3-04.txt` | ✅ Fixed | Was: IPC content instead of Personal Gifts | Replaced with correct content from `_full_text.txt` lines 14687-14797 |
| `data/fannie_mae_guide/B3-4-3-08.txt` | ✅ Fixed | Was: Manufactured home content instead of Employer Assistance | Replaced with correct content from `_full_text.txt` lines 14960-15031 |
| `data/fannie_mae_guide/B7-3-08.txt` | ✅ Fixed | Was: Flood insurance deductibles instead of Mortgagee Clause requirements | Replaced with correct content from `_full_text.txt` lines 30089-30172 |
| `data/fannie_mae_guide/_full_text.txt` | ✅ Correct | Contains all correct content (not indexed by design) | Reference source for fixes |
| `scripts/parse_fannie_mae_pdf.py` | ⚠️ Bug | Regex matches cross-references as section headers | Needs improvement to prevent future issues |

## Audit Results

**Methodology:** Searched all 369 Fannie Mae section files for titles containing sentence fragments ("; and", "are met", "is required", "for additional information", etc.)

**Findings:**
- 3 corrupted sections identified and fixed
- Remaining files with "and" in titles are legitimate (e.g., "Sanctions, Suspensions, and Terminations")

## Fix Log

| Date | Section | Action |
|------|---------|--------|
| 2026-01-19 | B3-4.3-04 | Replaced with correct Personal Gifts content |
| 2026-01-19 | B3-4.3-08 | Replaced with correct Employer Assistance content |
| 2026-01-19 | B7-3-08 | Replaced with correct Mortgagee Clause content |
| 2026-01-19 | All sections | Full fresh re-ingest into Pinecone completed |

## Re-ingestion Results

**Date:** 2026-01-19
**Duration:** 577.7 seconds (~9.6 minutes)

| Metric | Value |
|--------|-------|
| Files processed | 1,203 |
| Vectors created | 6,172 |
| Pinecone vector count | 6,170 |
| Files skipped | 0 |

**Status:** ✅ Complete - All corrected sections now indexed in Pinecone

---

## Validation Results

### Post-Fix Test: "How do I document gift funds?"

**Date:** 2026-01-19
**Status:** ✅ **FIX VERIFIED**

### Before vs After

| Aspect | Before Fix | After Fix |
|--------|------------|-----------|
| **Fannie Mae Content** | ❌ "Context does not include Fannie Mae requirements" | ✅ Complete B3-4.3-04 content |
| **Gift Letter Requirements** | Freddie Mac only | Both GSEs |
| **"Relationship to borrower"** | ❌ Missing | ✅ Included |
| **Citations** | Freddie Mac only | Fannie Mae B3-4.3-04 + Freddie Mac 5501.4 |

### AskPoli Parity Check

| Requirement | AskPoli | SAGE (After Fix) | Match? |
|-------------|---------|------------------|--------|
| Gift letter signed by donor | ✅ | ✅ | ✅ |
| Trust/estate: signed by trustee | ✅ | ✅ | ✅ |
| Actual/maximum dollar amount | ✅ | ✅ | ✅ |
| No repayment statement | ✅ | ✅ | ✅ |
| Donor's name, address, telephone | ✅ | ✅ | ✅ |
| **Relationship to borrower** | ✅ | ✅ | ✅ |
| DU resubmission note | ✅ | ✅ | ✅ |
| Pooled funds (12-month cohabitation) | ✅ | ✅ | ✅ |
| Shared residency documentation | ✅ | ✅ | ✅ |

### SAGE Exceeds AskPoli

SAGE now provides additional value that AskPoli cannot:

| Feature | AskPoli | SAGE |
|---------|---------|------|
| Fund transfer documentation methods | ❌ Not detailed | ✅ 5 specific methods listed |
| Wedding/graduation gift provisions | ❌ Not covered | ✅ Freddie Mac special rules |
| Freddie Mac coverage | ❌ None | ✅ Full 5501.4 content |
| Dual-GSE comparison | ❌ Impossible | ✅ Side-by-side |

### Quality Metrics (Final)

| Metric | Rating | Notes |
|--------|--------|-------|
| Factual Accuracy | ✅ Excellent | Matches AskPoli exactly for Fannie Mae |
| Completeness | ✅ Excellent | Both GSEs covered comprehensively |
| Dual-GSE Promise | ✅ Delivered | Citations from both sources |
| AskPoli Parity | ✅ 100% | All Fannie Mae requirements present |
| Added Value | ✅ Exceeds | Freddie Mac content AskPoli can't provide |

### Conclusion

**The fix is successful.** SAGE's "Ask" feature now:
1. Matches AskPoli 100% for Fannie Mae gift fund requirements
2. Exceeds AskPoli by providing Freddie Mac coverage
3. Delivers on the dual-GSE value proposition

---

## Source Documents

- Fannie Mae Quality Insider Newsletter, March 2025
- AskPoli screenshot showing gift funds answer
- SAGE RAG response (January 2026)
- `data/fannie_mae_guide/B3-4-3-04.txt` (corrupted)
- `data/fannie_mae_guide/_full_text.txt` (correct source)
