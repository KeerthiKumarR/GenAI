#!/usr/bin/env python3
"""
JargonSimplifier - AI-powered Layman Language Explainer
Built with LangChain, Google Gemini, and Python-Dotenv.
"""

import sys
import os
import argparse
import warnings
from pathlib import Path

# Suppress harmless SDK deprecation notices for clean terminal UI
warnings.filterwarnings("ignore")

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv(dotenv_path=CURRENT_DIR / ".env")

# Verify API key presence
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[ERROR] No GOOGLE_API_KEY or GEMINI_API_KEY found in environment or .env file.")
    print("Please check your .env file.")
    sys.exit(1)

# Keep environment clean with single key
os.environ["GOOGLE_API_KEY"] = api_key
if "GEMINI_API_KEY" in os.environ:
    del os.environ["GEMINI_API_KEY"]

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.theme import Theme
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# Setup rich console
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "bold green",
    "title": "bold magenta",
    "highlight": "bold cyan"
})
console = Console(theme=custom_theme) if RICH_AVAILABLE else None


# Prompt Templates for different simplification styles
STYLES = {
    "1": {
        "name": "Standard Layman Breakdown",
        "description": "Clear, structured explanation with relatable context and key takeaways",
        "system": """You are an expert communicator whose superpower is translating ultra-complex technical, medical, legal, financial, and scientific jargon into crystal-clear layman's terms that anyone can instantly grasp.

When given a piece of jargon, a term, or a complex concept, provide your explanation in the following markdown structure:

### 💡 What is it in plain English?
(A clear, simple 1-2 sentence definition without any buzzwords)

### 🧩 The Real-World Analogy
(A vivid, memorable everyday analogy — e.g. comparing it to cooking, traffic, smartphones, pizza, or house building)

### 🔍 How It Actually Works (Step-by-Step)
(Break down the moving parts into 2-4 simple, intuitive bullet points)

### 🌍 Why Does It Matter?
(Why a regular person or industry cares about this in real life)

### ⚡ Quick Cheat Sheet (The 10-Second Takeaway)
(A punchy one-sentence summary to remember forever)
"""
    },
    "2": {
        "name": "ELI5 (Explain Like I'm 5)",
        "description": "Ultra-simplified storytelling for complete beginners or kids",
        "system": """You are a warm, imaginative teacher talking to a curious 5-year-old.
Explain the complex jargon using simple words, fun characters or toys, and a short imaginative story.
Keep sentences short, lively, and completely devoid of industry vocabulary."""
    },
    "3": {
        "name": "The Analogy Master",
        "description": "Explains purely through brilliant, intuitive everyday analogies",
        "system": """You are the 'Analogy Master'. Your goal is to explain complex jargon using 2 distinct, highly relatable real-world analogies (e.g., one from everyday household life and one from sports or food).
Show how the components of the analogy map 1:1 to the complex concept."""
    },
    "4": {
        "name": "Executive / Business 1-Liner",
        "description": "Crisp, punchy, high-impact bottom-line summary for decision makers",
        "system": """You are an executive advisor. Explain this complex jargon in concise, high-impact plain terms:
1. **The Essence**: What it is in 1 sentence without buzzwords.
2. **Business/Practical Impact**: Why it matters.
3. **What It Is NOT**: Common misconception cleared in 1 line."""
    }
}


class JargonSimplifier:
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.4):
        """Initialize the LangChain Gemini LLM chain."""
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key,
            convert_system_message_to_human=True
        )
        self.parser = StrOutputParser()

    def explain(self, term: str, style_key: str = "1", audience_context: str = "") -> str:
        """Generate a layman explanation for the given term."""
        res = self.explain_with_tokens(term, style_key, audience_context)
        return res["explanation"]

    def explain_with_tokens(self, term: str, style_key: str = "1", audience_context: str = "") -> dict:
        """Generate a layman explanation and return token usage and execution time."""
        import time
        t0 = time.perf_counter()
        style = STYLES.get(style_key, STYLES["1"])
        
        system_prompt = style["system"]
        if audience_context:
            system_prompt += f"\n\nTarget audience/context: {audience_context}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Please explain this jargon / complex concept in layman terms:\n\n**{term}**")
        ])

        # Format messages and invoke LLM
        formatted = prompt.invoke({"term": term})
        ai_message = self.llm.invoke(formatted)
        explanation = self.parser.invoke(ai_message)
        t1 = time.perf_counter()

        usage = getattr(ai_message, "usage_metadata", {}) or {}
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

        word_count = len(explanation.split())
        tokens_per_word = round(output_tokens / max(1, word_count), 2)

        return {
            "explanation": explanation,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "word_count": word_count,
            "tokens_per_word": tokens_per_word,
            "process_time": f"{(t1 - t0) * 1000:.2f}ms"
        }


def print_banner():
    if not RICH_AVAILABLE:
        print("=" * 60)
        print("    JARGON SIMPLIFIER - Layman Language Translator")
        print("    Powered by LangChain & Google Gemini")
        print("=" * 60)
        return

    console.print(Panel.fit(
        "[bold cyan]🧠 JARGON SIMPLIFIER[/bold cyan] [bold white]| Layman Language AI Translator[/bold white]\n"
        "[dim]Powered by [green]LangChain[/green] & [yellow]Google Gemini[/yellow] with [magenta]python-dotenv[/magenta][/dim]",
        border_style="cyan"
    ))


def display_styles_menu():
    if not RICH_AVAILABLE:
        print("\nSelect Explanation Style:")
        for k, v in STYLES.items():
            print(f"  [{k}] {v['name']} - {v['description']}")
        return

    table = Table(title="Available Explanation Styles", show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan", width=8, justify="center")
    table.add_column("Style", style="bold white", width=26)
    table.add_column("Description", style="dim")

    for k, v in STYLES.items():
        table.add_row(f"[{k}]", v["name"], v["description"])

    console.print(table)


def interactive_mode(simplifier: JargonSimplifier):
    print_banner()
    if RICH_AVAILABLE:
        console.print("[green]✓[/green] Connected to Gemini AI via LangChain")
        console.print("Type your jargon term (or type [bold red]'exit'[/bold red] or [bold red]'q'[/bold red] to quit).\n")
    else:
        print("Connected to Gemini AI via LangChain.\nType 'exit' to quit.\n")

    current_style = "1"

    while True:
        try:
            if RICH_AVAILABLE:
                term = Prompt.ask("\n[bold cyan]Enter complex jargon / concept[/bold cyan] (or 'style' to change mode)")
            else:
                term = input("\nEnter complex jargon / concept (or 'style' to change mode): ")

            term = term.strip()
            if not term:
                continue

            if term.lower() in ["exit", "quit", "q"]:
                if RICH_AVAILABLE:
                    console.print("\n[bold yellow]Goodbye! Happy learning![/bold yellow] 👋\n")
                else:
                    print("Goodbye!")
                break

            if term.lower() == "style":
                display_styles_menu()
                choice = input("\nChoose a style (1-4) [default 1]: ").strip()
                if choice in STYLES:
                    current_style = choice
                    print(f"✓ Selected style: {STYLES[current_style]['name']}")
                else:
                    print("Invalid choice, keeping previous style.")
                continue

            # Generate explanation
            if RICH_AVAILABLE:
                with console.status(f"[bold green]Translating '{term}' into layman's terms with Gemini AI...[/bold green]"):
                    result = simplifier.explain(term, style_key=current_style)
                
                style_name = STYLES[current_style]["name"]
                console.print("\n")
                console.print(Panel(
                    Markdown(result),
                    title=f"[bold green]✨ Layman Explanation: {term} ({style_name})[/bold green]",
                    border_style="green",
                    padding=(1, 2)
                ))
            else:
                print(f"\n--- Layman Explanation: {term} ---")
                print(simplifier.explain(term, style_key=current_style))
                print("-" * 50)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[danger]Error generating explanation:[/danger] {e}")
            else:
                print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Explain complex jargon in layman's language using LangChain and Google Gemini."
    )
    parser.add_argument("term", nargs="?", help="The jargon term or concept to simplify (optional, starts interactive mode if omitted)")
    parser.add_argument("-s", "--style", choices=["1", "2", "3", "4"], default="1", help="Explanation style (1: Standard, 2: ELI5, 3: Analogy Master, 4: Executive)")
    parser.add_argument("-a", "--audience", default="", help="Specific audience context (e.g. 'high school student', 'marketing executive')")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Gemini model name (default: gemini-2.5-flash)")

    args = parser.parse_args()

    simplifier = JargonSimplifier(model_name=args.model)

    if args.term:
        # Single-shot command line mode
        try:
            result = simplifier.explain(args.term, style_key=args.style, audience_context=args.audience)
            if RICH_AVAILABLE:
                style_name = STYLES[args.style]["name"]
                console.print(Panel(
                    Markdown(result),
                    title=f"[bold green]✨ Layman Explanation: {args.term} ({style_name})[/bold green]",
                    border_style="green",
                    padding=(1, 2)
                ))
            else:
                print(result)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive mode
        interactive_mode(simplifier)


if __name__ == "__main__":
    main()
