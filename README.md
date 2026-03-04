# Multi-Agent Content Pipeline

> **4 AI agents. One pipeline. Professional content in under 90 seconds for ~$0.02.**

**[Live Demo](https://multiagentpipeline.streamlit.app/)**

Turn any topic into polished, fact-checked content — blog posts, LinkedIn articles, or Twitter threads — powered by AWS Bedrock and orchestrated with LangGraph.

---

## How It Works

```
Topic ──→ Researcher ──→ Writer ──→ Editor ──→ Fact-Checker ──→ Published Content
            │                │          │            │
        Gathers info    Crafts draft  Polishes    Verifies claims
        from web +      with tone &   clarity,    & corrects
        local docs      format        flow        inaccuracies
```

Each agent is backed by **Claude 3.5 Haiku** on AWS Bedrock, with its behavior defined entirely in **Markdown instruction files** — not hardcoded prompts.

---

## Key Features

| Feature | What It Does |
|---------|-------------|
| **Instruction-Based Agents** | Agent behavior lives in `.md` files — edit text, not code |
| **3 Content Formats** | Blog post, LinkedIn, Twitter/X threads |
| **4 Tone Options** | Professional, casual, technical, storytelling |
| **Smart Caching** | 24h content-addressed cache with cost savings tracking |
| **Input/Output Guardrails** | PII detection, prompt injection blocking, auto-redaction |
| **Quality Scoring** | LLM-as-judge evaluation with A-F grading |
| **Cost Tracking** | Per-agent token & cost breakdown, persisted to JSON |
| **Human-in-the-Loop** | Interactive mode — review and edit between stages |
| **Resilience** | Retry with exponential backoff + circuit breaker pattern |
| **Full Observability** | Trace IDs, event timeline, millisecond-level timing |
| **Streamlit UI** | 9-tab dashboard with real-time pipeline visualization |

---

## Quick Start

### Prerequisites

- Python 3.10+
- AWS account with Bedrock access (Claude 3.5 Haiku enabled)
- [Tavily API key](https://tavily.com) (free tier available) for web search

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/multi-agent-content-pipeline.git
cd multi-agent-content-pipeline

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials and Tavily API key

# Verify Bedrock access
python test_bedrock.py
```

### Run

**Web UI (recommended):**
```bash
streamlit run app.py
# Opens at http://localhost:8501
```

**Command line:**
```python
from dotenv import load_dotenv; load_dotenv()
from src.pipeline import ContentPipeline

pipeline = ContentPipeline()
result = pipeline.run(
    topic="Recent advances in RAG systems",
    content_format="blog_post",
    tone="professional"
)
print(result['final'])
```

**Interactive mode (human review between stages):**
```python
from src.pipeline_interactive import InteractivePipeline

pipeline = InteractivePipeline()
state = pipeline.create_initial_state(topic="Your topic", content_format="blog_post", tone="professional")
# Review and edit output at each stage before continuing
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              STREAMLIT UI  (app.py)                      │
│     Automatic + Interactive modes │ 9 output tabs        │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│          PIPELINE ORCHESTRATION  (LangGraph)             │
│                                                          │
│  Input Guardrails ──→ Agent Chain ──→ Output Guardrails  │
│       (PII, injection)    │          (PII redaction)     │
│                           ▼                              │
│   ┌──────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐ │
│   │Researcher│→ │  Writer  │→ │ Editor │→ │Fact-Check│ │
│   └──────────┘  └──────────┘  └────────┘  └──────────┘ │
│         │                                                │
│   Quality Evaluator  │  Cost Tracker  │  Pipeline Cache  │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│    INSTRUCTION LAYER  (Markdown files define behavior)   │
│    base_instructions.md + {role}_instructions.md         │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│    AWS BEDROCK  (Claude 3.5 Haiku / Sonnet)              │
│    Retry handler │ Circuit breaker │ Token tracking       │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
multi-agent-content-pipeline/
│
├── instructions/                  # Agent behavior (the real "code")
│   ├── base_instructions.md       #   Core principles for all agents
│   ├── researcher_instructions.md #   Research strategy & output format
│   ├── writer_instructions.md     #   Writing style, formats & techniques
│   ├── editor_instructions.md     #   4-pass editing methodology
│   └── fact_checker_instructions.md #  Verification process & reporting
│
├── src/                           # Core framework
│   ├── agent_core.py              #   Instruction-based agent engine
│   ├── bedrock_client.py          #   AWS Bedrock API wrapper
│   ├── instruction_loader.py      #   Loads & combines .md instructions
│   ├── pipeline.py                #   4-agent LangGraph orchestration
│   ├── pipeline_interactive.py    #   Human-in-the-loop variant
│   ├── cache.py                   #   Content-addressed caching (24h TTL)
│   ├── cost_tracker.py            #   Per-call cost tracking
│   ├── guardrails.py              #   Input/output safety validation
│   ├── evaluator.py               #   LLM-as-judge quality scoring
│   ├── resilience.py              #   Retry handler & circuit breaker
│   └── tracing.py                 #   Pipeline observability & timing
│
├── tools/                         # Agent tools
│   ├── web_search.py              #   Tavily-powered web search
│   └── document_search.py         #   Local document keyword search
│
├── tests/                         # Test suite (11 modules)
├── app.py                         # Streamlit web UI
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment config template
```

---

## The Innovation: Instruction-Based Agents

Each agent's entire behavior is defined in **Markdown files** — not Python code.

```
instructions/
├── base_instructions.md           → Shared principles for ALL agents
├── researcher_instructions.md     → "Search documents first, then web..."
├── writer_instructions.md         → "Use analogies, adapt tone..."
├── editor_instructions.md         → "4-pass editing: structure → paragraph → sentence → copy"
└── fact_checker_instructions.md   → "Verify every claim, assign confidence levels..."
```

**Why this matters:**

- **Non-developers can improve agents** — just edit a `.md` file
- **No redeployment needed** — save the file, run the pipeline
- **Version-controlled expertise** — track changes with git
- **Rapid iteration** — tweak instructions in seconds, not hours

**Example — want stricter fact-checking?**
```diff
  ## Quality Checklist
  - [ ] At least 3-5 credible sources
+ - [ ] Prioritize peer-reviewed papers
+ - [ ] Reject sources older than 2 years
```

Save. Done. Every future run uses the updated behavior.

---

## Content Formats & Tones

| Format | Output | Length |
|--------|--------|--------|
| **Blog Post** | Hook → Context → 3-5 sections → Takeaways → Conclusion | 800-1500 words |
| **LinkedIn** | Hook → Core insight → Bullet points → Engagement question | 300-500 words |
| **Twitter/X** | 5-7 tweet thread with hook → insights → CTA | 280 chars/tweet |

| Tone | Style |
|------|-------|
| **Professional** | Authoritative, data-driven, industry language |
| **Casual** | Conversational, relatable, accessible |
| **Technical** | Deep-dive, precise terminology, code examples |
| **Storytelling** | Narrative arc, analogies, human-centered |

---

## Safety & Guardrails

**Input validation:**
- PII detection (emails, phone numbers, SSNs, credit cards, IPs)
- Prompt injection detection
- Input length limits

**Output protection:**
- Automatic PII redaction before content is returned
- Safety status reported per run

---

## Cost Breakdown

| Stage | Avg Cost | What It Does |
|-------|----------|-------------|
| Researcher | ~$0.003 | Web + document search, synthesis |
| Writer | ~$0.006 | Draft creation with format/tone |
| Editor | ~$0.005 | 4-pass quality improvement |
| Fact-Checker | ~$0.006 | Claim verification + corrections |
| Evaluator | ~$0.001 | Quality scoring |
| **Total** | **~$0.02** | **Full pipeline per piece** |

**At scale:**
- 100 pieces → ~$2
- 1,000 pieces → ~$20
- With caching → **30-40% savings** on repeated topics

**Model pricing (per 1M tokens):**
| Model | Input | Output |
|-------|-------|--------|
| Claude 3.5 Haiku (default) | $0.80 | $4.00 |
| Claude 3.5 Sonnet (optional) | $3.00 | $15.00 |

---

## Configuration

### Environment Variables

```bash
# AWS Bedrock (required)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1

# Model selection (optional — defaults to Haiku)
BEDROCK_MODEL=us.anthropic.claude-3-5-haiku-20241022-v1:0

# Web search (required for Researcher agent)
TAVILY_API_KEY=tvly-your_api_key
```

### Switch to Sonnet (higher quality, higher cost)

```bash
BEDROCK_MODEL=us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

---

## Testing

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run a specific test
pytest tests/test_pipeline.py

# With coverage
pytest tests/ --cov=src --cov=tools
```

**Test coverage includes:** agent core, Bedrock client, instruction loader, pipeline, interactive pipeline, cache, guardrails, evaluator, resilience, and tracing.

---

## Streamlit UI

The web interface provides **9 output tabs:**

1. **Final Content** — Ready-to-publish output
2. **Fact-Check Report** — Verification details
3. **Research Notes** — Raw research output
4. **Draft** — Writer's first draft
5. **Edited Version** — Post-editor content
6. **Cost Breakdown** — Per-agent token & cost details
7. **Quality Score** — Relevancy, faithfulness, grade
8. **Safety Report** — Guardrail scan results
9. **Pipeline Trace** — Event timeline with timing

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | AWS Bedrock — Claude 3.5 Haiku / Sonnet |
| **Orchestration** | LangGraph + LangChain |
| **Web Search** | Tavily API |
| **UI** | Streamlit |
| **AWS SDK** | boto3 |
| **Validation** | Pydantic |
| **Config** | python-dotenv |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ResourceNotFoundException` | Enable Claude 3.5 Haiku in AWS Bedrock console |
| `Context length exceeded` | Reduce `max_tokens` in `src/pipeline.py` |
| High costs | Check `project3_costs.json`, switch to Haiku, reduce tokens |
| Slow runs (~90s) | Normal — 4 sequential LLM calls at ~15-20s each |
| No search results | Verify `TAVILY_API_KEY` in `.env` |

---

## License

MIT License — use and modify freely.

---

**Built with AWS Bedrock + LangGraph + Streamlit**
