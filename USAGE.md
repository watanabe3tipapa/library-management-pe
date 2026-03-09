# Library Management Tools - Python版

ISBNバーコードをカメラでスキャンし、Booklogに自動登録するためのローカルツールです。

## 新版について

**まずはブラウザ版をお試しください。**

```
https://[ユーザー名].github.io/library-management-pe/
```

ブラウザだけで動くので、インストール不要・Python不要・すぐ使用可能です！

---

## Python版の使い方

Python版はより高度な自動化が必要な方向けです。

## 準備

```bash
# リポジトリをクローン
git clone https://github.com/watanabe3tipapa/library-management-pe.git
cd library-management-pe

# 依存関係をインストール
uv sync

# Playwrightブラウザをインストール（Booklog自動追加を使用する場合）
uv run playwright install chromium
```

## 機能

### 1. ISBNスキャナー

カメラでISBNバーコードをスキャンし、ブラウザで表示します。

```bash
uv run python camera_isbn.py
# または出力ファイルを指定
uv run python camera_isbn.py -o my_books.csv
```

ブラウザで http://localhost:5005 を開く。

**操作:**
- スキャンしたISBNが右側のリストに追加される
- 「保存」ボタンでCSVファイルに保存
- 「ダウンロード」でCSVをダウンロード
- ウィンドウを閉じると自動保存キーで終了

### 2.
- Booklogに自動追加

CSVのISBNを自動的にBooklog.jpに追加します。

```bash
uv run python booklog_auto_add.py
```

**操作:**
1. ブラウザが起動してBooklogログイン画面が表示される
2. ログイン後、Enterを押すとセッションが保存される
3. CSVファイルのISBNが順に追加されていく

## ファイル構成

```
library-management-pe/
├── camera_isbn.py       # ISBNスキャナー（Flask + OpenCV）
├── booklog_auto_add.py  # Booklog自動追加ツール（Playwright）
├── scanned_isbn.csv     # スキャン結果の出力先（自動生成）
├── docs/                # ブラウザ版（GitHub Pages用）
└── README.md
```

## オプション

### camera_isbn.py

| オプション | 説明 | デフォルト |
|-----------|------|----------|
| -o, --output | 出力CSVファイル名 | scanned_isbn.csv |

### booklog_auto_add.py

| オプション | 説明 | デフォルト |
|-----------|------|----------|
| -i, --input | 入力CSVファイル名 | scanned_isbn.csv |

## トラブルシューティング

### カメラが開けない

```bash
# カメラが認識されているか確認
uv run python -c "import cv2; print(cv2.__version__)"
```

### Playwrightのエラー

```bash
# ブラウザを再インストール
uv run playwright install chromium
```

### ポート5005が使用中

```bash
# 別のポートで起動するには camera_isbn.py を編集
# app.run(threaded=True, port=5005) の port を変更
```

## 動作環境

- Python 3.13+
- macOS (Intel/Apple Silicon) / Linux / Windows
- カメラ付きデバイス
- OpenCV
- Flask
- Playwright（Booklog機能のみ）

> **Intel Macをお使いの場合**: HomebrewでOpenCVをインストールする場合、パスは /usr/local/bin（Apple Siliconは /opt/homebrew/bin）。

## ライセンス

MIT License
