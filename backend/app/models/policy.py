"""
Policy Update Models

Models for tracking GSE policy changes and updates.
"""

from datetime import date
from typing import Literal
from pydantic import BaseModel, Field


class PolicyUpdate(BaseModel):
    """A policy update from Fannie Mae or Freddie Mac."""

    id: str = Field(..., description="Unique identifier")
    gse: Literal["fannie_mae", "freddie_mac"] = Field(
        ..., description="Which GSE issued the update"
    )
    update_type: Literal["lender_letter", "bulletin", "guide_update"] = Field(
        ..., description="Type of update"
    )
    update_number: str = Field(..., description="Official update number (e.g., 'LL-2025-04')")
    title: str = Field(..., description="Update title")
    publish_date: date = Field(..., description="When the update was published")
    effective_date: date | None = Field(default=None, description="When the update takes effect")
    summary: str = Field(..., description="Summary of the update")
    affected_sections: list[str] = Field(
        default_factory=list, description="Guide sections affected (e.g., ['B5-6-01'])"
    )
    impact_analysis: str | None = Field(
        default=None, description="AI-generated analysis of the impact"
    )
    code_update: str | None = Field(
        default=None, description="Generated code diff for rules engine"
    )


class PolicyUpdatesResponse(BaseModel):
    """Response containing a list of policy updates."""

    updates: list[PolicyUpdate] = Field(..., description="List of policy updates")
    total: int = Field(..., description="Total number of updates available")


class CodeDiffResponse(BaseModel):
    """Response containing generated code for a policy update."""

    code: str = Field(..., description="Generated code diff")
    format: Literal["python", "typescript", "yaml", "json"] = Field(
        ..., description="Code format"
    )
