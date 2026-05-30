# report-build Skill

## 功能概述

報表建構器。解決問題：想匯出 PowerBI 風格報表

## 輸入

- `generate`: 生成內容

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python report-build.py generate
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）
- jinja2

## 檔案結構

```
500CLI/report-build/
├── report-build.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python