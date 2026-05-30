# cluster-quick Skill

## 功能概述

快速群集器。解決問題：群集分析

## 輸入

- `run`: 執行主要功能

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python cluster-quick.py run
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）
- scikit-learn

## 檔案結構

```
500CLI/cluster-quick/
├── cluster-quick.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python