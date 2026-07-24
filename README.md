Wii setting.txt Editor (cross-platform)
=====================================

A small Tkinter GUI to preview the decrypted `setting.txt` (Wii) and edit `AREA`, `VIDEO`, and `GAME` values.

Requirements
- Python 3 (no external packages required)

Usage
- Run the GUI:

  ```bash
  python3 gui.py
  ```

- Click `Open setting.txt` and choose your encrypted `setting.txt` file.
- Edit `AREA`, `VIDEO`, `GAME` fields and click `Save` to overwrite the opened file (it will be re-encrypted).
- Use `Save As...` to write to a different file.

Notes
- The tool uses the standard Wii XOR algorithm (key 0x73B5DBFA) and processes up to 256 bytes, matching common Wii utilities.
- Preview shows the first 1024 characters of the decrypted data; binary tail bytes are preserved when saving.

Files
- `gui.py` — the GUI application
- `decryptsetting.py` / `encrypt.py` — reference scripts included in the repo
- `setting.txt` / `decrypted.txt` — example files (if present)
