from config import client

def judge_agent(content):
    prompt = f"""You are a senior e-commerce content strategist acting as a quality judge.

You have been given the following shoe product description copy to evaluate:

{content}

---

EVALUATION RUBRIC:
Score each dimension from 1 to 5 using the scale below. Apply it consistently.

  1 = Poor       — Major deficiency, fails the criterion entirely
  2 = Weak       — Partially meets the criterion with notable gaps
  3 = Adequate   — Meets the criterion at a basic level
  4 = Good       — Clearly meets the criterion with minor room for improvement
  5 = Excellent  — Fully satisfies the criterion; hard to improve

DIMENSIONS:
  - clarity            : Is the copy easy to read and understand for a general buyer? (No jargon, logical flow)
  - persuasiveness     : Does the copy convince the reader to consider buying? (Emotional hooks, benefit emphasis)
  - differentiation    : Does the copy communicate what sets this product apart? (Unique angles, avoids generic phrases)
  - feature_relevance  : Are the highlighted features meaningful and important to a footwear buyer?
  - conversion_potential: How likely is this copy to drive a purchase action? (CTA strength, urgency, clarity of value)

---

STRICT OUTPUT RULES:
- Respond with ONLY a single valid JSON object. No markdown, no code fences, no extra text.
- Do NOT add any text before or after the JSON object.
- "score" must be an integer between 1 and 5 (inclusive). Never use 0 or null.
- "reason" must be a single, specific sentence (max 20 words) citing evidence from the provided copy.
- "overall_feedback" must be 1–2 actionable improvement suggestions (max 50 words total).
- Base ALL evaluations ONLY on the provided content. Do not infer or invent claims.
- Be consistent: the same quality of copy should always receive the same score.

Return exactly this JSON structure with no deviations:

{{
  "scores": {{
    "clarity": {{
      "score": <integer 1-5>,
      "reason": "<specific one-sentence justification citing the copy>"
    }},
    "persuasiveness": {{
      "score": <integer 1-5>,
      "reason": "<specific one-sentence justification citing the copy>"
    }},
    "differentiation": {{
      "score": <integer 1-5>,
      "reason": "<specific one-sentence justification citing the copy>"
    }},
    "feature_relevance": {{
      "score": <integer 1-5>,
      "reason": "<specific one-sentence justification citing the copy>"
    }},
    "conversion_potential": {{
      "score": <integer 1-5>,
      "reason": "<specific one-sentence justification citing the copy>"
    }}
  }},
  "overall_feedback": "<1-2 specific, actionable improvement suggestions based only on the copy provided>"
}}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content