"""
Changes Router

Handles policy update endpoints for tracking GSE guideline changes.
"""

from datetime import date
from typing import Literal
from fastapi import APIRouter, HTTPException, Query, status

from ..models import PolicyUpdate, PolicyUpdatesResponse, CodeDiffResponse

router = APIRouter(prefix="/changes", tags=["changes"])


# Mock policy updates data
# TODO: Replace with database queries in Phase 2
_mock_updates = [
    PolicyUpdate(
        id="ll-2025-04",
        gse="fannie_mae",
        update_type="lender_letter",
        update_number="LL-2025-04",
        title="Updates to HomeReady Income Limits",
        publish_date=date(2025, 1, 15),
        effective_date=date(2025, 3, 1),
        summary="This lender letter announces updates to HomeReady income limits "
        "based on the latest Area Median Income (AMI) data from FHFA. "
        "Income limits are increased in most areas to reflect rising median incomes.",
        affected_sections=["B5-6-01", "B5-6-02"],
        impact_analysis="Income limits increased by approximately 5% in most areas. "
        "This expands eligibility for HomeReady to more borrowers.",
        code_update=None,
    ),
    PolicyUpdate(
        id="ll-2025-03",
        gse="fannie_mae",
        update_type="lender_letter",
        update_number="LL-2025-03",
        title="2025 Conforming Loan Limits",
        publish_date=date(2025, 1, 10),
        effective_date=date(2025, 1, 1),
        summary="Announces the 2025 conforming loan limits. The baseline limit "
        "for single-family properties increased to $806,500. High-cost area "
        "limits are up to $1,209,750.",
        affected_sections=["B2-1-01"],
        impact_analysis="Higher loan limits allow more borrowers to access "
        "conforming loans with better rates.",
        code_update="# Update loan limits\nMAX_CONFORMING_LOAN = 806500\nMAX_HIGH_COST_LOAN = 1209750",
    ),
    PolicyUpdate(
        id="bulletin-2025-16",
        gse="freddie_mac",
        update_type="bulletin",
        update_number="2025-16",
        title="Home Possible DTI Flexibility",
        publish_date=date(2025, 1, 8),
        effective_date=date(2025, 2, 15),
        summary="Freddie Mac is updating the maximum DTI ratio for Home Possible "
        "loans to allow greater flexibility. Loans with strong compensating "
        "factors may exceed the standard 45% DTI limit.",
        affected_sections=["4501.5", "4501.9"],
        impact_analysis="This change could qualify more borrowers for Home Possible "
        "who have higher DTI but other strong credit factors.",
        code_update=None,
    ),
    PolicyUpdate(
        id="guide-update-2025-01",
        gse="freddie_mac",
        update_type="guide_update",
        update_number="2025-01",
        title="Updated Property Eligibility for Home Possible",
        publish_date=date(2024, 12, 20),
        effective_date=date(2025, 1, 15),
        summary="Clarifies property eligibility requirements for Home Possible, "
        "including updated guidance on manufactured housing and condos.",
        affected_sections=["4501.5", "5601.1"],
        impact_analysis="Expanded eligibility for manufactured housing may help "
        "more affordable housing options qualify.",
        code_update=None,
    ),
    PolicyUpdate(
        id="ll-2024-21",
        gse="fannie_mae",
        update_type="lender_letter",
        update_number="LL-2024-21",
        title="HomeReady Homeownership Education Updates",
        publish_date=date(2024, 11, 15),
        effective_date=date(2025, 1, 1),
        summary="Updates to homeownership education requirements for HomeReady. "
        "Clarifies when education is required and acceptable providers.",
        affected_sections=["B5-6-01"],
        impact_analysis="Provides clearer guidance on education requirements, "
        "which may streamline the qualification process.",
        code_update=None,
    ),
]


@router.get(
    "",
    response_model=PolicyUpdatesResponse,
    status_code=status.HTTP_200_OK,
    summary="List policy updates",
    description="Get a list of recent policy updates from Fannie Mae and Freddie Mac.",
)
async def list_changes(
    gse: Literal["fannie_mae", "freddie_mac"] | None = Query(
        default=None, description="Filter by GSE"
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of updates"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
) -> PolicyUpdatesResponse:
    """
    List policy updates with optional filtering.

    Returns a paginated list of policy updates, optionally filtered by GSE.
    """
    try:
        # Filter by GSE if specified
        filtered = _mock_updates
        if gse:
            filtered = [u for u in _mock_updates if u.gse == gse]

        # Sort by publish date (newest first)
        sorted_updates = sorted(filtered, key=lambda u: u.publish_date, reverse=True)

        # Apply pagination
        total = len(sorted_updates)
        paginated = sorted_updates[offset : offset + limit]

        return PolicyUpdatesResponse(updates=paginated, total=total)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing changes: {str(e)}",
        )


@router.get(
    "/{update_id}",
    response_model=PolicyUpdate,
    status_code=status.HTTP_200_OK,
    summary="Get policy update",
    description="Get details of a specific policy update.",
)
async def get_change(update_id: str) -> PolicyUpdate:
    """
    Get a specific policy update by ID.
    """
    # Find the update
    update = next((u for u in _mock_updates if u.id == update_id), None)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy update '{update_id}' not found",
        )

    return update


@router.get(
    "/{update_id}/code",
    response_model=CodeDiffResponse,
    status_code=status.HTTP_200_OK,
    summary="Get code diff for update",
    description="Get generated code changes for a policy update.",
)
async def get_change_code(
    update_id: str,
    format: Literal["python", "typescript", "yaml", "json"] = Query(
        default="python", description="Code format"
    ),
) -> CodeDiffResponse:
    """
    Get generated code diff for a policy update.

    Returns the code changes needed to implement the policy update
    in the specified format.
    """
    # Find the update
    update = next((u for u in _mock_updates if u.id == update_id), None)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy update '{update_id}' not found",
        )

    # Generate code based on format
    # TODO: Replace with actual code generation in Phase 2
    if format == "python":
        code = _generate_python_code(update)
    elif format == "typescript":
        code = _generate_typescript_code(update)
    elif format == "yaml":
        code = _generate_yaml_code(update)
    else:
        code = _generate_json_code(update)

    return CodeDiffResponse(code=code, format=format)


def _generate_python_code(update: PolicyUpdate) -> str:
    """Generate Python code for a policy update."""
    if update.code_update:
        return update.code_update

    return f'''# Generated code for {update.update_number}
# {update.title}
# Effective: {update.effective_date}

# TODO: Implement rules changes based on:
# {update.summary[:200]}...

# Affected sections: {', '.join(update.affected_sections)}
'''


def _generate_typescript_code(update: PolicyUpdate) -> str:
    """Generate TypeScript code for a policy update."""
    return f'''// Generated code for {update.update_number}
// {update.title}
// Effective: {update.effective_date}

// TODO: Implement rules changes based on:
// {update.summary[:200]}...

// Affected sections: {', '.join(update.affected_sections)}
'''


def _generate_yaml_code(update: PolicyUpdate) -> str:
    """Generate YAML code for a policy update."""
    return f'''# Generated rules for {update.update_number}
# {update.title}

update:
  number: "{update.update_number}"
  effective_date: "{update.effective_date}"
  affected_sections:
{chr(10).join(f'    - "{s}"' for s in update.affected_sections)}

# TODO: Add rule definitions
'''


def _generate_json_code(update: PolicyUpdate) -> str:
    """Generate JSON code for a policy update."""
    import json

    return json.dumps(
        {
            "update_number": update.update_number,
            "effective_date": str(update.effective_date),
            "affected_sections": update.affected_sections,
            "rules": {},
        },
        indent=2,
    )
