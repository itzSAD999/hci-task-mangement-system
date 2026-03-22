# hci-task-mangement-system

## TaskFlow — Premium Task Manager

**CSM 357 Human-Computer Interaction | KNUST**

A modern, premium task management application built with Python and CustomTkinter, designed and evaluated against 7 core HCI principles.

### HCI Principles Applied

| # | Principle | Implementation |
|---|-----------|----------------|
| 1 | **Efficiency** | Keyboard shortcuts for all actions, auto-dismissing tooltips |
| 2 | **Effectiveness** | Left-aligned task hierarchy, actionable status bar, clear filtering |
| 3 | **Usability** | Collapsible sidebar, inline calendar picker, integrated scroll navigation |
| 4 | **Functionality** | Full CRUD, undo/redo, date validation, theme persistence |
| 5 | **Learnability** | Interactive 20-second user guide with progress indicator |
| 6 | **Memorability** | Consistent design system across light/dark themes |
| 7 | **Satisfaction** | Smooth theme animations, hover micro-interactions, premium aesthetics |

Plus **13 Core UI/UX Heuristics**: Structure, Simplicity, Visibility, Feedback, Tolerance, Reuse, User Control, Consistency, Continuity, Hierarchy, Accessibility, Precision, Aesthetics.

### Features

- ✅ **Mark as Done**: Interactive completion toggle with visual feedback (slanted text, muted colors)
- 📌 **Task filtering**: Today / Upcoming / All / Completed
- 📅 **Calendar popup** for deadline selection (DD/MM format)
- ✏️ **Edit task popup** for focused modifications
- 🗑️ **Undo support** for accidental deletions
- ⌨️ **Full keyboard shortcut coverage** with tooltip discoverability
- ❓ **Interactive User Guide** accessible via the `?` button

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Focus task input |
| `Ctrl+P` | Open calendar picker |
| `Ctrl+S` | Toggle sidebar |
| `Ctrl+T` | Toggle dark/light mode |
| `Ctrl+Z` | Undo last delete |
| `Ctrl+X` | Clear all tasks |
| `E` | Edit selected task |
| `Del` | Delete selected task |
| `1` / `2` / `3` / `4` | Filter: Today / Upcoming / All / Completed |

### Requirements

```
pip install customtkinter
```

### Run

```
python task_manager.py
```
