import random
import json
import os
import sys

def resource_path(relative_path):
    """ 実行ファイル（.exe) とソースコードの両方でリソースへのパスを解決する """
    try:
        # PyInstallerが作成する一時フォルダ
        base_path = sys._MEIPASS
    except Exception:
        # 通常のPython環境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Character:
    @classmethod
    def create_from_config(cls, name: str, role: str, role_id: str):
        """指定された役割IDからメッセージと画像を読み込み、Characterインスタンスを生成する"""
        # role_idから画像パスとメッセージパスを生成
        image_path = resource_path(os.path.join('assets', 'images', f'{role_id}.png'))
        message_path = resource_path(os.path.join('assets', 'messages', f'{role_id}.json'))

        default_messages = {
            "low_price": {"threshold": 300, "messages": ["..."]},
            "medium_price": {"threshold": 500, "messages": ["..."]},
            "high_price": {"messages": ["..."]}
        }

        messages = default_messages
        if not os.path.exists(message_path):
            print(f"警告: メッセージファイルが見つかりません: {message_path}")
        else:
            try:
                with open(message_path, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            except Exception as e:
                print(f"エラー: メッセージファイルの読み込みに失敗しました: {message_path}, {e}")

        return cls(name, role, image_path, messages)

    def __init__(self, name: str, role: str, image_path: str, messages: dict):
        self.name = name
        self.role = role
        self.image_path = image_path
        self.image = None
        self.messages = messages

    def get_message(self, price: int) -> str:
        """価格に応じてキャラクターのメッセージを生成"""
        # 低価格帯から順にチェック
        low_price_data = self.messages.get("low_price", {})
        if price < low_price_data.get("threshold", 300):
            message_list = low_price_data.get("messages", ["..."])
            return random.choice(message_list)

        medium_price_data = self.messages.get("medium_price", {})
        if price < medium_price_data.get("threshold", 500):
            message_list = medium_price_data.get("messages", ["..."])
            return random.choice(message_list)

        # 上記のいずれにも当てはまらない場合は高価格帯
        else:
            high_price_data = self.messages.get("high_price", {})
            message_list = high_price_data.get("messages", ["..."])
            return random.choice(message_list)
