#!/usr/bin/env python3
"""Simple GUI editor for churches.json without exposing raw JSON."""

from __future__ import annotations

import json
import shutil
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


JSON_FILE = Path(__file__).with_name("churches.json")
FIELD_SPECS = [
    ("name", "Name"),
    ("charityNumber", "Charity Number"),
    ("region", "Region"),
    ("url", "Charity URL"),
    ("urlPeople", "People URL (optional)"),
    ("faceBook", "Facebook URL (optional)"),
    ("website", "Website URL (optional)"),
]
REQUIRED_FIELDS = ["name", "charityNumber", "region", "url"]
OPTIONAL_FIELDS = ["urlPeople", "faceBook", "website"]


class ChurchesEditor:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Church Directory Editor")
        self.root.geometry("880x560")

        self.data = self._load_data()
        self.selected_index: int | None = None

        self.name_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.fields: dict[str, tk.Text | ttk.Combobox] = {}

        self._build_ui()
        self._populate_name_dropdown()
        if self.data:
            self.name_combo.current(0)
            self._on_name_selected()

    def _load_data(self) -> list[dict]:
        if not JSON_FILE.exists():
            messagebox.showerror("Missing File", f"Cannot find {JSON_FILE}")
            raise SystemExit(1)

        try:
            with JSON_FILE.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
        except json.JSONDecodeError as exc:
            messagebox.showerror("Invalid JSON", f"Could not parse churches.json:\n{exc}")
            raise SystemExit(1)

        if not isinstance(loaded, list):
            messagebox.showerror("Invalid Format", "churches.json must contain a JSON array.")
            raise SystemExit(1)

        return loaded

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Select Church:").pack(side=tk.LEFT)
        self.name_combo = ttk.Combobox(
            top,
            textvariable=self.name_var,
            state="readonly",
            width=60,
        )
        self.name_combo.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        self.name_combo.bind("<<ComboboxSelected>>", lambda _e: self._on_name_selected())

        form_frame = ttk.Frame(self.root, padding=(12, 4, 12, 12))
        form_frame.pack(fill=tk.BOTH, expand=True)
        form_frame.columnconfigure(1, weight=1)

        for row, (field_key, label_text) in enumerate(FIELD_SPECS):
            ttk.Label(form_frame, text=label_text + ":").grid(
                row=row,
                column=0,
                sticky="nw",
                padx=(0, 8),
                pady=6,
            )

            if field_key == "region":
                widget = ttk.Combobox(
                    form_frame,
                    values=["North", "South", "East", "West"],
                    state="readonly",
                )
                widget.grid(row=row, column=1, sticky="ew", pady=6)
            else:
                widget = tk.Text(form_frame, height=2, wrap="word")
                widget.grid(row=row, column=1, sticky="ew", pady=6)

            self.fields[field_key] = widget

        button_row = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        button_row.pack(fill=tk.X)

        ttk.Button(button_row, text="Save Changes", command=self.save_current_record).pack(
            side=tk.LEFT
        )
        ttk.Button(button_row, text="Reload File", command=self.reload_data).pack(
            side=tk.LEFT,
            padx=8,
        )
        ttk.Button(button_row, text="Quit", command=self.root.quit).pack(side=tk.RIGHT)

        ttk.Label(self.root, textvariable=self.status_var, padding=(12, 0, 12, 12)).pack(
            anchor="w"
        )

    def _populate_name_dropdown(self) -> None:
        names = [self._display_name(item, idx) for idx, item in enumerate(self.data)]
        self.name_combo["values"] = names

    def _display_name(self, item: dict, idx: int) -> str:
        name = (item.get("name") or "").strip()
        return name if name else f"Record {idx + 1}"

    def _on_name_selected(self) -> None:
        idx = self.name_combo.current()
        if idx < 0:
            return

        self.selected_index = idx
        item = self.data[idx]

        for field_key, _label in FIELD_SPECS:
            value = str(item.get(field_key, "") or "")
            widget = self.fields[field_key]
            if isinstance(widget, ttk.Combobox):
                widget.set(value)
            else:
                widget.delete("1.0", tk.END)
                widget.insert("1.0", value)

        self.status_var.set(f"Loaded: {self._display_name(item, idx)}")

    def _collect_form_values(self) -> dict[str, str]:
        values: dict[str, str] = {}
        for field_key, _label in FIELD_SPECS:
            widget = self.fields[field_key]
            if isinstance(widget, ttk.Combobox):
                values[field_key] = widget.get().strip()
            else:
                values[field_key] = widget.get("1.0", tk.END).strip()
        return values

    def save_current_record(self) -> None:
        if self.selected_index is None:
            messagebox.showwarning("No Selection", "Select a church record first.")
            return

        form_values = self._collect_form_values()

        missing = [key for key in REQUIRED_FIELDS if not form_values.get(key)]
        if missing:
            messagebox.showwarning(
                "Missing Required Fields",
                "Please complete required fields: " + ", ".join(missing),
            )
            return

        # Build ordered record so amended entries keep a consistent field layout.
        amended = OrderedDict()
        amended["name"] = form_values["name"]
        amended["charityNumber"] = form_values["charityNumber"]
        amended["region"] = form_values["region"]
        amended["url"] = form_values["url"]
        amended["urlPeople"] = form_values.get("urlPeople", "")
        amended["faceBook"] = form_values.get("faceBook", "")
        amended["website"] = form_values.get("website", "")

        self.data[self.selected_index] = amended
        self._write_data()

        self._populate_name_dropdown()
        self.name_combo.current(self.selected_index)
        self.status_var.set(f"Saved: {amended['name']}")
        messagebox.showinfo("Saved", "Record updated and churches.json saved.")

    def _write_data(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = JSON_FILE.with_suffix(f".backup-{timestamp}.json")
        shutil.copy2(JSON_FILE, backup)

        with JSON_FILE.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    def reload_data(self) -> None:
        self.data = self._load_data()
        self._populate_name_dropdown()
        if self.data:
            self.name_combo.current(0)
            self._on_name_selected()
        self.status_var.set("Reloaded churches.json")


def main() -> None:
    root = tk.Tk()
    ChurchesEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
