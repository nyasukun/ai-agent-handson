# 2. 基本概念の理解

## 🌐 グラフ構造でのプログラミング

### 従来のプログラミング vs グラフ構造

#### 従来のプログラミング（線形）
```
開始 → 処理A → 処理B → 処理C → 終了
```

#### グラフ構造（非線形）
```
       ┌─ 処理B ─┐
開始 → 分岐      → 結合 → 終了
       └─ 処理C ─┘
```

### グラフ構造の利点

1. **柔軟な制御フロー**: 条件に応じた動的な処理選択
2. **並列処理**: 複数の処理を同時実行
3. **ループ処理**: 条件を満たすまで繰り返し
4. **可視化**: 処理の流れを図で表現可能

## 🔗 ノード（処理の単位）とエッジ（つなぎ方）

### ノード（Node）
処理の最小単位。以下のような役割を持ちます：

#### ノードの種類
- **処理ノード**: 実際の処理を行う（LLM呼び出し、計算など）
- **条件ノード**: 次の処理を決定する
- **開始ノード**: グラフの開始点
- **終了ノード**: グラフの終了点

#### ノードの実装例
```python
def my_node(state):
    # 状態を受け取り
    current_state = state
    
    # 何らかの処理を実行
    result = process_data(current_state["data"])
    
    # 状態を更新して返す
    return {"result": result}
```

### エッジ（Edge）
ノード間の接続を定義します：

#### エッジの種類
- **通常エッジ**: A → B の直接接続
- **条件エッジ**: 条件に応じてA → B or C
- **開始エッジ**: 開始ノードへの接続
- **終了エッジ**: 終了への接続

#### 条件エッジの例
```python
def decide_next_node(state):
    if state["score"] > 0.8:
        return "high_quality_node"
    else:
        return "improvement_node"
```

## 📊 StateGraph

### 状態管理の重要性

LangGraphでは、全ての情報を「状態（State）」として管理します。

#### 状態の役割
- **データの受け渡し**: ノード間でのデータ共有
- **履歴の保持**: 過去の処理結果を記録
- **制御情報**: 次の処理を決定するための情報

### StateGraphの基本構造

```python
from langgraph.graph import StateGraph
from typing import TypedDict, List

# 状態の定義
class AgentState(TypedDict):
    messages: List[str]
    current_step: str
    result: str

# StateGraphの作成
workflow = StateGraph(AgentState)

# ノードの追加
workflow.add_node("process_input", process_input_node)
workflow.add_node("generate_response", generate_response_node)

# エッジの追加
workflow.add_edge("process_input", "generate_response")
workflow.add_edge("generate_response", END)

# 開始点の設定
workflow.set_entry_point("process_input")
```

## 📍 チェックポイント

### 実行途中からの再開

チェックポイント機能により、以下が可能になります：

#### 1. **中断と再開**
```python
# 実行の中断
checkpoint = graph.get_state(thread_id)

# 後で再開
result = graph.invoke(input_data, thread_id=thread_id)
```

#### 2. **履歴の活用**
```python
# 過去の状態を取得
history = graph.get_state_history(thread_id)
for state in history:
    print(f"Step: {state.step}, State: {state.values}")
```

#### 3. **分岐点での選択**
```python
# 人間の判断を待つ
state = graph.invoke(input_data, interrupt_before=["human_review"])
# 人間が判断後、続行
result = graph.invoke(None, thread_id=thread_id)
```

### チェックポイントの実装例

```python
from langgraph.checkpoint.memory import MemorySaver

# メモリベースのチェックポイント
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# スレッドIDを指定して実行
thread_id = "conversation_1"
result = graph.invoke(
    {"messages": ["Hello"]},
    config={"configurable": {"thread_id": thread_id}}
)
```

## 🎯 実践への準備

これらの概念を理解したところで、次は実際に環境を準備して、コードを動かしてみましょう。

### 理解度チェック

以下の質問に答えられるか確認してください：

1. ノードとエッジの役割は？
2. StateGraphで状態を管理する利点は？
3. チェックポイント機能で何ができる？

次のセクションでは、実際にこれらの概念を使ってコードを書いていきます。
