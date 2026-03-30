#!/usr/bin/env python3
"""
DeepGit CLI — agent-friendly interface to the DeepGit agentic search workflow.

Usage:
    python cli.py "LLM fine-tuning with LoRA"
    python cli.py "RAG pipelines" --format json --top 5
    python cli.py "YOLO object detection" --min-stars 200 --quiet

Exit codes:
    0  Results returned successfully
    1  No results found
    2  Error during execution
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path

import truststore
truststore.inject_into_ssl()

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Silence all loggers when --quiet is requested (must happen before agent import)
def _configure_logging(quiet: bool) -> None:
    level = logging.CRITICAL if quiet else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    if quiet:
        logging.disable(logging.CRITICAL)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deepgit",
        description="Deep semantic search across GitHub repositories.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "query",
        help='Natural language search query, e.g. "LLM fine-tuning with LoRA on CPU"',
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. Use 'json' for machine-readable results. (default: text)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        metavar="N",
        help="Number of top repositories to return. (default: 10)",
    )
    parser.add_argument(
        "--min-stars",
        type=int,
        default=None,
        metavar="N",
        help="Minimum star count filter. (default: 50 per agent config)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=None,
        metavar="N",
        help="Maximum GitHub results to fetch before ranking. (default: 100)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress all log output. Results still go to stdout.",
    )
    return parser


def _format_json(query: str, result: dict, top: int) -> str:
    repos = result.get("final_ranked_data", [])[:top]
    output = {
        "query": query,
        "total_returned": len(repos),
        "results": [
            {
                "rank": rank,
                "title": repo.get("title", ""),
                "url": repo.get("link", ""),
                "stars": repo.get("stars", 0),
                "scores": {
                    "semantic_similarity": round(float(repo.get("semantic_similarity", 0)), 4),
                    "cross_encoder": round(float(repo.get("cross_encoder_score", 0)), 4),
                    "activity": round(float(repo.get("activity_score", 0)), 4),
                    "code_quality": repo.get("code_quality_score", 0),
                    "final": round(float(repo.get("final_score", 0)), 4),
                },
                "description": repo.get("combined_doc", "")[:400],
            }
            for rank, repo in enumerate(repos, 1)
        ],
    }
    return json.dumps(output, indent=2)


def _format_text(result: dict, top: int) -> str:
    repos = result.get("final_ranked_data", [])[:top]
    if not repos:
        return "No results found."
    lines = ["\n=== DeepGit Results ===\n"]
    for rank, repo in enumerate(repos, 1):
        lines.append(f"#{rank}  {repo.get('title', 'Unknown')}")
        lines.append(f"     URL:    {repo.get('link', '')}")
        lines.append(f"     Stars:  {repo.get('stars', 0):,}")
        lines.append(
            f"     Scores: semantic={repo.get('semantic_similarity', 0):.3f}  "
            f"xenc={repo.get('cross_encoder_score', 0):.3f}  "
            f"activity={repo.get('activity_score', 0):.2f}  "
            f"final={repo.get('final_score', 0):.3f}"
        )
        snippet = repo.get("combined_doc", "")[:160].replace("\n", " ")
        lines.append(f"     Desc:   {snippet}...")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    _configure_logging(args.quiet)

    # Build configurable overrides for AgentConfiguration
    configurable: dict = {}
    if args.min_stars is not None:
        configurable["min_stars"] = args.min_stars
    if args.max_results is not None:
        configurable["max_results"] = args.max_results

    run_config = {"configurable": configurable} if configurable else {}

    try:
        # Import after logging is configured so library noise respects --quiet
        from agent import AgentStateInput, graph

        initial = AgentStateInput(user_query=args.query)
        result = graph.invoke(initial, config=run_config)

        repos = result.get("final_ranked_data", [])
        if not repos:
            print("No results found.", file=sys.stdout)
            return 1

        if args.format == "json":
            print(_format_json(args.query, result, args.top))
        else:
            print(_format_text(result, args.top))

        return 0

    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        if not args.quiet:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
