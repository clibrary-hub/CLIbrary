# trip-split Skill

## 功能概述

行程分帳器。解決問題：多人合分行程帳

## 輸入

- `run`: 執行主要功能

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python trip-split.py run
```

## 技術棧

- Python 3.8+
- Click（CLI）
- Rich（終端美化）

## 檔案結構

```
500CLI/trip-split/
├── trip-split.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python