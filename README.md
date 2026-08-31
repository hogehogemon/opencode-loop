# Loop Engineering for opencode

A self-growth observation system **for opencode**. It reviews session logs to find improvement points — missing rules, skill gaps, and useful techniques. All proposals require **human approval** (human-in-the-loop). Trigger manually by typing `/loop`. Run **daily or at least weekly** for best results.

## What it does

At session start (or via `/loop` command), loop engineering:

1. **Inventories** your existing skills (`.opencode/skills/`)
2. **Reviews** the current session + last 7 days of sessions
3. **Extracts** observation points:
   - Missing rules (user corrections that exposed undocumented behavior)
   - Skill gaps (situations existing skills don't cover)
   - Techniques (workflows worth remembering)
4. **Logs** findings with status tracking (⏳proposed → ✅applied / ❌rejected)
5. **Presents** important proposals for your approval

## Installation

Ask opencode to install this skill. It will copy the files to the correct locations:

```
"Install loop engineering for opencode"
```

The agent will set up:
- `script/loop.py`
- `.opencode/skills/loop/SKILL.md`
- `.opencode/commands/loop.md`

## Usage

### Manual
Type `/loop` or ask the agent to "run loop engineering".

### CLI (direct search)
```bash
py script/loop.py --recent 7                    # list recent sessions
py script/loop.py --recent 7 --dir my-project   # filter by project
py script/loop.py "user correction"             # search session content
```

## File structure

After installation, loop engineering creates:

```
.opencode/skills/loop/
├── SKILL.md              # skill definition
├── last_run.txt          # last execution timestamp
└── observations.md       # proposals + techniques (auto-generated)
```

Add `last_run.txt` and `observations.md` to `.gitignore`.

## How observations work

Each run produces observations in these categories:

| Category | Example | Action |
|----------|---------|--------|
| Missing rule | "User said 'don't create files without asking'" | Log as AGENTS.md proposal |
| Skill gap | "No skill for handling MCP timeouts" | Log as skill candidate |
| Technique | "Used @explore for parallel KBA search" | Log in techniques section |

### Status lifecycle

```
⏳proposed → ✅applied (date)
           → ❌rejected
```

Pending proposals older than 1 week are re-prompted automatically.

### Skill classification

Before registering a new skill, classify it:

1. **Procedure** (steps needed each time) → skill candidate
2. **Rule** (always/never do X) → AGENTS.md proposal, not a skill
3. **Uncertain / rare** → defer

## Requirements

- Python 3.10+
- opencode installed (uses its SQLite DB at `~/.local/share/opencode/opencode.db`)
- No external dependencies (stdlib only: sqlite3, json, argparse)

## License

MIT
