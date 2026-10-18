# SPDX-License-Identifier: Apache-2.0
"""Independent review of the declared literal edit list (edits/declared_edits.py), with semantic tamper controls.

Edits found by Stack2979 / Jeremy Kothe (jeremykothe2), with AI assistance, on PR2979's words (mdumitrean). Does not import the
producer. It requires every shipped candidate to equal its parent with exactly the declared hunks (pure applier; profile, inventory
and cleanup re-derived), then runs the inherited exact auditor (forward and dual free-operator replay of all inputs) on the parent and
the candidate and on tampered copies. For every edit: a dropped new gate, a flipped coefficient and frames not re-solved (the old
frames put back on the new gates); and globally: the unedited restore, a stale cleanup, a stale claimed profile. Each tamper must be
rejected by the exact auditor or (profile/frame claims) by the re-derivation; the mechanism is recorded.
"""
import argparse, copy, gzip, hashlib, json, os, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'


def require(c, why):
    if not c:
        raise RuntimeError(why)


ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--source-dir', type=Path, required=True, help='directory holding audit_local.py and preload_move.py')
for n in ('parent-base', 'parent-extra', 'candidate-base', 'candidate-extra', 'edits'):
    ap.add_argument('--' + n, type=Path, required=True)
ap.add_argument('--out-dir', type=Path, required=True)
a = ap.parse_args()
ROOT, OUT = a.source_dir.resolve(), a.out_dir.resolve()
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).resolve().parent))
import declared_edits as D
pm = D.pm
AUDIT_SHA = 'a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
require(sha(ROOT / 'audit_local.py') == AUDIT_SHA, 'pinned auditor')
require(not OUT.exists(), 'fresh out-dir'); OUT.mkdir(parents=True)
read = lambda p: json.loads((lambda b: gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)(Path(p).read_bytes()))
SPEC = read(a.edits)


def audit(word, tag):
    p = OUT / (tag + '.json.gz')
    p.write_bytes(gzip.compress(json.dumps(word, separators=(',', ':')).encode(), mtime=0))
    out = OUT / (tag + '.audit.json')
    r = subprocess.run([sys.executable, '-B', str(ROOT / 'audit_local.py'), '--word', str(p), '--output', str(out)], capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    return r.returncode == 0 and out.exists() and json.loads(out.read_text()).get('status') == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD'


report = {'status': 'PASS_INDEPENDENT_EDIT_REVIEW', 'variants': {}}
for variant in ('base', 'extra'):
    S, X = read(getattr(a, 'parent_' + variant)), read(getattr(a, 'candidate_' + variant))
    edits, declared = SPEC['edits'][variant], SPEC['declared']
    require(set(S) == set(X), 'same section set')
    require({k for k in S if S[k] != X[k]} <= D.ALLOWED, 'only A, B, restore, report, cleanup differ')
    for k in ('cut', 'compensation', 'helper_final', 'start_extra', 'removed', 'prelude_events', 'warps'):
        require(S[k] == X[k], ('unchanged', k))
    rebuilt, ledger = D.apply(S, edits, declared)
    require(rebuilt == X, 'candidate is the parent with exactly the declared hunks')
    require(X['report']['local_profile'] == declared['local_profile'] and X['report']['width_inventory'] == declared['width_inventory'], 'declared profile and inventory')
    require(audit(S, variant + '-parent'), 'parent word audits (sanity)')
    require(audit(X, variant + '-candidate'), ('positive audit of the candidate', variant))
    controls = []

    def reject(name, mutate, rederive=False):
        m = copy.deepcopy(X)
        try:
            mutate(m)
        except Exception as e:
            controls.append([name, 'rejected at construction: %s' % e]); return
        require(m != X, ('control alters the word', name))
        if not audit(m, variant + '-ctl-' + name):
            controls.append([name, 'rejected by the exact auditor']); return
        require(rederive, ('tamper control accepted', name))
        controls.append([name, 'rejected by re-derivation (accepted by the auditor, but not the declared profile/cleanup)'])

    def locate(e):
        """index of the first new gate of edit e in the CANDIDATE word (edits are in source addresses; shift by earlier same-section edits)"""
        shift = sum(len(f['new']) - len(f['old']) for f in edits if f['section'] == e['section'] and f['start'] < e['start'])
        return e['section'], e['start'] + shift, len(e['new'])

    for e in edits:
        sec, i0, n = locate(e)
        require(X[sec][i0:i0 + n] == e['new'], ('edit located in candidate', e['id']))
        def drop(m, sec=sec, i0=i0): del m[sec][i0 + 1]
        reject('%s-drop-new-gate' % e['id'], drop)
        def flip(m, sec=sec, i0=i0, n=n):
            j = next(j for j in range(i0, i0 + n) if m[sec][j][0] == 'add'); m[sec][j][3] = -m[sec][j][3]
        reject('%s-flip-sign' % e['id'], flip)
        def stale(m, e=e, sec=sec, i0=i0, n=n):
            old = [g for g in e['old'] if g[-1] != e['new'][0][-1]] or e['old']
            for j in range(i0, i0 + n): m[sec][j][-1] = copy.deepcopy(old[min(j - i0, len(old) - 1)][-1])
            pr, inv = pm.frame_report(m)
            require(pr == declared['local_profile'] and inv == declared['width_inventory'], 'frames not re-solved change the paid profile')
        reject('%s-frames-not-resolved' % e['id'], stale, rederive=True)
        def small(m, sec=sec, i0=i0): m[sec][i0][-1] = m[sec][i0][-1][:-1]
        reject('%s-frame-below-bound' % e['id'], small)
    reject('parent-restore-kept', lambda m: m.__setitem__('restore', copy.deepcopy(S['restore'])))
    reject('stale-cleanup', lambda m: m.__setitem__('cleanup', copy.deepcopy(S['cleanup'])), rederive=True)
    def stale_claim(m): m['report'] = copy.deepcopy(S['report']); require(m['report'] == X['report'], 'stale claimed profile differs from the re-derived one')
    reject('stale-claimed-profile', stale_claim, rederive=True)
    require(len(controls) == 4 * len(edits) + 3, 'control count')
    report['variants'][variant] = dict(controls=controls, candidate_audit='PASS', ledger=ledger,
                                      parent_canonical_sha256=hashlib.sha256(json.dumps(S, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                                      candidate_canonical_sha256=hashlib.sha256(json.dumps(X, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
(OUT / 'REVIEW.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
print(report['status'], {v: len(d['controls']) for v, d in report['variants'].items()})
