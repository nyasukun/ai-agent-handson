# LangGraphで始めるAIエージェント入門 ハンズオン

## 🎯 本日のゴール

- LangGraphの基礎を理解する
- 自分のAIエージェントを「動く形」にできる
- LangGraphの位置づけ（LangChainとの違い）を理解する

## 📚 ハンズオン内容

1. **オープニング** - 目標設定とLangGraphの位置づけ
2. **基本概念の理解** - グラフ構造、ノード、エッジ、StateGraph
3. **環境準備** - Python環境とライブラリのセットアップ
4. **Hello World グラフ** - 最小限のグラフ作成
5. **LLMを使ったノード** - ChatOpenAIとの連携
6. **状態を持つエージェント** - マルチターン会話の実装
7. **外部ツールとの連携** - ツール呼び出しの実装

## 🚀 環境準備

### 1. Python環境
- Python 3.8以上
- Google Colab または VSCode

### 2. 必要ライブラリのインストール

```bash
# pipenvのインストール（未インストールの場合）
pip install pipenv

# requirements.txtからライブラリをインストール
pipenv install -r requirements.txt

# 開発用パッケージもインストール（オプション）
pipenv install --dev
```

### 3. OpenAI APIキーの設定

`.env`ファイルを作成（推奨）：

```bash
# .envファイルを作成
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

pipenvは自動的に`.env`ファイルを読み込みます。

または、環境変数として設定：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 📁 ファイル構成

```
ai-agent-handson/
├── README.md                    # このファイル
├── requirements.txt             # 必要ライブラリ定義
├── Pipfile                      # pipenv設定（スクリプト定義）
├── Pipfile.lock                 # 依存関係のロック（自動生成）
├── .env                         # 環境変数（作成が必要）
├── docs/                        # 理論解説
│   ├── 01_opening.md           # オープニング
│   ├── 02_basic_concepts.md    # 基本概念
│   └── 03_environment.md       # 環境準備
└── examples/                    # 実践コード
    ├── 04_hello_world.py       # Hello Worldグラフ
    ├── 05_llm_node.py          # LLMノードの実装
    ├── 06_stateful_agent.py    # 状態管理エージェント
    └── 07_tool_integration.py  # ツール連携
```

## 🏃‍♂️ 実行方法

### 方法1: pipenv runを使用（推奨）

```bash
# 個別実行
pipenv run python examples/04_hello_world.py
pipenv run python examples/05_llm_node.py
pipenv run python examples/06_stateful_agent.py
pipenv run python examples/07_tool_integration.py

# 便利なスクリプトを使用
pipenv run hello      # Hello Worldグラフ
pipenv run llm        # LLMノード
pipenv run stateful   # 状態管理エージェント
pipenv run tools      # ツール連携

# 全ての例を順次実行
pipenv run run-all
```

### 方法2: 仮想環境内で実行

```bash
# 仮想環境に入る
pipenv shell

# 通常のpythonコマンドで実行
python examples/04_hello_world.py
python examples/05_llm_node.py
python examples/06_stateful_agent.py
python examples/07_tool_integration.py
```

## 🎓 学習の進め方

1. まず `docs/` フォルダの理論解説を読む
2. `examples/` フォルダのコードを順番に実行
3. コードを改変して動作を確認
4. 自分なりのエージェントを作成してみる

## 💡 Tips

- 各コード例には詳細なコメントが付いています
- エラーが出た場合は、APIキーの設定を確認してください
- 質問や疑問があれば、コードのコメントを参考にしてください

## 📖 参考資料

- [LangGraph公式ドキュメント](https://langchain-ai.github.io/langgraph/)
- [LangChain公式ドキュメント](https://python.langchain.com/)
- [OpenAI API ドキュメント](https://platform.openai.com/docs)

Happy Coding! 🚀
