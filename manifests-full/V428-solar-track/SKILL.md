# solar-track Skill

## 功能概述

太陽能追蹤器。解決問題：太陽能板產量追蹤

## 輸入

- `diff`: 比對兩者差異

## 輸出

- JSON 結構化結果

## 使用範例

```bash
python solar-track.py diff
```

## 技術棧

- Python 3.8+
- Click（CLI）
- requests

## 檔案結構

```
500CLI/solar-track/
├── solar-track.py          # 主程式
├── requirements.txt    # 依賴
├── README.md          # 使用說明
└── SKILL.md           # 本文件
```

## 擴展方向

可依據實際需求擴展 `_process` 方法，接入真實數據源或 API。

## 標籤

#cli #automation #python