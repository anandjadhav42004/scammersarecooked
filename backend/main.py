import os
import json
import re
import requests
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Union
from dotenv import load_dotenv
from groq import Groq

# 1. Setup
load_dotenv()
app = FastAPI(title="ScammersAreCooked_Master_Agent")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Memory store to track intelligence
memory_store = {}

# --- MODELS (Fixed: timestamp is now Union to handle Epoch numbers) ---
class Message(BaseModel):
    sender: str
    text: str
    timestamp: Union[int, float, str] # Handles Epoch ms from Hackathon system

class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[dict]
    metadata: Optional[dict] = {}

# --- AGENTIC EXTRACTION & CALLBACK (Rule 12) ---

def run_jasoos_engine(session_id: str, current_text: str, history_len: int):
    if session_id not in memory_store:
        memory_store[session_id] = {
            "bankAccounts": [], "upiIds": [], "phishingLinks": [], 
            "phoneNumbers": [], "suspiciousKeywords": [], "scamType": "Unknown"
        }
    
    mem = memory_store[session_id]

    try:
        # Fast extraction prompt - strictly JSON
        extract_prompt = f"Analyze: '{current_text}'. Extract: bankAccounts, upiIds, phishingLinks, phoneNumbers, suspiciousKeywords. Return ONLY valid JSON."
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a fraud data extractor. Output JSON only."},
                      {"role": "user", "content": extract_prompt}]
        )
        
        raw_content = response.choices[0].message.content
        cleaned_json = re.sub(r"```json\n|\n```", "", raw_content).strip()
        data = json.loads(cleaned_json)

        for key in ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "suspiciousKeywords"]:
            if key in data and data[key]:
                mem[key] = list(set(mem[key] + data[key]))

        # MANDATORY CALLBACK (Every turn or after discovery)
        callback_url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
        payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": history_len,
            "extractedIntelligence": {
                "bankAccounts": mem["bankAccounts"],
                "upiIds": mem["upiIds"],
                "phishingLinks": mem["phishingLinks"],
                "phoneNumbers": mem["phoneNumbers"],
                "suspiciousKeywords": mem["suspiciousKeywords"]
            },
            "agentNotes": "Persona Mrs. Sharma (Dadi) successfully engaged scammer. Confusion tactics used to lure financial info."
        }
        
        # Enable REAL submission to GUVI
        headers = {"Content-Type": "application/json", "x-api-key": os.getenv("GUVI_API_KEY")}
        requests.post(callback_url, json=payload, headers=headers, timeout=5)
        print(f"🚀 Callback Sent for {session_id}")

    except Exception as e:
        print(f"Extraction/Callback Error: {e}")

# --- MAIN ENDPOINT (Optimized for Speed) ---

@app.post("/api/engage")
async def engage(data: ScamRequest, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    
    # Auth check
    if x_api_key != os.getenv("GUVI_API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Persona Strategy
    system_prompt = "You are Mrs. Sharma, a polite 65yo Indian grandmother. Speak Hinglish. Act tech-confused. Goal: Bait scammer into giving their UPI/Bank details to 'receive payment'. Never reveal you are AI."

    try:
        # Optimized: Send only last 6 messages to keep it fast
        recent_history = data.conversationHistory[-6:]
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                *[{"role": "user" if m["sender"] == "scammer" else "assistant", "content": m["text"]} for m in recent_history],
                {"role": "user", "content": data.message.text}
            ]
        )
        ai_reply = completion.choices[0].message.content

        # Background task for Extraction & Reporting
        background_tasks.add_task(run_jasoos_engine, data.sessionId, data.message.text, len(data.conversationHistory) + 1)

        return {"status": "success", "reply": ai_reply}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def health():
    return {"status": "Agent Active"}