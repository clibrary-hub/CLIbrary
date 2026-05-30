# schema-mig

> **Schema 遷移器**
> 分類：Q — DevOps與基礎設施 ｜ 編號：#334 ｜ 商用：✅

## 問題背景

**用戶痛點**：DB schema migration

本工具以 CLI 形式解決此問題，可獨立執行，也可串入 Agent 工作流。

## 商用狀態

✅ 完全可商用 — 純本地運算或開源套件，無第三方 API 限制。

---

## 技術規格

| 項目 | 規格 |
|------|------|
| 語言 | Python 3.11+ |
| 執行平台 | Windows / macOS / Linux |
| 介面 | CLI（`click` 框架） |
| 設定檔 | `~/.config/schema-mig/config.json` |
| 資料儲存 | 本地 SQLite / JSON（視工具而定） |

### 核心依賴

| 套件 | 用途 |
|------|------|
| `alembic` | 核心依賴 |
| `click` | 核心依賴 |
| `rich` | 核心依賴 |

---

## 安裝

```bash
# 建議使用虛擬環境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install alembic click rich

# 或從專案根目錄安裝
pip install -e .
```

### `pyproject.toml` 最小配置

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "schema-mig"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["alembic", "click", "rich"]

[project.scripts]
schema-mig = "schema_mig.cli:main"
```

---

## 目錄結構

```
schema-mig/
├── schema_mig/
│   ├── __init__.py
│   ├── cli.py          # Click 入口
│   ├── core.py         # 核心邏輯
│   └── utils.py        # 輔助函式
├── tests/
│   └── test_core.py
├── pyproject.toml
└── README.md
```

---

## CLI 介面

### 基本語法

```bash
schema-mig [OPTIONS] COMMAND [ARGS]...
```

### 子命令

| 命令 | 說明 |
|------|------|
| `run` | 執行主要功能 |
| `config` | 查看/設定組態 |
| `status` | 顯示目前狀態 |
| `export` | 匯出結果 |

### 常用選項

```
Options:
  --output, -o TEXT    輸出格式 [json|yaml|table|plain]  [default: table]
  --verbose, -v        詳細輸出
  --quiet, -q          靜音模式（只輸出結果）
  --config FILE        指定設定檔路徑
  --help               顯示說明訊息
```

### 範例

```bash
# 基本執行
schema-mig run

# 指定輸出格式
schema-mig run --output json

# 詳細模式
schema-mig run --verbose

# 靜音（適合 pipe 到其他工具）
schema-mig run --quiet | jq .

# 查看設定
schema-mig config show

# 匯出 JSON
schema-mig export --output json > result.json
```

---

## 核心實作

### `schema_mig/cli.py`

```python
import click
from rich.console import Console
from .core import SchemaMigCore

console = Console()

@click.group()
@click.option("--output", "-o", default="table",
              type=click.Choice(["json", "yaml", "table", "plain"]))
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def main(ctx, output, verbose):
    """Schema 遷移器"""
    ctx.ensure_object(dict)
    ctx.obj["output"] = output
    ctx.obj["verbose"] = verbose

@main.command()
@click.pass_context
def run(ctx):
    """執行主要功能"""
    core = SchemaMigCore()
    result = core.execute()
    if ctx.obj["output"] == "json":
        import json
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        console.print(result)

@main.command()
def config():
    """顯示或修改設定"""
    import json, pathlib
    cfg_path = pathlib.Path.home() / ".config" / "schema-mig" / "config.json"
    if cfg_path.exists():
        console.print_json(cfg_path.read_text())
    else:
        console.print("[yellow]尚未建立設定檔[/yellow]")

if __name__ == "__main__":
    main()
```

### `schema_mig/core.py`

```python
import json
import sqlite3
import pathlib
from dataclasses import dataclass, asdict
from typing import Any

DB_PATH = pathlib.Path.home() / ".config" / "schema-mig" / "data.db"

@dataclass
class Result:
    status: str
    data: Any
    message: str = ""

class SchemaMigCore:
    """
    核心邏輯類別。
    問題：DB schema migration
    解法：透過 alembic, click 實現自動化處理。
    """

    def __init__(self):
        self._init_db()

    def _init_db(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data TEXT NOT NULL
                )
            """)

    def execute(self, **kwargs) -> dict:
        """
        主執行流程：
        1. 收集輸入資料
        2. 進行核心處理
        3. 儲存結果
        4. 回傳結構化輸出
        """
        # TODO: 實作具體邏輯
        result = self._process(kwargs)
        self._save(result)
        return asdict(Result(status="ok", data=result))

    def _process(self, inputs: dict) -> Any:
        raise NotImplementedError("請實作 _process 方法")

    def _save(self, data: Any):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO records (data) VALUES (?)",
                (json.dumps(data, ensure_ascii=False),)
            )
```

---

## 輸入 / 輸出格式

### 輸入

```
stdin 或 --input 參數，支援：
- 純文字（UTF-8）
- JSON（自動偵測）
- 檔案路徑
```

### 輸出（JSON 模式）

```json
{
  "status": "ok",
  "data": {},
  "message": "",
  "meta": {
    "tool": "schema-mig",
    "version": "0.1.0",
    "timestamp": "2026-04-27T00:00:00Z"
  }
}
```

---

## 錯誤處理

| 錯誤碼 | 情境 | 處置 |
|--------|------|------|
| `E001` | 輸入格式錯誤 | 印出用法提示並退出 |
| `E002` | 相依套件缺失 | 提示安裝指令 |
| `E003` | 權限不足 | 提示以正確權限執行 |
| `E004` | 網路錯誤（如有） | 重試或離線降級 |
| `E005` | 資料庫損毀 | 備份並重建 |

```python
# 統一錯誤處理範例
import sys
from rich.console import Console

err_console = Console(stderr=True)

def handle_error(code: str, msg: str):
    err_console.print(f"[red][{code}] {msg}[/red]")
    sys.exit(1)
```

---

## Agent 串接指引

本工具設計為 Agent 友善的 CLI，可透過以下方式整合：

### 1. Tool Call 定義（MCP / Function Calling）

```json
{
  "name": "schema-mig",
  "description": "Schema 遷移器。解決問題：DB schema migration",
  "input_schema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["run", "status", "export"],
        "description": "要執行的操作"
      },
      "output_format": {
        "type": "string",
        "enum": ["json", "plain"],
        "default": "json"
      }
    },
    "required": ["action"]
  }
}
```

### 2. Shell 呼叫（適合 Claude Code / Agent SDK）

```bash
# Agent 呼叫範例
result=$(schema-mig run --quiet --output json)
echo $result | jq .data
```

### 3. Python SDK 整合

```python
import subprocess, json

def call_schema_mig(action="run") -> dict:
    proc = subprocess.run(
        ["schema-mig", action, "--output", "json", "--quiet"],
        capture_output=True, text=True
    )
    return json.loads(proc.stdout)
```

### 4. 與其他工具串接

```bash
# 管線串接範例
schema-mig run --quiet --output json \
  | jq -r '.data' \
  | other-tool process
```

---

## 測試

```bash
# 安裝測試依賴
pip install pytest pytest-cov

# 執行測試
pytest tests/ -v --cov=schema_mig --cov-report=term-missing

# 快速冒煙測試
schema-mig run --help
schema-mig config show
```

### `tests/test_core.py` 範例

```python
import pytest
from schema_mig.core import SchemaMigCore

def test_execute_returns_ok():
    core = SchemaMigCore()
    # result = core.execute()
    # assert result["status"] == "ok"
    pass  # 實作具體測試案例
```

---

## manifest.json

```json
{
  "name": "schema-mig",
  "version": "0.1.0",
  "description": "Schema 遷移器",
  "category": "Q",
  "category_name": "DevOps與基礎設施",
  "number": 334,
  "pain_point": "DB schema migration",
  "commercial": "✅",
  "language": "Python",
  "entry_point": "schema-mig",
  "dependencies": ["alembic", "click", "rich"],
  "tags": ["q", "cli", "automation"],
  "agent_compatible": true,
  "mcp_ready": true,
  "min_python": "3.11"
}
```

---

## 開發路線圖

- [ ] v0.1.0 — 基礎 CLI 功能
- [ ] v0.2.0 — 新增 `--watch` 持續監測模式
- [ ] v0.3.0 — MCP Server 包裝
- [ ] v1.0.0 — 穩定 API + 完整測試覆蓋

---

*工具編號 #334 ／ 類別 Q — DevOps與基礎設施 ／ 計畫版本 v1.0 ／ 2026-04-27*
