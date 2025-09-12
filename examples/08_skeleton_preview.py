"""
8. スケルトンプロジェクトプレビュー

このサンプルは、最終ステップのスケルトンプロジェクトで使用される
コア機能の簡単なプレビューです。

実際のスケルトンプロジェクトでは、このコードをベースに
ChainlitのWebUIとLangServeのAPIが追加されます。

GitHub: https://github.com/nyasukun/ai-agent-skelton
"""

import os
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import asyncio
from datetime import datetime

# 環境変数の確認
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  OPENAI_API_KEYが設定されていません")
    print("   実際のスケルトンプロジェクトでは .env ファイルで管理します")
    exit(1)

class AgentState(TypedDict):
    """エージェントの状態定義（スケルトンプロジェクトと同じ構造）"""
    messages: List[str]
    session_id: str
    context: str
    timestamp: str

class SkeletonPreviewAgent:
    """
    スケルトンプロジェクトのコア機能をプレビューするエージェント
    
    実際のスケルトンでは、これにWebUIとAPIが追加されます：
    - Chainlit: 美しいチャットインターフェース
    - LangServe: RESTful APIとPlayground
    - Docker: 簡単デプロイメント
    """
    
    def __init__(self):
        print("🤖 スケルトンプロジェクトプレビューエージェントを初期化中...")
        
        # LLMの初期化（スケルトンと同じ設定）
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            streaming=True  # スケルトンではストリーミングレスポンス対応
        )
        
        # グラフワークフローの構築
        self._build_workflow()
        print("✅ エージェント初期化完了")
    
    def _build_workflow(self):
        """
        LangGraphワークフローの構築
        スケルトンプロジェクトと同じ構造
        """
        workflow = StateGraph(AgentState)
        
        # ノードの追加
        workflow.add_node("preprocess", self._preprocess_input)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("postprocess", self._postprocess_output)
        
        # エッジの定義
        workflow.add_edge("preprocess", "generate_response")
        workflow.add_edge("generate_response", "postprocess")
        workflow.add_edge("postprocess", END)
        
        # エントリーポイント
        workflow.set_entry_point("preprocess")
        
        # コンパイル
        self.app = workflow.compile()
    
    def _preprocess_input(self, state: AgentState) -> AgentState:
        """
        入力の前処理
        スケルトンプロジェクトでは、より高度な前処理を実装
        """
        print(f"🔄 前処理中... (セッション: {state['session_id']})")
        
        # タイムスタンプの追加
        state["timestamp"] = datetime.now().isoformat()
        
        # コンテキストの設定
        state["context"] = "LangGraphハンズオンで学んだ技術を活用したAIエージェント"
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """
        LLMを使用した応答生成
        スケルトンプロジェクトと同じパターン
        """
        print("🧠 AI応答生成中...")
        
        # システムメッセージの設定
        system_message = SystemMessage(content=f"""
あなたは{state['context']}です。

特徴:
- LangGraphベースの構造化されたワークフロー
- セッション管理による会話履歴の保持
- ユーザーフレンドリーな対話

現在のセッション: {state['session_id']}
処理時刻: {state['timestamp']}
""")
        
        # メッセージの構築
        messages = [system_message]
        for msg in state["messages"]:
            messages.append(HumanMessage(content=msg))
        
        # LLMによる応答生成
        try:
            response = self.llm.invoke(messages)
            
            # 応答をメッセージリストに追加
            state["messages"].append(response.content)
            
            print(f"✅ 応答生成完了: {len(response.content)}文字")
            
        except Exception as e:
            error_msg = f"応答生成エラー: {str(e)}"
            print(f"❌ {error_msg}")
            state["messages"].append(error_msg)
        
        return state
    
    def _postprocess_output(self, state: AgentState) -> AgentState:
        """
        出力の後処理
        スケルトンプロジェクトでは、ログ記録や分析機能を追加
        """
        print("📝 後処理中...")
        
        # メッセージ数の記録（簡単な統計）
        message_count = len(state["messages"])
        print(f"📊 セッション統計: {message_count}メッセージ")
        
        return state
    
    async def chat(self, message: str, session_id: str = "default") -> str:
        """
        チャット機能
        スケルトンプロジェクトではWebUIとAPIの両方から呼び出される
        """
        print(f"\n💬 新しいメッセージ: {message[:50]}...")
        
        # 初期状態の設定
        initial_state = {
            "messages": [message],
            "session_id": session_id,
            "context": "",
            "timestamp": ""
        }
        
        # ワークフローの実行
        result = await self.app.ainvoke(initial_state)
        
        # 最後のメッセージ（AI応答）を返す
        return result["messages"][-1]

def print_skeleton_info():
    """スケルトンプロジェクトの情報表示"""
    print("=" * 60)
    print("🚀 LangGraph AIエージェント スケルトンプロジェクト")
    print("=" * 60)
    print()
    print("📦 完全版の特徴:")
    print("  ✅ ChainlitによるWebUI")
    print("  ✅ LangServeによるAPI")
    print("  ✅ セッション管理")
    print("  ✅ Docker対応")
    print("  ✅ 本番環境対応")
    print()
    print("🔗 GitHub: https://github.com/nyasukun/ai-agent-skelton")
    print()
    print("📋 実行手順:")
    print("  1. git clone https://github.com/nyasukun/ai-agent-skelton.git")
    print("  2. cd ai-agent-skelton")
    print("  3. pip install -r requirements.txt")
    print("  4. cp .env.example .env  # APIキーを設定")
    print("  5. chainlit run app.py -w")
    print("  6. http://localhost:8000 でWebUI起動！")
    print()
    print("=" * 60)

async def main():
    """メイン実行関数"""
    print_skeleton_info()
    
    # エージェントの初期化
    agent = SkeletonPreviewAgent()
    
    print("\n🎯 このプレビューでは、スケルトンプロジェクトのコア機能を体験できます")
    print("   実際のスケルトンでは、美しいWebUIとAPIが追加されます！")
    print()
    
    # インタラクティブチャット
    session_id = f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    while True:
        try:
            # ユーザー入力
            user_input = input("\n💬 メッセージを入力 (qで終了): ").strip()
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("\n👋 チャット終了")
                break
            
            if not user_input:
                continue
            
            # エージェントによる応答
            response = await agent.chat(user_input, session_id)
            
            print(f"\n🤖 エージェント: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 チャット終了")
            break
        except Exception as e:
            print(f"\n❌ エラー: {e}")
    
    print("\n🎉 スケルトンプロジェクトで、さらに高度な機能を体験してください！")
    print("🔗 https://github.com/nyasukun/ai-agent-skelton")

if __name__ == "__main__":
    # 非同期実行
    asyncio.run(main())
