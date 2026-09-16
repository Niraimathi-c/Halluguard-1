from __future__ import annotations
from .adapters import BaseLLM, MockLLM
from .claims import decompose
from .models import ClaimReport, ReliabilityReport, Verdict
from .retrieval import EvidenceRetriever, MemoryRetriever, rank_evidence
from .verification import verify_claim, classify, severity

class HalluGuard:
    def __init__(self, llm: BaseLLM | None = None, retriever: EvidenceRetriever | None = None, judge=None):
        self.llm=llm or MockLLM(); self.retriever=retriever or MemoryRetriever(); self.judge=judge

    def _correct(self, claim, evidence):
        # Corrections are evidence-derived: choose the strongest supporting sentence.
        supported=[e for e in evidence if e.relevance > 0]
        return supported[0].text if supported else None

    def verify(self, prompt: str, response: str | None = None) -> ReliabilityReport:
        original=response if response is not None else self.llm.generate(prompt)
        claims=decompose(original)
        reports=[]
        for i,text in enumerate(claims,1):
            evidence=rank_evidence(self.retriever.search(text,5))
            verdict,conf,sig,explain=verify_claim(text,evidence,self.judge)
            typ=classify(text)
            correction=None; status="NOT_NEEDED"; re_ver=None
            if verdict in (Verdict.REFUTED,Verdict.MIXED):
                correction=self._correct(text,evidence)
                if correction:
                    status="GENERATED"
                    re_ver,_,_,_=verify_claim(correction,evidence,self.judge)
                    status="VERIFIED" if re_ver==Verdict.SUPPORTED else "UNVERIFIED"
                    if status=="UNVERIFIED": correction=None
                else: status="UNVERIFIED"
            reports.append(ClaimReport(id=f"C{i}",text=text,verdict=verdict,confidence=conf,hallucination_type=typ if verdict!=Verdict.SUPPORTED else None,severity=severity(conf,typ) if verdict!=Verdict.SUPPORTED else None,evidence=evidence,signals=sig,correction=correction,correction_status=status,re_verification=re_ver,explanation=explain))
        final=[]
        for r in reports: final.append(r.correction if r.correction else r.text)
        ref=sum(r.verdict==Verdict.REFUTED for r in reports); unv=sum(r.verdict in (Verdict.UNVERIFIED,Verdict.MIXED) or r.correction_status=="UNVERIFIED" for r in reports); ver=sum(r.verdict==Verdict.SUPPORTED for r in reports)
        overall=Verdict.REFUTED if ref else (Verdict.UNVERIFIED if unv else Verdict.SUPPORTED)
        return ReliabilityReport(prompt=prompt,original_response=original,final_response=" ".join(final),claims=reports,overall_verdict=overall,verified_claims=ver,refuted_claims=ref,unverified_claims=unv,metadata={"pipeline":"claims→evidence→verification→correction→re-verification"})
