# 👟 ShoeScribe AI
### *Product descriptions that don't just describe — they sell.*

> A sequential multi-agent AI system that researches, writes, and evaluates high-converting e-commerce product descriptions for footwear — fully automated, end-to-end.

🔗 **Live Demo:** [web-production-c9ce1.up.railway.app](https://web-production-c9ce1.up.railway.app)

---

## 📌 Problem Statement

Writing compelling product descriptions for footwear is time-consuming, inconsistent, and requires both domain knowledge and copywriting expertise. E-commerce sellers and brands often resort to generic, uninspiring copy that fails to convert browsers into buyers.

**ShoeScribe AI** solves this by deploying a pipeline of four specialized AI agents that:
1. **Research** real competitor data and product features from the web
2. **Extract** marketing insights — features, pain points, benefits, and USPs
3. **Write** polished, conversion-optimized product descriptions
4. **Evaluate** the output across five quality dimensions using an LLM-as-Judge

An agentic approach is ideal here because the task naturally decomposes into sequential, interdependent subtasks — each requiring different reasoning capabilities — that no single LLM prompt can reliably handle alone.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│             USER  (Streamlit UI)            │
│        Inputs: product_name, category       │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           ORCHESTRATOR  (orchestrator.py)   │
└──┬────────────────────────────────────────┬─┘
   │                                        │
   ▼                                        ▼
[Agent 1]          [Agent 2]          [Agent 3]          [Agent 4]
Research    ──►    Insight     ──►   Copywriting  ──►    Judge
Agent              Agent              Agent              Agent
   │                 │                  │                  │
Tavily API       Groq LLM           Groq LLM           Groq LLM
   │                 │                  │                  │
{query,         {features,         {short_desc,       {clarity,
 summary[]}      pain_points,       long_desc,          persuasiveness,
                 benefits,          usp_bullets[]}      differentiation,
                 usp_ideas[]}                           feature_relevance,
                                                       {scores: {
                                                        clarity: {score, reason},
                                                        persuasiveness: {score, reason},
                                                        differentiation: {score, reason},
                                                        feature_relevance: {score, reason},
                                                        conversion_potential: {score, reason}},
                                                        overall_feedback}
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         FINAL RESULT  (rendered in UI)      │
│  { research, insights, content, evaluation }│
└─────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|---|---|
| LLM Inference | Groq API (`llama-3.1-8b-instant`) |
| Web Search Tool | Tavily Search API |
| UI Framework | Streamlit |
| Deployment | Railway |
| Config Management | python-dotenv |
| HTTP Client | requests |

---

## 🤖 Agents Overview

### 1. 🔍 Research Agent
- **Tool:** Tavily Search API
- Constructs a search query from the product name and category
- Retrieves up to 5 real web results about the product
- Outputs a structured summary for downstream agents

### 2. 💡 Insight Agent
- **Tool:** Groq LLM (`llama-3.1-8b-instant`)
- Transforms raw research into structured marketing intelligence
- Extracts: `features`, `pain_points`, `benefits`, `usp_ideas`
- Validates schema — enforces minimum 5 items per category; falls back to category-aware defaults if LLM output is insufficient
- Strips markdown code fences from LLM output before JSON parsing
- Prevents hallucination by grounding strictly in research data

### 3. ✍️ Copywriting Agent
- **Tool:** Groq LLM (`llama-3.1-8b-instant`)
- Generates three copy formats: short description (max 30 words), long description (max 100 words), and 4–6 USP bullets
- Persona-primed as an "expert e-commerce copywriter"
- Grounded only in Insight Agent output — no hallucinated claims
- Robust JSON parsing with markdown fence stripping and schema validation with safe defaults on failure

### 4. ⚖️ Judge Agent (LLM-as-Judge)
- **Tool:** Groq LLM (`llama-3.1-8b-instant`)
- Evaluates generated copy across 5 dimensions with a strict 1–5 integer scoring rubric:
  - **Clarity** — readability and absence of jargon
  - **Persuasiveness** — emotional hooks and benefit emphasis
  - **Differentiation** — uniqueness vs. generic phrases
  - **Feature Relevance** — importance of highlighted features to footwear buyers
  - **Conversion Potential** — CTA strength and purchase intent
- Returns a per-dimension score + one-sentence reason + overall actionable feedback
- Closes the quality-assurance loop without human review

---

## 🚀 Getting Started (Run Locally)

### Prerequisites
- Python 3.10+
- A [Groq API key](https://console.groq.com)
- A [Tavily API key](https://tavily.com)

### 1. Clone the repository
```bash
git clone https://github.com/upadhyayraman22/ShoeScribe-AI.git
cd ShoeScribe-AI
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 4. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🎯 How to Use

1. Enter a **Product Name** (e.g., `Puma Softride Pro Echo Consonance`)
2. Enter the **Category** (e.g., `Walking Shoes`)
3. Click **Generate**
4. Watch the 4-stage pipeline execute in real time:
   - ✅ Research → ✅ Insights → ✅ Writing → ✅ Evaluate
5. Get your ready-to-publish product description + quality scores

---

## 📁 Project Structure

```
ShoeScribe-AI/
├── app.py                              # Streamlit frontend
├── orchestrator.py                     # Pipeline coordinator
├── config.py                           # Groq client setup
├── style.css                           # Custom UI styling
├── requirements.txt                    # Python dependencies
├── Procfile                            # Railway deployment config
├── task_decomposition_specifications.md # Full agent specs & design doc
├── agents/
│   ├── research_agent.py               # Agent 1: Tavily web search
│   ├── insight_agent.py                # Agent 2: Feature extraction
│   ├── copywriting_agent.py            # Agent 3: Copy generation
│   └── judge_agent.py                  # Agent 4: LLM-as-Judge
└── tools/
    └── tavily_tool.py                  # Tavily API wrapper
```

---

## 📊 Sample Output

**Input:** `Puma Softride Premier GlideKnit` | `Walking Shoes`

**Market Insights extracted:**
- **Features:** Lightweight cushioning, Engineered knit upper, One-piece construction, Slip-on closure, Soft cushioning
- **Pain Points:** Foot pain, Sweating, Poor fit, Lack of cushioning, Discomfort
- **Benefits:** All-day comfort, Reduces fatigue, Improves performance, Enhanced comfort, Provides support
- **USP Ideas:** Cutting-edge cushioning tech, Environmentally-friendly materials, Ergonomic shoe design for better fit

**Short Description:**
> *"Experience unparalleled comfort with the Puma Softride Premier GlideKnit. Enjoy all-day comfort and support on your feet."*

**Key Selling Points generated:**
- Lightweight Cushioning — Reduces fatigue and improves performance
- Engineered Knit Upper — Provides a secure, easy fit
- One-Piece Construction — Offers enhanced comfort and support
- Slip-On Closure — Easy to put on and take off
- Soft Cushioning — Provides comfort and support all day
- Cutting-edge Cushioning Tech — Improves overall comfort and performance

**Quality Evaluation:**
| Dimension | Score | Reason |
|---|---|---|
| Clarity | 4/5 | Simple language and logical flow, easy to understand |
| Persuasiveness | 4/5 | Effectively emphasizes comfort and support with emotional hooks |
| Differentiation | 3/5 | Highlights unique features but some language is generic |
| Feature Relevance | 5/5 | Lightweight cushioning and slip-on closure are highly relevant |
| Conversion Potential | 4/5 | Clear CTA tone but lacks urgency or specific value mention |
| **Overall** | **4.0/5** | |

**Feedback:** *Consider adding more nuanced language to differentiate the product and including specific values or benefits to reinforce the CTA.*

---

## 👥 Team

| Name | GitHub |
|---|---|
| Raman Upadhyay | [@upadhyayraman22](https://github.com/upadhyayraman22) |
| S. Devanshu Murthy | — |

---

## 📄 Documentation

- [Task Decomposition & Specifications](./task_decomposition_specifications.md) — Full agent specs, input/output schemas, error handling, and design decisions.

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key for LLM inference |
| `TAVILY_API_KEY` | Your Tavily API key for web search |

> ⚠️ Never commit your `.env` file. Add it to `.gitignore`.

---

*Built for AI Agent Systems Design course project.*
