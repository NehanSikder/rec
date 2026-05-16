# rec — Production Pipeline Manager

A desktop tool for managing podcast and YouTube video production workflows.
Clone from GitHub, run `python run.py`, and the app launches.

---

## What It Is

A production pipeline manager. Not an editor — it orchestrates the tools you already use.
One session = one piece of content. Sessions move through configurable stages.
Each stage contains actions that can be run, undone, and marked complete.

The app never implements features itself. Every action delegates to an external tool
via a shell command, script, or file open. The YAML config is where users wire in their own tools.

---

## Distribution

- Clone repo from GitHub
- Run `python run.py` — auto-installs deps, launches app
- Requires Python 3.10+ on Mac

---

## UI

- **CustomTkinter** — dark/light mode, minimalist look
- Progress bar across the top showing stage completion status
- Stage body with action list and status icons
- Buttons: Run, Undo, Mark Complete, Skip, Back, Next
- Each session opens in its own window
- Session picker is the launch screen

### Progress Bar (Option B)

```
●━━━━━━━━━━●━━━━━━━━━━◐━━━━━━━━━━○━━━━━━━━━━○
Record     Edit      Mix        Export     Publish
 done       done      active      todo       todo
```

- Green filled node = completed stage
- Blue filled node = active stage
- Grey empty node = todo stage

### Action List

```
─── Mix ──────────────────────────────────────
✓  Noise Reduction
✓  Normalize Loudness
○  Balance Levels          [Run]
```

---

## Sessions

- Stored as JSON at `~/.rec/sessions/`
- Contains: metadata, current stage, action statuses, command history
- Persists between app restarts
- Session picker shown on launch (new or load existing)

---

## Stages (Default Pipeline)

```
Record → Edit → Mix → Export → Publish
```

Defined in `stages.yaml` — configurable without touching code.
User can override defaults via `~/.rec/stages.yaml`.
Stages can be added, removed, or reordered by editing the YAML.

Default config ships with all actions typed as `manual` — no shell commands.
Users wire in their own commands later by editing the YAML.

---

## Action Types

| Type | Behavior |
|---|---|
| `shell` | Runs a terminal command |
| `open` | Opens file in default app |
| `script` | Runs a Python script |
| `manual` | User marks done themselves |
| `prompt` | Collects input before proceeding |

---

## State & Undo

- Every executed action is logged to a command history
- Actions can be undone (delete output file, reset status)
- Undo is cross-stage — can revert an entire stage backward through the pipeline
- Stages can be skipped — marked as `skipped` status, pipeline moves forward

---

## File Structure

```
rec/
├── run.py                   # bootstrap: install deps + launch
├── stages.yaml              # default pipeline config
├── requirements.txt
├── config/
│   ├── models.py            # Stage, Action, PipelineConfig dataclasses
│   └── loader.py            # reads stages.yaml, supports user override
├── core/
│   ├── session.py           # Session model + JSON persistence
│   ├── state_machine.py     # stage advance, revert, status tracking
│   ├── action_runner.py     # executes actions by type
│   └── undo_stack.py        # command history + inverse operations
└── app/
    ├── main.py              # app entry point
    ├── components/
    │   ├── progress_bar.py  # top progress bar with stage nodes
    │   ├── action_list.py   # stage body with action rows
    │   └── session_picker.py # launch screen
    └── windows/
        └── main_window.py   # root window layout
```

---

## MVP Breakdown

### MVP 1 — Headless Core
No UI. Sessions, stages, and actions work from the terminal.

- [x] 1.1 Project structure + requirements.txt
- [x] 1.2 stages.yaml (default pipeline, all actions typed as manual, no shell commands)
- [ ] 1.3 Config models + loader (Stage, Action, PipelineConfig dataclasses)
- [ ] 1.4 Session model + JSON persistence (~/.podcast-tool/sessions/)
- [ ] 1.5 Stage state machine (advance, revert cross-stage, skip)
- [ ] 1.6 Action runner (manual, shell, open, script, prompt)
- [ ] 1.7 Undo stack (cross-stage, logs inverse operations)

### MVP 2 — UI Shell
Visual layer wired to the core. Buttons stubbed, no real action execution yet.

- [ ] 2.1 App window + layout skeleton (CustomTkinter)
- [ ] 2.2 Progress bar component — colored nodes + connecting line
- [ ] 2.3 Stage body + action list with status icons (✓ done / ● active / ○ todo)
- [ ] 2.4 Button row: Run, Mark Complete, Skip, Undo, Back, Next
- [ ] 2.5 Session picker screen (launch screen — new session or load existing)
- [ ] 2.6 Each session opens in its own window

### MVP 3 — Full Integration
Wire UI to core. Everything works end to end.

- [ ] 3.1 Wire Run button → action runner
- [ ] 3.2 Wire Mark Complete + Skip → stage state machine
- [ ] 3.3 Wire Undo → undo stack (cross-stage)
- [ ] 3.4 Wire Back/Next → stage navigation, progress bar updates live
- [ ] 3.5 Persist session state to JSON on every action
- [ ] 3.6 run.py bootstrap (auto-installs deps, launches app)
