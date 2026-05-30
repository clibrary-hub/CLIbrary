# file-recall Skill

## 功能概述

模糊記憶檔案搜尋器。解決問題：找不到上次那份檔是哪個

## 輸入

- `search`: 搜尋並顯示結果
- `send`: 處理並發送訊息

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python file-recall.py search
python file-recall.py send
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）
- whoosh

## 檔案結構

```
500CLI/file-recall/
├── file-recall.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python