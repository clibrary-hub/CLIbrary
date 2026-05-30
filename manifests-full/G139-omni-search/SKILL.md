# omni-search Skill

## 功能概述

跨工具統一搜尋。解決問題：跨工具搜尋很慢

## 輸入

- `search`: 搜尋並顯示結果

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python omni-search.py search
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）
- whoosh

## 檔案結構

```
500CLI/omni-search/
├── omni-search.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python