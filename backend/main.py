import os
import json
import re
import requests
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from groq import Groq

# 1. Environment Load
load_dotenv()

app = FastAPI(title="ScammersAreCooked AI")

# 2. Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 3. GLOBAL MEMORY STORE (Zaroori hai!)
# Yahan hum har session ka extracted data save karenge
session_intelligence_db = {}

# --- MODELS ---
class Message(BaseModel):
    sender: str
    text: str
    timestamp: str

class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[dict]
    metadata: Optional[dict] = {}

# --- HELPER FUNCTIONS ---

# --- HELPER FUNCTIONS (Updated) ---

# --- HELPER FUNCTIONS (Winning Logic) ---

def clean_json_string(json_str):
    try:
        start_index = json_str.find('{')
        end_index = json_str.rfind('}')
        if start_index != -1 and end_index != -1:
            return json_str[start_index : end_index + 1]
        return json_str.strip()
    except Exception:
        return json_str

def extract_intelligence(text: str, session_id: str):
    print(f"🕵️‍♂️ Deep Analyzing Session: {session_id}")
    
    # Init Memory
    if session_id not in session_intelligence_db:
        session_intelligence_db[session_id] = {
            "bankAccounts": [], "upiIds": [], "phishingLinks": [], 
            "phoneNumbers": [], "suspiciousKeywords": [], "scamType": "Unknown"
        }

    try:
        # UPDATED PROMPT: Ab hum Scam Type bhi maang rahe hain
        prompt = f"""
        Analyze this text: "{text}"
        Extract fraud details and identify the Scam Type (e.g., 'Bank Fraud', 'Lottery', 'Job Scam', 'Unknown').
        
        Return ONLY valid JSON:
        {{
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": [],
            "scamType": "..."
        }}
        """
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a fraud analyst. Output JSON only."},
                      {"role": "user", "content": prompt}]
        )
        
        raw_data = response.choices[0].message.content
        cleaned_data = clean_json_string(raw_data)
        extracted_data = json.loads(cleaned_data)

        # Update Memory
        current_data = session_intelligence_db[session_id]
        
        # Lists update karna
        for key in ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "suspiciousKeywords"]:
            if key in extracted_data and extracted_data[key]:
                current_data[key].extend(extracted_data[key])
                current_data[key] = list(set(current_data[key])) # Remove duplicates
        
        # Scam Type update karna
        if "scamType" in extracted_data and extracted_data["scamType"] != "Unknown":
            current_data["scamType"] = extracted_data["scamType"]

        print(f"✅ Updated Intel: {current_data}")

    except Exception as e:
        print(f"❌ Extraction Failed: {e}")

def send_final_report_to_guvi(session_id: str, history_len: int):
    """
    MANDATORY CALLBACK - Ab hum sach mein data bhejenge.
    """
    callback_url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    intel_data = session_intelligence_db.get(session_id, {})
    
    # Default empty values agar kuch na mile
    final_intel = {
        "bankAccounts": intel_data.get("bankAccounts", []),
        "upiIds": intel_data.get("upiIds", []),
        "phishingLinks": intel_data.get("phishingLinks", []),
        "phoneNumbers": intel_data.get("phoneNumbers", []),
        "suspiciousKeywords": intel_data.get("suspiciousKeywords", [])
    }
    
    scam_type = intel_data.get("scamType", "Suspicious Activity")

    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": history_len,
        "extractedIntelligence": final_intel,
        "agentNotes": f"Detected {scam_type}. Engaged by AI Agent 'Mrs. Sharma'. Extracted financial identifiers."
    }
    
    print(f"🚀 Sending Report to GUVI: {json.dumps(payload, indent=2)}")

    try:
        # --- YE LINE AB UNCOMMENT KAR RAHE HAIN (REAL SUBMISSION) ---
        # Note: Ye tabhi chalega jab SessionID real hoga (GUVI wala).
        # Local test me ye 404 ya 400 de sakta hai, par Deploy karte waqt ye ON hona chahiye.
        
        response = requests.post(callback_url, json=payload, timeout=5)
        print(f"📡 GUVI Response Code: {response.status_code}")
        print(f"📡 GUVI Response Body: {response.text}")
        
    except Exception as e:
        print(f"⚠️ Callback Failed (Network Error): {e}")
    """
    AI ke response me se sirf valid JSON dhundta hai using { and }.
    Isse 'Here is your JSON' type ka text hat jata hai.
    """
    try:
        # Sabse pehle '{' aur sabse aakhri '}' dhundo
        start_index = json_str.find('{')
        end_index = json_str.rfind('}')
        
        if start_index != -1 and end_index != -1:
            # Sirf { se } tak ka hissa return karo
            return json_str[start_index : end_index + 1]
        
        return json_str.strip() # Agar { } nahi mile to waise hi try karo
    except Exception:
        return json_str

def extract_intelligence(text: str, session_id: str):
    """
    Background Task: AI message padh kar data nikalega aur Global Memory mein save karega.
    """
    print(f"🕵️‍♂️ Analyzing logic for Session: {session_id}")
    
    # Session Initialize
    if session_id not in session_intelligence_db:
        session_intelligence_db[session_id] = {
            "bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": [], "suspiciousKeywords": []
        }

    try:
        prompt = f"""
        Analyze this text: "{text}"
        Extract fraud details. Return ONLY a single JSON object. Do not write any introduction.
        Format:
        {{
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }}
        """
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a JSON extractor. Output only JSON."},
                      {"role": "user", "content": prompt}]
        )
        
        raw_data = response.choices[0].message.content
        # Debugging ke liye print kar rahe hain ki AI ne kya bheja
        print(f"🤖 AI Raw Output: {raw_data}") 

        cleaned_data = clean_json_string(raw_data)
        extracted_data = json.loads(cleaned_data)

        # Memory Update
        current_data = session_intelligence_db[session_id]
        for key in current_data:
            if key in extracted_data and extracted_data[key]:
                current_data[key].extend(extracted_data[key])
                current_data[key] = list(set(current_data[key]))

        print(f"✅ Updated Intel for {session_id}: {current_data}")

    except Exception as e:
        print(f"❌ Extraction Failed: {e}")
    """AI ke response se markdown ```json hatata hai"""
    clean = re.sub(r"```json\n|\n```", "", json_str).strip()
    return clean

def extract_intelligence(text: str, session_id: str):
    """
    Background Task: AI message padh kar data nikalega aur Global Memory mein save karega.
    """
    print(f"🕵️‍♂️ Analyzing logic for Session: {session_id}")
    
    # Agar session pehli baar aaya hai, toh memory initialize karo
    if session_id not in session_intelligence_db:
        session_intelligence_db[session_id] = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }

    try:
        prompt = f"""
        Analyze this text for fraud details: "{text}"
        
        Extract:
        1. bankAccounts (Account numbers, IFSC)
        2. upiIds (e.g., name@okicici, numbers@paytm)
        3. phishingLinks (http/https urls)
        4. phoneNumbers (Mobile numbers)
        5. suspiciousKeywords (e.g., urgent, block, kyc, verify, otp)

        Return ONLY valid JSON format like:
        {{
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }}
        """
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a precise data extractor. Output only JSON."},
                      {"role": "user", "content": prompt}]
        )
        
        # 1. JSON Clean aur Parse karo
        raw_data = response.choices[0].message.content
        cleaned_data = clean_json_string(raw_data)
        extracted_data = json.loads(cleaned_data)

        # 2. Memory Update karo (Append new data)
        current_data = session_intelligence_db[session_id]
        
        # Sirf naya data add karo (Duplicates avoid karne ke liye set use kar sakte hain, par list append is fine for now)
        for key in current_data:
            if key in extracted_data and extracted_data[key]:
                # List extend kar rahe hain
                current_data[key].extend(extracted_data[key])
                # Unique bana lo
                current_data[key] = list(set(current_data[key]))

        print(f"✅ Updated Intel for {session_id}: {current_data}")

    except Exception as e:
        print(f"❌ Extraction Failed: {e}")

def send_final_report_to_guvi(session_id: str, history_len: int):
    """
    Mandatory Callback: GUVI ko final report bhejna.
    """
    callback_url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    # Memory se data uthao. Agar nahi hai to empty default use karo
    intel_data = session_intelligence_db.get(session_id, {
        "bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": [], "suspiciousKeywords": []
    })

    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": history_len,
        "extractedIntelligence": intel_data,
        "agentNotes": "The scammer was engaged by Mrs. Sharma (AI Agent). Multiple scam indicators detected."
    }
    
    try:
        # REAL SUBMISSION (Problem Statement Rule #12)
        # response = requests.post(callback_url, json=payload, timeout=10)
        # print(f"🚀 Callback Status: {response.status_code} | Body: {response.text}")
        
        # NOTE: Testing ke waqt GUVI ka server shayad error de agar session ID real nahi hai.
        # Isliye abhi ke liye print kar rahe hain. 
        # Jab Deploy karega, tab upar wali line uncomment kar dena.
        print(f"🚀 [MOCK SEND] Report sent to GUVI: {json.dumps(payload, indent=2)}")
        
    except Exception as e:
        print(f"⚠️ Callback Error: {e}")

# --- API ENDPOINT ---

@app.post("/api/engage")
async def engage(data: ScamRequest, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    
    # 1. Security Check
    if x_api_key != os.getenv("GUVI_API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. Dadi Logic (Sakshi's Persona)
    system_prompt = """
    You are Mrs. Sharma, a 65-year-old Indian grandmother. 
    You are friendly but extremely confused about technology. 
    You call everyone 'beta'. You speak in 'Hinglish' (Hindi + English).
    
    Objective: Keep the scammer talking. Ask dumb questions.
    If they ask for money/OTP, say "Beta chashma nahi mil raha" or "Internet slow hai".
    NEVER admit you are an AI.
    """

    try:
        # AI Reply
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                *[{"role": "user" if m["sender"] == "scammer" else "assistant", "content": m["text"]} for m in data.conversationHistory],
                {"role": "user", "content": data.message.text}
            ]
        )
        ai_reply = completion.choices[0].message.content

        # 3. BACKGROUND TASKS (Ye user ko wait nahi karwayenge)
        # Task A: Intelligence Extract karo
        background_tasks.add_task(extract_intelligence, data.message.text, data.sessionId)

        # Task B: Agar chat lambi ho gayi (e.g., > 6 messages), toh GUVI ko report bhej do
        # Problem statement kehta hai "Once scam intent is detected... send result"
        # Hum har 5 message ke baad update bhej sakte hain ya session end hone par
        if len(data.conversationHistory) > 5:
             background_tasks.add_task(send_final_report_to_guvi, data.sessionId, len(data.conversationHistory) + 1)

        # 4. Return Response
        return {
            "status": "success",
            "reply": ai_reply
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def home():
    return {"status": "AI Agent Active", "team": "ScammersAreCooked"}