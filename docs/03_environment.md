# 3. 環境準備

## 🐍 Python環境

### 推奨環境
- **Python**: 3.8以上（3.9以上推奨）
- **環境**: Google Colab または VSCode
- **OS**: Windows、macOS、Linux（すべて対応）

### Python バージョン確認
```bash
python --version
# または
python3 --version
```

## 📦 pipenv + requirements.txtでの環境構築

### 1. pipenvのインストール

```bash
# pipenvがインストールされていない場合
pip install pipenv

# インストール確認
pipenv --version
```

### 2. 仮想環境の作成とライブラリインストール

```bash
# プロジェクトディレクトリに移動
cd ai-agent-handson

# requirements.txtから仮想環境作成 + パッケージインストール
pipenv install -r requirements.txt

# 開発用パッケージも含めてインストール（オプション）
pipenv install --dev

# 特定のPythonバージョンを指定する場合
pipenv install -r requirements.txt --python 3.9
```

### 3. 仮想環境の使用方法

```bash
# 方法1: 仮想環境に入る
pipenv shell
# この後は通常のpythonコマンドが使用可能

# 方法2: 仮想環境内でコマンド実行
pipenv run python examples/04_hello_world.py

# 方法3: 定義済みスクリプトを使用
pipenv run hello      # Hello Worldの実行
pipenv run llm        # LLMノードの実行
pipenv run stateful   # 状態管理エージェントの実行
pipenv run tools      # ツール連携の実行
```

### 4. Google Colabの場合

```python
# Colabでは以下を最初のセルで実行（pipenvは使用できないため）
!pip install langgraph langchain langchain-openai openai python-dotenv
```

### 5. 依存関係の管理

```bash
# 新しいパッケージをrequirements.txtに追加してインストール
echo "new-package>=1.0.0" >> requirements.txt
pipenv install -r requirements.txt

# 依存関係を確認
pipenv graph

# 仮想環境の場所を確認
pipenv --venv

# 仮想環境を削除
pipenv --rm
```

## 🔑 OpenAI APIキーの設定

### APIキーの取得

1. [OpenAI Platform](https://platform.openai.com/)にアクセス
2. アカウント作成・ログイン
3. API Keys セクションでキーを生成
4. キーをコピーして保存（二度と表示されません）

### 設定方法

#### 方法1: .envファイル（推奨 - pipenvが自動読み込み）

プロジェクトルートに`.env`ファイルを作成：

```bash
# .envファイルを作成
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

pipenvは自動的に`.env`ファイルを読み込みます：

```python
import os
# pipenvが自動的に.envを読み込むため、直接取得可能
api_key = os.getenv("OPENAI_API_KEY")
```

#### 方法2: 環境変数

**macOS/Linux:**
```bash
export OPENAI_API_KEY="your-api-key-here"
pipenv shell  # 環境変数を引き継ぎ
```

**Windows:**
```cmd
set OPENAI_API_KEY=your-api-key-here
pipenv shell
```

#### 方法3: コード内で直接設定

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

⚠️ **セキュリティ注意**: コードにAPIキーを直接書く場合は、GitHubなどにアップロードしないよう注意してください。

## 🧪 動作確認

### 1. pipenv環境での基本確認

```bash
# 仮想環境に入る
pipenv shell

# または、pipenv run で実行
pipenv run python -c "
try:
    import langgraph
    import langchain
    from langchain_openai import ChatOpenAI
    print('✅ すべてのライブラリが正常にインポートされました')
    print(f'LangGraph version: {langgraph.__version__}')
    print(f'LangChain version: {langchain.__version__}')
except ImportError as e:
    print(f'❌ インポートエラー: {e}')
"
```

### 2. OpenAI API接続確認

```python
import os
from langchain_openai import ChatOpenAI

# APIキーの確認
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("✅ OpenAI APIキーが設定されています")
    
    # 簡単なテスト
    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        response = llm.invoke("Hello, can you respond with 'API connection successful'?")
        print(f"✅ API接続成功: {response.content}")
    except Exception as e:
        print(f"❌ API接続エラー: {e}")
else:
    print("❌ OpenAI APIキーが設定されていません")
```

## 🛠️ 開発環境の設定

### VSCodeの場合

#### 推奨拡張機能
- Python
- Python Debugger
- Jupyter
- Python Docstring Generator

#### settings.json設定例
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black"
}
```

### Google Colabの場合

#### 必要な設定
```python
# 最初のセルで実行
import os
from google.colab import userdata

# Colab SecretsからAPIキーを取得（推奨）
try:
    os.environ["OPENAI_API_KEY"] = userdata.get('OPENAI_API_KEY')
    print("✅ APIキーを設定しました")
except:
    print("❌ Colab SecretsにOPENAI_API_KEYを設定してください")
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. pipenvインストールエラー
```bash
# pipenvのキャッシュクリア
pipenv --clear

# 仮想環境を削除して再作成
pipenv --rm
pipenv install -r requirements.txt

# 特定のPythonバージョンを指定
pipenv install -r requirements.txt --python 3.9
```

#### 2. 依存関係の競合エラー
```bash
# Pipfile.lockを削除して再生成
rm Pipfile.lock
pipenv install -r requirements.txt

# 開発用パッケージを含めて再インストール
pipenv install --dev
```

#### 3. APIキー関連エラー
- APIキーの形式確認（sk-で始まる）
- 残高・使用制限の確認
- ファイアウォール・プロキシ設定の確認

#### 4. .envファイルが読み込まれない
```bash
# .envファイルの場所を確認
ls -la .env

# pipenv内で環境変数を確認
pipenv run python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# .envファイルの権限確認
chmod 644 .env
```

#### 5. 仮想環境の問題
```bash
# 現在の仮想環境を確認
pipenv --venv

# 仮想環境の削除と再作成
pipenv --rm
pipenv install -r requirements.txt --dev
```

## ✅ 環境準備チェックリスト

- [ ] Python 3.8以上がインストールされている
- [ ] pipenvがインストールされている
- [ ] `pipenv install -r requirements.txt --dev` が成功している
- [ ] `.env`ファイルにOpenAI APIキーが設定されている
- [ ] `pipenv run python -c "import langgraph"` が成功する
- [ ] OpenAI API接続テストが成功する
- [ ] 開発環境（VSCode/Colab）が準備されている

すべてチェックできたら、次のHello Worldグラフの作成に進みましょう！
