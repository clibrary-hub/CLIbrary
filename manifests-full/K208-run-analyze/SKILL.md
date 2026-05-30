# run-analyze Skill

## 功能概述

跑步分析器。解決問題：配速心率分析麻煩

## 輸入

- `scan`: 掃描並分析目標內容
- `run`: 執行處理流程

## 輸出

- JSON 結構化結果

## 使用範例

```bash
python run-analyze.py scan
python run-analyze.py run
```

## 技術棧

- Python 3.8+
- Click（CLI）
- pandas
- matplotlib

## 檔案結構

```
500CLI/run-analyze/
├── run-analyze.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python