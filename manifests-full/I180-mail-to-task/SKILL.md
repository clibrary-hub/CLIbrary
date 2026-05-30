# mail-to-task Skill

## 功能概述

郵件轉任務器。解決問題：想一鍵把信轉任務

## 輸入

- `generate`: 生成內容
- `send`: 處理並發送訊息

## 輸出

- JSON 結構化結果

## 使用範例

```bash
python mail-to-task.py generate
python mail-to-task.py send
```

## 技術棧

- Python 3.8+
- argparse（CLI）
- anthropic

## 檔案結構

```
500CLI/mail-to-task/
├── mail-to-task.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python