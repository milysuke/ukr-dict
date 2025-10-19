#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV → JSON batch converter for the dictionary project.
(robust version)
"""
import json, os, sys, hashlib, traceback
from typing import List, Tuple

CFG_PATH = "config.json"
MAN_PATH = "datasets-manifest.json"

def minify(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def sha12(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()[:12]

def read_text_any(path: str) -> Tuple[str, str]:
    with open(path, "rb") as f:
        b = f.read()
    if b.startswith(b"\xff\xfe"): return b.decode("utf-16le"), "utf-16le"
    if b.startswith(b"\xfe\xff"): return b.decode("utf-16be"), "utf-16be"
    if b.startswith(b"\xef\xbb\xbf"): return b.decode("utf-8-sig"), "utf-8-sig"
    for enc in ("utf-8", "cp932", "latin-1"):
        try: return b.decode(enc), enc
        except UnicodeDecodeError: pass
    return b.decode("utf-8", errors="replace"), "utf-8* (replace)"

def autodelim(line: str) -> str:
    return "\t" if ("\t" in line) else ","

def convert_lines(lines: List[str], src_col: int, dst_col: int, direction: str, label: str):
    rows = []
    for line in lines:
        if not line: continue
        if line.startswith("#;") or line.startswith("//"): continue
        delim = autodelim(line)
        cols = line.split(delim)
        need = max(src_col, dst_col) + 1
        if len(cols) < need: cols += [""]*(need-len(cols))
        src = cols[src_col].strip()
        dst = cols[dst_col].strip()
        if direction == "ja2uk":
            uk, ja = (dst or ""), (src or "")
        else:
            uk, ja = (src or ""), (dst or "")
        if not (uk or ja): continue
        rows.append({"uk": uk, "ja": ja, "src": label})
    return rows

def main() -> int:
    if not os.path.exists(CFG_PATH):
        print("[error] config.json not found", file=sys.stderr); return 1

    with open(CFG_PATH, "r", encoding="utf-8") as rf:
        cfg = json.load(rf)

    files = cfg.get("files", [])
    manifest = {"datasets": []}
    total = 0
    failures = 0

    for f in files:
        try:
            csv_path = f.get("csv")
            if not csv_path:
                print("[skip] entry without 'csv'"); continue

            # Keep this exact behaviour (as requested)
            json_path = f.get("json") or os.path.splitext(csv_path)[0] + ".json"
            label = f.get("label") or csv_path
            direction = f.get("direction", "uk2ja")
            src_col = int(f.get("src_col", 0))
            dst_col = int(f.get("dst_col", 2))

            data_bytes = b""
            if csv_path and os.path.exists(csv_path):
                text, enc = read_text_any(csv_path)
                print(f"[convert] {csv_path} (encoding={enc})")
                text = text.replace("\r\n","\n").replace("\r","\n")
                lines = [ln for ln in text.split("\n") if ln]
                rows = convert_lines(lines, src_col, dst_col, direction, label)
                data = minify(rows)
                os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
                with open(json_path, "w", encoding="utf-8") as wf: wf.write(data)
                data_bytes = data.encode("utf-8")
                total += len(rows)
                print(f"   -> {json_path} ({len(rows)} rows)")
            elif json_path and os.path.exists(json_path):
                with open(json_path, "rb") as rf2: data_bytes = rf2.read()
                print(f"[reuse] {json_path}")
            else:
                print(f"[skip] {csv_path or json_path} not found")

            manifest["datasets"].append({
                "path": json_path, "source": csv_path or "",
                "label": label, "version": sha12(data_bytes) if data_bytes else "noversion"
            })
        except Exception as e:
            failures += 1
            print(f"[error] converting {f} -> {e}", file=sys.stderr)
            traceback.print_exc()

    with open(MAN_PATH, "w", encoding="utf-8") as mf:
        mf.write(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"[done] total rows = {total}, failures = {failures}")
    return 0 if failures == 0 else 2

if __name__ == "__main__":
    sys.exit(main())
