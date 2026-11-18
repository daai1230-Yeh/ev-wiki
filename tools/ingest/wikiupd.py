"""ingest 時更新 wiki 頁面的共用函式。

    import sys; sys.path.insert(0, 'tools/ingest')
    from wikiupd import Batch
    b = Batch('2026-11-18', {'E': 'ev-news-2026-11-18-electrive-en', 'D': 'ev-news-2026-11-18-digitimes'})
    b.source('ev-news-2026-11-18-electrive-en', ['raw 檔名.md', ...], '標題', '> 導言', '內文')
    b.add('concepts/電池技術路線', ['E', 'D'], '## 小標（2026-11）\n\n> **結論**：...', rel=['[[BMW]]'])
    b.issue('BMW iX5 電芯供應商', 'InsideEVs：LGES／electrive：AESC', ['E', 'I'])

add() 會：改 updated:、把 slug 併入 sources:、把章節放進該頁當月的「## YYYY-MM 動態彙整」區塊
（不存在就在 Related 之前建立），最後自動補上「- 參見：」。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIKI = ROOT / 'wiki'
ISSUES = WIKI / '待核對清單.md'

def month_heading(month):
    return f'## {month} 動態彙整'

class Batch:
    def __init__(self, date, slugs):
        self.date, self.slugs, self.month = date, slugs, date[:7]

    def ref(self, keys, rel=()):
        links = [f'[[sources/{self.slugs[k]}]]' for k in keys] + list(rel)
        return '- 參見：' + ' | '.join(links)

    def source(self, slug, raw_files, title, intro, body):
        fm = ('---\ntags: [source]\nsources: [' + ', '.join(f'"{f}"' for f in raw_files) +
              f']\nupdated: {self.date}\n---\n\n# {title}\n\n{intro}\n\n{body.strip()}\n')
        (WIKI / 'sources' / f'{slug}.md').write_text(fm, encoding='utf-8')

    def add(self, page, keys, section, rel=()):
        p = WIKI / f'{page}.md'
        t = p.read_text(encoding='utf-8')
        t = re.sub(r'^updated:.*$', f'updated: {self.date}', t, count=1, flags=re.M)
        m = re.search(r'^sources:\s*\[(.*?)\]\s*$', t, re.M | re.S)
        if m:
            body = m.group(1)
            new = [self.slugs[k] for k in keys if self.slugs[k] not in body]
            if new:
                q = '"' in body
                extra = ', '.join((f'"{s}"' if q else s) for s in new)
                t = t[:m.start(1)] + (body.rstrip() + ', ' if body.strip() else '') + extra + t[m.end(1):]
        sec = section.strip()
        sec = re.sub(r'^## ', '### ', sec, flags=re.M)        # 降一級，收進月份區塊
        if '- 參見：' not in sec:
            sec += '\n\n' + self.ref(keys, rel)
        t = insert_into_month(t, self.month, sec)
        p.write_text(t, encoding='utf-8')

    def issue(self, topic, detail, keys, status='待核對'):
        """在 wiki/待核對清單.md 未結案表末加一列。detail 寫「A 說法／B 說法」。"""
        if not ISSUES.exists():
            raise SystemExit('wiki/待核對清單.md 不存在')
        src = '、'.join(f'[[sources/{self.slugs[k]}]]' for k in keys)
        row = f'| {self.date} | {topic} | {detail} | {src} | {status} |\n'
        t = ISSUES.read_text(encoding='utf-8')
        t = t.replace('<!-- OPEN-END -->', row + '<!-- OPEN-END -->', 1)
        ISSUES.write_text(t, encoding='utf-8')

def split_sections(text):
    """回傳 (前言, [(heading, body)])；只切 '## ' 層級。"""
    parts = re.split(r'(?m)^(?=## )', text)
    return parts[0], [(s.split('\n', 1)[0], s) for s in parts[1:]]

def insert_into_month(text, month, sec):
    head, secs = split_sections(text)
    mh = month_heading(month)
    for i, (h, s) in enumerate(secs):
        if h.strip() == mh:
            secs[i] = (h, s.rstrip('\n') + '\n\n' + sec + '\n\n')
            break
    else:
        block = (mh, f'{mh}\n\n> 本月逐批新增的動態；月底合併為一節 RRC 並更新頁首摘要與「簡報三段式」。\n\n{sec}\n\n')
        idx = next((i for i, (h, _) in enumerate(secs) if h.strip() == '## Related'), len(secs))
        secs.insert(idx, block)
    return head + ''.join(s for _, s in secs).rstrip('\n') + '\n'
