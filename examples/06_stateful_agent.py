"""
LangGraph 状態を持つエージェント

このスクリプトでは、状態管理によるマルチターン会話を学びます：
- チェックポイントを使った会話履歴の保持
- 複数ターンにわたる文脈の維持
- ユーザーセッション管理
- メモリ機能付きチャットボット

実行方法:
python examples/06_stateful_agent.py

注意: OpenAI APIキーが必要です
"""

import os
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uuid
from datetime import datetime


# ステップ1: 状態の定義
class ConversationState(TypedDict):
    """
    会話エージェントの状態定義
    
    Attributes:
        messages: 会話メッセージの履歴
        user_name: ユーザー名
        conversation_summary: 会話の要約
        user_preferences: ユーザーの好み
        session_info: セッション情報
        turn_count: 会話のターン数
        last_topic: 最後に話した話題
    """
    messages: List[dict]
    user_name: str
    conversation_summary: str
    user_preferences: dict
    session_info: dict
    turn_count: int
    last_topic: str


# ステップ2: LLMの設定
def setup_conversational_llm():
    """
    会話用LLMを設定
    
    Returns:
        設定済みのChatOpenAIインスタンス
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI APIキーが設定されていません")
    
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.8,  # 会話らしい自然さのため少し高め
        max_tokens=800,
    )


# ステップ3: 状態管理ノード
def conversation_input_node(state: ConversationState) -> ConversationState:
    """
    会話入力を処理し、状態を更新
    
    Args:
        state: 現在の会話状態
        
    Returns:
        更新された状態
    """
    print("📝 conversation_input_nodeが実行されました")
    
    # セッション情報の初期化
    if not state.get("session_info"):
        session_info = {
            "session_id": str(uuid.uuid4())[:8],
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_activity": datetime.now().strftime("%H:%M:%S")
        }
        state["session_info"] = session_info
        print(f"   新しいセッション開始: {session_info['session_id']}")
    else:
        # 最終活動時間を更新
        state["session_info"]["last_activity"] = datetime.now().strftime("%H:%M:%S")
    
    # ターン数を増加
    state["turn_count"] = state.get("turn_count", 0) + 1
    
    print(f"   ターン数: {state['turn_count']}")
    print(f"   セッション: {state['session_info']['session_id']}")
    
    return state


def memory_retrieval_node(state: ConversationState) -> ConversationState:
    """
    過去の会話履歴から関連情報を取得
    
    Args:
        state: 現在の会話状態
        
    Returns:
        関連情報を含む更新された状態
    """
    print("🧠 memory_retrieval_nodeが実行されました")
    
    messages = state.get("messages", [])
    
    # 最近の会話から話題を抽出
    if messages:
        recent_messages = messages[-6:]  # 最新6メッセージ
        topics = []
        
        for msg in recent_messages:
            if msg.get("type") == "human":
                content = msg.get("content", "").lower()
                # 簡単なキーワード抽出
                if any(word in content for word in ["天気", "weather"]):
                    topics.append("天気")
                elif any(word in content for word in ["プログラミング", "python", "code"]):
                    topics.append("プログラミング")
                elif any(word in content for word in ["料理", "レシピ", "食べ物"]):
                    topics.append("料理")
                elif any(word in content for word in ["旅行", "観光", "travel"]):
                    topics.append("旅行")
        
        if topics:
            state["last_topic"] = topics[-1]
            print(f"   検出された話題: {topics}")
    
    # ユーザー名の抽出（初回のみ）
    if not state.get("user_name") and messages:
        for msg in messages:
            if msg.get("type") == "human":
                content = msg.get("content", "")
                if "私の名前は" in content or "僕の名前は" in content:
                    # 簡単な名前抽出
                    words = content.split()
                    for i, word in enumerate(words):
                        if word in ["私の名前は", "僕の名前は"] and i + 1 < len(words):
                            name = words[i + 1].replace("です", "").replace("。", "")
                            state["user_name"] = name
                            print(f"   ユーザー名を記録: {name}")
                            break
    
    return state


def conversational_llm_node(state: ConversationState) -> ConversationState:
    """
    会話に特化したLLM応答生成
    
    Args:
        state: 現在の会話状態
        
    Returns:
        LLM応答を含む更新された状態
    """
    print("🤖 conversational_llm_nodeが実行されました")
    
    try:
        llm = setup_conversational_llm()
        
        # 現在のメッセージを取得
        messages = state.get("messages", [])
        if not messages:
            return state
        
        current_message = messages[-1]
        if current_message.get("type") != "human":
            return state
        
        # システムプロンプトを動的に構築
        system_prompt = "あなたは親しみやすい会話パートナーです。"
        
        # ユーザー名が分かっている場合
        if state.get("user_name"):
            system_prompt += f" ユーザーの名前は{state['user_name']}さんです。"
        
        # 前の話題を考慮
        if state.get("last_topic"):
            system_prompt += f" 最近{state['last_topic']}について話していました。"
        
        # 会話のターン数を考慮
        turn_count = state.get("turn_count", 1)
        if turn_count == 1:
            system_prompt += " これは会話の始まりです。"
        elif turn_count > 10:
            system_prompt += " これは長い会話の一部です。一貫性を保ってください。"
        
        system_prompt += """
        
以下の点に注意して応答してください：
1. 自然で親しみやすい口調
2. 過去の会話内容を適切に参照
3. ユーザーの興味や好みを覚えておく
4. 質問には具体的に答える
5. 会話を続けやすい応答を心がける
"""
        
        # 会話履歴を構築（最新10ターン）
        conversation_messages = [SystemMessage(content=system_prompt)]
        
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        for msg in recent_messages:
            if msg.get("type") == "human":
                conversation_messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("type") == "ai":
                conversation_messages.append(AIMessage(content=msg["content"]))
        
        # LLMから応答を取得
        response = llm.invoke(conversation_messages)
        ai_response = response.content
        
        print(f"   応答生成完了: {ai_response[:50]}...")
        
        # 応答をメッセージ履歴に追加
        updated_messages = messages.copy()
        updated_messages.append({
            "type": "ai",
            "content": ai_response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # ユーザーの好みを更新（簡単な実装）
        preferences = state.get("user_preferences", {})
        user_message = current_message["content"].lower()
        
        if "好き" in user_message:
            if "好きなもの" not in preferences:
                preferences["好きなもの"] = []
            # 簡単なキーワード抽出
            for word in ["音楽", "映画", "本", "料理", "旅行", "スポーツ"]:
                if word in user_message:
                    if word not in preferences["好きなもの"]:
                        preferences["好きなもの"].append(word)
        
        return {
            **state,
            "messages": updated_messages,
            "user_preferences": preferences
        }
        
    except Exception as e:
        print(f"❌ 会話LLMノードでエラー: {e}")
        
        # エラー時のフォールバック応答
        error_messages = state.get("messages", []).copy()
        error_messages.append({
            "type": "ai",
            "content": "申し訳ありません。少し考えがまとまりません。もう一度話しかけてください。",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        return {
            **state,
            "messages": error_messages
        }


def conversation_summary_node(state: ConversationState) -> ConversationState:
    """
    会話の要約を生成・更新
    
    Args:
        state: 現在の会話状態
        
    Returns:
        要約を含む更新された状態
    """
    print("📋 conversation_summary_nodeが実行されました")
    
    messages = state.get("messages", [])
    turn_count = state.get("turn_count", 0)
    
    # 5ターンごとに要約を更新
    if turn_count % 5 == 0 and len(messages) >= 10:
        try:
            llm = setup_conversational_llm()
            
            # 最近の会話を要約用に整理
            recent_conversation = []
            recent_messages = messages[-10:]
            
            for msg in recent_messages:
                if msg.get("type") == "human":
                    recent_conversation.append(f"ユーザー: {msg['content']}")
                elif msg.get("type") == "ai":
                    recent_conversation.append(f"AI: {msg['content']}")
            
            conversation_text = "\n".join(recent_conversation)
            
            summary_prompt = f"""
以下の会話を簡潔に要約してください。主な話題、ユーザーの関心事、重要なポイントを含めてください。

会話:
{conversation_text}

要約:
"""
            
            response = llm.invoke([HumanMessage(content=summary_prompt)])
            summary = response.content
            
            print(f"   会話要約を更新しました")
            
            return {
                **state,
                "conversation_summary": summary
            }
            
        except Exception as e:
            print(f"❌ 要約生成でエラー: {e}")
    
    return state


# ステップ4: グラフの構築
def create_stateful_agent():
    """
    状態を持つ会話エージェントを作成
    
    Returns:
        コンパイル済みのグラフ
    """
    print("📊 状態管理エージェントを構築中...")
    
    workflow = StateGraph(ConversationState)
    
    # ノードを追加
    workflow.add_node("input_processing", conversation_input_node)
    workflow.add_node("memory_retrieval", memory_retrieval_node)
    workflow.add_node("conversational_llm", conversational_llm_node)
    workflow.add_node("summary_update", conversation_summary_node)
    
    # エッジを追加
    workflow.add_edge("input_processing", "memory_retrieval")
    workflow.add_edge("memory_retrieval", "conversational_llm")
    workflow.add_edge("conversational_llm", "summary_update")
    workflow.add_edge("summary_update", END)
    
    # 開始点を設定
    workflow.set_entry_point("input_processing")
    
    # チェックポイント機能を有効化
    memory_saver = MemorySaver()
    graph = workflow.compile(checkpointer=memory_saver)
    
    print("✅ 状態管理エージェントの構築完了")
    return graph


# ステップ5: 実行例
def run_stateful_conversation():
    """
    状態管理会話の実行例
    """
    print("=" * 60)
    print("💬 状態管理会話エージェント実行開始")
    print("=" * 60)
    
    try:
        agent = create_stateful_agent()
        
        # セッションIDを生成
        session_id = f"conversation_{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": session_id}}
        
        # 会話シミュレーション
        conversation_turns = [
            "こんにちは！私の名前は田中です。",
            "今日はプログラミングについて学びたいと思っています。",
            "Pythonは初心者にも優しい言語ですか？",
            "私は音楽と映画が好きです。",
            "LangGraphについてもっと詳しく教えてください。",
            "ありがとうございました。とても勉強になりました！"
        ]
        
        # 初期状態
        current_state = {
            "messages": [],
            "user_name": "",
            "conversation_summary": "",
            "user_preferences": {},
            "session_info": {},
            "turn_count": 0,
            "last_topic": ""
        }
        
        for i, user_input in enumerate(conversation_turns, 1):
            print(f"\n--- ターン {i} ---")
            print(f"👤 ユーザー: {user_input}")
            
            # ユーザーメッセージを状態に追加
            current_state["messages"].append({
                "type": "human",
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # エージェントを実行
            result = agent.invoke(current_state, config=config)
            
            # AI応答を表示
            ai_messages = [msg for msg in result["messages"] if msg.get("type") == "ai"]
            if ai_messages:
                latest_ai_response = ai_messages[-1]["content"]
                print(f"🤖 AI: {latest_ai_response}")
            
            # 状態を更新
            current_state = result
            
            # セッション情報を表示
            if i == 1:
                print(f"📊 セッション情報:")
                print(f"   ID: {result['session_info']['session_id']}")
                print(f"   開始時刻: {result['session_info']['start_time']}")
            
            # ユーザー情報の表示
            if result.get("user_name"):
                print(f"👤 認識されたユーザー名: {result['user_name']}")
            
            if result.get("last_topic"):
                print(f"📝 現在の話題: {result['last_topic']}")
            
            # 要約の表示（更新された場合）
            if result.get("conversation_summary") and i % 5 == 0:
                print(f"📋 会話要約: {result['conversation_summary'][:100]}...")
        
        # 最終状態の表示
        print("\n" + "=" * 60)
        print("📊 最終セッション情報")
        print("=" * 60)
        print(f"総ターン数: {current_state['turn_count']}")
        print(f"ユーザー名: {current_state.get('user_name', '不明')}")
        print(f"最後の話題: {current_state.get('last_topic', 'なし')}")
        print(f"好み: {current_state.get('user_preferences', {})}")
        print(f"メッセージ数: {len(current_state['messages'])}")
        
    except Exception as e:
        print(f"❌ 実行エラー: {e}")


def interactive_stateful_chat():
    """
    インタラクティブな状態管理チャット
    """
    print("\n" + "=" * 60)
    print("💬 インタラクティブ状態管理チャット")
    print("'quit'または'終了'で終了")
    print("'状態'で現在の状態を確認")
    print("=" * 60)
    
    try:
        agent = create_stateful_agent()
        session_id = f"interactive_{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": session_id}}
        
        # 初期状態
        current_state = {
            "messages": [],
            "user_name": "",
            "conversation_summary": "",
            "user_preferences": {},
            "session_info": {},
            "turn_count": 0,
            "last_topic": ""
        }
        
        print(f"🆔 セッションID: {session_id}")
        
        while True:
            user_input = input("\n💬 あなた: ").strip()
            
            if user_input.lower() in ['quit', '終了', 'exit']:
                print("👋 チャットを終了します")
                break
            
            if user_input == '状態':
                print(f"\n📊 現在の状態:")
                print(f"   ターン数: {current_state.get('turn_count', 0)}")
                print(f"   ユーザー名: {current_state.get('user_name', '未設定')}")
                print(f"   最後の話題: {current_state.get('last_topic', 'なし')}")
                print(f"   好み: {current_state.get('user_preferences', {})}")
                print(f"   メッセージ数: {len(current_state.get('messages', []))}")
                continue
            
            if not user_input:
                print("❌ メッセージを入力してください")
                continue
            
            try:
                # ユーザーメッセージを追加
                current_state["messages"].append({
                    "type": "human",
                    "content": user_input,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                
                # エージェント実行
                result = agent.invoke(current_state, config=config)
                
                # AI応答を表示
                ai_messages = [msg for msg in result["messages"] if msg.get("type") == "ai"]
                if ai_messages:
                    latest_ai_response = ai_messages[-1]["content"]
                    print(f"🤖 AI: {latest_ai_response}")
                
                current_state = result
                
            except Exception as e:
                print(f"❌ エラー: {e}")
                
    except KeyboardInterrupt:
        print("\n👋 チャットを終了します")
    except Exception as e:
        print(f"❌ チャット開始エラー: {e}")


if __name__ == "__main__":
    # APIキーの確認
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OpenAI APIキーが設定されていません")
        print("APIキーを設定してから実行してください")
        exit(1)
    
    # 状態管理会話の例を実行
    run_stateful_conversation()
    
    print("\n💡 次のステップ:")
    print("   - examples/07_tool_integration.py で外部ツール連携を学習")
    print("   - interactive_stateful_chat()でリアルタイムチャットを体験")
    print("   - 異なる会話パターンを試してみてください")
    
    # インタラクティブチャットの提案
    # interactive_stateful_chat()  # コメントアウト解除で実行
