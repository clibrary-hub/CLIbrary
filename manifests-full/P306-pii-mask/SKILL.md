# pii-mask Skill

## 功能概述

PII 遮罩器。解決問題：隱私資料遮罩

## 輸入

- `send`: 處理並發送訊息

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python pii-mask.py send
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）
- presidio-analyzer

## 檔案結構

```
500CLI/pii-mask/
├── pii-mask.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python