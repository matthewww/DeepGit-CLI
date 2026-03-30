# DeepGit CLI

Deep semantic search across GitHub repositories. Designed for use by coding agents
(GitHub Copilot CLI, Claude Code, opencode, etc.) and terminal power users.

## Install

```bash
pip install .
```

This installs `deepgit` as a command on your PATH.

## Required: API keys

You need two keys — one for GitHub, one for the LLM used to expand your query into
GitHub search tags.

| Key | Where to get it | Cost |
|---|---|---|
| `GITHUB_API_KEY` | [github.com/settings/tokens](https://github.com/settings/tokens) — classic PAT, no special scopes needed | Free |
| `GROQ_API_KEY` *(recommended)* | [console.groq.com](https://console.groq.com) — sign up, create key | Free tier |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Paid |

**Quickest free setup:**
```bash
cp .env ~/.deepgit.env
# edit ~/.deepgit.env:
#   GITHUB_API_KEY=ghp_...
#   GROQ_API_KEY=gsk_...
#   DEEPGIT_LLM_MODEL=llama-3.1-8b-instant
#   DEEPGIT_LLM_BASE_URL=https://api.groq.com/openai/v1
```

**No-account local setup (Ollama):**
```bash
# Install ollama from https://ollama.com, then:
ollama pull llama3
# In ~/.deepgit.env:
#   GITHUB_API_KEY=ghp_...
#   DEEPGIT_LLM_MODEL=llama3
#   DEEPGIT_LLM_BASE_URL=http://localhost:11434/v1
```

## Options

| Flag | Default | Description |
|---|---|---|
| `query` | — | Natural language search query (required) |
| `--format text\|json` | `text` | Output format. Use `json` for machine-readable results |
| `--top N` | `10` | Number of top repositories to return |
| `--min-stars N` | `50` | Minimum star count filter |
| `--max-results N` | `100` | Max GitHub results to fetch before ranking |
| `--model MODEL` | env var | LLM model for query expansion (overrides `DEEPGIT_LLM_MODEL`) |
| `--quiet` | off | Suppress all log output (results still go to stdout) |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Results returned successfully |
| `1` | No results found |
| `2` | Error during execution |

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GITHUB_API_KEY` | **Yes** | GitHub personal access token |
| `ANTHROPIC_API_KEY` | For Claude | Anthropic API key |
| `OPENAI_API_KEY` | For OpenAI models | OpenAI API key |
| `GROQ_API_KEY` | For Groq | Groq API key |
| `DEEPGIT_LLM_MODEL` | No | Model name (e.g. `llama-3.1-8b-instant`, `claude-haiku-4-5-20251001`) |
| `DEEPGIT_LLM_BASE_URL` | No | OpenAI-compatible base URL for Groq/Ollama/LM Studio |

`.env` is loaded from the first location found (in order):

1. Current working directory (`.env`) — recommended for per-project keys
2. User home (`~/.deepgit.env`) — recommended for global install
3. Same directory as the installed `cli.py`
4. Parent of `cli.py` (dev / repo-root fallback)

## LLM providers

| Provider | Key var | `DEEPGIT_LLM_BASE_URL` | Example model |
|---|---|---|---|
| **Groq** *(recommended, free)* | `GROQ_API_KEY` | `https://api.groq.com/openai/v1` | `llama-3.1-8b-instant` |
| **Ollama** *(local, no key)* | — | `http://localhost:11434/v1` | `llama3` |
| **OpenAI** | `OPENAI_API_KEY` | *(leave unset)* | `gpt-4o-mini` |
| **Anthropic** | `ANTHROPIC_API_KEY` | *(leave unset)* | `claude-haiku-4-5-20251001` |

Pass `--model MODEL` to override inline without changing your `.env`.

## JSON output schema

```json
{
  "query": "...",
  "total_returned": 5,
  "results": [
    {
      "rank": 1,
      "title": "owner/repo",
      "url": "https://github.com/owner/repo",
      "stars": 12345,
      "scores": {
        "semantic_similarity": 0.8123,
        "cross_encoder": 8.42,
        "activity": 14.5,
        "final": 0.7841
      },
      "description": "First 400 chars of README..."
    }
  ]
}
```

## Pipeline

```
convert_searchable_query      LLM expands query to GitHub search tags
ingest_github_repos           Async GitHub API fetch (README + docs)
neural_dense_retrieval        ColBERT-v2 embeddings + BM25 + FAISS (hybrid)
cross_encoder_reranking       MiniLM cross-encoder re-ranks top 100 to top 50
threshold_filtering           Drops repos below min_stars + cross-encoder threshold
repository_activity_analysis  PR count, commit frequency, activity score
multi_factor_ranking          Weighted: xenc 35% · semantic 25% · activity 20% · stars 20%
output_presentation           Formats top-N results
```

All ML models run locally (SentenceTransformers, FAISS). No external ML API calls beyond the LLM.

## Agent usage tips

- Use `--format json --quiet` for clean machine-readable output with no log noise
- Use `--top 3` for fast single-pick selection
- Use `--min-stars 100` to bias toward established projects
- Set `DEEPGIT_LLM_MODEL` to your agent's native model to avoid a second API provider

## Origin

Forked from [zamalali/DeepGit](https://github.com/zamalali/DeepGit).

**Removed:** Gradio web UI, Docker, code quality analysis (flake8 cloning), dependency analysis, hardware filtering, decision maker, merge analysis stages.

**Changed:** LLM is now configurable via env vars (Groq/Ollama/OpenAI/Anthropic); installable as a `deepgit` CLI command via `pyproject.toml`; ranking weights rebalanced without code quality signal.
