# Holiday Hardening Log

Unattended multi-day hardening work on `finance-ai-library` while Keyaan is away.
Each entry is one session. Read this whole file before doing anything — it's the
only memory carried between sessions.

---

## Session 1 — 2026-09-07 (Sunday)

**Branch:** `claude/holiday-hardening` created fresh from `main` (no prior branch or PR
existed — this is genuinely session 1, not a resumption).

### Findings before starting any changes

The library was already in noticeably good shape. Ran a full schema audit and a
render/CLI smoke test across all 19 prompts before touching anything:

- 17 of 19 YAML files fully match the CLAUDE.md schema (all required + optional fields
  present, `id` matches filename, category/difficulty valid, `example_input` covers every
  required input with no stray keys).
- All 19 prompts render cleanly via `lib/renderer.py` with zero leftover `{placeholder}`
  text, and all 19 pass `cli.py list / info / preview` with no runtime errors.
- CLAUDE.md's documented category breakdown (variance 5, month_end 4, reporting 6,
  headcount 2, costing 2 = 19) matches the actual `prompts/` tree exactly — no drift to
  tidy.

### Work done this session

1. **Schema validation (scope item 1):** audited all 19 YAMLs programmatically against
   the CLAUDE.md schema. Only gap found: `prompts/month_end/vat_rec.yaml` and
   `prompts/reporting/margin_bridge.yaml` are both missing `example_output`. **Did not
   fill these in** — see "Flagged for Keyaan" below, this is a genuine conflict in my
   instructions, not a bug I felt safe resolving unilaterally.
2. **Test suite (scope item 2):** rewrote `tests/test_library.py` to cover all 19 prompts
   (previously only 5 had render coverage). Added: full schema-field assertions per YAML,
   `example_input` completeness checks, computed-field evaluation checks, and a
   `StubProvider` (subclass of `lib.providers.base.LLMProvider`) used to exercise
   `run_prompt_from_def` end-to-end for every prompt with zero network calls. 140 tests
   total, all passing (`python -m pytest tests/test_library.py -q`).
3. **CLI exercise (scope item 3):** ran `list`, `info`, and `preview` programmatically
   against all 19 prompts (now also codified as parametrized tests). No runtime bugs
   found — no broken template placeholders, no failing `computed_fields` expressions.
4. **Bug fixes (scope item 4):** none needed — nothing found that was a genuine
   structural/code bug rather than a design choice or a documentation gap (see flags
   below).
5. **README/CLAUDE.md tidy (scope item 5):** counts don't drift, so no edits needed there.
   Separately noticed the repo has **no `README.md` at all** — flagged below rather than
   authored, since it's a portfolio-positioning/voice decision.
6. **Prompt quality experiment (scope item 6):** done. Wrote
   `experiments/prompt_quality_comparison.md` covering `variance_commentary` (variance),
   `vat_rec` (month_end), and `board_pack_narrative` (reporting) — 3 tiers × 2
   (raw/skill) × 3 prompts = 18 outputs, all generated directly by me and clearly
   labelled, per the instruction that there's no live API key in this environment. Short
   version of the finding: the hypothesis holds in a *moderate* form (skill scaffolding
   beats a weak raw prompt on structure/discipline/safety, and for the compliance-shaped
   `vat_rec` prompt actively catches a risk-rating a generic LLM under-called) but not in
   its strong form — an amazing raw prompt with real facts in it still beats a weak skill
   input, because scaffolding can't invent facts nobody supplied. Full analysis and all
   18 outputs are in the experiment file.

### Flagged for Keyaan (not resolved autonomously — need your judgment)

1. **`vat_rec.yaml` / `margin_bridge.yaml` missing `example_output`.** Your task
   instructions for item 1 explicitly call out fixing missing `example_output` as part of
   schema validation, but the HARD LIMITS in the same instructions say never to invent
   business/accounting content for a prompt's real system_prompt/template/output in items
   1–5. Writing a realistic `example_output` for these two *is* inventing accounting
   narrative content (fabricated numbers-in-prose, same as the other 17 prompts' existing
   `example_output` fields). I judged the HARD LIMIT should win and left both fields
   untouched rather than guess which instruction you'd want to override. Worth noting:
   `app/streamlit_app.py` shows `example_output` is only used for a "preview what this
   looks like" panel — the "Load example data" button itself only depends on
   `example_input`, which both files already have in full. So functionally nothing is
   broken; this is a content gap, not a bug. If you want these filled in, say so (or
   write them yourself — you're the one whose name is on the `author:` field on every
   other one).
2. **No `README.md` in the repo root.** CLAUDE.md is comprehensive (quick start, prompt
   catalogue, architecture, schema, providers) but doesn't render on the GitHub repo
   homepage the way a README.md would. For a "flagship portfolio project" this seems
   worth having, but authoring one is a positioning/voice decision I didn't want to make
   unprompted mid-hardening-pass — happy to draft one next session (could largely mirror
   CLAUDE.md) if you confirm you want it, or if it's intentional (e.g. you're relying on
   CLAUDE.md being the canonical doc) just say so and I'll close this out.
3. **`lib/providers/anthropic_provider.py`** (`_get_client`, lines ~23-34) has a hardcoded
   personal path reference: it tries to import `TrackedAnthropic` from
   `~/Claude/intelligence-hub` before falling back to the plain `anthropic.Anthropic`
   client. This is functionally harmless — the `except Exception` fallback works fine for
   anyone without that path — but it's a private/personal path baked into a public
   portfolio repo's source, which could look odd to a reviewer reading the code (and
   reveals a bit about your personal tooling setup). I didn't touch it since it's clearly
   a deliberate convenience for your own cost-tracking, not a bug. Flagging in case you
   want to strip it, gate it behind an env var, or leave it — your call.

### State for next session

- All 19 YAMLs, `lib/`, `cli.py`, `app/streamlit_app.py`: audited, no code bugs found.
- `tests/test_library.py`: full 19-prompt coverage added, all passing.
- `experiments/prompt_quality_comparison.md`: written, not wired into any production code.
- Scope items 1–6 are all **substantively complete** after one session — the codebase was
  already close to launch-ready going in, so there wasn't a backlog of bugs to work
  through. There are three flagged items above still open (all judgment calls for
  Keyaan, not code bugs), plus whatever CI feedback comes back on the PR.
- **Next session should:** re-run `python -m pytest tests/test_library.py -q` to confirm
  nothing regressed, check whether Keyaan has responded to any of the three flags above
  (act on them if so — e.g. if he asks for `example_output` to be added, or a README
  drafted), check the PR for review comments or CI failures, and otherwise there isn't
  fresh scope to invent — do not add features or expand scope beyond what's listed at the
  top of this file's originating task. If genuinely nothing changed and nothing needs
  doing, say so briefly in this log rather than manufacturing busywork.
