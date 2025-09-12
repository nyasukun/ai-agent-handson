"""
LangGraph Hello World グラフ

このスクリプトでは、LangGraphの最小限の実装を学びます：
- 基本的なノードの定義
- エッジによる接続
- グラフの実行

実行方法:
python examples/04_hello_world.py
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END


# ステップ1: 状態の定義
class GraphState(TypedDict):
    """
    グラフで使用する状態を定義
    
    Attributes:
        message: 処理中のメッセージ
        step_count: 実行したステップ数
        result: 最終結果
    """
    message: str
    step_count: int
    result: str


# ステップ2: ノードの定義
def greeting_node(state: GraphState) -> GraphState:
    """
    挨拶メッセージを生成するノード
    
    Args:
        state: 現在の状態
        
    Returns:
        更新された状態
    """
    print("🚀 greeting_nodeが実行されました")
    
    # 状態を更新
    updated_state = {
        "message": "Hello, LangGraph World!",
        "step_count": state.get("step_count", 0) + 1,
        "result": state.get("result", "")
    }
    
    print(f"   メッセージ: {updated_state['message']}")
    print(f"   ステップ数: {updated_state['step_count']}")
    
    return updated_state


def processing_node(state: GraphState) -> GraphState:
    """
    メッセージを処理するノード
    
    Args:
        state: 現在の状態
        
    Returns:
        更新された状態
    """
    print("⚙️ processing_nodeが実行されました")
    
    # メッセージを処理（大文字に変換）
    processed_message = state["message"].upper()
    
    updated_state = {
        "message": processed_message,
        "step_count": state["step_count"] + 1,
        "result": state.get("result", "")
    }
    
    print(f"   処理後メッセージ: {updated_state['message']}")
    print(f"   ステップ数: {updated_state['step_count']}")
    
    return updated_state


def final_node(state: GraphState) -> GraphState:
    """
    最終結果を生成するノード
    
    Args:
        state: 現在の状態
        
    Returns:
        更新された状態
    """
    print("🎯 final_nodeが実行されました")
    
    # 最終結果を作成
    final_result = f"処理完了: {state['message']} (合計{state['step_count'] + 1}ステップ)"
    
    updated_state = {
        "message": state["message"],
        "step_count": state["step_count"] + 1,
        "result": final_result
    }
    
    print(f"   最終結果: {updated_state['result']}")
    
    return updated_state


# ステップ3: グラフの構築
def create_hello_world_graph():
    """
    Hello Worldグラフを作成
    
    Returns:
        コンパイル済みのグラフ
    """
    print("📊 グラフを構築中...")
    
    # StateGraphのインスタンスを作成
    workflow = StateGraph(GraphState)
    
    # ノードを追加
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("processing", processing_node)
    workflow.add_node("final", final_node)
    
    # エッジを追加（ノード間の接続）
    workflow.add_edge("greeting", "processing")
    workflow.add_edge("processing", "final")
    workflow.add_edge("final", END)
    
    # 開始ノードを設定
    workflow.set_entry_point("greeting")
    
    # グラフをコンパイル
    graph = workflow.compile()
    
    print("✅ グラフの構築が完了しました")
    return graph


# ステップ4: グラフの実行
def run_hello_world_example():
    """
    Hello Worldの例を実行
    """
    print("=" * 50)
    print("🌟 LangGraph Hello World 実行開始")
    print("=" * 50)
    
    # グラフを作成
    graph = create_hello_world_graph()
    
    # 初期状態を設定
    initial_state = {
        "message": "",
        "step_count": 0,
        "result": ""
    }
    
    print("\n📥 初期状態:")
    print(f"   message: '{initial_state['message']}'")
    print(f"   step_count: {initial_state['step_count']}")
    print(f"   result: '{initial_state['result']}'")
    
    print("\n🔄 グラフ実行中...")
    print("-" * 30)
    
    # グラフを実行
    try:
        final_state = graph.invoke(initial_state)
        
        print("-" * 30)
        print("\n📤 最終状態:")
        print(f"   message: '{final_state['message']}'")
        print(f"   step_count: {final_state['step_count']}")
        print(f"   result: '{final_state['result']}'")
        
        print("\n" + "=" * 50)
        print("🎉 実行完了！")
        print("=" * 50)
        
        return final_state
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return None


# ステップ5: 高度な例 - 条件分岐
def create_conditional_graph():
    """
    条件分岐を含むグラフの例
    
    Returns:
        コンパイル済みのグラフ
    """
    print("📊 条件分岐グラフを構築中...")
    
    def decision_node(state: GraphState) -> GraphState:
        """条件判断ノード"""
        print("🤔 decision_nodeが実行されました")
        return state
    
    def path_a_node(state: GraphState) -> GraphState:
        """パスA"""
        print("🅰️ path_a_nodeが実行されました")
        return {**state, "result": "パスAを通りました"}
    
    def path_b_node(state: GraphState) -> GraphState:
        """パスB"""
        print("🅱️ path_b_nodeが実行されました")
        return {**state, "result": "パスBを通りました"}
    
    def decide_path(state: GraphState) -> str:
        """どちらのパスに進むかを決定"""
        # メッセージの長さで分岐
        if len(state.get("message", "")) > 10:
            print("   → 長いメッセージなのでパスAへ")
            return "path_a"
        else:
            print("   → 短いメッセージなのでパスBへ")
            return "path_b"
    
    workflow = StateGraph(GraphState)
    
    # ノードを追加
    workflow.add_node("decision", decision_node)
    workflow.add_node("path_a", path_a_node)
    workflow.add_node("path_b", path_b_node)
    
    # 条件分岐エッジを追加
    workflow.add_conditional_edges(
        "decision",
        decide_path,
        {
            "path_a": "path_a",
            "path_b": "path_b"
        }
    )
    
    # 終了エッジ
    workflow.add_edge("path_a", END)
    workflow.add_edge("path_b", END)
    
    # 開始点設定
    workflow.set_entry_point("decision")
    
    return workflow.compile()


def run_conditional_example():
    """
    条件分岐の例を実行
    """
    print("\n" + "=" * 50)
    print("🔀 条件分岐グラフの実行")
    print("=" * 50)
    
    graph = create_conditional_graph()
    
    # 短いメッセージでテスト
    print("\n📝 テスト1: 短いメッセージ")
    result1 = graph.invoke({"message": "Hi", "step_count": 0, "result": ""})
    print(f"結果: {result1['result']}")
    
    # 長いメッセージでテスト
    print("\n📝 テスト2: 長いメッセージ")
    result2 = graph.invoke({"message": "This is a very long message", "step_count": 0, "result": ""})
    print(f"結果: {result2['result']}")


if __name__ == "__main__":
    # 基本のHello Worldを実行
    run_hello_world_example()
    
    # 条件分岐の例も実行
    run_conditional_example()
    
    print("\n💡 次のステップ:")
    print("   - examples/05_llm_node.py でLLMとの統合を学習")
    print("   - コードを改変して動作を確認してみてください")
    print("   - 新しいノードを追加してみてください")
