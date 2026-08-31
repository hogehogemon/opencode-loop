---
name: loop
description: Use at session start to run the loop-engineering self-growth observation (when last_run.txt is older than 24h). Observes the current session and appends findings to observations.md. Does NOT modify AGENTS.md or any skill without user approval.
---

# Loop Engineering (Session Observation Skill)

## Procedure

### Step 0 — Inventory existing skills
List all skill names and descriptions under `.opencode/skills/`.
Use this inventory as the baseline for gap detection.
If no skills exist, treat AGENTS.md as the sole knowledge base.

### Step 1 — Review current + recent sessions
Observe the following:
- **Current session** (the entire conversation; focus on user corrections, changes, and instructions)
- **Recent sessions**: run `py script/loop.py --recent 7 --dir <project-dir> --compact` to list sessions updated in the last 7 days.
  - Use `--dir` to exclude other projects
  - Use `--compact` for one-line-per-session output
  - To see details, re-run without `--compact`, or search with `py script/loop.py "<query>"`

Extract these observation points from each session:
1. **Missing rules** — user corrections that exposed rules not documented in AGENTS.md or skills.
2. **Skill gaps** — situations or procedures that existing skills did not cover.
3. **Techniques** — useful tool usage or workflows worth remembering.
4. **Stray files at repo root** — check for unexpected directories/files at the repository root. If found, delete them and log which tool/agent created them.

### Step 2 — Append to observations.md

Append to `.opencode/skills/loop/observations.md`:

```markdown
## YYYY-MM-DD

### Observations
- [Skill/AGENTS.md section name] Observation (specific, with examples) → Proposal: concrete fix

### Techniques
- technique name: description (when/how it was used)
```

- Every observation MUST include "→ Proposal: ..." with a concrete action
- Create the file if it doesn't exist
- Do not update if there are no observations (no empty entries)
- **Status markers**: use `⏳proposed` when adding. Change to `✅applied (date)` when approved, or `❌rejected` if rejected.
- **Follow up**: each run, check for `⏳proposed` entries older than 1 week → re-prompt user.
- **Skill classification** (3 choices before registering):
  1. **Procedure** (steps needed each time) → skill candidate
  2. **Rule** (always/never do X) → AGENTS.md proposal, not a skill
  3. **Uncertain / rare** → defer

### Step 2.5 — Present proposals
- Present the **most important** proposals to the user
- Format: "I found these → ①... ②... Apply?"

### Step 3 — Record execution time
Write the current datetime to `.opencode/skills/loop/last_run.txt` (format: `YYYY-MM-DDTHH:MM:SS`)

## Constraints
- Do NOT modify AGENTS.md or existing skills. Log only.
- Present proposals to the user; apply only after explicit approval.
- Do not run repeatedly in the same session.
- Only observe sessions from `loop.py --recent 7` results.
