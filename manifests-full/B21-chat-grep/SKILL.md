# chat-grep Skill

## 功能概述

對話歷史搜尋器。解決問題：歷史對話無法搜尋

## 輸入

- `search`: 搜尋並顯示結果
- `send`: 處理並發送訊息

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python chat-grep.py search
python chat-grep.py send
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）

## 檔案結構

```
500CLI/chat-grep/
├── chat-grep.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python