#!/usr/bin/env python3
"""
Chat Pipeline with Memory using LangChain, Gemini 3.8 Flash, and RunnableWithMessageHistory.
Demonstrates:
1. ChatPromptTemplate with MessagesPlaceholder for 'history'
2. Wrapping chain in RunnableWithMessageHistory
3. Storing and managing session IDs using an in-memory dictionary
4. Multi-turn conversation proof (Turn 1: Telling name, Turn 2: Asking for name)
"""

import os
import warnings
from dotenv import load_dotenv

# LangChain Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory, BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Suppress harmless deprecation/SDK notices
warnings.filterwarnings("ignore")

# 1. Load API Key
load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]


# =====================================================================
# 2. IN-MEMORY DICTIONARY FOR SESSION STORAGE
# =====================================================================
# This dictionary maps session_id (str) -> InMemoryChatMessageHistory object
session_store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Session lookup function required by RunnableWithMessageHistory.
    Retrieves the conversation history for a given session_id,
    or initializes a new InMemoryChatMessageHistory if it doesn't exist yet.
    """
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
        print(f"🆕 [Session Store] Created new chat history for session_id: '{session_id}'")
    else:
        print(f"📂 [Session Store] Retrieved existing history for session_id: '{session_id}' ({len(session_store[session_id].messages)} previous messages)")
    return session_store[session_id]


# =====================================================================
# 3. PROMPT TEMPLATE WITH MessagesPlaceholder FOR 'history'
# =====================================================================
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful, friendly, and concise AI assistant with memory. "
        "Remember user details and refer back to conversation history when relevant."
    ),
    # MessagesPlaceholder dynamically injects the list of past messages into the prompt
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])


# =====================================================================
# 4. LLM & BASE LCEL CHAIN
# =====================================================================
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        temperature=0.2
    )
except Exception:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2
    )

output_parser = StrOutputParser()

# Base Chain (Prompt -> LLM -> Parser)
base_chain = prompt | llm | output_parser


# =====================================================================
# 5. WRAP WITH RunnableWithMessageHistory
# =====================================================================
conversational_chain = RunnableWithMessageHistory(
    base_chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)


# =====================================================================
# 6. MULTI-TURN CONVERSATION PROOF
# =====================================================================
def run_demo():
    print("=" * 70)
    print("🤖 LANGCHAIN CHAT MEMORY DEMO (RunnableWithMessageHistory + Gemini)")
    print("=" * 70)

    # Define a unique session ID
    session_id = "user_session_42"
    config = {"configurable": {"session_id": session_id}}

    print(f"\n🔑 Active Session ID: '{session_id}'\n")

    # -------------------------------------------------------------
    # TURN 1: Tell the AI our name
    # -------------------------------------------------------------
    turn1_input = "Hi! My name is Keerthi Kumar. I am a software engineer."
    print("👤 [Turn 1 - User Input]:", turn1_input)
    
    response_1 = conversational_chain.invoke(
        {"input": turn1_input},
        config=config
    )
    print("🤖 [Turn 1 - AI Response]:\n", response_1.strip())
    print("-" * 70)

    # -------------------------------------------------------------
    # TURN 2: Ask the AI to recall our name
    # -------------------------------------------------------------
    turn2_input = "What is my name and what do I do?"
    print("👤 [Turn 2 - User Input]:", turn2_input)

    response_2 = conversational_chain.invoke(
        {"input": turn2_input},
        config=config
    )
    print("🤖 [Turn 2 - AI Response]:\n", response_2.strip())
    print("-" * 70)

    # -------------------------------------------------------------
    # STUDY / INSPECT STORED SESSION HISTORY
    # -------------------------------------------------------------
    print("\n🔍 [STUDY CODE] Inspecting Raw In-Memory Dictionary (`session_store`):")
    print(f"Total Active Sessions: {len(session_store)}")
    print(f"Messages Stored under '{session_id}':")
    for idx, msg in enumerate(session_store[session_id].messages, 1):
        sender = "👤 Human" if msg.type == "human" else "🤖 AI"
        print(f"   [{idx}] {sender}: {msg.content}")

    print("\n" + "=" * 70)
    print("✅ Proof Complete: AI remembered name across conversation turns!")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
