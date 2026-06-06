# Gemini Agent Instructions

Purpose
-------
Provide explicit, short guidance for agents when the `gemini` argument is supplied by the user.

Quick rules
-----------
- Keep responses concise and numbered.
- Always show environment activation and dependency commands before executing runs.
- Present reproducible commands and estimate runtimes for analysis tasks.
- Ask for confirmation before any state-changing command (DB writes, data replacement, commits).

Minimal checklist for `gemini` runs
----------------------------------
1. Summarize the goal in 1 sentence.
2. List required environment steps (venv activation, deps install).
3. Describe files to be changed and why; offer an incremental plan.
4. Run non-destructive checks (lint, tests) locally and report results.
5. If user approves, perform stateful steps and report outputs.

Example usage
-------------
Run locally with explicit activation and a dry-run flag where applicable:

```powershell
mutual\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py --dry-run
```

Notes for agents
----------------
- Prefer creating a small instruction file or skill and request explicit user confirmation before running commands that modify `data/` or the DB.
- Keep messages short and actionable; surface only the most relevant commands and diffs.
