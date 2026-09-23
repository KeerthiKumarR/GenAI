# 🤖 GenAI Python Projects Suite

A curated collection of Generative AI, LLM orchestration, semantic routing, session memory, and utility applications built with **Google Gemini**, **LangChain**, and **FastAPI**.

---

## 📂 Projects Overview

| Project | File / Directory | Key Technologies | Description |
| :--- | :--- | :--- | :--- |
| **FastAPI Jargon & Token Tracker** | `main.py` | FastAPI, LangChain, Gemini, Pydantic | Production-grade API with custom token tracking middleware, timing metrics, and async Jargon translation. |
| **Semantic Router & Guardrails** | `semantic_router_guardrails.py` | LangChain, `RunnableBranch`, Gemini | Dynamic intent classification & safety guardrails routing queries to code generators, toxic prompt rejection, or polite boundaries. |
| **Chat Memory & Session History** | `chat_memory_demo.py` | `RunnableWithMessageHistory`, Gemini | Stateful multi-turn conversational AI maintaining per-session memory buffers (`InMemoryChatMessageHistory`). |
| **Jargon Simplifier Application** | `jargon_simplifier/` | LangChain, Rich CLI, FastAPI Server | Dual-interface tool (CLI & Web) to transform complex technical, legal, and medical jargon into plain English. |
| **QR Code Generator** | `qr_app/` | `qrcode`, Pillow | Customized QR code generator with styling, borders, and image export. |
| **Dataset Organizer** | `organize_data.py` | `pathlib`, `shutil` | Automated utility script to categorize and sort unorganized multi-format files into structured folders. |

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/KeerthiKumarR/GenAI.git
cd GenAI
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## 🚀 Running the Projects

### 1. FastAPI Server & Token Tracking Middleware
```bash
uvicorn main:app --reload --port 8000
```
- Open Swagger Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Translate Jargon endpoint: `POST /translate-jargon`
- Global metrics: `GET /metrics`

### 2. Semantic Router & Guardrails
```bash
python semantic_router_guardrails.py
```
Demonstrates how `RunnableBranch` categorizes inputs and routes toxic queries to security filters while answering legitimate coding questions.

### 3. Chat Pipeline with Multi-Turn Memory
```bash
python chat_memory_demo.py
```
Tests multi-turn persistence across independent session IDs.

### 4. Jargon Simplifier (CLI & Web)
```bash
# Terminal Interactive Mode
python jargon_simplifier/jargon_simplifier.py

# Or Web App Mode
python jargon_simplifier/web_server.py
```

### 5. File / Data Organizer
```bash
python organize_data.py
```

---

## 🛡️ Best Practices & Security
- **API Key Protection**: All sensitive tokens and keys are loaded via `python-dotenv` and ignored via `.gitignore`.
- **Token Observability**: Integrated middleware tracks prompt and completion tokens for latency and cost tracking.
