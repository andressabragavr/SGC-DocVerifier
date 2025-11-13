from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from agent.graph import run_validation
import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=False)  # carrega .env


API_KEY = os.getenv("AGENT_API_KEY", "")  # opcional

class ValReq(BaseModel):
    cert_id: str
    skip_ocr: bool = False 

app = FastAPI(title="DocVerifier Agent")

@app.post("/validate")
def validate(req: ValReq, x_agent_key: str | None = Header(None)):
    if API_KEY and x_agent_key != API_KEY:
        raise HTTPException(status_code=401, detail="unauthorized")
    return run_validation(
        req.cert_id,
        skip_ocr=req.skip_ocr  
    )
