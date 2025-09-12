"""
LangGraph 外部ツールとの連携

このスクリプトでは、外部ツールとLLMエージェントの連携を学びます：
- 計算ツールの実装
- Web検索ツール（シミュレーション）
- ツール呼び出しの制御
- エラーハンドリング
- 複数ツールの組み合わせ

実行方法:
python examples/07_tool_integration.py

注意: OpenAI APIキーが必要です
"""

import os
import json
import math
import random
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
import requests
from datetime import datetime
import uuid


# ステップ1: 状態の定義
class ToolAgentState(TypedDict):
    """
    ツール統合エージェントの状態定義
    
    Attributes:
        messages: 会話メッセージの履歴
        user_input: ユーザーの入力
        tool_calls: 実行されたツール呼び出しの履歴
        tool_results: ツール実行結果
        final_response: 最終応答
        session_id: セッションID
        step_count: 実行ステップ数
    """
    messages: List[dict]
    user_input: str
    tool_calls: List[dict]
    tool_results: List[dict]
    final_response: str
    session_id: str
    step_count: int


# ステップ2: ツールの定義
@tool
def calculator_tool(expression: str) -> str:
    """
    数学計算を実行するツール
    
    Args:
        expression: 計算式（例: "2 + 3 * 4", "sqrt(16)", "sin(3.14/2)"）
        
    Returns:
        計算結果の文字列
    """
    try:
        # 安全な数学関数を定義
        safe_dict = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow,
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "log": math.log, "log10": math.log10, "exp": math.exp,
            "pi": math.pi, "e": math.e
        }
        
        # 計算を実行
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"計算結果: {expression} = {result}"
        
    except Exception as e:
        return f"計算エラー: {str(e)}"


@tool
def web_search_tool(query: str) -> str:
    """
    Web検索を実行するツール（シミュレーション版）
    
    Args:
        query: 検索クエリ
        
    Returns:
        検索結果の文字列
    """
    # 実際のWeb検索APIの代わりにシミュレーション
    simulated_results = {
        "天気": "今日の東京の天気は晴れ、気温は25度です。",
        "ニュース": "本日の主要ニュース: AI技術の発展が続いています。",
        "python": "Pythonは1991年にGuido van Rossumによって開発されたプログラミング言語です。",
        "langgraph": "LangGraphはLangChainチームが開発したグラフベースのワークフロー構築ツールです。",
        "機械学習": "機械学習は人工知能の一分野で、データから自動的にパターンを学習する技術です。",
    }
    
    query_lower = query.lower()
    for key, value in simulated_results.items():
        if key in query_lower:
            return f"検索結果 '{query}': {value}"
    
    # デフォルトの応答
    return f"検索結果 '{query}': 関連する情報が見つかりました。詳細な情報については専門サイトをご確認ください。"


@tool
def current_time_tool() -> str:
    """
    現在時刻を取得するツール
    
    Returns:
        現在時刻の文字列
    """
    now = datetime.now()
    return f"現在時刻: {now.strftime('%Y年%m月%d日 %H時%M分%S秒')}"


@tool
def random_number_tool(min_val: int = 1, max_val: int = 100) -> str:
    """
    ランダムな数値を生成するツール
    
    Args:
        min_val: 最小値
        max_val: 最大値
        
    Returns:
        ランダム数値の文字列
    """
    random_num = random.randint(min_val, max_val)
    return f"ランダム数値 ({min_val}-{max_val}): {random_num}"


@tool
def text_analyzer_tool(text: str) -> str:
    """
    テキスト分析ツール
    
    Args:
        text: 分析対象のテキスト
        
    Returns:
        分析結果の文字列
    """
    try:
        char_count = len(text)
        word_count = len(text.split())
        line_count = len(text.split('\n'))
        
        # 簡単な感情分析（キーワードベース）
        positive_words = ['嬉しい', '楽しい', '素晴らしい', '良い', 'ありがとう']
        negative_words = ['悲しい', '怒り', '困った', '悪い', '問題']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = "ポジティブ"
        elif negative_count > positive_count:
            sentiment = "ネガティブ"
        else:
            sentiment = "中性"
        
        return f"""テキスト分析結果:
- 文字数: {char_count}
- 単語数: {word_count}
- 行数: {line_count}
- 感情: {sentiment} (ポジティブ: {positive_count}, ネガティブ: {negative_count})"""
        
    except Exception as e:
        return f"分析エラー: {str(e)}"


# ステップ3: ツール管理
class ToolManager:
    """ツール管理クラス"""
    
    def __init__(self):
        self.available_tools = {
            "calculator": calculator_tool,
            "web_search": web_search_tool,
            "current_time": current_time_tool,
            "random_number": random_number_tool,
            "text_analyzer": text_analyzer_tool,
        }
    
    def get_tool_descriptions(self) -> str:
        """利用可能なツールの説明を取得"""
        descriptions = []
        for name, tool_func in self.available_tools.items():
            descriptions.append(f"- {name}: {tool_func.description}")
        return "\n".join(descriptions)
    
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """ツールを実行"""
        if tool_name in self.available_tools:
            try:
                return self.available_tools[tool_name].invoke(kwargs)
            except Exception as e:
                return f"ツール実行エラー ({tool_name}): {str(e)}"
        else:
            return f"不明なツール: {tool_name}"


# ステップ4: LLMの設定
def setup_tool_enabled_llm():
    """
    ツール対応LLMを設定
    
    Returns:
        設定済みのChatOpenAIインスタンス
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI APIキーが設定されていません")
    
    # ツール対応のLLM設定
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,  # ツール使用時は低めに設定
        max_tokens=1000,
    )
    
    # ツールをLLMにバインド
    tool_manager = ToolManager()
    tools = list(tool_manager.available_tools.values())
    llm_with_tools = llm.bind_tools(tools)
    
    return llm_with_tools, tool_manager


# ステップ5: ノードの定義
def input_analysis_node(state: ToolAgentState) -> ToolAgentState:
    """
    ユーザー入力を分析し、必要なツールを判断
    
    Args:
        state: 現在の状態
        
    Returns:
        更新された状態
    """
    print("🔍 input_analysis_nodeが実行されました")
    
    user_input = state.get("user_input", "")
    session_id = state.get("session_id", str(uuid.uuid4())[:8])
    
    print(f"   ユーザー入力: {user_input}")
    print(f"   セッションID: {session_id}")
    
    return {
        **state,
        "session_id": session_id,
        "step_count": state.get("step_count", 0) + 1
    }


def llm_planning_node(state: ToolAgentState) -> ToolAgentState:
    """
    LLMがツール使用を計画するノード
    
    Args:
        state: 現在の状態
        
    Returns:
        ツール呼び出し計画を含む状態
    """
    print("🧠 llm_planning_nodeが実行されました")
    
    try:
        llm_with_tools, tool_manager = setup_tool_enabled_llm()
        user_input = state["user_input"]
        
        # システムプロンプト
        system_prompt = f"""
あなたは様々なツールを使えるAIアシスタントです。
ユーザーの質問に答えるために、適切なツールを選択して使用してください。

利用可能なツール:
{tool_manager.get_tool_descriptions()}

ユーザーの質問に答えるために必要なツールがあれば使用し、
そうでなければ直接回答してください。

ツールを使用する場合は、適切なパラメータを指定してください。
"""
        
        # LLMにツール使用を含む応答を求める
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
        
        response = llm_with_tools.invoke(messages)
        
        # ツール呼び出しがあるかチェック
        tool_calls = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_calls.append({
                    "id": tool_call.get("id", ""),
                    "name": tool_call.get("name", ""),
                    "args": tool_call.get("args", {})
                })
                print(f"   ツール呼び出し計画: {tool_call.get('name')} with {tool_call.get('args')}")
        
        # メッセージを更新
        updated_messages = state.get("messages", [])
        updated_messages.append({
            "type": "ai",
            "content": response.content or "",
            "tool_calls": tool_calls
        })
        
        return {
            **state,
            "messages": updated_messages,
            "tool_calls": tool_calls,
            "step_count": state["step_count"] + 1
        }
        
    except Exception as e:
        print(f"❌ LLM計画ノードでエラー: {e}")
        return {
            **state,
            "final_response": f"計画エラー: {str(e)}",
            "step_count": state["step_count"] + 1
        }


def tool_execution_node(state: ToolAgentState) -> ToolAgentState:
    """
    ツールを実行するノード
    
    Args:
        state: 現在の状態
        
    Returns:
        ツール実行結果を含む状態
    """
    print("🛠️ tool_execution_nodeが実行されました")
    
    tool_calls = state.get("tool_calls", [])
    tool_results = []
    
    if not tool_calls:
        print("   実行するツールがありません")
        return state
    
    try:
        _, tool_manager = setup_tool_enabled_llm()
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name", "")
            tool_args = tool_call.get("args", {})
            
            print(f"   ツール実行: {tool_name} with args {tool_args}")
            
            # ツールを実行
            result = tool_manager.execute_tool(tool_name, **tool_args)
            
            tool_results.append({
                "tool_call_id": tool_call.get("id", ""),
                "tool_name": tool_name,
                "result": result
            })
            
            print(f"   実行結果: {result}")
        
        return {
            **state,
            "tool_results": tool_results,
            "step_count": state["step_count"] + 1
        }
        
    except Exception as e:
        print(f"❌ ツール実行でエラー: {e}")
        return {
            **state,
            "tool_results": [{"error": str(e)}],
            "step_count": state["step_count"] + 1
        }


def response_generation_node(state: ToolAgentState) -> ToolAgentState:
    """
    ツール結果を元に最終応答を生成
    
    Args:
        state: 現在の状態
        
    Returns:
        最終応答を含む状態
    """
    print("📝 response_generation_nodeが実行されました")
    
    try:
        llm, _ = setup_tool_enabled_llm()
        
        user_input = state["user_input"]
        tool_results = state.get("tool_results", [])
        messages = state.get("messages", [])
        
        # ツール結果がある場合
        if tool_results:
            # ツール結果をまとめる
            tool_summary = []
            for result in tool_results:
                if "error" in result:
                    tool_summary.append(f"エラー: {result['error']}")
                else:
                    tool_summary.append(f"{result['tool_name']}: {result['result']}")
            
            tool_summary_text = "\n".join(tool_summary)
            
            # 最終応答生成プロンプト
            final_prompt = f"""
ユーザーの質問: {user_input}

ツール実行結果:
{tool_summary_text}

上記のツール実行結果を基に、ユーザーの質問に対する適切で分かりやすい回答を生成してください。
ツールの結果を自然な形で組み込み、ユーザーにとって有用な情報を提供してください。
"""
            
            response = llm.invoke([HumanMessage(content=final_prompt)])
            final_response = response.content
            
        else:
            # ツール結果がない場合は、最後のAI応答を使用
            ai_messages = [msg for msg in messages if msg.get("type") == "ai"]
            if ai_messages:
                final_response = ai_messages[-1].get("content", "申し訳ございません。適切な回答を生成できませんでした。")
            else:
                final_response = "申し訳ございません。回答を生成できませんでした。"
        
        print(f"   最終応答生成完了")
        
        return {
            **state,
            "final_response": final_response,
            "step_count": state["step_count"] + 1
        }
        
    except Exception as e:
        print(f"❌ 応答生成でエラー: {e}")
        return {
            **state,
            "final_response": f"応答生成エラー: {str(e)}",
            "step_count": state["step_count"] + 1
        }


# ステップ6: 条件分岐の定義
def should_use_tools(state: ToolAgentState) -> str:
    """
    ツールを使用するかどうかを判断
    
    Args:
        state: 現在の状態
        
    Returns:
        次のノード名
    """
    tool_calls = state.get("tool_calls", [])
    
    if tool_calls:
        print("   → ツールを実行します")
        return "execute_tools"
    else:
        print("   → ツールを使用せず直接応答します")
        return "generate_response"


# ステップ7: グラフの構築
def create_tool_agent():
    """
    ツール統合エージェントを作成
    
    Returns:
        コンパイル済みのグラフ
    """
    print("📊 ツール統合エージェントを構築中...")
    
    workflow = StateGraph(ToolAgentState)
    
    # ノードを追加
    workflow.add_node("analyze_input", input_analysis_node)
    workflow.add_node("plan_with_llm", llm_planning_node)
    workflow.add_node("execute_tools", tool_execution_node)
    workflow.add_node("generate_response", response_generation_node)
    
    # エッジを追加
    workflow.add_edge("analyze_input", "plan_with_llm")
    
    # 条件分岐エッジ
    workflow.add_conditional_edges(
        "plan_with_llm",
        should_use_tools,
        {
            "execute_tools": "execute_tools",
            "generate_response": "generate_response"
        }
    )
    
    # ツール実行後は応答生成へ
    workflow.add_edge("execute_tools", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # 開始点を設定
    workflow.set_entry_point("analyze_input")
    
    # チェックポイント機能を有効化
    memory_saver = MemorySaver()
    graph = workflow.compile(checkpointer=memory_saver)
    
    print("✅ ツール統合エージェントの構築完了")
    return graph


# ステップ8: 実行例
def run_tool_integration_examples():
    """
    ツール統合の実行例
    """
    print("=" * 60)
    print("🛠️ ツール統合エージェント実行開始")
    print("=" * 60)
    
    try:
        agent = create_tool_agent()
        
        # テスト質問リスト
        test_questions = [
            "2 + 3 * 4を計算してください",
            "平方根16は何ですか？",
            "現在時刻を教えてください",
            "1から10の間でランダムな数字を生成してください",
            "「今日は素晴らしい一日です！ありがとう！」というテキストを分析してください",
            "Pythonについて検索してください",
            "こんにちは！元気ですか？"  # ツールを使わない質問
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*20} テスト {i} {'='*20}")
            print(f"❓ 質問: {question}")
            print("-" * 50)
            
            # セッションIDを生成
            session_id = f"tool_test_{i}"
            config = {"configurable": {"thread_id": session_id}}
            
            # 初期状態
            initial_state = {
                "messages": [],
                "user_input": question,
                "tool_calls": [],
                "tool_results": [],
                "final_response": "",
                "session_id": session_id,
                "step_count": 0
            }
            
            # エージェントを実行
            result = agent.invoke(initial_state, config=config)
            
            # 結果を表示
            print(f"\n✅ 最終応答:")
            print(result["final_response"])
            
            # ツール使用情報を表示
            if result.get("tool_calls"):
                print(f"\n🛠️ 使用されたツール:")
                for tool_call in result["tool_calls"]:
                    print(f"   - {tool_call['name']}: {tool_call['args']}")
            
            if result.get("tool_results"):
                print(f"\n📊 ツール実行結果:")
                for tool_result in result["tool_results"]:
                    if "error" not in tool_result:
                        print(f"   - {tool_result['tool_name']}: {tool_result['result']}")
            
            print(f"\n📈 実行ステップ数: {result['step_count']}")
            
    except Exception as e:
        print(f"❌ 実行エラー: {e}")


def interactive_tool_agent():
    """
    インタラクティブなツール統合エージェント
    """
    print("\n" + "=" * 60)
    print("🛠️ インタラクティブツールエージェント")
    print("'quit'または'終了'で終了")
    print("'ツール'で利用可能なツール一覧を表示")
    print("=" * 60)
    
    try:
        agent = create_tool_agent()
        tool_manager = ToolManager()
        
        print(f"\n📋 利用可能なツール:")
        print(tool_manager.get_tool_descriptions())
        
        session_id = f"interactive_tool_{uuid.uuid4().hex[:8]}"
        print(f"\n🆔 セッションID: {session_id}")
        
        while True:
            user_input = input("\n💬 質問: ").strip()
            
            if user_input.lower() in ['quit', '終了', 'exit']:
                print("👋 エージェントを終了します")
                break
            
            if user_input == 'ツール':
                print(f"\n📋 利用可能なツール:")
                print(tool_manager.get_tool_descriptions())
                continue
            
            if not user_input:
                print("❌ 質問を入力してください")
                continue
            
            try:
                config = {"configurable": {"thread_id": session_id}}
                
                initial_state = {
                    "messages": [],
                    "user_input": user_input,
                    "tool_calls": [],
                    "tool_results": [],
                    "final_response": "",
                    "session_id": session_id,
                    "step_count": 0
                }
                
                print("🔄 処理中...")
                result = agent.invoke(initial_state, config=config)
                
                print(f"\n🤖 AI: {result['final_response']}")
                
                # ツール使用情報を表示
                if result.get("tool_calls"):
                    print(f"\n🛠️ 使用ツール: {', '.join([tc['name'] for tc in result['tool_calls']])}")
                
            except Exception as e:
                print(f"❌ エラー: {e}")
                
    except KeyboardInterrupt:
        print("\n👋 エージェントを終了します")
    except Exception as e:
        print(f"❌ エージェント開始エラー: {e}")


if __name__ == "__main__":
    # APIキーの確認
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OpenAI APIキーが設定されていません")
        print("APIキーを設定してから実行してください")
        exit(1)
    
    # ツール統合例の実行
    run_tool_integration_examples()
    
    print("\n💡 完了！")
    print("   - 全てのハンズオン内容を学習しました")
    print("   - interactive_tool_agent()でリアルタイム体験")
    print("   - 自分だけのツールを追加してみてください")
    print("   - より複雑なエージェントを構築してみてください")
    
    # インタラクティブエージェントの提案
    # interactive_tool_agent()  # コメントアウト解除で実行
