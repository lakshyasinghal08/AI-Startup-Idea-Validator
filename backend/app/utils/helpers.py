"""
General Helper Functions
========================
Purpose:
    Reusable helper functions for string sanitization, UUID formatting,
    and safe dictionary extraction across modules.

Milestone Notes:
    - Milestone 1: Basic string cleaning and ID generator utilities.
    - Future Milestones: Additional data formatters, token counters, and PDF helpers.
"""

import re
import uuid


def sanitize_text(text: str) -> str:
    """
    Cleans raw user input or scraped web content by stripping excess whitespace
    and non-printable characters.
    """
    if not text:
        return ""
    # Replace multiple whitespace/newlines with a single space
    cleaned = re.sub(r"\s+", " ", text)
    return cleaned.strip()


def generate_short_id(prefix: str = "idea") -> str:
    """
    Generates a unique human-readable short identifier.
    Example: 'idea_a1b2c3d4'
    """
    short_uuid = uuid.uuid4().hex[:8]
    return f"{prefix}_{short_uuid}"
