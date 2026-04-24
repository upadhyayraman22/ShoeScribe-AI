import json
import re
from config import client

def _extract_json(raw: str) -> str:
    """Strip markdown code fences if present and return the bare JSON string."""
    raw = raw.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if fenced:
        return fenced.group(1).strip()
    return raw

def _validate_schema(data: dict) -> dict:
    """Ensure all required keys exist; fill missing ones with safe defaults."""
    defaults = {
        "short_description": "",
        "long_description": "",
        "usp_bullets": []
    }
    for key, default in defaults.items():
        if key not in data:
            data[key] = default
    # Ensure usp_bullets is a list
    if not isinstance(data["usp_bullets"], list):
        data["usp_bullets"] = []
    return data

def copywriting_agent(insights, user_input, feedback=None):
    # Safely parse insights so we know what we're working with
    if isinstance(insights, str):
        try:
            insights_obj = json.loads(insights)
            insights_text = json.dumps(insights_obj, indent=2)
        except (json.JSONDecodeError, ValueError):
            insights_text = insights.strip()
    else:
        insights_text = json.dumps(insights, indent=2)

    feedback_instruction = ""

    if feedback and len(feedback.strip()) > 10:
        feedback_instruction = f"""
Improve the product description based on this feedback:

{feedback}

Rules:
- Fix only the weak areas mentioned
- Keep strong parts unchanged
- Improve weak sections; rewrite parts only if necessary for clarity and impact
- Improve clarity, persuasiveness, and structure
"""
    prompt = f"""You are an expert e-commerce copywriter specialising in footwear products.

{feedback_instruction}

Product name: {user_input}

Below are the structured product insights you must use as your ONLY knowledge source.
These were extracted from verified market research data.

---
{insights_text}
---

Your task is to write compelling, conversion-focused product copy using ONLY the insights above.

GROUNDING RULES (strictly enforced):
- Base content primarily on the insights above.
- You may improve clarity, structure, and persuasiveness using general writing knowledge.
- Do NOT invent specific product claims not supported by the insights.
- Do NOT create or invent brand names, company names, or competitor names.
- Do NOT fabricate features, statistics, endorsements, or claims not found in the input.
- If a USP bullet has no supporting insight, do NOT include it.
- If unsure about a claim, use generic, neutral language instead of inventing specifics.
- Keep all copy realistic and grounded in the provided data.

OUTPUT RULES:
- Respond with ONLY a single valid JSON object.
- No markdown, no code fences, no commentary, no text before or after the JSON.
- short_description : 1–2 sentences, max 30 words, punchy and buyer-focused.
- long_description  : 3–5 sentences, max 100 words, benefit-driven and specific to the insights.
- usp_bullets       : 4–6 items, each max 12 words, in the format "<Feature — Benefit>".
- If there are insufficient insights for a field, return an empty string or empty list.

Return exactly this JSON structure:

{{
  "short_description": "<1-2 punchy sentences grounded in the provided insights>",
  "long_description": "<3-5 sentences of detailed, benefit-driven copy from the insights>",
  "usp_bullets": [
    "<Feature — specific benefit derived from the insights>",
    "..."
  ]
}}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
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
            "short_description": "",
            "long_description": "",
            "usp_bullets": []
        })