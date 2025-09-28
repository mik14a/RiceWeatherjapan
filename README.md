# Rice Weather japan
ファミコン風　キャラクター会話ゲームです
お米の価格によって　主婦と農家と政治家がそれぞれの立場でしゃべります
プレイヤーは基本的に介入は出来ません。
テレビを見ている感覚です

## 対象
windows11

## ダウンロード
GitHubからダウンロードできます。以下のページの緑の「Code」ボタンを押してzipをダウンロードします。
https://github.com/ootoda/RiceWeatherjapan

## インストール
Pythonで作っています。初回起動時に　Pygameのインストールが必要となることがあります。
以下のコマンドを、コマンドプロンプトから入力して必要なものをダウンロードしてください。

```shell
pip install -r requirements.txt
```

## 使い方
`Rice Weather japan_v1.7.py` をクリックすると起動します。

## 開発とビルド

実行可能な `.exe` ファイルを作成（ビルド）する手順です。

### 1. 開発環境の準備

このプロジェクトは **Python 3.11** でのビルドを推奨します。

```shell
# Python 3.11 を指定して仮想環境を作成 (初回のみ)
uv venv -p 3.11

# 仮想環境を有効化
.venv\Scripts\activate

# 必要なライブラリをインストール
uv pip install -r requirements.txt
```

### 2. ビルドの実行

`build.bat` を実行すると、`dist` フォルダ内に `RiceWeatherJapan.exe` が生成されます。

## ライセンス
MIT License
