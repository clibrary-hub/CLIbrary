# chat-sync Skill

## 功能概述

對話跨裝置同步。解決問題：對話備份難跨裝置

## 輸入

- `export`: 匯出結果到檔案
- `send`: 處理並發送訊息

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python chat-sync.py export
python chat-sync.py send
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）
- rsync

## 檔案結構

```
500CLI/chat-sync/
├── chat-sync.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python