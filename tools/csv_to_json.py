#!/usr/bin/env python3
# -*- coding: utf-8 -*-
<<<<<<< HEAD
=======
"""
CSV → JSON batch converter for the dictionary project.
(robust version)
"""
import json, os, sys, hashlib, traceback
from typing import List, Tuple
>>>>>>> 55e5f142effe473b9686a47420bc1e4ee48c27a6

"""
2列のCSV辞書ファイルをJSON形式に変換するシンプルツール
ウクライナ語・日本語辞書用
"""

<<<<<<< HEAD
import csv
import json
import sys
import os
from pathlib import Path

def csv_to_json(csv_file_path):
    """
    2列のCSVファイルをJSON形式に変換する
    A列をキー、B列を値として使用
    
    Parameters:
    -----------
    csv_file_path : str
        入力CSVファイルのパス
    """
    
    # 出力ファイル名を設定（同じ名前で拡張子を.jsonに変更）
    json_file_path = Path(csv_file_path).with_suffix('.json')
    
    # 複数のエンコーディングを試す
    encodings = ['utf-8-sig', 'utf-8', 'shift-jis', 'cp932']
    
    for encoding in encodings:
        try:
            print(f"📖 {encoding} で読み込み中...")
            
            with open(csv_file_path, 'r', encoding=encoding) as csv_file:
                # CSVを読み込む
                csv_reader = csv.reader(csv_file)
                
                # ヘッダー行をスキップ（存在する場合）
                first_row = next(csv_reader, None)
                if not first_row or len(first_row) < 2:
                    print("❌ エラー: CSVファイルには少なくとも2列必要です")
                    sys.exit(1)
                
                # 最初の行がヘッダーかデータか判定
                # （両方が日本語/ウクライナ語文字を含む可能性があるため、データとして扱う）
                dictionary = {}
                
                # 最初の行も処理
                if len(first_row) >= 2 and first_row[0] and first_row[1]:
                    # ヘッダーっぽい場合（例：「Ukrainian」「Japanese」など）はスキップ
                    if not (first_row[0].lower() in ['ukrainian', 'japanese', 'word', 'translation', '単語', '翻訳', 'a', 'b']):
                        dictionary[first_row[0].strip()] = first_row[1].strip()
                
                # 残りの行を処理
                row_count = 0
                for row in csv_reader:
                    row_count += 1
                    if len(row) >= 2:
                        key = row[0].strip() if row[0] else ""
                        value = row[1].strip() if row[1] else ""
                        
                        # キーが空でない場合のみ追加
                        if key:
                            dictionary[key] = value
                
                # 辞書が空でなければ成功
                if dictionary:
                    # JSONファイルとして保存
                    with open(json_file_path, 'w', encoding='utf-8') as json_file:
                        json.dump(dictionary, json_file, 
                                 ensure_ascii=False,  # 非ASCII文字をそのまま保存
                                 indent=2,            # 見やすいインデント
                                 sort_keys=False)     # 元の順序を保持
                    
                    print(f"\n✅ 変換成功！")
                    print(f"📂 入力ファイル: {csv_file_path}")
                    print(f"📄 出力ファイル: {json_file_path}")
                    print(f"📊 変換された単語数: {len(dictionary)} 個")
                    print(f"\n最初の5個の例:")
                    
                    # 最初の5個を表示
                    count = 0
                    for k, v in dictionary.items():
                        if count >= 5:
                            break
                        print(f"  {k} → {v}")
                        count += 1
                    
                    return dictionary
                else:
                    print("⚠️  データが見つかりませんでした")
                    continue
                    
        except UnicodeDecodeError:
            continue  # 次のエンコーディングを試す
        except Exception as e:
            print(f"⚠️  {encoding} での読み込みに失敗: {str(e)}")
            continue
    
    print(f"\n❌ エラー: ファイルを読み込めませんでした")
    print("Excelで保存する際は、「CSV UTF-8 (コンマ区切り)」形式を選択してください")
    sys.exit(1)

def main():
    """メイン関数"""
    
    print("=" * 50)
    print("CSV → JSON 辞書変換ツール (2列専用)")
    print("=" * 50)
    
    # コマンドライン引数をチェック
    if len(sys.argv) < 2:
        print("\n📝 使い方:")
        print("  python csv_to_json.py [CSVファイル名]")
        print("\n例:")
        print("  python csv_to_json.py dictionary.csv")
        print("\n説明:")
        print("  ・A列の内容をキー、B列の内容を値としてJSON形式に変換します")
        print("  ・ウクライナ語、日本語、英語などに対応")
        print("  ・文字コードは自動判定されます")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # ファイルの存在を確認
    if not os.path.exists(csv_file):
        print(f"❌ エラー: ファイル '{csv_file}' が見つかりません")
        print(f"現在のフォルダ: {os.getcwd()}")
        print("\nファイル名を確認してください（拡張子 .csv も含める）")
        sys.exit(1)
    
    # ファイル形式の確認
    if not csv_file.lower().endswith('.csv'):
        print(f"⚠️  警告: ファイル '{csv_file}' は .csv 拡張子ではありません")
        response = input("続行しますか？ (y/n): ")
        if response.lower() != 'y':
            print("処理を中止しました")
            sys.exit(0)
    
    print(f"\n🔄 変換を開始します: {csv_file}")
    
    # 変換を実行
    csv_to_json(csv_file)
    
    print("\n✨ 処理が完了しました！")
    print("JSONファイルが作成されました。メモ帳やVSCodeなどで確認できます。")

if __name__ == "__main__":
    main()
=======
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
>>>>>>> 55e5f142effe473b9686a47420bc1e4ee48c27a6
