# agent-notify Skill

## 功能概述

任務通知器。解決問題：Agent 失敗無通知

## 輸入

- `send`: 處理並發送訊息

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python agent-notify.py send
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）
- plyer

## 檔案結構

```
500CLI/agent-notify/
├── agent-notify.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python