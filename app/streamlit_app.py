"""Finance AI Library — unified Streamlit UI."""
import json
import os
import sys
from pathlib import Path

import streamlit as st

# Allow running from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.loader import load_all_prompts, list_categories
from lib.renderer import coerce_inputs, resolve_computed, render_template
from lib.runner import run_prompt_from_def
from lib.providers import create_provider

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Finance AI Library",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CATEGORY_LABELS = {
    "variance": "Variance Analysis",
    "month_end": "Month-End Close",
    "reporting": "Management Reporting",
    "headcount": "Headcount & Spend",
    "costing": "Costing",
}

DIFFICULTY_COLOURS = {
    "beginner": "#2ea043",
    "intermediate": "#d29922",
    "advanced": "#cf222e",
}


# ── Sidebar: provider config ───────────────────────────────────────────────────
def sidebar_provider() -> dict | None:
    st.sidebar.header("LLM Provider")

    provider_choice = st.sidebar.selectbox(
        "Provider",
        ["anthropic", "openai", "openai_compatible"],
        format_func=lambda x: {
            "anthropic": "Anthropic (Claude)",
            "openai": "OpenAI",
            "openai_compatible": "OpenAI-Compatible (Ollama, Groq, etc.)",
        }[x],
    )

    default_models = {
        "anthropic": "claude-sonnet-4-6",
        "openai": "gpt-4o",
        "openai_compatible": "llama3",
    }

    # Try loading API key from env first
    env_key = os.environ.get("ANTHROPIC_API_KEY", "") if provider_choice == "anthropic" else os.environ.get("OPENAI_API_KEY", "")
    api_key = st.sidebar.text_input(
        "API Key",
        value=env_key,
        type="password",
        placeholder="sk-… or leave blank for dry-run mode",
    )

    base_url = None
    if provider_choice == "openai_compatible":
        base_url = st.sidebar.text_input("Base URL", placeholder="http://localhost:11434/v1")

    model = st.sidebar.text_input("Model", value=default_models[provider_choice])
    max_tokens = st.sidebar.slider("Max tokens", 256, 4096, 1024, 128)

    has_key = bool(api_key and api_key.strip())
    if has_key:
        st.sidebar.success("API key loaded — live mode")
    else:
        st.sidebar.info("No API key — dry-run mode (preview prompt only)")

    return {
        "provider": provider_choice,
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "max_tokens": max_tokens,
        "has_key": has_key,
    }


# ── Sidebar: filter + search ───────────────────────────────────────────────────
def sidebar_filters(prompts: list[dict]) -> list[dict]:
    st.sidebar.markdown("---")
    st.sidebar.header("Browse Prompts")

    categories = ["All"] + [CATEGORY_LABELS.get(c, c.title()) for c in list_categories()]
    cat_choice = st.sidebar.selectbox("Category", categories)

    search = st.sidebar.text_input("Search", placeholder="e.g. variance, EBITDA, VAT…")

    filtered = prompts
    if cat_choice != "All":
        # Reverse-look up the key from label
        cat_key = next((k for k, v in CATEGORY_LABELS.items() if v == cat_choice), None)
        if cat_key:
            filtered = [p for p in filtered if p.get("category") == cat_key]

    if search:
        q = search.lower()
        filtered = [
            p for p in filtered
            if q in p.get("title", "").lower()
            or q in p.get("description", "").lower()
            or any(q in t.lower() for t in p.get("tags", []))
        ]

    return filtered


# ── Form builder ───────────────────────────────────────────────────────────────
def build_form(prompt_def: dict, defaults: dict | None = None) -> dict:
    """Render Streamlit input widgets for each prompt input field."""
    values = {}
    for inp in prompt_def.get("inputs", []):
        key = inp["key"]
        label = inp["label"]
        inp_type = inp.get("type", "text")
        required = inp.get("required", True)
        example = inp.get("example", "")
        default = (defaults or {}).get(key, "")

        full_label = f"{label} {'*' if required else '(optional)'}"
        widget_key = f"form_{prompt_def['id']}_{key}"

        if inp_type == "number":
            num_default = float(default) if default not in ("", None) else 0.0
            val = st.number_input(full_label, value=num_default, key=widget_key)
        elif inp_type == "textarea":
            ta_default = str(default) if default not in ("", None) else ""
            ph = str(example) if example else ""
            val = st.text_area(full_label, value=ta_default, height=120, key=widget_key, placeholder=ph)
        else:
            str_default = str(default) if default not in ("", None) else ""
            ph = str(example) if example else ""
            val = st.text_input(full_label, value=str_default, key=widget_key, placeholder=ph)

        values[key] = val

    return values


# ── Prompt card ────────────────────────────────────────────────────────────────
def render_prompt_card(p: dict, selected_id: str | None) -> bool:
    cat_label = CATEGORY_LABELS.get(p.get("category", ""), p.get("category", "").title())
    diff = p.get("difficulty", "")
    diff_colour = DIFFICULTY_COLOURS.get(diff, "#888")
    tags = " · ".join(p.get("tags", [])[:4])

    is_selected = p["id"] == selected_id
    border = "2px solid #1f77b4" if is_selected else "1px solid #333"

    st.markdown(
        f"""
        <div style="border:{border};border-radius:8px;padding:12px 16px;margin-bottom:8px;background:#1a1a1a">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <strong style="font-size:1rem">{p.get('title','')}</strong>
            <span style="color:{diff_colour};font-size:0.75rem;font-weight:600">{diff.upper()}</span>
          </div>
          <div style="color:#aaa;font-size:0.8rem;margin-top:2px">{cat_label}</div>
          <div style="color:#ccc;font-size:0.85rem;margin-top:6px">{p.get('description','')}</div>
          <div style="color:#777;font-size:0.75rem;margin-top:6px">{tags}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.button("Open →", key=f"open_{p['id']}", use_container_width=True)


# ── Main run panel ─────────────────────────────────────────────────────────────
def render_run_panel(prompt_def: dict, provider_cfg: dict) -> None:
    st.subheader(prompt_def.get("title", ""))

    cat_label = CATEGORY_LABELS.get(prompt_def.get("category", ""), "")
    diff = prompt_def.get("difficulty", "")
    diff_colour = DIFFICULTY_COLOURS.get(diff, "#888")

    col_meta1, col_meta2, col_meta3 = st.columns(3)
    col_meta1.markdown(f"**Category:** {cat_label}")
    col_meta2.markdown(f"**Difficulty:** <span style='color:{diff_colour}'>{diff}</span>", unsafe_allow_html=True)
    col_meta3.markdown(f"**Version:** {prompt_def.get('version','—')}")

    tags = prompt_def.get("tags", [])
    if tags:
        st.markdown(" · ".join(f"`{t}`" for t in tags))

    st.markdown(prompt_def.get("purpose", prompt_def.get("description", "")))

    # Expandable: system prompt
    with st.expander("System prompt", expanded=False):
        st.code(prompt_def.get("system_prompt", "(none)"), language="text")

    # Expandable: output spec
    output_spec = prompt_def.get("output_spec")
    if output_spec:
        with st.expander("Output specification", expanded=False):
            st.json(output_spec)

    st.markdown("---")

    # Form
    col_form, col_output = st.columns([1, 1])

    with col_form:
        st.markdown("**Inputs**")

        # Load example button
        example_input = prompt_def.get("example_input")
        if example_input and st.button("Load example data", key=f"load_example_{prompt_def['id']}"):
            for k, v in example_input.items():
                widget_key = f"form_{prompt_def['id']}_{k}"
                if widget_key in st.session_state:
                    st.session_state[widget_key] = v

        raw_values = build_form(prompt_def)

        run_col, preview_col = st.columns(2)
        run_clicked = run_col.button(
            "Run" if provider_cfg["has_key"] else "Run (no key — dry-run)",
            key=f"run_{prompt_def['id']}",
            type="primary",
        )
        preview_clicked = preview_col.button("Preview prompt", key=f"preview_{prompt_def['id']}")

    with col_output:
        st.markdown("**Output**")

        if run_clicked or preview_clicked:
            typed = coerce_inputs(prompt_def, raw_values)
            resolved = resolve_computed(prompt_def, typed)
            user_prompt = render_template(prompt_def, resolved)
            system_prompt = prompt_def.get("system_prompt", "")

            if preview_clicked or not provider_cfg["has_key"]:
                st.markdown("**Rendered prompt (preview)**")
                st.text_area("", value=user_prompt, height=400, key=f"preview_out_{prompt_def['id']}", disabled=True)
            else:
                with st.spinner("Calling LLM…"):
                    try:
                        provider = create_provider(
                            provider=provider_cfg["provider"],
                            api_key=provider_cfg["api_key"],
                            base_url=provider_cfg.get("base_url"),
                        )
                        _, _, response = run_prompt_from_def(
                            prompt_def=prompt_def,
                            raw_inputs=raw_values,
                            provider=provider,
                            model=provider_cfg["model"],
                            max_tokens=provider_cfg["max_tokens"],
                        )
                        st.session_state[f"response_{prompt_def['id']}"] = response
                    except Exception as e:
                        st.error(f"Error: {e}")

        # Show cached response
        response_key = f"response_{prompt_def['id']}"
        if response_key in st.session_state:
            response = st.session_state[response_key]
            st.markdown(response)
            st.download_button(
                "Download response",
                data=response,
                file_name=f"{prompt_def['id']}_response.md",
                mime="text/markdown",
                key=f"dl_{prompt_def['id']}",
            )

        # Show example output
        elif prompt_def.get("example_output"):
            with st.expander("Example output", expanded=False):
                st.markdown(prompt_def["example_output"])


# ── Main ────────────────────────────────────────────────────────────────────────
def main() -> None:
    st.title("Finance AI Library")
    st.caption("19 AI prompts for management accountants · Anthropic · OpenAI · Any compatible LLM")

    provider_cfg = sidebar_provider()

    prompts = load_all_prompts()
    filtered = sidebar_filters(prompts)

    # State: which prompt is open
    if "selected_prompt_id" not in st.session_state:
        st.session_state.selected_prompt_id = None

    # Layout: card grid on left, run panel on right (or full width when narrow)
    if st.session_state.selected_prompt_id is None:
        # Browse mode: card grid
        st.markdown(f"**{len(filtered)} prompt{'s' if len(filtered) != 1 else ''} found**")
        cols = st.columns(2)
        for i, p in enumerate(filtered):
            with cols[i % 2]:
                clicked = render_prompt_card(p, st.session_state.selected_prompt_id)
                if clicked:
                    st.session_state.selected_prompt_id = p["id"]
                    st.rerun()
    else:
        # Run mode
        if st.button("← Back to library"):
            st.session_state.selected_prompt_id = None
            # Clear cached response for this prompt
            for key in list(st.session_state.keys()):
                if key.startswith("response_"):
                    del st.session_state[key]
            st.rerun()

        prompt_def = next((p for p in prompts if p["id"] == st.session_state.selected_prompt_id), None)
        if prompt_def is None:
            st.error("Prompt not found.")
            st.session_state.selected_prompt_id = None
        else:
            render_run_panel(prompt_def, provider_cfg)


if __name__ == "__main__":
    main()
