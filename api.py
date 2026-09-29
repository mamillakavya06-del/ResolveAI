import os
import re
import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from groq import Groq
from hindsight_client import Hindsight


# ============================================================
# SETUP
# ============================================================

load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BANK_ID = "resolveai_customer_demo"
MODEL = "openai/gpt-oss-120b"


if not HINDSIGHT_API_KEY:
    raise RuntimeError("HINDSIGHT_API_KEY is missing from .env")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing from .env")


# ============================================================
# CLIENTS
# ============================================================

hindsight = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=HINDSIGHT_API_KEY
)

groq_client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(title="ResolveAI API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    customer_id: str
    message: str


# ============================================================
# ASYNC HELPER
# ============================================================

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


# ============================================================
# ENSURE HINDSIGHT BANK
# ============================================================

def ensure_bank():

    try:

        hindsight.create_bank(
            bank_id=BANK_ID,
            name="ResolveAI Customer Memory",
            mission=(
                "Remember customer support history, recurring complaints, "
                "previous troubleshooting steps, preferences, unresolved "
                "issues, and useful information that can improve future "
                "customer support interactions."
            ),
            disposition_empathy=7,
            disposition_literalism=6,
            disposition_skepticism=5
        )

        return True

    except Exception as e:

        error_text = str(e).lower()

        if (
            "already exists" in error_text
            or "409" in error_text
            or "conflict" in error_text
        ):
            return True

        return True


# ============================================================
# CLEAN MEMORY
# ============================================================

def clean_memory_text(text):

    if not text:
        return ""

    text = str(text)

    text = re.sub(r"\s+", " ", text)

    text = text.replace("###", "")
    text = text.replace("**", "")

    return text.strip()


# ============================================================
# EXTRACT MEMORY TEXT
# ============================================================

def extract_memory_text(memory):

    try:

        if hasattr(memory, "text"):
            return clean_memory_text(memory.text)

        if isinstance(memory, dict):

            return clean_memory_text(
                memory.get("text")
                or memory.get("content")
                or memory.get("memory")
                or ""
            )

    except Exception:
        pass

    return ""


# ============================================================
# RECALL CUSTOMER MEMORY
# ============================================================

def recall_customer_memory(customer_id, complaint):

    try:

        result = run_async(
            hindsight.recall(
                bank_id=BANK_ID,
                query=complaint,
                tags=[customer_id],
                tags_match="exact",
                max_tokens=3000,
                budget="high",
                include_chunks=True
            )
        )

        memories = getattr(result, "memories", None)

        if memories:
            return memories

    except Exception:
        pass


    # --------------------------------------------------------
    # FALLBACK SEARCH
    # --------------------------------------------------------

    try:

        result = run_async(
            hindsight.recall(
                bank_id=BANK_ID,
                query=f"""
Customer ID: {customer_id}

Current complaint:

{complaint}

Find memories related to this customer and this complaint.

Prioritize previous complaints, troubleshooting steps,
unresolved issues, customer preferences, and previous resolutions.
""",
                max_tokens=4000,
                budget="high",
                include_chunks=True
            )
        )

        memories = getattr(result, "memories", None)

        if not memories:
            return []

        customer_memories = []

        for memory in memories:

            text = extract_memory_text(memory)

            if customer_id.lower() in text.lower():
                customer_memories.append(memory)

        return customer_memories

    except Exception:
        return []


# ============================================================
# GENERATE MEMORY SUMMARY
# ============================================================

def generate_memory_summary(customer_id, complaint, memories):

    if not memories:
        return []

    memory_texts = []

    for memory in memories:

        text = extract_memory_text(memory)

        if text:
            memory_texts.append(text)

    if not memory_texts:
        return []

    combined_memories = "\n".join(
        f"- {text}"
        for text in memory_texts[:15]
    )

    prompt = f"""
You are the memory summarization component of ResolveAI.

Customer ID:
{customer_id}

Current complaint:
{complaint}

Previous customer memories:
{combined_memories}

Create a concise summary of what ResolveAI should remember
before responding to this customer.

Rules:
- Give exactly 4 bullet points maximum.
- Mention only useful information.
- Focus on recurring issues.
- Mention troubleshooting already attempted.
- Mention unresolved problems.
- Mention useful next steps if present.
- Do not invent information.
- Do not repeat the same point.
- Keep each bullet concise.
"""

    try:

        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You summarize customer-support memory "
                        "accurately and concisely."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=500
        )

        content = response.choices[0].message.content.strip()

        lines = content.splitlines()

        bullets = []

        for line in lines:

            line = line.strip()

            if not line:
                continue

            line = re.sub(
                r"^[•\-\*\d\.\)\s]+",
                "",
                line
            )

            if len(line) > 5:
                bullets.append(line)

        return bullets[:4]

    except Exception:

        return [
            clean_memory_text(text)
            for text in memory_texts[:4]
        ]


# ============================================================
# GENERATE PERSONALIZED RESOLUTION
# ============================================================

def generate_resolution(
    customer_id,
    complaint,
    memory_summary,
    memories
):

    summary_text = "\n".join(
        f"- {item}"
        for item in memory_summary
    )

    raw_memory_text = "\n".join(
        f"- {extract_memory_text(memory)}"
        for memory in memories[:10]
        if extract_memory_text(memory)
    )

    prompt = f"""
You are ResolveAI, a persistent-memory customer support agent.

Customer ID:
{customer_id}

Current complaint:
{complaint}

What ResolveAI remembers:
{summary_text}

Detailed relevant memory:
{raw_memory_text}

Write a personalized customer-support response.

Requirements:

1. Address the customer using their customer ID.
2. Acknowledge that this may be a recurring issue when memory supports it.
3. Do NOT ask the customer to repeat troubleshooting steps already completed.
4. Clearly explain the next useful diagnostic or resolution step.
5. Be professional, empathetic and concise.
6. If escalation is appropriate based on memory, explain it naturally.
7. Do not invent account details, policies, refunds or technical facts.
8. Use numbered steps only when useful.
9. Do not mention Hindsight, Groq, prompts, memory systems or implementation.
"""

    try:

        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional customer support agent "
                        "that uses customer history to avoid repetitive "
                        "support and provide personalized resolutions."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=900
        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        raise RuntimeError(
            f"Unable to generate personalized resolution: {e}"
        )


# ============================================================
# SAVE INTERACTION TO HINDSIGHT
# ============================================================

def save_interaction(customer_id, complaint, resolution):

    memory_content = f"""
Customer ID: {customer_id}

Customer complaint:
{complaint}

ResolveAI response:
{resolution}

This interaction belongs to the customer support history of {customer_id}.

Remember recurring issues, troubleshooting already attempted,
unresolved problems, preferences, and useful future support context.
"""

    try:

        summary_response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract useful persistent customer-support "
                        "memory from the interaction."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
Customer ID: {customer_id}

Complaint:
{complaint}

Resolution:
{resolution}

Create a concise persistent memory that will help a future
customer-support agent understand this customer's history.

Do not invent facts.
"""
                }
            ],
            temperature=0.2,
            max_tokens=400
        )

        memory_summary = (
            summary_response.choices[0].message.content.strip()
        )

    except Exception:

        memory_summary = memory_content


    try:

        run_async(
            hindsight.retain(
                bank_id=BANK_ID,
                content=memory_summary,
                context="ResolveAI customer support interaction",
                metadata={
                    "customer_id": customer_id,
                    "type": "customer_support_memory"
                },
                tags=[customer_id]
            )
        )

        return True, None

    except Exception as e:

        return False, str(e)


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "ResolveAI API"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "ResolveAI"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    customer_id = request.customer_id.strip()
    complaint = request.message.strip()

    if not customer_id:
        return {
            "success": False,
            "error": "Customer ID is required."
        }

    if not complaint:
        return {
            "success": False,
            "error": "Customer message is required."
        }


    # Make sure Hindsight bank exists
    ensure_bank()


    # 1. Recall previous customer history
    memories = recall_customer_memory(
        customer_id,
        complaint
    )


    # 2. Summarize relevant history
    memory_summary = generate_memory_summary(
        customer_id,
        complaint,
        memories
    )


    # 3. Generate personalized response
    resolution = generate_resolution(
        customer_id,
        complaint,
        memory_summary,
        memories
    )


    # 4. Save current interaction
    saved, save_error = save_interaction(
        customer_id,
        complaint,
        resolution
    )


    # 5. Prepare memory for frontend
    memory_text = []

    for memory in memories:

        text = extract_memory_text(memory)

        if text:
            memory_text.append(text)


    return {
        "success": True,
        "customer_id": customer_id,
        "response": resolution,
        "memory_summary": memory_summary,
        "memories": memory_text,
        "memory_count": len(memory_text),
        "saved": saved,
        "save_error": save_error
    }