"""Masqrayd Soundboard standalone Windows prototype.

Run: py -m pip install -r standalone/requirements.txt
     py standalone/soundboard.py
OBS: Capture the application's audio using Application Audio Capture (BETA).
"""
import json
import shutil
import tkinter as tk
import uuid
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

import pygame

APP_DIR = Path.home() / "Music" / "Masqrayd Soundboard"
SOUNDS_DIR = APP_DIR / "Sounds"
LIBRARY_FILE = APP_DIR / "library.json"
COLORS = ["#9d3453", "#c04b72", "#715a91", "#396e82", "#44755d", "#b68a41"]


class Soundboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Masqrayd Soundboard — Standalone")
        self.geometry("850x560")
        self.minsize(540, 380)
        self.configure(bg="#202127")
        SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(32)
        self.items = self.load_library()
        self.playing = {}
        self.dragging = None
        self.pad_buttons = {}
        self.volume = tk.DoubleVar(value=0.8)
        self.search = tk.StringVar()
        self.show_archived = tk.BooleanVar(value=False)
        self.bank = tk.StringVar(value='All')
        self.edit_mode = tk.BooleanVar(value=False)
        self.make_ui()
        self.refresh()
        self.after(200, self.poll_playback)
        self.protocol("WM_DELETE_WINDOW", self.close)

    def load_library(self):
        if LIBRARY_FILE.exists():
            try:
                data = json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
            except (OSError, ValueError):
                messagebox.showwarning("Library", "Library could not be read. Starting with an empty view.")
        return []

    def save(self):
        APP_DIR.mkdir(parents=True, exist_ok=True)
        tmp = LIBRARY_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.items, indent=2), encoding="utf-8")
        tmp.replace(LIBRARY_FILE)

    def make_ui(self):
        header = tk.Frame(self, bg="#202127")
        header.pack(fill="x", padx=14, pady=12)
        tk.Label(header, text="MASQRAYD SOUNDBOARD", fg="#f3e9ed", bg="#202127",
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Button(header, text="+ Import sounds", command=self.import_sounds).pack(side="right")
        bar = tk.Frame(self, bg="#202127")
        bar.pack(fill="x", padx=14, pady=(0, 12))
        tk.Label(bar, text="Search", fg="white", bg="#202127").pack(side="left")
        tk.Entry(bar, textvariable=self.search, width=23).pack(side="left", padx=7)
        self.search.trace_add("write", lambda *_: self.refresh())
        tk.Checkbutton(bar, text="Show archived", variable=self.show_archived,
                       command=self.refresh, bg="#202127", fg="white",
                       selectcolor="#3b3b44").pack(side="left")
        tk.Button(bar, text="Stop all", command=self.stop_all).pack(side="right")
        tk.Checkbutton(bar, text="Arrange pads", variable=self.edit_mode, command=self.refresh,
                       bg="#202127", fg="white", selectcolor="#3b3b44").pack(side="left")
        self.bank_menu = ttk.Combobox(bar, textvariable=self.bank, width=14, state="readonly")
        self.bank_menu.pack(side="left", padx=5)
        self.bank_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        tk.Scale(bar, from_=0, to=1, resolution=0.05, orient="horizontal",
                 variable=self.volume, label="Master volume", bg="#202127", fg="white",
                 highlightthickness=0, length=180, command=lambda _: self.update_volume()).pack(side="right")
        self.canvas = tk.Canvas(self, bg="#202127", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True, padx=(14, 0))
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.grid_frame = tk.Frame(self.canvas, bg="#202127")
        self.window_id = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.resize_grid)
        self.status = tk.Label(self, text="Ready • OBS: use Application Audio Capture for this app",
                               bg="#202127", fg="#b7b5bd", anchor="w")
        self.status.pack(fill="x", padx=14, pady=8)

    def resize_grid(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)
        self.refresh()

    def import_sounds(self):
        paths = filedialog.askopenfilenames(title="Import sound effects",
                                            filetypes=[("Audio files", "*.wav *.mp3 *.ogg"), ("All files", "*.*")])
        for name in paths:
            src = Path(name)
            dest = SOUNDS_DIR / (uuid.uuid4().hex[:10] + src.suffix.lower())
            try:
                shutil.copy2(src, dest)
                self.items.append({"id": uuid.uuid4().hex, "label": src.stem,
                                   "path": str(dest), "color": COLORS[len(self.items) % len(COLORS)],
                                   "archived": False, "bank": "General"})
            except OSError as exc:
                messagebox.showerror("Import failed", str(exc))
        self.save()
        self.refresh()

    def refresh(self):
        if not hasattr(self, "grid_frame"):
            return
        for child in self.grid_frame.winfo_children():
            child.destroy()
        self.pad_buttons = {}
        banks = ["All"] + sorted({x.get("bank", "General") for x in self.items})
        self.bank_menu["values"] = banks
        if self.bank.get() not in banks:
            self.bank.set("All")
        count = max(2, self.canvas.winfo_width() // 180)
        query = self.search.get().casefold()
        visible = [x for x in self.items
                   if (self.show_archived.get() or not x.get("archived"))
                   and (self.bank.get() == "All" or x.get("bank", "General") == self.bank.get())
                   and query in x.get("label", "").casefold()]
        for index, item in enumerate(visible):
            tile = tk.Frame(self.grid_frame, bg="#303039", padx=5, pady=5)
            tile.grid(row=index // count, column=index % count, padx=5, pady=5, sticky="nsew")
            playing = item["id"] in self.playing and self.playing[item["id"]].get_busy()
            label = item["label"][:30]
            pad = tk.Button(tile, text=label, wraplength=135, height=3, width=17,
                            bg="#d72e45" if playing else item.get("color", COLORS[0]),
                            fg="white", activebackground="#ed5267",
                            command=lambda x=item: self.play(x) if not self.edit_mode.get() else None)
            pad.pack(fill="x")
            self.pad_buttons[item["id"]] = pad
            if self.edit_mode.get():
                pad.configure(cursor="fleur", relief="raised")
                pad.bind("<ButtonPress-1>", lambda e, x=item: self.start_drag(e, x))
                pad.bind("<ButtonRelease-1>", lambda e, x=item: self.finish_drag(e, x))
            tk.Button(tile, text="⚙ Edit" if not self.edit_mode.get() else "⚙ Color / Group",
                      command=lambda x=item: self.edit(x)).pack(fill="x", pady=(5, 0))
        for col in range(count):
            self.grid_frame.grid_columnconfigure(col, weight=1)

    def start_drag(self, event, item):
        self.dragging = item["id"]

    def finish_drag(self, event, item):
        if not self.dragging:
            return
        # Identify the pad under the pointer, including when crossing tile boundaries.
        target_widget = self.winfo_containing(event.x_root, event.y_root)
        target_id = None
        while target_widget is not None:
            for key, button in self.pad_buttons.items():
                if target_widget == button:
                    target_id = key
                    break
            if target_id or target_widget == self:
                break
            target_widget = target_widget.master
        source_id = self.dragging
        self.dragging = None
        if target_id and source_id != target_id:
            source = next((x for x in self.items if x["id"] == source_id), None)
            target = next((x for x in self.items if x["id"] == target_id), None)
            if source and target:
                self.items.remove(source)
                self.items.insert(self.items.index(target), source)
                self.save()
                self.refresh()

    def play(self, item):
        path = Path(item["path"])
        if not path.is_file():
            if messagebox.askyesno("Missing sound", "File missing. Locate it now?"):
                self.relink(item)
            return
        try:
            sound = pygame.mixer.Sound(str(path))
            channel = pygame.mixer.find_channel(force=True)
            if channel is None:
                raise RuntimeError("No available audio channel")
            channel.set_volume(self.volume.get())
            channel.play(sound)
            self.playing[item["id"]] = channel
            self.refresh()
        except (pygame.error, OSError, RuntimeError) as exc:
            messagebox.showerror("Playback failed", str(exc))

    def edit(self, item):
        choice = simpledialog.askstring("Pad label", "Sound label:",
                                        initialvalue=item["label"], parent=self)
        if choice is not None and choice.strip():
            item["label"] = choice.strip()
        selected = colorchooser.askcolor(color=item.get("color", COLORS[0]), parent=self,
                                         title="Choose pad color")[1]
        if selected:
            item["color"] = selected
        group = simpledialog.askstring("Sound group", "Group / bank name:",
                                       initialvalue=item.get("bank", "General"), parent=self)
        if group is not None and group.strip():
            item["bank"] = group.strip()
        action = messagebox.askyesnocancel("Sound management",
                                          "Archive/unarchive this pad?\\nYes: toggle archive\\nNo: locate replacement audio\\nCancel: finish")
        if action is True:
            item["archived"] = not item.get("archived", False)
        elif action is False:
            self.relink(item)
        self.save()
        self.refresh()

    def relink(self, item):
        path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav *.mp3 *.ogg")])
        if path:
            item["path"] = path
            self.save()
            self.refresh()

    def update_volume(self):
        for channel in self.playing.values():
            if channel.get_busy():
                channel.set_volume(self.volume.get())

    def poll_playback(self):
        ended = [key for key, channel in self.playing.items() if not channel.get_busy()]
        if ended:
            for key in ended:
                del self.playing[key]
            self.refresh()
        self.after(200, self.poll_playback)

    def stop_all(self):
        pygame.mixer.stop()
        self.playing.clear()
        self.refresh()

    def close(self):
        self.stop_all()
        pygame.mixer.quit()
        self.destroy()


if __name__ == "__main__":
    Soundboard().mainloop()
