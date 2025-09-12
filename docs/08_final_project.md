# 8. 最終ステップ: 実用的なAIエージェントスケルトン

## 🎯 このステップの目標

ハンズオンで学んだLangGraphの知識を活かして、実際のWebアプリケーションを動かしてみましょう！

## 🏗️ スケルトンプロジェクトの概要

[AI Agent Skeleton](https://github.com/nyasukun/ai-agent-skelton)は、今回学んだ技術を統合した実用的なプロジェクトです。

### 主な特徴

- **ChainlitによるWebUI**: 美しいチャットインターフェース
- **LangServeによるAPI**: RESTful APIとPlaygroundの提供
- **LangGraphベース**: 今回学んだグラフ構造を実践活用
- **OpenAI API統合**: GPT-3.5-turboを使用した自然言語処理
- **メモリ機能**: セッション管理による会話履歴の保持
- **Docker対応**: 簡単デプロイメント

### アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐
│   Chainlit UI   │    │  LangServe API  │
│  (Port: 8001)   │    │  (Port: 8000)   │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌─────────────────┐
         │  LangGraph      │
         │  Agent Core     │
         └─────────────────┘
                     │
         ┌─────────────────┐
         │   OpenAI API    │
         └─────────────────┘
```

## 🚀 実行手順

### 1. プロジェクトの取得

```bash
# スケルトンプロジェクトをクローン
git clone https://github.com/nyasukun/ai-agent-skelton.git
cd ai-agent-skelton
```

### 2. 環境セットアップ

```bash
# 依存関係をインストール
pip install -r requirements.txt

# 環境変数ファイルを作成
cp .env.example .env
```

### 3. APIキーの設定

`.env`ファイルを編集してOpenAI APIキーを設定：

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. アプリケーションの起動

#### 方法1: ChainlitのWebUI（推奨）

```bash
chainlit run app.py -w
```

ブラウザで `http://localhost:8000` にアクセス

#### 方法2: LangServe APIサーバー

```bash
python server.py
```

以下のエンドポイントが利用可能：
- **API Documentation**: `http://localhost:8000/docs`
- **LangServe Playground**: `http://localhost:8000/langserve/playground`
- **Chat API**: `POST http://localhost:8000/chat`

#### 方法3: 両方同時実行

```bash
# Terminal 1: LangServe API
python server.py

# Terminal 2: Chainlit UI
chainlit run app.py -w --port 8001
```

## 🔧 コードの理解

### agent.py - LangGraphエージェントの実装

スケルトンプロジェクトの`agent.py`は、今回学んだ概念を統合しています：

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class AgentState(TypedDict):
    messages: List[str]
    session_id: str
    # ハンズオンで学んだ状態管理

class ChatAgent:
    def __init__(self):
        # 今回学んだStateGraphの作成
        workflow = StateGraph(AgentState)
        
        # ノードの追加（ハンズオンで学んだパターン）
        workflow.add_node("process_input", self._process_input)
        workflow.add_node("generate_response", self._generate_response)
        
        # エッジの定義（条件分岐も可能）
        workflow.add_edge("process_input", "generate_response")
        workflow.add_edge("generate_response", END)
        
        # エントリーポイント
        workflow.set_entry_point("process_input")
        
        self.app = workflow.compile()
```

### app.py - ChainlitによるWebUI

```python
import chainlit as cl
from agent import ChatAgent

@cl.on_chat_start
async def on_chat_start():
    # セッション開始時の処理
    agent = ChatAgent()
    cl.user_session.set("agent", agent)

@cl.on_message
async def on_message(message: cl.Message):
    # ハンズオンで学んだエージェントを使用
    agent = cl.user_session.get("agent")
    response = await agent.invoke({
        "messages": [message.content],
        "session_id": cl.user_session.get("id")
    })
    await cl.Message(content=response["messages"][-1]).send()
```

## 🎨 カスタマイズのポイント

### 1. エージェントの拡張

ハンズオンで学んだツール統合を追加：

```python
def _tool_node(self, state: AgentState) -> AgentState:
    # 外部APIやデータベースへのアクセス
    # ハンズオン例07で学んだパターンを適用
    return state

# ワークフローに追加
workflow.add_node("use_tools", self._tool_node)
```

### 2. UIのカスタマイズ

```python
@cl.on_chat_start
async def on_chat_start():
    # カスタムウェルカムメッセージ
    await cl.Message(
        content="🤖 ハンズオンで学んだLangGraphエージェントです！何でも聞いてください。"
    ).send()
```

### 3. APIエンドポイントの追加

```python
from fastapi import FastAPI
from langserve import add_routes

app = FastAPI()

# ハンズオンで作成したエージェントをAPI化
add_routes(app, agent, path="/chat")

# カスタムエンドポイント
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## 🔄 ハンズオンとの対応関係

| ハンズオンステップ | スケルトンでの実装 |
|---|---|
| 04_hello_world.py | 基本的なグラフ構造 |
| 05_llm_node.py | OpenAI APIとの統合 |
| 06_stateful_agent.py | セッション管理とメモリ |
| 07_tool_integration.py | 外部ツールとの連携 |

## 🚀 次のステップ

1. **カスタマイズ**: 自分のユースケースに合わせて機能を拡張
2. **デプロイ**: Docker Composeを使用した本番環境デプロイ
3. **スケール**: 複数ユーザー対応やパフォーマンス最適化

## 💡 学習のまとめ

このスケルトンプロジェクトを通じて、以下を体験できます：

- ✅ LangGraphの実践的な活用方法
- ✅ WebUIとAPIの両方を提供するアーキテクチャ
- ✅ 実用的なAIエージェントの構築パターン
- ✅ 本番環境を意識した設計

**おめでとうございます！** 🎉

これで、LangGraphを使った実用的なAIエージェント開発の基礎をマスターしました。学んだ知識を活かして、ぜひ自分だけのAIエージェントを作ってみてください！

## 📚 参考リンク

- [AI Agent Skeleton Repository](https://github.com/nyasukun/ai-agent-skelton)
- [Chainlit Documentation](https://docs.chainlit.io/)
- [LangServe Documentation](https://python.langchain.com/docs/langserve)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
