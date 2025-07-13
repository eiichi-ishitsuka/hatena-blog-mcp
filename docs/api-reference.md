# API リファレンス

## HatenaBlogClient クラス

### 概要

`HatenaBlogClient`は、はてなブログのAtomPub APIとやり取りするためのメインクラスです。

ファイル: `src/hatena_blog_mcp/client.py:24`

### 初期化

```python
HatenaBlogClient(hatena_id: str, api_key: str, blog_id: str)
```

パラメータ:

- `hatena_id`: はてなID
- `api_key`: はてなAPIキー
- `blog_id`: ブログID（ドメイン名の最初の部分）

### メソッド

#### get_entries(page: int = 1) -> List[BlogEntry]

機能: ブログエントリの一覧を取得します。

パラメータ:

- `page`: ページ番号（1から開始）

戻り値: `BlogEntry`オブジェクトのリスト

実装: `src/hatena_blog_mcp/client.py:77`

#### get_entry(entry_id: str) -> Optional[BlogEntry]

機能: 指定されたIDの特定のブログエントリを取得します。

パラメータ:

- `entry_id`: エントリID

戻り値: `BlogEntry`オブジェクト、または見つからない場合は`None`

実装: `src/hatena_blog_mcp/client.py:94`

#### search_entries(query: str, max_results: int = 10) -> List[BlogEntry]

機能: タイトルまたは本文でブログエントリを検索します。

パラメータ:

- `query`: 検索クエリ
- `max_results`: 最大結果数

戻り値: マッチした`BlogEntry`オブジェクトのリスト

実装: `src/hatena_blog_mcp/client.py:115`

#### get_categories() -> List[str]

機能: ブログで使用されているカテゴリの一覧を取得します。

戻り値: カテゴリ名の文字列リスト

実装: `src/hatena_blog_mcp/client.py:146`

#### create_entry(title: str, content: str, categories: List[str] = None, is_draft: bool = True) -> BlogEntry

機能: 新しいブログエントリを作成します。

パラメータ:

- `title`: 記事のタイトル
- `content`: 記事の内容（HTMLまたはプレーンテキスト）
- `categories`: カテゴリ名のリスト（デフォルト: None）
- `is_draft`: 下書きかどうか（デフォルト: True）

戻り値: 作成された`BlogEntry`オブジェクト

実装: `src/hatena_blog_mcp/client.py:167`

## BlogEntry クラス

### 概要

ブログエントリを表現するPydanticモデルです。

ファイル: `src/hatena_blog_mcp/client.py:10`

### フィールド

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `id` | `str` | エントリID |
| `title` | `str` | タイトル |
| `content` | `str` | 記事の本文 |
| `published` | `datetime` | 公開日時 |
| `updated` | `datetime` | 更新日時 |
| `author` | `str` | 作者名 |
| `categories` | `List[str]` | カテゴリリスト（デフォルト: 空リスト） |
| `is_draft` | `bool` | 下書きかどうか（デフォルト: False） |
| `edit_url` | `Optional[str]` | 編集URL（デフォルト: None） |

## MCPサーバー関数

### handle_list_tools() -> list[Tool]

機能: 利用可能なツールの一覧を返します。

戻り値: MCPツールオブジェクトのリスト

実装: `src/hatena_blog_mcp/server.py:37`

### handle_call_tool(name: str, arguments: dict) -> list[TextContent]

機能: 指定されたツールを実行します。

パラメータ:

- `name`: ツール名
- `arguments`: ツールの引数

戻り値: テキストコンテンツのリスト

実装: `src/hatena_blog_mcp/server.py:113`

### handle_list_resources() -> list[Resource]

機能: 利用可能なリソースの一覧を返します。

戻り値: MCPリソースオブジェクトのリスト

実装: `src/hatena_blog_mcp/server.py:216`

### handle_read_resource(uri: AnyUrl) -> str

機能: 指定されたリソースの内容を取得します。

パラメータ:
- `uri`: リソースURI

戻り値: リソースの内容

実装: `src/hatena_blog_mcp/server.py:235`

## フォーマット関数

### format_entry_summary(entry: BlogEntry) -> str

機能: ブログエントリのサマリー形式を生成します。

実装: `src/hatena_blog_mcp/server.py:184`

### format_entry_detail(entry: BlogEntry) -> str

機能: ブログエントリの詳細形式を生成します。

実装: `src/hatena_blog_mcp/server.py:198`

## 例外処理

### 一般的な例外

- `ValueError`: 環境変数が設定されていない場合
- `requests.exceptions.HTTPError`: HTTP通信エラー
- `ET.ParseError`: XML解析エラー

### エラーメッセージ

```python
# 環境変数エラー
"Missing required environment variables: HATENA_ID, HATENA_API_KEY, HATENA_BLOG_ID"

# 記事が見つからない
"Blog entry '{entry_id}' not found."

# 検索結果なし
"No blog entries found matching '{query}'."
```