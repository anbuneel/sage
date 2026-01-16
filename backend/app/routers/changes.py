"""
Changes Router

Handles policy update endpoints for tracking GSE guideline changes.
"""

import logging
from datetime import date
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from sqlalchemy import select, func

from ..config import get_settings
from ..models import PolicyUpdate as PolicyUpdateModel, PolicyUpdatesResponse, CodeDiffResponse
from ..db import get_session, PolicyUpdate as DBPolicyUpdate
from ..services.scrapers import FannieMaeScraper, FreddieMacScraper

router = APIRouter(prefix="/changes", tags=["changes"])
logger = logging.getLogger(__name__)


# Mock policy updates data (fallback when DB not configured)
_mock_updates = [
    PolicyUpdateModel(
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
    PolicyUpdateModel(
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
    PolicyUpdateModel(
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
    PolicyUpdateModel(
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
    PolicyUpdateModel(
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


async def _get_updates_from_db(
    gse: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[PolicyUpdateModel], int]:
    """Get updates from database."""
    async with get_session() as session:
        # Build base query
        query = select(DBPolicyUpdate)

        if gse:
            query = query.where(DBPolicyUpdate.gse == gse)

        # Get total count
        count_query = select(func.count()).select_from(DBPolicyUpdate)
        if gse:
            count_query = count_query.where(DBPolicyUpdate.gse == gse)
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(DBPolicyUpdate.publish_date.desc())
        query = query.offset(offset).limit(limit)

        result = await session.execute(query)
        db_updates = result.scalars().all()

        # Convert to Pydantic models
        updates = []
        for db_update in db_updates:
            updates.append(
                PolicyUpdateModel(
                    id=str(db_update.id),
                    gse=db_update.gse,
                    update_type=db_update.update_type,
                    update_number=db_update.update_number,
                    title=db_update.title,
                    publish_date=db_update.publish_date,
                    effective_date=db_update.effective_date,
                    summary=db_update.summary,
                    affected_sections=db_update.affected_sections or [],
                    impact_analysis=db_update.impact_analysis,
                    code_update=db_update.code_update,
                )
            )

        return updates, total


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
        settings = get_settings()

        if settings.database_url:
            # Use database
            updates, total = await _get_updates_from_db(gse, limit, offset)

            # If no database results, fall back to mock
            if not updates:
                logger.info("No database results, using mock data")
                return _get_mock_response(gse, limit, offset)

            return PolicyUpdatesResponse(updates=updates, total=total)
        else:
            # Use mock data
            return _get_mock_response(gse, limit, offset)

    except Exception as e:
        logger.error(f"Error listing changes: {e}")
        # Fall back to mock data on error
        return _get_mock_response(gse, limit, offset)


def _get_mock_response(
    gse: str | None,
    limit: int,
    offset: int,
) -> PolicyUpdatesResponse:
    """Get mock response for when DB is not available."""
    filtered = _mock_updates
    if gse:
        filtered = [u for u in _mock_updates if u.gse == gse]

    sorted_updates = sorted(filtered, key=lambda u: u.publish_date, reverse=True)
    total = len(sorted_updates)
    paginated = sorted_updates[offset : offset + limit]

    return PolicyUpdatesResponse(updates=paginated, total=total)


@router.get(
    "/{update_id}",
    response_model=PolicyUpdateModel,
    status_code=status.HTTP_200_OK,
    summary="Get policy update",
    description="Get details of a specific policy update.",
)
async def get_change(update_id: str) -> PolicyUpdateModel:
    """
    Get a specific policy update by ID.
    """
    settings = get_settings()

    if settings.database_url:
        async with get_session() as session:
            result = await session.execute(
                select(DBPolicyUpdate).where(DBPolicyUpdate.id == update_id)
            )
            db_update = result.scalar_one_or_none()

            if db_update:
                return PolicyUpdateModel(
                    id=str(db_update.id),
                    gse=db_update.gse,
                    update_type=db_update.update_type,
                    update_number=db_update.update_number,
                    title=db_update.title,
                    publish_date=db_update.publish_date,
                    effective_date=db_update.effective_date,
                    summary=db_update.summary,
                    affected_sections=db_update.affected_sections or [],
                    impact_analysis=db_update.impact_analysis,
                    code_update=db_update.code_update,
                )

    # Try mock data
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
    # Get the update first
    update = await get_change(update_id)

    # Generate code based on format
    if format == "python":
        code = _generate_python_code(update)
    elif format == "typescript":
        code = _generate_typescript_code(update)
    elif format == "yaml":
        code = _generate_yaml_code(update)
    else:
        code = _generate_json_code(update)

    return CodeDiffResponse(code=code, format=format)


@router.post(
    "/refresh",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger policy update refresh",
    description="Trigger a background refresh of policy updates from GSE websites.",
)
async def refresh_updates(
    background_tasks: BackgroundTasks,
    gse: Literal["fannie_mae", "freddie_mac", "all"] = Query(
        default="all", description="Which GSE to refresh"
    ),
) -> dict:
    """
    Trigger a background refresh of policy updates.

    This runs the scrapers to check for new Lender Letters and Bulletins.
    """
    settings = get_settings()

    if not settings.database_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured. Cannot refresh updates.",
        )

    # Queue background tasks
    if gse in ["fannie_mae", "all"]:
        background_tasks.add_task(_run_fannie_scraper)

    if gse in ["freddie_mac", "all"]:
        background_tasks.add_task(_run_freddie_scraper)

    return {
        "message": f"Policy update refresh queued for {gse}",
        "status": "queued",
    }


async def _run_fannie_scraper():
    """Run Fannie Mae scraper in background."""
    scraper = FannieMaeScraper()
    try:
        result = await scraper.run()
        logger.info(f"Fannie Mae scraper completed: {result}")
    finally:
        await scraper.close()


async def _run_freddie_scraper():
    """Run Freddie Mac scraper in background."""
    scraper = FreddieMacScraper()
    try:
        result = await scraper.run()
        logger.info(f"Freddie Mac scraper completed: {result}")
    finally:
        await scraper.close()


def _generate_python_code(update: PolicyUpdateModel) -> str:
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


def _generate_typescript_code(update: PolicyUpdateModel) -> str:
    """Generate TypeScript code for a policy update."""
    return f'''// Generated code for {update.update_number}
// {update.title}
// Effective: {update.effective_date}

// TODO: Implement rules changes based on:
// {update.summary[:200]}...

// Affected sections: {', '.join(update.affected_sections)}
'''


def _generate_yaml_code(update: PolicyUpdateModel) -> str:
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


def _generate_json_code(update: PolicyUpdateModel) -> str:
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
