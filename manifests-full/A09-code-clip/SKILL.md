# code-clip Skill

## 功能概述

剪貼簿程式碼格式化。解決問題：複製貼上程式碼格式跑掉

## 輸入

- `export`: 匯出結果到檔案

## 輸出

- JSON 結構化結果
- 終端美化輸出（rich）

## 使用範例

```bash
python code-clip.py export
```

## 技術棧

- Python 3.8+
- argparse（CLI）
- Rich（終端美化）
- pyperclip
- black

## 檔案結構

```
500CLI/code-clip/
├── code-clip.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python