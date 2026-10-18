"""B. Spec versus convention census: every file:line anchor of the rule table (README section B.2) is checked here.

data/census/anchors.json lists, per table row, (path, line, needle), with line numbers as of the base commit 7dfa22b.
The needle must occur within two lines of the cited line (paths relative to the repository root; the upstream paper is
upstream/build/sections).  Files under docs/research/ (the hub's ledgers and reviews, which main rewrites often) are
matched by their text anywhere in the file, and the line where it now sits is printed.  The line ranges cited in the
prose of README sections B.1 and B.3 are not in this list.
The classification of each rule (spec / proved / convention) is argued in the README; this script only checks that
the cited text says what the table quotes, plus four corrections that are statements about the repository itself.
"""
import json
import re

from report import DATA, REPO, check, finish

WINDOW = 2
anchors = json.loads((DATA / 'census' / 'anchors.json').read_text())
by_row = {}
for a in anchors:
    lines = (REPO / a['path']).read_text(encoding='utf-8').split('\n')
    if a['path'].startswith('docs/research/'):
        hits = [i + 1 for i, ln in enumerate(lines) if a['needle'] in ln]
        ok = bool(hits)
        where = '%s:%d (7dfa22b), text now at %s' % (a['path'], a['line'], ','.join(map(str, hits)) or '-')
    else:
        lo, hi = max(0, a['line'] - 1 - WINDOW), min(len(lines), a['line'] + WINDOW)
        ok = any(a['needle'] in lines[i] for i in range(lo, hi))
        where = '%s:%d' % (a['path'], a['line'])
    by_row.setdefault(a['row'], []).append((ok, where))
for row in sorted(by_row):
    res = by_row[row]
    check('B.row%02d' % row, all(ok for ok, _ in res),
          '%d anchors: %s' % (len(res), ', '.join(loc + ('' if ok else ' MISSING') for ok, loc in res)))

# Correction 1: in the bit legality checker, the nested-and-priced MOVE rule, the common-frame ADD rule and the COPY
# lifecycle are all on line 11; line 10 holds the containment helper and the owner/helper selection.
L = (REPO / 'research/e8-bit-carrier-skeleton/code/bit/checkers/legality_h.cpp').read_text().split('\n')
check('B.corr.legality-line11',
      all(t in L[10] for t in ('illegal or mispriced MOVE', 'ADD not in common frame', 'invalid COPY lifecycle'))
      and 'owners' in L[9] and 'illegal or mispriced MOVE' not in L[9],
      'MOVE / ADD / COPY rules on legality_h.cpp:11; owner selection on :10')
# Correction 2: the invocation invariant Inv used by the complex five-stage bridge is imported, not defined, in main.
lean = [p for p in REPO.rglob('*.lean') if '.git' not in p.parts]
defs = [p for p in lean if re.search(r'^\s*(structure|def|class|abbrev|inductive)\s+G?Inv\b', p.read_text(errors='ignore'), re.M)]
imps = [p for p in lean if 'import Work.Bridge.Inv' in p.read_text(errors='ignore')]
check('B.corr.inv-not-defined', not defs and len(imps) >= 1,
      '%d Lean files import Work.Bridge.Inv; no Lean file of main defines Inv or GInv' % len(imps))
# Correction 3: PR #370's assertion 'x registers are never destinations' is sufficient, not necessary (#425, #493).
R = (REPO / 'research/e8-bit-carrier-skeleton/README.md').read_text()
check('B.corr.x-destinations', '"x registers are never destinations"' in R and 'sufficient condition, not a necessary one' in R,
      "#493's README records the #370 assertion as sufficient, not necessary (#425's scalar-interface lemma)")
# Correction 4: the maintainer's review lists whole-call hosting and normalized wrappers as interface assumptions and
# says the fixed-word ceiling discussions were not independently certified.
D = (REPO / 'docs/research/community-pr531-review.md').read_text()
check('B.corr.scope-note', 'whole-call correlated-helper hosting' in D and 'independently certified** in this integration' in D,
      'docs/research/community-pr531-review.md, "Scope and research notes"')
finish()
