"""
Clean up army_index markdown files converted from Word.
Removes HTML/VML/CSS artifacts and fixes table row wrapping.

Usage:
    python clean_army_data.py            # preview (dry run)
    python clean_army_data.py --apply    # write changes to disk

After applying, delete data/vector_store/ and restart the app so
the vector store is rebuilt from the cleaned files.
"""

import re
import sys
from pathlib import Path

DRY_RUN = '--apply' not in sys.argv


# ── HTML / Word artifact patterns ─────────────────────────────────────────────

# <!-- [if …] --> … <![endif]--> conditional comment blocks
_IF_BLOCK = re.compile(r'<!--\[if[^\]]*\]>.*?<!\[endif\]-->', re.DOTALL)

# <style> … </style>
_STYLE_TAG = re.compile(r'<style[^>]*>.*?</style>', re.DOTALL | re.IGNORECASE)

# Any remaining HTML / XML tags
_ANY_TAG = re.compile(r'<[^>]+>', re.DOTALL)

# /* Style Definitions */ … block that leaks into plain text
_MSO_BLOCK = re.compile(r'/\*\s*Style Definitions\s*\*/.*?(?=\n\n|\Z)', re.DOTALL)

# v\:* {behavior:url(#default#VML);} lines (VML namespace CSS)
_VML_LINE = re.compile(
    r'^[vow]\\?:\*\s*\{behavior:url\(#default#VML\);\}\s*$', re.MULTILINE
)
_SHAPE_LINE = re.compile(
    r'^\.shape\s*\{behavior:url\(#default#VML\);\}\s*$', re.MULTILINE
)


def strip_html_artifacts(text: str) -> str:
    text = _IF_BLOCK.sub('', text)
    text = _STYLE_TAG.sub('', text)
    text = _ANY_TAG.sub('', text)
    text = _MSO_BLOCK.sub('', text)
    text = _VML_LINE.sub('', text)
    text = _SHAPE_LINE.sub('', text)
    # Collapse 3+ consecutive blank lines to two
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── Table row fixer ───────────────────────────────────────────────────────────

def fix_table_rows(text: str) -> str:
    """
    Each markdown table row must be on a single line ending with '|'.
    Word conversion sometimes wraps a long row across two lines; re-join them.
    """
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('|'):
            # Keep joining while the current line is an incomplete row
            # (doesn't end with '|') and the next line is also a table row
            while (
                not line.rstrip().endswith('|')
                and i + 1 < len(lines)
                and lines[i + 1].strip().startswith('|')
            ):
                i += 1
                # Strip leading '|' from continuation to avoid double '|'
                continuation = lines[i].strip()
                line = line.rstrip() + continuation[1:]  # drop leading '|'
            out.append(line)
        else:
            out.append(line)
        i += 1
    return '\n'.join(out)


# ── Per-file processing ───────────────────────────────────────────────────────

def clean_file(path: Path, dry_run: bool) -> tuple[bool, list[str]]:
    """Return (changed, diff_lines)."""
    original = path.read_text(encoding='utf-8', errors='replace')
    cleaned = strip_html_artifacts(original)
    cleaned = fix_table_rows(cleaned)

    if cleaned == original:
        return False, []

    # Build a short diff summary
    orig_lines = original.splitlines()
    new_lines = cleaned.splitlines()
    removed = len(orig_lines) - len(new_lines)
    diff = [f'  lines: {len(orig_lines)} → {len(new_lines)} ({removed:+d})']

    if not dry_run:
        path.write_text(cleaned, encoding='utf-8')

    return True, diff


def main():
    root = Path(__file__).parent
    army_dir = root / 'rules' / 'army_index'
    if not army_dir.exists():
        print(f'Directory not found: {army_dir}')
        sys.exit(1)

    md_files = sorted(army_dir.glob('*.md'))
    if not md_files:
        print('No .md files found.')
        sys.exit(0)

    mode = 'DRY RUN (preview)' if DRY_RUN else 'APPLYING changes'
    print(f'\n=== clean_army_data.py — {mode} ===\n')

    changed = 0
    for f in md_files:
        modified, diff = clean_file(f, DRY_RUN)
        if modified:
            marker = '[would change]' if DRY_RUN else '[changed]'
            print(f'  {marker} {f.name}')
            for d in diff:
                print(d)
            changed += 1
        else:
            print(f'  [ok]      {f.name}')

    print(f'\n{"Would update" if DRY_RUN else "Updated"} {changed}/{len(md_files)} file(s).')

    if DRY_RUN and changed:
        print('\nRun with --apply to write changes:')
        print('  python clean_army_data.py --apply')
    elif not DRY_RUN and changed:
        print('\nNext: delete the cached vector store so it is rebuilt from clean files:')
        print('  Remove-Item -Recurse -Force data\\vector_store')
        print('  python main.py   # or restart the app')


if __name__ == '__main__':
    main()
