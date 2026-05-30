# page-diff Skill

## 功能概述

網頁差異器。解決問題：網站變動 diff

## 輸入

- `diff`: 比對兩者差異

## 輸出

- JSON 結構化結果

## 使用範例

```bash
python page-diff.py diff
```

## 技術棧

- Python 3.8+
- Click（CLI）
- requests

## 檔案結構

```
500CLI/page-diff/
├── page-diff.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python