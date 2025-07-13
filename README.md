# Hatena Blog MCP Server

はてなブログのAtomPub APIを使用してブログ記事を参照するMCP (Model Context Protocol) サーバーです。

## 概要

このMCPサーバーを使用すると、AIアシスタント（Claude等）がはてなブログの記事データにアクセスできるようになります。

### 主な機能

- ブログエントリの一覧取得・検索
- 特定のエントリの詳細取得
- カテゴリ一覧の取得

## クイックスタート

### 1. インストール

```bash
pip install -e .
```

### 2. 環境設定

`.env.example`を`.env`にコピーして設定：

```bash
cp .env.example .env
```

必要な環境変数：
- `HATENA_ID`: はてなID
- `HATENA_API_KEY`: APIキー（[アカウント設定](https://blog.hatena.ne.jp/my/config)から取得）
- `HATENA_BLOG_ID`: ブログID

### 3. 起動

```bash
hatena-blog-mcp
```

## ドキュメント

詳細な使用方法や開発ガイドについては、以下のドキュメントを参照してください：

- 📖 **[完全なドキュメント](docs/)** - MkDocsで生成された詳細ドキュメント
- 🚀 **[セットアップガイド](docs/setup.md)** - 詳細なインストールと設定手順
- 📋 **[使用方法](docs/usage.md)** - MCPツールの詳細な使い方
- 🔧 **[API リファレンス](docs/api-reference.md)** - 関数・クラスの詳細仕様
- 👨‍💻 **[開発ガイド](docs/development.md)** - 貢献者向けの開発情報

### ドキュメントをローカルで確認

```bash
pip install -e ".[dev]"
mkdocs serve
```

## ライセンス

MIT License
