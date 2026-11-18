#!/usr/bin/env python3
"""把 concept／entity／country 頁中同一月份的「## 標題（YYYY-MM）」章節收進「## YYYY-MM 動態彙整」。

用法：python3 tools/ingest/consolidate.py [--min 2] [--dry]
- 只搬移與降級標題（## → ###、### → ####），不刪除任何內容。
- 同月份章節 ≥ --min 個才合併；「## Related」移到頁尾。
- 已存在的「動態彙整」區塊會沿用並依原順序併入。
"""
import re, argparse
from pathlib import Path
from wikiupd import WIKI, split_sections, month_heading

DATED = re.compile(r'^## .*?[（(](\d{4}-\d{2})(?:-\d{2})?[^）)]*[）)]\s*$')
ROLL = re.compile(r'^## (\d{4}-\d{2}) 動態彙整\s*$')

def demote(s):
    s = re.sub(r'(?m)^### ', '#### ', s)
    return re.sub(r'(?m)^## ', '### ', s)

def process(p, minimum, dry):
    t = p.read_text(encoding='utf-8')
    fm_end = t.find('\n---', 3)
    head, secs = split_sections(t)
    by_month = {}
    for h, s in secs:
        m = DATED.match(h) or ROLL.match(h)
        if m: by_month.setdefault(m.group(1), []).append(h)
    targets = {mo for mo, hs in by_month.items() if len(hs) >= minimum}
    if not targets and sum(1 for h, _ in secs if h.strip() == '## Related') < 2: return 0
    out, placed, related = [], set(), []
    groups = {mo: [] for mo in targets}
    for h, s in secs:
        if h.strip() == '## Related': related.append(s); continue
        m = DATED.match(h) or ROLL.match(h)
        mo = m.group(1) if m else None
        if mo in targets:
            body = s.split('\n', 1)[1] if ROLL.match(h) else demote(s)
            body = re.sub(r'^\s*> 本月逐批新增的動態.*\n', '', body) if ROLL.match(h) else body
            groups[mo].append(body.strip('\n'))
            if mo not in placed:
                out.append(('G', mo)); placed.add(mo)
        else:
            out.append(('S', s))
    res = head
    for kind, v in out:
        if kind == 'S': res += v
        else:
            mh = month_heading(v)
            res += f'{mh}\n\n> 本月逐批新增的動態；月底合併為一節 RRC 並更新頁首摘要與「簡報三段式」。\n\n' + '\n\n'.join(groups[v]) + '\n\n'
    if related:
        links, seen = [], set()
        for s in related:
            for l in s.split('\n')[1:]:
                if l.strip() and l.strip() not in seen: seen.add(l.strip()); links.append(l)
        res = res.rstrip('\n') + '\n\n## Related\n' + '\n'.join(links) + '\n'
    res = res.rstrip('\n') + '\n'
    n = sum(len(by_month[m]) for m in targets)
    if not dry: p.write_text(res, encoding='utf-8')
    return n

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--min', type=int, default=2); ap.add_argument('--dry', action='store_true')
    a = ap.parse_args(); total = 0
    for d in ('concepts', 'entities', 'countries'):
        for p in sorted((WIKI / d).glob('*.md')):
            n = process(p, a.min, a.dry)
            if n: print(f'{n:4d}  {d}/{p.stem}'); total += n
    print('sections grouped:', total)

if __name__ == '__main__':
    main()
