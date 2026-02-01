# Project Architecture 🏗️

1. **Frontend:** API Endpoint only (REST API).
2. **Backend:** FastAPI (Python).
3. **Brain:** Llama 3.3 (via Groq Cloud).
4. **Logic:** 
   - Receives Scam message.
   - Extracts intelligence (UPI, Bank, etc.) in background tasks.
   - Sends mandatory final report to GUVI evaluation endpoint.