#!/usr/bin/env python3
"""
Web UI Server for JargonSimplifier
Built with Python HTTP Server, LangChain, Google Gemini, and python-dotenv.
"""

import os
import json
import sys
import warnings
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

# Load environment from current directory's .env file
load_dotenv(dotenv_path=CURRENT_DIR / ".env")

# Ensure API Key
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[ERROR] GOOGLE_API_KEY or GEMINI_API_KEY not found in .env")
os.environ["GOOGLE_API_KEY"] = api_key or ""
if "GEMINI_API_KEY" in os.environ:
    del os.environ["GEMINI_API_KEY"]

simplifier = None

def get_simplifier():
    global simplifier
    if simplifier is None:
        from jargon_simplifier import JargonSimplifier
        simplifier = JargonSimplifier()
    return simplifier

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JargonSimplifier - AI Layman Language Explainer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg-color: #0d1117;
            --card-bg: rgba(22, 27, 34, 0.85);
            --card-border: rgba(56, 139, 253, 0.2);
            --card-border-glow: rgba(56, 139, 253, 0.4);
            --primary: #58a6ff;
            --primary-gradient: linear-gradient(135deg, #58a6ff 0%, #bc8cff 100%);
            --accent: #3fb950;
            --text: #f0f6fc;
            --text-dim: #8b949e;
            --input-bg: #090d13;
            --tag-bg: rgba(56, 139, 253, 0.12);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(88, 166, 255, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(188, 140, 255, 0.08) 0%, transparent 40%);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2.5rem 1rem;
        }

        .container {
            width: 100%;
            max-width: 880px;
        }

        header {
            text-align: center;
            margin-bottom: 2.5rem;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--tag-bg);
            border: 1px solid var(--card-border);
            color: var(--primary);
            padding: 0.4rem 1rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1rem;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        h1 {
            font-size: 2.8rem;
            font-weight: 800;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.6rem;
            letter-spacing: -0.5px;
        }

        .subtitle {
            color: var(--text-dim);
            font-size: 1.15rem;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.5;
        }

        .card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            margin-bottom: 2rem;
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: var(--card-border-glow);
        }

        .input-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text);
        }

        input[type="text"], textarea {
            width: 100%;
            background: var(--input-bg);
            border: 1px solid #30363d;
            color: var(--text);
            padding: 1rem 1.2rem;
            border-radius: 12px;
            font-size: 1.05rem;
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        input[type="text"]:focus, textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.2);
        }

        .styles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.8rem;
            margin-bottom: 1.5rem;
        }

        .style-btn {
            background: var(--input-bg);
            border: 1px solid #30363d;
            color: var(--text-dim);
            padding: 0.8rem;
            border-radius: 10px;
            cursor: pointer;
            text-align: left;
            transition: all 0.2s;
        }

        .style-btn:hover {
            border-color: var(--primary);
            color: var(--text);
        }

        .style-btn.active {
            background: rgba(88, 166, 255, 0.15);
            border-color: var(--primary);
            color: var(--primary);
            font-weight: 600;
        }

        .style-btn-title {
            font-size: 0.95rem;
            display: block;
            margin-bottom: 0.2rem;
        }

        .style-btn-desc {
            font-size: 0.75rem;
            opacity: 0.8;
            display: block;
        }

        .quick-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }

        .quick-tag {
            background: #21262d;
            border: 1px solid #30363d;
            color: var(--text-dim);
            padding: 0.35rem 0.8rem;
            border-radius: 20px;
            font-size: 0.82rem;
            cursor: pointer;
            transition: all 0.2s;
        }

        .quick-tag:hover {
            background: var(--primary);
            color: #0d1117;
            border-color: var(--primary);
            font-weight: 600;
        }

        .btn-submit {
            width: 100%;
            background: var(--primary-gradient);
            border: none;
            color: #0d1117;
            font-weight: 700;
            font-size: 1.1rem;
            padding: 1rem;
            border-radius: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.6rem;
            transition: transform 0.15s, filter 0.2s;
            box-shadow: 0 4px 20px rgba(88, 166, 255, 0.3);
        }

        .btn-submit:hover {
            filter: brightness(1.1);
            transform: translateY(-2px);
        }

        .btn-submit:active {
            transform: translateY(0);
        }

        .btn-submit:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .result-card {
            display: none;
            background: var(--card-bg);
            border: 1px solid var(--accent);
            border-radius: 18px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(63, 185, 80, 0.15);
            position: relative;
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #30363d;
        }

        .result-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .copy-btn {
            background: #21262d;
            border: 1px solid #30363d;
            color: var(--text);
            padding: 0.4rem 0.8rem;
            border-radius: 8px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        }

        .copy-btn:hover {
            background: var(--primary);
            color: #0d1117;
        }

        .stats-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            margin-bottom: 1.5rem;
            padding: 0.75rem 1rem;
            background: rgba(13, 17, 23, 0.7);
            border: 1px solid rgba(88, 166, 255, 0.2);
            border-radius: 10px;
        }

        .stat-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.85rem;
            color: #c9d1d9;
            background: rgba(33, 38, 45, 0.8);
            padding: 0.3rem 0.6rem;
            border-radius: 6px;
            border: 1px solid #30363d;
        }

        .stat-chip strong {
            color: var(--primary);
        }

        .stat-chip.accent strong {
            color: var(--accent);
        }

        .markdown-body {
            color: var(--text);
            line-height: 1.7;
            font-size: 1.05rem;
        }

        .markdown-body h3 {
            color: var(--primary);
            margin: 1.5rem 0 0.5rem 0;
            font-size: 1.15rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .markdown-body p {
            margin-bottom: 1rem;
            color: #c9d1d9;
        }

        .markdown-body ul, .markdown-body ol {
            padding-left: 1.5rem;
            margin-bottom: 1rem;
        }

        .markdown-body li {
            margin-bottom: 0.4rem;
            color: #c9d1d9;
        }

        .markdown-body strong {
            color: #f0f6fc;
        }

        .loader {
            display: none;
            text-align: center;
            padding: 2rem;
            color: var(--text-dim);
        }

        .spinner {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 3px solid rgba(88, 166, 255, 0.2);
            border-radius: 50%;
            border-top-color: var(--primary);
            animation: spin 0.8s linear infinite;
            margin-bottom: 1rem;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        footer {
            margin-top: auto;
            text-align: center;
            color: var(--text-dim);
            font-size: 0.85rem;
            padding: 1.5rem 0;
        }

        footer a {
            color: var(--primary);
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge">🚀 Powered by LangChain + Google Gemini + Dotenv</div>
            <h1>Jargon Simplifier</h1>
            <p class="subtitle">Transform intimidating tech, finance, medical, and scientific jargon into clear, intuitive layman explanations anyone can understand.</p>
        </header>

        <div class="card">
            <div class="input-group">
                <label for="jargon-input">What complex term or concept do you want explained?</label>
                <input type="text" id="jargon-input" placeholder="e.g., Quantum Supremacy, Backpropagation, EBITDA, Kubernetes..." autofocus>
            </div>

            <div class="quick-tags">
                <span class="quick-tag" onclick="selectQuickTag('Zero-Knowledge Proofs')">Zero-Knowledge Proofs</span>
                <span class="quick-tag" onclick="selectQuickTag('Kubernetes Pods')">Kubernetes</span>
                <span class="quick-tag" onclick="selectQuickTag('Retrieval-Augmented Generation (RAG)')">RAG in AI</span>
                <span class="quick-tag" onclick="selectQuickTag('Epigenetics')">Epigenetics</span>
                <span class="quick-tag" onclick="selectQuickTag('Overfitting & Underfitting')">Overfitting</span>
                <span class="quick-tag" onclick="selectQuickTag('EBITDA')">EBITDA</span>
            </div>

            <label>Choose Explanation Style:</label>
            <div class="styles-grid">
                <div class="style-btn active" onclick="setStyle('1', this)">
                    <span class="style-btn-title">💡 Standard Layman</span>
                    <span class="style-btn-desc">Structured breakdown with analogy & takeaways</span>
                </div>
                <div class="style-btn" onclick="setStyle('2', this)">
                    <span class="style-btn-title">👶 ELI5 (Explain Like 5)</span>
                    <span class="style-btn-desc">Playful story for absolute beginners</span>
                </div>
                <div class="style-btn" onclick="setStyle('3', this)">
                    <span class="style-btn-title">🍕 Analogy Master</span>
                    <span class="style-btn-desc">Everyday real-world comparisons</span>
                </div>
                <div class="style-btn" onclick="setStyle('4', this)">
                    <span class="style-btn-title">👔 Executive 1-Liner</span>
                    <span class="style-btn-desc">Crisp, bottom-line summary</span>
                </div>
            </div>

            <button id="submit-btn" class="btn-submit" onclick="generateExplanation()">
                <span>✨ Simplify Into Plain English</span>
            </button>
        </div>

        <div id="loader" class="loader">
            <div class="spinner"></div>
            <p>Asking Gemini AI via LangChain pipeline to simplify your jargon...</p>
        </div>

        <div id="result-card" class="result-card">
            <div class="result-header">
                <div class="result-title" id="result-term">✨ Explanation</div>
                <button class="copy-btn" onclick="copyResult()">📋 Copy Markdown</button>
            </div>
            
            <div id="stats-bar" class="stats-bar" style="display: none;">
                <div class="stat-chip">⏱️ Latency: <strong id="stat-latency">-</strong></div>
                <div class="stat-chip">📥 Prompt Tokens: <strong id="stat-input-tokens">-</strong></div>
                <div class="stat-chip">📤 Completion Tokens: <strong id="stat-output-tokens">-</strong></div>
                <div class="stat-chip accent">📊 Total Tokens: <strong id="stat-total-tokens">-</strong></div>
                <div class="stat-chip">📝 Words: <strong id="stat-words">-</strong></div>
                <div class="stat-chip accent">🎯 Tokens/Word: <strong id="stat-ratio">-</strong></div>
            </div>

            <div id="result-content" class="markdown-body"></div>
        </div>

        <footer>
            Built with <strong>LangChain</strong>, <strong>python-dotenv</strong>, and <strong>Google Gemini AI</strong>.
        </footer>
    </div>

    <script>
        let selectedStyle = "1";
        let rawMarkdown = "";

        function setStyle(styleId, element) {
            selectedStyle = styleId;
            document.querySelectorAll('.style-btn').forEach(btn => btn.classList.remove('active'));
            element.classList.add('active');
        }

        function selectQuickTag(tag) {
            document.getElementById('jargon-input').value = tag;
            generateExplanation();
        }

        async function generateExplanation() {
            const input = document.getElementById('jargon-input');
            const term = input.value.trim();
            if (!term) return;

            const submitBtn = document.getElementById('submit-btn');
            const loader = document.getElementById('loader');
            const resultCard = document.getElementById('result-card');
            const resultContent = document.getElementById('result-content');
            const resultTerm = document.getElementById('result-term');
            const statsBar = document.getElementById('stats-bar');

            submitBtn.disabled = true;
            loader.style.display = 'block';
            resultCard.style.display = 'none';

            try {
                const response = await fetch('/api/simplify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ term: term, style: selectedStyle })
                });

                const data = await response.json();
                if (data.error) {
                    throw new Error(data.error);
                }

                rawMarkdown = data.explanation;
                resultTerm.textContent = `✨ Layman Guide: ${term}`;
                resultContent.innerHTML = marked.parse(data.explanation);

                // Populate token & latency stats & ratio
                if (data.total_tokens !== undefined) {
                    document.getElementById('stat-latency').textContent = data.process_time || '-';
                    document.getElementById('stat-input-tokens').textContent = data.input_tokens || '0';
                    document.getElementById('stat-output-tokens').textContent = data.output_tokens || '0';
                    document.getElementById('stat-total-tokens').textContent = data.total_tokens || '0';
                    document.getElementById('stat-words').textContent = data.word_count || '-';
                    document.getElementById('stat-ratio').textContent = (data.tokens_per_word !== undefined ? data.tokens_per_word + 'x' : '-');
                    statsBar.style.display = 'flex';
                }

                resultCard.style.display = 'block';
                resultCard.scrollIntoView({ behavior: 'smooth' });
            } catch (err) {
                alert("Error simplifying jargon: " + err.message);
            } finally {
                submitBtn.disabled = false;
                loader.style.display = 'none';
            }
        }

        document.getElementById('jargon-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                generateExplanation();
            }
        });

        function copyResult() {
            if (!rawMarkdown) return;
            navigator.clipboard.writeText(rawMarkdown).then(() => {
                const btn = document.querySelector('.copy-btn');
                btn.textContent = '✓ Copied!';
                setTimeout(() => btn.textContent = '📋 Copy Markdown', 2000);
            });
        }
    </script>
</body>
</html>
"""


class SimplifierHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/simplify":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                data = json.loads(body)
                term = data.get("term", "").strip()
                style = str(data.get("style", "1"))
                
                if not term:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Term is required"}).encode("utf-8"))
                    return

                s = get_simplifier()
                result = s.explain_with_tokens(term, style_key=style)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "term": term,
                    "style": style,
                    "explanation": result["explanation"],
                    "input_tokens": result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                    "total_tokens": result["total_tokens"],
                    "word_count": result["word_count"],
                    "tokens_per_word": result["tokens_per_word"],
                    "process_time": result["process_time"]
                }).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def start_server(port: int = 8080):
    server = HTTPServer(("0.0.0.0", port), SimplifierHandler)
    print(f"==================================================")
    print(f"🚀 Jargon Simplifier Web UI running at:")
    print(f"   http://localhost:{port}")
    print(f"==================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    start_server(port)
