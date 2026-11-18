"""寫入／更新 concept 頁的「## 簡報三段式」卡片（位置：頁首摘要段落之後、第一個 ## 之前）。

    from briefing import put
    put('電池技術路線', '2026-11-18', CARD_MARKDOWN)               # concept 頁
    put('韓國', '2026-11-18', CARD_MARKDOWN, folder='countries')   # 國家頁
"""
import re
from wikiupd import WIKI

HEAD = '## 簡報三段式（更新：{d}）'
NOTE = '> 演講或簡報前的備課卡，依《高效演講》的「坡道—發現—甜點」結構，以可直接講出口的段落寫成；講稿口吻依 [[templates/逐字稿專家口吻指南]]。數字引用前請查 [[待核對清單]]。'

def put(stem, date, card, folder='concepts'):
    p = WIKI / folder / f'{stem}.md'
    t = p.read_text(encoding='utf-8')
    block = HEAD.format(d=date) + '\n\n' + NOTE + '\n\n' + card.strip() + '\n\n'
    m = re.search(r'(?ms)^## 簡報三段式（更新：[^）]*）\n.*?(?=^## )', t)
    if m:
        t = t[:m.start()] + block + t[m.end():]
    else:
        m = re.search(r'(?m)^## ', t)
        t = t[:m.start()] + block + t[m.start():]
    t = re.sub(r'^updated:.*$', f'updated: {date}', t, count=1, flags=re.M)
    p.write_text(t, encoding='utf-8')

def _card_span(t):
    m = re.search(r'(?ms)^## 簡報三段式（更新：[^）]*）\n.*?(?=^## (?!簡報))', t)
    if not m: raise ValueError('no card')
    return m

def set_ramp(stem, ramp, folder='concepts'):
    """只替換「### 坡道」到「**一句話主題**」之間的開場段落。"""
    p = WIKI / folder / f'{stem}.md'; t = p.read_text(encoding='utf-8')
    m = _card_span(t); card = m.group(0)
    new = re.sub(r'(?s)(### 坡道[^\n]*\n\n).*?(\n\n\*\*一句話主題\*\*)', lambda x: x.group(1) + ramp.strip() + x.group(2), card, count=1)
    if new == card: raise ValueError(f'ramp not replaced: {stem}')
    p.write_text(t[:m.start()] + new + t[m.end():], encoding='utf-8')

def set_glossary(stem, items, folder='concepts'):
    """在卡片末尾放「**名詞速懂（給新人）**」；items 為 [(名詞, 解釋), ...]，已存在則取代。"""
    p = WIKI / folder / f'{stem}.md'; t = p.read_text(encoding='utf-8')
    m = _card_span(t); card = m.group(0).rstrip('\n')
    card = re.sub(r'(?s)\n\n\*\*名詞速懂（給新人）\*\*\n.*$', '', card)
    block = '\n\n**名詞速懂（給新人）**\n' + '\n'.join(f'- **{k}**：{v}' for k, v in items)
    p.write_text(t[:m.start()] + card + block + '\n\n' + t[m.end():], encoding='utf-8')
