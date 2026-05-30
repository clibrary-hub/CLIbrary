# output-tracker Skill

## 功能概述

產出追蹤器。解決問題：Agent 產出檔案散落各處難以追蹤

## 輸入

- `diff`: 比對兩者差異
- `export`: 匯出結果到檔案

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python output-tracker.py diff
python output-tracker.py export
```

## 技術棧

- Python 3.8+
- argparse（CLI）
- Rich（終端美化）
- watchdog

## 檔案結構

```
500CLI/output-tracker/
├── output-tracker.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python