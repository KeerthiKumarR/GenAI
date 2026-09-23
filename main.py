import os
import time
import warnings
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Suppress harmless SDK notices
warnings.filterwarnings("ignore")

# Load environment variables
try:
    load_dotenv(override=True)
except Exception:
    pass

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]

app = FastAPI(
    title="FastAPI Jargon Translator & Token Tracking Server",
    description="FastAPI server providing health check, word count, response timing & token tracking middleware, and async LangChain Jargon Translation.",
    version="1.0.0",
)

# Global response & token metrics tracker
response_metrics = {
    "total_responses": 0,
    "total_tokens_spent": 0,
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "status_codes": {}
}


# ==========================================
# 1. RESPONSE & TOKEN LOGGING MIDDLEWARE
# ==========================================
@app.middleware("http")
async def calculate_response_and_tokens_middleware(request: Request, call_next):
    """
    Middleware that:
    1. Measures the exact time taken to process the response.
    2. Initializes and captures Request & Response token counts (input, output, total).
    3. Logs token usage for both request and response in real-time.
    4. Attaches timing and token headers (X-Process-Time, X-Input-Tokens, X-Output-Tokens, X-Total-Tokens).
    5. Aggregates cumulative token and response metrics.
    """
    # 1. Initialize token state on the request
    request.state.token_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0
    }

    start_time = time.perf_counter()

    # 2. Process request through endpoint handler
    response = await call_next(request)

    # 3. Calculate processing time
    process_time = time.perf_counter() - start_time
    formatted_time = f"{process_time * 1000:.2f}ms"

    # 4. Retrieve token counts spent during this request
    token_usage = getattr(request.state, "token_usage", {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
    input_tokens = token_usage.get("input_tokens", 0)
    output_tokens = token_usage.get("output_tokens", 0)
    total_tokens = token_usage.get("total_tokens", 0)

    # If it's a non-LLM endpoint (e.g. /word-count or /health), calculate approximate token counts based on payload
    if total_tokens == 0:
        # Approximate: ~1 token per 4 chars of text
        input_tokens = max(1, len(str(request.url.path)) // 4)
        output_tokens = max(1, int(response.headers.get("content-length", 40)) // 4)
        total_tokens = input_tokens + output_tokens

    # 5. Calculate tokens per word ratio
    word_count = token_usage.get("word_count", max(1, output_tokens // 2))
    tokens_per_word = token_usage.get("tokens_per_word", round(output_tokens / max(1, word_count), 2))

    # 6. Attach headers to response
    response.headers["X-Process-Time"] = formatted_time
    response.headers["X-Input-Tokens"] = str(input_tokens)
    response.headers["X-Output-Tokens"] = str(output_tokens)
    response.headers["X-Total-Tokens"] = str(total_tokens)
    response.headers["X-Tokens-Per-Word"] = str(tokens_per_word)

    # 7. Update global metrics
    response_metrics["total_responses"] += 1
    response_metrics["total_tokens_spent"] += total_tokens
    response_metrics["total_input_tokens"] += input_tokens
    response_metrics["total_output_tokens"] += output_tokens
    status = response.status_code
    response_metrics["status_codes"][status] = response_metrics["status_codes"].get(status, 0) + 1

    # 8. Comprehensive logging for both Request & Response
    print(f"\n========================================================")
    print(f"📡 [{request.method}] {request.url.path} -> HTTP {status}")
    print(f"⏱️  Response Time      : {formatted_time}")
    print(f"📥 Request Tokens      : {input_tokens} tokens")
    print(f"📤 Response Tokens     : {output_tokens} tokens")
    print(f"📊 Total Tokens Spent  : {total_tokens} tokens")
    print(f"🎯 Tokens/Word Ratio   : {tokens_per_word} tokens/word")
    print(f"📈 Lifetime Tokens     : {response_metrics['total_tokens_spent']} tokens")
    print(f"========================================================\n")

    return response


# ==========================================
# 2. PYDANTIC DATA MODELS
# ==========================================
class TextRequest(BaseModel):
    text: str = Field(..., example="Hi, my name is Aditya", description="The text string to count words from.")


class WordCountResponse(BaseModel):
    word_count: int = Field(..., description="Total number of words in the provided text.")
    text: str = Field(..., description="Original input text.")


class HealthResponse(BaseModel):
    status: str = Field("ok", description="Status of the server.")
    message: str = Field("Server is running fine", description="Detailed health message.")


class TranslateRequest(BaseModel):
    jargon: str = Field(..., example="Kubernetes Pod Autoscaler", description="The jargon or complex technical concept to translate.")


class TokenDetails(BaseModel):
    input_tokens: int = Field(..., description="Tokens consumed by the prompt/input.")
    output_tokens: int = Field(..., description="Tokens generated in the response.")
    total_tokens: int = Field(..., description="Total tokens spent for this request.")
    word_count: int = Field(..., description="Total words generated in the explanation.")
    tokens_per_word: float = Field(..., description="Ratio of completion tokens per word.")


class TranslateResponse(BaseModel):
    jargon: str = Field(..., description="The original input jargon.")
    translated: str = Field(..., description="The layman translation generated by Gemini.")
    tokens_spent: Optional[TokenDetails] = Field(None, description="Detailed breakdown of tokens spent.")


# ==========================================
# 3. LANGCHAIN JARGON TRANSLATOR SETUP (DAY 3)
# ==========================================
JARGON_SYSTEM_PROMPT = """You are an expert communicator whose superpower is translating ultra-complex technical, medical, legal, financial, and scientific jargon into crystal-clear layman's terms that anyone can instantly grasp.

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
(A punchy one-sentence summary to remember forever)"""

translate_prompt = ChatPromptTemplate.from_messages([
    ("system", JARGON_SYSTEM_PROMPT),
    ("human", "Please explain this jargon / complex concept in layman terms:\n\n**{jargon}**")
])

# Initialize ChatGoogleGenerativeAI with gemini-3.8-flash (or fallback)
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        temperature=0.4
    )
except Exception:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.4
    )

output_parser = StrOutputParser()


# ==========================================
# 4. ENDPOINTS
# ==========================================
@app.get("/", response_model=HealthResponse, tags=["Health Check"])
@app.get("/health", response_model=HealthResponse, tags=["Health Check"])
@app.get("/status", response_model=HealthResponse, tags=["Health Check"])
def check_status():
    """Check whether the server is running fine or not."""
    return HealthResponse(
        status="ok",
        message="Server is running fine"
    )


@app.post("/word-count", response_model=WordCountResponse, tags=["Word Counter"])
def count_words(payload: TextRequest):
    """Accepts a text string in the request body and returns the word count."""
    words = payload.text.split()
    return WordCountResponse(
        word_count=len(words),
        text=payload.text
    )


@app.post("/translate", response_model=TranslateResponse, tags=["Jargon Translator"])
async def translate_jargon(payload: TranslateRequest, request: Request):
    """
    Translates technical jargon into plain layman terms using LangChain and Gemini.
    Captures exact prompt & completion tokens spent, word count, and tokens-per-word ratio.
    """
    try:
        # Format the prompt messages
        formatted_messages = await translate_prompt.ainvoke({"jargon": payload.jargon})

        # VERY IMPORTANT: Execute using the asynchronous .ainvoke() method and await the result
        ai_message = await llm.ainvoke(formatted_messages)
        translated_text = output_parser.invoke(ai_message)

        # Extract exact token usage metadata from Gemini
        usage = getattr(ai_message, "usage_metadata", {}) or {}
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

        word_count = len(translated_text.split())
        tokens_per_word = round(output_tokens / max(1, word_count), 2)

        # Pass token counts to the middleware via request.state
        request.state.token_usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "word_count": word_count,
            "tokens_per_word": tokens_per_word
        }

        return TranslateResponse(
            jargon=payload.jargon,
            translated=translated_text,
            tokens_spent=TokenDetails(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                word_count=word_count,
                tokens_per_word=tokens_per_word
            )
        )
    except Exception as e:
        # Fallback if specific flash model variant needed
        try:
            fallback_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4)
            formatted_messages = await translate_prompt.ainvoke({"jargon": payload.jargon})
            ai_message = await fallback_llm.ainvoke(formatted_messages)
            translated_text = output_parser.invoke(ai_message)

            usage = getattr(ai_message, "usage_metadata", {}) or {}
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

            word_count = len(translated_text.split())
            tokens_per_word = round(output_tokens / max(1, word_count), 2)

            request.state.token_usage = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "word_count": word_count,
                "tokens_per_word": tokens_per_word
            }

            return TranslateResponse(
                jargon=payload.jargon,
                translated=translated_text,
                tokens_spent=TokenDetails(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    word_count=word_count,
                    tokens_per_word=tokens_per_word
                )
            )
        except Exception as inner_e:
            raise HTTPException(status_code=500, detail=f"LLM Translation failed: {str(inner_e)}")


@app.get("/metrics", tags=["Metrics"])
def get_metrics():
    """Returns total responses served and lifetime token statistics tracked by the middleware."""
    return {
        "metrics": response_metrics
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
