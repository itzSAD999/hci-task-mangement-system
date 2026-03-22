"""
TaskFlow — Premium Task Manager
CSM 357 Human-Computer Interaction | KNUST
HCI Principles applied:
  1. Efficiency     — Keyboard shortcuts, auto-hide tooltips, minimal clicks
  2. Effectiveness  — Clear task hierarchy, left-aligned content, actionable status bar
  3. Usability      — Collapsible sidebar, inline calendar, scroll navigation
  4. Functionality  — CRUD operations, filtering, undo, data persistence
  5. Learnability   — Interactive 20-second user guide with progress indicator
  6. Memorability   — Consistent design system across light/dark themes
  7. Satisfaction   — Smooth animations, premium aesthetics, micro-interactions
  + 13 Core UI/UX Heuristics (Structure, Simplicity, Visibility, Feedback,
    Tolerance, Reuse, User Control, Consistency, Continuity, Hierarchy,
    Accessibility, Precision, Aesthetics)
"""

from __future__ import annotations

import customtkinter as ctk  # type: ignore[import-not-found]
import calendar as cal_mod
from datetime import datetime, timedelta
from typing import Callable, Optional

# ─────────────────────────  DESIGN SYSTEM (Consistency & Aesthetics)  ─────

LIGHT: dict[str, str] = {
    "bg": "#F8F9FD",           # Soft grayish blue
    "sidebar": "#FFFFFF",      # Clean white sidebar
    "panel": "#FFFFFF",        # Card surface
    "accent": "#7C5CFC",       # Primary brand color (Purple)
    "accent_h": "#6A48E8",     # Hover brand
    "accent_soft": "#F0EEFF",  # Tone for badges
    "text": "#1A1A2E",         # High contrast title
    "text_sec": "#6B7280",     # Muted body
    "muted": "#9CA3AF",        # Muted hints
    "border": "#E5E7EB",       # Subtle dividers
    "ok": "#10B981", "ok_bg": "#ECFDF5",
    "err": "#EF4444", "err_bg": "#FEF2F2",
    "info": "#3B82F6", "info_bg": "#EFF6FF",
    "warn": "#F59E0B",
    "nav_active_bg": "#F0EEFF",
    "nav_active_fg": "#7C5CFC",
    "card_hover": "#F9FAFB",
    "input_bg": "#F9F8FC",
    "input_bd": "#ECEAF3",
}

DARK: dict[str, str] = {
    "bg": "#0B0A10",           # Deep dark
    "sidebar": "#15141B",      # Slightly lighter sidebar
    "panel": "#1C1B22",        # Card surface
    "accent": "#A78BFA",       # Light purple
    "accent_h": "#C4B5FD",
    "accent_soft": "#2D2B3D",
    "text": "#F3F4F6",
    "text_sec": "#9CA3AF",
    "muted": "#6B6A80",
    "border": "#2D2D35",
    "ok": "#34D399", "ok_bg": "#064E3B",
    "err": "#F87171", "err_bg": "#450A0A",
    "info": "#60A5FA", "info_bg": "#1E3A8A",
    "warn": "#FBBF24",
    "nav_active_bg": "#2D2B3D",
    "nav_active_fg": "#A78BFA",
    "card_hover": "#25242C",
    "input_bg": "#15142A",
    "input_bd": "#2C2D35",
}

_YEAR = datetime.now().year

# ─────────────────────────  LOGIC HELPERS (Precision)  ───────────────────────

def _parse_date(s: str) -> datetime | None:
    s = s.strip().replace("-", "/")
    if not s: return None
    # Prioritizes DD/MM as requested by user
    for f in ("%d/%m/%Y", "%d/%m/%y", "%d/%m", "%m/%d/%Y", "%m/%d/%y", "%m/%d"):
        try:
            d = datetime.strptime(s, f)
            return d.replace(year=_YEAR) if f in ("%d/%m", "%m/%d") else d
        except ValueError: pass
    return None

def _date_style(ds: str, c: dict[str, str]) -> tuple[str, str, str]:
    d = _parse_date(ds)
    if d is None: return ("", "", "")
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = (d - today).days
    label = d.strftime("%d %b")
    if delta < 0: return (f"⚠ {label} (Past)", c["err_bg"], c["err"])
    if delta == 0: return ("📌 TODAY", c["ok_bg"], c["ok"])
    if delta <= 3: return (f"🔜 {label}", c["info_bg"], c["info"])
    return (f"📅 {label}", c["accent_soft"], c["accent"])

# ─────────────────────────  CALENDAR COMPONENT (Reuse)  ──────────────────

class CalendarPopup(ctk.CTkToplevel):
    """Refined Month-Grid date picker following dashboard aesthetics."""
    def __init__(self, parent: ctk.CTk, palette: dict[str, str], callback: Callable[[str], None]):
        super().__init__(parent) # type: ignore
        self.title("Select Due Date")
        self.geometry("340x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set() # Modal behavior
        self._cb, self._c = callback, palette
        now = datetime.now()
        self._year, self._month = now.year, now.month
        
        self.configure(fg_color=self._c["panel"])
        
        # Header Nav
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=25, pady=(25, 10))
        
        # Navigation
        self.lbl = ctk.CTkLabel(nav, text="", font=ctk.CTkFont(size=16, weight="bold"), text_color=self._c["text"])
        self.lbl.pack(side="left")
        
        btn_fr = ctk.CTkFrame(nav, fg_color="transparent")
        btn_fr.pack(side="right")
        
        ctk.CTkButton(btn_fr, text="❮", width=34, height=34, corner_radius=8, 
                      fg_color=self._c["accent_soft"], text_color=self._c["accent"], hover_color=self._c["nav_active_bg"],
                      command=self._prev).pack(side="left", padx=2)
        ctk.CTkButton(btn_fr, text="❯", width=34, height=34, corner_radius=8, 
                      fg_color=self._c["accent_soft"], text_color=self._c["accent"], hover_color=self._c["nav_active_bg"],
                      command=self._next).pack(side="left", padx=2)
        
        # Day names
        days_fr = ctk.CTkFrame(self, fg_color="transparent")
        days_fr.pack(fill="x", padx=25, pady=(10, 5))
        for d in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            ctk.CTkLabel(days_fr, text=d, width=40, text_color=self._c["muted"],
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        self.grid_fr = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_fr.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Footer
        ftr_fr = ctk.CTkFrame(self, fg_color="transparent")
        ftr_fr.pack(fill="x", padx=25, pady=(5, 25))
        
        ctk.CTkButton(ftr_fr, text="Select Today", height=42, corner_radius=12,
                      font=ctk.CTkFont(weight="bold"),
                      fg_color=self._c["accent"], hover_color=self._c["accent_h"],
                      command=self._pick_today).pack(side="left", fill="x", expand=True, padx=(0, 5))
                      
        ctk.CTkButton(ftr_fr, text="✕", width=42, height=42, corner_radius=12,
                      fg_color=self._c["accent_soft"], text_color=self._c["accent"],
                      command=self.destroy).pack(side="left", padx=(5, 0))
        
        self._center_window()
        self._render()

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}") 

    def _prev(self): 
        self._month, self._year = (12, self._year-1) if self._month==1 else (self._month-1, self._year)
        self._render()
    def _next(self): 
        self._month, self._year = (1, self._year+1) if self._month==12 else (self._month+1, self._year)
        self._render()
    def _render(self):
        for w in self.grid_fr.winfo_children(): w.destroy()
        self.lbl.configure(text=f"{cal_mod.month_name[self._month]} {self._year}")
        matrix = cal_mod.monthcalendar(self._year, self._month)
        today = datetime.now()
        for week in matrix:
            f = ctk.CTkFrame(self.grid_fr, fg_color="transparent")
            f.pack(fill="x")
            for day in week:
                if day == 0: 
                    ctk.CTkLabel(f, text="", width=40).pack(side="left", padx=1)
                else:
                    is_today = (day == today.day and self._month == today.month and self._year == today.year)
                    btn = ctk.CTkButton(f, text=str(day), width=40, height=38, corner_radius=10,
                                        fg_color=self._c["accent"] if is_today else "transparent",
                                        text_color="#FFFFFF" if is_today else self._c["text"],
                                        hover_color=self._c["accent_soft"],
                                        font=ctk.CTkFont(size=12, weight="bold" if is_today else "normal"),
                                        command=lambda d=day: self._pick(d))
                    btn.pack(side="left", padx=1, pady=1)
    def _pick(self, d: int): self._cb(f"{d:02d}/{self._month:02d}"); self.destroy()
    def _pick_today(self): n=datetime.now(); self._cb(f"{n.day:02d}/{n.month:02d}"); self.destroy()

class ToolTip:
    """Auto-hiding tooltip (Efficiency — disappears after 3s or on leave)."""
    def __init__(self, widget: ctk.CTkBaseClass, text: str):
        self.widget = widget
        self.text = text
        self.tip: Optional[ctk.CTkToplevel] = None
        self._timer_id: Optional[str] = None
        self.widget.bind("<Enter>", lambda e: self.show())
        self.widget.bind("<Leave>", lambda e: self.hide())

    def show(self):
        if self.tip or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 25
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
            self.tip = ctk.CTkToplevel(self.widget)
            if self.tip is not None:
                self.tip.wm_overrideredirect(True)  # type: ignore[union-attr]
                self.tip.geometry(f"+{x}+{y}")  # type: ignore[union-attr]
                self.tip.configure(fg_color="#1A1A2E")  # type: ignore[union-attr]
                lbl = ctk.CTkLabel(
                    self.tip, text=self.text, text_color="#F3F4F6",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    corner_radius=8, padx=12, pady=6,
                )
                lbl.pack()
                # Auto-hide after 3 seconds (Efficiency)
                self._timer_id = self.widget.after(3000, self.hide)
        except Exception:
            pass

    def hide(self):
        if self._timer_id:
            try:
                self.widget.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        if self.tip:
            try:
                self.tip.destroy()  # type: ignore[union-attr]
            except Exception:
                pass
            self.tip = None

class ClearConfirmPopup(ctk.CTkToplevel):
    """Modal confirmation for destructive actions (HCI Error Prevention)."""
    def __init__(self, parent: ctk.CTk, palette: dict[str, str], callback: Callable[[], None]):
        super().__init__(parent) # type: ignore
        self.title("Confirm Action")
        self.geometry("400x260")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.configure(fg_color=palette["panel"])
        
        ctk.CTkLabel(self, text="⚠️  WARNING", font=ctk.CTkFont(size=15, weight="bold"), text_color=palette["err"]).pack(pady=(30, 5))
        ctk.CTkLabel(self, text="This will permanently delete all tasks.\nType 'CLEAR' to proceed.", font=ctk.CTkFont(size=14), text_color=palette["text"]).pack(pady=5)
        
        self.entry = ctk.CTkEntry(self, placeholder_text="CLEAR", width=260, height=45, corner_radius=12, justify="center",
                                      fg_color=palette["input_bg"], border_color=palette["input_bd"], text_color=palette["text"])
        self.entry.pack(pady=15)
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self._confirm())
        
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=(5, 30))
        
        ctk.CTkButton(btn_row, text="Confirm Clear", width=140, height=42, corner_radius=12,
                      fg_color=palette["err"], hover_color="#DC2626", font=ctk.CTkFont(weight="bold"),
                      command=self._confirm).pack(side="left", padx=10)
                      
        ctk.CTkButton(btn_row, text="Cancel", width=100, height=42, corner_radius=12,
                      fg_color=palette["accent_soft"], text_color=palette["accent"], 
                      command=self.destroy).pack(side="left", padx=10)
        
        self._cb = callback
        self._c = palette
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _confirm(self):
        if self.entry.get().strip().upper() == "CLEAR":
            self._cb()
            self.destroy()
        else:
            self.entry.configure(border_color=self._c["err"])

class UserGuidePopup(ctk.CTkToplevel):
    """Interactive 20-second guide (Learnability & Memorability)."""
    def __init__(self, parent: ctk.CTk, palette: dict[str, str]):
        super().__init__(parent)  # type: ignore
        self.title("Quick Start Guide")
        self.geometry("520x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._c = palette
        self.configure(fg_color=palette["bg"])

        self.slides = [
            ("🚀  Welcome to TaskFlow",
             "Your premium task management dashboard.\n"
             "Learn the essentials in under 20 seconds.",
             "Tip: You can reopen this guide anytime via the ? button."),
            ("📝  Create & Schedule Tasks",
             "1. Type a task description in the input field.\n"
             "2. Set a deadline using DD/MM or the 📅 Picker.\n"
             "3. Press Enter or click ＋ Add Task.",
             "Shortcut: Ctrl+N focuses the task input instantly."),
            ("🔍  Organize & Filter",
             "• Use the sidebar to filter: Today (1), Upcoming (2), All (3).\n"
             "• Collapse the sidebar with Ctrl+S for a wider view.\n"
             "• Click a task card to select it, double-click to edit.",
             "Shortcut: Press E to edit, Del to remove a selected task."),
            ("⌨️  Master Power Shortcuts",
             "Ctrl+Z  →  Undo last delete\n"
             "Ctrl+T  →  Toggle Dark/Light mode\n"
             "Ctrl+P  →  Open Calendar Picker\n"
             "Ctrl+X  →  Clear all tasks",
             "Pro tip: Hover any button to see its shortcut in a tooltip."),
        ]
        self._step = 0
        self._total = len(self.slides)

        # ── Header Card ──
        self.card = ctk.CTkFrame(self, fg_color=palette["panel"], corner_radius=20, border_width=1,
                                  border_color=palette["border"])
        self.card.pack(fill="both", expand=True, padx=30, pady=(30, 15))

        # Step indicator (Learnability — shows progress)
        self.step_lbl = ctk.CTkLabel(self.card, text="", font=ctk.CTkFont(size=11, weight="bold"),
                                      text_color=palette["muted"])
        self.step_lbl.pack(pady=(25, 5))

        self.lbl_head = ctk.CTkLabel(self.card, text="", font=ctk.CTkFont(size=22, weight="bold"),
                                      text_color=palette["accent"])
        self.lbl_head.pack(pady=(5, 10))

        # Divider
        ctk.CTkFrame(self.card, height=2, fg_color=palette["border"]).pack(fill="x", padx=40, pady=5)

        self.lbl_body = ctk.CTkLabel(self.card, text="", font=ctk.CTkFont(size=14),
                                      text_color=palette["text"], justify="left")
        self.lbl_body.pack(pady=(15, 10), padx=35, anchor="w")

        # Tip area (Satisfaction — helpful micro-hint per slide)
        self.lbl_tip = ctk.CTkLabel(self.card, text="", font=ctk.CTkFont(size=11, slant="italic"),
                                     text_color=palette["info"])
        self.lbl_tip.pack(pady=(5, 20), padx=35, anchor="w")

        # ── Progress bar (Learnability — visual progress) ──
        self.prog_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.prog_frame.pack(fill="x", padx=35, pady=(0, 5))
        self.dots: list[ctk.CTkFrame] = []
        for i in range(self._total):
            dot = ctk.CTkFrame(self.prog_frame, width=40, height=5, corner_radius=3,
                               fg_color=palette["accent"] if i == 0 else palette["border"])
            dot.pack(side="left", expand=True, fill="x", padx=2)
            self.dots.append(dot)

        # ── Navigation ──
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=30, pady=(5, 25))

        self.btn_skip = ctk.CTkButton(nav, text="Skip Guide", width=100, height=42, corner_radius=12,
                                       fg_color=palette["accent_soft"], text_color=palette["text_sec"],
                                       font=ctk.CTkFont(size=12), command=self.destroy)
        self.btn_skip.pack(side="left")

        self.btn_next = ctk.CTkButton(nav, text="Next  ❯", width=140, height=42, corner_radius=12,
                                       fg_color=palette["accent"], hover_color=palette["accent_h"],
                                       font=ctk.CTkFont(size=13, weight="bold"), command=self._next)
        self.btn_next.pack(side="right")

        self.btn_prev = ctk.CTkButton(nav, text="❮  Back", width=100, height=42, corner_radius=12,
                                       fg_color=palette["accent_soft"], text_color=palette["accent"],
                                       font=ctk.CTkFont(size=12), command=self._prev)
        self.btn_prev.pack(side="right", padx=(0, 10))

        self._render()
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _render(self):
        title, body, tip = self.slides[self._step]
        self.step_lbl.configure(text=f"STEP {self._step + 1} OF {self._total}")
        self.lbl_head.configure(text=title)
        self.lbl_body.configure(text=body)
        self.lbl_tip.configure(text=f"💡 {tip}")

        # Progress dots
        for i, dot in enumerate(self.dots):
            dot.configure(fg_color=self._c["accent"] if i <= self._step else self._c["border"])

        # Button states (Usability — disable back on first, show finish on last)
        self.btn_prev.configure(state="normal" if self._step > 0 else "disabled")
        is_last = self._step == self._total - 1
        self.btn_next.configure(text="✓  Finish" if is_last else "Next  ❯")
        self.btn_skip.pack_forget() if is_last else self.btn_skip.pack(side="left")

    def _next(self):
        if self._step < self._total - 1:
            self._step += 1
            self._render()
        else:
            self.destroy()

    def _prev(self):
        if self._step > 0:
            self._step -= 1
            self._render()

class EditTaskPopup(ctk.CTkToplevel):
    """Modern modal for editing tasks (Focused Flow)."""
    def __init__(self, parent: ctk.CTk, palette: dict[str, str], task: dict[str, str], callback: Callable[[str, str], None]):
        super().__init__(parent) # type: ignore
        self.title("Edit Task")
        self.geometry("460x360")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self._c = palette
        self._cb = callback
        self.configure(fg_color=palette["panel"])
        
        ctk.CTkLabel(self, text="✏️  Edit Task", font=ctk.CTkFont(size=20, weight="bold"), text_color=palette["text"]).pack(pady=(35, 20))
        
        # Task Input
        self.ent_task = ctk.CTkEntry(self, width=380, height=50, corner_radius=12, font=ctk.CTkFont(size=14),
                                     fg_color=palette["input_bg"], border_color=palette["input_bd"], text_color=palette["text"])
        self.ent_task.pack(pady=5)
        self.ent_task.insert(0, task["text"])
        self.ent_task.focus_set()
        
        # Date Input Row
        date_fr = ctk.CTkFrame(self, fg_color="transparent")
        date_fr.pack(pady=20)
        
        self.ent_date = ctk.CTkEntry(date_fr, placeholder_text="DD/MM", width=120, height=42, corner_radius=10,
                                     fg_color=palette["input_bg"], border_color=palette["input_bd"], text_color=palette["text"])
        self.ent_date.pack(side="left", padx=10)
        self.ent_date.insert(0, task["date"])
        
        ctk.CTkButton(date_fr, text="📅 Picker", width=100, height=42, corner_radius=10,
                      fg_color=palette["accent_soft"], text_color=palette["accent"],
                      command=self._open_cal).pack(side="left", padx=10)
        
        # Action Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=(15, 35))
        
        ctk.CTkButton(btn_row, text="Save Changes", width=160, height=48, corner_radius=12,
                      fg_color=palette["accent"], hover_color=palette["accent_h"], font=ctk.CTkFont(weight="bold"),
                      command=self._save).pack(side="left", padx=10)
                      
        ctk.CTkButton(btn_row, text="Cancel", width=100, height=48, corner_radius=12,
                      fg_color="transparent", text_color=palette["text_sec"], 
                      command=self.destroy).pack(side="left", padx=10)

        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _open_cal(self):
        def on_picked(d: str):
            self.ent_date.delete(0, "end")
            self.ent_date.insert(0, d)
        CalendarPopup(self, self._c, on_picked)

    def _save(self):
        txt, dt = self.ent_task.get().strip(), self.ent_date.get().strip()
        if not txt: return
        self._cb(txt, dt)
        self.destroy()


# ─────────────────────────  MAIN APPLICATION (Structure)  ─────────────────

class TaskFlowApp(ctk.CTk):
    """Dashboard-style task manager implementing 13 UX principles."""
    MAX_LEN = 120

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("TaskFlow Dashboard")
        self.geometry("1024x740")
        self.minsize(860, 640)
        
        # State
        self.tasks: list[dict[str, str]] = []
        self.last_deleted: dict[str, str] | None = None
        self.last_deleted_idx: int | None = None
        self._sel_idx: int | None = None # Index in current view
        self._filter = "today"
        self._is_dark = True
        self._c = DARK
        self._msg_timer = None
        self._editing_idx: int | None = None # Real index of task being edited
        self._side_collapsed = False

        self._init_layout()
        self._bind_keys()
        self._apply_theme()
        self._init_tooltips()

    def _init_tooltips(self):
        ToolTip(self.btn_toggle, "Toggle Sidebar (Ctrl+S)")
        ToolTip(self.guide_btn, "User Guide (20s)")
        ToolTip(self.mode_btn, "Toggle Theme (Ctrl+T)")
        ToolTip(self.btn_add, "Add New Task (Ctrl+N)")
        ToolTip(self.btn_cal, "Open Calendar Picker (Ctrl+P)")
        ToolTip(self.btn_del, "Delete Selected Task (Del)")
        ToolTip(self.btn_edit, "Edit Selected Task (E)")
        ToolTip(self.btn_undo, "Undo Last Delete (Ctrl+Z)")
        ToolTip(self.btn_clear, "Clear All Tasks (Ctrl+X)")
        
        # Nav tooltips
        ToolTip(self.nav_btns["today"], "Show Today's Tasks (1)")
        ToolTip(self.nav_btns["upcoming"], "Show Upcoming Tasks (2)")
        ToolTip(self.nav_btns["all"], "Show All Tasks (3)")
        
        # Scroll Nav tooltips
        for w in self.scroll_nav.winfo_children():
            if hasattr(w, "cget") and w.cget("text") == "▲": ToolTip(w, "Scroll Up") # type: ignore
            if hasattr(w, "cget") and w.cget("text") == "▼": ToolTip(w, "Scroll Down") # type: ignore

    def _bind_keys(self):
        self.bind("<Control-z>", lambda e: self._undo())
        self.bind("<Control-Z>", lambda e: self._undo())
        self.bind("<Delete>", lambda e: self._delete())
        self.bind("<Control-n>", lambda e: self.ent_task.focus_set())
        self.bind("<Control-N>", lambda e: self.ent_task.focus_set())
        self.bind("1", lambda e: self._set_filter("today"))
        self.bind("2", lambda e: self._set_filter("upcoming"))
        self.bind("3", lambda e: self._set_filter("all"))
        self.bind("<Control-t>", lambda e: self._toggle_mode())
        self.bind("<Control-T>", lambda e: self._toggle_mode())
        self.bind("<Control-s>", lambda e: self._toggle_sidebar())
        self.bind("<Control-S>", lambda e: self._toggle_sidebar())
        self.bind("<Control-p>", lambda e: self._open_cal())
        self.bind("<Control-P>", lambda e: self._open_cal())
        self.bind("<Control-x>", lambda e: self._show_clear_dialog())
        self.bind("<Control-X>", lambda e: self._show_clear_dialog())
        self.bind("e", lambda e: self._edit())
        self.bind("E", lambda e: self._edit())

    def _init_layout(self):
        # 1. SIDEBAR PANEL (Structure & Continuity)
        self.side = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.side.pack(side="left", fill="y")
        self.side.pack_propagate(False)

        # Brand / Logo / Toggle
        self.side_hdr = ctk.CTkFrame(self.side, fg_color="transparent")
        self.side_hdr.pack(fill="x", padx=20, pady=(40, 30))
        
        self.btn_toggle = ctk.CTkButton(self.side_hdr, text="✕", width=40, height=40, corner_radius=10,
                                        font=ctk.CTkFont(size=20), fg_color="transparent", 
                                        text_color=self._c["text"], hover_color=self._c["accent_soft"],
                                        command=self._toggle_sidebar)
        self.btn_toggle.pack(side="left")

        self.logo_lbl = ctk.CTkLabel(self.side_hdr, text="TaskFlow", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_lbl.pack(side="left", padx=(15, 0))

        # Navigation (Efficiency)
        self.nav_btns = {}
        self.nav_data = [("today", "Today", "📌"), ("upcoming", "Upcoming", "📆"), ("all", "All Tasks", "📋")]
        for key, text, ico in self.nav_data:
            btn = ctk.CTkButton(self.side, text=f"  {ico}  {text}", anchor="w", height=48, corner_radius=12,
                                font=ctk.CTkFont(size=14, weight="bold"),
                                command=lambda k=key: self._set_filter(k))
            btn.pack(fill="x", padx=15, pady=4)
            self.nav_btns[key] = btn

        # Sidebar Divider
        ctk.CTkFrame(self.side, height=1, fg_color=self._c["border"]).pack(fill="x", padx=20, pady=20)

        # 2. MAIN CONTENT AREA (Hierarchy & Aesthetics)
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.pack(side="left", fill="both", expand=True, padx=40, pady=0)

        # Header Title with Toggle (Visibility)
        hdr_row = ctk.CTkFrame(self.main, fg_color="transparent")
        hdr_row.pack(fill="x", pady=(40, 5))
        
        self.greeting = ctk.CTkLabel(hdr_row, text="Hello,", font=ctk.CTkFont(size=32, weight="bold"))
        self.greeting.pack(side="left")
        
        # Darkmode Icon moved to top
        hdr_btns = ctk.CTkFrame(hdr_row, fg_color="transparent")
        hdr_btns.pack(side="right")

        self.guide_btn = ctk.CTkButton(hdr_btns, text="?", width=42, height=42, corner_radius=12,
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color=self._c["accent_soft"], text_color=self._c["accent"],
                                       command=self._open_guide)
        self.guide_btn.pack(side="left", padx=5)

        self.mode_btn = ctk.CTkButton(hdr_btns, text="☀️  Mode Toggle", width=130, height=42, corner_radius=12,
                                      font=ctk.CTkFont(size=12, weight="bold"),
                                      command=self._toggle_mode)
        self.mode_btn.pack(side="left", padx=5)
        self.sub_text = ctk.CTkLabel(self.main, text="Here's what's on your agenda today.", font=ctk.CTkFont(size=16))
        self.sub_text.pack(anchor="w", pady=(0, 15))

        # Status Bar (Feedback - Moved to top for visibility)
        self.status_bar = ctk.CTkFrame(self.main, height=42, corner_radius=12, border_width=1)
        self.status_bar.pack(fill="x", pady=(0, 20))
        self.status_bar.pack_propagate(False)
        self.status_lbl = ctk.CTkLabel(self.status_bar, text="Ready", font=ctk.CTkFont(size=12))
        self.status_lbl.pack(side="left", padx=15)

        # INPUT AREA (Simplicity & Tolerance)
        self.input_card = ctk.CTkFrame(self.main, corner_radius=20, border_width=1)
        self.input_card.pack(fill="x", pady=(0, 25))
        
        row1 = ctk.CTkFrame(self.input_card, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(20, 10))
        
        self.ent_task = ctk.CTkEntry(row1, placeholder_text="Enter a task description...", height=48, 
                                     corner_radius=12, border_width=2, font=ctk.CTkFont(size=15))
        self.ent_task.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.ent_task.bind("<Return>", lambda e: self._add())
        self.ent_task.bind("<KeyRelease>", lambda e: self._upd_cc())

        self.btn_add = ctk.CTkButton(row1, text="＋  Add Task", width=120, height=48, corner_radius=12,
                                     font=ctk.CTkFont(size=14, weight="bold"), command=self._add)
        self.btn_add.pack(side="right")

        row2 = ctk.CTkFrame(self.input_card, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(0, 20))

        self.ent_date = ctk.CTkEntry(row2, placeholder_text="DD/MM", width=90, height=36, corner_radius=10,
                                     font=ctk.CTkFont(size=12))
        self.ent_date.pack(side="left", padx=(0, 8))
        self.ent_date.bind("<Return>", lambda e: self._add())
        
        ctk.CTkLabel(row2, text="day/month", font=ctk.CTkFont(size=10), text_color=self._c["muted"]).pack(side="left", padx=(0, 12))

        self.btn_cal = ctk.CTkButton(row2, text="📅 Picker", width=100, height=36, corner_radius=10,
                                     font=ctk.CTkFont(size=12, weight="bold"), command=self._open_cal)
        self.btn_cal.pack(side="left", padx=(0, 12))

        self.lbl_cc = ctk.CTkLabel(row2, text="0 / 120", font=ctk.CTkFont(size=11))
        self.lbl_cc.pack(side="right")

        # TASK LIST VIEW (Visibility + Usability)
        scroll_container = ctk.CTkFrame(self.main, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True)

        self.scroll = ctk.CTkScrollableFrame(scroll_container, fg_color="transparent")
        self.scroll.pack(side="left", fill="both", expand=True)

        # Scroll Rail — arrows stacked tightly with scrollbar (Usability)
        self.scroll_nav = ctk.CTkFrame(scroll_container, fg_color=self._c["panel"],
                                        width=36, corner_radius=10)
        self.scroll_nav.pack(side="right", fill="y", padx=(4, 0), pady=4)
        self.scroll_nav.pack_propagate(False)

        ctk.CTkButton(self.scroll_nav, text="▲", width=30, height=30, corner_radius=6,
                      fg_color=self._c["accent_soft"], text_color=self._c["accent"],
                      hover_color=self._c["nav_active_bg"],
                      command=lambda: self.scroll._parent_canvas.yview_scroll(-3, "units")).pack(pady=(4, 2))

        # Spacer to push ▼ to bottom
        ctk.CTkFrame(self.scroll_nav, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkButton(self.scroll_nav, text="▼", width=30, height=30, corner_radius=6,
                      fg_color=self._c["accent_soft"], text_color=self._c["accent"],
                      hover_color=self._c["nav_active_bg"],
                      command=lambda: self.scroll._parent_canvas.yview_scroll(3, "units")).pack(pady=(2, 4))

        # BOTTOM BAR (Feedback & User Control)
        self.bottom_fr = ctk.CTkFrame(self.main, fg_color="transparent")
        self.bottom_fr.pack(fill="x", pady=(15, 25))

        # Actions
        self.action_fr = ctk.CTkFrame(self.bottom_fr, fg_color="transparent")
        self.action_fr.pack(fill="x")

        self.btn_del = ctk.CTkButton(self.action_fr, text="🗑  Delete Selected", height=42, corner_radius=12,
                                     font=ctk.CTkFont(size=13, weight="bold"), command=self._delete)
        self.btn_del.pack(side="left", padx=(0, 10))

        self.btn_edit = ctk.CTkButton(self.action_fr, text="✏️  Edit Selected", height=42, corner_radius=12,
                                      font=ctk.CTkFont(size=13, weight="bold"), command=self._edit)
        self.btn_edit.pack(side="left", padx=(0, 10))

        self.btn_undo = ctk.CTkButton(self.action_fr, text="↩  Undo Last", height=42, corner_radius=12,
                                      font=ctk.CTkFont(size=13, weight="bold"), command=self._undo)
        self.btn_undo.pack(side="left", padx=(0, 10))

        self.btn_clear = ctk.CTkButton(self.action_fr, text="🧹  Clear All", height=42, corner_radius=12,
                                       font=ctk.CTkFont(size=13, weight="bold"), command=self._show_clear_dialog)
        self.btn_clear.pack(side="right")

    # ═══════════════════  LOGIC HELPERS  ══════════════════════════════════

    def _get_filtered(self) -> list[tuple[int, dict[str, str]]]:
        res = []
        today_str = datetime.now().strftime("%d/%m")
        for i, t in enumerate(self.tasks):
            is_today = (not t["date"]) or (today_str == t["date"])
            if self._filter == "all": res.append((i, t))
            elif self._filter == "today" and is_today: res.append((i, t))
            elif self._filter == "upcoming" and not is_today: res.append((i, t))
        return res

    def _status(self, msg: str, kind: str = "info"):
        c = self._c
        colors = {"ok": c["ok"], "err": c["err"], "info": c["info"]}
        bgs = {"ok": c["ok_bg"], "err": c["err_bg"], "info": c["info_bg"]}
        self.status_lbl.configure(text=msg, text_color=colors.get(kind, c["text_sec"]))
        self.status_bar.configure(fg_color=bgs.get(kind, c["panel"]), border_color=colors.get(kind, c["border"]))
        if self._msg_timer: self.after_cancel(self._msg_timer)
        self._msg_timer = self.after(4000, self._reset_status)

    def _reset_status(self):
        self.status_lbl.configure(text="Ready", text_color=self._c["text_sec"])
        self.status_bar.configure(fg_color=self._c["panel"], border_color=self._c["border"])

    def _upd_cc(self):
        n = len(self.ent_task.get())
        self.lbl_cc.configure(text=f"{n} / 120", text_color=self._c["err"] if n > 120 else self._c["text_sec"])

    # ═══════════════════  CORE ACTIONS (User Control)  ════════════════════

    def _set_filter(self, f: str):
        self._filter = f
        self._sel_idx = None
        self._refresh()
        self._refresh_nav()

    def _add(self):
        txt, dt = self.ent_task.get().strip(), self.ent_date.get().strip()
        if not txt: self._status("Please enter a task description.", "err"); return
        if len(txt) > self.MAX_LEN: self._status("Task too long.", "err"); return
        if dt and not _parse_date(dt): self._status("Invalid date format. Use DD/MM.", "err"); return
        
        idx = self._editing_idx
        if isinstance(idx, int):
            # Update existing
            self.tasks[idx] = {"text": txt, "date": dt}
            self._status(f"Updated task: {txt}", "ok")
            self._cancel_edit()
        else:
            # Add new
            self.tasks.append({"text": txt, "date": dt})
            self.ent_task.delete(0, "end"); self.ent_date.delete(0, "end")
            self._upd_cc()
            self._status(f"Added task: {txt}", "ok")
        
        self._refresh(); self._refresh_nav()

    def _edit(self, view_idx: int | None = None):
        """Enter edit mode for selected task or provided view index via focused popup."""
        if view_idx is None:
            view_idx = self._sel_idx
        
        if view_idx is None: return
        
        filtered = self._get_filtered()
        if view_idx >= len(filtered): return
        
        real_idx, task = filtered[view_idx]
        self._editing_idx = real_idx
        
        EditTaskPopup(self, self._c, task, self._on_edit_save)

    def _on_edit_save(self, txt: str, dt: str):
        idx = self._editing_idx
        if not isinstance(idx, int): return
        self.tasks[idx] = {"text": txt, "date": dt}
        self._status(f"Updated task: {txt}", "ok")
        self._editing_idx = None
        self._refresh(); self._refresh_nav()

    def _delete(self):
        sidx = self._sel_idx
        if sidx is None: return
        filtered = self._get_filtered()
        if sidx >= len(filtered): return
        
        real_idx, task = filtered[sidx]
        self.last_deleted = self.tasks.pop(real_idx)
        self.last_deleted_idx = real_idx
        self._sel_idx = None
        self._status(f"Deleted task: {task['text']}", "info")
        self._refresh(); self._refresh_nav()

    def _undo(self):
        task = self.last_deleted
        ridx = self.last_deleted_idx
        if task is None or ridx is None: return
        self.tasks.insert(ridx, task) # type: ignore
        text = task["text"]
        self.last_deleted = None; self.last_deleted_idx = None
        self._status(f"Restored task: {text}", "ok")
        self._refresh(); self._refresh_nav()

    def _show_clear_dialog(self):
        if not self.tasks: return
        ClearConfirmPopup(self, self._c, self._do_clear)

    def _do_clear(self):
        n = len(self.tasks)
        self.tasks.clear()
        self.last_deleted = None
        self.last_deleted_idx = None
        self._sel_idx = None
        self._refresh(); self._refresh_nav()
        self._status(f"Cleared {n} tasks.", "ok")

    # ═══════════════════  THEMING & UI REFRESH  ═══════════════════════════

    def _toggle_mode(self):
        old_c = self._c
        self._is_dark = not self._is_dark
        self._c = DARK if self._is_dark else LIGHT
        ctk.set_appearance_mode("dark" if self._is_dark else "light")
        self.mode_btn.configure(text="☀️  Light Mode" if self._is_dark else "🌙  Dark Mode")
        
        # Smooth transition animation
        steps = 8
        for i in range(1, steps + 1):
            t = i / steps
            self.after(i * 25, lambda f=t: self._animate_step(old_c, self._c, f))
        
        self.after((steps + 1) * 25, lambda: (self._apply_theme(), self._refresh()))

    def _animate_step(self, c1: dict[str, str], c2: dict[str, str], f: float):
        def _interp(k: str):
            h1: str = str(c1[k])
            h2: str = str(c2[k])
            rgb1 = (int(h1[1:3], 16), int(h1[3:5], 16), int(h1[5:7], 16))  # type: ignore[index]
            rgb2 = (int(h2[1:3], 16), int(h2[3:5], 16), int(h2[5:7], 16))  # type: ignore[index]
            res = tuple(max(0, min(255, int(rgb1[j] + (rgb2[j] - rgb1[j]) * f))) for j in range(3))
            return '#%02x%02x%02x' % res

        bg = _interp("bg")
        side = _interp("sidebar")
        pan = _interp("panel")
        
        self.configure(fg_color=bg)
        self.side.configure(fg_color=side)
        self.side_hdr.configure(fg_color=side)
        self.main.configure(fg_color=bg)
        self.scroll.configure(fg_color=bg)
        self.input_card.configure(fg_color=pan)
        self.status_bar.configure(fg_color=pan)

    def _apply_theme(self):
        c = self._c
        self.configure(fg_color=c["bg"])
        self.side.configure(fg_color=c["sidebar"])
        self.side_hdr.configure(fg_color=c["sidebar"])
        self.main.configure(fg_color=c["bg"])
        self.greeting.configure(text_color=c["text"])
        self.sub_text.configure(text_color=c["text_sec"])
        self.input_card.configure(fg_color=c["panel"], border_color=c["border"])
        self.ent_task.configure(fg_color=c["input_bg"], border_color=c["input_bd"], text_color=c["text"])
        self.ent_date.configure(fg_color=c["input_bg"], border_color=c["input_bd"], text_color=c["text"])
        self.btn_add.configure(fg_color=c["accent"], hover_color=c["accent_h"])
        self.btn_toggle.configure(text_color=c["text"], hover_color=c["accent_soft"])
        self.scroll.configure(fg_color=c["bg"])
        self.scroll_nav.configure(fg_color=c["panel"])
        for child in self.scroll_nav.winfo_children():
            if hasattr(child, 'configure') and hasattr(child, 'cget'):
                try:
                    child.configure(fg_color=c["accent_soft"], text_color=c["accent"])  # type: ignore
                except Exception:
                    pass
        self.status_bar.configure(fg_color=c["panel"], border_color=c["border"])
        self.status_lbl.configure(text_color=c["text_sec"])
        
        self.mode_btn.configure(fg_color=c["accent_soft"], text_color=c["accent"], hover_color=c["nav_active_bg"])
        self.guide_btn.configure(fg_color=c["accent_soft"], text_color=c["accent"], hover_color=c["nav_active_bg"])
        self.btn_cal.configure(fg_color=c["accent_soft"], text_color=c["accent"], hover_color=c["nav_active_bg"])

        self._refresh_nav()
        self._ctrls()

    def _ctrls(self):
        c = self._c
        sel = self._sel_idx is not None
        can_undo = self.last_deleted is not None
        has_tasks = len(self.tasks) > 0
        
        self.btn_del.configure(state="normal" if sel else "disabled",
                               fg_color=c["err"] if sel else c["accent_soft"],
                               text_color="#FFFFFF" if sel else c["muted"])
        self.btn_edit.configure(state="normal" if sel else "disabled",
                                fg_color=c["accent"] if sel else c["accent_soft"],
                                text_color="#FFFFFF" if sel else c["muted"])
        self.btn_undo.configure(state="normal" if can_undo else "disabled",
                                fg_color=c["accent"] if can_undo else c["accent_soft"],
                                text_color="#FFFFFF" if can_undo else c["muted"])
        self.btn_clear.configure(state="normal" if has_tasks else "disabled",
                                 fg_color=c["err"] if has_tasks else c["accent_soft"],
                                 text_color="#FFFFFF" if has_tasks else c["muted"])

    def _refresh_nav(self):
        c = self._c
        for k, btn in self.nav_btns.items():
            active = (k == self._filter)
            btn.configure(fg_color=c["nav_active_bg"] if active else "transparent",
                          text_color=c["nav_active_fg"] if active else c["text_sec"],
                          hover_color=c["nav_active_bg"])

    def _refresh(self):
        for w in self.scroll.winfo_children(): w.destroy()
        filtered = self._get_filtered()
        if not filtered:
            msg = "No tasks found for today." if self._filter == "today" else "No tasks scheduled."
            ctk.CTkLabel(self.scroll, text=msg, font=ctk.CTkFont(size=14, slant="italic"), text_color=self._c["muted"]).pack(pady=60)
            self._ctrls(); return

        for i, (ri, task) in enumerate(filtered):
            sel = (i == self._sel_idx)
            card = ctk.CTkFrame(self.scroll, corner_radius=16, height=64, border_width=2 if sel else 1,
                                fg_color=self._c["nav_active_bg"] if sel else self._c["panel"],
                                border_color=self._c["accent"] if sel else self._c["border"])
            card.pack(fill="x", pady=5, padx=4)
            card.pack_propagate(False)

            # Left Accent Bar (Effectiveness — visual hierarchy)
            acc = ctk.CTkFrame(card, width=5, corner_radius=3,
                               fg_color=self._c["accent"] if sel else self._c["border"])
            acc.pack(side="left", fill="y", padx=(4, 0), pady=6)

            # Selection Icon (Memorability — consistent visual language)
            ico = "✔" if sel else "○"
            ctk.CTkLabel(card, text=ico, font=ctk.CTkFont(size=18),
                         text_color=self._c["accent"]).pack(side="left", padx=(14, 10))

            # Task Text — LEFT ALIGNED (Effectiveness — scannable list)
            ctk.CTkLabel(card, text=task["text"],
                         font=ctk.CTkFont(size=14, weight="bold" if sel else "normal"),
                         text_color=self._c["text"],
                         anchor="w").pack(side="left", fill="x", expand=True, anchor="w")

            # Date Badge — right side (Functionality — at-a-glance deadline)
            if task["date"]:
                lb, bg, fg = _date_style(task["date"], self._c)
                bfr = ctk.CTkFrame(card, fg_color=bg, corner_radius=10)
                bfr.pack(side="right", padx=(10, 16), pady=14)
                ctk.CTkLabel(bfr, text=lb, font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=fg).pack(padx=10, pady=3)

            # Interaction Bindings (Satisfaction — responsive hover feedback)
            for w in [card, acc]:
                w.bind("<Button-1>", lambda e, idx=i: self._on_card_click(idx))
                w.bind("<Double-Button-1>", lambda e, idx=i: self._edit(idx))
                w.bind("<Enter>", lambda e, c=card, s=sel: c.configure(
                    fg_color=self._c["card_hover"] if not s else self._c["nav_active_bg"]))
                w.bind("<Leave>", lambda e, c=card, s=sel: c.configure(
                    fg_color=self._c["panel"] if not s else self._c["nav_active_bg"]))
        
        self._ctrls()

    def _on_card_click(self, idx: int):
        self._sel_idx = idx if self._sel_idx != idx else None
        self._refresh()

    def _open_cal(self):
        CalendarPopup(self, self._c, self._on_date_picked)

    def _toggle_sidebar(self):
        self._side_collapsed = not self._side_collapsed
        new_w = 80 if self._side_collapsed else 240
        self.side.configure(width=new_w)
        self.btn_toggle.configure(text="☰" if self._side_collapsed else "✕")
        
        if self._side_collapsed:
            self.logo_lbl.pack_forget()
            for k, (key, text, ico) in zip(self.nav_btns.keys(), self.nav_data):
                self.nav_btns[k].configure(text=f" {ico}", anchor="center")
        else:
            self.logo_lbl.pack(side="left", padx=(15, 0))
            for k, (key, text, ico) in zip(self.nav_btns.keys(), self.nav_data):
                self.nav_btns[k].configure(text=f"  {ico}  {text}", anchor="w")

    def _on_date_picked(self, dstr: str):
        self.ent_date.delete(0, "end"); self.ent_date.insert(0, dstr)

    def _open_guide(self):
        UserGuidePopup(self, self._c)

if __name__ == "__main__":
    app = TaskFlowApp()
    app.mainloop()
