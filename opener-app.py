"""מיני-דפדפן: פותח קישורים אחד-אחד בפרופיל הנכון של Chrome.

קורא את הקבצים מ-profiles/*.txt (פורמט קיים: שורה ראשונה # PROFILE=...).
מאפשר לעבור על הקישורים בלחיצה על "הבא", ולערוך את הרשימה.
"""
from __future__ import annotations

import re
import subprocess
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

ROOT = Path(__file__).parent
PROFILES_DIR = ROOT / "profiles"
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def load_profiles() -> list[dict]:
    """טוען את כל קבצי הפרופילים. מחזיר רשימת dicts עם name, chrome_profile, urls, file."""
    profiles = []
    if not PROFILES_DIR.exists():
        return profiles

    for file in sorted(PROFILES_DIR.glob("*.txt")):
        with open(file, encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f]

        chrome_profile = None
        urls = []
        comments_header = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            m = re.match(r"^#\s*PROFILE\s*=\s*(.+)$", stripped)
            if m:
                chrome_profile = m.group(1).strip()
                continue
            if stripped.startswith("#"):
                comments_header.append(stripped)
                continue
            urls.append(stripped)

        if not chrome_profile:
            continue

        name = file.stem
        # שם תצוגה אם מופיע בהערות
        display = name
        for c in comments_header:
            m = re.search(r"שם תצוגה:\s*(.+)", c)
            if m:
                display = m.group(1).strip()
                break

        profiles.append({
            "name": name,
            "display": display,
            "chrome_profile": chrome_profile,
            "urls": urls,
            "file": file,
            "comments_header": comments_header,
        })
    return profiles


def save_profile(profile: dict) -> None:
    """שומר פרופיל חזרה לקובץ שלו."""
    lines = [f"# PROFILE={profile['chrome_profile']}"]
    lines.extend(profile.get("comments_header", []))
    lines.extend(profile["urls"])
    with open(profile["file"], "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def open_url_in_chrome(chrome_profile: str, url: str) -> None:
    """פותח URL בפרופיל מסוים של Chrome."""
    subprocess.Popen([
        CHROME_BIN,
        f"--profile-directory={chrome_profile}",
        url,
    ])


# ──────────────────────────────────────────────────────────────────
# GUI
# ──────────────────────────────────────────────────────────────────

class OpenerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("בוקר טוב — פותח קישורים")
        self.root.geometry("780x560")

        self.profiles = load_profiles()
        self.current_profile_idx = 0
        self.current_url_idx = 0
        self.visited: set[tuple[int, int]] = set()  # (profile_idx, url_idx)

        # פונטים
        self.font_default = tkfont.Font(family="Helvetica", size=13)
        self.font_big = tkfont.Font(family="Helvetica", size=15, weight="bold")
        self.font_url = tkfont.Font(family="Menlo", size=11)

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        # פס עליון
        top = tk.Frame(self.root, bg="#2c3e50", padx=12, pady=10)
        top.pack(fill="x")

        self.lbl_profile = tk.Label(top, text="", font=self.font_big,
                                     fg="white", bg="#2c3e50", anchor="e")
        self.lbl_profile.pack(side="right", fill="x", expand=True)

        self.lbl_progress = tk.Label(top, text="", font=self.font_default,
                                      fg="#bdc3c7", bg="#2c3e50")
        self.lbl_progress.pack(side="left")

        # אזור מרכזי - URL נוכחי + רשימת URLs
        main = tk.Frame(self.root, padx=12, pady=12)
        main.pack(fill="both", expand=True)

        # URL נוכחי
        cur_frame = tk.LabelFrame(main, text="הקישור הנוכחי",
                                   font=self.font_default, padx=10, pady=10)
        cur_frame.pack(fill="x", pady=(0, 10))

        self.lbl_current_url = tk.Label(cur_frame, text="", font=self.font_url,
                                         fg="#2980b9", wraplength=720,
                                         justify="left", anchor="w")
        self.lbl_current_url.pack(fill="x")

        # כפתורים
        btns = tk.Frame(main)
        btns.pack(fill="x", pady=(0, 10))

        tk.Button(btns, text="◀ הקודם", font=self.font_default,
                  command=self.prev_url, width=10).pack(side="right", padx=4)

        self.btn_open = tk.Button(btns, text="פתח ועבור הלאה ▶",
                                   font=self.font_big, bg="#27ae60", fg="white",
                                   activebackground="#1e8449",
                                   command=self.open_and_advance, width=20,
                                   relief="flat", padx=10, pady=6)
        self.btn_open.pack(side="right", padx=4)

        tk.Button(btns, text="דלג", font=self.font_default,
                  command=self.skip_url, width=8).pack(side="right", padx=4)

        tk.Button(btns, text="↻ אפס סימונים", font=self.font_default,
                  command=self.reset_visited).pack(side="left", padx=4)

        tk.Button(btns, text="✏️ ערוך פרופיל", font=self.font_default,
                  command=self.edit_profile).pack(side="left", padx=4)

        tk.Button(btns, text="🔁 רענן מקובץ", font=self.font_default,
                  command=self.reload_profiles).pack(side="left", padx=4)

        # רשימת קישורים בפרופיל הנוכחי
        list_frame = tk.LabelFrame(main, text="קישורים בפרופיל הזה",
                                    font=self.font_default, padx=6, pady=6)
        list_frame.pack(fill="both", expand=True)

        list_inner = tk.Frame(list_frame)
        list_inner.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_inner)
        scrollbar.pack(side="right", fill="y")

        self.url_list = tk.Listbox(list_inner, font=self.font_url,
                                    yscrollcommand=scrollbar.set,
                                    activestyle="dotbox", height=10)
        self.url_list.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.url_list.yview)
        self.url_list.bind("<Double-Button-1>", self._on_list_double_click)

        # פס סטטוס תחתון
        self.status = tk.Label(self.root, text="", anchor="w",
                               bg="#ecf0f1", padx=10, pady=4,
                               font=self.font_default)
        self.status.pack(fill="x", side="bottom")

    # ──────────────────────────────────────────────────────────────
    # logic
    # ──────────────────────────────────────────────────────────────

    def _current_profile(self) -> dict | None:
        if not self.profiles:
            return None
        return self.profiles[self.current_profile_idx]

    def _current_url(self) -> str | None:
        p = self._current_profile()
        if not p or not p["urls"]:
            return None
        return p["urls"][self.current_url_idx]

    def _refresh(self):
        if not self.profiles:
            self.lbl_profile.config(text="(אין פרופילים)")
            self.lbl_current_url.config(text="הוסף קבצים ל-profiles/")
            self.status.config(text="")
            self.btn_open.config(state="disabled")
            return

        p = self._current_profile()
        self.lbl_profile.config(text=f"📁 {p['display']} ({p['chrome_profile']})")

        total = sum(len(pp["urls"]) for pp in self.profiles)
        done = len(self.visited)
        self.lbl_progress.config(text=f"{done}/{total}")

        url = self._current_url()
        if url is None:
            self.lbl_current_url.config(text="(אין קישורים בפרופיל הזה)")
            self.btn_open.config(state="disabled")
        else:
            self.lbl_current_url.config(text=url)
            self.btn_open.config(state="normal")

        # רשימה
        self.url_list.delete(0, tk.END)
        for i, u in enumerate(p["urls"]):
            mark = "✓" if (self.current_profile_idx, i) in self.visited else "○"
            cursor = "►" if i == self.current_url_idx else " "
            self.url_list.insert(tk.END, f"{cursor} {mark}  {u}")
            if (self.current_profile_idx, i) in self.visited:
                self.url_list.itemconfig(i, fg="#95a5a6")
            if i == self.current_url_idx:
                self.url_list.itemconfig(i, bg="#fff3cd")

        self.url_list.see(self.current_url_idx)

        self.status.config(
            text=f"פרופיל {self.current_profile_idx + 1}/{len(self.profiles)} • "
                 f"קישור {self.current_url_idx + 1}/{len(p['urls']) or 1}"
        )

    def open_and_advance(self):
        p = self._current_profile()
        url = self._current_url()
        if not p or url is None:
            return
        open_url_in_chrome(p["chrome_profile"], url)
        self.visited.add((self.current_profile_idx, self.current_url_idx))
        self._advance()

    def skip_url(self):
        self._advance()

    def _advance(self):
        """עובר לקישור הבא. אם זה הסוף של פרופיל, עובר לפרופיל הבא."""
        p = self._current_profile()
        if not p:
            return
        if self.current_url_idx + 1 < len(p["urls"]):
            self.current_url_idx += 1
        elif self.current_profile_idx + 1 < len(self.profiles):
            self.current_profile_idx += 1
            self.current_url_idx = 0
        else:
            messagebox.showinfo("סיימת!", "עברת על כל הקישורים בכל הפרופילים.")
        self._refresh()

    def prev_url(self):
        if self.current_url_idx > 0:
            self.current_url_idx -= 1
        elif self.current_profile_idx > 0:
            self.current_profile_idx -= 1
            self.current_url_idx = max(0, len(self._current_profile()["urls"]) - 1)
        self._refresh()

    def reset_visited(self):
        self.visited.clear()
        self.current_profile_idx = 0
        self.current_url_idx = 0
        self._refresh()

    def reload_profiles(self):
        self.profiles = load_profiles()
        self.current_profile_idx = 0
        self.current_url_idx = 0
        self.visited.clear()
        self._refresh()

    def _on_list_double_click(self, _event):
        sel = self.url_list.curselection()
        if not sel:
            return
        self.current_url_idx = sel[0]
        self._refresh()

    # ──────────────────────────────────────────────────────────────
    # editing
    # ──────────────────────────────────────────────────────────────

    def edit_profile(self):
        p = self._current_profile()
        if not p:
            return
        EditorWindow(self.root, p, on_save=self._on_profile_saved)

    def _on_profile_saved(self, updated_profile: dict):
        save_profile(updated_profile)
        # שומרים מיקום נוכחי
        prof_idx = self.current_profile_idx
        url_idx = min(self.current_url_idx, max(0, len(updated_profile["urls"]) - 1))
        self.profiles = load_profiles()
        self.current_profile_idx = min(prof_idx, len(self.profiles) - 1)
        self.current_url_idx = url_idx
        self._refresh()


class EditorWindow:
    """חלון עריכה לפרופיל - הוספה/הסרה/עריכה של URLs."""

    def __init__(self, parent, profile: dict, on_save):
        self.profile = profile
        self.on_save = on_save

        self.win = tk.Toplevel(parent)
        self.win.title(f"עריכה: {profile['display']}")
        self.win.geometry("680x460")
        self.win.transient(parent)

        font_default = tkfont.Font(family="Helvetica", size=13)
        font_url = tkfont.Font(family="Menlo", size=11)

        header = tk.Label(self.win, text=f"📁 {profile['display']} ({profile['chrome_profile']})",
                          font=tkfont.Font(family="Helvetica", size=14, weight="bold"),
                          pady=8)
        header.pack(fill="x")

        # רשימת URLs - Text widget כדי לאפשר עריכה ישירה
        frame = tk.Frame(self.win, padx=10, pady=4)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="שורה לכל קישור. שורות שמתחילות ב-# נחשבות להערה.",
                 font=font_default, fg="#7f8c8d").pack(anchor="w", pady=(0, 4))

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.text = tk.Text(frame, font=font_url, wrap="none",
                             yscrollcommand=scrollbar.set, height=15)
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text.yview)

        # מאכלסים: הערות + URLs
        content_lines = list(profile.get("comments_header", []))
        content_lines.extend(profile["urls"])
        self.text.insert("1.0", "\n".join(content_lines))

        # כפתורים
        btns = tk.Frame(self.win, padx=10, pady=10)
        btns.pack(fill="x")

        tk.Button(btns, text="💾 שמור", font=font_default, bg="#27ae60",
                  fg="white", command=self.save, width=12,
                  relief="flat").pack(side="right", padx=4)
        tk.Button(btns, text="ביטול", font=font_default,
                  command=self.win.destroy, width=10).pack(side="right", padx=4)

    def save(self):
        content = self.text.get("1.0", "end-1c").strip()
        new_urls = []
        new_comments = []
        for line in content.splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                # שורת הערה - שומרים, אבל לא שורת PROFILE (אסור לשנות)
                if re.match(r"^#\s*PROFILE\s*=", s):
                    continue
                new_comments.append(s)
            else:
                new_urls.append(s)

        updated = dict(self.profile)
        updated["urls"] = new_urls
        updated["comments_header"] = new_comments
        self.on_save(updated)
        self.win.destroy()


def main():
    root = tk.Tk()
    OpenerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
