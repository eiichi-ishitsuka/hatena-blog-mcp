# 使用方法

## MCPツールの概要

Hatena Blog MCPサーバーは以下の4つのツールを提供します：

### 1. get_blog_entries

ブログエントリの一覧を取得します。

パラメータ:

- `page` (オプション): ページ番号（デフォルト: 1）
- `limit` (オプション): 取得する記事数の上限（デフォルト: 10、最大: 100）

使用例:
```json
{
  "name": "get_blog_entries",
  "arguments": {
    "page": 1,
    "limit": 5
  }
}
```

戻り値:
```
Found 5 blog entries (page 1):

記事タイトル1 ✅ Published
ID: 123456789
Author: author-name
Published: 2024-01-15 10:30
Categories: カテゴリ1, カテゴリ2

記事の内容の最初の200文字...

---

記事タイトル2 📝 Draft
...
```

### 2. get_blog_entry

指定されたIDの特定の記事を取得します。

パラメータ:

- `entry_id` (必須): 取得したい記事のID

使用例:
```json
{
  "name": "get_blog_entry",
  "arguments": {
    "entry_id": "123456789"
  }
}
```

戻り値:
```
# 記事タイトル ✅ Published

ID: 123456789
Author: author-name
Published: 2024-01-15 10:30:45
Updated: 2024-01-15 11:00:30
Categories: カテゴリ1, カテゴリ2

## Content

記事の完全な内容がここに表示されます...
```

### 3. search_blog_entries

タイトルまたは本文で記事を検索します。

パラメータ:

- `query` (必須): 検索クエリ
- `max_results` (オプション): 最大結果数（デフォルト: 10、最大: 50）

使用例:
```json
{
  "name": "search_blog_entries",
  "arguments": {
    "query": "Python",
    "max_results": 3
  }
}
```

戻り値:
```
Found 3 blog entries matching 'Python':

Pythonプログラミング入門 ✅ Published
ID: 123456789
Author: author-name
Published: 2024-01-15 10:30
Categories: プログラミング, Python

Pythonの基本的な使い方について説明します...

---
```

### 4. get_blog_categories

ブログで使用されているカテゴリの一覧を取得します。

パラメータ:
なし

使用例:
```json
{
  "name": "get_blog_categories",
  "arguments": {}
}
```

戻り値:
```
Available categories (5):

- プログラミング
- Python
- 日記
- 技術
- 雑記
```

## MCPリソース

MCPサーバーは以下のリソースも提供します：

### hatena://blog/entries

すべてのブログエントリのサマリーを取得できます。

### hatena://blog/categories

利用可能なカテゴリの一覧を取得できます。

## エラーハンドリング

### 一般的なエラー

1. 認証エラー
```
Error: Authentication failed. Please check your HATENA_ID and HATENA_API_KEY.
```

2. 記事が見つからない
```
Blog entry '999999' not found.
```

3. 検索結果なし
```
No blog entries found matching 'nonexistent-term'.
```

### 設定関連のエラー

```
Error: Missing required environment variables: HATENA_ID, HATENA_API_KEY, HATENA_BLOG_ID
```

この場合は[セットアップガイド](setup.md#configuration)を参照して環境変数を正しく設定してください。

## ベストプラクティス

### 効率的な使用方法

1. 記事検索: 大量の記事がある場合は`search_blog_entries`を使用して特定の記事を見つける
2. ページネーション: `get_blog_entries`でページごとに記事を取得する
3. 詳細表示: 興味のある記事のIDがわかったら`get_blog_entry`で詳細を取得する

### パフォーマンス考慮事項

- 検索機能は最大100記事までスキャンします
- 大量の記事がある場合、検索には時間がかかる可能性があります
- APIレート制限に注意してください