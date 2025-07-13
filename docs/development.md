# 開発ガイド

## 開発環境のセットアップ

### 前提条件

- Python 3.10以上
- Git

### 開発用依存関係のインストール

```bash
pip install -e ".[dev]"
```

これにより以下のツールがインストールされます：

- pytest (テスト)
- pytest-asyncio (非同期テスト)
- pytest-cov (カバレッジ)
- black (コードフォーマット)
- mypy (型チェック)
- ruff (リンター)

## コード品質

### フォーマット

```bash
black src/ tests/
```

### リンティング

```bash
ruff check src/ tests/
```

### 型チェック

```bash
mypy src/
```

## テスト

### テストの実行

```bash
# 全テスト実行
pytest

# カバレッジ付きで実行
pytest --cov=hatena_blog_mcp --cov-report=html

# 詳細出力
pytest -v

# 特定のテストファイル
pytest tests/test_client.py
```

### テスト構造

```
tests/
├── __init__.py
├── test_client.py      # HatenaBlogClientのテスト
└── test_server.py      # MCPサーバーのテスト
```

### テストの書き方

新しい機能を追加する際は、対応するテストも作成してください：

```python
def test_new_feature():
    """新機能のテスト."""
    # Given
    setup_data = ...
    
    # When
    result = function_under_test(setup_data)
    
    # Then
    assert result == expected_value
```

## プロジェクト構造

```
hatena-blog-mcp/
├── src/
│   └── hatena_blog_mcp/
│       ├── __init__.py
│       ├── client.py       # はてなブログAPIクライアント
│       └── server.py       # MCPサーバー実装
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   └── test_server.py
├── docs/                   # MkDocsドキュメント
├── pyproject.toml         # プロジェクト設定
├── README.md
└── .env.example           # 環境変数テンプレート
```

## アーキテクチャ

### クライアント層 (client.py)

- `HatenaBlogClient`: はてなブログのAtomPub APIとの通信を担当
- `BlogEntry`: ブログエントリのデータモデル
- XML解析とPydanticモデルへの変換

### サーバー層 (server.py)

- MCPプロトコルの実装
- ツールとリソースの提供
- クライアント層との連携

### データフロー

```
MCP Client → MCP Server → HatenaBlogClient → Hatena AtomPub API
                ↓              ↓               ↓
            Tool/Resource → BlogEntry ← XML Response
```

## 新機能の追加

### 1. クライアント機能の追加

新しいAPIエンドポイントを追加する場合：

1. `HatenaBlogClient`にメソッドを追加
2. 必要に応じて新しいデータモデルを作成
3. テストを作成

### 2. MCPツールの追加

新しいMCPツールを追加する場合：

1. `handle_list_tools()`にツール定義を追加
2. `handle_call_tool()`にツール実行ロジックを追加
3. 必要に応じてフォーマット関数を作成
4. テストを作成

### 3. MCPリソースの追加

新しいMCPリソースを追加する場合：

1. `handle_list_resources()`にリソース定義を追加
2. `handle_read_resource()`にリソース取得ロジックを追加
3. テストを作成

## コントリビューション

### プルリクエストガイドライン

1. 新機能には適切なテストを含める
2. コード品質チェックが通ることを確認
3. ドキュメントの更新が必要な場合は含める
4. コミットメッセージは明確で説明的に

### 実行すべきチェック

プルリクエスト前に以下を実行：

```bash
# フォーマット
black src/ tests/

# リンティング
ruff check src/ tests/

# 型チェック
mypy src/

# テスト
pytest --cov=hatena_blog_mcp

# カバレッジが十分であることを確認
```

## トラブルシューティング

### よくある問題

1. **型エラー**
   - `mypy src/`で型チェックを実行
   - 型アノテーションを追加

2. **テスト失敗**
   - `pytest -v`で詳細なエラー情報を確認
   - モックが正しく設定されているか確認

3. **インポートエラー**
   - `pip install -e .`で開発モードインストール
   - `PYTHONPATH`の設定を確認

### デバッグ

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

または環境変数で：

```bash
export PYTHONPATH="src:$PYTHONPATH"
python -m hatena_blog_mcp.server
```