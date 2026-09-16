from fastapi import FastAPI
from pydantic import BaseModel, Field
from .pipeline import HalluGuard
from .adapters import MockLLM, OpenAIAdapter, GeminiAdapter, OpenAICompatibleAdapter
from .models import Evidence
from .retrieval import MemoryRetriever

app=FastAPI(title="HalluGuard",version="0.1.0",description="Claim-level, evidence-grounded LLM reliability API")
retriever=MemoryRetriever([
 Evidence(id="demo-1",text="Pride and Prejudice is a novel by English author Jane Austen, first published in 1813.",source="Demo corpus",authority=.9,freshness=.9,provenance="seeded"),
 Evidence(id="demo-2",text="The Earth orbits the Sun and takes approximately 365.25 days to complete one orbit.",source="Demo corpus",authority=.9,freshness=.9,provenance="seeded"),
])

class VerifyRequest(BaseModel):
    prompt: str
    response: str | None = None
    provider: str = Field(default="mock", description="mock, openai, gemini, llama, or mistral")
    model: str | None = None
    base_url: str | None = None

@app.get("/health")
def health(): return {"status":"ok","service":"halluguard"}

@app.post("/v1/verify")
def verify(req: VerifyRequest):
    if req.provider=="openai": llm=OpenAIAdapter(req.model or "gpt-4o-mini")
    elif req.provider=="gemini": llm=GeminiAdapter(req.model or "gemini-2.0-flash")
    elif req.provider in {"llama","mistral"}: llm=OpenAICompatibleAdapter(req.model or req.provider, req.base_url or "http://localhost:8000/v1")
    else: llm=MockLLM(req.response)
    return HalluGuard(llm=llm,retriever=retriever).verify(req.prompt,req.response).model_dump(mode="json")
