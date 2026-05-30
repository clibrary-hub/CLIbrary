# checkpoint Skill

## 功能概述

斷點恢復器。解決問題：連續作業沒有斷點恢復

## 輸入

- `scan`: 掃描並分析目標內容

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python checkpoint.py scan
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）

## 檔案結構

```
500CLI/checkpoint/
├── checkpoint.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python