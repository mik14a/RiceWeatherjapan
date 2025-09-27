import pygame
import random
import time
import os
import csv
import json
from typing import Dict, List, Tuple, Optional
from PIL import Image

from source.character import Character
from source.news_item import NewsItem

class RiceGameWindow:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("ファミコン風米価格アドベンチャー")

        # 日本語フォント設定 - PressStart2Pを優先
        self.font_large = self.load_japanese_font(40)
        self.font_medium = self.load_japanese_font(36)
        self.font_small = self.load_japanese_font(34)

        # 色定義（ファミコン風カラーパレット）
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'blue': (0, 88, 248),
            'green': (0, 168, 0),
            'red': (248, 56, 0),
            'yellow': (252, 252,  6),
            'gray': (128, 128, 128),
            'dark_blue': (0, 0, 128),
            'text_bg': (24, 24, 88),
            'news_bg': (88, 24, 24)  # ニュース用背景色
        }

        # ゲーム状態
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_month = 1
        self.rice_price = 400
        self.last_update = time.time()

        # ニュースシステム
        self.news_items = NewsItem.load_from_csv(os.path.join("assets", "data", "news.csv"))
        self.showing_news = False
        self.current_news = None
        self.news_start_time = 0
        self.news_duration = 6.0  # ニュース表示時間（4秒）
        self.character_message_duration = 5.0  # キャラクター会話時間（5秒）

        # キャラクター設定
        self.characters = [
            Character.create_from_config("田中さん", "主婦", "housewife"),
            Character.create_from_config("山田さん", "農家", "farmer"),
            Character.create_from_config("佐藤議員", "政治家", "politician")
        ]
        self.current_speaker = 0

        # テキスト表示用
        self.current_message = ""
        self.display_message = ""
        self.message_index = 0
        self.last_char_time = 0
        self.char_delay = 100  # ミリ秒

        # 画像フォルダ
        self.image_folders = {
            'characters': os.path.join('assets', 'images', 'characters/'),
            'backgrounds': os.path.join('assets', 'images', 'backgrounds/'),
            'rice': os.path.join('assets', 'images', 'rice/'),
            'ui': os.path.join('assets', 'images', 'ui/')
        }

        # --- Sound Setup ---
        try:
            pygame.mixer.init() # Initialize the mixer module
            print("Pygame mixer initialized successfully.")
        except pygame.error as e:
            print(f"Error initializing pygame mixer: {e}")
            print("Sound playback will be disabled.")
            self.mixer_available = False
        else:
            self.mixer_available = True

        # Define sound file paths (assuming a 'sounds' folder)
        self.sound_files = {
            "month_change": os.path.join("assets", "sounds", "month_change.wav"),
            "text_click": os.path.join("assets", "sounds", "text_click.wav"),
            "background_music": os.path.join("assets", "sounds", "background_music.mp3"),
            "news_alert": os.path.join("assets", "sounds", "news_alert.wav")  # ニュース開始音
        }
        self.loaded_sounds = {}
        self.load_sounds()
        # --- End Sound Setup ---

        # 背景画像（季節別）
        self.background_images = {}
        self.load_resources()

    def should_show_news(self) -> bool:
        """ニュースを表示するかどうかを決定（10-36%の確率）"""
        if not self.news_items:
            return False

        probability = random.randint(10, 36)
        return random.randint(1, 100) <= probability

    def select_random_news(self) -> Optional[NewsItem]:
        """ランダムなニュース項目を選択"""
        if not self.news_items:
            return None
        return random.choice(self.news_items)

    def load_sounds(self):
        """Loads sound files into the mixer."""
        if not self.mixer_available:
            return

        for name, path in self.sound_files.items():
            if os.path.exists(path):
                try:
                    if name == "background_music":
                        # For background music, we'll load it directly in play_background_music
                        pass
                    else:
                        self.loaded_sounds[name] = pygame.mixer.Sound(path)
                        print(f"Loaded sound: {name} from {path}")
                except pygame.error as e:
                    print(f"Error loading sound file {path}: {e}")
            else:
                print(f"Sound file not found: {path}")

    def play_sound_effect(self, sound_name: str):
        """Plays a sound effect if the mixer is available and the sound is loaded."""
        if not self.mixer_available:
            return

        if sound_name in self.loaded_sounds:
            try:
                self.loaded_sounds[sound_name].play()
            except pygame.error as e:
                print(f"Error playing sound effect '{sound_name}': {e}")
        else:
            print(f"Sound effect '{sound_name}' not found or not loaded.")

    def play_background_music(self):
        """Plays the background music, looping indefinitely, if mixer is available."""
        if not self.mixer_available:
            return

        music_path = self.sound_files.get("background_music")
        if music_path and os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1) # -1 for infinite loop
                print(f"Playing background music: {music_path}")
            except pygame.error as e:
                print(f"Error playing background music {music_path}: {e}")
        else:
            print("Background music file not found or not specified.")

    def stop_background_music(self):
        """Stops the background music if the mixer is available."""
        if self.mixer_available:
            pygame.mixer.music.stop()
            print("Background music stopped.")

    def load_resources(self):
        """リソースを読み込み"""
        # フォルダが存在しない場合は作成
        for folder in self.image_folders.values():
            if not os.path.exists(folder):
                os.makedirs(folder)

        # 画像読み込み（存在する場合）
        try:
            # キャラクター画像の読み込み
            for char in self.characters:
                if os.path.exists(char.image_path):
                    char.image = pygame.image.load(char.image_path)
                    char.image = pygame.transform.scale(char.image, (120, 120))

            # 背景画像の読み込み（季節別）
            seasons = ['spring', 'summer', 'autumn', 'winter']
            for season in seasons:
                bg_path = os.path.join(self.image_folders['backgrounds'], f"{season}.png")
                if os.path.exists(bg_path):
                    self.background_images[season] = pygame.image.load(bg_path)
                    self.background_images[season] = pygame.transform.scale(
                        self.background_images[season], (self.width, self.height)
                    )
        except Exception as e:
            print(f"画像読み込みエラー: {e}")

    def load_japanese_font(self, size: int):
        """日本語フォントを読み込み (x12y16pxMaruMonica.ttfを優先)"""
        font_paths_to_try = [
            # 優先度1: x12y16pxMaruMonica (ファミコン風)
            os.path.join('assets', 'fonts', 'x12y16pxMaruMonica.ttf'),

            # 優先度2: システムフォント（Windows, macOS, Linux）
            # Windows
            "C:/Windows/Fonts/msgothic.ttc",  # MS Gothic
            "C:/Windows/Fonts/msmincho.ttc",  # MS Mincho
            "C:/Windows/Fonts/meiryo.ttc",    # Meiryo
            "C:/Windows/Fonts/NotoSansCJK-Regular.ttc",
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            # Linux
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for font_path in font_paths_to_try:
            try:
                if os.path.exists(font_path):
                    print(f"フォントを読み込み中: {font_path}")
                    return pygame.font.Font(font_path, size)
            except Exception as e:
                print(f"フォント '{font_path}' の読み込みに失敗しました: {e}")
                continue

        # フォールバック: システムフォントから日本語対応フォントを探す
        try:
            print("システムフォントから日本語フォントを検索します...")
            available_fonts = pygame.font.get_fonts()
            japanese_fonts = [
                'msgothic', 'msmincho', 'meiryo', 'notosanscjk',
                'hiraginokakugothicpro', 'hiraginominchopro',
                'takao', 'ipa', 'vlgothic', 'arial unicode ms'
            ]

            for jp_font in japanese_fonts:
                if jp_font in available_fonts:
                    print(f"システムフォント '{jp_font}' を使用します。")
                    return pygame.SysFont(jp_font, size)

            print("日本語対応システムフォントが見つかりません。デフォルトフォントを使用します。")
            return pygame.font.Font(None, size)
        except Exception as e:
            print(f"システムフォントの検索中にエラーが発生しました: {e}")
            print("デフォルトフォントを使用します。")
            return pygame.font.Font(None, size)

    def get_season(self, month: int) -> str:
        """月から季節を取得"""
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'autumn'
        else:
            return 'winter'

    def update_price(self):
        """価格を更新（タイミング調整版）"""
        current_time = time.time()

        # ニュース表示中の場合
        if self.showing_news:
            if current_time - self.news_start_time >= self.news_duration:
                # ニュース終了、キャラクター会話に移行
                self.showing_news = False
                self.current_news = None
                self.set_new_message()
                self.character_start_time = current_time  # キャラクター会話の開始時間を記録
            return

        # キャラクター会話中で、ニュースの後の場合
        if hasattr(self, 'character_start_time') and self.character_start_time > 0:
            if current_time - self.character_start_time >= self.character_message_duration:
                # キャラクター会話終了、月を切り替える
                self.advance_month(current_time)
                self.character_start_time = 0  # リセット
            return

        # 通常の月更新タイミング（ニュースがなかった場合）
        if current_time - self.last_update >= self.character_message_duration:
            self.advance_month(current_time)

    def advance_month(self, current_time):
        """月を進める処理"""
        # 月を進める
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1

        # 価格を変動させる（季節要因も考慮）
        season_factor = self.get_season_price_factor()
        base_change = random.randint(-100, 100)
        seasonal_change = season_factor * random.randint(-50, 50)

        self.rice_price += int(base_change + seasonal_change)
        self.rice_price = max(200, min(800, self.rice_price))  # 価格範囲制限

        # 月変更音
        self.play_sound_effect("month_change")

        # ニュースを表示するかチェック
        if self.should_show_news():
            self.current_news = self.select_random_news()
            if self.current_news:
                self.showing_news = True
                self.news_start_time = current_time
                self.display_message = ""
                self.message_index = 0

                # ニュースアラート音
                self.play_sound_effect("news_alert")
                print(f"ニュースを表示中: {self.current_news.name}")
            else:
                # ニュースがない場合は通常のキャラクター会話
                self.set_new_message()
                self.last_update = current_time
        else:
            # ニュースを表示しない場合は通常のキャラクター会話
            self.set_new_message()
            self.last_update = current_time

    def get_season_price_factor(self) -> float:
        """季節による価格変動係数"""
        season = self.get_season(self.current_month)
        factors = {
            'spring': 0.8,  # 春：やや安定
            'summer': 1.2,  # 夏：やや高め
            'autumn': 0.6,  # 秋：収穫期で安め
            'winter': 1.0   # 冬：通常
        }
        return factors.get(season, 1.0)

    def set_new_message(self):
        """新しいメッセージを設定"""
        speaker = self.characters[self.current_speaker]
        self.current_message = speaker.get_message(self.rice_price)
        self.display_message = ""
        self.message_index = 0

        # 次の話者に変更
        self.current_speaker = (self.current_speaker + 1) % len(self.characters)

    def update_text_display(self):
        """テキストを一文字ずつ表示"""
        current_time = pygame.time.get_ticks()

        if self.showing_news and self.current_news:
            # ニューステキストの表示
            full_news_text = f"【{self.current_news.name}】{self.current_news.content}"
            if (self.message_index < len(full_news_text) and
                current_time - self.last_char_time > self.char_delay):

                self.display_message += full_news_text[self.message_index]
                self.message_index += 1
                self.last_char_time = current_time

                # テキスト音効果
                self.play_sound_effect("text_click")
        else:
            # 通常のキャラクター会話
            if (self.message_index < len(self.current_message) and
                current_time - self.last_char_time > self.char_delay):

                self.display_message += self.current_message[self.message_index]
                self.message_index += 1
                self.last_char_time = current_time

                # テキスト音効果
                self.play_sound_effect("text_click")

    def draw_text_window(self):
        """ファミコン風テキストウィンドウを描画"""
        # ウィンドウの位置とサイズ
        window_rect = pygame.Rect(50, 400, self.width - 100, 150)
        border_rect = pygame.Rect(45, 395, self.width - 90, 160)

        # ニュース表示時は背景色を変更
        bg_color = self.colors['news_bg'] if self.showing_news else self.colors['text_bg']

        # ボーダーとウィンドウ背景
        pygame.draw.rect(self.screen, self.colors['white'], border_rect)
        pygame.draw.rect(self.screen, bg_color, window_rect)

        # 内側のボーダー
        inner_border = pygame.Rect(45, 395, self.width - 90, 160)
        pygame.draw.rect(self.screen, self.colors['white'], inner_border, 2)

        if self.showing_news and self.current_news:
            # ニュース表示
            news_label = self.font_medium.render("【 ニュース速報 】", True, self.colors['yellow'])
            self.screen.blit(news_label, (70, 405))
        else:
            # 話者名表示
            speaker = self.characters[(self.current_speaker - 1) % len(self.characters)]
            speaker_text = self.font_medium.render(f"{speaker.name}（{speaker.role}）",
                                                 True, self.colors['yellow'])
            self.screen.blit(speaker_text, (70, 405))

        # メッセージテキスト表示（複数行対応）445は表示の高さの位置 2行目の高さは45
        lines = self.wrap_text(self.display_message, self.width - 140)
        y_offset = 445
        for line in lines:
            if y_offset < 540:  # ウィンドウ内に収まる範囲
                text_surface = self.font_small.render(line, True, self.colors['white'])
                self.screen.blit(text_surface, (70, y_offset))
                y_offset += 45

    def wrap_text(self, text: str, max_width: int) -> List[str]:
        """テキストを指定幅で折り返し"""
        words = text
        lines = []
        current_line = ""

        for char in words:
            test_line = current_line + char
            text_width = self.font_small.size(test_line)[0]

            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char

        if current_line:
            lines.append(current_line)

        return lines

    def draw_ui(self):
        """UI要素を描画"""
        # タイトル
        title = self.font_large.render("Rice Weather Japan", True, self.colors['white'])
        title_rect = title.get_rect(center=(self.width // 2, 30))
        self.screen.blit(title, title_rect)

        # 月表示
        month_text = self.font_medium.render(f"{self.current_month}月", True, self.colors['white'])
        self.screen.blit(month_text, (50, 70))

        # 価格表示
        price_text = self.font_medium.render(f"米価格: ¥{self.rice_price}/kg",
                                           True, self.colors['green'])
        self.screen.blit(price_text, (140, 70))

        # ニュース表示中の表示
        if self.showing_news:
            news_indicator = self.font_small.render("【新しいトピックです】", True, self.colors['red'])
            self.screen.blit(news_indicator, (70, 350))

        # 価格グラフ（簡易版）
        self.draw_price_indicator()

        # キャラクター表示
        self.draw_characters()

    def draw_price_indicator(self):
        """価格インジケーターを描画"""
        indicator_rect = pygame.Rect(400, 87, 250, 20)
        pygame.draw.rect(self.screen, self.colors['gray'], indicator_rect)

        # 価格に応じた色分け
        price_ratio = (self.rice_price - 200) / 600  # 200-800の範囲を0-1に正規化
        if price_ratio < 0.33:
            color = self.colors['blue']  # 安い
        elif price_ratio < 0.66:
            color = self.colors['green']  # 適正
        else:
            color = self.colors['red']  # 高い

        fill_width = int(240 * price_ratio)
        fill_rect = pygame.Rect(405, 92, fill_width, 10)
        pygame.draw.rect(self.screen, color, fill_rect)

    def draw_characters(self):
        """キャラクターを描画"""
        char_positions = [(150, 190), (350, 190), (550, 190)]

        for i, char in enumerate(self.characters):
            x, y = char_positions[i]

            # キャラクター画像（または代替矩形）
            if char.image:
                self.screen.blit(char.image, (x, y))
            else:
                # 画像がない場合の代替表示
                char_rect = pygame.Rect(x, y, 120, 120)
                colors = [self.colors['red'], self.colors['green'], self.colors['blue']]
                pygame.draw.rect(self.screen, colors[i], char_rect)

                # キャラクター名
                name_text = self.font_small.render(char.role, True, self.colors['white'])
                name_rect = name_text.get_rect(center=(x + 60, y + 60))
                self.screen.blit(name_text, name_rect)

            # 現在の話者をハイライト（ニュース表示中は無効）8はボーダーの太さ
            if not self.showing_news and i == (self.current_speaker - 1) % len(self.characters):
                highlight_rect = pygame.Rect(x - 10, y - 10, 140, 140)
                pygame.draw.rect(self.screen, self.colors['yellow'], highlight_rect, 16)

    def draw_background(self):
        """背景を描画"""
        season = self.get_season(self.current_month)

        if season in self.background_images:
            self.screen.blit(self.background_images[season], (0, 0))
        else:
            # 背景画像がない場合のグラデーション背景
            season_colors = {
                'spring': (100, 200, 100),
                'summer': (100, 150, 250),
                'autumn': (200, 150, 100),
                'winter': (150, 150, 200)
            }
            bg_color = season_colors.get(season, (50, 50, 100))
            self.screen.fill(bg_color)

    def run(self):
        """メインゲームループ"""
        # 初期メッセージ設定
        self.set_new_message()

        # Play background music
        self.play_background_music()

        while self.running:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # スペースキーで次のメッセージ
                        if self.showing_news:
                            if self.message_index >= len(f"【{self.current_news.name}】{self.current_news.content}"):
                                # ニュース表示を強制終了してキャラクター会話へ
                                self.showing_news = False
                                self.current_news = None
                                self.set_new_message()
                            else:
                                # ニュースメッセージを即座に全表示
                                full_text = f"【{self.current_news.name}】{self.current_news.content}"
                                self.display_message = full_text
                                self.message_index = len(full_text)
                        else:
                            if self.message_index >= len(self.current_message):
                                self.set_new_message()
                            else:
                                # メッセージを即座に全表示
                                self.display_message = self.current_message
                                self.message_index = len(self.current_message)

            # ゲーム状態更新
            self.update_price()
            self.update_text_display()

            # 描画
            self.draw_background()
            self.draw_ui()
            self.draw_text_window()

            pygame.display.flip()
            self.clock.tick(60)

        # Stop background music before quitting
        self.stop_background_music()
        pygame.quit()
