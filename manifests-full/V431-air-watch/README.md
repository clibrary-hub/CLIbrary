# air-watch

> **空氣告警器**
> 分類：V — 智慧家庭與IoT ｜ 編號：#431 ｜ 商用：⚠️

## 問題背景

**用戶痛點**：室內空氣品質告警

本工具以 CLI 形式解決此問題，可獨立執行，也可串入 Agent 工作流。

## 商用狀態

⚠️ 受限商用 — 需用戶自帶 API Key（BYOK）或遵守第三方服務條款。

---

## 技術規格

| 項目 | 規格 |
|------|------|
| 語言 | Python 3.11+ |
| 執行平台 | Windows / macOS / Linux |
| 介面 | CLI（`click` 框架） |
| 設定檔 | `~/.config/air-watch/config.json` |
| 資料儲存 | 本地 SQLite / JSON（視工具而定） |

### 核心依賴

| 套件 | 用途 |
|------|------|
| `paho-mqtt` | 核心依賴 |
| `click` | 核心依賴 |
| `rich` | 核心依賴 |

---

## 安裝

```bash
# 建議使用虛擬環境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install paho-mqtt click rich

# 或從專案根目錄安裝
pip install -e .
```

### `pyproject.toml` 最小配置

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "air-watch"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["paho-mqtt", "click", "rich"]

[project.scripts]
air-watch = "air_watch.cli:main"
```

---

## 目錄結構

```
air-watch/
├── air_watch/
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
air-watch [OPTIONS] COMMAND [ARGS]...
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
air-watch run

# 指定輸出格式
air-watch run --output json

# 詳細模式
air-watch run --verbose

# 靜音（適合 pipe 到其他工具）
air-watch run --quiet | jq .

# 查看設定
air-watch config show

# 匯出 JSON
air-watch export --output json > result.json
```

---

## 核心實作

### `air_watch/cli.py`

```python
import click
from rich.console import Console
from .core import AirWatchCore

console = Console()

@click.group()
@click.option("--output", "-o", default="table",
              type=click.Choice(["json", "yaml", "table", "plain"]))
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def main(ctx, output, verbose):
    """空氣告警器"""
    ctx.ensure_object(dict)
    ctx.obj["output"] = output
    ctx.obj["verbose"] = verbose

@main.command()
@click.pass_context
def run(ctx):
    """執行主要功能"""
    core = AirWatchCore()
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
    cfg_path = pathlib.Path.home() / ".config" / "air-watch" / "config.json"
    if cfg_path.exists():
        console.print_json(cfg_path.read_text())
    else:
        console.print("[yellow]尚未建立設定檔[/yellow]")

if __name__ == "__main__":
    main()
```

### `air_watch/core.py`

```python
import json
import sqlite3
import pathlib
from dataclasses import dataclass, asdict
from typing import Any

DB_PATH = pathlib.Path.home() / ".config" / "air-watch" / "data.db"

@dataclass
class Result:
    status: str
    data: Any
    message: str = ""

class AirWatchCore:
    """
    核心邏輯類別。
    問題：室內空氣品質告警
    解法：透過 paho-mqtt, click 實現自動化處理。
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
    "tool": "air-watch",
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
  "name": "air-watch",
  "description": "空氣告警器。解決問題：室內空氣品質告警",
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
result=$(air-watch run --quiet --output json)
echo $result | jq .data
```

### 3. Python SDK 整合

```python
import subprocess, json

def call_air_watch(action="run") -> dict:
    proc = subprocess.run(
        ["air-watch", action, "--output", "json", "--quiet"],
        capture_output=True, text=True
    )
    return json.loads(proc.stdout)
```

### 4. 與其他工具串接

```bash
# 管線串接範例
air-watch run --quiet --output json \
  | jq -r '.data' \
  | other-tool process
```

---

## 測試

```bash
# 安裝測試依賴
pip install pytest pytest-cov

# 執行測試
pytest tests/ -v --cov=air_watch --cov-report=term-missing

# 快速冒煙測試
air-watch run --help
air-watch config show
```

### `tests/test_core.py` 範例

```python
import pytest
from air_watch.core import AirWatchCore

def test_execute_returns_ok():
    core = AirWatchCore()
    # result = core.execute()
    # assert result["status"] == "ok"
    pass  # 實作具體測試案例
```

---

## manifest.json

```json
{
  "name": "air-watch",
  "version": "0.1.0",
  "description": "空氣告警器",
  "category": "V",
  "category_name": "智慧家庭與IoT",
  "number": 431,
  "pain_point": "室內空氣品質告警",
  "commercial": "⚠️",
  "language": "Python",
  "entry_point": "air-watch",
  "dependencies": ["paho-mqtt", "click", "rich"],
  "tags": ["v", "cli", "automation"],
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

*工具編號 #431 ／ 類別 V — 智慧家庭與IoT ／ 計畫版本 v1.0 ／ 2026-04-27*
