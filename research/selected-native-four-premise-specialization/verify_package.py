#!/usr/bin/env python3
"""Authenticate the frozen candidate and delimited imported review evidence."""
from hashlib import sha256
from pathlib import Path
import difflib
import json

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    record = json.loads((HERE/'INTEGRITY.json').read_text())
    for path, expected in record['files'].items():
        target = HERE/path
        need(target.is_file() and not target.is_symlink(), 'regular frozen file: '+path)
        need(sha256(target.read_bytes()).hexdigest() == expected, 'frozen candidate bytes: '+path)
    need(record['selected_certificate_changed'] is False, 'no selected certificate change')
    reviews = json.loads((HERE/'REVIEW-BINDINGS.json').read_text())
    for field in ('reviewed_argument','final_argument','complete_diff'):
        item = reviews[field]
        need(sha256((HERE/item['path']).read_bytes()).hexdigest() == item['sha256'],
             'review argument binding: '+field)
    original = reviews['reviewed_argument']['path']
    final = reviews['final_argument']['path']
    difference = ''.join(difflib.unified_diff((HERE/original).read_text().splitlines(True),
                                             (HERE/final).read_text().splitlines(True),
                                             fromfile=original,tofile=final))
    need(difference == (HERE/reviews['complete_diff']['path']).read_text(),
         'complete reviewed-to-final proof diff')
    for family, optimized in [('binary','RESULT-OPTIMIZED.json'),('complex','RESULT-O.json')]:
        need((HERE/'review'/family/'RESULT.json').read_bytes() ==
             (HERE/'review'/family/optimized).read_bytes(),
             'independent normal/optimized receipts: '+family)
    print(json.dumps(dict(status='PASS_SELECTED_NATIVE_PACKAGE_BINDINGS',
                         files=len(record['files']), selected_certificate_changed=False,
                         candidate_review_status=record['candidate_review_status']), indent=2))


if __name__ == '__main__':
    main()
