# Task Decomposition & Specifications
## ShoeScribe AI — Multi-Agent Product Description Generation System

---

> **Course / Project Context:** AI Agent Systems Design  
> **Domain:** E-Commerce — Footwear Product Description Generation  
> **Architecture:** Sequential Multi-Agent Pipeline  
> **Primary LLM Backend:** Groq API (`llama-3.1-8b-instant`)  
> **External Tool:** Tavily Search API  
> **Interface:** Streamlit Web Application  

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Overall System Flow](#2-overall-system-flow)
3. [Input / Output Structure](#3-input--output-structure)
4. [Agent Specifications](#4-agent-specifications)
   - 4.1 [Research Agent](#41-research-agent)
   - 4.2 [Insight Agent](#42-insight-agent)
   - 4.3 [Copywriting Agent](#43-copywriting-agent)
   - 4.4 [Judge Agent](#44-judge-agent)
5. [Worked Example](#5-worked-example)
6. [Error Handling Summary](#6-error-handling-summary)
7. [Design Decisions & Constraints](#7-design-decisions--constraints)

---

## 1. System Overview

**ShoeScribe AI** is a sequential multi-agent system designed to automate the generation of high-quality, persuasive e-commerce product descriptions for footwear products. The system eliminates the need for manual copywriting by chaining four specialized AI agents, each responsible for a distinct phase of the content generation lifecycle.

The system follows a **linear pipeline architecture**, where the output of each agent becomes the structured input to the next. Coordination is managed by a central **Orchestrator** module (`orchestrator.py`), which invokes agents in a fixed sequence and consolidates their results into a unified response dictionary. A **Streamlit** front-end (`app.py`) exposes the pipeline to end users through a web interface.

### 1.1 Agents at a Glance

| # | Agent | Role | Underlying Technology |
|---|-------|------|----------------------|
| 1 | **Research Agent** | Retrieves real-world product information from the web | Tavily Search API |
| 2 | **Insight Agent** | Structures raw research into actionable marketing signals | Groq LLM (Llama 3.1 8B) |
| 3 | **Copywriting Agent** | Generates polished product descriptions from structured insights | Groq LLM (Llama 3.1 8B) |
| 4 | **Judge Agent** | Evaluates the generated copy across five quality dimensions | Groq LLM (Llama 3.1 8B) |

---

## 2. Overall System Flow

The following diagram illustrates the end-to-end execution flow of the pipeline.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER (Streamlit UI)                          │
│              Inputs: product_name, category                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR  (orchestrator.py)                  │
│                     run_pipeline(product_name, category)            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   [STEP 1]             [STEP 2]             [STEP 3]             [STEP 4]
 Research Agent  ──►  Insight Agent  ──►  Copywriting  ──►  Judge Agent
                                           Agent
          │                    │                    │                │
  {query,           {features,           {short_desc,        {scores:{clarity,persuasiveness,
   summary[]}        pain_points,         long_desc,           differentiation,feature_relevance,
                     benefits,            usp_bullets[]}       conversion_potential}
                     usp_ideas[]}                              (each:{score,reason}),
                                                               overall_feedback}
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FINAL RESULT DICTIONARY                          │
│   { "research": ..., "insights": ..., "content": ...,               │
│     "evaluation": ...}                                              │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                      Rendered in Streamlit UI
```

### 2.1 Execution Sequence

| Step | Action | Dependency |
|------|--------|------------|
| 1 | User provides `product_name` and `category` via UI | None |
| 2 | Orchestrator calls `research_agent(product_name, category)` | User Input |
| 3 | Orchestrator calls `insight_agent(research_output)` | Research Agent output |
| 4 | Orchestrator calls `copywriting_agent(insights, product_name)` | Insight Agent output |
| 5 | Orchestrator calls `judge_agent(content)` | Copywriting Agent output |
| 6 | Orchestrator returns unified result dictionary | All agent outputs |
| 7 | Streamlit UI renders each section with JSON parsing and fallback | Orchestrator return value |

---

## 3. Input / Output Structure

### 3.1 Global System Input

The system accepts two plain-text string inputs from the user:

```json
{
  "product_name": "string  — Name of the shoe product (e.g., 'Nike Air Max 270')",
  "category":     "string  — Shoe category or type  (e.g., 'running shoes')"
}
```

### 3.2 Global System Output

The orchestrator returns a single Python dictionary with four keys, each holding the raw string output (JSON-formatted) of the corresponding agent:

```json
{
  "research":   "{ \"query\": \"...\", \"summary\": [...] }",
  "insights":   "{ \"features\": [...], \"pain_points\": [...], \"benefits\": [...], \"usp_ideas\": [...] }",
  "content":    "{ \"short_description\": \"...\", \"long_description\": \"...\", \"usp_bullets\": [...] }",
  "evaluation": "{ \"clarity\": \"...\", \"persuasiveness\": \"...\", \"differentiation\": \"...\", \"feature_relevance\": \"...\", \"conversion_potential\": \"...\", \"feedback\": \"...\" }"
}
```

> [!NOTE]
> All LLM agents are instructed to return **strictly valid JSON** with no surrounding prose. The Streamlit UI attempts `json.loads()` on each output and falls back to `st.write()` if parsing fails, ensuring graceful degradation.

---

## 4. Agent Specifications

---

### 4.1 Research Agent

**File:** `agents/research_agent.py`  
**Tool Used:** `tools/tavily_tool.py` → Tavily Search REST API

#### 4.1.1 Purpose

The Research Agent is responsible for grounding the pipeline in real, factual, web-sourced information about the target shoe product and its competitive landscape. It converts raw user input into a structured collection of textual summaries retrieved from the internet.

#### 4.1.2 Input

| Parameter | Type | Source | Description |
|-----------|------|--------|-------------|
| `product_name` | `str` | User / Orchestrator | Name of the shoe product (e.g., `"Nike Air Max 270"`) |
| `category` | `str` | User / Orchestrator | Product category (e.g., `"running shoes"`) |

#### 4.1.3 Processing Steps

```
Step 1 — Query Construction
  Concatenate product_name, category, and fixed keywords:
  query = f"{product_name} {category} features benefits"
  → Example: "Nike Air Max 270 running shoes features benefits"

Step 2 — External API Call
  Invoke tavily_search(query) which sends an HTTP POST request to:
  URL      : https://api.tavily.com/search
  Payload  : { api_key, query, search_depth: "basic", max_results: 5 }
  Auth     : TAVILY_API_KEY loaded from .env

Step 3 — Result Extraction
  Iterate over results list in the API response JSON.
  For each result object, extract the "content" field.
  Append non-empty content strings to a summaries list.

Step 4 — Output Assembly
  Return a dictionary with:
    "query"   : the constructed search string
    "summary" : list of content strings (up to 5 entries)
```

#### 4.1.4 Output Schema

```json
{
  "query":   "Nike Air Max 270 running shoes features benefits",
  "summary": [
    "The Nike Air Max 270 features a large Air unit...",
    "Reviewers praised the cushioning for long-distance runs...",
    "..."
  ]
}
```

#### 4.1.5 Decision Points

| Decision | Condition | Outcome |
|----------|-----------|---------|
| Query enrichment | Always | Appends `"features benefits"` to ensure topically relevant results |
| Result count cap | Tavily returns ≤ 5 by default | At most 5 content summaries are collected |
| Empty content guard | `r.get("content", "")` | If a result has no content field, an empty string is appended (silently skipped in practice) |

#### 4.1.6 Error Handling

| Failure Mode | Cause | Current Behaviour | Recommended Improvement |
|--------------|-------|-------------------|------------------------|
| HTTP error from Tavily | Network failure, quota exceeded, invalid API key | `response.json()` will raise `JSONDecodeError` or return an error dict; the `for` loop over `results.get("results", [])` returns an empty list gracefully | Add `response.raise_for_status()` and wrap in `try/except requests.RequestException` |
| Missing API key | `.env` not configured | `requests.post` proceeds with `None` as key; Tavily returns a 401 error | Validate `os.getenv("TAVILY_API_KEY")` at startup and raise `EnvironmentError` |
| Empty results | No relevant pages found | `summary` is an empty list `[]` | Downstream agents receive empty context; add a minimum-results check |

---

### 4.2 Insight Agent

**File:** `agents/insight_agent.py`  
**Tool Used:** Groq API (`llama-3.1-8b-instant` via `config.py`)

#### 4.2.1 Purpose

The Insight Agent transforms unstructured web-scraped text into a structured, marketing-focused intelligence report. It uses an LLM to extract four categories of actionable information: product features, consumer pain points, key benefits, and unique selling proposition (USP) ideas.

#### 4.2.2 Input

| Parameter | Type | Source | Description |
|-----------|------|--------|-------------|
| `research_data` | `dict` | Orchestrator | Dictionary containing `"summary"` (list of strings from Research Agent) and `"category"` (string from user input) |

#### 4.2.3 Processing Steps

```
Step 1 — Context Truncation
  Concatenate only the first two items of research_data["summary"]:
  combined_text = " ".join(research_data["summary"][:2])
  → Limits token usage and focuses on the most relevant content

Step 2 — Prompt Construction
  Build a structured system prompt that:
    a) Presents the combined_text as competitor/market data
    b) Instructs the LLM to extract exactly four categories
    c) Specifies strict JSON-only output format
    d) Prohibits brand name invention to prevent hallucination

Step 3 — LLM Inference
  Call client.chat.completions.create() with:
    model    : "llama-3.1-8b-instant"
    messages : [{ "role": "user", "content": prompt }]
  Receive a ChatCompletion response object

Step 4 — Content Extraction
  Return response.choices[0].message.content
  → Raw string, expected to be valid JSON
```

#### 4.2.4 Output Schema

```json
{
  "features": [
    "Breathable mesh upper",
    "Responsive foam midsole",
    "Rubber outsole with multi-directional traction"
  ],
  "pain_points": [
    "Lack of arch support in budget alternatives",
    "Poor durability in cheaper options",
    "Narrow fit not suitable for wide feet"
  ],
  "benefits": [
    "Enhanced comfort for all-day wear",
    "Reduced foot fatigue during long runs",
    "Stylish design suitable for gym and casual use"
  ],
  "usp_ideas": [
    "All-day comfort engineered for performance",
    "Where style meets athletic precision",
    "Zero compromise on cushioning or durability"
  ]
}
```

#### 4.2.5 Decision Points

| Decision | Condition | Outcome |
|----------|-----------|---------|
| Context window management | Always takes `summary[:2]` | Ensures prompt stays within LLM token limits; trades completeness for reliability |
| JSON enforcement | Prompt instructs "Return STRICT JSON" and "Output ONLY JSON" | Reduces probability of prose-wrapped JSON that breaks downstream parsing |
| Markdown fence stripping | `_extract_json()` called on every LLM response | Strips ` ```json ``` ` wrappers before `json.loads()`, preventing parse failures |
| Schema validation with fallbacks | `_validate_schema()` checks each key; `FALLBACKS` dict provides category-aware defaults | If any list has fewer than 3 items or is missing, it is replaced with a realistic fallback for that shoe category |
| Empty context guard | `if not combined_text` | Returns a hardcoded fallback JSON dict rather than calling the LLM with empty input |

#### 4.2.6 Error Handling

| Failure Mode | Cause | Current Behaviour | Recommended Improvement |
|--------------|-------|-------------------|------------------------|
| LLM returns invalid JSON | Model adds preamble or markdown code blocks | `_extract_json()` strips fences; if `json.loads()` still fails, returns a safe empty structure | ✅ Handled |
| Empty `summary` input | Research Agent returned no results | `combined_text` becomes `""` — function returns hardcoded fallback dict immediately | ✅ Handled via explicit empty-context guard |
| Groq API failure | Rate limit, network error, invalid key | Unhandled exception propagates and crashes the pipeline | ⚠️ Wrap in `try/except` with a user-friendly error message |
| Malformed output keys or small lists | LLM deviates from schema or returns fewer items than required | `_validate_schema()` replaces invalid/short lists with category-aware `FALLBACKS` | ✅ Handled |

---

### 4.3 Copywriting Agent

**File:** `agents/copywriting_agent.py`  
**Tool Used:** Groq API (`llama-3.1-8b-instant` via `config.py`)

#### 4.3.1 Purpose

The Copywriting Agent synthesises the structured marketing intelligence from the Insight Agent into consumer-facing product copy. It produces three distinct output formats — a short teaser description, a detailed long-form description, and a bulleted list of USPs — mirroring the content structure used on real e-commerce product pages.

#### 4.3.2 Input

| Parameter | Type | Source | Description |
|-----------|------|--------|-------------|
| `insights` | `str` | Insight Agent | Raw JSON string containing features, pain_points, benefits, usp_ideas |
| `user_input` | `str` | Orchestrator | The `product_name` string from the original user input |

> [!NOTE]
> `user_input` is the product name (`product_name` variable), not the full user input dictionary. The `category` field is not passed to this agent directly.

#### 4.3.3 Processing Steps

```
Step 1 — Prompt Construction
  Build a prompt that:
    a) Establishes the agent's persona: "expert e-commerce copywriter"
    b) Injects insights (the raw JSON string) as the sole knowledge source
    c) Injects user_input (product name) as product context
    d) Specifies the required JSON output schema with three fields
    e) Lists four guardrail rules to constrain generation behaviour

Step 2 — LLM Inference
  Call client.chat.completions.create() with:
    model    : "llama-3.1-8b-instant"
    messages : [{ "role": "user", "content": prompt }]

Step 3 — Content Extraction
  Return response.choices[0].message.content
  → Raw string, expected to be valid JSON
```

#### 4.3.4 Output Schema

```json
{
  "short_description": "Experience unmatched comfort and style with every step. Engineered for performance, built for life.",
  "long_description": "Designed for athletes and everyday wearers alike, these running shoes combine a breathable mesh upper with a responsive foam midsole to deliver superior cushioning without the weight. The multi-directional rubber outsole ensures reliable grip on any surface, while the ergonomic last supports natural foot movement. Whether you're pushing through a 10K or navigating a busy day, these shoes adapt to every demand with effortless precision.",
  "usp_bullets": [
    "Breathable mesh upper for maximum airflow during intense activity",
    "Responsive foam midsole absorbs impact and returns energy with every stride",
    "Durable rubber outsole engineered for multi-surface grip",
    "Lightweight construction reduces foot fatigue on long runs",
    "Versatile design transitions seamlessly from gym to street"
  ]
}
```

#### 4.3.5 Decision Points

| Decision | Condition | Outcome |
|----------|-----------|---------|
| Persona priming | Always | "expert e-commerce copywriter" persona improves output quality and tone adherence |
| Insights-only grounding | Prompt states "Based ONLY on these insights" | Prevents the model from hallucinating features not supported by research |
| Generic brand rule | "Do NOT invent brand names" | Produces brand-neutral copy suitable for white-label or generic product pages |
| Realism constraint | "Keep it realistic and product-focused" | Prevents over-the-top marketing language that may reduce consumer trust |

#### 4.3.6 Error Handling

| Failure Mode | Cause | Current Behaviour | Recommended Improvement |
|--------------|-------|-------------------|------------------------|
| Malformed `insights` input | If Insight Agent returned invalid JSON, it is still passed as a string | LLM attempts to parse the raw string; quality degrades silently | Parse and validate `insights` before passing; use `json.loads()` with a fallback |
| JSON output non-compliance | LLM adds markdown formatting or prose | Streamlit `json.loads()` fails and renders raw string fallback | Add post-processing to strip markdown code block fences |
| Groq API failure | Quota/network error | Unhandled exception crashes the pipeline | Wrap in `try/except` with retry logic |
| Missing USP bullets | LLM returns empty list | UI renders no bullet points without error | Validate output: if `usp_bullets` is empty, flag for re-generation |

---

### 4.4 Judge Agent

**File:** `agents/judge_agent.py`  
**Tool Used:** Groq API (`llama-3.1-8b-instant` via `config.py`)

#### 4.4.1 Purpose

The Judge Agent acts as an autonomous quality evaluator. It independently reviews the product descriptions generated by the Copywriting Agent and scores them across five marketing-effectiveness dimensions, providing actionable feedback. This closes the quality-assurance loop within the pipeline without requiring human review.

#### 4.4.2 Input

| Parameter | Type | Source | Description |
|-----------|------|--------|-------------|
| `content` | `str` | Copywriting Agent | Raw JSON string containing `short_description`, `long_description`, and `usp_bullets` |

#### 4.4.3 Processing Steps

```
Step 1 — Prompt Construction
  Build an evaluation prompt that:
    a) Presents the content (raw JSON string) to be evaluated
    b) Defines a 1–5 integer scoring rubric (Poor → Excellent)
    c) Specifies five evaluation dimensions with strict JSON-only output
    d) Requires a per-dimension integer "score" + one-sentence "reason"
    e) Requires an "overall_feedback" string with 1–2 actionable suggestions

Step 2 — LLM Inference
  Call client.chat.completions.create() with:
    model    : "llama-3.1-8b-instant"
    messages : [{ "role": "user", "content": prompt }]

Step 3 — Content Extraction
  Return response.choices[0].message.content
  → Raw string, expected to be valid JSON evaluation report
```

#### 4.4.4 Output Schema

```json
{
  "scores": {
    "clarity": {
      "score": 4,
      "reason": "The copy uses simple language and logical flow, making it easy to understand."
    },
    "persuasiveness": {
      "score": 4,
      "reason": "The copy effectively emphasises benefits of comfort and support with emotional hooks."
    },
    "differentiation": {
      "score": 3,
      "reason": "While the copy highlights unique features, some of the language is generic and could be more nuanced."
    },
    "feature_relevance": {
      "score": 5,
      "reason": "The highlighted features such as lightweight cushioning and slip-on closure are highly relevant to footwear buyers."
    },
    "conversion_potential": {
      "score": 4,
      "reason": "The copy includes a clear call to action in the tone but lacks urgency or a clear mention of value."
    }
  },
  "overall_feedback": "Consider adding more nuanced language to differentiate the product and including specific values or benefits to reinforce the CTA."
}
```

#### 4.4.5 Decision Points

| Decision | Condition | Outcome |
|----------|-----------|---------|
| Five-dimension evaluation | Always | Provides a structured, reproducible quality report rather than a subjective freeform review |
| Numeric 1–5 integer scoring rubric | Prompt enforces integer scores; rubric defines Poor=1 through Excellent=5 | Eliminates qualitative label inconsistency across runs; enables direct numeric comparison |
| Per-dimension reason field | Prompt requires a ≤20-word sentence citing copy evidence | Makes scores auditable and traceable to specific copy elements |
| Separate `overall_feedback` field | Always | Consolidates 1–2 actionable improvement suggestions into one field for easier parsing |
| Same model as other agents | `llama-3.1-8b-instant` | Ensures consistency; however, using a more capable/different model could reduce circular self-evaluation bias |

#### 4.4.6 Error Handling

| Failure Mode | Cause | Current Behaviour | Recommended Improvement |
|--------------|-------|-------------------|------------------------|
| Circular bias | Same model evaluates its own generation | Evaluation may be biased toward leniency | Use a different, more powerful model (e.g., `llama-3.3-70b`) for the Judge Agent |
| Invalid JSON output | LLM wraps output in markdown or prose | Orchestrator wraps `json.loads()` in `try/except`; on failure evaluation dict is empty `{}` | ✅ Handled with graceful degradation |
| Missing evaluation fields | LLM omits one or more score keys | UI renders only the keys present; no crash | ⚠️ Validate all five score keys are present before returning |

---

## 5. Worked Example

The following illustrates a complete end-to-end execution trace through the system.

### 5.1 System Input

```json
{
  "product_name": "Nike Air Max 270",
  "category":     "running shoes"
}
```

### 5.2 Research Agent Output

**Constructed Query:** `"Nike Air Max 270 running shoes features benefits"`

```json
{
  "query": "Nike Air Max 270 running shoes features benefits",
  "summary": [
    "The Nike Air Max 270 features Nike's largest Air unit yet in the heel, providing maximum cushioning and a bold look. The upper is made from engineered mesh for breathability, and the design is inspired by the Air Max 180 and 93.",
    "Users report excellent comfort for casual wear and light jogging. The shoe offers a snug fit with a pull-tab for easy wear. The foam midsole complements the Air unit for a comfortable ride. Ideal for lifestyle use and light training.",
    "Compared to other Air Max models, the 270 prioritises lifestyle comfort over aggressive athletic performance. It lacks a structured support system, which some users find limiting for high-intensity sports.",
    "The outsole uses durable rubber with a waffle-inspired tread pattern for traction on urban surfaces. Available in a wide range of colourways to suit different style preferences.",
    "Price range: $130–$160. Competitors include Adidas UltraBoost and New Balance Fresh Foam, which offer more structured support for serious runners."
  ]
}
```

### 5.3 Insight Agent Output

```json
{
  "features": [
    "Largest Air unit heel cushioning",
    "Engineered mesh upper for breathability",
    "Foam midsole complementing Air unit",
    "Durable rubber waffle-tread outsole",
    "Pull-tab for easy wear"
  ],
  "pain_points": [
    "Lacks structured support for high-intensity sports",
    "Not ideal for serious running performance",
    "Competing models offer more support at similar price points"
  ],
  "benefits": [
    "Maximum heel cushioning for all-day comfort",
    "Breathable upper reduces heat buildup",
    "Lightweight design minimises foot fatigue",
    "Versatile for lifestyle and light training use"
  ],
  "usp_ideas": [
    "The biggest Air cushion. The boldest statement.",
    "From morning runs to city streets — one shoe, endless comfort.",
    "Inspired by icons, built for today."
  ]
}
```

### 5.4 Copywriting Agent Output

```json
{
  "short_description": "Bold design meets unrivalled cushioning. The ultimate shoe for those who refuse to compromise on comfort or style.",
  "long_description": "Step into a new dimension of comfort with a shoe built around Nike's largest Air heel unit ever. The engineered mesh upper wraps your foot in breathable, lightweight support, while the foam midsole works in harmony with the Air cushioning to absorb every impact. A durable rubber outsole with waffle-inspired tread keeps you confident on any urban surface. Whether you're logging early morning miles or navigating a busy day in the city, this shoe transitions effortlessly — because your life doesn't stop, and neither should your comfort.",
  "usp_bullets": [
    "Largest Air unit heel — superior cushioning you can feel from the first step",
    "Engineered mesh upper delivers targeted breathability and a sock-like fit",
    "Foam + Air midsole combination for responsive, all-day impact absorption",
    "Waffle-tread rubber outsole for reliable traction on city surfaces",
    "Versatile lifestyle-to-training design with pull-tab for effortless wear"
  ]
}
```

### 5.5 Judge Agent Output

```json
{
  "clarity":              "High — Copy is clear, jargon-free, and easy to understand across all three formats.",
  "persuasiveness":       "High — The long description uses vivid sensory language and a lifestyle narrative that resonates with the target audience.",
  "differentiation":      "Medium — USPs highlight features effectively, but do not strongly contrast against named competitors.",
  "feature_relevance":    "High — All five USP bullets map directly to extracted product features.",
  "conversion_potential": "High — Strong headline, compelling narrative, and specific feature bullets create a persuasive purchase case.",
  "feedback":             "To strengthen differentiation, consider adding a direct comparison hook (e.g., 'More cushion than the competition, at a price that makes sense'). Including a size/fit note could also reduce purchase hesitation."
}
```

---

## 6. Error Handling Summary

The table below consolidates the cross-cutting error handling posture of the system.

| Layer | Error Category | Current State | Priority Fix |
|-------|---------------|---------------|--------------|
| UI (app.py) | JSON parse failure | `safe_json()` with `try/except` fallback | ✅ Handled |
| Research Agent | HTTP / API failure | Unhandled — crashes pipeline | ⚠️ Add try/except + raise_for_status |
| Research Agent | Missing API key | Silent `None` key, 401 from Tavily | ⚠️ Validate at startup |
| Research Agent | Empty results | Empty list passed downstream | ⚠️ Add minimum results guard |
| Insight Agent | Empty context | Returns hardcoded fallback JSON immediately | ✅ Handled |
| Insight Agent | LLM JSON non-compliance | `_extract_json()` strips fences; `try/except` returns safe empty structure | ✅ Handled |
| Insight Agent | Schema too sparse | `_validate_schema()` replaces short/missing lists with `FALLBACKS` | ✅ Handled |
| Copywriting Agent | Malformed insight input | `json.loads()` + `_validate_schema()` before use; safe defaults on failure | ✅ Handled |
| Judge Agent | Circular evaluation bias | LLM evaluates its own output | ℹ️ Design limitation — consider model change |
| Judge Agent | Non-standardised scores | Numeric 1–5 rubric enforced in prompt | ✅ Handled |
| Judge Agent | Invalid JSON response | Orchestrator wraps `json.loads()` in `try/except`; falls back to `{}` | ✅ Handled |
| All LLM Agents | Groq API failure | Unhandled exception | ⚠️ Add try/except with retry logic |

---

## 7. Design Decisions & Constraints

### 7.1 Sequential vs. Parallel Architecture

The system uses a **strictly sequential pipeline**. This choice ensures that each agent benefits from the full output of its predecessor, maintaining semantic coherence throughout the generation process. A parallel architecture (e.g., Research + Insight concurrently) was not adopted because the Insight Agent is semantically dependent on Research Agent results.

### 7.2 Context Window Management in Insight Agent

The Insight Agent deliberately truncates research summaries to the first two items (`summary[:2]`). This is a pragmatic trade-off between **token economy** and **coverage** — using all five summaries risks exceeding the effective context window of the `llama-3.1-8b-instant` model for structured extraction tasks.

### 7.3 Unified LLM Model Across Agents

All three LLM-based agents (`insight_agent`, `copywriting_agent`, `judge_agent`) use the same model: `llama-3.1-8b-instant` via the Groq API. This simplifies configuration and reduces API complexity, but introduces a **self-evaluation bias** in the Judge Agent, as it evaluates content generated by an identical model with similar priors. The Judge Agent mitigates inconsistency by enforcing a strict **1–5 integer scoring rubric** with per-dimension one-sentence justifications, making scores reproducible and auditable even within the same model.

### 7.4 JSON-as-Contract Communication Protocol

Inter-agent communication relies entirely on **JSON strings** as the lingua franca. Agents do not share memory or state — each receives a string input and returns a string output. This stateless design improves modularity and testability, but requires robust JSON validation at each boundary, which is currently only partially implemented.

### 7.5 Hallucination Mitigation Strategy

Two explicit constraints appear in the LLM prompts to reduce hallucination:
1. **"Do not invent brand names"** — prevents the model from fabricating competitor or endorsement references.
2. **"Based ONLY on these insights"** — grounds the Copywriting Agent's output strictly in Insight Agent data, rather than allowing the model to draw on parametric memory.

### 7.6 Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM Inference | Groq API (`llama-3.1-8b-instant`) | Fast, cost-effective language model inference |
| Web Search | Tavily Search API | Real-time, LLM-optimised web retrieval |
| UI Framework | Streamlit | Rapid deployment of interactive Python web apps |
| Configuration | `python-dotenv` | Secure API key management via `.env` file |
| HTTP Client | `requests` | Tavily API communication |

---

*Document prepared for ShoeScribe AI — Multi-Agent System Design.*  
*All agent specifications are derived from source code analysis of the production codebase.*
