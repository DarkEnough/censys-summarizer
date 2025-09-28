from pydantic import BaseModel
from typing import List, Dict, Any, Literal

class HealthResponse(BaseModel):
    status: str

class SummarizationRequest(BaseModel):
    hosts: List[Dict[str, Any]]
    summarizer: Literal["groq", "huggingface"] = "groq"

class HostSummary(BaseModel):
    host_id: str
    summary: str
    original_data: Dict[str, Any]

class SummarizationResponse(BaseModel):
    summarizer_used: str
    summaries: List[Dict[str, Any]]
