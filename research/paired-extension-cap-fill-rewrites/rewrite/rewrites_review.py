# SPDX-License-Identifier: Apache-2.0
"""Independent review of the declared PR2917 gate rewrites, with semantic tamper controls.

Rewrites by Jeremy Kothe (jeremykothe2), with AI assistance, on PR2917's (mason-hale) words (PR2908 jeremydiviney; PR2894; PR2857 Lyy-iiis).
Does not import the producer. It requires every shipped candidate to differ from its PR2917 source only in sections A and restore (plus
the derived report/cleanup) and, per rewrite class, to consist of exactly the declared literal hunks; then the inherited exact auditor
(forward and dual free-operator replay of every input column) must accept the candidate and REJECT each tampered copy, with at least
two tamper controls for every rewrite class: R-retime, A3779-cut-start-read, PM-carrier-lender-entry, B-carrier-retime.
"""
import argparse, copy, gzip, hashlib, json, os, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'


def require(c, why):
    if not c:
        raise RuntimeError(why)


ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--source-dir', type=Path, required=True, help='pinned PR2833 new/borrow directory holding audit_local.py')
for n in ('parent-base', 'parent-extra', 'candidate-base', 'candidate-extra', 'rewrites'):
    ap.add_argument('--' + n, type=Path, required=True)
ap.add_argument('--out-dir', type=Path, required=True)
a = ap.parse_args()
ROOT, OUT = a.source_dir.resolve(), a.out_dir.resolve()
AUDIT_SHA = 'a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
require(sha(ROOT / 'audit_local.py') == AUDIT_SHA, 'pinned auditor')
require(not OUT.exists(), 'fresh out-dir'); OUT.mkdir(parents=True)
read = lambda p: json.loads((lambda b: gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)(Path(p).read_bytes()))
R = read(a.rewrites)
CLASSES = {'R-retime', 'A3779-cut-start-read', 'PM-carrier-lender-entry', 'B-carrier-retime'}
require({r['cls'] for r in R} == CLASSES, 'four declared classes')


def audit(word, tag):
    p = OUT / (tag + '.json.gz')
    p.write_bytes(gzip.compress(json.dumps(word, separators=(',', ':')).encode(), mtime=0))
    out = OUT / (tag + '.audit.json')
    r = subprocess.run([sys.executable, '-B', str(ROOT / 'audit_local.py'), '--word', str(p), '--output', str(out)], capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    ok = r.returncode == 0 and out.exists() and json.loads(out.read_text()).get('status') == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD'
    return ok


def inserted(rw):
    """Literal gates a rewrite inserts (new minus old, as multiset), with their section and address."""
    out = []
    for e in rw['edits']:
        old = [json.dumps(g) for g in e['old']]
        for g in e['new']:
            if json.dumps(g) in old:
                old.remove(json.dumps(g))
            else:
                out.append((e['section'], e['start'], g))
    return out


def find(word, sec, g):
    h = [i for i, x in enumerate(word[sec]) if x == g]
    require(len(h) >= 1, ('gate present', g)); return h[0]


report = {'status': 'PASS_INDEPENDENT_REWRITE_REVIEW', 'variants': {}}
for variant in ('base', 'extra'):
    S, X = read(getattr(a, 'parent_' + variant)), read(getattr(a, 'candidate_' + variant))
    require(set(S) == set(X), 'same section set')
    require({k for k in S if S[k] != X[k]} <= {'A', 'B', 'restore', 'warps', 'report', 'cleanup'}, 'only A, B, restore, warps, report, cleanup differ')
    for k in ('cut', 'compensation', 'helper_final', 'start_extra', 'removed', 'prelude_events'):
        require(S[k] == X[k], ('unchanged', k))
    # candidate = source with the declared hunks and nothing else: replay by a one-pass sequence merge
    for sec in ('A', 'B', 'restore'):
        hunks = sorted((e['start'], e['stop'], e['new']) for rw in R for e in rw['edits'] if e['section'] == sec)
        out, pos = [], 0
        for s0, s1, new in hunks:
            require(s0 >= pos, 'ordered disjoint hunks'); out += S[sec][pos:s0] + new; pos = s1
        out += S[sec][pos:]
        require(out == X[sec], ('candidate ' + sec + ' is the source with exactly the declared hunks'))
    # phase warps: only their B positions move, by the number of deleted B gates before them
    deleted = [e['start'] for rw in R for e in rw['edits'] if e['section'] == 'B' and not e['new']]
    require(len(S['warps']) == len(X['warps']) and all(x[1:] == s[1:] and x[0] == s[0] - sum(1 for d in deleted if d < s[0]) for s, x in zip(S['warps'], X['warps'])), 'warp positions shifted by deleted B gates only')
    require(X['report']['local_profile'] == {'1': 2407, '2': 641, '3': 281, '4': 111, '5': 26, '8': 8}, 'paid profile')
    require(X['report']['width_inventory'] == {'4': 26, '5': 2, '7': 62, '8': 96, '9': 222}, 'inventory unchanged')
    require(audit(S, variant + '-source'), 'source word audits (sanity)')
    require(audit(X, variant + '-candidate'), ('positive audit of the candidate', variant))
    controls = []

    def reject(name, mutate):
        m = copy.deepcopy(X)
        try:
            mutate(m)
        except Exception as e:
            controls.append([name, 'rejected at construction: %s' % e]); return
        require(m != X, ('control alters the word', name))
        require(not audit(m, variant + '-ctl-' + name), ('tamper control accepted', name))
        controls.append([name, 'rejected by the exact auditor'])

    by = {}
    for rw in R: by.setdefault(rw['cls'], []).append(rw)
    # R-retime: drop the early entry; flip its sign
    rt = by['R-retime'][0]; sec, _, g = inserted(rt)[0]
    reject('R-retime-drop-early-entry', lambda m: m[sec].pop(find(m, sec, g)))
    def flip(m, sec=sec, g=g): m[sec][find(m, sec, g)][3] = -m[sec][find(m, sec, g)][3]
    reject('R-retime-flip-sign', flip)
    rt2 = by['R-retime'][2]; sec2, _, g2 = inserted(rt2)[0]
    reject('R-retime-drop-second-class-entry', lambda m: m[sec2].pop(find(m, sec2, g2)))
    # A3779: drop the moved read; flip it
    ar = by['A3779-cut-start-read'][0]; sa, _, ga = inserted(ar)[0]
    reject('A3779-drop-read', lambda m: m[sa].pop(find(m, sa, ga)))
    def flip2(m): m[sa][find(m, sa, ga)][3] = -m[sa][find(m, sa, ga)][3]
    reject('A3779-flip-sign', flip2)
    # PM-carrier lender entries: drop one, flip one, swap the lender register of one
    pc = by['PM-carrier-lender-entry']; ins = [x for rw in pc for x in inserted(rw)]
    sp, _, gp = ins[0]
    reject('PM-carrier-drop-entry', lambda m: m[sp].pop(find(m, sp, gp)))
    def flip3(m): m[sp][find(m, sp, gp)][3] = -m[sp][find(m, sp, gp)][3] if gp[0] == 'add' else 0
    reject('PM-carrier-flip-sign', flip3)
    sq, _, gq = ins[-1]
    def swap(m): m[sq][find(m, sq, gq)][2] = gq[2] + 1
    reject('PM-carrier-wrong-lender', swap)
    # B-carrier-retime: drop the moved lender gate in A; flip it; keep the deleted B gate as well (double application)
    bc = by['B-carrier-retime'][0]; sb, _, gb = [t for t in inserted(bc) if t[0] == 'A'][0]
    reject('B-carrier-retime-drop-A-gate', lambda m: m[sb].pop(find(m, sb, gb)))
    def flip4(m): m[sb][find(m, sb, gb)][3] = -m[sb][find(m, sb, gb)][3]
    reject('B-carrier-retime-flip-sign', flip4)
    bold = [e for e in bc['edits'] if e['section'] == 'B'][0]
    def keepb(m): m['B'].insert(bold['start'], copy.deepcopy(bold['old'][0]))
    reject('B-carrier-retime-keep-B-gate', keepb)
    reject('stale-cleanup', lambda m: m.__setitem__('cleanup', copy.deepcopy(S['cleanup'])))
    # a derived cleanup that is stale does not change the program; the exact auditor must still bind it
    reject('source-restore-kept', lambda m: m.__setitem__('restore', copy.deepcopy(S['restore'])))
    require(len(controls) == 13, 'thirteen controls')
    report['variants'][variant] = dict(controls=controls, candidate_audit='PASS', source_canonical_sha256=hashlib.sha256(json.dumps(S, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                                      candidate_canonical_sha256=hashlib.sha256(json.dumps(X, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
(OUT / 'REVIEW.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
print(report['status'], {v: len(d['controls']) for v, d in report['variants'].items()})
