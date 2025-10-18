#!/usr/bin/env python3
import json, os, sys, hashlib
ROOT = os.getcwd()
CFG_PATH = os.path.join(ROOT, "config.json")
MAN_PATH = os.path.join(ROOT, "datasets-manifest.json")

def read_text(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def write_text(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)

def minify(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",",":"))

def sha_short(b: bytes):
    return hashlib.sha1(b).hexdigest()[:12]

def autodelim(line: str):
    return "\t" if ("\t" in line) else ","

def convert_lines(lines, src_col, dst_col, direction, label):
    rows = []
    for line in lines:
        if not line:
            continue
        delim = autodelim(line)
        cols = line.split(delim)
        while len(cols) <= max(src_col, dst_col):
            cols.append("")
        src = cols[src_col] if src_col < len(cols) else ""
        dst = cols[dst_col] if dst_col < len(cols) else ""
        if direction == "ja2uk":
            uk = dst or ""
            ja = src or ""
        else:
            uk = src or ""
            ja = dst or ""
        rows.append({"uk": uk, "ja": ja, "src": label})
    return rows

def main():
    if not os.path.exists(CFG_PATH):
        print("config.json not found.", file=sys.stderr); sys.exit(1)
    cfg = json.loads(read_text(CFG_PATH))
    files = cfg.get("files", [])
    manifest = {"datasets": []}
    total = 0
    for f in files:
        csv_path = f.get("csv")
        json_path = f.get("json") or (os.path.splitext(csv_path)[0] + ".json")
        label = f.get("label") or csv_path
        direction = f.get("direction","uk2ja")
        src_col = int(f.get("src_col",0))
        dst_col = int(f.get("dst_col",2))

        data_bytes = b""
        if csv_path and os.path.exists(csv_path):
            text = read_text(csv_path).replace("\r\n","\n").replace("\r","\n")
            lines = [ln for ln in text.split("\n") if ln]
            rows = convert_lines(lines, src_col, dst_col, direction, label)
            data = minify(rows)
            write_text(json_path, data)
            data_bytes = data.encode("utf-8")
            total += len(rows)
            print(f"Converted {csv_path} -> {json_path} ({len(rows)} rows)")
        elif json_path and os.path.exists(json_path):
            data_bytes = open(json_path, "rb").read()
            print(f"Using existing JSON {json_path}")
        else:
            print(f"Skip: {csv_path or json_path} not found")

        version = sha_short(data_bytes) if data_bytes else "noversion"
        manifest['datasets'].append({"path": json_path, "source": csv_path or "", "label": label, "version": version})

    write_text(MAN_PATH, json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"Updated manifest. Total rows: {total}")

if __name__ == "__main__":
    main()
