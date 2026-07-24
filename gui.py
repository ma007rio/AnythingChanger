#!/usr/bin/env python3
"""Wii setting.txt editor (cross-platform, Tkinter)

Features:
- Open an encrypted `setting.txt` and preview its decrypted contents
- Edit `AREA`, `VIDEO`, and `GAME` values and save (re-encrypt)
- Save to original `setting.txt` or `Save As...`

No external dependencies; runs on Windows, macOS, Linux with Python 3.
"""
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


def xor_transform(data: bytearray) -> bytearray:
    key = 0x73B5DBFA
    buf = bytearray(data)
    length = min(len(buf), 256)
    for i in range(length):
        buf[i] ^= (key & 0xff)
        key = ((key << 1) & 0xFFFFFFFF) | (key >> 31)
    return buf


def decrypt_bytes(data: bytes) -> bytes:
    return bytes(xor_transform(bytearray(data)))


def encrypt_bytes(data: bytes) -> bytes:
    # symmetric
    return bytes(xor_transform(bytearray(data)))


def parse_setting_values(text: str):
    vals = {}
    for key in ("AREA", "VIDEO", "GAME"):
        m = re.search(rf"^{key}=(.*)$", text, flags=re.MULTILINE)
        vals[key] = m.group(1).strip() if m else ""
    return vals


def replace_setting_values(text: str, new_vals: dict) -> str:
    def _repl(m):
        k = m.group(1)
        return f"{k}={new_vals.get(k, m.group(2))}"

    # Replace AREA, VIDEO, GAME lines if present
    for k in ("AREA", "VIDEO", "GAME"):
        text = re.sub(rf"^{k}=.*$", f"{k}={new_vals.get(k,'')}", text, flags=re.MULTILINE)
    return text


class App:
    def __init__(self, root):
        self.root = root
        root.title("Wii setting.txt Editor")

        frm = ttk.Frame(root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        btnrow = ttk.Frame(frm)
        btnrow.pack(fill=tk.X)

        ttk.Button(btnrow, text="Open setting.txt", command=self.open_file).pack(side=tk.LEFT)
        ttk.Button(btnrow, text="Save", command=self.save_file).pack(side=tk.LEFT)
        ttk.Button(btnrow, text="Save As...", command=self.save_as).pack(side=tk.LEFT)

        fields = ttk.Frame(frm, padding=(0, 10, 0, 10))
        fields.pack(fill=tk.X)

        ttk.Label(fields, text="AREA:").grid(row=0, column=0, sticky=tk.W)
        self.area_var = tk.StringVar()
        self.area_entry = ttk.Entry(fields, textvariable=self.area_var, width=20)
        self.area_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(fields, text="VIDEO:").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        self.video_var = tk.StringVar()
        self.video_entry = ttk.Entry(fields, textvariable=self.video_var, width=20)
        self.video_entry.grid(row=0, column=3, sticky=tk.W)

        ttk.Label(fields, text="GAME:").grid(row=0, column=4, sticky=tk.W, padx=(10,0))
        self.game_var = tk.StringVar()
        self.game_entry = ttk.Entry(fields, textvariable=self.game_var, width=10)
        self.game_entry.grid(row=0, column=5, sticky=tk.W)

        preview_label = ttk.Label(frm, text="Decrypted preview (first 1024 chars):")
        preview_label.pack(anchor=tk.W)

        self.text = tk.Text(frm, wrap=tk.NONE, height=20)
        self.text.pack(fill=tk.BOTH, expand=True)

        self.filepath = None
        self.orig_data = None

    def open_file(self):
        path = filedialog.askopenfilename(title="Open setting.txt", filetypes=[("All files","*")])
        if not path:
            return
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")
            return

        dec = decrypt_bytes(data)
        # Decode with latin-1 to preserve raw bytes
        dec_text = dec.decode('latin-1', errors='replace')
        preview = dec_text[:1024]
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', preview)

        vals = parse_setting_values(dec_text)
        self.area_var.set(vals.get('AREA',''))
        self.video_var.set(vals.get('VIDEO',''))
        self.game_var.set(vals.get('GAME',''))

        self.filepath = path
        self.orig_data = data
        self.root.title(f"Wii setting.txt Editor — {os.path.basename(path)}")

    def _gather_new_vals(self):
        return {'AREA': self.area_var.get(), 'VIDEO': self.video_var.get(), 'GAME': self.game_var.get()}

    def save_file(self):
        if not self.filepath or not self.orig_data:
            messagebox.showinfo("Info", "Open a `setting.txt` file first.")
            return
        try:
            dec = decrypt_bytes(self.orig_data)
            dec_text = dec.decode('latin-1', errors='replace')
            new_text = replace_setting_values(dec_text, self._gather_new_vals())
            # Rebuild bytes preserving length: encode latin-1
            new_bytes = new_text.encode('latin-1') + dec[len(new_text.encode('latin-1')):]
            enc = encrypt_bytes(new_bytes)
            with open(self.filepath, 'wb') as f:
                f.write(enc)
            messagebox.showinfo("Saved", f"Saved and re-encrypted {self.filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def save_as(self):
        if not self.orig_data:
            messagebox.showinfo("Info", "Open a `setting.txt` file first.")
            return
        path = filedialog.asksaveasfilename(title="Save setting.txt as", defaultextension=".txt")
        if not path:
            return
        try:
            dec = decrypt_bytes(self.orig_data)
            dec_text = dec.decode('latin-1', errors='replace')
            new_text = replace_setting_values(dec_text, self._gather_new_vals())
            new_bytes = new_text.encode('latin-1') + dec[len(new_text.encode('latin-1')):]
            enc = encrypt_bytes(new_bytes)
            with open(path, 'wb') as f:
                f.write(enc)
            messagebox.showinfo("Saved", f"Saved and re-encrypted {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")


def main():
    root = tk.Tk()
    app = App(root)
    root.geometry('900x600')
    root.mainloop()


if __name__ == '__main__':
    main()
