#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
2列のCSV辞書ファイルをJSON形式に変換するシンプルツール
ウクライナ語・日本語辞書用
"""

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