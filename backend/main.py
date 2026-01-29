import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from groq import Groq

# .env file load karo
load_dotenv()

app = FastAPI()

# Groq Client setup (Key .env se uthayega)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Models (GUVI ke format ke hisaab se)
class Message(BaseModel):
    sender: str
    text: str
    timestamp: str

class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[dict]
    metadata: Optional[dict] = {}

@app.post("/api/engage")
async def engage(data: ScamRequest, x_api_key: str = Header(None)):
    # Security Check
    if x_api_key != os.getenv("GUVI_API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Humara System Prompt (Dadi ka Character)
    system_prompt = """
    You are Mrs. Sharma, a 65-year-old Indian grandmother. 
    You are friendly but very confused about technology. 
    You call everyone 'beta'. You speak in a mix of Hindi and English (Hinglish).
    A scammer is messaging you. Act confused to keep them talking. 
    Ask things like 'Beta ye OTP kya hota hai?' or 'Mere bank wale toh ghar aate hain'.
    Do not reveal you are an AI. 
    """

    try:
        # AI ko message bhejna
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                # Purani chat history AI ko dena taaki wo sab yaad rakhe
                *[{"role": m["sender"] if m["sender"] != "scammer" else "user", "content": m["text"]} for m in data.conversationHistory],
                {"role": "user", "content": data.message.text}
            ]
        )
        
        ai_reply = completion.choices[0].message.content

        return {
            "status": "success",
            "reply": ai_reply
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def home():
    return {"status": "AI Agent Active", "team": "ScammersAreCooked"}