#!/usr/bin/env python3
"""Re-extract the numerical table from a local copy of arXiv:2309.14850v2.

This optional provenance check performs no network access and writes no files.
Download the HTML linked in EXTERNAL.json separately, then pass its path.
Only stdlib HTML parsing is used. Article prose is not redistributed.
"""
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys


class Panels(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.depth = 0
        self.row = None
        self.cell = None
        self.math = None
        self.rows = {}

    def handle_starttag(self, tag, attrs):
        at = dict(attrs)
        if tag == 'section':
            if at.get('id') == 'S6.SS3':
                self.inside, self.depth = True, 1
            elif self.inside:
                self.depth += 1
        if not self.inside:
            return
        if tag == 'tr':
            self.row = []
        elif tag == 'td':
            self.cell, self.math = [], None
        elif tag == 'math' and self.cell is not None:
            self.math = at.get('alttext')

    def handle_data(self, text):
        if self.inside and self.cell is not None:
            self.cell.append(text)

    def handle_endtag(self, tag):
        if not self.inside:
            return
        if tag == 'td' and self.cell is not None:
            self.row.append(self.math if self.math is not None else ''.join(self.cell).strip())
            self.cell = None
        elif tag == 'tr' and self.row:
            match = re.fullmatch(r'\\chi_\{(\d+)\}', self.row[0])
            if match:
                self.rows.setdefault(int(match[1]), []).extend(map(int, self.row[1:]))
            self.row = None
        elif tag == 'section':
            self.depth -= 1
            if not self.depth:
                self.inside = False


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: extract_table.py /path/to/2309.14850v2.html')
    here = Path(__file__).resolve().parent
    content = Path(sys.argv[1]).read_bytes()
    parser = Panels()
    parser.feed(content.decode('utf8'))
    expected = json.loads((here/'table.json').read_text(encoding='utf8'))
    got = [parser.rows.get(i) for i in range(1,68)]
    if got != expected['characters'] or set(parser.rows) != set(range(1,68)):
        raise SystemExit('FAIL_PUBLISHED_TABLE_EXTRACTION')
    print(json.dumps({'status':'PASS_PUBLISHED_TABLE_EXTRACTION', 'characters':67,
                      'classes':67, 'html_sha256':sha256(content).hexdigest(),
                      'note':'HTML bytes may change; all mathematical table entries must agree.'}, indent=2))


if __name__ == '__main__':
    main()
