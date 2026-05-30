# proj-bundle Skill

## 功能概述

專案精簡打包器。解決問題：想把專案壓縮給 Agent 看

## 輸入

- `export`: 匯出結果到檔案

## 輸出

- JSON 結構化結果

## 使用範例

```bash
python proj-bundle.py export
```

## 技術棧

- Python 3.8+
- argparse（CLI）
- gitpython

## 檔案結構

```
500CLI/proj-bundle/
├── proj-bundle.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python