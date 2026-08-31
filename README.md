# Loop Engineering Skill for opencode

A self-growth observation system **for opencode**. It reviews session logs to find improvement points — missing rules, skill gaps, and useful techniques. All proposals require **human approval** (human-in-the-loop). Trigger manually by typing `/loop`. Run **daily or at least weekly** for best results.

**Version: 1.0.0**

## What it does

Type `/loop` to run loop engineering. The agent will:

1. **Inventories** your existing skills (`.opencode/skills/`)
2. **Reviews** the current session + last 7 days of sessions
3. **Extracts** observation points:
   - Missing rules (user corrections that exposed undocumented behavior)
   - Skill gaps (situations existing skills don't cover)
   - Techniques (workflows worth remembering)
4. **Logs** findings with status tracking (⏳proposed → ✅applied / ❌rejected)
5. **Presents** important proposals for your approval

## Installation

Ask opencode to install this skill:

```
"Install loop engineering from https://github.com/hogehogemon/opencode-loop"
```

The agent will clone the repo and copy:
- `skills/loop/` → `.opencode/skills/loop/`
- `commands/loop.md` → `.opencode/commands/loop.md`

## Usage

### Manual
Type `/loop` or ask the agent to "run loop engineering".

### CLI (direct search)
```bash
py .opencode/skills/loop/loop.py --recent 7                    # list recent sessions
py .opencode/skills/loop/loop.py --recent 7 --dir my-project   # filter by project
py .opencode/skills/loop/loop.py "user correction"             # search session content
py .opencode/skills/loop/loop.py --version                     # show installed version
```

### Check for updates
Check https://github.com/hogehogemon/opencode-loop/releases for the latest version.

## File structure

```
.opencode/
├── skills/
│   └── loop/
│       ├── SKILL.md              # skill definition
│       ├── loop.py               # session search tool
│       ├── last_run.txt          # last execution timestamp (auto-generated)
│       └── observations.md       # proposals + techniques (auto-generated)
└── commands/
    └── loop.md                   # /loop command definition
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
