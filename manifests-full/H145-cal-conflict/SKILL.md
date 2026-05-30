# cal-conflict Skill

## 功能概述

衝突偵測器。解決問題：行程衝突不知道

## 輸入

- `diff`: 比對兩者差異

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python cal-conflict.py diff
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）
- icalendar

## 檔案結構

```
500CLI/cal-conflict/
├── cal-conflict.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python