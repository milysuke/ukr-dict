#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV(2列) → JSON 辞書変換ツール
- 引数あり: 指定CSVだけ変換
- 引数なし: config.json の datasets[].file を一括変換（無ければ *.csv 全部）
- 文字コード自動判定 (utf-8-sig, utf-8, cp932, shift-jis)
- 生成結果から datasets-manifest.json を更新
"""

import csv
import json
import sys
import os
from pathlib import Path
from typing import Dict, List

ENCODINGS = ["utf-8-sig", "utf-8", "cp932", "shift-jis"]
REPO_ROOT = Path(__file__).resolve().parents[1] if (Path(__file__).parent.name == "tools") else Path(__file__).resolve().parent
CONFIG_PATH = REPO_ROOT / "config.json"
MANIFEST_PATH = REPO_ROOT / "datasets-manifest.json"

def convert_two_col_csv(csv_path: Path) -> Dict[str, str]:
    """2列CSVを dict に変換し、同名.json を出力して dict を返す"""
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found")

    last_error = None
    for enc in ENCODINGS:
        try:
            data: Dict[str, str] = {}
            with csv_path.open("r", encoding=enc, newline="") as f:
                reader = csv.reader(f)
                first = next(reader, None)
                if first is None or len(first) < 2:
                    raise ValueError("CSV は少なくとも2列が必要です")

                # 1行目がヘッダー風でもデータとして取り込む（空値は無視）
                def add_row(row):
                    if len(row) >= 2:
                        k = (row[0] or "").strip()
                        v = (row[1] or "").strip()
                        if k:
                            data[k] = v

                add_row(first)
                for row in reader:
                    add_row(row)

            if not data:
                raise ValueError("データ行がありません")

            json_path = csv_path.with_suffix(".json")
            with json_path.open("w", encoding="utf-8") as jf:
                json.dump(data, jf, ensure_ascii=False, indent=2)

            print(f"✅ {csv_path.name} → {json_path.name}  ({len(data)} entries, enc={enc})")
            return data
        except Exception as e:
            last_error = e
            # 次のエンコーディングへ
            continue
    raise RuntimeError(f"読込失敗: {csv_path} / last error: {last_error}")

def load_config_csv_list() -> List[Path]:
    """config.json(datasets[].file) があればそのCSVを、なければ *.csv を列挙"""
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            datasets = cfg.get("datasets", cfg) if isinstance(cfg, dict) else cfg
            files = []
            for item in datasets:
                f = item.get("file") if isinstance(item, dict) else None
                if not f:
                    continue
                p = REPO_ROOT / f
                if p.suffix.lower() == ".csv":
                    files.append(p)
            if files:
                print(f"ℹ️ config.json から {len(files)} 件の CSV を検出")
                return files
        except Exception as e:
            print(f"⚠️ config.json を読み込めませんでした: {e}")

    files = sorted(REPO_ROOT.glob("*.csv"))
    print(f"ℹ️ ルート直下の *.csv から {len(files)} 件を検出")
    return files

def update_manifest_from_config(converted: List[Path]):
    """config.json があれば、それを元に datasets-manifest.json を更新。なければ簡易生成。"""
    converted_set = {p.with_suffix(".json").name for p in converted}
    manifest = []

    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            datasets = cfg.get("datasets", cfg) if isinstance(cfg, dict) else cfg
            for item in datasets:
                if not isinstance(item, dict):
                    continue
                csv_name = Path(item.get("file", "")).name
                json_name = Path(csv_name).with_suffix(".json").name
                if json_name in converted_set:
                    entry = {
                        "label": item.get("label", json_name),
                        "file": json_name,
                        "direction": item.get("direction", "uk2ja")
                    }
                    manifest.append(entry)
        except Exception as e:
            print(f"⚠️ manifest 生成で config.json を参照できませんでした: {e}")

    if not manifest:
        # 簡易：変換できたJSONだけを列挙
        for p in converted:
            manifest.append({
                "label": p.with_suffix(".json").name,
                "file": p.with_suffix(".json").name,
                "direction": "uk2ja"
            })

    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📝 datasets-manifest.json を更新しました（{len(manifest)} 件）")

def main():
    print("=" * 50)
    print("CSV → JSON 辞書変換ツール (2列専用)")
    print("=" * 50)

    args = [a for a in sys.argv[1:] if a.strip()]
    targets: List[Path] = []

    if args:
        for a in args:
            p = (REPO_ROOT / a) if not a.startswith("/") else Path(a)
            if p.suffix.lower() != ".csv":
                print(f"⚠️ スキップ（CSV拡張子ではない）: {p.name}")
                continue
            targets.append(p)
        if not targets:
            print("❌ 変換対象の CSV がありません（引数の拡張子を確認してください）")
            sys.exit(1)
    else:
        # 引数無し：config.json または *.csv 一括
        targets = load_config_csv_list()
        if not targets:
            print("❌ 変換対象の CSV が見つかりません")
            sys.exit(1)

    converted: List[Path] = []
    for csv_path in targets:
        try:
            convert_two_col_csv(csv_path)
            converted.append(csv_path)
        except Exception as e:
            print(f"❌ 失敗: {csv_path.name} -> {e}")

    if not converted:
        print("❌ 1件も変換できませんでした")
        sys.exit(1)

    # manifest 更新（あると便利）
    try:
        update_manifest_from_config(converted)
    except Exception as e:
        print(f"⚠️ manifest 更新に失敗: {e}")

    print("\n✨ 処理完了")

if __name__ == "__main__":
    main()
