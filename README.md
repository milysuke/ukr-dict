# ウクライナ語日本語・日本語ウクライナ語辞典（GitHub Pages 完全版）

この一式と **以下の11個のCSV** を同じリポジトリ直下に置き、GitHub Pages を有効化すると、
ブラウザで検索できる辞書サイトが完成します。

```
jap-ukr.csv
jap-ukr-lat.csv
jap-ukr-yomi.csv
ukr-acc.csv
ukr-frek-pro.csv
ukr-frek-rev.csv
ukr-henka.csv
ukr-jap.csv
ukr-jap-ad.csv
ukr-jap-ad-lat.csv
ukr-jap-lat.csv
```

## 機能
- 🇺🇦↔🇯🇵 逆引き（UK→JA / JA→UK / 両方向）
- 📚 11ファイルの横断検索（ON/OFF）
- 🚀 Web Worker 検索
- 💾 IndexedDB キャッシュ（`datasets-manifest.json` の version による更新判定）
- 🔡 正規化（全角/半角・カナ→ひらがな・濁点/半濁点・長音・約物・アクセント・大小）

## セットアップ（最短）
1. リポジトリ直下にこのフォルダ内のファイル **＋ 上記CSV 11個** を置く
2. GitHub → Settings → Pages → Source: **Deploy from a branch**、Branch: **main** / **/(root)** を選択
3. 公開URL： `https://ユーザー名.github.io/リポジトリ名/`

> CSV は **タブ区切り/カンマ区切りどちらでもOK**（自動判別）。列が2列の場合は不足列は空として扱います。

## ファイル構成
- `index.html` … UI本体（JSON優先、CSVフォールバック）
- `worker.js` … 高速検索＋拡張正規化
- `idb.js` … IndexedDBヘルパ
- `config.json` … 11ファイルの設定（方向：`ja2uk`/`uk2ja`、列番号など）
- `datasets-manifest.json` … JSONのversion管理（Actionsが更新）
- `.github/workflows/csv_to_json.yml` … CSV→JSON 自動変換（コミット時）
- `tools/csv_to_json.py` … 変換スクリプト（自動区切り・不足列許容・方向変換）

## 方向と列の前提
- 既定では **A列=ソース語、C列=ターゲット語** とみなし、
  - `jap-*.csv` は **JA→UK**（日本語→ウクライナ語）
  - `ukr-*.csv` は **UK→JA**（ウクライナ語→日本語）
- 列構成が異なる場合は `config.json` の `src_col` / `dst_col` を修正してください。
