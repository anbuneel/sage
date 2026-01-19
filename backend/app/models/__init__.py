"""
SAGE Pydantic Models

All data models used across the application.
"""

from .loan import (
    LoanScenario,
    RuleViolation,
    FixSuggestion,
    ProductResult,
    EligibilityResult,
    # Demo mode models
    RAGRetrieval,
    ReasoningStep,
    IndexStats,
    ParsedInput,
    DemoModeData,
)
from .chat import (
    Citation,
    ChatMessage,
    ChatRequest,
    ChatResponse,
)
from .policy import PolicyUpdate, PolicyUpdatesResponse, CodeDiffResponse
from .fix_finder import (
    GuideCitation,
    CompensatingFactor,
    EnhancedFixSuggestion,
    SimulationResult,
    FixSequence,
    ToolCall,
    ReactStep,
    FixFinderResult,
)

# Rebuild EligibilityResult to resolve forward reference to FixFinderResult
EligibilityResult.model_rebuild()

__all__ = [
    # Loan models
    "LoanScenario",
    "RuleViolation",
    "FixSuggestion",
    "ProductResult",
    "EligibilityResult",
    # Demo mode models
    "RAGRetrieval",
    "ReasoningStep",
    "IndexStats",
    "ParsedInput",
    "DemoModeData",
    # Chat models
    "Citation",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    # Policy models
    "PolicyUpdate",
    "PolicyUpdatesResponse",
    "CodeDiffResponse",
    # Fix Finder models
    "GuideCitation",
    "CompensatingFactor",
    "EnhancedFixSuggestion",
    "SimulationResult",
    "FixSequence",
    "ToolCall",
    "ReactStep",
    "FixFinderResult",
]
