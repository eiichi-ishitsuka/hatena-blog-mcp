# Hatena Blog MCP Server

はてなブログのAtomPub APIを使用してブログ記事を参照するMCPサーバーです。

## 機能

- ブログエントリの一覧取得
- 特定のエントリの詳細取得
- エントリの検索（タイトル・本文）
- カテゴリ一覧の取得

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -e .
```

### 2. 環境変数の設定

`.env.example`を`.env`にコピーして、あなたの設定情報を入力してください：

```bash
cp .env.example .env
```

必要な情報：
- `HATENA_ID`: はてなID
- `HATENA_API_KEY`: APIキー（アカウント設定から取得）
- `HATENA_BLOG_ID`: ブログID（通常はブログドメインの最初の部分）

### 3. APIキーの取得方法

1. はてなブログにログイン
2. 設定 → アカウント設定にアクセス
3. "APIキー"の項目からAPIキーを取得

## 使用方法

### ローカルでMCPサーバーとして起動

```bash
hatena-blog-mcp
```


## tests

```bash
pytest --cov -v tests/
```
