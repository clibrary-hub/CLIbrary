# 500 CLI 工具 — 實作進度追蹤

> 最後更新：2026-04-29  
> 此文件由 `update-progress.py` 自動產生，供 Agent 讀取以了解哪些工具已完成、哪些待實作。

## 狀態說明

| 圖示 | 狀態 | 說明 |
|------|------|------|
| ✅ | 完成 | 已完整實作，`python tool.py --help` 正常執行且無 TODO |
| ⬜ | 未實作 | skeleton 骨架，核心邏輯 `_process()` 待寫 |
| 🔵 | 部分實作 | 語法正確，已移除 TODO，但 --help 可能有問題 |
| ❌ | 執行錯誤 | 缺少依賴套件或語法錯誤，需修復 |
| ⬛ | 檔案不存在 | .py 主程式尚未建立 |

## 總覽統計

| 狀態 | 數量 | 百分比 |
|------|-----:|-------:|
| ✅ 完成 | 266 | 53.2% |
| ⬜ 未實作 | 211 | 42.2% |
| 🔵 部分實作 | 0 | 0.0% |
| ❌ 執行錯誤 | 23 | 4.6% |
| ⬛ 檔案不存在 | 0 | 0.0% |
| **合計** | **500** | **100%** |

## 類別完成度一覽

| 類別 | 名稱 | 完成 | 總計 | 進度條 |
|------|------|-----:|-----:|--------|
| A | 檔案管理與上下文 | 0 | 20 | `░░░░░░░░░░` 0% |
| B | 對話與記憶管理 | 20 | 20 | `██████████` 100% |
| C | 程式碼品質與開發輔助 | 20 | 20 | `██████████` 100% |
| D | 自動化與工作流程 | 13 | 20 | `██████░░░░` 65% |
| E | 資料處理與整合 | 14 | 20 | `███████░░░` 70% |
| F | Agent間通訊與協作 | 9 | 20 | `████░░░░░░` 45% |
| G | 個人生產力 | 20 | 20 | `██████████` 100% |
| H | 行事曆與時間管理 | 14 | 20 | `███████░░░` 70% |
| I | 郵件與通訊 | 13 | 20 | `██████░░░░` 65% |
| J | 財務與帳務 | 12 | 20 | `██████░░░░` 60% |
| K | 健康與健身 | 12 | 20 | `██████░░░░` 60% |
| L | 媒體處理 | 15 | 20 | `███████░░░` 75% |
| M | 網路爬蟲與監控 | 8 | 20 | `████░░░░░░` 40% |
| N | 資料分析與視覺化 | 20 | 20 | `██████████` 100% |
| O | AI/ML輔助 | 20 | 20 | `██████████` 100% |
| P | 安全與隱私 | 10 | 20 | `█████░░░░░` 50% |
| Q | DevOps與基礎設施 | 11 | 20 | `█████░░░░░` 55% |
| R | 知識管理與筆記 | 13 | 20 | `██████░░░░` 65% |
| S | 學習與研究 | 9 | 20 | `████░░░░░░` 45% |
| T | 旅遊與生活 | 11 | 20 | `█████░░░░░` 55% |
| U | 購物與訂閱管理 | 2 | 20 | `█░░░░░░░░░` 10% |
| V | 智慧家庭與IoT | 0 | 20 | `░░░░░░░░░░` 0% |
| W | 翻譯與在地化 | 0 | 20 | `░░░░░░░░░░` 0% |
| X | 寫作與內容創作 | 0 | 20 | `░░░░░░░░░░` 0% |
| Y | 法律合約商務 | 0 | 20 | `░░░░░░░░░░` 0% |

## Agent 實作指引

### 如何實作一個工具
1. 找到工具目錄：`500CLI/{CAT}{NUM}-{name}/`
2. 修改 `{name}.py`，將 `_process()` 改為真實邏輯（移除 TODO/placeholder）
3. 更新 `requirements.txt`（優先只用 `click>=8.0` 和 `rich>=13.0`）
4. 驗證：`python -X utf8 {name}.py --help` 應回傳 exit 0
5. 更新進度：`python -X utf8 update-progress.py`

### 依賴原則（重要）
- ✅ 優先用標準庫（ast, pathlib, re, subprocess, sqlite3, json, csv...）
- ✅ 允許：`click`, `rich`（幾乎必裝）
- ⚠️ 謹慎使用：`pandas`, `requests`（常見但較重）
- ❌ 避免：需要 API key 的套件（anthropic, openai）作為必要依賴
- ❌ 避免：`gitpython`, `whoosh`, `tiktoken` 等較冷門套件（改用 subprocess 呼叫 git）

---

## A — 檔案管理與上下文

進度：`░░░░░░░░░░` 0/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| A01 | `repo-map` | 專案結構摘要器 | ✅ | ❌ error | 語法錯誤 |
| A02 | `ctx-pack` | 智能上下文打包器 | ✅ | ❌ error | 語法錯誤 |
| A03 | `project-briefer` | 專案摘要產生器 | ✅ | ❌ error | 語法錯誤 |
| A04 | `output-tracker` | 產出追蹤器 | ✅ | ❌ error | 語法錯誤 |
| A05 | `diff-review` | 多版本差異比較器 | ✅ | ❌ error | 語法錯誤 |
| A06 | `snap-guard` | 加工前快照保護器 | ✅ | ❌ error | 語法錯誤 |
| A07 | `chunk-feeder` | 大檔案分塊餵入器 | ✅ | ❌ error | 語法錯誤 |
| A08 | `recent-changes` | 最近變更偵測器 | ✅ | ❌ error | 語法錯誤 |
| A09 | `code-clip` | 剪貼簿程式碼格式化 | ✅ | ❌ error | 語法錯誤 |
| A10 | `merge-pilot` | 多 Agent 合併解衝器 | ✅ | ❌ error | 語法錯誤 |
| A11 | `file-recall` | 模糊記憶檔案搜尋器 | ✅ | ❌ error | 語法錯誤 |
| A12 | `dup-finder` | 重複檔案偵測清理器 | ✅ | ❌ error | 語法錯誤 |
| A13 | `path-normalize` | 路徑跨平台標準化 | ✅ | ❌ error | 語法錯誤 |
| A14 | `filename-clean` | 檔名清洗器 | ✅ | ❌ error | 語法錯誤 |
| A15 | `bulk-rename` | 批次重新命名器 | ✅ | ❌ error | 語法錯誤 |
| A16 | `download-sorter` | 下載分類器 | ✅ | ❌ error | 語法錯誤 |
| A17 | `dir-weigh` | 資料夾佔用分析器 | ✅ | ❌ error | 語法錯誤 |
| A18 | `bigfile-locate` | 大檔案定位器 | ✅ | ❌ error | 語法錯誤 |
| A19 | `proj-bundle` | 專案精簡打包器 | ✅ | ❌ error | 語法錯誤 |
| A20 | `agent-pack` | Agent 互傳打包格式 | ✅ | ❌ error | 語法錯誤 |

## B — 對話與記憶管理

進度：`██████████` 20/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| B21 | `chat-grep` | 對話歷史搜尋器 | ✅ | ✅ ok |  |
| B22 | `decision-log` | 決策記錄追蹤器 | ✅ | ✅ ok |  |
| B23 | `prompt-vault` | Prompt 模板庫 | ✅ | ✅ ok |  |
| B24 | `chat-export` | 對話標準化匯出器 | ✅ | ✅ ok |  |
| B25 | `pin-msg` | 關鍵訊息釘選器 | ✅ | ✅ ok |  |
| B26 | `ctx-bridge` | 跨 Agent 上下文橋接 | ✅ | ✅ ok |  |
| B27 | `response-slim` | 回覆瘦身摘要器 | ✅ | ✅ ok |  |
| B28 | `token-meter` | Token 計量計費器 | ✅ | ✅ ok |  |
| B29 | `sysprompt-git` | System Prompt 版控 | ✅ | ✅ ok |  |
| B30 | `code-extract` | 對話程式碼提取器 | ✅ | ✅ ok |  |
| B31 | `chat-transcode` | 對話格式轉換器 | ✅ | ✅ ok |  |
| B32 | `mem-store` | 本地長期記憶庫 | ✅ | ✅ ok |  |
| B33 | `mem-reconcile` | 記憶整理整合器 | ✅ | ✅ ok |  |
| B34 | `chat-semsearch` | 語意對話搜尋 | ✅ | ✅ ok |  |
| B35 | `chat-branch` | 對話分支版控器 | ✅ | ✅ ok |  |
| B36 | `chat-to-card` | 對話卡片化 | ✅ | ✅ ok |  |
| B37 | `prompt-shield` | Prompt 注入過濾器 | ✅ | ✅ ok |  |
| B38 | `pii-redact` | PII 遮罩器 | ✅ | ✅ ok |  |
| B39 | `multi-agent-render` | 多角色對話排版 | ✅ | ✅ ok |  |
| B40 | `chat-sync` | 對話跨裝置同步 | ✅ | ✅ ok |  |

## C — 程式碼品質與開發輔助

進度：`██████████` 20/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| C41 | `lint-guard` | 自動 lint 修復 | ✅ | ✅ ok |  |
| C42 | `style-snap` | 程式碼風格擷取器 | ✅ | ✅ ok |  |
| C43 | `test-gap` | 覆蓋率缺口分析器 | ✅ | ✅ ok |  |
| C44 | `dep-audit` | 依賴審計清理器 | ✅ | ✅ ok |  |
| C45 | `sec-scan` | 安全掃描器 | ✅ | ✅ ok |  |
| C46 | `api-compat` | API 相容性檢查 | ✅ | ✅ ok |  |
| C47 | `refactor-verify` | 重構等價驗證器 | ✅ | ✅ ok |  |
| C48 | `type-fill` | 型別補全器 | ✅ | ✅ ok |  |
| C49 | `code-dedupe` | 重複碼清理器 | ✅ | ✅ ok |  |
| C50 | `doc-fill` | 文件註解填充器 | ✅ | ✅ ok |  |
| C51 | `dead-code` | 死碼偵測器 | ✅ | ✅ ok |  |
| C52 | `func-split` | 長函式拆分建議器 | ✅ | ✅ ok |  |
| C53 | `name-lint` | 命名規約檢查器 | ✅ | ✅ ok |  |
| C54 | `impact-trace` | 改動影響追蹤器 | ✅ | ✅ ok |  |
| C55 | `commit-fmt` | Commit 訊息格式器 | ✅ | ✅ ok |  |
| C56 | `pr-brief` | PR 自動摘要器 | ✅ | ✅ ok |  |
| C57 | `test-locate` | 測試對應器 | ✅ | ✅ ok |  |
| C58 | `changelog-bot` | Changelog 產生器 | ✅ | ✅ ok |  |
| C59 | `const-extract` | 常數抽取器 | ✅ | ✅ ok |  |
| C60 | `todo-board` | TODO 集中追蹤器 | ✅ | ✅ ok |  |

## D — 自動化與工作流程

進度：`██████░░░░` 13/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| D61 | `agent-macro` | Agent 巨集錄製器 | ✅ | ✅ ok |  |
| D62 | `agent-notify` | 任務通知器 | ⚠️ | ✅ ok |  |
| D63 | `agent-cron` | Agent 排程器 | ✅ | ✅ ok |  |
| D64 | `pre-check` | 環境前置檢查器 | ✅ | ✅ ok |  |
| D65 | `checkpoint` | 斷點恢復器 | ✅ | ✅ ok |  |
| D66 | `flow-tracker` | 流程進度追蹤器 | ✅ | ✅ ok |  |
| D67 | `ai-gate` | AI 品質關卡 | ✅ | ✅ ok |  |
| D68 | `agent-config` | 設定遷移器 | ✅ | ✅ ok |  |
| D69 | `agent-pool` | Agent 任務池 | ✅ | ✅ ok |  |
| D70 | `sandbox-run` | 命令沙箱執行 | ✅ | ✅ ok |  |
| D71 | `task-replay` | 任務重放器 | ✅ | ✅ ok |  |
| D72 | `human-gate` | 人類審批關卡 | ✅ | ✅ ok |  |
| D73 | `agent-queue` | 任務佇列服務 | ✅ | ✅ ok |  |
| D74 | `retry-policy` | 重試策略執行器 | ✅ | ⬜ skeleton |  |
| D75 | `timeout-shield` | 超時保護器 | ✅ | ⬜ skeleton |  |
| D76 | `rate-shaper` | 速率整形器 | ✅ | ⬜ skeleton |  |
| D77 | `agent-record` | 操作錄製器 | ✅ | ⬜ skeleton |  |
| D78 | `script-hub` | 腳本中央倉 | ✅ | ⬜ skeleton |  |
| D79 | `dry-run` | 預演模式包裝器 | ✅ | ⬜ skeleton |  |
| D80 | `flow-dash` | 流程儀表板 | ✅ | ⬜ skeleton |  |

## E — 資料處理與整合

進度：`███████░░░` 14/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| E81 | `web-clean` | 網頁清洗器 | ⚠️ | ✅ ok |  |
| E82 | `doc-to-md` | 文件轉 Markdown | ✅ | ✅ ok |  |
| E83 | `schema-brief` | Schema 摘要器 | ✅ | ✅ ok |  |
| E84 | `api-slim` | API 回應瘦身器 | ✅ | ✅ ok |  |
| E85 | `log-focus` | 日誌焦點提取器 | ✅ | ✅ ok |  |
| E86 | `env-sync` | 環境變數同步器 | ✅ | ✅ ok |  |
| E87 | `i18n-sync` | 翻譯同步器 | ✅ | ✅ ok |  |
| E88 | `git-fetch-auth` | 認證抓取器 | ✅ | ✅ ok |  |
| E89 | `ocr-feed` | 截圖 OCR 餵入器 | ✅ | ✅ ok |  |
| E90 | `format-fix` | 結構資料修復 | ✅ | ✅ ok |  |
| E91 | `csv-infer` | CSV 結構推斷器 | ✅ | ✅ ok |  |
| E92 | `json-path` | JSON 路徑搜尋器 | ✅ | ✅ ok |  |
| E93 | `data-transcode` | 多格式轉換器 | ✅ | ✅ ok |  |
| E94 | `schema-diff` | Schema 差異器 | ✅ | ✅ ok |  |
| E95 | `stream-pipe` | 串流管線器 | ✅ | ⬜ skeleton |  |
| E96 | `data-join` | 多源 join 器 | ✅ | ⬜ skeleton |  |
| E97 | `data-scrub` | 髒資料清洗器 | ✅ | ⬜ skeleton |  |
| E98 | `dq-score` | 資料品質評分器 | ✅ | ⬜ skeleton |  |
| E99 | `smart-sample` | 智慧抽樣器 | ✅ | ⬜ skeleton |  |
| E100 | `data-profile` | 資料剖析器 | ✅ | ⬜ skeleton |  |

## F — Agent間通訊與協作

進度：`████░░░░░░` 9/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| F101 | `agent-bus` | Agent 訊息匯流排 | ✅ | ✅ ok |  |
| F102 | `agent-iface` | Agent 介面適配器 | ✅ | ✅ ok |  |
| F103 | `agent-router` | 任務分派路由器 | ✅ | ✅ ok |  |
| F104 | `agent-reducer` | 結果聚合器 | ✅ | ✅ ok |  |
| F105 | `agent-acl` | Agent 權限控管 | ✅ | ✅ ok |  |
| F106 | `agent-vote` | Agent 投票決策器 | ✅ | ✅ ok |  |
| F107 | `agent-role` | 角色定義器 | ✅ | ✅ ok |  |
| F108 | `tool-registry` | 工具註冊中心 | ✅ | ✅ ok |  |
| F109 | `agent-card` | Agent 能力名片 | ✅ | ✅ ok |  |
| F110 | `agent-trace` | 跨 Agent 追蹤器 | ✅ | ⬜ skeleton |  |
| F111 | `agent-deadlock` | 死鎖偵測器 | ✅ | ⬜ skeleton |  |
| F112 | `agent-health` | Agent 健康檢測 | ✅ | ⬜ skeleton |  |
| F113 | `tool-call-norm` | Tool Call 標準化 | ✅ | ⬜ skeleton |  |
| F114 | `mcp-bridge` | MCP 協議橋接 | ✅ | ⬜ skeleton |  |
| F115 | `agent-hook` | Webhook 集中器 | ⚠️ | ⬜ skeleton |  |
| F116 | `agent-mediator` | 對話協調者 | ✅ | ⬜ skeleton |  |
| F117 | `result-cache` | 結果共享快取 | ✅ | ⬜ skeleton |  |
| F118 | `agent-bench` | Agent 評測器 | ✅ | ⬜ skeleton |  |
| F119 | `agent-billing` | 多 Agent 計費分攤 | ⚠️ | ⬜ skeleton |  |
| F120 | `agent-failover` | Agent 故障切換 | ✅ | ⬜ skeleton |  |

## G — 個人生產力

進度：`██████████` 20/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| G121 | `todo-merge` | 待辦集中器 | ✅ | ✅ ok |  |
| G122 | `pomo` | 終端番茄鐘 | ✅ | ✅ ok |  |
| G123 | `focus-log` | 專注時間記錄器 | ✅ | ✅ ok |  |
| G124 | `daily-recap` | 每日自動回顧器 | ✅ | ✅ ok |  |
| G125 | `morning-boot` | 晨啟動工作流 | ✅ | ✅ ok |  |
| G126 | `night-wind` | 睡前清場器 | ✅ | ✅ ok |  |
| G127 | `worklog` | 自動工時日誌 | ✅ | ✅ ok |  |
| G128 | `meeting-prep` | 會議準備器 | ✅ | ✅ ok |  |
| G129 | `meeting-notes` | 會議筆記器 | ✅ | ✅ ok |  |
| G130 | `weekly-report` | 週報產生器 | ✅ | ✅ ok |  |
| G131 | `okr-track` | OKR 追蹤器 | ✅ | ✅ ok |  |
| G132 | `task-breakdown` | 任務拆解器 | ✅ | ✅ ok |  |
| G133 | `time-track` | 自動時間追蹤 | ✅ | ✅ ok |  |
| G134 | `version-cleaner` | 版本清理器 | ✅ | ✅ ok |  |
| G135 | `archive-bot` | 自動封存器 | ✅ | ✅ ok |  |
| G136 | `decision-search` | 決策搜尋器 | ✅ | ✅ ok |  |
| G137 | `audio-minutes` | 會議轉摘要 | ⚠️ | ✅ ok |  |
| G138 | `inbox-zero` | 收件匣自動清空器 | ⚠️ | ✅ ok |  |
| G139 | `omni-search` | 跨工具統一搜尋 | ✅ | ✅ ok |  |
| G140 | `quick-idea` | 想法即時投擲器 | ✅ | ✅ ok |  |

## H — 行事曆與時間管理

進度：`███████░░░` 14/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| H141 | `cal-merge` | 日曆合併器 | ⚠️ | ✅ ok |  |
| H142 | `slot-find` | 共同時段搜尋 | ⚠️ | ✅ ok |  |
| H143 | `tz-convert` | 時區換算器 | ✅ | ✅ ok |  |
| H144 | `book-flow` | 預約流程器 | ⚠️ | ✅ ok |  |
| H145 | `cal-conflict` | 衝突偵測器 | ⚠️ | ✅ ok |  |
| H146 | `recur-helper` | 重複規則助手 | ✅ | ✅ ok |  |
| H147 | `trip-plan` | 行程排程器 | ✅ | ✅ ok |  |
| H148 | `reminder-rank` | 提醒優先排序 | ✅ | ✅ ok |  |
| H149 | `overwork-guard` | 過勞守門員 | ✅ | ✅ ok |  |
| H150 | `deadline-board` | 截止日看板 | ✅ | ✅ ok |  |
| H151 | `countdown` | 倒數提醒器 | ✅ | ✅ ok |  |
| H152 | `deep-work-plan` | 深工排程器 | ✅ | ✅ ok |  |
| H153 | `away-mode` | 出差代辦模式 | ✅ | ✅ ok |  |
| H154 | `nl-cal` | 自然語言建會 | ⚠️ | ✅ ok |  |
| H155 | `dnd-rules` | 勿擾規則器 | ⚠️ | ⬜ skeleton |  |
| H156 | `meeting-cost` | 會議成本計算 | ✅ | ⬜ skeleton |  |
| H157 | `study-plan` | 學習計畫追蹤 | ✅ | ⬜ skeleton |  |
| H158 | `routine-bot` | 例行事務提醒 | ✅ | ⬜ skeleton |  |
| H159 | `procrastinate-nudge` | 反拖延提醒 | ✅ | ⬜ skeleton |  |
| H160 | `time-blocks` | 時間區塊視覺化 | ✅ | ⬜ skeleton |  |

## I — 郵件與通訊

進度：`██████░░░░` 13/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| I161 | `mail-sort` | 郵件智慧分類 | ⚠️ | ✅ ok |  |
| I162 | `mail-priority` | 信件優先評分 | ⚠️ | ✅ ok |  |
| I163 | `unsub-bot` | 自動退訂器 | ⚠️ | ✅ ok |  |
| I164 | `mail-draft` | AI 草稿產生器 | ⚠️ | ✅ ok |  |
| I165 | `mail-followup` | 待回信追蹤 | ⚠️ | ✅ ok |  |
| I166 | `mail-unify` | 跨帳戶統合 | ⚠️ | ✅ ok |  |
| I167 | `thread-summarize` | 信件串摘要 | ⚠️ | ✅ ok |  |
| I168 | `mail-schedule` | 排程寄信 | ⚠️ | ✅ ok |  |
| I169 | `sig-sync` | 簽名檔同步 | ✅ | ✅ ok |  |
| I170 | `chat-search` | IM 跨平台搜尋 | ⚠️ | ✅ ok |  |
| I171 | `im-digest` | IM 摘要器 | ⚠️ | ✅ ok |  |
| I172 | `auto-reply` | 規則式自動回 | ⚠️ | ✅ ok |  |
| I173 | `chat-minutes` | IM 會議紀錄 | ⚠️ | ✅ ok |  |
| I174 | `otp-collect` | OTP 集中器 | ⚠️ | ⬜ skeleton |  |
| I175 | `mail-merge` | 客製群發器 | ⚠️ | ⬜ skeleton |  |
| I176 | `attach-vault` | 附件保管庫 | ✅ | ⬜ skeleton |  |
| I177 | `tone-shift` | 文字語氣轉換 | ✅ | ⬜ skeleton |  |
| I178 | `mail-translate` | 郵件翻譯助手 | ⚠️ | ⬜ skeleton |  |
| I179 | `mail-proof` | 郵件校稿器 | ✅ | ⬜ skeleton |  |
| I180 | `mail-to-task` | 郵件轉任務器 | ⚠️ | ⬜ skeleton |  |

## J — 財務與帳務

進度：`██████░░░░` 12/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| J181 | `expense-merge` | 跨帳戶記帳 | ⚠️ | ✅ ok |  |
| J182 | `receipt-ocr` | 收據 OCR | ✅ | ✅ ok |  |
| J183 | `expense-report` | 報帳產生器 | ✅ | ✅ ok |  |
| J184 | `sub-cost` | 訂閱總帳器 | ✅ | ✅ ok |  |
| J185 | `fx-rate` | 匯率查詢器 | ⚠️ | ✅ ok |  |
| J186 | `multi-ccy-ledger` | 多幣別帳本 | ✅ | ✅ ok |  |
| J187 | `crypto-portfolio` | 加密資產聚合 | ⚠️ | ✅ ok |  |
| J188 | `net-worth` | 淨值追蹤器 | ✅ | ✅ ok |  |
| J189 | `budget-guard` | 預算守門員 | ✅ | ✅ ok |  |
| J190 | `tax-collect` | 報稅資料收集器 | ⚠️ | ✅ ok |  |
| J191 | `invoice-vault` | 發票保管庫 | ✅ | ✅ ok |  |
| J192 | `invoice-gen` | 發票產生器 | ✅ | ✅ ok |  |
| J193 | `compound-calc` | 複利計算器 | ✅ | ⬜ skeleton |  |
| J194 | `stock-track` | 部位績效追蹤 | ⚠️ | ⬜ skeleton |  |
| J195 | `recon-bot` | 對帳機器人 | ✅ | ⬜ skeleton |  |
| J196 | `loan-calc` | 貸款試算器 | ✅ | ⬜ skeleton |  |
| J197 | `depreciate-calc` | 折舊計算器 | ✅ | ⬜ skeleton |  |
| J198 | `split-bill` | 分帳器 | ✅ | ⬜ skeleton |  |
| J199 | `tax-est` | 個稅試算器 | ⚠️ | ⬜ skeleton |  |
| J200 | `dup-charge` | 重複扣款偵測器 | ✅ | ⬜ skeleton |  |

## K — 健康與健身

進度：`██████░░░░` 12/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| K201 | `health-merge` | 健康資料整合 | ⚠️ | ✅ ok |  |
| K202 | `cal-count` | 熱量計算器 | ✅ | ✅ ok |  |
| K203 | `water-nudge` | 喝水提醒器 | ✅ | ✅ ok |  |
| K204 | `stand-up` | 起身提醒器 | ✅ | ✅ ok |  |
| K205 | `sleep-trends` | 睡眠趨勢分析 | ⚠️ | ✅ ok |  |
| K206 | `workout-plan` | 健身計畫追蹤 | ✅ | ✅ ok |  |
| K207 | `pr-log` | 個人最佳紀錄 | ✅ | ✅ ok |  |
| K208 | `run-analyze` | 跑步分析器 | ⚠️ | ✅ ok |  |
| K209 | `stretch-cron` | 拉伸提醒器 | ✅ | ✅ ok |  |
| K210 | `cycle-track` | 週期追蹤器 | ✅ | ✅ ok |  |
| K211 | `med-reminder` | 用藥提醒器 | ✅ | ✅ ok |  |
| K212 | `recipe-nutri` | 食譜營養分析 | ✅ | ✅ ok |  |
| K213 | `mood-log` | 情緒日記器 | ✅ | ⬜ skeleton |  |
| K214 | `meditate` | 冥想計時器 | ✅ | ⬜ skeleton |  |
| K215 | `weight-trend` | 體重趨勢器 | ✅ | ⬜ skeleton |  |
| K216 | `lab-explain` | 健檢報告解讀器 | ⚠️ | ⬜ skeleton |  |
| K217 | `eye-rest` | 護眼提醒器 | ✅ | ⬜ skeleton |  |
| K218 | `step-goal` | 步數目標追蹤 | ⚠️ | ⬜ skeleton |  |
| K219 | `drug-check` | 藥物交互查詢 | ⚠️ | ⬜ skeleton |  |
| K220 | `gym-route` | 健身房路徑器 | ✅ | ⬜ skeleton |  |

## L — 媒體處理

進度：`███████░░░` 15/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| L221 | `video-to-gif` | 影片轉 GIF | ✅ | ✅ ok |  |
| L222 | `video-compress` | 智慧壓縮器 | ✅ | ✅ ok |  |
| L223 | `video-trim` | 批次剪輯器 | ✅ | ✅ ok |  |
| L224 | `auto-subtitle` | 自動字幕產生器 | ⚠️ | ✅ ok |  |
| L225 | `sub-translate` | 字幕翻譯器 | ⚠️ | ✅ ok |  |
| L226 | `img-shrink` | 圖片批壓器 | ✅ | ✅ ok |  |
| L227 | `bg-remove` | 背景移除器 | ⚠️ | ✅ ok |  |
| L228 | `shot-annotate` | 截圖標註器 | ✅ | ✅ ok |  |
| L229 | `shot-blur` | 敏感區塊模糊 | ✅ | ✅ ok |  |
| L230 | `img-transcode` | 圖片格式轉換 | ✅ | ✅ ok |  |
| L231 | `thumb-make` | 縮圖產生器 | ✅ | ✅ ok |  |
| L232 | `video-recode` | 影片重編碼 | ✅ | ✅ ok |  |
| L233 | `audio-denoise` | 音訊降噪器 | ⚠️ | ✅ ok |  |
| L234 | `audio-stt` | 語音轉文字 | ⚠️ | ✅ ok |  |
| L235 | `text-tts` | 文字轉語音 | ⚠️ | ✅ ok |  |
| L236 | `live-clip` | 直播切片器 | ✅ | ⬜ skeleton |  |
| L237 | `video-summary` | 影片摘要器 | ⚠️ | ⬜ skeleton |  |
| L238 | `img-ocr` | 圖片 OCR 器 | ✅ | ⬜ skeleton |  |
| L239 | `exif-clean` | EXIF 清除器 | ✅ | ⬜ skeleton |  |
| L240 | `gif-opt` | 動圖最佳化器 | ✅ | ⬜ skeleton |  |

## M — 網路爬蟲與監控

進度：`████░░░░░░` 8/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| M241 | `web-fetch` | 網頁抓取器 | ⚠️ | ✅ ok |  |
| M242 | `headless-fetch` | Headless 抓取 | ⚠️ | ❌ error | 語法錯誤 |
| M243 | `page-watch` | 變動監控器 | ⚠️ | ✅ ok |  |
| M244 | `price-watch` | 價格追蹤器 | ⚠️ | ✅ ok |  |
| M245 | `api-monitor` | API 監測器 | ✅ | ✅ ok |  |
| M246 | `cert-watch` | 憑證守望者 | ✅ | ❌ error | 語法錯誤 |
| M247 | `rss-fold` | RSS 聚合器 | ✅ | ✅ ok |  |
| M248 | `uptime-ping` | 可達性測試器 | ✅ | ✅ ok |  |
| M249 | `link-check` | 死鏈檢查器 | ✅ | ✅ ok |  |
| M250 | `perf-audit` | 效能稽核器 | ✅ | ✅ ok |  |
| M251 | `seo-audit` | SEO 稽核器 | ✅ | ⬜ skeleton |  |
| M252 | `pcap-brief` | 抓包摘要器 | ✅ | ⬜ skeleton |  |
| M253 | `sitemap-gen` | Sitemap 產生器 | ✅ | ⬜ skeleton |  |
| M254 | `ld-extract` | 結構化資料提取 | ⚠️ | ⬜ skeleton |  |
| M255 | `web-snap-tr` | 網站翻譯快照 | ⚠️ | ⬜ skeleton |  |
| M256 | `page-archive` | 離線存檔器 | ⚠️ | ⬜ skeleton |  |
| M257 | `page-diff` | 網頁差異器 | ⚠️ | ⬜ skeleton |  |
| M258 | `polite-crawler` | 守規範爬蟲 | ⚠️ | ⬜ skeleton |  |
| M259 | `api-sniff` | API 規格嗅探器 | ⚠️ | ⬜ skeleton |  |
| M260 | `dataset-find` | 資料集發現器 | ✅ | ⬜ skeleton |  |

## N — 資料分析與視覺化

進度：`██████████` 20/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| N261 | `csv-stat` | CSV 統計器 | ✅ | ✅ ok |  |
| N262 | `term-plot` | 終端繪圖器 | ✅ | ✅ ok |  |
| N263 | `csv-sql` | CSV SQL 引擎 | ✅ | ✅ ok |  |
| N264 | `pivot-quick` | 樞紐表器 | ✅ | ✅ ok |  |
| N265 | `ab-test` | AB 檢定器 | ✅ | ✅ ok |  |
| N266 | `ts-decompose` | 時序分解器 | ✅ | ✅ ok |  |
| N267 | `anomaly-detect` | 異常偵測器 | ✅ | ✅ ok |  |
| N268 | `cluster-quick` | 快速群集器 | ✅ | ✅ ok |  |
| N269 | `eda-report` | EDA 報告器 | ✅ | ✅ ok |  |
| N270 | `regress-quick` | 快速迴歸 | ✅ | ✅ ok |  |
| N271 | `corr-matrix` | 相關矩陣器 | ✅ | ✅ ok |  |
| N272 | `chart-title` | 圖表標題器 | ✅ | ✅ ok |  |
| N273 | `chart-alt` | Alt 文字器 | ✅ | ✅ ok |  |
| N274 | `report-build` | 報表建構器 | ✅ | ✅ ok |  |
| N275 | `kpi-board` | KPI 儀表板 | ✅ | ✅ ok |  |
| N276 | `period-cmp` | 期比計算器 | ✅ | ✅ ok |  |
| N277 | `what-if` | 假設模擬器 | ✅ | ✅ ok |  |
| N278 | `cohort-analyze` | Cohort 分析器 | ✅ | ✅ ok |  |
| N279 | `data-narrate` | 資料敘事器 | ⚠️ | ✅ ok |  |
| N280 | `forecast-quick` | 快速預測器 | ✅ | ✅ ok |  |

## O — AI/ML輔助

進度：`██████████` 20/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| O281 | `llm-route` | 模型路由器 | ⚠️ | ✅ ok |  |
| O282 | `llm-compare` | 模型比對器 | ⚠️ | ✅ ok |  |
| O283 | `embed-index` | 向量索引器 | ✅ | ✅ ok |  |
| O284 | `rag-eval` | RAG 評估器 | ✅ | ✅ ok |  |
| O285 | `prompt-eval` | Prompt 評測器 | ✅ | ✅ ok |  |
| O286 | `llm-jsonschema` | JSON 驗證器 | ✅ | ✅ ok |  |
| O287 | `halluc-check` | 幻覺檢查器 | ✅ | ✅ ok |  |
| O288 | `ft-dataset` | 微調資料器 | ✅ | ✅ ok |  |
| O289 | `data-dedupe-ml` | 訓練去重器 | ✅ | ✅ ok |  |
| O290 | `llm-cost-opt` | 成本最佳化器 | ⚠️ | ✅ ok |  |
| O291 | `tok-trim` | Token 截斷器 | ✅ | ✅ ok |  |
| O292 | `agent-eval` | Agent 評測器 | ✅ | ✅ ok |  |
| O293 | `llm-cache` | LLM 快取 | ⚠️ | ✅ ok |  |
| O294 | `model-vault` | 模型版本管理 | ✅ | ✅ ok |  |
| O295 | `pi-test` | 提示注入測試器 | ✅ | ✅ ok |  |
| O296 | `embed-drift` | 嵌入漂移監測 | ✅ | ✅ ok |  |
| O297 | `ft-monitor` | 微調監測器 | ✅ | ✅ ok |  |
| O298 | `model-quant` | 模型量化器 | ✅ | ✅ ok |  |
| O299 | `infer-bench` | 推論基準器 | ✅ | ✅ ok |  |
| O300 | `llm-replay` | 流量回放器 | ✅ | ✅ ok |  |

## P — 安全與隱私

進度：`█████░░░░░` 10/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| P301 | `pwn-check` | 帳密洩漏查詢 | ⚠️ | ✅ ok |  |
| P302 | `pw-gen` | 密碼產生器 | ✅ | ✅ ok |  |
| P303 | `file-crypt` | 檔案加解密器 | ✅ | ✅ ok |  |
| P304 | `key-exchange` | 金鑰交換助手 | ✅ | ✅ ok |  |
| P305 | `secret-scan` | Secrets 掃描器 | ✅ | ✅ ok |  |
| P306 | `pii-mask` | PII 遮罩器 | ✅ | ✅ ok |  |
| P307 | `sbom-gen` | SBOM 產生器 | ✅ | ✅ ok |  |
| P308 | `cve-check` | CVE 查詢器 | ⚠️ | ✅ ok |  |
| P309 | `tls-audit` | TLS 稽核器 | ✅ | ✅ ok |  |
| P310 | `behavior-alert` | 行為告警器 | ✅ | ✅ ok |  |
| P311 | `link-safe` | 連結安全檢查 | ⚠️ | ⬜ skeleton |  |
| P312 | `policy-brief` | 隱私政策摘要 | ✅ | ⬜ skeleton |  |
| P313 | `dns-trust` | DNS 信任查詢 | ✅ | ⬜ skeleton |  |
| P314 | `vpn-config` | VPN 設定器 | ✅ | ⬜ skeleton |  |
| P315 | `watermark` | 浮水印器 | ✅ | ⬜ skeleton |  |
| P316 | `wm-detect` | 浮水印偵測器 | ✅ | ⬜ skeleton |  |
| P317 | `sig-verify` | 簽章驗證器 | ✅ | ⬜ skeleton |  |
| P318 | `key-rotate` | 金鑰輪轉器 | ⚠️ | ⬜ skeleton |  |
| P319 | `redteam-prompt` | 紅隊測試器 | ✅ | ⬜ skeleton |  |
| P320 | `gdpr-scan` | GDPR 掃描器 | ✅ | ⬜ skeleton |  |

## Q — DevOps與基礎設施

進度：`█████░░░░░` 11/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| Q321 | `docker-cleanup` | Docker 清理器 | ✅ | ✅ ok |  |
| Q322 | `compose-orch` | Compose 編排器 | ✅ | ✅ ok |  |
| Q323 | `k8s-tail` | k8s 多 Pod 日誌 | ✅ | ✅ ok |  |
| Q324 | `kctx-flip` | Context 切換器 | ✅ | ✅ ok |  |
| Q325 | `tf-brief` | Terraform 摘要器 | ✅ | ✅ ok |  |
| Q326 | `cloud-cost` | 雲端花費守門員 | ⚠️ | ✅ ok |  |
| Q327 | `ci-diag` | CI 失敗診斷器 | ✅ | ✅ ok |  |
| Q328 | `deploy-rollback` | 部署回滾器 | ✅ | ✅ ok |  |
| Q329 | `flag-cli` | Feature Flag CLI | ⚠️ | ✅ ok |  |
| Q330 | `promql-helper` | PromQL 助手 | ✅ | ✅ ok |  |
| Q331 | `grafana-port` | Grafana 搬遷器 | ⚠️ | ✅ ok |  |
| Q332 | `nginx-try` | Nginx 配置試跑器 | ✅ | ⬜ skeleton |  |
| Q333 | `slow-sql` | 慢查詢分析器 | ✅ | ⬜ skeleton |  |
| Q334 | `schema-mig` | Schema 遷移器 | ✅ | ⬜ skeleton |  |
| Q335 | `db-snap` | DB 備份器 | ✅ | ⬜ skeleton |  |
| Q336 | `log-ship` | Log Shipping 設定器 | ✅ | ⬜ skeleton |  |
| Q337 | `img-scan` | Image 漏洞掃描 | ✅ | ⬜ skeleton |  |
| Q338 | `dns-audit` | DNS 稽核器 | ✅ | ⬜ skeleton |  |
| Q339 | `ssl-renew-check` | 續期檢查 | ✅ | ⬜ skeleton |  |
| Q340 | `pipeline-tpl` | CI 樣板器 | ✅ | ⬜ skeleton |  |

## R — 知識管理與筆記

進度：`██████░░░░` 13/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| R341 | `note-search` | 筆記搜尋器 | ✅ | ✅ ok |  |
| R342 | `backlinks` | 反向連結器 | ✅ | ✅ ok |  |
| R343 | `zettel` | Zettelkasten CLI | ✅ | ✅ ok |  |
| R344 | `note-graph` | 筆記圖譜器 | ✅ | ✅ ok |  |
| R345 | `note-port` | 筆記搬遷器 | ⚠️ | ✅ ok |  |
| R346 | `md-split` | Markdown 拆分 | ✅ | ✅ ok |  |
| R347 | `note-git` | 筆記版控器 | ✅ | ✅ ok |  |
| R348 | `tag-suggest` | 標籤建議器 | ✅ | ✅ ok |  |
| R349 | `highlight-collect` | 高亮收集器 | ✅ | ✅ ok |  |
| R350 | `article-note` | 文章筆記化 | ⚠️ | ✅ ok |  |
| R351 | `note-dedupe` | 筆記去重器 | ✅ | ✅ ok |  |
| R352 | `para-link` | 段落連結器 | ✅ | ✅ ok |  |
| R353 | `know-fuse` | 知識融合器 | ✅ | ✅ ok |  |
| R354 | `card-make` | 知識卡片產生 | ✅ | ⬜ skeleton |  |
| R355 | `keypoint-pull` | 重點抽取器 | ✅ | ⬜ skeleton |  |
| R356 | `wiki-pub` | 知識庫發佈器 | ✅ | ⬜ skeleton |  |
| R357 | `bib-tidy` | BibTeX 整理器 | ✅ | ⬜ skeleton |  |
| R358 | `paper-dedupe` | 文獻去重器 | ✅ | ⬜ skeleton |  |
| R359 | `latex-fix` | LaTeX 修復器 | ✅ | ⬜ skeleton |  |
| R360 | `wiki-deploy` | Wiki 部署器 | ✅ | ⬜ skeleton |  |

## S — 學習與研究

進度：`████░░░░░░` 9/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| S361 | `paper-find` | 文獻搜尋器 | ⚠️ | ✅ ok |  |
| S362 | `paper-brief` | 論文摘要器 | ⚠️ | ✅ ok |  |
| S363 | `cite-graph` | 引用網絡器 | ⚠️ | ✅ ok |  |
| S364 | `srs-deck` | 間隔重複卡片 | ✅ | ✅ ok |  |
| S365 | `vocab-card` | 詞彙卡片器 | ✅ | ✅ ok |  |
| S366 | `lecture-notes` | 講座筆記器 | ⚠️ | ✅ ok |  |
| S367 | `book-cross` | 跨書比對器 | ⚠️ | ✅ ok |  |
| S368 | `quiz-gen` | 題目產生器 | ✅ | ✅ ok |  |
| S369 | `mock-interview` | 模擬面試器 | ✅ | ✅ ok |  |
| S370 | `exercise-judge` | 練習評測器 | ✅ | ⬜ skeleton |  |
| S371 | `concept-map` | 概念地圖器 | ✅ | ⬜ skeleton |  |
| S372 | `thesis-track` | 論文進度追蹤 | ✅ | ⬜ skeleton |  |
| S373 | `pdf-marks` | PDF 註記器 | ✅ | ⬜ skeleton |  |
| S374 | `fig-pull` | 圖表抽取器 | ⚠️ | ⬜ skeleton |  |
| S375 | `lab-log` | 實驗紀錄器 | ✅ | ⬜ skeleton |  |
| S376 | `multi-paper` | 跨語檢索器 | ⚠️ | ⬜ skeleton |  |
| S377 | `rq-split` | 問題拆解器 | ✅ | ⬜ skeleton |  |
| S378 | `paper-style` | 論文格式器 | ✅ | ⬜ skeleton |  |
| S379 | `caption-gen` | 圖說產生器 | ✅ | ⬜ skeleton |  |
| S380 | `arxiv-feed` | Arxiv 推播器 | ⚠️ | ⬜ skeleton |  |

## T — 旅遊與生活

進度：`█████░░░░░` 11/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| T381 | `trip-pack` | 行程整合器 | ⚠️ | ✅ ok |  |
| T382 | `flight-watch` | 機票追蹤器 | ⚠️ | ✅ ok |  |
| T383 | `stay-compare` | 住宿比對器 | ⚠️ | ✅ ok |  |
| T384 | `trip-budget` | 旅遊預算器 | ✅ | ✅ ok |  |
| T385 | `visa-doc` | 簽證文件清單 | ⚠️ | ✅ ok |  |
| T386 | `trip-tz` | 行程時區器 | ✅ | ✅ ok |  |
| T387 | `pack-list` | 行李清單器 | ✅ | ✅ ok |  |
| T388 | `wx-brief` | 天氣摘要器 | ⚠️ | ✅ ok |  |
| T389 | `route-build` | 路線產生器 | ⚠️ | ✅ ok |  |
| T390 | `eats-suggest` | 餐廳推薦器 | ⚠️ | ✅ ok |  |
| T391 | `menu-tr` | 菜單翻譯器 | ⚠️ | ✅ ok |  |
| T392 | `emergency-card` | 緊急卡 | ✅ | ⬜ skeleton |  |
| T393 | `lost-list` | 失物清單器 | ✅ | ⬜ skeleton |  |
| T394 | `mpg-log` | 油耗紀錄器 | ✅ | ⬜ skeleton |  |
| T395 | `transit-time` | 大眾運輸時刻 | ⚠️ | ⬜ skeleton |  |
| T396 | `trip-recap` | 遊記產生器 | ⚠️ | ⬜ skeleton |  |
| T397 | `trip-split` | 行程分帳器 | ✅ | ⬜ skeleton |  |
| T398 | `phrase-pal` | 在地用語助手 | ✅ | ⬜ skeleton |  |
| T399 | `travel-ins` | 旅保建議器 | ⚠️ | ⬜ skeleton |  |
| T400 | `trip-conflict` | 行程衝突器 | ✅ | ⬜ skeleton |  |

## U — 購物與訂閱管理

進度：`█░░░░░░░░░` 2/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| U401 | `price-cmp` | 多平台比價器 | ❌ | ✅ ok |  |
| U402 | `price-history` | 價歷追蹤器 | ⚠️ | ❌ error | 語法錯誤 |
| U403 | `shop-list` | 購物清單器 | ✅ | ✅ ok |  |
| U404 | `order-hub` | 訂單集中器 | ⚠️ | ⬜ skeleton |  |
| U405 | `return-track` | 退貨追蹤器 | ⚠️ | ⬜ skeleton |  |
| U406 | `coupon-vault` | 折價券保管庫 | ⚠️ | ⬜ skeleton |  |
| U407 | `sub-expire` | 訂閱到期器 | ✅ | ⬜ skeleton |  |
| U408 | `sub-cancel` | 訂閱取消助手 | ⚠️ | ⬜ skeleton |  |
| U409 | `restock` | 補貨提醒器 | ✅ | ⬜ skeleton |  |
| U410 | `gift-list` | 送禮清單器 | ✅ | ⬜ skeleton |  |
| U411 | `cart-nudge` | 結帳提醒器 | ⚠️ | ⬜ skeleton |  |
| U412 | `review-brief` | 評價摘要器 | ⚠️ | ⬜ skeleton |  |
| U413 | `review-real` | 假評論偵測器 | ⚠️ | ⬜ skeleton |  |
| U414 | `shop-guard` | 購物守門員 | ✅ | ⬜ skeleton |  |
| U415 | `pay-est` | 跨幣付款試算 | ✅ | ⬜ skeleton |  |
| U416 | `flash-deal` | 搶購提醒器 | ⚠️ | ⬜ skeleton |  |
| U417 | `combo-opt` | 換購最佳化器 | ✅ | ⬜ skeleton |  |
| U418 | `pantry-low` | 家庫提醒器 | ✅ | ⬜ skeleton |  |
| U419 | `resell-pm` | 二手再售助手 | ⚠️ | ⬜ skeleton |  |
| U420 | `sub-share` | 訂閱分帳器 | ✅ | ⬜ skeleton |  |

## V — 智慧家庭與IoT

進度：`░░░░░░░░░░` 0/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| V421 | `iot-bridge` | IoT 橋接器 | ⚠️ | ⬜ skeleton |  |
| V422 | `scene-flip` | 場景切換器 | ⚠️ | ⬜ skeleton |  |
| V423 | `light-schedule` | 燈光排程器 | ⚠️ | ⬜ skeleton |  |
| V424 | `hvac-rule` | 空調規則器 | ⚠️ | ⬜ skeleton |  |
| V425 | `cam-events` | 安防事件摘要 | ⚠️ | ⬜ skeleton |  |
| V426 | `lock-log` | 門鎖紀錄器 | ⚠️ | ⬜ skeleton |  |
| V427 | `power-watch` | 用電監測器 | ⚠️ | ⬜ skeleton |  |
| V428 | `solar-track` | 太陽能追蹤器 | ⚠️ | ⬜ skeleton |  |
| V429 | `print-queue` | 列印佇列器 | ✅ | ⬜ skeleton |  |
| V430 | `pet-feed` | 餵食排程器 | ⚠️ | ⬜ skeleton |  |
| V431 | `air-watch` | 空氣告警器 | ⚠️ | ⬜ skeleton |  |
| V432 | `blind-schedule` | 窗簾排程器 | ⚠️ | ⬜ skeleton |  |
| V433 | `leak-alert` | 漏水告警器 | ⚠️ | ⬜ skeleton |  |
| V434 | `nas-health` | NAS 健康檢查 | ✅ | ⬜ skeleton |  |
| V435 | `home-traffic` | 家用流量分析 | ✅ | ⬜ skeleton |  |
| V436 | `home-backup` | 家庭備份器 | ✅ | ⬜ skeleton |  |
| V437 | `cam-privacy` | 隱私模式器 | ⚠️ | ⬜ skeleton |  |
| V438 | `rule-conflict` | 規則衝突器 | ✅ | ⬜ skeleton |  |
| V439 | `mqtt-tap` | MQTT 監聽器 | ✅ | ⬜ skeleton |  |
| V440 | `energy-tip` | 節能建議器 | ✅ | ⬜ skeleton |  |

## W — 翻譯與在地化

進度：`░░░░░░░░░░` 0/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| W441 | `doc-tr` | 文件翻譯器 | ⚠️ | ⬜ skeleton |  |
| W442 | `srt-tr` | SRT 翻譯器 | ⚠️ | ⬜ skeleton |  |
| W443 | `i18n-keys` | 字串鍵管理器 | ✅ | ⬜ skeleton |  |
| W444 | `tm-store` | 翻譯記憶庫 | ✅ | ⬜ skeleton |  |
| W445 | `glossary` | 術語表管理器 | ✅ | ⬜ skeleton |  |
| W446 | `mt-eval` | MT 品質評估器 | ✅ | ⬜ skeleton |  |
| W447 | `loc-suggest` | 在地化建議器 | ⚠️ | ⬜ skeleton |  |
| W448 | `lang-align` | 多語對齊器 | ✅ | ⬜ skeleton |  |
| W449 | `str-expand-est` | 翻譯擴張估算 | ✅ | ⬜ skeleton |  |
| W450 | `i18n-seo` | i18n SEO 工具 | ✅ | ⬜ skeleton |  |
| W451 | `i18n-extract` | 字串抽取器 | ✅ | ⬜ skeleton |  |
| W452 | `plural-rules` | 複數規則器 | ✅ | ⬜ skeleton |  |
| W453 | `rtl-check` | RTL 檢查器 | ✅ | ⬜ skeleton |  |
| W454 | `font-cover` | 字型涵蓋器 | ✅ | ⬜ skeleton |  |
| W455 | `culture-lint` | 文化敏感詞 | ✅ | ⬜ skeleton |  |
| W456 | `tr-cost` | 翻譯預算器 | ✅ | ⬜ skeleton |  |
| W457 | `bi-read` | 雙語閱讀器 | ✅ | ⬜ skeleton |  |
| W458 | `img-tr` | 圖內文翻譯器 | ⚠️ | ⬜ skeleton |  |
| W459 | `stream-cc` | 即時字幕器 | ⚠️ | ⬜ skeleton |  |
| W460 | `locale-fmt` | 在地格式器 | ✅ | ⬜ skeleton |  |

## X — 寫作與內容創作

進度：`░░░░░░░░░░` 0/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| X461 | `outline-bot` | 大綱產生器 | ✅ | ⬜ skeleton |  |
| X462 | `voice-tune` | 口吻調整器 | ✅ | ⬜ skeleton |  |
| X463 | `len-flex` | 文長伸縮器 | ✅ | ⬜ skeleton |  |
| X464 | `hook-gen` | 開頭吊鉤產生器 | ✅ | ⬜ skeleton |  |
| X465 | `title-variants` | 標題變體器 | ✅ | ⬜ skeleton |  |
| X466 | `meta-gen` | Meta 標籤產生器 | ✅ | ⬜ skeleton |  |
| X467 | `cite-check` | 引用檢查器 | ✅ | ⬜ skeleton |  |
| X468 | `plag-scan` | 抄襲掃描器 | ⚠️ | ⬜ skeleton |  |
| X469 | `news-layout` | 電子報排版器 | ✅ | ⬜ skeleton |  |
| X470 | `blog-pub` | 部落格發佈器 | ⚠️ | ⬜ skeleton |  |
| X471 | `short-script` | 短影音腳本器 | ✅ | ⬜ skeleton |  |
| X472 | `podcast-script` | Podcast 腳本器 | ✅ | ⬜ skeleton |  |
| X473 | `social-post` | 社群貼文器 | ⚠️ | ⬜ skeleton |  |
| X474 | `xpost` | 跨平台重排器 | ⚠️ | ⬜ skeleton |  |
| X475 | `caption-img` | 圖配文產生器 | ✅ | ⬜ skeleton |  |
| X476 | `read-score` | 可讀性評分器 | ✅ | ⬜ skeleton |  |
| X477 | `syntax-rep` | 句法重複器 | ✅ | ⬜ skeleton |  |
| X478 | `gist-pull` | 精華抽取器 | ✅ | ⬜ skeleton |  |
| X479 | `story-arc` | 故事結構器 | ✅ | ⬜ skeleton |  |
| X480 | `quote-story` | 引用故事化器 | ✅ | ⬜ skeleton |  |

## Y — 法律合約商務

進度：`░░░░░░░░░░` 0/20 完成

| # | 工具 | 描述 | 商用 | 狀態 | 備註 |
|---|------|------|:----:|------|------|
| Y481 | `contract-brief` | 合約摘要器 | ✅ | ⬜ skeleton |  |
| Y482 | `contract-risk` | 風險條款偵測 | ✅ | ⬜ skeleton |  |
| Y483 | `redline-diff` | 合約 Redline | ✅ | ⬜ skeleton |  |
| Y484 | `nda-tpl` | NDA 模板器 | ✅ | ⬜ skeleton |  |
| Y485 | `license-compat` | 授權相容檢查 | ✅ | ⬜ skeleton |  |
| Y486 | `copyright-gen` | 著作權聲明 | ✅ | ⬜ skeleton |  |
| Y487 | `privacy-gen` | 隱私政策產生 | ✅ | ⬜ skeleton |  |
| Y488 | `tm-prelim` | 商標初查器 | ⚠️ | ⬜ skeleton |  |
| Y489 | `corp-vault` | 公司文件保管 | ✅ | ⬜ skeleton |  |
| Y490 | `quote-gen` | 報價單產生器 | ✅ | ⬜ skeleton |  |
| Y491 | `po-flow` | 採購流程器 | ✅ | ⬜ skeleton |  |
| Y492 | `mou-draft` | MOU 草擬器 | ✅ | ⬜ skeleton |  |
| Y493 | `hr-onoff` | HR 流程器 | ✅ | ⬜ skeleton |  |
| Y494 | `travel-claim` | 差旅報帳器 | ✅ | ⬜ skeleton |  |
| Y495 | `cust-onboard` | 客戶入手流程 | ✅ | ⬜ skeleton |  |
| Y496 | `ticket-route` | 客訴路由器 | ✅ | ⬜ skeleton |  |
| Y497 | `sla-watch` | SLA 守望者 | ✅ | ⬜ skeleton |  |
| Y498 | `comp-watch` | 競品監測器 | ⚠️ | ⬜ skeleton |  |
| Y499 | `bizplan-kpi` | 商計 KPI 整理 | ✅ | ⬜ skeleton |  |
| Y500 | `pitch-fmt` | 簡報排版器 | ⚠️ | ⬜ skeleton |  |
