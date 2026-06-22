#!/usr/bin/env python3
"""
convert_foreign_news.py
將「駐外新聞」Google Drive 資料夾內的 PDF/DOCX/ODT/TIF 檔案
轉換為 Markdown，存入 raw/assets/駐外新聞/

用法：
  python3 convert_foreign_news.py           # 只處理新增/更新的檔案
  python3 convert_foreign_news.py --all     # 重新處理所有檔案
  python3 convert_foreign_news.py --dry-run # 列出待處理檔案，不實際轉換
"""

import os
import re
import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime

# ─── 路徑設定 ──────────────────────────────────────────────
SOURCE_DIR = Path("/Users/claude/Library/CloudStorage/GoogleDrive-daai1230@gmail.com/我的雲端硬碟/駐外新聞")
OUTPUT_DIR = Path("/Users/claude/Documents/Claude code AI筆記/raw/assets/駐外新聞")
MANIFEST_FILE = Path("/Users/claude/Documents/Claude code AI筆記/raw/assets/駐外新聞/.manifest.json")

# ─── 日期轉換（民國 → 西元）──────────────────────────────
def roc_to_ad(roc_year: int) -> int:
    return roc_year + 1911

# ─── 檔名解析 ─────────────────────────────────────────────
ATTACH_PATTERNS = [
    re.compile(r'[\(（]附件\s*(\d+)[\)）]$', re.IGNORECASE),  # (附件1) / （附件1）
    re.compile(r'_附件\s*(\d+)$', re.IGNORECASE),             # _附件1
    re.compile(r'[。\.]附件\s*(\d+)$', re.IGNORECASE),        # 。附件1 / .附件1
    re.compile(r'[。\.]附件$', re.IGNORECASE),                 # 。附件 (無數字)
    re.compile(r'[\(（]來函[\)）]$'),                          # (來函)
    re.compile(r'_來函$'),
    re.compile(r'[\(（]附件[\)）]$', re.IGNORECASE),           # (附件) 無數字
]

DATE_RE = re.compile(r'^(\d{2,3})\.(\d{1,2})\.(\d{1,2})')

def parse_filename(fname: str):
    """
    解析檔名，回傳 (ad_date_str, base_key, attachment_idx, clean_title)
    ad_date_str: "YYYY-MM-DD"
    base_key: 去掉附件後綴的純標題（用於分組）
    attachment_idx: None=主檔，int=附件序號
    clean_title: 適合用作 MD 檔名的標題
    """
    stem = Path(fname).stem

    # 日期
    m = DATE_RE.match(stem)
    if not m:
        return None
    roc_y, mo, da = int(m.group(1)), int(m.group(2)), int(m.group(3))
    ad_y = roc_to_ad(roc_y)
    date_str = f"{ad_y}-{mo:02d}-{da:02d}"

    # 去掉日期前綴，取標題部分
    title_part = stem[m.end():].strip('_').strip()

    # 檢查是否為附件
    attach_idx = None
    for pat in ATTACH_PATTERNS:
        ma = pat.search(title_part)
        if ma:
            attach_idx = int(ma.group(1)) if ma.lastindex and ma.lastindex >= 1 else 99
            title_part = title_part[:ma.start()].rstrip('_').strip()
            break

    # 去掉括號內的會辦、函 等行政標記，作為 base_key
    base_key = title_part
    # 清理不合法字元，作為 MD 檔名
    clean_title = re.sub(r'[/\\:*?"<>|]', '-', title_part)
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()

    return date_str, base_key, attach_idx, clean_title


# ─── 文字擷取 ─────────────────────────────────────────────
def extract_pdf(path: Path) -> str:
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(str(path))
        # 去掉裝訂線（豎排｜字元）
        text = re.sub(r'[｜|]{2,}', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    except Exception as e:
        return f"[PDF 擷取失敗：{e}]"

def extract_docx(path: Path) -> str:
    try:
        import docx
        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return '\n\n'.join(paragraphs)
    except Exception as e:
        return f"[DOCX 擷取失敗：{e}]"

def extract_odt(path: Path) -> str:
    try:
        from odf import teletype
        from odf.opendocument import load
        doc = load(str(path))
        return teletype.extractText(doc.text).strip()
    except Exception as e:
        return f"[ODT 擷取失敗：{e}]"

def extract_tif(path: Path) -> str:
    # TIF 通常是掃描圖，需要 OCR
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(str(path))
        text = pytesseract.image_to_string(img, lang='chi_tra+eng')
        return text.strip() if text.strip() else "[TIF 掃描圖，OCR 無法識別文字]"
    except Exception:
        return "[TIF 掃描圖檔，需要手動閱讀（未安裝 Tesseract OCR）]"

def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        return extract_pdf(path)
    elif suffix == '.docx':
        return extract_docx(path)
    elif suffix == '.doc':
        return extract_docx(path)  # 嘗試，可能失敗
    elif suffix == '.odt':
        return extract_odt(path)
    elif suffix in ('.tif', '.tiff'):
        return extract_tif(path)
    else:
        return f"[不支援的檔案格式：{suffix}]"


# ─── 群組化（主檔 + 附件）────────────────────────────────
def group_files_in_folder(folder: Path):
    """
    回傳 list of (date_str, clean_title, country, main_file, [attach_files])
    """
    groups = {}  # base_key -> {date, clean_title, main, attaches}

    for f in sorted(folder.iterdir()):
        if f.is_dir() or f.suffix.lower() in ('.db',):
            continue
        parsed = parse_filename(f.name)
        if not parsed:
            continue
        date_str, base_key, attach_idx, clean_title = parsed

        key = (date_str, base_key)
        if key not in groups:
            groups[key] = {
                'date': date_str,
                'clean_title': clean_title,
                'main': None,
                'attaches': []
            }

        if attach_idx is None:
            groups[key]['main'] = f
        else:
            groups[key]['attaches'].append((attach_idx, f))

    return groups


# ─── 產生 MD ─────────────────────────────────────────────
def build_md(date_str: str, clean_title: str, country: str,
             main_file: Path | None, attach_files: list[tuple]) -> str:
    """
    組合主檔 + 附件為一份 MD
    """
    today = datetime.now().strftime('%Y-%m-%d')

    # frontmatter
    lines = [
        '---',
        f'title: "{clean_title}"',
        f'date: {date_str}',
        f'country: {country}',
        f'source: 駐外新聞',
        f'tags:',
        f'  - 駐外新聞',
        f'  - {country}',
        f'clipped: {today}',
        '---',
        '',
        f'# {clean_title}',
        '',
        f'**發文日期**：{date_str}　｜　**地區**：{country}',
        '',
        '---',
        '',
    ]

    # 主文
    if main_file:
        lines.append('## 主文')
        lines.append('')
        text = extract_text(main_file)
        lines.append(text)
        lines.append('')
    else:
        lines.append('（無主文檔案）')
        lines.append('')

    # 附件
    if attach_files:
        for idx, af in sorted(attach_files, key=lambda x: x[0]):
            lines.append(f'---')
            lines.append('')
            lines.append(f'## 附件 {idx}')
            lines.append('')
            text = extract_text(af)
            lines.append(text)
            lines.append('')

    # 原始檔案參考
    lines.append('---')
    lines.append('')
    lines.append('## 原始檔案')
    lines.append('')
    if main_file:
        lines.append(f'- 主文：`{main_file.name}`')
    for idx, af in sorted(attach_files, key=lambda x: x[0]):
        lines.append(f'- 附件 {idx}：`{af.name}`')

    return '\n'.join(lines)


# ─── MD 輸出檔名 ─────────────────────────────────────────
def make_output_filename(date_str: str, country_folder: str, clean_title: str) -> str:
    # 取國家名（去掉「亞-」「歐-」等前綴）
    country_short = re.sub(r'^[^\-]+-', '', country_folder)
    # 限制標題長度
    title_truncated = clean_title[:60].strip()
    fname = f"{date_str}-{country_short}-{title_truncated}.md"
    # 去掉 Windows 不合法字元
    fname = re.sub(r'[/\\:*?"<>|]', '-', fname)
    return fname


# ─── Manifest（增量追蹤）────────────────────────────────
def load_manifest() -> dict:
    if MANIFEST_FILE.exists():
        with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_manifest(manifest: dict):
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

def file_hash(path: Path) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def group_hash(main_file, attach_files) -> str:
    """所有相關檔案的 hash 合併，用於偵測更新"""
    files = []
    if main_file:
        files.append(main_file)
    files.extend([af for _, af in attach_files])
    combined = '|'.join(f"{f.name}:{file_hash(f)}" for f in sorted(files, key=lambda x: x.name))
    return hashlib.md5(combined.encode()).hexdigest()


# ─── 主流程 ──────────────────────────────────────────────
def main():
    force_all = '--all' in sys.argv
    dry_run = '--dry-run' in sys.argv

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()

    new_count = 0
    skip_count = 0
    error_count = 0
    updated_files = []

    country_folders = [d for d in sorted(SOURCE_DIR.iterdir()) if d.is_dir()]

    for country_folder in country_folders:
        country_name = country_folder.name
        groups = group_files_in_folder(country_folder)

        for (date_str, base_key), g in sorted(groups.items()):
            main_file = g['main']
            attach_files = g['attaches']
            clean_title = g['clean_title']

            output_fname = make_output_filename(date_str, country_name, clean_title)
            output_path = OUTPUT_DIR / output_fname

            # 計算 hash 偵測變動
            manifest_key = str(output_fname)
            try:
                gh = group_hash(main_file, attach_files)
            except Exception as e:
                print(f"  ⚠️  Hash 失敗 {output_fname}: {e}")
                error_count += 1
                continue

            if not force_all and manifest.get(manifest_key) == gh:
                skip_count += 1
                continue

            # 有更新或全新
            if dry_run:
                status = '新增' if manifest_key not in manifest else '更新'
                print(f"  [{status}] {output_fname}")
                updated_files.append(output_fname)
                new_count += 1
                continue

            try:
                md_content = build_md(date_str, clean_title, country_name,
                                      main_file, attach_files)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                manifest[manifest_key] = gh
                status = '新增' if output_path.stat().st_size > 0 else '更新'
                print(f"  ✅ {output_fname}")
                updated_files.append(output_fname)
                new_count += 1
            except Exception as e:
                print(f"  ❌ {output_fname}: {e}")
                error_count += 1

    if not dry_run:
        save_manifest(manifest)

    print()
    print(f"{'模擬' if dry_run else '完成'}：新增/更新 {new_count} 篇，跳過 {skip_count} 篇（無變動），失敗 {error_count} 篇")
    if updated_files:
        print()
        print("更新的檔案：")
        for f in updated_files:
            print(f"  raw/assets/駐外新聞/{f}")

    return updated_files


if __name__ == '__main__':
    main()
