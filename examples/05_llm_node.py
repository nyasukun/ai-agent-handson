"""
LangGraph LLMノード統合

このスクリプトでは、LangGraphにLLM（ChatOpenAI）を統合する方法を学びます：
- LLMをノードとして組み込む
- プロンプトテンプレートの活用
- 質問応答システムの構築
- エラーハンドリング

実行方法:
python examples/05_llm_node.py

注意: OpenAI APIキーが必要です
"""

import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ステップ1: 状態の定義
class LLMGraphState(TypedDict):
    """
    LLMグラフで使用する状態を定義
    
    Attributes:
        messages: 会話履歴
        user_input: ユーザーの入力
        ai_response: AIの応答
        context: 追加のコンテキスト情報
        step_count: 実行したステップ数
    """
    messages: List[str]
    user_input: str
    ai_response: str
    context: str
    step_count: int


# ステップ2: LLMの設定
def setup_llm():
    """
    OpenAI LLMを設定
    
    Returns:
        設定済みのChatOpenAIインスタンス
    """
    # APIキーの確認
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI APIキーが設定されていません。\n"
            "環境変数 OPENAI_API_KEY を設定するか、\n"
            "os.environ['OPENAI_API_KEY'] = 'your-key' を実行してください。"
        )
    
    # ChatOpenAIのインスタンスを作成
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",  # 使用するモデル
        temperature=0.7,        # 応答の創造性（0-2）
        max_tokens=500,         # 最大トークン数
    )
    
    print("✅ LLMが正常に設定されました")
    return llm


# ステップ3: LLMノードの定義
def input_processing_node(state: LLMGraphState) -> LLMGraphState:
    """
    ユーザー入力を処理するノード
    
    Args:
        state: 現在の状態
        
    Returns:
        更新された状態
    """
    print("📝 input_processing_nodeが実行されました")
    
    user_input = state.get("user_input", "")
    
    # 入力の前処理
    processed_input = user_input.strip()
    if not processed_input:
        processed_input = "こんにちは！"
    
    print(f"   処理された入力: {processed_input}")
    
    return {
        **state,
        "user_input": processed_input,
        "step_count": state.get("step_count", 0) + 1
    }


def llm_response_node(state: LLMGraphState) -> LLMGraphState:
    """
    LLMから応答を生成するノード
    
    Args:
        state: 現在の状態
        
    Returns:
        更新された状態
    """
    print("🤖 llm_response_nodeが実行されました")
    
    try:
        # LLMを設定
        llm = setup_llm()
        
        # システムメッセージを設定
        system_message = SystemMessage(content="""
あなたは親切で知識豊富なAIアシスタントです。
ユーザーの質問に対して、わかりやすく丁寧に回答してください。
回答は日本語で行い、簡潔でありながら有用な情報を提供してください。
""")
        
        # ユーザーメッセージを作成
        user_message = HumanMessage(content=state["user_input"])
        
        # LLMに送信するメッセージリスト
        messages = [system_message, user_message]
        
        print(f"   LLMに送信: {state['user_input']}")
        
        # LLMから応答を取得
        response = llm.invoke(messages)
        ai_response = response.content
        
        print(f"   LLMからの応答: {ai_response[:100]}...")
        
        # メッセージ履歴を更新
        updated_messages = state.get("messages", [])
        updated_messages.extend([
            f"ユーザー: {state['user_input']}",
            f"AI: {ai_response}"
        ])
        
        return {
            **state,
            "ai_response": ai_response,
            "messages": updated_messages,
            "step_count": state["step_count"] + 1
        }
        
    except Exception as e:
        print(f"❌ LLMノードでエラーが発生: {e}")
        error_response = f"申し訳ございません。エラーが発生しました: {str(e)}"
        
        return {
            **state,
            "ai_response": error_response,
            "step_count": state["step_count"] + 1
        }


def context_enhancement_node(state: LLMGraphState) -> LLMGraphState:
    """
    応答にコンテキストを追加するノード
    
    Args:
        state: 現在の状態
        
    Returns:
        更新された状態
    """
    print("🔍 context_enhancement_nodeが実行されました")
    
    ai_response = state.get("ai_response", "")
    step_count = state.get("step_count", 0)
    
    # コンテキスト情報を追加
    enhanced_context = f"""
--- 応答情報 ---
実行ステップ数: {step_count}
応答文字数: {len(ai_response)}
処理時刻: LangGraphで処理済み

元の応答:
{ai_response}
"""
    
    print(f"   コンテキストを追加しました")
    
    return {
        **state,
        "context": enhanced_context,
        "step_count": step_count + 1
    }


# ステップ4: 高度なLLMノード - プロンプトエンジニアリング
def advanced_llm_node(state: LLMGraphState) -> LLMGraphState:
    """
    高度なプロンプトエンジニアリングを使用するLLMノード
    
    Args:
        state: 現在の状態
        
    Returns:
        更新された状態
    """
    print("🚀 advanced_llm_nodeが実行されました")
    
    try:
        llm = setup_llm()
        user_input = state["user_input"]
        
        # 高度なシステムプロンプト
        system_prompt = """
あなたは専門的なAIアシスタントです。以下の形式で回答してください：

1. **要約**: ユーザーの質問を一文で要約
2. **回答**: 詳細で実用的な回答
3. **補足**: 関連する追加情報や提案
4. **次のステップ**: ユーザーが次に取るべき行動

回答は構造化され、実行可能で価値のある内容にしてください。
"""
        
        # 会話履歴を考慮したプロンプト
        conversation_history = "\n".join(state.get("messages", [])[-4:])  # 最新4つの履歴
        
        enhanced_prompt = f"""
{system_prompt}

会話履歴:
{conversation_history}

現在の質問: {user_input}
"""
        
        messages = [
            SystemMessage(content=enhanced_prompt),
            HumanMessage(content=user_input)
        ]
        
        response = llm.invoke(messages)
        advanced_response = response.content
        
        print(f"   高度な応答を生成しました")
        
        return {
            **state,
            "ai_response": advanced_response,
            "step_count": state["step_count"] + 1
        }
        
    except Exception as e:
        print(f"❌ 高度なLLMノードでエラー: {e}")
        return {
            **state,
            "ai_response": f"高度な処理でエラーが発生: {str(e)}",
            "step_count": state["step_count"] + 1
        }


# ステップ5: グラフの構築
def create_llm_graph():
    """
    LLMを含むグラフを作成
    
    Returns:
        コンパイル済みのグラフ
    """
    print("📊 LLMグラフを構築中...")
    
    workflow = StateGraph(LLMGraphState)
    
    # ノードを追加
    workflow.add_node("input_processing", input_processing_node)
    workflow.add_node("llm_response", llm_response_node)
    workflow.add_node("context_enhancement", context_enhancement_node)
    
    # エッジを追加
    workflow.add_edge("input_processing", "llm_response")
    workflow.add_edge("llm_response", "context_enhancement")
    workflow.add_edge("context_enhancement", END)
    
    # 開始点を設定
    workflow.set_entry_point("input_processing")
    
    return workflow.compile()


def create_advanced_llm_graph():
    """
    高度なLLMグラフを作成（条件分岐付き）
    
    Returns:
        コンパイル済みのグラフ
    """
    print("📊 高度なLLMグラフを構築中...")
    
    def decide_llm_type(state: LLMGraphState) -> str:
        """どのLLMノードを使うかを決定"""
        user_input = state.get("user_input", "")
        
        # 質問の複雑さで判断
        if any(keyword in user_input.lower() for keyword in ["詳しく", "説明", "教えて", "方法"]):
            print("   → 詳細な質問なので高度なLLMを使用")
            return "advanced_llm"
        else:
            print("   → 簡単な質問なので標準LLMを使用")
            return "standard_llm"
    
    workflow = StateGraph(LLMGraphState)
    
    # ノードを追加
    workflow.add_node("input_processing", input_processing_node)
    workflow.add_node("standard_llm", llm_response_node)
    workflow.add_node("advanced_llm", advanced_llm_node)
    workflow.add_node("context_enhancement", context_enhancement_node)
    
    # 条件分岐エッジ
    workflow.add_conditional_edges(
        "input_processing",
        decide_llm_type,
        {
            "standard_llm": "standard_llm",
            "advanced_llm": "advanced_llm"
        }
    )
    
    # 通常のエッジ
    workflow.add_edge("standard_llm", "context_enhancement")
    workflow.add_edge("advanced_llm", "context_enhancement")
    workflow.add_edge("context_enhancement", END)
    
    workflow.set_entry_point("input_processing")
    
    return workflow.compile()


# ステップ6: 実行例
def run_llm_example():
    """
    LLMグラフの実行例
    """
    print("=" * 60)
    print("🤖 LangGraph + LLM 実行開始")
    print("=" * 60)
    
    try:
        # 基本グラフを作成
        graph = create_llm_graph()
        
        # テスト質問リスト
        test_questions = [
            "こんにちは！LangGraphについて教えてください。",
            "Pythonでリストを作る方法は？",
            "今日の天気はどうですか？",
            ""  # 空の入力テスト
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 テスト {i}: {question if question else '(空の入力)'}")
            print("-" * 40)
            
            # 初期状態
            initial_state = {
                "messages": [],
                "user_input": question,
                "ai_response": "",
                "context": "",
                "step_count": 0
            }
            
            # グラフ実行
            result = graph.invoke(initial_state)
            
            print(f"\n✅ AI応答:")
            print(result["ai_response"])
            print(f"\nステップ数: {result['step_count']}")
            
    except Exception as e:
        print(f"❌ 実行エラー: {e}")


def run_advanced_llm_example():
    """
    高度なLLMグラフの実行例
    """
    print("\n" + "=" * 60)
    print("🚀 高度なLLMグラフの実行")
    print("=" * 60)
    
    try:
        graph = create_advanced_llm_graph()
        
        # 異なるタイプの質問をテスト
        questions = [
            "こんにちは",  # シンプルな挨拶
            "機械学習について詳しく教えてください"  # 複雑な質問
        ]
        
        for question in questions:
            print(f"\n📝 質問: {question}")
            print("-" * 40)
            
            result = graph.invoke({
                "messages": [],
                "user_input": question,
                "ai_response": "",
                "context": "",
                "step_count": 0
            })
            
            print(f"✅ AI応答:")
            print(result["ai_response"])
            
    except Exception as e:
        print(f"❌ 高度な実行でエラー: {e}")


def interactive_mode():
    """
    インタラクティブモード
    """
    print("\n" + "=" * 60)
    print("💬 インタラクティブモード")
    print("'quit'または'終了'で終了")
    print("=" * 60)
    
    try:
        graph = create_advanced_llm_graph()
        messages = []
        
        while True:
            user_input = input("\n質問を入力してください: ").strip()
            
            if user_input.lower() in ['quit', '終了', 'exit']:
                print("👋 インタラクティブモードを終了します")
                break
            
            if not user_input:
                print("❌ 質問を入力してください")
                continue
            
            try:
                result = graph.invoke({
                    "messages": messages,
                    "user_input": user_input,
                    "ai_response": "",
                    "context": "",
                    "step_count": 0
                })
                
                print(f"\n🤖 AI: {result['ai_response']}")
                messages = result["messages"]
                
            except Exception as e:
                print(f"❌ エラー: {e}")
                
    except KeyboardInterrupt:
        print("\n👋 プログラムを終了します")
    except Exception as e:
        print(f"❌ インタラクティブモードでエラー: {e}")


if __name__ == "__main__":
    # APIキーの確認
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OpenAI APIキーが設定されていません")
        print("以下の方法でAPIキーを設定してください:")
        print("1. 環境変数: export OPENAI_API_KEY='your-key'")
        print("2. コード内: os.environ['OPENAI_API_KEY'] = 'your-key'")
        print("\n設定後、再度実行してください")
        exit(1)
    
    # 基本例の実行
    run_llm_example()
    
    # 高度な例の実行
    run_advanced_llm_example()
    
    # インタラクティブモードの提案
    print("\n💡 次のステップ:")
    print("   - examples/06_stateful_agent.py で状態管理を学習")
    print("   - interactive_mode()を呼び出してチャットを体験")
    print("   - 異なるプロンプトやパラメータを試してみてください")
    
    # オプション: インタラクティブモードの実行
    # interactive_mode()  # コメントアウト解除で実行
