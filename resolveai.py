"""Small command-line smoke test for ResolveAI + Hindsight."""

import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)

bank_id = os.getenv("HINDSIGHT_BANK_ID", "resolveai_customer_demo")

try:
    client.create_bank(
        bank_id=bank_id,
        name="ResolveAI Customer Memory",
        mission="Remember customer support history and recurring issues.",
    )
except Exception as exc:
    if not any(token in str(exc).lower() for token in ("already exists", "409", "conflict")):
        raise

customer_id = input("Customer ID: ").strip() or "CUST001"
complaint = input("Customer complaint: ").strip()

previous = client.recall(
    bank_id=bank_id,
    query=complaint,
    tags=[customer_id],
    tags_match="any_strict",
    max_tokens=2500,
)

print("\nPrevious memories:")
for item in previous.results:
    print(f"- {item.text}")

result = client.retain(
    bank_id=bank_id,
    content=f"Customer ID: {customer_id}\nComplaint: {complaint}",
    context="ResolveAI customer support interaction",
    tags=[customer_id],
    metadata={"customer_id": customer_id, "type": "customer_support_memory"},
)

print(f"\nSaved successfully: {result.success}")
