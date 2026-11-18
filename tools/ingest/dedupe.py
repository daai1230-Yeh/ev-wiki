#!/usr/bin/env python3
"""找出 raw/assets 新增且未重複的新聞檔。

用法：python3 tools/ingest/dedupe.py [--days 14]
輸出：tools/ingest/out/new.json（新檔清單），並列印：
  N <檔案>                 待 ingest
  D <檔案> <- <重複對象>    重複（標題正規化或原文網址相同），不 ingest
  ~ <檔案> ~ <檔案>         可能為同一事件（不同媒體），ingest 時請合併或互相標註
  ! <檔案> <類型>           贊助／AI生成／新聞稿等低權重內容
"""
import re, sys, json, unicodedata, subprocess, argparse, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'out'

def git_ls(*args):
    o = subprocess.run(['git', '-c', 'core.quotepath=off', 'ls-files', *args, '-z', 'raw/assets'],
                       cwd=ROOT, capture_output=True).stdout.decode()
    return [x for x in o.split('\0') if x.endswith('.md')]

def title_key(path):
    n = Path(path).stem
    n = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', n)
    n = unicodedata.normalize('NFKC', n)
    n = re.sub(r'HHTD\s*26', '', n, flags=re.I)
    return re.sub(r'[\s\W_]+', '', n).lower()

def read(path):
    try: return (ROOT / path).read_text(encoding='utf-8', errors='ignore')
    except Exception: return ''

def url_of(text):
    m = re.search(r'^source:\s*"?(https?://[^\s"]+)', text, re.M)
    if not m: return None
    u = m.group(1).split('#')[0].split('?')[0].rstrip('/')
    return u.lower()

ENT = None
def entities():
    global ENT
    if ENT is None:
        ENT = sorted({p.stem for p in (ROOT / 'wiki/entities').glob('*.md')} |
                     {'Cybercab', 'Model Y', 'Model 3', 'Neue Klasse', 'iX5', 'ID. Buzz', 'FSD', 'TAD',
                      'eCitaro', 'Zenob', 'Woodruff', 'Grünheide', 'Jupiter Power'}, key=len, reverse=True)
    return ENT
ALIAS = {'特斯拉': 'Tesla', '比亞迪': '比亞迪', 'BYD': '比亞迪', '福斯': 'Volkswagen', 'VW': 'Volkswagen',
         'Hyundai': '現代汽車', 'Kia': '起亞', 'Honda': '本田', 'Toyota': '豐田', 'CATL': '寧德時代',
         'Samsung SDI': '三星SDI', 'LG Energy': 'LGES', 'Li Auto': '理想汽車', 'Mercedes': '賓士', '賓士': '賓士'}

def topic_set(title):
    s = set()
    for a, b in ALIAS.items():
        if a.lower() in title.lower(): s.add(b)
    for e in entities():
        if e.lower() in title.lower(): s.add(e)
    return s

FLAGS = [(r'Sponsored|贊助', '贊助內容'), (r'AI\s*協助生成|AI-generated', 'AI生成稿'),
         (r'美通社|PR Newswire|prnasia', '廠商新聞稿'), (r'觀點：|觀點:|評論', '觀點稿')]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--days', type=int, default=14); a = ap.parse_args()
    tracked = git_ls()
    t_title = {title_key(f): f for f in tracked}
    t_url = {}
    cutoff = (datetime.date.today() - datetime.timedelta(days=a.days)).isoformat()
    recent = []
    for f in tracked:
        txt = read(f); u = url_of(txt)
        if u: t_url[u] = f
        d = Path(f).stem[:10]
        if d >= cutoff: recent.append(f)
    new, dup, seen_t, seen_u = [], [], {}, {}
    for f in sorted(git_ls('-o', '--exclude-standard')):
        k = title_key(f); txt = read(f); u = url_of(txt)
        hit = t_title.get(k) or seen_t.get(k) or (u and (t_url.get(u) or seen_u.get(u)))
        if hit: dup.append((f, hit)); continue
        seen_t[k] = f
        if u: seen_u[u] = f
        new.append(f)
    OUT.mkdir(exist_ok=True)
    (OUT / 'new.json').write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(new)} new, {len(dup)} duplicate')
    for f in new: print('N', f)
    for f, h in dup: print('D', f, '<-', h)
    # 同一事件提示：與本批其他檔或近 N 天已 ingest 檔共享 ≥2 個主題詞
    pool = [(f, topic_set(Path(f).stem)) for f in new] + [(f, topic_set(Path(f).stem)) for f in recent]
    for i, (f, s) in enumerate(pool[:len(new)]):
        for g, t in pool[i + 1:]:
            if len(s & t) >= 2: print('~', f, '~', g, sorted(s & t))
    for f in new:
        txt = read(f)[:3000]
        for pat, lab in FLAGS:
            if re.search(pat, txt): print('!', f, lab); break

if __name__ == '__main__':
    main()
