---
description: Run loop engineering immediately
---

Run the loop engineering observation.

## Steps
1. Load the `loop` skill
2. Check the last execution time in `.opencode/skills/loop/last_run.txt`
3. List sessions updated in the last 7 days with `py script/loop.py --recent 7`
4. Extract observation points from the current session and recent sessions (missing rules / skill gaps / techniques)
5. Append observations to `.opencode/skills/loop/observations.md`
6. Record the current date/time in `.opencode/skills/loop/last_run.txt`

## Constraints
- Do NOT modify AGENTS.md or existing skills. Log only.
- Present improvement proposals to the user and apply only after approval.
- Do not update logs with empty observations (no empty entries).
