from __future__ import annotations
import math, re
from .models import Evidence, Signal, Verdict, HallucinationType, Severity

_NEG = {"not","no","never","false","incorrect","wrong"}

def _tokens(s): return set(re.findall(r"[a-z0-9]+",s.lower()))

def similarity(a,b):
    A,B=_tokens(a),_tokens(b)
    return len(A&B)/math.sqrt(max(1,len(A)*len(B)))

def nli_heuristic(claim,evidence):
    c,e=claim.lower(),evidence.lower(); sim=similarity(c,e)
    cneg=bool(_NEG & _tokens(c)); eneg=bool(_NEG & _tokens(e))
    if sim >= .55 and cneg==eneg: return "entailment", min(1.0,.55+.45*sim)
    if sim >= .45 and cneg!=eneg: return "contradiction", min(1.0,.50+.50*sim)
    return "neutral", max(0.0,sim)

def verify_claim(claim: str, evidence: list[Evidence], judge=None):
    if not evidence: return Verdict.UNVERIFIED,0.0,Signal(),"No independent evidence was retrieved."
    signals=[]
    for e in evidence:
        nli,ns=nli_heuristic(claim,e.text); signals.append((nli,ns,similarity(claim,e.text),e))
    ent=[x for x in signals if x[0]=="entailment"]; con=[x for x in signals if x[0]=="contradiction"]
    best=max(signals,key=lambda x:x[1]+x[2]*.25)
    judge_score=judge(claim,[x[3] for x in signals]) if judge else None
    if ent and con: verdict=Verdict.MIXED
    elif ent and best[1]>=.65: verdict=Verdict.SUPPORTED
    elif con and best[1]>=.60: verdict=Verdict.REFUTED
    else: verdict=Verdict.UNVERIFIED
    confidence=min(1.0,.65*best[1]+.25*best[2]+(.10*(judge_score if judge_score is not None else 1.0)))
    sig=Signal(nli=best[0],nli_score=best[1],similarity=best[2],judge=judge_score)
    explanation=f"Best evidence signal: {best[0]} (NLI={best[1]:.2f}, similarity={best[2]:.2f})."
    if ent and con: explanation += " Credible evidence contains conflicting signals."
    return verdict,round(confidence,3),sig,explanation

def classify(claim: str):
    s=claim.lower()
    if re.search(r"\b(19|20)\d{2}\b|yesterday|today|tomorrow|last year|next year",s): return HallucinationType.TEMPORAL
    if re.search(r"\b\d+(?:\.\d+)?%?\b",s): return HallucinationType.NUMERICAL
    if re.search(r"https?://|doi:|according to|source|citation",s): return HallucinationType.CITATION
    if re.search(r"\b(because|therefore|thus|implies|causes)\b",s): return HallucinationType.LOGICAL
    if re.search(r"\b(is|was|are|were)\b",s): return HallucinationType.FACTUAL
    return HallucinationType.CONTEXTUAL

def severity(confidence: float, claim_type: HallucinationType):
    if confidence >= .9: return Severity.CRITICAL
    if confidence >= .75: return Severity.HIGH
    if confidence >= .55: return Severity.MEDIUM
    return Severity.LOW
