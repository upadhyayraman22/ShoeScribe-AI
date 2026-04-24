import json
import re
from config import client

def _extract_json(raw: str) -> str:
    """Strip markdown code fences if present and return the bare JSON string."""
    raw = raw.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if fenced:
        return fenced.group(1).strip()
    return raw

def _validate_schema(data: dict) -> dict:
    defaults = {
        "features": ["basic feature"],
        "pain_points": ["general discomfort"],
        "benefits": ["basic benefit"],
        "usp_ideas": ["standard advantage"]
    }

    for key, default in defaults.items():
        if key not in data or not isinstance(data[key], list) or len(data[key]) == 0:
            data[key] = default

    return data

def insight_agent(research_data):
    combined_text = " ".join(research_data["summary"][:2]).strip()

    if not combined_text:
        fallback = {
            "features": ["lightweight design", "breathable material", "durable build", "cushioned sole", "ergonomic fit"],
            "pain_points": ["foot fatigue", "poor ventilation", "lack of support", "low durability", "bad fit"],
            "benefits": ["better comfort", "improved performance", "longer wear life", "reduced strain", "enhanced support"],
            "usp_ideas": ["advanced cushioning tech", "eco-friendly materials", "designed for all-day comfort"]
        }
        return json.dumps(fallback)

    prompt = """You are a product research analyst specialising in footwear.

Below is raw market research data extracted from the web about a shoe product.

---
{combined_text}
---

Return STRICT JSON in this format:

{{
  "features": ["lightweight", "breathable", "durable", "shock absorption", "comfortable fit"],
  "benefits": ["reduces fatigue", "improves performance", "long-lasting wear", "better support", "enhanced comfort"],
  "pain_points": ["foot pain", "sweating", "poor durability", "lack of cushioning", "bad fit"],
  "usp_ideas": ["advanced cushioning technology", "eco-friendly materials", "ergonomic design"]
}}

Rules:
- features MUST have at least 5 SPECIFIC product features
- benefits MUST have at least 5 CLEAR customer outcomes
- pain_points MUST have at least 5 REALISTIC customer problems
- usp_ideas MUST have at least 3 STRONG marketing angles

- Prefer extracting from the text, but if missing, infer realistic items based on category

- Avoid generic words like: "good", "nice", "high quality"
- Make outputs highly relevant to the product and category

- DO NOT return empty arrays
- Output ONLY JSON
""".format(combined_text=combined_text)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    cleaned = _extract_json(raw)

    try:
        parsed = json.loads(cleaned)
        validated = _validate_schema(parsed)
        return json.dumps(validated)
    except (json.JSONDecodeError, ValueError):
        # Return a safe empty structure rather than propagating broken JSON
        return json.dumps({
            "features": [],
            "pain_points": [],
            "benefits": [],
            "usp_ideas": []
        })