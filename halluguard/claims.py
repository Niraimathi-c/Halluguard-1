from __future__ import annotations
import re
from .models import ClaimReport

_SENTENCE = re.compile(r'(?<=[.!?])\s+|\n+')

def decompose(text: str) -> list[str]:
    """Conservative sentence-level atomic decomposition with conjunction splitting."""
    out=[]
    for sentence in (s.strip() for s in _SENTENCE.split(text)):
        if not sentence: continue
        parts=re.split(r'\s+(?:and|but)\s+(?=[A-Z0-9])', sentence)
        out.extend(p.strip() for p in parts if p.strip())
    return out
