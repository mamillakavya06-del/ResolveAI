# ResolveAI — Persistent-Memory Customer Complaint Agent

ResolveAI is a Streamlit customer-support agent that uses Groq for response generation and Hindsight for persistent customer memory.

## Run

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your own API keys.

```bash
streamlit run app.py
```

## Demonstrate persistent memory

1. Use `CUST001`.
2. Submit a first complaint, such as: `My order is delayed and the courier has not updated the tracking.`
3. Confirm **Interaction successfully stored in Hindsight persistent memory**.
4. Submit a second complaint with the same customer ID: `My order is delayed again with the same courier.`
5. ResolveAI should retrieve the first interaction as prior memory and use it in the personalized resolution.

## Important implementation detail

`hindsight-client` 0.10.x exposes synchronous convenience methods such as `retain()` and `recall()`. They already manage their own async execution. The app therefore calls them directly instead of passing their return values to `asyncio.run_until_complete()`.
