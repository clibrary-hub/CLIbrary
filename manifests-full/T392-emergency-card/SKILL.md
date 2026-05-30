# emergency-card Skill

## 功能概述

緊急卡。解決問題：緊急聯絡資訊整理

## 輸入

- `diff`: 比對兩者差異

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python emergency-card.py diff
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）
- yaml

## 檔案結構

```
500CLI/emergency-card/
├── emergency-card.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python