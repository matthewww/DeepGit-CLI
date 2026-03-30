# DeepGit — TODO

## 1. Configurable AI Provider / Model
Currently hardcoded to `claude-haiku-4-5-20251001` via the LiteLLM proxy. Make the LLM
fully configurable so any provider (Anthropic, OpenAI, Groq, Ollama, etc.) and model can
be swapped without touching source code.

- [ ] Surface `DEEPGIT_LLM_MODEL` and `DEEPGIT_LLM_BASE_URL` env vars (with sensible defaults)
- [ ] Accept `--model` flag in `cli.py`
- [ ] Centralise LLM construction into a single factory (`tools/llm.py`) used by `chat.py`, `decision.py`
- [ ] Document supported providers and example `.env` snippets in `README`

---

## 2. Lean CLI-Only Fork
A separate fork of DeepGit that strips out everything not needed for terminal/agent use:
Gradio, LangGraph orchestration, the web UI, and any stages found to add little value
(informed by item 3). The result should be a focused, fast, dependency-light CLI tool.

- [ ] Complete codebase analysis (item 3) first — findings drive what gets cut
- [ ] Remove Gradio and all UI code (`app.py`, `themes/`, assets)
- [ ] Remove LangGraph; replace the graph with a plain sequential Python pipeline
- [ ] Drop stages proven low-value by A/B tests (item 4)
- [ ] Slim down `requirements.txt` to only what the core pipeline needs
- [ ] Single entrypoint: `deepgit.py` or installable `deepgit` command
- [ ] Target: `pip install` + one command to results, no server, no browser

---

## 3. Codebase Analysis — Does Every Stage Earn Its Place?
The pipeline has 11 nodes. Not all of them may be contributing meaningfully to result
quality. Map each stage's actual impact before investing further.

- [ ] Document each pipeline stage: what it does, its cost (latency + compute), and its claimed benefit
- [ ] Instrument the graph to log per-stage timing and candidate counts
- [ ] Identify stages that frequently pass through all candidates unchanged (i.e. no-ops in practice)
- [ ] Write a short findings note once data is collected

Stages to examine:
| Stage | Question |
|---|---|
| `parse_hardware` | Does hardware filtering ever fire in practice? |
| `dependency_analysis` | How often does it actually drop repos? |
| `decision_maker` | Does it ever return `1` (run code quality)? |
| `code_quality_analysis` | If rarely triggered, is it worth the overhead? |
| `merge_analysis` | Is this just a fan-in join or does it add logic? |

---

## 4. A/B Effectiveness Tests
Compare ranking quality across pipeline configurations to validate (or challenge)
the value of each stage.

- [ ] Define a small golden dataset: ~20 queries with known "ground truth" top repos
- [ ] Implement a scoring metric (e.g. NDCG@5, hit-rate@3)
- [ ] Run A/B: full pipeline vs. BM25-only vs. ColBERT-only vs. no cross-encoder
- [ ] Run A/B: with vs. without activity/quality scores in final ranking
- [ ] Produce a comparison table and commit it to `docs/`

---

## 5. CLI Tests
The `cli.py` entrypoint has no test coverage. Add tests that exercise it end-to-end
without making real network calls.

- [ ] Test `--help` output and argument parsing
- [ ] Test `--format json` produces valid, schema-conformant JSON
- [ ] Test `--format text` produces readable output
- [ ] Test exit code `1` when the graph returns no results
- [ ] Test exit code `2` on a simulated graph error
- [ ] Mock `graph.invoke` so tests are fast and offline
- [ ] Add to `run_tests.py` / CI alongside existing tests
