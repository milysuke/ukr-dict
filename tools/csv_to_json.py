# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import json, os, sys, hashlib

ROOT = os.getcwd()
CFG_PATH = os.path.join(ROOT, "config.json")
MAN_PATH = os.path.join(ROOT, "datasets-manifest.json")

def jmin(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def sha_short(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()[:12]

# Read text with auto encoding detection (UTF-16LE/BE, UTF-8 BOM, UTF-8, CP932)
def read_text_any(path: str):
    with open(path, "rb") as f:
        b = f.read()
    if b.startswith(b"\xff\xfe"):
        return b.decode("utf-16le"), "utf-16le"
    if b.startswith(b"\xfe\xff"):
        return b.decode("utf-16be"), "utf-16be"
    if b.startswith(b"\xef\xbb\xbf"):
        return b.decode("utf-8-sig"), "utf-8-sig"
    for enc in ("utf-8", "cp932", "latin-1"):
        try:
            return b.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return b.decode("utf-8", errors="replace"), "utf-8*"

def autodelim(line: str) -> str:
    return "\t" if ("\t" in line) else ","

def convert_lines(lines, src_col, dst_col, direction, label):
    rows = []
    for line in lines:
        if not line:
            continue
        delim = autodelim(line)
        cols = line.split(delim)
        # pad columns
        need = max(src_col, dst_col) + 1
        if len(cols) < need:
            cols += [""] * (need - len(cols))
        src = cols[src_col]
        dst = cols[dst_col]
        if direction == "ja2uk":
            uk, ja = (dst or ""), (src or "")
        else:  # uk2ja
            uk, ja = (src or ""), (dst or "")
        rows.append({"uk": uk, "ja": ja, "src": label})
    return rows

def main():
    if not os.path.exists(CFG_PATH):
        print("config.json not found.", file=sys.stderr)
        sys.exit(1)

    with open(CFG_PATH, "r", encoding="utf-8") as rf:
        cfg = json.load(rf)

    files = cfg.get("files", [])
    manifest = {"datasets": []}
    total_rows = 0

    for f in files:
        csv_path = f.get("csv")
        json_path = f.get("json") or (os.path
