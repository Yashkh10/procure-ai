import json
import os

from dotenv import load_dotenv
from google import genai

from agent.prompts import SYSTEM_PROMPT
from agent.tools import (
    get_inventory,
    get_forecast,
    get_suppliers,
    get_open_purchase_orders,
    get_constraints
)


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def run_agent(db, sku, proposed_quantity):
    inventory = get_inventory(db, sku)
    forecast = get_forecast(db, sku)
    suppliers = get_suppliers(db, sku)
    open_orders = get_open_purchase_orders(db, sku)
    constraints = get_constraints(db, sku)

    context = {
        "sku": sku,
        "proposed_quantity": proposed_quantity,
        "inventory": inventory,
        "forecast": forecast,
        "suppliers": suppliers,
        "open_purchase_orders": open_orders,
        "constraints": constraints
    }

    prompt = f"""
{SYSTEM_PROMPT}

Purchasing situation:

{json.dumps(context, indent=2)}

Analyze the situation and return only valid JSON.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)
