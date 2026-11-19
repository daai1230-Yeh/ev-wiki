#!/usr/bin/env python3
"""
EV Knowledge Base — Dashboard Generator
Reads wiki/ markdown files and writes docs/index.html (GitHub Pages ready).

Usage:
    python generate_dashboard.py

After each ingest, run this script, then push docs/index.html to GitHub.
"""

import re, json, sys
from pathlib import Path
from datetime import datetime

WIKI_DIR  = Path(__file__).parent / "wiki"
OUTPUT_DIR = Path(__file__).parent / "docs"

# ─────────────────────────── Parsers ────────────────────────────────────────

def parse_frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n?(.*)', text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, rest = m.group(1), m.group(2)
    fm = {}
    tags_m = re.search(r'tags:\s*\[([^\]]*)\]', fm_text)
    if tags_m:
        fm['tags'] = [t.strip() for t in tags_m.group(1).split(',') if t.strip()]
    src_m = re.search(r'sources:\s*\[([^\]]*)\]', fm_text, re.DOTALL)
    if src_m:
        s = src_m.group(1).replace('\n', ' ')
        fm['sources'] = [x.strip() for x in s.split(',') if x.strip()]
    upd_m = re.search(r'updated:\s*(\S+)', fm_text)
    if upd_m:
        fm['updated'] = upd_m.group(1)
    return fm, rest

def first_paragraph(text, max_len=200):
    buf, started = [], False
    for line in text.split('\n'):
        s = line.strip()
        if s.startswith('#'):
            if started: break
            continue
        if not s:
            if started: break
            continue
        buf.append(s)
        started = True
    joined = ' '.join(buf)
    return joined[:max_len] + ('…' if len(joined) > max_len else '')

def parse_index():
    content = (WIKI_DIR / "index.md").read_text(encoding='utf-8')
    m = re.search(r'Last updated: ([\d-]+) \| Pages: (\d+) \| Sources: (\d+)', content)
    stats = {'last_updated': '—', 'pages': 0, 'sources': 0}
    if m:
        stats = {'last_updated': m.group(1), 'pages': int(m.group(2)), 'sources': int(m.group(3))}

    sections, current = {}, None
    for line in content.split('\n'):
        h3 = re.match(r'^### (.+)', line)
        if h3:
            current = h3.group(1)
            sections[current] = []
            continue
        if line.startswith('- [[sources/') and current:
            m2 = re.match(r'- \[\[sources/([^\]]+)\]\] — (.+?)(?:\s*\(([^)]+)\))?\s*$', line)
            if m2:
                sections[current].append({
                    'name': m2.group(1),
                    'desc': m2.group(2).strip(),
                    'date': m2.group(3) or ''
                })
    return stats, {k: v for k, v in sections.items() if v}

def _split_findings(text):
    """Split a prose blob (e.g. Key additions) into discrete findings."""
    parts = re.split(r'[；;]\s*|。\s*(?=\S)', text)
    out = []
    for p in parts:
        p = p.strip(' 　。;；,，')
        if len(p) >= 4:
            out.append(p)
    return out

def parse_log():
    """Parse log.md into structured 坡道 / 發現 / 甜點 narrative entries.

    Supports an optional explicit narrative written at ingest time:
        - 坡道: one-line relevance hook
        - 發現: a key finding
        - 甜點: closing takeaway / what to watch
    If those markers are absent, the narrative is derived from the standard
    ingest fields (Key additions → 發現, 備註 → 甜點, scope counts → 坡道).
    """
    content = (WIKI_DIR / "log.md").read_text(encoding='utf-8')
    blocks = re.split(r'(?m)^## \[', content)
    entries = []
    for blk in blocks:
        m = re.match(r'(\d{4}-\d{2}-\d{2})\] (\w+) \| (.+)', blk)
        if not m:
            continue
        date, typ, title = m.group(1), m.group(2), m.group(3).strip()
        body = blk[m.end():]

        ramp = None
        discoveries, dessert, generic = [], [], []
        concepts, entities, countries, new_pages, sources = [], [], [], [], []
        key_text, note_text = '', ''

        for line in body.split('\n'):
            s = line.strip()
            if not s.startswith('- '):
                continue
            item = s[2:].strip()

            # explicit narrative markers (future ingest style)
            mm = re.match(r'(坡道|發現|甜點)\s*[:：]\s*(.*)', item)
            if mm:
                tag, val = mm.group(1), mm.group(2).strip()
                if   tag == '坡道': ramp = val
                elif tag == '發現': discoveries.append(val)
                else:               dessert.append(val)
                continue

            fm = re.match(r'([^:：]+)[:：]\s*(.*)', item)
            if not fm:
                if len(item) > 6:
                    generic.append(item)
                continue
            label, val = fm.group(1).strip(), fm.group(2).strip()
            low = label.lower()

            if low.startswith('summary page'):
                sources += re.findall(r'\[\[sources/([^\]]+)\]\]', val)
            elif low.startswith('raw asset'):
                pass
            elif label.startswith('Pages updated') and 'concept' in low:
                concepts += [x.strip() for x in re.split(r'[、,，]', val)
                             if x.strip() and x.strip() != '無']
            elif label.startswith('Pages updated') and 'entit' in low:
                entities += [x.strip() for x in re.split(r'[、,，]', val)
                             if x.strip() and x.strip() != '無']
            elif label.startswith('Countries'):
                countries += re.findall(r'\[\[countries/([^\]]+)\]\]', val)
            elif label.startswith('New pages'):
                if val and val != '無':
                    found = re.findall(r'\[\[([^\]]+)\]\]', val)
                    new_pages += found if found else [val]
            elif low.startswith('key addition') or low.startswith('key change'):
                key_text = val
            elif label.startswith('備註') or low.startswith('note'):
                note_text = val
            else:
                if len(val) > 6:
                    generic.append(item)

        # fallbacks
        if not discoveries and key_text:
            discoveries = _split_findings(key_text)
        if not discoveries and generic:
            discoveries = [re.sub(r'\*\*([^*]+)\*\*', r'\1', g)[:180] for g in generic][:12]
        if not dessert and note_text:
            dessert = _split_findings(note_text)

        if not ramp:
            pieces = []
            if sources:   pieces.append(f"{len(sources)} 個來源")
            if concepts:  pieces.append(f"{len(concepts)} 概念")
            if countries: pieces.append(f"{len(countries)} 國家")
            if entities:  pieces.append(f"{len(entities)} 車廠")
            np = re.search(r'（\s*(\d+)\s*篇', title)
            if pieces or np:
                lead = f"本批匯入 {np.group(1)} 篇新聞" if np else "本批更新"
                ramp = lead + ("，更新 " + "、".join(pieces) if pieces else "") + "。"
            else:
                ramp = title

        entries.append({
            'date': date, 'type': typ, 'title': title,
            'ramp': ramp,
            'discoveries': discoveries[:12],
            'dessert': dessert[:8],
            'concepts': concepts, 'entities': entities,
            'countries': countries, 'new_pages': new_pages,
            'sources': sources,
        })

    entries.sort(key=lambda x: x['date'], reverse=True)
    return entries[:20]

def parse_concepts():
    out = []
    for f in sorted((WIKI_DIR / "concepts").glob("*.md")):
        text = f.read_text(encoding='utf-8')
        fm, rest = parse_frontmatter(text)
        title_m = re.search(r'^# (.+)$', rest, re.MULTILINE)
        title = title_m.group(1) if title_m else f.stem
        h2s = re.findall(r'^## (.+)', rest, re.MULTILINE)
        out.append({
            'file': f.stem, 'title': title,
            'summary': first_paragraph(rest),
            'updated': fm.get('updated', ''),
            'source_count': len(fm.get('sources', [])),
            'sections': len(h2s),
            'section_titles': h2s[:6],
            'body': rest.strip(),          # full markdown for the detail subpage
        })
    out.sort(key=lambda x: -x['source_count'])
    return out

def parse_entities():
    out = []
    for f in sorted((WIKI_DIR / "entities").glob("*.md")):
        text = f.read_text(encoding='utf-8')
        fm, rest = parse_frontmatter(text)
        title_m = re.search(r'^# (.+)$', rest, re.MULTILINE)
        title = title_m.group(1) if title_m else f.stem
        out.append({
            'file': f.stem, 'title': title,
            'summary': first_paragraph(rest, 160),
            'updated': fm.get('updated', ''),
            'source_count': len(fm.get('sources', [])),
            'body': rest.strip(),          # full markdown for the detail subpage
        })
    out.sort(key=lambda x: -x['source_count'])
    return out

def parse_countries():
    out = []
    cdir = WIKI_DIR / "countries"
    if not cdir.exists():
        return out
    for f in sorted(cdir.glob("*.md")):
        text = f.read_text(encoding='utf-8')
        fm, rest = parse_frontmatter(text)
        title_m = re.search(r'^# (.+)$', rest, re.MULTILINE)
        title = title_m.group(1) if title_m else f.stem
        h2s = re.findall(r'^## (.+)', rest, re.MULTILINE)
        out.append({
            'file': f.stem, 'title': title,
            'summary': first_paragraph(rest),
            'updated': fm.get('updated', ''),
            'source_count': len(fm.get('sources', [])),
            'sections': len(h2s),
            'section_titles': h2s[:6],
            'body': rest.strip(),          # full markdown for the detail subpage
        })
    out.sort(key=lambda x: -x['source_count'])
    return out

def parse_source_url(body):
    """Extract the original-article URL from a source page body."""
    m = re.search(r'\*\*來源\*\*[：:]\s*\[[^\]]+\]\((https?://[^)]+)\)', body)
    if m:
        return m.group(1)
    m = re.search(r'\*\*來源\*\*[：:]\s*(https?://\S+)', body)
    if m:
        return m.group(1).rstrip('）)　,。')
    m = re.search(r'(https?://\S+)', body)
    return m.group(1).rstrip('）)　,。') if m else ''

def parse_sources_full():
    """name -> {title, url, body, updated} for every source page on disk."""
    out = {}
    for f in sorted((WIKI_DIR / "sources").glob("*.md")):
        text = f.read_text(encoding='utf-8')
        fm, rest = parse_frontmatter(text)
        title_m = re.search(r'^# (.+)$', rest, re.MULTILINE)
        out[f.stem] = {
            'title': title_m.group(1) if title_m else f.stem,
            'url': parse_source_url(rest),
            'updated': fm.get('updated', ''),
            'body': rest.strip(),
        }
    return out

def build_charts(sections):
    # dataviz validated dark categorical palette (fixed order, never cycled)
    cat_labels, cat_data, cat_colors_map = [], [], {
        '電動乘用車': '#3987e5', '電動商用車與電動巴士': '#d95926',
        '市場與政策': '#199e70', '電池技術': '#c98500',
        '充電基礎建設': '#d55181', '半導體供應鏈': '#0ca30c',
    }
    cat_colors = []
    fallback = ['#9085e9','#e66767']
    fi = 0
    for sec, srcs in sections.items():
        if srcs:
            cat_labels.append(sec)
            cat_data.append(len(srcs))
            cat_colors.append(cat_colors_map.get(sec, fallback[fi % len(fallback)]))
            if sec not in cat_colors_map: fi += 1

    monthly = {}
    for srcs in sections.values():
        for src in srcs:
            d = src.get('date', '')
            if d and len(d) >= 7:
                month = d[:7]
                monthly[month] = monthly.get(month, 0) + 1
    months = sorted(monthly.keys())

    return {
        'categories': {'labels': cat_labels, 'data': cat_data, 'colors': cat_colors},
        'monthly': {'labels': months, 'data': [monthly[m] for m in months]}
    }

# ─────────────────────────── HTML Template ──────────────────────────────────

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>電動車產業知識庫 Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>
<style>
  ::-webkit-scrollbar{width:5px;height:5px}
  ::-webkit-scrollbar-track{background:#1e293b}
  ::-webkit-scrollbar-thumb{background:#475569;border-radius:3px}
  html{scroll-behavior:smooth}
  .card{transition:transform .15s ease,box-shadow .15s ease}
  .card:hover{transform:translateY(-3px);box-shadow:0 10px 30px rgba(0,0,0,.4)}
  .nav-active{background:#10b981!important;color:#0f172a!important;font-weight:600}
  .tag{display:inline-block;font-size:.65rem;padding:1px 6px;border-radius:999px;border:1px solid}
  .fade-in{animation:fadeIn .3s ease}
  @keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
  .source-row:hover{background:#1e293b}
  .type-ingest{color:#10b981}
  .type-query{color:#3b82f6}
  .type-maintenance{color:#f59e0b}
  .type-synthesis{color:#a855f7}
  .type-init{color:#94a3b8}
  #search-box:focus{outline:none;border-color:#10b981;box-shadow:0 0 0 2px rgba(16,185,129,.2)}
  .tab-btn.active{background:#10b981;color:#0f172a;border-color:#10b981}
  .concept-tag-filter.active{background:#3b82f6;color:#fff;border-color:#3b82f6}
  .tooltip{position:relative}
  .tooltip:hover .tip{display:block}
  .tip{display:none;position:absolute;bottom:125%;left:50%;transform:translateX(-50%);
       background:#0f172a;border:1px solid #334155;color:#e2e8f0;font-size:.7rem;
       padding:4px 8px;border-radius:6px;white-space:nowrap;z-index:50}
  .clickable{cursor:pointer}

  /* ── Detail subpage (slide-over) ── */
  #detail-overlay{position:fixed;inset:0;z-index:100;display:none}
  #detail-overlay.open{display:block}
  #detail-backdrop{position:absolute;inset:0;background:rgba(2,6,23,.7);backdrop-filter:blur(2px);animation:fadeIn .2s ease}
  #detail-panel{position:absolute;top:0;right:0;height:100%;width:min(760px,94vw);
    background:#0f172a;border-left:1px solid #1e293b;box-shadow:-20px 0 60px rgba(0,0,0,.5);
    display:flex;flex-direction:column;transform:translateX(100%);transition:transform .25s ease}
  #detail-overlay.open #detail-panel{transform:translateX(0)}
  #detail-head{flex-shrink:0;border-bottom:1px solid #1e293b;padding:16px 22px;
    background:#0f172a;display:flex;align-items:flex-start;gap:12px}
  #detail-body{overflow-y:auto;padding:22px 26px 60px}

  /* rendered-markdown prose */
  .md-body{color:#cbd5e1;font-size:.9rem;line-height:1.75}
  .md-body h1{font-size:1.4rem;font-weight:700;color:#f1f5f9;margin:.2em 0 .6em}
  .md-body h2{font-size:1.1rem;font-weight:600;color:#34d399;margin:1.5em 0 .5em;
    padding-bottom:.25em;border-bottom:1px solid #1e293b}
  .md-body h3{font-size:.98rem;font-weight:600;color:#93c5fd;margin:1.1em 0 .4em}
  .md-body p{margin:.6em 0}
  .md-body ul,.md-body ol{margin:.5em 0 .5em 1.3em;list-style:revert}
  .md-body li{margin:.25em 0}
  .md-body strong{color:#f1f5f9;font-weight:600}
  .md-body code{background:#1e293b;color:#fbbf24;padding:1px 5px;border-radius:4px;font-size:.85em}
  .md-body a{color:#38bdf8;text-decoration:none;border-bottom:1px dotted #38bdf8}
  .md-body a:hover{color:#7dd3fc}
  .md-body a.wl{color:#a78bfa;border-bottom:1px dashed #a78bfa;cursor:pointer}
  .md-body a.wl:hover{color:#c4b5fd;background:rgba(167,139,250,.1)}
  .md-body table{border-collapse:collapse;width:100%;margin:1em 0;font-size:.82rem;display:block;overflow-x:auto}
  .md-body th,.md-body td{border:1px solid #1e293b;padding:6px 10px;text-align:left}
  .md-body th{background:#1e293b;color:#e2e8f0;font-weight:600}
  .md-body tr:nth-child(even){background:rgba(30,41,59,.4)}
  .md-body blockquote{border-left:3px solid #475569;padding-left:1em;color:#94a3b8;margin:.8em 0}
  .md-body hr{border:0;border-top:1px solid #1e293b;margin:1.4em 0}

  /* ── 坡道 / 發現 / 甜點 narrative ── */
  .narr-zone{border-radius:14px;padding:16px 18px;margin-bottom:14px;border:1px solid}
  .narr-ramp{background:rgba(57,135,229,.08);border-color:rgba(57,135,229,.35)}
  .narr-disc{background:rgba(25,158,112,.07);border-color:rgba(25,158,112,.30)}
  .narr-upd {background:rgba(144,133,233,.07);border-color:rgba(144,133,233,.30)}
  .narr-dess{background:rgba(201,133,0,.08);border-color:rgba(201,133,0,.35)}
  .narr-label{font-size:.72rem;font-weight:700;letter-spacing:.04em;margin-bottom:8px;display:flex;align-items:center;gap:6px}
  .narr-ramp .narr-label{color:#7fb3f2}
  .narr-disc .narr-label{color:#4fcfa0}
  .narr-upd  .narr-label{color:#b4a9f0}
  .narr-dess .narr-label{color:#e0b24d}
  .narr-ramp-text{color:#dbeafe;font-size:.98rem;line-height:1.7;font-weight:500}
  .narr-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:9px}
  .narr-list li{color:#cbd5e1;font-size:.88rem;line-height:1.65;padding-left:20px;position:relative}
  .narr-disc .narr-list li::before{content:"▸";position:absolute;left:2px;color:#4fcfa0}
  .narr-dess .narr-list li::before{content:"◆";position:absolute;left:2px;color:#e0b24d;font-size:.7rem;top:3px}
  .narr-list li strong{color:#f1f5f9}
  .nav-chip{display:inline-flex;align-items:center;font-size:.76rem;border-radius:999px;
    padding:3px 11px;margin:0 6px 6px 0;border:1px solid;cursor:pointer;transition:all .12s}
  .chip-concept{background:rgba(57,135,229,.12);border-color:rgba(57,135,229,.4);color:#8fc0f5}
  .chip-concept:hover{background:rgba(57,135,229,.25)}
  .chip-country{background:rgba(25,158,112,.12);border-color:rgba(25,158,112,.4);color:#5fd3a8}
  .chip-country:hover{background:rgba(25,158,112,.25)}
  .chip-entity{background:rgba(201,133,0,.14);border-color:rgba(201,133,0,.4);color:#e7bf63}
  .chip-entity:hover{background:rgba(201,133,0,.26)}
  .chip-source{background:rgba(144,133,233,.12);border-color:rgba(144,133,233,.4);color:#b4a9f0}
  .chip-source:hover{background:rgba(144,133,233,.25)}
  .nav-chip-static{display:inline-flex;align-items:center;font-size:.76rem;border-radius:999px;
    padding:3px 11px;margin:0 6px 6px 0;border:1px solid #334155;color:#94a3b8}
</style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen font-sans">

<script>const D = __WIKI_DATA__;</script>

<div class="flex h-screen overflow-hidden">

  <!-- ── Sidebar ── -->
  <aside class="w-44 bg-slate-800 border-r border-slate-700 flex-shrink-0 flex flex-col overflow-y-auto">
    <div class="p-4 border-b border-slate-700">
      <div class="text-emerald-400 font-bold text-base leading-tight">🚗 EV 知識庫</div>
      <div class="text-slate-400 text-xs mt-0.5">產業動態 Dashboard</div>
    </div>
    <nav class="flex-1 p-2 space-y-0.5" id="sidenav">
      <a href="#activity"  class="nav-link block px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-700 cursor-pointer">📰 最新動態</a>
      <a href="#concepts"  class="nav-link block px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-700 cursor-pointer">🗺️ 概念地圖</a>
      <a href="#countries" class="nav-link block px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-700 cursor-pointer">🌍 國家動態</a>
      <a href="#entities"  class="nav-link block px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-700 cursor-pointer">🏭 車廠資料庫</a>
      <a href="#sources"   class="nav-link block px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-700 cursor-pointer">📚 來源追蹤</a>
    </nav>
    <div class="p-3 border-t border-slate-700 text-xs text-slate-500 leading-relaxed">
      <div>最後更新</div>
      <div class="text-slate-300" id="sidebar-date"></div>
      <div class="mt-1">生成時間</div>
      <div class="text-slate-400" id="sidebar-gen"></div>
    </div>
  </aside>

  <!-- ── Main ── -->
  <main class="flex-1 overflow-y-auto" id="main-scroll">

    <!-- Top Bar -->
    <div class="sticky top-0 z-20 bg-slate-900/95 backdrop-blur-sm border-b border-slate-700/60 px-6 py-2.5 flex items-center justify-between gap-4">
      <div class="text-slate-400 text-sm" id="top-stats"></div>
      <div class="relative">
        <input id="search-box" type="text" placeholder="🔍  搜尋概念、企業、來源…"
          class="bg-slate-800 border border-slate-600 rounded-lg px-4 py-1.5 text-sm text-slate-200 w-80 placeholder-slate-500 transition">
        <div id="search-results"
          class="hidden absolute right-0 top-full mt-1 bg-slate-800 border border-slate-600 rounded-xl shadow-2xl w-96 max-h-96 overflow-y-auto z-50 fade-in">
        </div>
      </div>
    </div>

    <div class="px-6 py-6 space-y-14 max-w-screen-xl">

      <!-- ── Recent Activity ── -->
      <section id="activity">
        <h2 class="section-title text-lg font-semibold text-slate-200 mb-5 flex items-center gap-2">
          <span class="text-emerald-400">◈</span> 最新動態
          <span class="ml-2 text-xs text-slate-500 font-normal">（坡道 → 發現 → 甜點；點擊每則看完整敘事與原文）</span>
        </h2>
        <div id="activity-list" class="relative border-l-2 border-slate-700 ml-3 pl-6 space-y-5"></div>
      </section>

      <!-- ── Concepts ── -->
      <section id="concepts">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-5">
          <h2 class="section-title text-lg font-semibold text-slate-200 flex items-center gap-2">
            <span class="text-emerald-400">◈</span> 概念地圖
            <span class="ml-2 text-xs text-slate-500 font-normal">（點擊卡片看完整內容）</span>
          </h2>
          <div class="flex gap-2 flex-wrap" id="concept-filters"></div>
        </div>
        <div id="concepts-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"></div>
      </section>

      <!-- ── Countries ── -->
      <section id="countries">
        <h2 class="section-title text-lg font-semibold text-slate-200 mb-5 flex items-center gap-2">
          <span class="text-emerald-400">◈</span> 國家動態
          <span class="ml-2 text-xs text-slate-500 font-normal">（點擊卡片看完整內容）</span>
        </h2>
        <div id="countries-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"></div>
      </section>

      <!-- ── Entities ── -->
      <section id="entities">
        <h2 class="section-title text-lg font-semibold text-slate-200 mb-5 flex items-center gap-2">
          <span class="text-emerald-400">◈</span> 車廠資料庫
          <span class="ml-2 text-xs text-slate-500 font-normal">（點擊卡片看完整資料）</span>
        </h2>
        <div id="entities-grid" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3"></div>
      </section>

      <!-- ── Sources ── -->
      <section id="sources" class="pb-16">
        <h2 class="section-title text-lg font-semibold text-slate-200 mb-5 flex items-center gap-2">
          <span class="text-emerald-400">◈</span> 來源追蹤
        </h2>
        <div class="flex gap-2 flex-wrap mb-4" id="source-tabs"></div>
        <div id="source-panel"></div>
      </section>

    </div>
  </main>
</div>

<!-- ── Detail subpage (slide-over) ── -->
<div id="detail-overlay" aria-hidden="true">
  <div id="detail-backdrop"></div>
  <div id="detail-panel" role="dialog" aria-modal="true">
    <div id="detail-head">
      <button id="detail-back" class="hidden flex-shrink-0 text-slate-400 hover:text-emerald-400 text-lg leading-none mt-0.5" title="返回">←</button>
      <div class="flex-1 min-w-0">
        <div id="detail-kicker" class="text-xs font-medium mb-0.5"></div>
        <div id="detail-title" class="text-base font-semibold text-slate-100 leading-snug break-words"></div>
        <div id="detail-meta" class="mt-1"></div>
      </div>
      <button id="detail-close" class="flex-shrink-0 text-slate-400 hover:text-rose-400 text-2xl leading-none" title="關閉 (Esc)">×</button>
    </div>
    <div id="detail-body"></div>
  </div>
</div>

<!-- ── JavaScript ── -->
<script>
(function(){
// ── Config ──────────────────────────────────────────────────────────────────
const SECTION_COLORS = {          // dataviz validated dark categorical palette
  '電動乘用車':       '#3987e5',
  '電動商用車與電動巴士': '#d95926',
  '市場與政策':       '#199e70',
  '電池技術':         '#c98500',
  '充電基礎建設':     '#d55181',
  '半導體供應鏈':     '#0ca30c',
};
const CONCEPT_CATEGORIES = [
  {label:'全部', key:'all'},
  {label:'🌍 市場/政策', key:'market',  match: /市場|政策|關稅|出海/},
  {label:'🔋 電池/技術', key:'battery', match: /電池|鈉離子/},
  {label:'🚌 商用車',   key:'cv',      match: /巴士|卡車|商用/},
  {label:'🤖 自動駕駛', key:'av',      match: /ADAS|Robotaxi|自動/},
  {label:'⚡ 基礎設施', key:'infra',   match: /充電|儲能/},
  {label:'💾 半導體',  key:'semi',    match: /半導體/},
];
const TYPE_ICONS = {ingest:'📥', query:'🔍', maintenance:'🔧', synthesis:'🔗', init:'🌱'};
const TYPE_LABELS = {ingest:'Ingest', query:'Query', maintenance:'維護', synthesis:'綜合分析', init:'初始化'};

// ── Helpers ─────────────────────────────────────────────────────────────────
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const $  = id => document.getElementById(id);
const mk = (tag, cls, html='') => { const e=document.createElement(tag); e.className=cls; e.innerHTML=html; return e; };

// ── Detail subpage engine ────────────────────────────────────────────────────
// Lookup maps keyed by file/name so wikilinks can resolve to a detail view.
const CMAP = {}, EMAP = {}, NMAP = {}, SMAP = D.source_pages || {};
D.concepts.forEach(c => CMAP[c.file] = c);
D.entities.forEach(e => EMAP[e.file] = e);
(D.countries || []).forEach(n => NMAP[n.file] = n);
const TITLE_TO_ENTITY = {}; D.entities.forEach(e => TITLE_TO_ENTITY[e.title] = e.file);
const TITLE_TO_CONCEPT = {}; D.concepts.forEach(c => TITLE_TO_CONCEPT[c.file] = c.file);

if (window.marked) marked.setOptions({ gfm:true, breaks:false });

// Convert [[wikilinks]] into clickable cross-links before markdown rendering.
function resolveWikilinks(md){
  return md.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (m, target, label) => {
    target = target.trim();
    const seg = target.split('/');
    const key = seg[seg.length - 1].trim();
    let type = '';
    if (/^sources\//i.test(target) && SMAP[key]) type = 'source';
    else if (/^entit(y|ies)\//i.test(target)) type = 'entity';
    else if (/^countr(y|ies)\//i.test(target)) type = 'country';
    else if (/^concepts?\//i.test(target)) type = 'concept';
    else if (SMAP[key]) type = 'source';
    else if (EMAP[key] || TITLE_TO_ENTITY[key]) type = 'entity';
    else if (NMAP[key]) type = 'country';
    else if (CMAP[key]) type = 'concept';
    const text = (label || key).trim();
    if (!type) return esc(text);
    const ekey = (type === 'entity' && !EMAP[key] && TITLE_TO_ENTITY[key]) ? TITLE_TO_ENTITY[key] : key;
    return `<a class="wl" data-t="${esc(type)}" data-k="${esc(ekey)}">${esc(text)}</a>`;
  });
}

function renderMarkdown(md){
  const html = (window.marked ? marked.parse(resolveWikilinks(md)) : esc(md));
  // open every external link in a new tab
  return html.replace(/<a\s+href="(https?:)/g, '<a target="_blank" rel="noopener" href="$1');
}

const detailHist = [];
function openDetail(type, key, push=true){
  let item, kicker, kColor, meta = '';
  if (type === 'concept'){
    item = CMAP[key]; if (!item) return;
    kicker = '🗺️ 概念地圖'; kColor = 'text-blue-400';
    meta = `<span class="text-xs text-slate-500">${esc(item.source_count)} 個來源 · 更新 ${esc(item.updated||'—')}</span>`;
  } else if (type === 'country'){
    item = NMAP[key]; if (!item) return;
    kicker = '🌍 國家動態'; kColor = 'text-teal-400';
    meta = `<span class="text-xs text-slate-500">${esc(item.source_count)} 個來源 · 更新 ${esc(item.updated||'—')}</span>`;
  } else if (type === 'entity'){
    item = EMAP[key]; if (!item) return;
    kicker = '🏭 車廠資料庫'; kColor = 'text-amber-400';
    meta = `<span class="text-xs text-slate-500">${esc(item.source_count)} 個來源 · 更新 ${esc(item.updated||'—')}</span>`;
  } else if (type === 'source'){
    item = SMAP[key]; if (!item) return;
    kicker = '📄 來源'; kColor = 'text-emerald-400';
    if (item.url) meta = `<a href="${esc(item.url)}" target="_blank" rel="noopener"
        class="inline-flex items-center gap-1 text-xs bg-emerald-500/15 text-emerald-300 border border-emerald-500/40 rounded-full px-3 py-1 hover:bg-emerald-500/25 transition">↗ 查看原文</a>`;
  } else return;

  if (push) detailHist.push({type, key});
  $('detail-kicker').className = 'text-xs font-medium mb-0.5 ' + kColor;
  $('detail-kicker').textContent = kicker;
  $('detail-title').textContent = item.title || key;
  $('detail-meta').innerHTML = meta;
  $('detail-body').innerHTML = `<div class="md-body">${renderMarkdown(item.body || '_（無內容）_')}</div>`;
  $('detail-back').classList.toggle('hidden', detailHist.length < 2);
  const ov = $('detail-overlay');
  ov.classList.add('open'); ov.setAttribute('aria-hidden','false');
  $('detail-body').scrollTop = 0;
  document.body.style.overflow = 'hidden';
}

// chip that opens a detail subpage when the target page exists
function navChip(label, type, key, map, cls){
  if (map && map[key])
    return `<button class="nav-chip ${cls}" data-t="${type}" data-k="${esc(key)}">${esc(label)}</button>`;
  return `<span class="nav-chip-static">${esc(label)}</span>`;
}
function openActivity(i, push=true){
  const e = D.log[i]; if (!e) return;
  const TYPE_LABELS = {ingest:'Ingest', query:'Query', maintenance:'維護', synthesis:'綜合分析', init:'初始化'};
  if (push){ detailHist.length = 0; detailHist.push({type:'activity', key:i}); }
  $('detail-kicker').className = 'text-xs font-medium mb-0.5 type-' + e.type;
  $('detail-kicker').textContent = '📰 ' + (TYPE_LABELS[e.type] || e.type) + ' · 最新動態';
  $('detail-title').textContent = e.title;
  $('detail-meta').innerHTML = `<span class="text-xs font-mono text-slate-500">${esc(e.date)}</span>`;

  let html = '';
  // 🛝 坡道
  html += `<div class="narr-zone narr-ramp">
      <div class="narr-label">🛝 坡道 · 為何值得看</div>
      <div class="narr-ramp-text">${inlineMd(e.ramp || e.title)}</div>
    </div>`;
  // 🔍 發現
  if ((e.discoveries||[]).length){
    html += `<div class="narr-zone narr-disc">
        <div class="narr-label">🔍 發現 · 核心重點</div>
        <ul class="narr-list">${e.discoveries.map(d => `<li>${inlineMd(d)}</li>`).join('')}</ul>
      </div>`;
  }
  // 📄 本批更新（可點 chips）
  const chips = []
    .concat((e.concepts ||[]).map(n => navChip(n, 'concept', n, CMAP,
              CMAP[n] ? 'chip-concept' : '')))
    .concat((e.countries||[]).map(n => navChip(n, 'country', n, NMAP, 'chip-country')))
    .concat((e.entities ||[]).map(n => {
       const k = EMAP[n] ? n : (TITLE_TO_ENTITY[n] || '');
       return navChip(n, 'entity', k, EMAP, 'chip-entity');
     }))
    .concat((e.sources ||[]).map(n => navChip(n, 'source', n, SMAP, 'chip-source')));
  if (chips.length){
    html += `<div class="narr-zone narr-upd">
        <div class="narr-label">📄 本批更新 · 點擊跳頁</div>
        <div>${chips.join('')}</div>
      </div>`;
  }
  // 🍰 甜點
  if ((e.dessert||[]).length){
    html += `<div class="narr-zone narr-dess">
        <div class="narr-label">🍰 甜點 · 下一步追蹤 / 待核對</div>
        <ul class="narr-list">${e.dessert.map(d => `<li>${inlineMd(d)}</li>`).join('')}</ul>
      </div>`;
  }

  $('detail-body').innerHTML = html;
  $('detail-back').classList.toggle('hidden', detailHist.length < 2);
  const ov = $('detail-overlay');
  ov.classList.add('open'); ov.setAttribute('aria-hidden','false');
  $('detail-body').scrollTop = 0;
  document.body.style.overflow = 'hidden';
}

function closeDetail(){
  const ov = $('detail-overlay');
  ov.classList.remove('open'); ov.setAttribute('aria-hidden','true');
  detailHist.length = 0;
  document.body.style.overflow = '';
}

function setupDetail(){
  $('detail-close').addEventListener('click', closeDetail);
  $('detail-backdrop').addEventListener('click', closeDetail);
  $('detail-back').addEventListener('click', () => {
    detailHist.pop();                       // current
    const prev = detailHist[detailHist.length - 1];
    if (!prev) return;
    if (prev.type === 'activity') openActivity(prev.key, false);
    else openDetail(prev.type, prev.key, false);
  });
  // wikilink + chip navigation inside the detail body
  $('detail-body').addEventListener('click', ev => {
    const a = ev.target.closest('[data-t][data-k]');
    if (!a) return;
    ev.preventDefault();
    openDetail(a.dataset.t, a.dataset.k);
  });
  document.addEventListener('keydown', ev => {
    if (ev.key === 'Escape' && $('detail-overlay').classList.contains('open')) closeDetail();
  });
}

// ── Render: Stats ────────────────────────────────────────────────────────────
function renderStats(){
  const s = D.stats;
  $('sidebar-date').textContent = s.last_updated;
  $('sidebar-gen').textContent  = D.generated_at;
  $('top-stats').innerHTML =
    `<span class="text-emerald-400 font-semibold">${s.sources}</span> 來源 ·
     <span class="text-blue-400 font-semibold">${s.concepts}</span> 概念 ·
     <span class="text-teal-400 font-semibold">${s.countries||0}</span> 國家 ·
     <span class="text-amber-400 font-semibold">${s.entities}</span> 車廠 ·
     最後更新 <span class="text-slate-300">${s.last_updated}</span>`;
}

// ── Render: Activity Timeline (坡道 / 發現 / 甜點) ─────────────────────────────
// inline markdown: **bold** only, escaped
function inlineMd(s){
  return esc(s).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
}
const ACTIVITY_DAYS = 3;   // 最新動態：最新 ingest 日往前 N 個日曆日內的全部 ingest（同日多批都列出）
const ACTIVITY_MIN  = 3;   // 若不足 N 則（如週末無 ingest），以更早的 ingest 補足

function renderActivity(){
  const el = $('activity-list');
  // 以原始索引配對，過濾出 ingest（若無則退回全部），取最近 N 個日期
  let rows = D.log.map((e, i) => ({e, i}));
  const ingests = rows.filter(r => r.e.type === 'ingest');
  rows = ingests.length ? ingests : rows;
  if (rows.length) {
    const newest = new Date(rows[0].e.date);
    const cutoff = new Date(newest.getTime() - (ACTIVITY_DAYS - 1) * 86400000).toISOString().slice(0, 10);
    const inWindow = rows.filter(r => r.e.date >= cutoff);
    rows = inWindow.length >= ACTIVITY_MIN ? inWindow : rows.slice(0, ACTIVITY_MIN);
  }

  el.innerHTML = rows.map(({e, i}) => {
    const icon  = TYPE_ICONS[e.type] || '📌';
    const cls   = `type-${e.type}`;
    const label = TYPE_LABELS[e.type] || e.type;

    // 🔍 發現：卡片最多 6 項，其餘進詳情頁
    const DISC_CAP = 6;
    const disc = (e.discoveries || []).slice(0, DISC_CAP).map(d =>
      `<li>${inlineMd(d)}</li>`).join('');
    const nMore = (e.discoveries || []).length - DISC_CAP;
    // 🍰 甜點
    const dess = (e.dessert || []).map(d => `<li>${inlineMd(d)}</li>`).join('');
    // 本批更新計數
    const counts = [];
    if ((e.concepts||[]).length)  counts.push(`${e.concepts.length} 概念`);
    if ((e.countries||[]).length) counts.push(`${e.countries.length} 國家`);
    if ((e.entities||[]).length)  counts.push(`${e.entities.length} 車廠`);
    if ((e.sources||[]).length)   counts.push(`${e.sources.length} 來源`);

    return `
      <div class="relative fade-in">
        <div class="absolute -left-9 top-1 w-4 h-4 rounded-full bg-slate-700 border-2 border-slate-600 flex items-center justify-center text-xs">
          <span class="${cls}">${icon}</span>
        </div>
        <div class="bg-slate-800/60 rounded-xl border border-slate-700/60 p-4 clickable hover:border-emerald-500/50 transition" data-log="${i}">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-xs font-mono text-slate-500">${e.date}</span>
            <span class="tag ${cls} border-current opacity-70">${label}</span>
            <span class="ml-auto text-[11px] text-emerald-400/70">看完整敘事 →</span>
          </div>

          <div class="narr-zone narr-ramp">
            <div class="narr-label">🛝 坡道 · 為何值得看</div>
            <div class="narr-ramp-text">${inlineMd(e.ramp || e.title)}</div>
          </div>

          ${disc ? `<div class="narr-zone narr-disc">
            <div class="narr-label">🔍 發現 · 核心重點</div>
            <ul class="narr-list">${disc}</ul>
            ${nMore > 0 ? `<div class="text-[11px] text-slate-500 mt-1">…點開看其餘 ${nMore} 項發現</div>` : ''}
          </div>` : ''}

          ${dess ? `<div class="narr-zone narr-dess">
            <div class="narr-label">🍰 甜點 · 下一步追蹤 / 待核對</div>
            <ul class="narr-list">${dess}</ul>
          </div>` : ''}

          ${counts.length ? `<div class="text-[11px] text-slate-500 mt-2">本批更新 ${counts.join('、')} · 點擊看可跳頁連結</div>` : ''}
        </div>
      </div>`;
  }).join('');

  el.onclick = ev => {
    const card = ev.target.closest('[data-log]');
    if (card) openActivity(+card.dataset.log);
  };
}

// ── Render: Concepts Grid ────────────────────────────────────────────────────
let conceptFilter = 'all';

function renderConceptFilters(){
  $('concept-filters').innerHTML = CONCEPT_CATEGORIES.map(c => `
    <button class="concept-tag-filter ${c.key==='all'?'active':''} px-3 py-1 rounded-full text-xs border border-slate-600 text-slate-300 hover:border-blue-400 transition cursor-pointer"
            data-key="${c.key}">${c.label}</button>`).join('');
  $('concept-filters').addEventListener('click', e => {
    const btn = e.target.closest('.concept-tag-filter');
    if (!btn) return;
    document.querySelectorAll('.concept-tag-filter').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    conceptFilter = btn.dataset.key;
    renderConcepts();
  });
}

function renderConcepts(){
  let list = D.concepts;
  if (conceptFilter !== 'all') {
    const cat = CONCEPT_CATEGORIES.find(c => c.key === conceptFilter);
    if (cat) list = list.filter(c => cat.match.test(c.title + c.file));
  }
  $('concepts-grid').innerHTML = list.map(c => {
    const bar = Math.min(100, Math.round(c.source_count / 30 * 100));
    const sections = c.section_titles.slice(0,4).map(s =>
      `<span class="inline-block bg-slate-700/60 text-slate-300 text-xs rounded px-1.5 py-0.5 mr-1 mb-1">${esc(s.replace(/：.*/,'').substring(0,18))}</span>`).join('');
    return `
      <div class="card clickable bg-slate-800 border border-slate-700 rounded-2xl p-5 flex flex-col gap-3 fade-in"
           data-concept="${esc(c.file)}">
        <div class="flex items-start justify-between gap-2">
          <h3 class="text-base font-semibold text-slate-100 leading-tight">${esc(c.title)}</h3>
          <span class="flex-shrink-0 text-xs text-emerald-400 font-mono">${c.source_count} 來源</span>
        </div>
        <p class="text-xs text-slate-400 leading-relaxed flex-1">${esc(c.summary)}</p>
        ${sections ? `<div class="flex flex-wrap">${sections}</div>` : ''}
        <div class="flex items-center gap-2 mt-auto">
          <div class="flex-1 bg-slate-700 rounded-full h-1">
            <div class="bg-emerald-500 h-1 rounded-full transition-all" style="width:${bar}%"></div>
          </div>
          <span class="text-xs text-slate-500">${c.updated}</span>
        </div>
        <div class="text-[11px] text-blue-400/70 mt-1">點擊看完整內容 →</div>
      </div>`;
  }).join('');
  $('concepts-grid').onclick = ev => {
    const card = ev.target.closest('[data-concept]');
    if (card) openDetail('concept', card.dataset.concept);
  };
}

// ── Render: Countries Grid ───────────────────────────────────────────────────
function renderCountries(){
  const list = D.countries || [];
  const grid = $('countries-grid');
  if (!grid) return;
  grid.innerHTML = list.map(c => {
    const sections = c.section_titles.slice(0,4).map(s =>
      `<span class="inline-block bg-slate-700/60 text-slate-300 text-xs rounded px-1.5 py-0.5 mr-1 mb-1">${esc(s.replace(/：.*/,'').substring(0,18))}</span>`).join('');
    return `
      <div class="card clickable bg-slate-800 border border-slate-700 rounded-2xl p-5 flex flex-col gap-3 fade-in"
           data-country="${esc(c.file)}">
        <div class="flex items-start justify-between gap-2">
          <h3 class="text-base font-semibold text-slate-100 leading-tight">🌍 ${esc(c.title)}</h3>
          <span class="flex-shrink-0 text-xs text-teal-400 font-mono">${c.source_count} 來源</span>
        </div>
        <p class="text-xs text-slate-400 leading-relaxed flex-1">${esc(c.summary)}</p>
        ${sections ? `<div class="flex flex-wrap">${sections}</div>` : ''}
        <div class="flex items-center justify-between mt-auto">
          <span class="text-xs text-slate-500">${c.updated}</span>
          <span class="text-[11px] text-teal-400/70">看完整內容 →</span>
        </div>
      </div>`;
  }).join('');
  grid.onclick = ev => {
    const card = ev.target.closest('[data-country]');
    if (card) openDetail('country', card.dataset.country);
  };
}

// ── Render: Entities ────────────────────────────────────────────────────────
function renderEntities(){
  $('entities-grid').innerHTML = D.entities.map(e => `
    <div class="card clickable bg-slate-800 border border-slate-700 rounded-xl p-4 flex flex-col gap-2 fade-in"
         data-entity="${esc(e.file)}">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-100">${esc(e.title)}</h3>
        <span class="text-xs text-amber-400 font-mono">${e.source_count}</span>
      </div>
      <p class="text-xs text-slate-400 leading-relaxed">${esc(e.summary)}</p>
      <div class="flex items-center justify-between mt-auto">
        <span class="text-xs text-slate-600">${e.updated}</span>
        <span class="text-[11px] text-amber-400/70">看完整資料 →</span>
      </div>
    </div>`).join('');
  $('entities-grid').onclick = ev => {
    const card = ev.target.closest('[data-entity]');
    if (card) openDetail('entity', card.dataset.entity);
  };
}

// ── Render: Sources (Tabbed) ─────────────────────────────────────────────────
let activeSourceTab = null;

// label colour on a filled categorical chip: white, except dark on yellow
const fillInk = hex => (hex.toLowerCase() === '#c98500' ? '#0b0b0b' : '#ffffff');
function renderSourceTabs(){
  const sections = Object.keys(D.sections);
  activeSourceTab = sections[0] || null;
  $('source-tabs').innerHTML = sections.map((sec, i) => {
    const color = SECTION_COLORS[sec] || '#9085e9';
    return `<button class="tab-btn ${i===0?'active':''} px-4 py-1.5 rounded-full text-xs border border-slate-600 text-slate-300 hover:border-emerald-500 transition cursor-pointer"
               data-sec="${esc(sec)}" style="${i===0?`background:${color};color:${fillInk(color)};border-color:${color}`:''}">
               ${esc(sec)} <span class="opacity-70">(${D.sections[sec].length})</span>
             </button>`;
  }).join('');
  $('source-tabs').addEventListener('click', e => {
    const btn = e.target.closest('.tab-btn');
    if (!btn) return;
    activeSourceTab = btn.dataset.sec;
    document.querySelectorAll('.tab-btn').forEach((b, i) => {
      const sec = b.dataset.sec;
      const c = SECTION_COLORS[sec] || '#9085e9';
      if (sec === activeSourceTab) {
        b.classList.add('active'); b.style.background = c; b.style.color = fillInk(c); b.style.borderColor = c;
      } else {
        b.classList.remove('active'); b.style.background = ''; b.style.color = ''; b.style.borderColor = '';
      }
    });
    renderSourcePanel();
  });
  renderSourcePanel();
}

function renderSourcePanel(){
  const srcs = D.sections[activeSourceTab] || [];
  $('source-panel').innerHTML = `
    <div class="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden fade-in">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-slate-700">
            <th class="text-left px-4 py-3 text-xs text-slate-400 font-medium w-28">日期</th>
            <th class="text-left px-4 py-3 text-xs text-slate-400 font-medium">摘要</th>
            <th class="text-right px-4 py-3 text-xs text-slate-400 font-medium w-24">原文</th>
          </tr>
        </thead>
        <tbody>
          ${[...srcs].reverse().map(s => {
            const sp = SMAP[s.name] || {};
            const ext = sp.url
              ? `<a href="${esc(sp.url)}" target="_blank" rel="noopener" data-stop="1"
                    class="inline-flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-300 whitespace-nowrap">↗ 原文</a>`
              : `<span class="text-xs text-slate-600">—</span>`;
            return `
            <tr class="source-row clickable border-b border-slate-700/50 transition" data-source="${esc(s.name)}">
              <td class="px-4 py-3 text-xs font-mono text-slate-500 align-top">${esc(s.date)}</td>
              <td class="px-4 py-3 text-xs text-slate-300 leading-relaxed align-top">
                <span class="font-mono text-slate-500 mr-2">${esc(s.name)}</span>
                ${esc(s.desc)}
              </td>
              <td class="px-4 py-3 text-right align-top">${ext}</td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>
    </div>`;
  $('source-panel').onclick = ev => {
    if (ev.target.closest('[data-stop]')) return;   // let the ↗ 原文 link work
    const row = ev.target.closest('[data-source]');
    if (row) openDetail('source', row.dataset.source);
  };
}

// ── Search ───────────────────────────────────────────────────────────────────
function setupSearch(){
  const box = $('search-box');
  const res = $('search-results');

  function buildIndex(){
    const idx = [];
    D.concepts.forEach(c => idx.push({type:'概念', icon:'🗺️', title:c.title, sub:c.summary, color:'text-blue-400', dt:'concept', dk:c.file}));
    (D.countries||[]).forEach(n => idx.push({type:'國家', icon:'🌍', title:n.title, sub:n.summary, color:'text-teal-400', dt:'country', dk:n.file}));
    D.entities.forEach(e => idx.push({type:'車廠', icon:'🏭', title:e.title, sub:e.summary, color:'text-amber-400', dt:'entity', dk:e.file}));
    Object.entries(D.sections).forEach(([sec, srcs]) =>
      srcs.forEach(s => idx.push({type:'來源', icon:'📄', title:s.name, sub:s.desc, color:'text-emerald-400', sec, dt:'source', dk:s.name}))
    );
    return idx;
  }

  const INDEX = buildIndex();

  box.addEventListener('input', () => {
    const q = box.value.trim().toLowerCase();
    if (!q) { res.classList.add('hidden'); return; }
    const hits = INDEX.filter(x =>
      x.title.toLowerCase().includes(q) || x.sub.toLowerCase().includes(q)
    ).slice(0, 15);
    if (!hits.length) { res.innerHTML = '<div class="p-4 text-slate-500 text-sm">無結果</div>'; }
    else {
      res.innerHTML = hits.map(h => `
        <div class="search-hit flex items-start gap-3 px-4 py-3 hover:bg-slate-700 cursor-pointer border-b border-slate-700/50 last:border-0"
             data-t="${esc(h.dt)}" data-k="${esc(h.dk)}">
          <span class="text-lg mt-0.5">${h.icon}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-xs ${h.color} font-medium">${h.type}</span>
              <span class="text-sm text-slate-200 font-medium truncate">${esc(h.title)}</span>
            </div>
            <div class="text-xs text-slate-400 mt-0.5 line-clamp-2">${esc(h.sub)}</div>
          </div>
        </div>`).join('');
    }
    res.classList.remove('hidden');
  });

  res.addEventListener('click', e => {
    const hit = e.target.closest('.search-hit');
    if (!hit) return;
    res.classList.add('hidden');
    box.value = '';
    openDetail(hit.dataset.t, hit.dataset.k);
  });

  document.addEventListener('click', e => {
    if (!box.contains(e.target) && !res.contains(e.target)) res.classList.add('hidden');
  });
}

// ── Scrollspy ────────────────────────────────────────────────────────────────
function setupScrollspy(){
  const sections = ['activity','concepts','countries','entities','sources'];
  const links = document.querySelectorAll('.nav-link');
  const scroll = $('main-scroll');
  scroll.addEventListener('scroll', () => {
    let current = sections[0];
    sections.forEach(id => {
      const el = document.getElementById(id);
      if (el && el.getBoundingClientRect().top < 120) current = id;
    });
    links.forEach(l => {
      if (l.getAttribute('href') === '#' + current) l.classList.add('nav-active');
      else l.classList.remove('nav-active');
    });
  }, {passive:true});
}

// ── Boot ─────────────────────────────────────────────────────────────────────
renderStats();
renderActivity();
renderConceptFilters();
renderConcepts();
renderCountries();
renderEntities();
renderSourceTabs();
setupSearch();
setupScrollspy();
setupDetail();

})();
</script>
</body>
</html>
'''

# ─────────────────────────── Main ───────────────────────────────────────────

def generate():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("🔍 Parsing wiki content…")
    stats, sections = parse_index()
    log_entries      = parse_log()
    concepts         = parse_concepts()
    countries        = parse_countries()
    entities         = parse_entities()
    source_pages     = parse_sources_full()

    entity_count = len(entities)

    data = {
        'stats': {**stats, 'entities': entity_count, 'concepts': len(concepts),
                  'countries': len(countries)},
        'log':          log_entries,
        'concepts':     concepts,
        'countries':    countries,
        'entities':     entities,
        'sections':     sections,
        'source_pages': source_pages,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }

    payload = json.dumps(data, ensure_ascii=False, indent=2)
    payload = payload.replace('</', '<\\/')   # keep markdown bodies from closing the <script>
    html = HTML_TEMPLATE.replace('__WIKI_DATA__', payload)

    out = OUTPUT_DIR / "index.html"
    out.write_text(html, encoding='utf-8')

    print(f"✅ Dashboard → {out}")
    print(f"   📚 {stats['sources']} 來源  |  🗺️ {len(concepts)} 概念  |  🌍 {len(countries)} 國家  |  🏭 {entity_count} 車廠  |  📄 {stats['pages']} 頁")
    print()
    print("── 本機預覽 ─────────────────────────────────────────────")
    print("   cd docs && python -m http.server 8080")
    print("   → http://localhost:8080")
    print()
    print("── 推送到 GitHub Pages ──────────────────────────────────")
    print("   git add docs/index.html && git commit -m 'chore: update dashboard'")
    print("   git push")
    print("────────────────────────────────────────────────────────")

if __name__ == '__main__':
    generate()
