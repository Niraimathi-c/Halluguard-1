from __future__ import annotations
import os
from abc import ABC, abstractmethod
import httpx

class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str: ...

class MockLLM(BaseLLM):
    def __init__(self, response: str | None = None): self.response = response
    def generate(self, prompt: str) -> str:
        return self.response or "I don't have enough information to answer reliably."

class OpenAIAdapter(BaseLLM):
    def __init__(self, model="gpt-4o-mini", api_key=None, base_url="https://api.openai.com/v1"):
        self.model, self.api_key, self.base_url = model, api_key or os.getenv("OPENAI_API_KEY"), base_url.rstrip("/")
    def generate(self, prompt: str) -> str:
        if not self.api_key: raise RuntimeError("OPENAI_API_KEY is not configured")
        r = httpx.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": self.model, "messages":[{"role":"user","content":prompt}]}, timeout=60)
        r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]

class GeminiAdapter(BaseLLM):
    def __init__(self, model="gemini-2.0-flash", api_key=None):
        self.model, self.api_key = model, api_key or os.getenv("GEMINI_API_KEY")
    def generate(self, prompt: str) -> str:
        if not self.api_key: raise RuntimeError("GEMINI_API_KEY is not configured")
        url=f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        r=httpx.post(url,json={"contents":[{"parts":[{"text":prompt}]}]},timeout=60); r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

class OpenAICompatibleAdapter(BaseLLM):
    """Works with Llama, Mistral and other OpenAI-compatible inference servers."""
    def __init__(self, model, base_url, api_key=None): self.model,self.base_url,self.api_key=model,base_url.rstrip("/"),api_key or os.getenv("LLM_API_KEY", "local")
    def generate(self,prompt):
        r=httpx.post(f"{self.base_url}/chat/completions",headers={"Authorization":f"Bearer {self.api_key}"},json={"model":self.model,"messages":[{"role":"user","content":prompt}]},timeout=60); r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]

LlamaAdapter = OpenAICompatibleAdapter
MistralAdapter = OpenAICompatibleAdapter
