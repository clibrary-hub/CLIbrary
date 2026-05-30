# mail-sort Skill

## 功能概述

郵件智慧分類。解決問題：收件匣太多分類麻煩

## 輸入

- `run`: 執行處理流程
- `send`: 處理並發送訊息

## 輸出

- JSON 結構化結果

## 使用範例

```bash
python mail-sort.py run
python mail-sort.py send
```

## 技術棧

- Python 3.8+
- Click（CLI）
- anthropic

## 檔案結構

```
500CLI/mail-sort/
├── mail-sort.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python