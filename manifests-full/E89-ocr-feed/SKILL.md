# ocr-feed Skill

## 功能概述

截圖 OCR 餵入器。解決問題：截圖文字無法餵入

## 輸入

- `run`: 執行主要功能

## 輸出

- JSON 結構化結果

## 使用範例

```bash
python ocr-feed.py run
```

## 技術棧

- Python 3.8+
- Click（CLI）
- pytesseract
- Pillow

## 檔案結構

```
500CLI/ocr-feed/
├── ocr-feed.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python