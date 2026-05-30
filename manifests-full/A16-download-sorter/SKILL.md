# download-sorter Skill

## 功能概述

下載分類器。解決問題：整理下載資料夾耗時

## 輸入

- `run`: 執行處理流程

## 輸出

- JSON 結構化結果

## 使用範例

```bash
python download-sorter.py run
```

## 技術棧

- Python 3.8+
- Click（CLI）

## 檔案結構

```
500CLI/download-sorter/
├── download-sorter.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python