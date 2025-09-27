import os
# sourceフォルダからゲームのロジックを読み込む
# これで RiceGameWindow クラスが使えるようになる
from source.rice_game_window import RiceGameWindow


def main():
    """メイン関数"""
    print("=== ファミコン風米価格アドベンチャー v1.7 ===")
    print("新機能: ニュースCSV連携")
    print("")
    print("使用方法:")
    print("- ゲームは自動で進行し、通常は5秒ごとに月が変わります")
    print("- 月の切り替わり時、10-36%の確率でニュースが表示されます")
    print("- ニュースは4秒間表示され、その後キャラクター会話が5秒間表示されます")
    print("- スペースキーでメッセージを進められます")
    print("")
    print("必要ファイル・フォルダ構成:")
    print("- assets/data/news.csv: C列に名前、D列に本文を記載")
    print("- assets/images/characters/ - キャラクター画像")
    print("- assets/images/backgrounds/ - 背景画像（spring.png, summer.png, autumn.png, winter.png）")
    print("- assets/images/rice/ - 米関連画像")
    print("- assets/images/ui/ - UI要素画像")
    print("- assets/sounds/ - 音声ファイル (.mp3, .wav)")
    print("- assets/fonts/ - フォントファイル (.ttf)")
    print("")
    print("※ 画像ファイルが見つからない場合は代替表示されます")
    print("※ news.csv が見つからない場合、ニュース機能は無効になります")
    print("")
    print("フォント確認:")

    # フォント確認 (main関数内でpygame.init()を再度呼ぶのは避ける)
    # pygame.init()はRiceGameWindowの__init__で一度だけ呼ばれます。
    # ここでは、フォントが正しくロードされるかどうかの確認メッセージを表示します。
    font_check_path = os.path.join('assets', 'fonts', 'x12y16pxMaruMonica.ttf')
    if os.path.exists(font_check_path):
        print(f"- \"{font_check_path}\" が見つかりました。ファミコン風フォントとして使用を試みます。")
    else:
        print(f"- \"{font_check_path}\" が見つかりません。システムフォントまたはデフォルトフォントを使用します。")
        print("  ファミコン風フォントを使用するには、'assets/fonts'フォルダを作成し、その中にフォントファイルを配置してください。")

    # CSVファイル確認
    csv_check_path = os.path.join("assets", "data", "news.csv")
    if os.path.exists(csv_check_path):
        print(f"- \"{csv_check_path}\" が見つかりました。ニュース機能が有効になります。")
    else:
        print(f"- \"{csv_check_path}\" が見つかりません。ニュース機能は無効になります。")
        print("  ニュース機能を使用するには、'assets/data'フォルダを作成し、'news.csv'を配置してください。")

    print("\nゲームを開始します...")

    game = RiceGameWindow()
    game.run()

if __name__ == "__main__":
    main()
