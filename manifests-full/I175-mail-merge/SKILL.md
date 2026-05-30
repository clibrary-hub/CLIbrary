# mail-merge Skill

## 功能概述

客製群發器。解決問題：寄發大量個人化信

## 輸入

- `diff`: 比對兩者差異
- `send`: 處理並發送訊息

## 輸出

- JSON 結構化結果

## 使用範例

```bash
python mail-merge.py diff
python mail-merge.py send
```

## 技術棧

- Python 3.8+
- Click（CLI）
- jinja2

## 檔案結構

```
500CLI/mail-merge/
├── mail-merge.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python