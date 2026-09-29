import os
import re
import uuid
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

# ============================================================
# ResolveAI — Persistent-Memory Customer Complaint Agent
# ============================================================

load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "resolveai_customer_demo")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
HINDSIGHT_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")

st.set_page_config(
    page_title="ResolveAI | Persistent-Memory Support",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# GLOBAL STYLING
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --ink: #172554;
        --muted: #64748b;
        --line: #dbe4f0;
        --surface: rgba(255,255,255,.88);
        --primary: #4f46e5;
        --primary-2: #7c3aed;
        --success: #059669;
        --soft: #f5f7ff;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 4%, rgba(99,102,241,.14), transparent 28%),
            radial-gradient(circle at 92% 8%, rgba(14,165,233,.12), transparent 25%),
            linear-gradient(180deg, #f8fbff 0%, #eef3ff 100%);
    }

    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    header[data-testid="stHeader"] { background: transparent; }

    h1, h2, h3 {
        color: var(--ink) !important;
        letter-spacing: -.035em;
    }

    h1 { font-size: 3.15rem !important; font-weight: 850 !important; }
    h2 { font-size: 1.65rem !important; font-weight: 800 !important; }
    h3 { font-size: 1.12rem !important; font-weight: 750 !important; }

    .hero {
        padding: 30px 34px;
        border: 1px solid rgba(99,102,241,.15);
        border-radius: 26px;
        background: linear-gradient(135deg, rgba(255,255,255,.96), rgba(245,247,255,.86));
        box-shadow: 0 18px 55px rgba(30,41,59,.09);
        margin-bottom: 22px;
    }

    .brand-row { display:flex; align-items:center; gap:14px; }
    .brand-icon {
        width:58px; height:58px; display:flex; align-items:center; justify-content:center;
        border-radius:18px;
        background: linear-gradient(135deg, #eef2ff, #f5f3ff);
        font-size:31px;
        box-shadow: inset 0 0 0 1px rgba(99,102,241,.12);
    }
    .brand-title { font-size:38px; font-weight:850; color:#172554; line-height:1; }
    .brand-sub { margin-top:8px; color:#64748b; font-size:15px; }

    .pill {
        display:inline-flex; align-items:center; gap:7px;
        padding:7px 12px; border-radius:999px;
        font-size:12px; font-weight:750;
        margin:12px 8px 0 0;
        border:1px solid rgba(99,102,241,.15);
        background:#fff;
        color:#334155;
    }
    .pill-green { color:#047857; background:#ecfdf5; border-color:#a7f3d0; }
    .pill-purple { color:#5b21b6; background:#f5f3ff; border-color:#ddd6fe; }

    .card {
        background: var(--surface);
        border:1px solid var(--line);
        border-radius:20px;
        padding:20px 21px;
        box-shadow: 0 10px 32px rgba(15,23,42,.055);
        height:100%;
    }
    .card-title { color:#475569; font-size:12px; font-weight:750; text-transform:uppercase; letter-spacing:.09em; }
    .card-value { color:#172554; font-size:27px; font-weight:850; margin-top:5px; }
    .card-note { color:#64748b; font-size:12px; margin-top:5px; }

    .section-label {
        color:#4f46e5; font-size:12px; font-weight:850;
        text-transform:uppercase; letter-spacing:.12em; margin-bottom:5px;
    }

    .memory-box {
        border:1px solid #c7d2fe;
        background:linear-gradient(135deg,#eef2ff,#f8f7ff);
        border-radius:18px;
        padding:17px 19px;
        margin:9px 0;
    }
    .memory-kicker { color:#6366f1; font-size:11px; font-weight:850; text-transform:uppercase; letter-spacing:.1em; }
    .memory-text { color:#1e293b; font-size:14px; line-height:1.55; margin-top:5px; }

    .resolution-box {
        border:1px solid #a7f3d0;
        background:linear-gradient(135deg,#ecfdf5,#f4fffb);
        border-radius:20px;
        padding:22px 24px;
        color:#064e3b;
        line-height:1.68;
        box-shadow:0 10px 28px rgba(5,150,105,.07);
    }

    .journey {
        border:1px solid var(--line);
        border-radius:18px;
        padding:18px;
        background:rgba(255,255,255,.72);
        min-height:145px;
    }
    .journey-num {
        width:32px; height:32px; border-radius:10px;
        display:flex; align-items:center; justify-content:center;
        background:#eef2ff; color:#4f46e5; font-weight:850;
        margin-bottom:12px;
    }
    .journey-title { color:#172554; font-weight:800; font-size:16px; }
    .journey-text { color:#64748b; font-size:13px; line-height:1.55; margin-top:7px; }

    .empty-memory {
        border:1px dashed #cbd5e1;
        border-radius:18px;
        padding:22px;
        color:#64748b;
        background:rgba(255,255,255,.55);
    }

    textarea {
        border-radius:16px !important;
        border:1px solid #cbd5e1 !important;
        background:rgba(255,255,255,.88) !important;
        font-size:15px !important;
    }
    textarea:focus {
        border:2px solid #6366f1 !important;
        box-shadow:0 0 0 4px rgba(99,102,241,.10) !important;
    }

    .stTextInput input {
        border-radius:13px !important;
        background:rgba(255,255,255,.9) !important;
    }

    .stButton > button {
        border-radius:13px !important;
        min-height:3rem;
        font-weight:800 !important;
        border:1px solid #dbe4f0 !important;
        transition:all .18s ease;
    }
    .stButton > button:hover {
        transform:translateY(-1px);
        box-shadow:0 10px 22px rgba(15,23,42,.10);
    }

    [data-testid="stMetric"] {
        border:1px solid var(--line);
        border-radius:18px;
        background:rgba(255,255,255,.82);
        box-shadow:0 10px 30px rgba(15,23,42,.05);
        padding:17px;
    }

    [data-testid="stExpander"] {
        border:1px solid var(--line) !important;
        border-radius:16px !important;
        background:rgba(255,255,255,.65) !important;
    }

    [data-testid="stAlert"] { border-radius:16px !important; }

    .footer {
        text-align:center;
        color:#94a3b8;
        font-size:12px;
        padding:20px 0 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CLIENTS
# ============================================================

if not HINDSIGHT_API_KEY or not GROQ_API_KEY:
    st.error("API configuration is incomplete. Add HINDSIGHT_API_KEY and GROQ_API_KEY to .env.")
    st.stop()

hindsight = Hindsight(base_url=HINDSIGHT_URL, api_key=HINDSIGHT_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# ============================================================
# HELPERS
# ============================================================

def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("###", "").replace("**", "")
    return text.strip()


def memory_text(memory: Any) -> str:
    if hasattr(memory, "text"):
        return clean_text(memory.text)
    if isinstance(memory, dict):
        return clean_text(
            memory.get("text")
            or memory.get("content")
            or memory.get("memory")
            or ""
        )
    return ""


def ensure_bank() -> tuple[bool, str | None]:
    try:
        hindsight.create_bank(
            bank_id=BANK_ID,
            name="ResolveAI Customer Memory",
            mission=(
                "Remember customer support history, recurring complaints, "
                "previous troubleshooting steps, unresolved issues, "
                "preferences, and useful context for future support."
            ),
            disposition_empathy=7,
            disposition_literalism=6,
            disposition_skepticism=5,
        )
        return True, None
    except Exception as exc:
        message = str(exc)
        lowered = message.lower()
        if "already exists" in lowered or "409" in lowered or "conflict" in lowered:
            return True, None
        return False, message


def recall_customer_memory(customer_id: str, complaint: str) -> list[Any]:
    """Recall only memories belonging to this customer.

    IMPORTANT: hindsight.recall() is already a synchronous wrapper.
    Do not wrap it in run_until_complete/await.
    """
    queries = [
        (
            complaint,
            {"tags": [customer_id], "tags_match": "any_strict"},
        ),
        (
            f"Customer {customer_id}. Previous support history related to: {complaint}",
            {},
        ),
    ]

    for query, extra in queries:
        try:
            result = hindsight.recall(
                bank_id=BANK_ID,
                query=query,
                max_tokens=4000,
                budget="high",
                include_chunks=True,
                **extra,
            )

            # Hindsight 0.10.x returns RecallResponse.results.
            results = list(getattr(result, "results", []) or [])

            if extra:
                return results

            filtered = []
            for item in results:
                text = memory_text(item)
                tags = getattr(item, "tags", None) or []
                metadata = getattr(item, "metadata", None) or {}
                if (
                    customer_id.lower() in text.lower()
                    or customer_id in tags
                    or str(metadata.get("customer_id", "")).lower() == customer_id.lower()
                ):
                    filtered.append(item)
            return filtered
        except Exception:
            continue

    return []


def generate_memory_summary(customer_id: str, complaint: str, memories: list[Any]) -> list[str]:
    texts = [memory_text(item) for item in memories if memory_text(item)]
    if not texts:
        return []

    prompt = f"""
You are the memory summarization component of ResolveAI.

Customer ID: {customer_id}
Current complaint: {complaint}

Relevant previous memories:
{chr(10).join('- ' + t for t in texts[:12])}

Return up to 4 concise bullet points containing only useful prior context:
- recurring issues
- troubleshooting already attempted
- unresolved problems
- useful previous resolutions or preferences

Do not invent facts and do not mention the memory system.
"""

    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Summarize customer-support history accurately."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=450,
        )
        lines = response.choices[0].message.content.strip().splitlines()
        bullets = []
        for line in lines:
            line = re.sub(r"^[•\-*\d\.\)\s]+", "", line.strip())
            if len(line) > 5:
                bullets.append(line)
        return bullets[:4]
    except Exception:
        return texts[:4]


def generate_resolution(
    customer_id: str,
    complaint: str,
    memory_summary: list[str],
    memories: list[Any],
) -> str:
    summary = "\n".join(f"- {item}" for item in memory_summary) or "No relevant previous memory was found."
    raw = "\n".join(
        f"- {memory_text(item)}"
        for item in memories[:8]
        if memory_text(item)
    ) or "None"

    prompt = f"""
You are ResolveAI, a persistent-memory customer support agent.

Customer ID: {customer_id}
Current complaint: {complaint}

Relevant history:
{summary}

Detailed evidence:
{raw}

Create a professional, empathetic resolution.
Rules:
1. Address the customer by ID.
2. Use prior history only when it is actually relevant.
3. Never ask the customer to repeat troubleshooting already documented.
4. Clearly state the next useful action.
5. Do not invent policies, refunds, account details, or technical facts.
6. If escalation is appropriate, explain why.
7. Do not mention Hindsight, Groq, prompts, or implementation details.
"""

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a precise and empathetic customer support agent."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.35,
        max_tokens=900,
    )
    return response.choices[0].message.content.strip()


def save_interaction(customer_id: str, complaint: str, resolution: str) -> tuple[bool, str | None, str | None]:
    """Persist the interaction in Hindsight.

    IMPORTANT: hindsight.retain() is already synchronous in hindsight-client 0.10.1.
    The previous code incorrectly passed its RetainResponse into run_until_complete(),
    causing: 'An asyncio.Future, a coroutine or an awaitable is required'.
    """
    try:
        summary_response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Extract concise, durable customer-support memory from the interaction.",
                },
                {
                    "role": "user",
                    "content": f"""
Customer ID: {customer_id}
Complaint: {complaint}
Resolution: {resolution}

Write a concise memory for future support. Include recurring issues,
important troubleshooting, unresolved items, and useful resolution context.
Do not invent facts.
""",
                },
            ],
            temperature=0.15,
            max_tokens=450,
        )
        memory_content = summary_response.choices[0].message.content.strip()
    except Exception:
        memory_content = (
            f"Customer ID: {customer_id}. Complaint: {complaint}. "
            f"ResolveAI resolution: {resolution}"
        )

    document_id = f"{customer_id}-{uuid.uuid4().hex[:12]}"

    try:
        result = hindsight.retain(
            bank_id=BANK_ID,
            content=memory_content,
            context="ResolveAI customer support interaction",
            document_id=document_id,
            metadata={
                "customer_id": customer_id,
                "type": "customer_support_memory",
            },
            tags=[customer_id],
            retain_async=False,
        )

        if not getattr(result, "success", False):
            return False, f"Hindsight returned success={getattr(result, 'success', None)}", memory_content

        return True, None, memory_content
    except Exception as exc:
        return False, str(exc), memory_content


def process_complaint(customer_id: str, complaint: str) -> dict[str, Any]:
    memories = recall_customer_memory(customer_id, complaint)
    summary = generate_memory_summary(customer_id, complaint, memories)
    resolution = generate_resolution(customer_id, complaint, summary, memories)
    saved, save_error, stored_memory = save_interaction(customer_id, complaint, resolution)
    return {
        "memories": memories,
        "summary": summary,
        "resolution": resolution,
        "saved": saved,
        "save_error": save_error,
        "stored_memory": stored_memory,
    }

# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "processed": False,
    "customer_id": "CUST001",
    "complaint": "",
    "clear_form": False,
    "memories": [],
    "memory_summary": [],
    "resolution": "",
    "save_status": None,
    "stored_memory": "",
    "bank_ready": False,
    "bank_error": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# BANK HEALTH
# ============================================================

if not st.session_state.bank_ready:
    ready, error = ensure_bank()
    st.session_state.bank_ready = ready
    st.session_state.bank_error = error

# ============================================================
# HERO
# ============================================================

st.markdown(
    f"""
    <div class="hero">
      <div class="brand-row">
        <div class="brand-icon">🧠</div>
        <div>
          <div class="brand-title">ResolveAI</div>
          <div class="brand-sub">Persistent-memory customer complaint agent</div>
        </div>
      </div>
      <div style="margin-top:18px;color:#475569;font-size:15px;line-height:1.6;max-width:820px;">
        ResolveAI remembers relevant customer history, reasons over the current complaint,
        and turns each interaction into durable context for better future support.
      </div>
      <span class="pill pill-green">● Hindsight Memory {'Connected' if st.session_state.bank_ready else 'Needs attention'}</span>
      <span class="pill pill-purple">✦ Groq Reasoning</span>
      <span class="pill">↻ Persistent Customer Context</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.bank_error:
    st.error(f"Hindsight bank could not be initialized: {st.session_state.bank_error}")
    st.stop()

# ============================================================
# TOP METRICS
# ============================================================

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(
        '<div class="card"><div class="card-title">Customer</div>'
        f'<div class="card-value">{st.session_state.customer_id or "—"}</div>'
        '<div class="card-note">Persistent identity used for memory retrieval</div></div>',
        unsafe_allow_html=True,
    )
with m2:
    prior_count = len(st.session_state.memories) if st.session_state.processed else 0
    st.markdown(
        '<div class="card"><div class="card-title">Relevant prior memories</div>'
        f'<div class="card-value">{prior_count}</div>'
        '<div class="card-note">Retrieved before the current response</div></div>',
        unsafe_allow_html=True,
    )
with m3:
    saved_label = "Saved to Hindsight" if st.session_state.save_status and st.session_state.save_status[0] else "Awaiting interaction"
    st.markdown(
        '<div class="card"><div class="card-title">Memory state</div>'
        f'<div class="card-value" style="font-size:22px">{saved_label}</div>'
        '<div class="card-note">The current interaction becomes future context</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ============================================================
# SUPPORT WORKSPACE
# ============================================================

if st.session_state.clear_form:
    st.session_state.customer_input = st.session_state.customer_id
    st.session_state.complaint_input = ""
    st.session_state.clear_form = False

st.markdown('<div class="section-label">LIVE INVESTIGATION</div>', unsafe_allow_html=True)
st.header("Resolve a customer complaint")
st.caption("Run the same customer twice to demonstrate persistent memory: the second interaction should retrieve the first interaction as prior context.")

left, right = st.columns([1, 1.8], gap="large")

with left:
    customer_id = st.text_input(
        "Customer ID",
        value=st.session_state.customer_id,
        key="customer_input",
        placeholder="CUST001",
    )
    st.markdown(
        """
        <div class="card" style="margin-top:14px;">
          <div class="card-title">Demo scenario</div>
          <div style="font-size:14px;color:#334155;line-height:1.6;margin-top:8px;">
            <b>Interaction 1:</b> report a delivery problem.<br>
            <b>Interaction 2:</b> report the same problem again.<br>
            <span style="color:#64748b;">ResolveAI should recognize the returning customer and use the earlier context.</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    complaint = st.text_area(
        "Customer complaint",
        value=st.session_state.complaint if st.session_state.processed else "",
        height=190,
        key="complaint_input",
        placeholder="Example: My order is delayed again. Last time I had the same delivery issue with this courier.",
        label_visibility="visible",
    )

b1, b2, _ = st.columns([1, 1, 1.2])
with b1:
    process_clicked = st.button("✨ Resolve Complaint", type="primary", use_container_width=True)
with b2:
    clear_clicked = st.button("↻ New Complaint", use_container_width=True)

if clear_clicked:
    st.session_state.processed = False
    st.session_state.complaint = ""
    st.session_state.memories = []
    st.session_state.memory_summary = []
    st.session_state.resolution = ""
    st.session_state.save_status = None
    st.session_state.stored_memory = ""
    st.session_state.clear_form = True
    st.rerun()

if process_clicked:
    cid = customer_id.strip()
    text = complaint.strip()

    if not cid:
        st.warning("Enter a Customer ID first.")
    elif not text:
        st.warning("Enter the customer's complaint first.")
    else:
        with st.status("ResolveAI is investigating…", expanded=True) as status:
            st.write("🧠 Recalling relevant customer history…")
            try:
                result = process_complaint(cid, text)
            except Exception as exc:
                st.session_state.processed = False
                status.update(label="Investigation failed", state="error")
                st.error(f"Could not complete the investigation: {exc}")
                st.stop()

            st.write("🔎 Reasoning over current complaint + prior context…")
            st.write("💾 Persisting this interaction to Hindsight…")
            status.update(label="Investigation complete", state="complete")

        st.session_state.processed = True
        st.session_state.customer_id = cid
        st.session_state.complaint = text
        st.session_state.memories = result["memories"]
        st.session_state.memory_summary = result["summary"]
        st.session_state.resolution = result["resolution"]
        st.session_state.save_status = (result["saved"], result["save_error"])
        st.session_state.stored_memory = result["stored_memory"]
        st.rerun()

# ============================================================
# RESULTS
# ============================================================

if st.session_state.processed:
    st.divider()

    r1, r2 = st.columns([1, 1.35], gap="large")

    with r1:
        st.markdown('<div class="section-label">REMEMBER</div>', unsafe_allow_html=True)
        st.header("What ResolveAI remembers")

        if st.session_state.memory_summary:
            for item in st.session_state.memory_summary:
                st.markdown(
                    f'<div class="memory-box"><div class="memory-kicker">Relevant customer memory</div>'
                    f'<div class="memory-text">{item}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="empty-memory"><b>No relevant prior memory.</b><br>'
                'This is expected for a customer’s first interaction. The interaction has now been saved for future support.</div>',
                unsafe_allow_html=True,
            )

        with st.expander("View raw Hindsight results"):
            if st.session_state.memories:
                for idx, item in enumerate(st.session_state.memories, 1):
                    st.markdown(f"**Memory {idx}**")
                    st.write(memory_text(item))
            else:
                st.write("No prior Hindsight results were retrieved for this complaint.")

    with r2:
        st.markdown('<div class="section-label">RESOLVE</div>', unsafe_allow_html=True)
        st.header("Personalized Resolution")
        st.markdown(
            f'<div class="resolution-box">{st.session_state.resolution.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )

        st.write("")
        saved, save_error = st.session_state.save_status or (False, None)
        if saved:
            st.success("✓ Interaction successfully stored in Hindsight persistent memory.")
        else:
            st.error("✕ Response generated, but Hindsight did not confirm the memory save.")
            if save_error:
                with st.expander("Technical error details"):
                    st.code(save_error)

        with st.expander("What was stored for future support"):
            st.write(st.session_state.stored_memory or "No stored memory content available.")

    st.divider()
    st.markdown('<div class="section-label">THE MEMORY LOOP</div>', unsafe_allow_html=True)
    st.header("Remember → Reason → Learn")

    j1, j2, j3 = st.columns(3)
    with j1:
        st.markdown(
            '<div class="journey"><div class="journey-num">1</div>'
            '<div class="journey-title">Remember</div>'
            '<div class="journey-text">Retrieve relevant history for this customer before generating the response.</div></div>',
            unsafe_allow_html=True,
        )
    with j2:
        st.markdown(
            '<div class="journey"><div class="journey-num">2</div>'
            '<div class="journey-title">Reason</div>'
            '<div class="journey-text">Combine the current complaint with the retrieved context to avoid repetitive support.</div></div>',
            unsafe_allow_html=True,
        )
    with j3:
        st.markdown(
            '<div class="journey"><div class="journey-num">3</div>'
            '<div class="journey-title">Learn</div>'
            '<div class="journey-text">Store the new interaction so a later complaint can use it as persistent customer context.</div></div>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="footer">ResolveAI • Persistent customer memory • Evidence-aware personalized support</div>',
    unsafe_allow_html=True,
)
