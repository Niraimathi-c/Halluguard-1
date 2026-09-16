from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class Verdict(str, Enum):
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    MIXED = "MIXED"
    UNVERIFIED = "UNVERIFIED"

class Severity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class HallucinationType(str, Enum):
    FACTUAL = "factual"
    ENTITY = "entity"
    TEMPORAL = "temporal"
    NUMERICAL = "numerical"
    RELATIONAL = "relational"
    CITATION = "citation"
    CONTEXTUAL = "contextual"
    LOGICAL = "logical"

class Evidence(BaseModel):
    id: str
    text: str
    source: str
    url: str | None = None
    authority: float = 0.5
    freshness: float = 0.5
    provenance: str = "unknown"
    relevance: float = 0.0
    corroboration: float = 0.0
    independence: float = 1.0

class Signal(BaseModel):
    nli: str = "unknown"
    nli_score: float = 0.0
    similarity: float = 0.0
    judge: float | None = None

class ClaimReport(BaseModel):
    id: str
    text: str
    verdict: Verdict
    confidence: float
    hallucination_type: HallucinationType | None = None
    severity: Severity | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    signals: Signal = Field(default_factory=Signal)
    correction: str | None = None
    correction_status: str = "NOT_NEEDED"
    re_verification: Verdict | None = None
    explanation: str = ""

class ReliabilityReport(BaseModel):
    prompt: str
    original_response: str
    final_response: str
    claims: list[ClaimReport]
    overall_verdict: Verdict
    verified_claims: int
    refuted_claims: int
    unverified_claims: int
    metadata: dict[str, Any] = Field(default_factory=dict)
