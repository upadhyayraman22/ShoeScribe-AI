# 👟 ShoeScribe AI
### *Product descriptions that don't just describe — they sell.*

> A sequential multi-agent AI system that researches, writes, and evaluates high-converting e-commerce product descriptions for footwear — fully automated, end-to-end.

🔗 **Live Demo:** [web-production-c9ce1.up.railway.app](https://web-production-c9ce1.up.railway.app)

---

## 📋 Table of Contents

1. [Problem Statement](#-problem-statement)
2. [Why an Agentic Approach](#-why-an-agentic-approach)
3. [System Architecture](#️-system-architecture)
4. [Agent Workflow](#-agent-workflow)
5. [Task Decomposition](#-task-decomposition)
6. [LLM-as-Judge](#️-llm-as-judge)
7. [Technology Stack](#️-technology-stack)
8. [Key Features](#-key-features)
9. [Setup & Installation](#-setup--installation)
10. [Deployment](#-deployment)
11. [Example Output](#-example-output)
12. [Project Structure](#-project-structure)
13. [Demo Video](#-demo-video)
14. [Team](#-team)

---

## 📌 Problem Statement

Writing compelling product descriptions for footwear is time-consuming, inconsistent, and requires both domain knowledge and copywriting expertise. E-commerce sellers and brands often resort to generic, uninspiring copy that fails to convert browsers into buyers.

**ShoeScribe AI** solves this by deploying a pipeline of four specialized AI agents that:
1. **Research** real competitor data and product features from the web
2. **Extract** marketing insights — features, pain points, benefits, and USPs
3. **Write** polished, conversion-optimized product descriptions
4. **Evaluate** the output across five quality dimensions using an LLM-as-Judge

---

## 🧠 Why an Agentic Approach

A single LLM prompt cannot reliably accomplish this task because the workflow involves four fundamentally different reasoning capabilities that must execute in a strict dependency chain:

- **Web Retrieval** — fetching real, grounded product data from the internet (requires an external tool)
- **Structured Extraction** — converting raw web text into actionable marketing categories
- **Creative Generation** — producing persuasive, audience-specific product copy from structured data
- **Critical Evaluation** — scoring output quality across professional dimensions with specific justifications

Each agent depends entirely on the output of its predecessor. This sequential dependency makes a pipeline architecture the only viable design. Additionally, an agentic approach allows each agent to be independently prompted, validated, and improved — a modularity that a monolithic prompt cannot provide.

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    USER  (Streamlit UI)                  │
│              Inputs: product_name + category             │
└────────────────────────┬─────────────────────────────────┘
                         │  run_pipeline(name, category)
                         ▼
┌──────────────────────────────────────────────────────────┐
│              ORCHESTRATOR  (orchestrator.py)             │
│          Coordinates sequential agent execution          │
└────────────────────────┬─────────────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │         AGENT 1             │◄──── 🔎 Tavily Search API
          │      Research Agent         │          tavily_tool.py
          │    research_agent.py        │
          │  Queries web for product    │
          │  features & competitors     │
          │                             │
          │  OUTPUT:                    │
          │  { query: string,           │
          │    summary: string[] }      │
          └──────────────┬──────────────┘
                         │ { query, summary[] }
                         ▼
          ┌──────────────────────────────┐
          │         AGENT 2              │◄──── 🤖 Groq API
          │       Insight Agent          │    llama-3.1-8b-instant
          │      insight_agent.py        │
          │  Extracts features, pain     │
          │  points, benefits, USPs      │
          │                              │
          │  OUTPUT:                     │
          │  { features: string[],       │
          │    pain_points: string[],    │
          │    benefits: string[],       │
          │    usp_ideas: string[] }     │
          └──────────────┬───────────────┘
                         │ { features, pain_points... }
                         ▼
          ┌──────────────────────────────┐
          │         AGENT 3              │◄──── 🤖 Groq API
          │     Copywriting Agent        │    llama-3.1-8b-instant
          │   copywriting_agent.py       │
          │  Generates short desc,       │
          │  long desc, USP bullets      │
          │                              │
          │  OUTPUT:                     │
          │  { short_description,        │
          │    long_description,         │
          │    usp_bullets: string[] }   │
          └──────────────┬───────────────┘
                         │ { short_desc, long_desc... }
                         ▼
          ┌──────────────────────────────┐
          │         AGENT 4              │◄──── 🤖 Groq API
          │  Judge Agent (LLM-as-Judge)  │    llama-3.1-8b-instant
          │      judge_agent.py          │
          │  Scores copy on 5 dimensions │
          │  with 1–5 integer rubric     │
          │                              │
          │  OUTPUT:                     │
          │  { scores: {                 │
          │    clarity: {score, reason}, │
          │    persuasiveness: {...},    │
          │    differentiation: {...},   │
          │    feature_relevance: {...}, │
          │    conversion_potential:{...}│
          │  }, overall_feedback }       │
          └──────────────┬───────────────┘
                         │ Final result object
┌────────────────────────▼─────────────────────────────────┐
│               STREAMLIT UI — Final Rendered Output        │
│   Market Insights  •  Product Description (short + long  │
│   + USP bullets)  •  Quality Evaluation (scores +        │
│   per-dimension reasons + overall feedback)              │
└──────────────────────────────────────────────────────────┘
```

> 📐 Full visual diagram: [`Submission_Files/Architecture_diagram.png`](./Submission_Files/)

---

## 🔄 Agent Workflow

| Step | Agent | Input | Tool | Output |
|---|---|---|---|---|
| 1 | Research Agent | `product_name`, `category` | Tavily Search API | `{ query, summary[] }` |
| 2 | Insight Agent | Research summary | Groq LLM | `{ features[], pain_points[], benefits[], usp_ideas[] }` |
| 3 | Copywriting Agent | Insight JSON | Groq LLM | `{ short_description, long_description, usp_bullets[] }` |
| 4 | Judge Agent | Copy JSON | Groq LLM | `{ scores: { dimension: {score, reason} }, overall_feedback }` |

---

## 📝 Task Decomposition

Each agent has a clearly defined, independent responsibility:

**Agent 1 — Research Agent (`research_agent.py`)**
- Constructs a targeted search query from product name and category
- Calls Tavily Search API and retrieves up to 5 real web results
- Returns structured `{ query, summary[] }` for downstream use

**Agent 2 — Insight Agent (`insight_agent.py`)**
- Transforms raw web text into structured marketing intelligence
- Enforces schema: minimum 5 items per category with category-aware fallbacks
- Strips markdown code fences from LLM output before JSON parsing
- Extracts: `features`, `pain_points`, `benefits`, `usp_ideas`

**Agent 3 — Copywriting Agent (`copywriting_agent.py`)**
- Generates short description (max 30 words), long description (max 100 words), and 4–6 USP bullets
- Persona-primed as an expert e-commerce copywriter
- Grounded only in Insight Agent output — no hallucinated claims
- Robust JSON parsing with schema validation and safe defaults on failure

**Agent 4 — Judge Agent (`judge_agent.py`)**
- Evaluates generated copy across 5 professional dimensions
- Returns integer score (1–5) + one-sentence reason per dimension
- Provides overall actionable feedback for improvement

> 📄 Full specs: [`task_decomposition_specifications.md`](./task_decomposition_specifications.md)

---

## ⚖️ LLM-as-Judge

The Judge Agent acts as an automated quality reviewer, evaluating copy without any human involvement:

| Dimension | What It Measures |
|---|---|
| **Clarity** | Readability and absence of jargon for a general buyer |
| **Persuasiveness** | Emotional hooks and benefit emphasis that drive consideration |
| **Differentiation** | Uniqueness vs. generic phrases — does this stand out? |
| **Feature Relevance** | Importance of highlighted features to footwear buyers |
| **Conversion Potential** | CTA strength, urgency, and clarity of value proposition |

**Scoring Rubric:** `1 = Poor` · `2 = Weak` · `3 = Adequate` · `4 = Good` · `5 = Excellent`

The judge is strictly prompted to cite evidence from the copy in each reason, preventing generic evaluations.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| LLM Inference | Groq API (`llama-3.1-8b-instant`) |
| Web Search Tool | Tavily Search API |
| UI Framework | Streamlit |
| Deployment | Railway |
| Config Management | python-dotenv |
| HTTP Client | requests |
| Language | Python 3.10+ |

---

## ✨ Key Features

- **4-agent sequential pipeline** — each agent specialised for one reasoning task
- **Real web research** via Tavily — no hallucinated product claims
- **Structured JSON outputs** with schema validation and safe fallbacks at every stage
- **LLM-as-Judge** — automated 5-dimension quality evaluation with actionable feedback
- **Live pipeline tracker** — Streamlit UI shows Research → Insights → Writing → Evaluate in real time
- **Regenerate button** — re-run the full pipeline with one click
- **Deployment-ready** — live on Railway with a public URL

---

## 🚀 Setup & Installation

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

**How to Use:**
1. Enter a **Product Name** (e.g., `Puma Softride Pro Echo Consonance`)
2. Enter the **Category** (e.g., `Walking Shoes`)
3. Click **Generate**
4. Watch the 4-stage pipeline execute in real time
5. Get your ready-to-publish product description + quality scores

---

## 🌐 Deployment

The app is deployed on **Railway** and accessible at:

🔗 **[web-production-c9ce1.up.railway.app](https://web-production-c9ce1.up.railway.app)**

### Environment Variables (set in Railway dashboard)

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key for LLM inference |
| `TAVILY_API_KEY` | Your Tavily API key for web search |

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore`.

---

## 📊 Example Output

**Input:** `Puma Softride Premier GlideKnit` | `Walking Shoes`

**Market Insights extracted:**
- **Features:** Lightweight cushioning, Engineered knit upper, One-piece construction, Slip-on closure, Soft cushioning
- **Pain Points:** Foot pain, Sweating, Poor fit, Lack of cushioning, Discomfort
- **Benefits:** All-day comfort, Reduces fatigue, Improves performance, Enhanced comfort, Provides support
- **USP Ideas:** Cutting-edge cushioning tech, Environmentally-friendly materials, Ergonomic shoe design for better fit

**Short Description:**
> *"Experience unparalleled comfort with the Puma Softride Premier GlideKnit. Enjoy all-day comfort and support on your feet."*

**Key Selling Points:**
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
| **Overall** | **4.0 / 5** | |

**Feedback:** *Consider adding more nuanced language to differentiate the product and including specific values or benefits to reinforce the CTA.*

---

## 📁 Project Structure

```
ShoeScribe-AI/
├── app.py                                  # Streamlit frontend
├── orchestrator.py                         # Pipeline coordinator
├── config.py                               # Groq client setup
├── style.css                               # Custom UI styling
├── requirements.txt                        # Python dependencies
├── Procfile                                # Railway deployment config
├── task_decomposition_specifications.md    # Full agent specs & design doc
├── agents/
│   ├── research_agent.py                   # Agent 1: Tavily web search
│   ├── insight_agent.py                    # Agent 2: Feature extraction
│   ├── copywriting_agent.py                # Agent 3: Copy generation
│   └── judge_agent.py                      # Agent 4: LLM-as-Judge
├── tools/
│   └── tavily_tool.py                      # Tavily API wrapper
└── Submission_Files/
    ├── README.md                           # Demo video link
    ├── Problem_Statement_ShoeScribe_AI.docx
    ├── task_decomposition_specifications.md
    └── Architecture_Diagram.excalidraw
```

---

## 🎥 Demo Video

📹 **Loom walkthrough:** *(link will be added before submission)*

The video covers:
- Problem statement and motivation
- End-to-end demo with a real product
- LLM-as-Judge evaluation in action

---

## 👥 Team

| Role | Member | Roll No. |
|---|---|---|
| Role A — Architect & Integrator | S. Devanshu Murthy | 11 |
| Role B — Builder & Deployer | Raman Upadhyay | 10 |

**Semester:** IV · B.Tech ECE-B
**Department:** Electronics and Communication Engineering
**Date:** 24/04/2026

---

## 📄 Documentation

- [Task Decomposition & Specifications](./task_decomposition_specifications.md) — Full agent specs, input/output schemas, error handling, and design decisions.
- [Submission Files](./Submission_Files/) — Architecture diagram, problem statement, and demo video.

---

*Built for AI Agent Systems Design course project.*
