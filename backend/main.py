from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
try:
    # For deployment (when run as module)
    from backend.models import SummarizationRequest, SummarizationResponse, HealthResponse
    from backend.summarizer_groq import GroqSummarizer
    from backend.summarizer_hf import HFSummarizer
except ImportError:
    # For local development (when run from backend directory)
    from models import SummarizationRequest, SummarizationResponse, HealthResponse
    from summarizer_groq import GroqSummarizer
    from summarizer_hf import HFSummarizer

app = FastAPI(title="Censys Data Summarizer API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize summarizers
groq_summarizer = GroqSummarizer()
hf_summarizer = HFSummarizer()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/batch_summarize", response_model=SummarizationResponse)
async def batch_summarize(request: SummarizationRequest):
    """
    Summarize a batch of hosts using the selected summarizer.
    """
    try:
        # Select summarizer based on request
        if request.summarizer == "groq":
            summarizer = groq_summarizer
        elif request.summarizer == "huggingface":
            summarizer = hf_summarizer
        else:
            raise HTTPException(status_code=400, detail="Invalid summarizer choice")
        
        # Process each host
        summaries = []
        for host in request.hosts:
            # Create a text representation of the host data
            host_text = json.dumps(host, indent=2)
            summary = summarizer.summarize(host_text)
            summaries.append({
                "host_id": host.get("ip", "unknown"),
                "summary": summary,
                "original_data": host
            })
        
        return {
            "summarizer_used": request.summarizer,
            "summaries": summaries
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_dataset", response_model=SummarizationResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    summarizer: str = "groq"
):
    """
    Upload a JSON file containing host data and summarize using the selected summarizer.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="File must be a JSON file")
        
        # Read and parse JSON content
        content = await file.read()
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        
        # Handle different JSON structures
        if isinstance(data, dict):
            # Check if it has a 'hosts' key (nested structure)
            if 'hosts' in data:
                data = data['hosts']
            else:
                # Single host object, wrap in list
                data = [data]
        elif not isinstance(data, list):
            # Convert to list if it's not already
            data = [data]
        
        # Create request and process
        request = SummarizationRequest(hosts=data, summarizer=summarizer)
        return await batch_summarize(request)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
