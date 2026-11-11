"""Masqrayd Soundboard standalone Windows prototype.

Run: py -m pip install -r standalone/requirements.txt
     py standalone/soundboard.py
Sound plays through the Windows default audio device.
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
        self.drag_start = None
        self.selected_pad = None
        self.shape = tk.StringVar(value="Square")
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
        self.status = tk.Label(self, text="Ready • Playing through Windows default audio output",
                               bg="#202127", fg="#b7b5bd", anchor="w")
        self.status.pack(fill="x", padx=14, pady=8)
        self.shape_menu = ttk.Combobox(header, textvariable=self.shape, values=["Square", "Rectangle", "Compact"], width=12, state="readonly")
        self.shape_menu.pack(side="right", padx=8)
        self.shape_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh())

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
        size = {"Square": (124, 124), "Rectangle": (168, 92), "Compact": (96, 96)}[self.shape.get()]
        width, height = size
        count = max(1, self.canvas.winfo_width() // (width + 14))
        query = self.search.get().casefold()
        visible = [x for x in self.items if
                   (self.show_archived.get() or not x.get("archived")) and
                   (self.bank.get() == "All" or x.get("bank", "General") == self.bank.get()) and
                   query in x.get("label", "").casefold()]
        for index, item in enumerate(visible):
            playing = item["id"] in self.playing and self.playing[item["id"]].get_busy()
            selected = self.selected_pad == item["id"] and self.edit_mode.get()
            tile = tk.Label(self.grid_frame, text=item["label"][:45], width=1, height=1,
                            font=("Segoe UI", 10, "bold"), wraplength=width-16,
                            justify="center", anchor="center", cursor="fleur" if self.edit_mode.get() else "hand2",
                            bg="#d72e45" if playing else item.get("color", COLORS[0]),
                            fg="white", relief="solid" if selected else "flat", bd=3 if selected else 1)
            tile.grid(row=index // count, column=index % count, padx=6, pady=6)
            tile.grid_propagate(False)
            tile.configure(width=width, height=height)
            # Grid's pixel sizing comes from a fixed-size outer frame, not label character units.
            tile.grid_forget()
            holder = tk.Frame(self.grid_frame, width=width, height=height, bg="#202127")
            holder.grid(row=index // count, column=index % count, padx=6, pady=6)
            holder.grid_propagate(False)
            tile.place(in_=holder, x=0, y=0, relwidth=1, relheight=1)
            self.pad_buttons[item["id"]] = tile
            tile.bind("<ButtonPress-1>", lambda e, x=item: self.pad_press(e, x))
            tile.bind("<B1-Motion>", self.pad_motion)
            tile.bind("<ButtonRelease-1>", lambda e, x=item: self.pad_release(e, x))
            tile.bind("<Button-3>", lambda e, x=item: self.pad_menu(e, x))
        self.grid_frame.update_idletasks()

    def pad_press(self, event, item):
        self.dragging = item["id"]
        self.drag_start = (event.x_root, event.y_root)

    def pad_motion(self, event):
        if not self.edit_mode.get() or not self.dragging:
            return
        x, y = self.winfo_pointerxy()
        for key, pad in self.pad_buttons.items():
            pad.configure(relief="solid" if key != self.dragging and
                          pad.winfo_rootx() <= x < pad.winfo_rootx() + pad.winfo_width() and
                          pad.winfo_rooty() <= y < pad.winfo_rooty() + pad.winfo_height() else "flat")

    def pad_release(self, event, item):
        source_id = self.dragging
        self.dragging = None
        if not self.edit_mode.get():
            self.play(item)
            return
        x, y = self.winfo_pointerxy()
        moved = self.drag_start is not None and (
            abs(x - self.drag_start[0]) + abs(y - self.drag_start[1]) >= 8)
        self.drag_start = None
        if moved:
            target_id = next((key for key, pad in self.pad_buttons.items()
                              if pad.winfo_rootx() <= x < pad.winfo_rootx() + pad.winfo_width()
                              and pad.winfo_rooty() <= y < pad.winfo_rooty() + pad.winfo_height()), None)
            if target_id and target_id != source_id:
                self.selected_pad = None
                self.move_pad(source_id, target_id)
            else:
                self.refresh()
        elif self.selected_pad and self.selected_pad != item["id"]:
            selected = self.selected_pad
            self.selected_pad = None
            self.move_pad(selected, item["id"])
        else:
            self.selected_pad = None if self.selected_pad == item["id"] else item["id"]
            self.status.configure(text="Select destination pad to move" if self.selected_pad else "Selection cleared")
            self.refresh()

    def move_pad(self, source_id, target_id):
        source = next((x for x in self.items if x["id"] == source_id), None)
        target = next((x for x in self.items if x["id"] == target_id), None)
        if source and target and source != target:
            self.items.remove(source)
            self.items.insert(self.items.index(target), source)
            self.save()
            self.status.configure(text="Pad arrangement saved")
        self.refresh()

    def pad_menu(self, event, item):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Change color...", command=lambda: self.change_color(item))
        menu.add_command(label="Rename...", command=lambda: self.rename_pad(item))
        menu.add_command(label="Change group...", command=lambda: self.change_group(item))
        menu.add_separator()
        menu.add_command(label="Move to first", command=lambda: self.move_to_edge(item, True))
        menu.add_command(label="Move to last", command=lambda: self.move_to_edge(item, False))
        menu.add_command(label="Move left", command=lambda: self.move_by(item, -1))
        menu.add_command(label="Move right", command=lambda: self.move_by(item, 1))
        menu.add_separator()
        menu.add_command(label="Relink audio...", command=lambda: self.relink(item))
        menu.add_command(label="Unarchive" if item.get("archived") else "Archive",
                         command=lambda: self.toggle_archive(item))
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()

    def change_color(self, item):
        color = colorchooser.askcolor(color=item.get("color", COLORS[0]), parent=self)[1]
        if color:
            item["color"] = color
            self.save()
            self.refresh()

    def rename_pad(self, item):
        label = simpledialog.askstring("Rename pad", "Label:", initialvalue=item["label"], parent=self)
        if label and label.strip():
            item["label"] = label.strip()
            self.save()
            self.refresh()

    def change_group(self, item):
        bank = simpledialog.askstring("Sound group", "Group:", initialvalue=item.get("bank", "General"), parent=self)
        if bank and bank.strip():
            item["bank"] = bank.strip()
            self.save()
            self.refresh()

    def toggle_archive(self, item):
        item["archived"] = not item.get("archived", False)
        self.save()
        self.refresh()

    def move_by(self, item, offset):
        i = self.items.index(item)
        j = max(0, min(len(self.items)-1, i+offset))
        self.items.insert(j, self.items.pop(i))
        self.save()
        self.refresh()

    def move_to_edge(self, item, first):
        self.items.remove(item)
        self.items.insert(0 if first else len(self.items), item)
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
