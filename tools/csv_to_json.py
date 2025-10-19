#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sys, hashlib

CFG_PATH = "config.json"
MAN_PATH = "datasets-manifest.json"

def minify(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def sha12(b: bytes):
    return hashlib.sha1(b).hexdigest()[:12]

def read_text_any(path):
    with open(path, "rb") as f:
        b = f.read()
    if b.startswith(b"\xff\xfe"): return b.decode("utf-16le"), "utf-16le"
    if b.startswith(b"\xfe\xff"): return b.decode("utf-16be"), "utf-16be"
    if b.startswith(b"\xef\xbb\xbf"): return b.decode("utf-8-sig"), "utf-8-sig"
    for enc in ("utf-8", "cp932", "latin-1"):
        try: return b.decode(enc), enc
        except UnicodeDecodeError: pass
    return b.decode("utf-8", errors="replace"), "utf-8*"

def autodelim(line: str): return "\t" if ("\t" in line) else ","

def convert_lines(lines, src_col, dst_col, direction, label):
    rows=[]
    for line in lines:
        if not line: continue
        cols = line.split(autodelim(line))
        need = max(src_col, dst_col) + 1
        if len(cols) < need: cols += [""]*(need-len(cols))
        src, dst = cols[src_col], cols[dst_col]
        if direction=="ja2uk": uk, ja = (dst or ""), (src or "")
        else:                 uk, ja = (src or ""), (dst or "")
        rows.append({"uk":uk, "ja":ja, "src":label})
    return rows

def main():
    if not os.path.exists(CFG_PATH):
        print("config.json not found", file=sys.stderr); sys.exit(1)
    with open(CFG_PATH, "r", encoding="utf-8") as rf:
        cfg = json.load(rf)

    files = cfg.get("files", [])
    manifest = {"datasets": []}
    total = 0

    for f in files:
        csv_path = f.get("csv")
        # ★問題の行：絶対にこの1行のままにしてください
   json_path = f.get("json") or os.path.splitext(csv_path)[0] + ".json"
        label = f.get("label") or csv_path
        direction = f.get("direction","uk2ja")
        src_col = int(f.get("src_col",0))
        dst_col = int(f.get("dst_col",2))

        data_bytes = b""
        if csv_path and os.path.exists(csv_path):
            text, enc = read_text_any(csv_path)
            print(f"[convert] {csv_path} (detected {enc})")
            text = text.replace("\r\n","\n").replace("\r","\n")
            rows = convert_lines([ln for ln in text.split("\n") if ln],
                                 src_col, dst_col, direction, label)
            data = minify(rows)
            with open(json_path, "w", encoding="utf-8") as wf: wf.write(data)
            data_bytes = data.encode("utf-8")
            total += len(rows)
            print(f" -> {json_path} ({len(rows)} rows)")
        elif json_path and os.path.exists(json_path):
            with open(json_path, "rb") as rf: data_bytes = rf.read()
            print(f"[reuse] {json_path}")
        else:
            print(f"[skip] {csv_path or json_path} not found")

        manifest["datasets"].append({
            "path": json_path, "source": csv_path or "",
            "label": label, "version": sha12(data_bytes) if data_bytes else "noversion"
        })

    with open(MAN_PATH, "w", encoding="utf-8") as mf:
        mf.write(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"[done] total rows = {total}")

if __name__ == "__main__":
    main()
