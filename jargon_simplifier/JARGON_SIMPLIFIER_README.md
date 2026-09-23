# 🧠 JargonSimplifier - AI-Powered Layman Language Translator

An AI-powered software application that transforms complex, intimidating technical, medical, legal, financial, and scientific jargon into crystal-clear layman's terms that anyone can understand.

Built with **LangChain**, **Google Gemini**, and **python-dotenv**.

---

## 📦 Installed & Used Pip Modules

Here is the complete breakdown of pip modules installed and used in this project:

### 1. **Core Direct Dependencies**
| Package | Version | Purpose & Usage |
| :--- | :--- | :--- |
| [`python-dotenv`](https://pypi.org/project/python-dotenv/) | `1.2.3` | **(Mandatory Requirement)** Automatically loads API keys securely from your `.env` file into system environment variables. |
| [`langchain`](https://pypi.org/project/langchain/) | `1.4.0` | **(Mandatory Requirement)** Orchestration framework for LLM chains and prompt engineering pipelines. |
| [`langchain-core`](https://pypi.org/project/langchain-core/) | `1.6.2` | Core abstractions for prompt templates (`ChatPromptTemplate`), outputs (`StrOutputParser`), and LCEL runnable pipelines (`prompt | model | parser`). |
| [`langchain-google-genai`](https://pypi.org/project/langchain-google-genai/) | `4.4.0` | Official LangChain integration with Google Gemini chat models (`ChatGoogleGenerativeAI`). |
| [`rich`](https://pypi.org/project/rich/) | `15.0.0` | Beautiful terminal formatting, panels, markdown rendering, styled tables, and spinners. |

### 2. **Key Sub-dependencies (Automatically Installed)**
- **`google-genai` / `google-auth`**: Google Gemini official client SDK & authentication layer.
- **`pydantic` & `pydantic-core`**: Data validation and type safety for LangChain schemas.
- **`httpx` & `httpcore`**: Modern async/sync HTTP networking client for LLM API calls.
- **`langsmith`**: Observability, debugging, and tracing support for LangChain.

---

## ⚙️ Configuration (`.env`)

Your `.env` file is pre-configured with your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

---

## 🚀 How to Run

### Option 1: Interactive Terminal Mode
Start the interactive CLI:
```bash
.venv/bin/python jargon_simplifier.py
```
- Type any complex term (e.g. `Backpropagation`, `Epigenetics`, `Zero-Knowledge Proofs`).
- Type `style` to switch explanation modes on the fly.
- Type `exit` or `q` to quit.

---

### Option 2: Single-Shot Command Line Mode
Quickly translate any term directly from your terminal:

```bash
# Standard Layman explanation
.venv/bin/python jargon_simplifier.py "Quantum Entanglement"

# ELI5 (Explain Like I'm 5) Story mode
.venv/bin/python jargon_simplifier.py "Retrieval-Augmented Generation" --style 2

# Real-world Analogy mode
.venv/bin/python jargon_simplifier.py "Kubernetes" --style 3

# Executive 1-Liner / Bottom-line mode
.venv/bin/python jargon_simplifier.py "EBITDA" --style 4
```

---

### Option 3: Modern Web UI (Dashboard)
Run the local web dashboard:
```bash
.venv/bin/python web_server.py 8080
```
Then open **`http://localhost:8080`** in your browser to enjoy:
- Glassmorphism dark mode UI.
- Interactive mode switcher.
- Quick topic tags.
- Instant copy-to-clipboard for generated markdown.

---

## 🎯 Supported Explanation Styles

1. **💡 Standard Layman Breakdown**: Definition in plain English + Real-world analogy + Step-by-step breakdown + Why it matters + 10-second cheat sheet.
2. **👶 ELI5 (Explain Like I'm 5)**: Engaging, playful story explanation designed for children or complete beginners.
3. **🍕 Analogy Master**: Explains purely through dual everyday analogies (e.g. cooking, sports, cars).
4. **👔 Executive 1-Liner**: High-impact, jargon-free summary highlighting essence, practical impact, and common misconceptions.
