"""
Universal API Response Envelope Schemas
=======================================
Purpose:
    Enforces a consistent RESTful JSON response structure across all endpoints.
    Provides standardized envelopes for success data and structured errors.

Milestone Notes:
    - Milestone 1: Generic wrapper classes for API payloads.
    - Future Milestones: Integrate pagination envelopes and validation error aggregators.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Represents a specific field-level or system error."""
    field: str | None = Field(default=None, description="Affected field name if validation error")
    message: str = Field(..., description="Human-readable error description")


class ApiResponse(BaseModel, Generic[T]):
    """
    Standardized API response wrapper ensuring consistent JSON responses across all routes.
    """
    success: bool = Field(default=True, description="Indicates whether the request was successful")
    data: T | None = Field(default=None, description="Payload data returned by the endpoint")
    message: str = Field(default="Operation completed successfully", description="Status message")
    errors: list[ErrorDetail] | None = Field(default=None, description="List of error details if failed")
