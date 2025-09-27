import csv
import os
from typing import List


class NewsItem:
    @classmethod
    def load_from_csv(cls, file_path: str) -> List['NewsItem']:
        """CSVファイルからニュース項目を読み込み、NewsItemのリストを生成する"""
        news_items = []
        if not os.path.exists(file_path):
            print(f"警告: {file_path}が見つかりません。ニュース機能は無効になります。")
            return news_items

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader, None)  # ヘッダー行をスキップ

                for row in csv_reader:
                    if len(row) >= 4:
                        name, content = row[2].strip(), row[3].strip()
                        if name and content:
                            news_items.append(cls(name, content))
            print(f"ニュース項目を{len(news_items)}件読み込みました。")
        except Exception as e:
            print(f"news.csvの読み込み中にエラーが発生しました: {e}")

        return news_items

    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content
