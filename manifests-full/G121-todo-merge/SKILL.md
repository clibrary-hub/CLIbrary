# todo-merge Skill

## 功能概述

待辦集中器。解決問題：待辦事項散落多處

## 輸入

- `diff`: 比對兩者差異
- `run`: 執行處理流程
- `generate`: 生成內容

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python todo-merge.py diff
python todo-merge.py run
python todo-merge.py generate
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）

## 檔案結構

```
500CLI/todo-merge/
├── todo-merge.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python