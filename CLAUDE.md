# LLM Wiki Schema — Claude Code AI 知識庫

This file is the schema for this LLM Wiki. It tells Claude how to maintain this knowledge base. Follow these instructions precisely in every session.

---

## Project Purpose

這是一個關於**電動車產業**的個人知識庫，涵蓋：
- 電動乘用車（EV）
- 電動巴士（Electric Bus）
- 電動商用車（Electric Commercial Vehicle / ECV）

涵蓋維度：**產業動態、市場分析、政策法規、核心技術**

目標是隨著來源文件的累積，建立一個結構化、互相連結的知識體系，而不只是儲存原始文件。

---

## Directory Structure

```
/
├── CLAUDE.md          ← This file. The schema.
├── raw/               ← Immutable source documents. Never modify these.
│   └── assets/        ← Downloaded images referenced by sources.
└── wiki/              ← Everything you write lives here.
    ├── index.md       ← Master content catalog (always keep updated).
    ├── log.md         ← Append-only chronological record.
    ├── overview.md    ← High-level synthesis of the whole knowledge base.
    ├── countries/     ← 國家/地區分類頁面（政策、市場、產業）
    └── ...            ← Entity, concept, and topic pages.
```

**Rules:**
- Never modify files in `raw/`. They are the source of truth.
- Always update `wiki/index.md` and `wiki/log.md` after any operation.
- All wiki pages are markdown (`.md`). Use wikilinks `[[Page Name]]` for cross-references.

---

## Page Conventions

Every wiki page (except index.md and log.md) should follow this format:

```markdown
---
tags: [entity|concept|source|comparison|synthesis]
sources: [source filenames this page draws from]
updated: YYYY-MM-DD
---

# Page Title

One-paragraph summary at the top.

## Section Headings

Content...

## Related
- [[Linked Page 1]]
- [[Linked Page 2]]
```

---

## Operations

### INGEST — Adding a new source

When the user says "ingest [source]" or drops a file into `raw/`:

#### Step 0 — 確保原文存在（必做）
每一篇 `wiki/sources/` 頁必須對應至少一個 `raw/assets/` 原文檔。
- 若原文已在 `raw/assets/`：直接進行步驟 1。
- 若**尚未抓取**：先使用 **news-clipper skill**（`/news-clipper`）將原文剪輯並存入 `raw/assets/`，再繼續。
  - electrive.com、sustainable-bus.com：公開，可直接抓取。
  - digitimes.com.tw：需使用者已登入 Chrome。
  - 其他來源：嘗試直接抓取；失敗則在 frontmatter 記錄 `clipped: pending`。

#### Steps 1–8（正式流程）

1. Read the source document fully.
2. Discuss key takeaways with the user — ask what to emphasize.
3. Create `wiki/sources/[source-name].md` — a structured summary page.
   - **必填**：frontmatter 的 `sources:` 欄位必須填入對應的 `raw/assets/` 檔名。
   - 格式：`sources: [filename.md]`（可多個，逗號分隔）
4. Identify 5–15 existing wiki pages that need updating based on new info.
5. Update those pages: revise claims, add cross-references, note contradictions.
   5a. **國家頁面**：同步更新 `wiki/countries/` 下對應的國家/地區頁面（政策、市場、產業動態）。
6. If a key entity or concept has no page, create one.
7. Update `wiki/index.md` — add the new source summary and any new pages.
8. Append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] ingest | [Source Title]
   - Summary page: [[sources/source-name]]
   - Raw asset: raw/assets/[filename.md]
   - Pages updated: [[Page1]], [[Page2]], ...
   - Countries updated: [[countries/X]], [[countries/Y]], ...
   - New pages created: [[NewPage1]], ...
   - Key additions: brief note on what changed
   ```

#### Dashboard 更新（每次 ingest 後）
```bash
python3 generate_dashboard.py
git add docs/index.html wiki/ && git commit -m "update: $(date +%Y-%m-%d)" && git push
```

### QUERY — Answering questions

When the user asks a question:

1. Read `wiki/index.md` to identify relevant pages.
2. Read the relevant pages.
3. Synthesize an answer with citations (`[[page-name]]`).
4. If the answer is valuable (non-trivial), offer to file it back into the wiki as a new page.
5. Append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] query | [Question Summary]
   - Pages consulted: [[Page1]], [[Page2]], ...
   - Filed back: [[NewPage]] (if applicable)
   ```

### LINT — Health check

When the user says "lint" or "health check":

1. Read all pages in `wiki/`.
2. Report and fix:
   - Contradictions between pages
   - Stale claims superseded by newer sources
   - Orphan pages (no inbound links)
   - Important concepts mentioned but lacking their own page
   - Missing cross-references between related pages
   - Data gaps that could be filled with a web search
3. Suggest 3–5 new questions worth investigating.
4. Append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] lint
   - Issues fixed: N
   - Orphans resolved: ...
   - Suggested investigations: ...
   ```

---

## Index Format

`wiki/index.md` is organized by category. Format:

```markdown
# Wiki Index

Last updated: YYYY-MM-DD | Pages: N | Sources: N

## Sources
- [[sources/name]] — One-line summary. (YYYY-MM-DD)

## Concepts
- [[concept-name]] — One-line summary.

## Entities
- [[entity-name]] — One-line summary.

## Countries
- [[countries/國家名]] — One-line summary.

## Syntheses & Comparisons
- [[synthesis-name]] — One-line summary.
```

---

## Log Format

`wiki/log.md` entries always start with `## [YYYY-MM-DD] type | title` so they are grep-parseable.

To get the last 5 entries: `grep "^## \[" wiki/log.md | tail -5`

---

## Tone & Style

- Write wiki pages in clear, neutral, encyclopedia-style prose.
- Prefer concrete over abstract. Include examples.
- Cross-reference aggressively — if you mention a concept that has a page, link it.
- Flag uncertainty explicitly: use "As of [date]," or "Claimed by [source], unverified."
