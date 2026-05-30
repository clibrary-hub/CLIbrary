# dup-finder Skill

## 功能概述

重複檔案偵測清理器。解決問題：大量重複檔案佔空間

## 輸入

- `scan`: 掃描並分析目標內容
- `search`: 搜尋並顯示結果

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python dup-finder.py scan
python dup-finder.py search
```

## 技術棧

- Python 3.8+
- argparse（CLI）
- Rich（終端美化）

## 檔案結構

```
500CLI/dup-finder/
├── dup-finder.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python