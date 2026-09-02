# finance-ai-library

Vendor-agnostic library of 19 finance AI prompts and skills for management accountants.
Supersedes `finance-skills-library` (7 skills) and `accounting-prompt-library` (12 prompts) — both now archived.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # add your API key(s)

# Browse + run in the browser (port 8513)
streamlit run app/streamlit_app.py --server.port 8513

# CLI
python cli.py list
python cli.py info variance_commentary
python cli.py preview pl_deep_dive --input '{"period":"Oct 2025",...}'
python cli.py run adverse_volume_variance --input input.json --provider anthropic
```

## Prompt catalogue

| Category | Count | Key prompts |
|---|---|---|
| variance | 5 | variance_commentary, waterfall_narrative, budget_vs_actual_narrative, adverse_volume_variance, favourable_price_variance |
| month_end | 4 | vat_rec, close_checklist_generator, prepayments_schedule, accruals_review |
| reporting | 6 | pl_deep_dive, budget_reforecast, margin_bridge, board_pack_narrative, kpi_commentary, rolling_forecast_assumptions |
| headcount | 2 | headcount_forecast, departmental_spend_commentary |
| costing | 2 | overhead_absorption, cost_centre_deep_dive |

## Architecture

```
finance-ai-library/
├── prompts/              # 19 YAML prompt definitions
│   ├── variance/
│   ├── month_end/
│   ├── reporting/
│   ├── headcount/
│   └── costing/
├── lib/
│   ├── loader.py         # Load/filter YAML prompt definitions
│   ├── renderer.py       # Input coercion, computed fields, template rendering
│   ├── runner.py         # Orchestrates: load → render → call → return
│   └── providers/
│       ├── base.py       # Abstract LLMProvider interface
│       ├── anthropic_provider.py
│       └── openai_provider.py  # Also covers Ollama, Groq, etc.
├── app/
│   └── streamlit_app.py  # Unified UI (port 8513)
└── cli.py                # Command-line runner
```

## Adding a new prompt

1. Create a YAML file in the appropriate `prompts/<category>/` directory
2. Follow the schema in any existing YAML (id, title, category, inputs, system_prompt, user_prompt_template)
3. Restart the Streamlit app

## YAML schema

Each YAML prompt file has these top-level fields:

- `id` — unique string identifier
- `title` — human-readable name
- `category` — one of: variance | month_end | reporting | headcount | costing
- `tags` — list of strings
- `difficulty` — beginner | intermediate | advanced
- `inputs` — list of input definitions (key, label, type, required, example)
- `computed_fields` — dict of {name: python_expression} evaluated before rendering
- `system_prompt` — the LLM system prompt (literal block scalar)
- `user_prompt_template` — template with {field_name} placeholders
- `output_spec` — output format description (optional)
- `error_handling` — dict of error cases (optional)
- `example_input` / `example_output` — for the UI "Load example" button

## Provider support

| Provider | Pass to `--provider` | Notes |
|---|---|---|
| Anthropic Claude | `anthropic` | ANTHROPIC_API_KEY |
| OpenAI GPT | `openai` | OPENAI_API_KEY |
| Ollama (local) | `openai_compatible` | base_url=http://localhost:11434/v1, api_key=ollama |
| Groq | `openai_compatible` | base_url=https://api.groq.com/openai/v1 |
| Mistral | `openai_compatible` | base_url=https://api.mistral.ai/v1 |

## Port

Streamlit: **8513**

## Superseded projects

These two projects are now archived — do not extend them:
- `finance-skills-library/` — 7 Claude Code skills (.md format, Anthropic-only)
- `accounting-prompt-library/` — 12 JSON prompts (Anthropic-only, no system prompts)

All content from both is preserved and improved in this library.
