from halluguard.pipeline import HalluGuard
from halluguard.models import Evidence, Verdict
from halluguard.retrieval import MemoryRetriever


def test_supported_claim():
    r=MemoryRetriever([Evidence(id="1",text="The capital of France is Paris.",source="test",authority=.9)])
    report=HalluGuard(retriever=r).verify("q","The capital of France is Paris.")
    assert report.claims[0].verdict == Verdict.SUPPORTED


def test_unverified_is_safe():
    report=HalluGuard().verify("q","This unsupported fact is definitely true.")
    assert report.overall_verdict == Verdict.UNVERIFIED
    assert report.final_response == report.original_response


def test_atomic_split():
    report=HalluGuard().verify("q","Paris is in France. Berlin is in Germany.")
    assert len(report.claims)==2
    assert report.claims[0].id=="C1" and report.claims[1].id=="C2"
