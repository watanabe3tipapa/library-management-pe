# ISBNスキャナー - ブラウザ版

ISBNバーコードをカメラでスキャンして、書籍情報を自動取得・管理できるWebアプリケーションです。

## クイックスタート

### 1. アクセス

GitHub Pagesで公開中:

```
https://[ユーザー名].github.io/library-management-pe/
```

### 2. 使い方

1. 「カメラ開始」ボタンをクリック
2. カメラを選択（複数台ある場合）
3. ISBNバーコードをカメラに向ける
4. 自動的に書籍情報が取得されてリストに追加される

### 3. 保存・エクスポート

- 保存: CSVファイルとしてダウンロード
- CSVダウンロード: 別の名前で保存
- クリア: リストを空にする

## 機能

- カメラスキャン: スマホのカメラやWebカメラでISBNを読み取り
- 書籍情報自動取得: Google Books APIでタイトル・著者・表紙を自動取得
- CSVエクスポート: スキャン結果をCSVで保存
- モバイル対応: スマホ・タブレット・デスクトップ全て対応
- インストール不要: ブラウザだけで動く（Python不要）

## 動作環境

- Chrome, Safari, Firefox, Edge 最新版
- カメラ付きデバイス
- HTTPS接続（カメラアクセスには必須）

> 注意: iOS SafariではHTTPSが必須です。GitHub Pagesは自動HTTPS対応なのでご安心ください。

## 開発

### ローカルで実行

```bash
# docsフォルダで簡易サーバー起動
cd docs
python3 -m http.server 8000
# → http://localhost:8000 でアクセス
```

### ファイル構成

```
docs/
├── index.html    # メイン画面
├── style.css    # スタイリング
├── script.js    # ロジック
└── USAGE.md     # このドキュメント
```

## 技術スタック

- html5-qrcode: バーコード読み取り（ZXingベース）
- Google Books API: 書籍情報取得
- Vanilla JS: ロジック（依存関係なし）

## ライセンス

MIT License
