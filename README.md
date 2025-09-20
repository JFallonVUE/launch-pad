# LaunchPad AI

Production-grade decisioning for VUE services + behavioral bias plans. Two modes:
- **Lighting** (15 Qs) → JSON only
- **Deep Dive** (40–50 Qs) → JSON + .docx “Proposal + Listing Lingo Pack”

Grounded on your VUE catalog & bias playbook (RAG). Final selections + rationales are LLM-driven.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...            # required for real LLM/embeddings
export PUBLIC_BASE_URL=http://localhost:8000
make run
