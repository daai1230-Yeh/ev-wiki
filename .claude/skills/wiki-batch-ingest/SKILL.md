---
name: wiki-batch-ingest
description: 批次 ingest raw/assets 新增文章到 EV LLM Wiki（含去重、來源網址、RRC 更新、index/log/dashboard/commit/push），並回報更新了哪些 concept、countries、entities。當使用者說「有再新增一些文章」「請 ingest raw/assets」「ingest 新文章」時使用。
---

# wiki-batch-ingest — 批次 ingest 新文章

等同使用者標準指令：「有再新增一些文章 → 請 ingest raw/assets → source 要加上來源文章網址 → 最後說明哪些 concept、countries、entities 有更新」。
所有規則以專案根目錄 `CLAUDE.md` 為準（RRC 三層結構、數字敘事、DIGITIMES 用語）。

## 流程

1. **找新檔**：`git ls-files -o --exclude-standard raw/assets` 列出未追蹤檔；只處理 `.md` 新聞（`.html` 口說練習檔不是來源，略過）。
2. **去重**：標題正規化（NFKC、去空白與標點，含 【】「」：、？！引號）後比對 `git ls-files raw/assets` 與本批已有項目；標點/全形變體視為重複，維持未追蹤，不 ingest。
3. **自動覆寫檔**：剪輯器就地覆寫已追蹤檔（僅 tags/author 變動）不 stage、不 commit，最後在報告中提醒。
4. **若全為重複**：直接回報「無新文章」及原因，不改 index/log、不 commit。
5. **讀全文**，依媒體分組建立 `wiki/sources/ev-news-YYYY-MM-DD-{electrive-en|insideevs|digitimes|digest|...}.md`：
   - frontmatter：`tags: [source]`、`sources: ["raw 檔名", ...]`、`updated:`。
   - **每篇文章附原文網址**（取自 raw 檔 frontmatter `source:`）。
   - Digitimes CarTech 無單篇網址 → **不得編造**，在頁面註明「原文網址未提供（Digitimes 付費站）」並於報告說明。
   - Google Alerts digest 僅為摘錄，標註「摘錄、未查證全文」。
   - 多來源數字矛盾時並列並標「待核對」。
6. **更新 5–15+ 個既有頁**：`wiki/entities/`、`wiki/concepts/`、`wiki/countries/`。新增/大改章節用 RRC（`> **結論**` / 主因（基準→因果→so what）/ 觀察 / 參見）；把新 source slug 併入該頁 `sources:`，改 `updated:`。缺頁才新建。
7. **index.md**：新 source 行插在上一批第一行之前；更新標頭 `Last updated | Pages | Sources` 計數；新頁加入對應分類。
8. **log.md**：append `## [YYYY-MM-DD] ingest | 標題`，含 Summary page、Raw asset、Pages/Countries updated、New pages、Key additions。
9. **Dashboard 與提交**：
   ```bash
   python3 generate_dashboard.py
   git add docs/index.html wiki/ <本批新 raw 檔> && git commit -m "update: $(date +%Y-%m-%d)" && git push
   ```
   commit 結尾加：`Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`。

## 最終回報格式（繁體中文）

- 本批篇數 → 來源頁清單；跳過的重複/非來源檔
- 網址狀況（哪些有、哪些無）
- **更新的 Concepts / Countries / Entities**（分三組逐一列名）
- index 計數（Sources / Pages）
- 重點與待核對事項
- 未納入 commit 的被覆寫 raw 檔提醒
