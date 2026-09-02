#!/usr/bin/env python3
"""Finance Prompt Library — CLI runner.

Usage examples:

  # List all prompts
  python cli.py list

  # List prompts in a category
  python cli.py list --category variance

  # Preview a rendered prompt (no API call)
  python cli.py preview variance_commentary --input '{"period":"October 2025","line_items":"[...]","materiality_threshold_abs":5000,"materiality_threshold_pct":3,"tone":"executive"}'

  # Run a prompt with Anthropic
  python cli.py run pl_deep_dive --input input.json --provider anthropic --model claude-sonnet-4-6

  # Run a prompt with OpenAI
  python cli.py run board_pack_narrative --input input.json --provider openai --model gpt-4o

  # Run a prompt with Ollama (no API key needed)
  python cli.py run adverse_volume_variance --input input.json --provider openai_compatible --base-url http://localhost:11434/v1 --model llama3 --api-key ollama
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.loader import load_all_prompts, load_by_id, list_categories
from lib.renderer import coerce_inputs, resolve_computed, render_template
from lib.runner import run_prompt_from_def
from lib.providers import create_provider


def cmd_list(args: argparse.Namespace) -> None:
    prompts = load_all_prompts()
    if args.category:
        prompts = [p for p in prompts if p.get("category") == args.category]

    if not prompts:
        print("No prompts found.")
        return

    print(f"\n{'ID':<40} {'CATEGORY':<15} {'DIFFICULTY':<12} TITLE")
    print("-" * 100)
    for p in prompts:
        print(f"{p['id']:<40} {p.get('category',''):<15} {p.get('difficulty',''):<12} {p.get('title','')}")

    print(f"\nTotal: {len(prompts)} prompts")
    print(f"Categories: {', '.join(list_categories())}")


def cmd_info(args: argparse.Namespace) -> None:
    prompt = load_by_id(args.prompt_id)
    if prompt is None:
        print(f"Error: prompt '{args.prompt_id}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"ID:          {prompt['id']}")
    print(f"Title:       {prompt.get('title','')}")
    print(f"Category:    {prompt.get('category','')}")
    print(f"Difficulty:  {prompt.get('difficulty','')}")
    print(f"Version:     {prompt.get('version','')}")
    print(f"Tags:        {', '.join(prompt.get('tags',[]))}")
    print(f"\nDescription:\n  {prompt.get('description','').strip()}")

    print(f"\nInputs:")
    for inp in prompt.get("inputs", []):
        req = "required" if inp.get("required") else "optional"
        print(f"  {inp['key']:<25} {inp.get('type','text'):<10} {req}")

    if prompt.get("computed_fields"):
        print(f"\nComputed fields:")
        for k, expr in prompt["computed_fields"].items():
            print(f"  {k}: {expr}")


def cmd_preview(args: argparse.Namespace) -> None:
    prompt = load_by_id(args.prompt_id)
    if prompt is None:
        print(f"Error: prompt '{args.prompt_id}' not found.", file=sys.stderr)
        sys.exit(1)

    raw = _load_input(args)
    typed = coerce_inputs(prompt, raw)
    resolved = resolve_computed(prompt, typed)
    user_prompt = render_template(prompt, resolved)

    if args.show_system:
        print("=== SYSTEM PROMPT ===")
        print(prompt.get("system_prompt", "(none)"))
        print("\n=== USER PROMPT ===")
    print(user_prompt)


def cmd_run(args: argparse.Namespace) -> None:
    prompt = load_by_id(args.prompt_id)
    if prompt is None:
        print(f"Error: prompt '{args.prompt_id}' not found.", file=sys.stderr)
        sys.exit(1)

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    if not api_key and args.provider != "openai_compatible":
        print("Error: no API key. Set ANTHROPIC_API_KEY / OPENAI_API_KEY or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    provider = create_provider(
        provider=args.provider,
        api_key=api_key,
        base_url=args.base_url,
    )

    raw = _load_input(args)
    model = args.model or provider.default_model

    print(f"Running '{prompt['id']}' via {args.provider} / {model}…", file=sys.stderr)
    _, _, response = run_prompt_from_def(
        prompt_def=prompt,
        raw_inputs=raw,
        provider=provider,
        model=model,
        max_tokens=args.max_tokens,
    )

    if args.output:
        Path(args.output).write_text(response, encoding="utf-8")
        print(f"Response saved to {args.output}", file=sys.stderr)
    else:
        print(response)


def _load_input(args: argparse.Namespace) -> dict:
    if hasattr(args, "input") and args.input:
        if args.input.strip().startswith("{"):
            return json.loads(args.input)
        return json.loads(Path(args.input).read_text(encoding="utf-8"))
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="finance-prompt-library",
        description="Finance Prompt Library CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="List available prompts")
    p_list.add_argument("--category", help="Filter by category")

    # info
    p_info = sub.add_parser("info", help="Show prompt details")
    p_info.add_argument("prompt_id")

    # preview
    p_preview = sub.add_parser("preview", help="Render a prompt without calling the LLM")
    p_preview.add_argument("prompt_id")
    p_preview.add_argument("--input", "-i", help="JSON string or path to input JSON file")
    p_preview.add_argument("--show-system", action="store_true", help="Also print the system prompt")

    # run
    p_run = sub.add_parser("run", help="Run a prompt against an LLM")
    p_run.add_argument("prompt_id")
    p_run.add_argument("--input", "-i", help="JSON string or path to input JSON file")
    p_run.add_argument("--provider", default="anthropic", choices=["anthropic", "openai", "openai_compatible"])
    p_run.add_argument("--model", help="Model name (defaults to provider default)")
    p_run.add_argument("--api-key", help="API key (overrides env vars)")
    p_run.add_argument("--base-url", help="Base URL for openai_compatible provider")
    p_run.add_argument("--max-tokens", type=int, default=1024)
    p_run.add_argument("--output", "-o", help="Save response to this file")

    args = parser.parse_args()

    commands = {"list": cmd_list, "info": cmd_info, "preview": cmd_preview, "run": cmd_run}
    commands[args.command](args)


if __name__ == "__main__":
    main()
