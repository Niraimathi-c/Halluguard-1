from __future__ import annotations
import re
from abc import ABC, abstractmethod
from .models import Evidence

class EvidenceRetriever(ABC):
    @abstractmethod
    def search(self, claim: str, k: int = 5) -> list[Evidence]: ...

class MemoryRetriever(EvidenceRetriever):
    def __init__(self, documents: list[Evidence] | None = None): self.documents=documents or []
    def add(self, evidence: Evidence): self.documents.append(evidence)
    @staticmethod
    def _terms(s): return set(re.findall(r"[a-z0-9]+", s.lower()))
    def search(self, claim, k=5):
        q=self._terms(claim)
        scored=[]
        for e in self.documents:
            overlap=len(q & self._terms(e.text)) / max(1,len(q))
            e2=e.model_copy(update={"relevance":overlap})
            scored.append(e2)
        return sorted(scored,key=lambda x:(x.relevance,x.authority,x.freshness,x.corroboration),reverse=True)[:k]

def rank_evidence(items: list[Evidence]) -> list[Evidence]:
    """Weighted source-aware ranking; keeps provenance explicit."""
    return sorted(items,key=lambda e: .40*e.relevance+.18*e.authority+.12*e.freshness+.12*e.corroboration+.10*e.independence+.08*e.provenance_score if hasattr(e,'provenance_score') else (.40*e.relevance+.18*e.authority+.12*e.freshness+.12*e.corroboration+.10*e.independence),reverse=True)
