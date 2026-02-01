# 🛡️ ScammersAreCooked: The Intelligent Honey-Pot 👵

[![Hackathon](https://img.shields.io/badge/India%20AI%20Impact-Buildathon%202026-blueviolet)](https://www.guvi.in/mlp/india_AI_impact_buildathon)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**ScammersAreCooked** is a next-generation AI-driven Agentic Honey-Pot designed to fight India's rising fraud crisis. Our system doesn't just block scammers—it **wastes their time** and **extracts their secrets**.

---
🌐 Live API Endpoint: https://scammersarecooked.onrender.com/api/engage
🔑 API Key: SCAMMERS_ARE_COOKED_SECRET


## 🎯 The Concept: "The Bholi Dadi Strategy" 👵
Most AI systems are designed to be helpful. Ours is designed to be **deceptive**. 

When a scammer sends a message, our agent takes the persona of **Mrs. Sharma**, a 65-year-old retired grandmother. She is friendly, slightly confused by technology, but has a "lot of money in her savings account." 

### Why this works?
- **High Engagement:** Scammers feel they have an "easy target," keeping them engaged for 20+ messages.
- **Deceptive Extraction:** While "Dadi" is acting confused, the AI is secretly scanning the conversation to extract UPI IDs, Bank details, and Phishing links.
- **Law Enforcement Ready:** All extracted intelligence is automatically formatted and reported to the authorities (GUVI Evaluation Endpoint).

---

## 🚀 Features
- 🧠 **Autonomous Reasoning:** Uses Llama 3.1 / GPT-4o to adapt to scammer tactics in real-time.
- 🎭 **Dynamic Persona:** Maintains a consistent "Mrs. Sharma" personality across multi-turn chats.
- 🕵️ **Intelligence Extraction:** Real-time extraction of:
    - `upi_id`
    - `bank_account_no`
    - `ifsc_code`
    - `phishing_url`
- 💾 **Session History:** Remembers every message to stay ahead of the scammer's logic.
- ⚡ **Low Latency:** Powered by **FastAPI** and **Groq Cloud** for lightning-fast replies.

---

## 🛠️ Tech Stack
- **Language:** Python
- **Backend:** FastAPI
- **AI Brain:** Groq (Llama 3.1) / OpenAI API
- **History Management:** JSON Session Store (Scaleable to Redis)
- **Deployment:** Render

---

## 📂 Project Structure
```text
ScammersAreCooked/
├── backend/            # FastAPI Source Code
│   ├── main.py         # Entry point for the API
│   └── utils.py        # Extraction & Intelligence logic
├── brain/              # AI Persona & Prompt Engineering
│   ├── system_prompt.txt # The "Dadi" Persona Script
│   └── extraction.json  # Data extraction rules
├── docs/               # Architecture diagrams
└── README.md           # You are here!
🏗️ How it Works (The Flow)
Receive: Scam message arrives at /api/engage.
Context: System fetches previous chat history for that sessionId.
Reason: The AI reasons: "Is this a scam? Yes. How would Dadi respond to this?"
Respond: Returns a believable, human-like response to the scammer.
Extract: If the scammer reveals payment info, it's captured immediately.
Report: Sends the final Intelligence Report to GUVI.
👥 The Team: ScammersAreCooked
Name	Role	GitHub
Anand Jadhav	Backend Architect & Integration	@anandjadhav42004
Sakshi Kadadekar	AI Persona & Strategy Design	@sakshi-kadadekar
