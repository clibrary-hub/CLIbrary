# rule-conflict Skill

## 功能概述

規則衝突器。解決問題：自動化規則衝突檢查

## 輸入

- `diff`: 比對兩者差異

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python rule-conflict.py diff
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）
- pydantic

## 檔案結構

```
500CLI/rule-conflict/
├── rule-conflict.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python