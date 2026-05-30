# concept-map Skill

## 功能概述

概念地圖器。解決問題：概念地圖產生

## 輸入

- `scan`: 掃描並分析目標內容

## 輸出

- JSON 結構化結果

## 使用範例

```bash
python concept-map.py scan
```

## 技術棧

- Python 3.8+
- Click（CLI）
- networkx
- anthropic

## 檔案結構

```
500CLI/concept-map/
├── concept-map.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python