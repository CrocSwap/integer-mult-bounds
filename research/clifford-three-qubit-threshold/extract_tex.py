#!/usr/bin/env python3
"""Independently compare the published TeX table with the retained numbers.

Optional provenance check: accepts an already downloaded arXiv:2309.14850v2
TeX source. No network, article redistribution, or primary parser import.
Prepared for alephnan with OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from pathlib import Path
import re
import sys


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: extract_tex.py /path/to/2309.14850v2.tex')
    raw = Path(sys.argv[1]).read_bytes()
    text = raw.decode('utf8')
    heading = r'\subsection{Character table of Three-qubit Clifford group}'
    if text.count(heading) != 1:
        raise SystemExit('FAIL_TEX_TABLE_SECTION')
    text = text.split(heading, 1)[1]
    rows = {}
    for line in text.splitlines():
        match = re.match(r'\s*\$\\chi_\{(\d+)\}\$&(.*)', line)
        if match:
            cells = match[2].split(r'\\', 1)[0].split('&')
            try:
                values = [int(cell.strip()) for cell in cells]
            except ValueError as exc:
                raise SystemExit('FAIL_TEX_NONINTEGER_TABLE_CELL') from exc
            rows.setdefault(int(match[1]), []).extend(values)
    here = Path(__file__).resolve().parent
    retained = json.loads((here/'table.json').read_text(encoding='utf8'))['characters']
    if set(rows) != set(range(1,68)) or [rows[i] for i in range(1,68)] != retained:
        raise SystemExit('FAIL_TEX_TABLE_ENTRY_COMPARISON')
    print(json.dumps({'status':'PASS_PUBLISHED_TEX_TABLE_COMPARISON',
                      'characters':67, 'classes':67, 'cells_compared':4489,
                      'tex_sha256':sha256(raw).hexdigest()}, indent=2))


if __name__ == '__main__':
    main()
