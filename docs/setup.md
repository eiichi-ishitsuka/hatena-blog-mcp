# セットアップ

## インストール {#installation}

### 前提条件

- Python 3.10以上
- はてなブログのアカウント
- はてなブログAPIキー

### 依存関係のインストール

```bash
pip install -e .
```

## 設定 {#configuration}

### 環境変数の設定

`.env.example`を`.env`にコピーして、設定情報を入力してください：

```bash
cp .env.example .env
```

### 必要な環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `HATENA_ID` | はてなID | `your-hatena-id` |
| `HATENA_API_KEY` | はてなAPIキー | `your-api-key` |
| `HATENA_BLOG_ID` | ブログID（ドメイン名の最初の部分） | `your-blog` |

### APIキーの取得方法

1. はてなブログにログイン
2. 「設定」→「アカウント設定」にアクセス
3. 「APIキー」の項目からAPIキーを取得

### ブログIDの確認方法

ブログのURLが `https://your-blog.hatenablog.com/` の場合、ブログIDは `your-blog` です。

## MCPサーバーの起動

### スタンドアロン起動

```bash
hatena-blog-mcp
```

### MCPクライアントとの統合

MCPサーバーは標準入出力（stdio）を使用してMCPクライアントと通信します。クライアント側の設定については、使用するMCPクライアントのドキュメントを参照してください。

## 動作確認

### テストの実行

```bash
pytest --cov -v tests/
```

### 手動確認

環境変数が正しく設定されているかを確認：

```bash
python -c "
import os
from src.hatena_blog_mcp.client import HatenaBlogClient

hatena_id = os.getenv('HATENA_ID')
api_key = os.getenv('HATENA_API_KEY')
blog_id = os.getenv('HATENA_BLOG_ID')

print(f'HATENA_ID: {hatena_id}')
print(f'API_KEY: {'*' * len(api_key) if api_key else 'Not set'}')
print(f'BLOG_ID: {blog_id}')

client = HatenaBlogClient(hatena_id, api_key, blog_id)
entries = client.get_entries(1)
print(f'取得された記事数: {len(entries)}')
"
```