import os
import json
import re
import requests
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from groq import Groq

# 1. Setup
load_dotenv()
app = FastAPI(title="ScammersAreCooked_Master_Agent")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Global Memory for Extraction
memory_store = {}

# --- MODELS (GUVI Compliance) ---
class Message(BaseModel):
    sender: str
    text: str
    timestamp: str

class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[dict]
    metadata: Optional[dict] = {}

# --- SAKSHI'S BRAIN: EXTRACTION & STRATEGY ---

def run_jasoos_engine(session_id: str, current_text: str, history_len: int):
    """
    SAKSHI'S PART: Analyzing scam intent and extracting data.
    """
    if session_id not in memory_store:
        memory_store[session_id] = {
            "bankAccounts": [], "upiIds": [], "phishingLinks": [], 
            "phoneNumbers": [], "suspiciousKeywords": [], "scamType": "Unknown"
        }
    
    mem = memory_store[session_id]

    # Extraction Prompt (High Precision)
    extract_prompt = f"""
    Analyze this scammer message: "{current_text}"
    1. Identify Scam Type (e.g. Bank Fraud, Job Scam, Lottery).
    2. Extract: Bank Accounts, UPI IDs, Phishing Links, Phone Numbers.
    3. Identify Suspicious Keywords used (e.g. Urgent, OTP, Blocked).
    Return ONLY a valid JSON object.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a fraud analyst. Output only JSON."},
                      {"role": "user", "content": extract_prompt}]
        )
        
        # Clean AI output
        raw_content = response.choices[0].message.content
        cleaned_json = re.sub(r"```json\n|\n```", "", raw_content).strip()
        data = json.loads(cleaned_json)

        # Update Memory (Sakshi's Intelligence Layer)
        for key in ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "suspiciousKeywords"]:
            if key in data and data[key]:
                mem[key] = list(set(mem[key] + data[key]))
        
        if "scamType" in data: mem["scamType"] = data["scamType"]

        # MANDATORY CALLBACK (Rule #12)
        # If we have any intel or it's a long chat, report to GUVI
        if len(mem["upiIds"]) > 0 or len(mem["bankAccounts"]) > 0 or history_len >= 5:
            trigger_guvi_callback(session_id, history_len, mem)

    except Exception as e:
        print(f"Extraction Error: {e}")

def trigger_guvi_callback(session_id, history_len, intel):
    """MANDATORY CALLBACK - Rule 12"""
    callback_url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    # Sakshi's Agent Notes Strategy
    agent_notes = f"Detected {intel['scamType']}. Persona 'Mrs. Sharma' engaged scammer. " \
                  f"Used confusion tactics to lure scammer into revealing financial info."

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
        "agentNotes": agent_notes
    }
    
    try:
        headers = {"Content-Type": "application/json", "x-api-key": os.getenv("GUVI_API_KEY")}
        # res = requests.post(callback_url, json=payload, timeout=5) # Real submission
        print(f"🎯 CALLBACK PAYLOAD READY: {json.dumps(payload)}")
    except Exception as e:
        print(f"Callback Failed: {e}")

# --- MAIN ENDPOINT (Anand's Backend) ---

@app.post("/api/engage")
async def engage(data: ScamRequest, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    
    # 1. Authentication (Rule 4)
    if x_api_key != os.getenv("GUVI_API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. SAKSHI'S PERSONA (Rule 7)
    system_prompt = """
    PERSONA: You are Mrs. Sharma, a 65-year-old retired school teacher.
    BEHAVIOR: You are polite, lonely, and call everyone 'beta'. You act confused about technology.
    STRATEGY: 
    - If they ask for OTP, say "Beta, I can't find my glasses, can you wait?".
    - If they ask for money, say "I have 2 lakhs in my savings, I want to send it, but I don't know your details. Please give me your UPI ID or Bank account so I can ask my neighbor to pay you."
    - This is a TRAP to get the scammer's bank/UPI info.
    - Never reveal you are an AI. Speak in Hinglish (Hindi + English).
    """

    try:
        # AI Engagement (Rule 8 & 9)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                *[{"role": "user" if m["sender"] == "scammer" else "assistant", "content": m["text"]} for m in data.conversationHistory],
                {"role": "user", "content": data.message.text}
            ]
        )
        ai_reply = completion.choices[0].message.content

        # 3. BACKGROUND TASKS (Agentic Extraction - Rule 11)
        background_tasks.add_task(run_jasoos_engine, data.sessionId, data.message.text, len(data.conversationHistory) + 1)

        return {
            "status": "success",
            "reply": ai_reply
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def health():
    return {"status": "Agent Active", "persona": "Mrs. Sharma (Sakshi's Brain)", "team": "ScammersAreCooked (Anand's Backend)"}