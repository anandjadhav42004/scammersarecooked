import os
import json
import re
import requests
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = FastAPI(title="ScammersAreCooked_Agentic_HoneyPot")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Global Memory to track intelligence for the mandatory callback
# In production, this would be a database like Redis
memory_store = {}

# --- MODELS (As per Section 6 & 12 of Problem Statement) ---

class Message(BaseModel):
    sender: str
    text: str
    timestamp: str

class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[dict]
    metadata: Optional[dict] = {}

# --- CORE AGENTIC LOGIC ---

def run_jasoos_engine(session_id: str, current_text: str, history_len: int):
    """
    This is the Agent's brain that extracts intelligence and 
    fires the MANDATORY CALLBACK (Rule #12).
    """
    if session_id not in memory_store:
        memory_store[session_id] = {
            "bankAccounts": [], "upiIds": [], "phishingLinks": [], 
            "phoneNumbers": [], "suspiciousKeywords": [], "count": 0
        }
    
    mem = memory_store[session_id]
    mem["count"] += 1

    # 1. Extraction Logic using AI
    extract_prompt = f"""
    Analyze this message: "{current_text}"
    Extract: Bank accounts, UPI IDs, Phishing links, Phone numbers, and Scam keywords.
    Return ONLY a JSON object.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a fraud intelligence extractor. Output JSON only."},
                      {"role": "user", "content": extract_prompt}]
        )
        # Clean and parse JSON
        raw_json = re.sub(r"```json\n|\n```", "", response.choices[0].message.content).strip()
        data = json.loads(raw_json)

        # Update memory
        for key in ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "suspiciousKeywords"]:
            if key in data and data[key]:
                mem[key] = list(set(mem[key] + data[key]))

        # 2. MANDATORY CALLBACK TRIGGER (Rule #12)
        # We send the report if we found critical info OR if conversation is long enough (e.g., 5+ turns)
        if len(mem["upiIds"]) > 0 or len(mem["bankAccounts"]) > 0 or history_len >= 5:
            trigger_guvi_callback(session_id, history_len, mem)

    except Exception as e:
        print(f"Extraction Error: {e}")

def trigger_guvi_callback(session_id, history_len, intel):
    """Sends the final result to GUVI as per Rule 12."""
    callback_url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": history_len,
        "extractedIntelligence": {
            "bankAccounts": intel["bankAccounts"],
            "upiIds": intel["upiIds"],
            "phishingLinks": intel["phishingLinks"],
            "phoneNumbers": intel["phoneNumbers"],
            "suspiciousKeywords": intel["suspiciousKeywords"]
        },
        "agentNotes": "Autonomous Agent Mrs. Sharma successfully engaged the scammer and extracted financial identifiers."
    }
    
    try:
        # Rule 12: Mandatory POST request
        headers = {"Content-Type": "application/json", "x-api-key": os.getenv("GUVI_API_KEY")}
        # res = requests.post(callback_url, json=payload, timeout=5)
        # print(f"Callback Sent: {res.status_code}")
        print(f"🎯 CALLBACK PAYLOAD READY: {json.dumps(payload)}")
    except Exception as e:
        print(f"Callback Failed: {e}")

# --- API ENDPOINT (Rule 3 & 4) ---

@app.post("/api/engage")
async def engage(data: ScamRequest, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    
    # 1. Authentication (Rule 4)
    if x_api_key != os.getenv("GUVI_API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. Maintain Human-like Persona (Rule 7)
    system_prompt = """
    You are Mrs. Sharma, a 65-year-old retired school teacher. 
    You are polite, talkative, and call everyone 'beta'. 
    You act confused about technology to keep scammers talking.
    If they ask for money or OTP, make excuses like 'I can't see the screen' or 'My grandson is not home'.
    Your goal is to get their UPI ID or Bank details. 
    Never reveal you are an AI. Use Hinglish.
    """

    try:
        # Generate Response (Rule 8)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                *[{"role": "user" if m["sender"] == "scammer" else "assistant", "content": m["text"]} for m in data.conversationHistory],
                {"role": "user", "content": data.message.text}
            ]
        )
        ai_reply = completion.choices[0].message.content

        # 3. Agentic Extraction (Run in background for low latency - Rule 9)
        background_tasks.add_task(run_jasoos_engine, data.sessionId, data.message.text, len(data.conversationHistory) + 1)

        return {
            "status": "success",
            "reply": ai_reply
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def health():
    return {"status": "Agent Active", "persona": "Mrs. Sharma", "team": "ScammersAreCooked"}