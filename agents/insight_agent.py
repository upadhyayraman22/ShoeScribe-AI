import json
import re
from config import client

FALLBACKS = {
    "running shoes": {
        "features": ["breathable mesh upper", "responsive cushioning", "lightweight build", "shock absorption sole", "durable outsole"],
        "benefits": ["reduces fatigue", "improves running performance", "enhances comfort", "supports long-distance runs", "prevents foot strain"],
        "pain_points": ["foot fatigue", "poor cushioning", "sweaty feet", "heavy shoes", "lack of support"],
        "usp_ideas": ["engineered for endurance", "optimized energy return", "ultra-light comfort design"]
    },
    "casual shoes": {
        "features": ["stylish design", "comfortable insole", "durable material", "lightweight construction", "versatile look"],
        "benefits": ["all-day comfort", "matches multiple outfits", "easy to wear", "long-lasting usage", "enhanced style"],
        "pain_points": ["uncomfortable fit", "poor durability", "outdated design", "heavy feel", "low breathability"],
        "usp_ideas": ["perfect everyday wear", "blend of comfort and fashion", "designed for daily lifestyle"]
    }
}

def _extract_json(raw: str) -> str:
    """Strip markdown code fences if present and return the bare JSON string."""
    raw = raw.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if fenced:
        return fenced.group(1).strip()
    return raw

def _validate_schema(data: dict, category: str) -> dict:
    category = category.lower()

    fallback = FALLBACKS.get(category, FALLBACKS.get("casual shoes"))  # type: ignore[name-defined]

    for key in ["features", "benefits", "pain_points", "usp_ideas"]:
        value = data.get(key, [])

        # If invalid OR too small → replace with fallback
        if not isinstance(value, list) or len(value) < 3:
            data[key] = fallback[key]

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
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    raw = response.choices[0].message.content
    cleaned = _extract_json(raw)

    try:
        parsed = json.loads(cleaned)
        validated = _validate_schema(parsed, research_data.get("category", "casual shoes"))
        return json.dumps(validated)
    except (json.JSONDecodeError, ValueError):
        # Return a safe empty structure rather than propagating broken JSON
        return json.dumps({
            "features": [],
            "pain_points": [],
            "benefits": [],
            "usp_ideas": []
        })