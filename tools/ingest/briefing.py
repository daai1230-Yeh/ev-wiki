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
