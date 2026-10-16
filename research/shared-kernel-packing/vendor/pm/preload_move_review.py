# SPDX-License-Identifier: Apache-2.0
"""Independent review of the declared preload-move stage, with semantic fault controls.

Preload re-synthesis by Jeremy Kothe (jeremykothe2) with AI assistance, on the PR2857
(Lyy-iiis) shared-kernel words and PR2863 (Dugongue) packing. This reviewer does not import
the producer. It re-derives, from the PR2857 words alone, the staged-kernel gates of the two
declared quartets, the delivery entries, the preload-network edits and the carrier raises,
and requires the shipped candidate to differ from the source by exactly that. The inherited
exact auditor (forward and dual free-operator replay over every input column) then audits the
candidate, and eleven fault controls must each be rejected by it.
"""
def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)

import os, sys, json, gzip, copy, hashlib, subprocess, argparse, importlib.util
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-dir', type=Path, required=True, help='pinned PR2833 new/borrow directory (audit_local.py, word_patch.py)')
for name in ('shared-base', 'shared-extra', 'candidate-base', 'candidate-extra', 'patch-base', 'patch-extra'):
    parser.add_argument('--' + name, type=Path, required=True)
parser.add_argument('--out-dir', type=Path, required=True)
args = parser.parse_args()
ROOT = args.source_dir.resolve()
OUT = args.out_dir.resolve()
require(not OUT.exists() and OUT != ROOT and ROOT not in OUT.parents and OUT not in ROOT.parents, 'fresh external out-dir')
PINS = {'word_patch': ('word_patch.py', '9b3287f189c4f29c1a8bdb1ba01fdcfe14a57d87b50fa4f2f646fb2346ab01ce'), 'audit_local': ('audit_local.py', 'a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90')}
SOURCE_CANONICAL = {'base': 'c0af0ef7ee6282e91f046d027983b35eaed7ebcb46489134d47e07724cf664bc', 'extra': '61b20fbe78fdcbca0cde0597befcc254017ee206dad0724c576672aca690c66f'}
QUARTETS = [dict(q=(457, 456, 466, 467), holder=499, preload_old=(85, 'add', 457, 498), preload_new=['add', 456, 498, -1, 1, []], after_pair={466: (105, 500), 467: None}, undo_after=(105, ['add', 467, 500, -1, 1, []])),
            dict(q=(458, 459, 464, 465), holder=510, preload_old=(100, 'add', 458, 510), preload_new=['add', 459, 510, -1, 1, []], undo_after=(125, ['add', 465, 512, -1, 1, []]))]
HOLDERS = {457: 499, 458: 510}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canon(w):
    return hashlib.sha256(json.dumps(w, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def read(path):
    b = Path(path).read_bytes()
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)
def tree_snapshot(root):
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}

before = {k: sha(ROOT / f) for k, (f, h) in PINS.items()}
for k, (f, h) in PINS.items():
    require(before[k] == h, ('pinned source mismatch', k))
protected = {}
for t in ('base', 'extra'):
    for kind in ('shared', 'candidate', 'patch'):
        protected[kind + '_' + t] = getattr(args, kind + '_' + t).resolve()
before.update({k: sha(p) for k, p in protected.items()})
tree_before = tree_snapshot(ROOT)
OUT.mkdir(parents=True)
spec = importlib.util.spec_from_file_location('_pinned_word_patch', ROOT / 'word_patch.py')
wp = importlib.util.module_from_spec(spec); spec.loader.exec_module(wp)

def basis(vs):
    piv = {}
    for a in vs:
        while a:
            bit = a.bit_length() - 1
            if bit in piv: a ^= piv[bit]
            else: piv[bit] = a; break
    for k in sorted(piv):
        for j in piv:
            if j > k and piv[j] >> k & 1: piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv, reverse=True))
def span(U):
    s = {0}
    for z in U: s |= {z ^ v for v in list(s)}
    return s
def regs(g):
    return g[1:3] if g[0] == 'add' else g[1:2]
def rederive(m):
    t = copy.deepcopy(m); t['A'] = t['A'][t['prelude_events']:]
    return wp.derive_cleanup(t, wp.restored_of(m))

def expected_gates(S, q, holder):
    """Kernel, entry and carrier facts of one quartet, re-derived from the SOURCE word only."""
    A = S['A']; info = {}
    for h in q:
        pairs = [(i, g) for i, g in enumerate(A) if g[0] == 'add' and g[1] == h and g[-1]]
        require(len(pairs) == 1, ('one staged pair gate', h, pairs))
        i, g = pairs[0]; s = g[2]
        require(all(e[1] != s for e in A), ('partner A-constant', h))
        info[h] = (i, s, g[3], g[4], tuple(basis(g[-1])), g[-1])
    q0, q1, q2, q3 = q
    i0, s0, n0, d0, E, E_raw = info[q0]; i1, s1, n1, d1, E1, _ = info[q1]
    i2, s2, n2, d2, G, G_raw = info[q2]; i3, s3, n3, d3, G1, _ = info[q3]
    require(E == E1 and G == G1 and len(E) == len(G) == 2, 'paired frame interface')
    line = sorted((span(E) & span(G)) - {0})
    require(len(line) == 1, 'frames meet in exactly one line')
    L = list(basis(line))
    mk = lambda t, s, n, d, U: ['add', t, s, n, d, list(U)]
    return dict(L=L, i0=i0,
        kernel={min(i0, i2): [mk(q2, q0, -1, 1, L)],
                max(i0, i1) + 1: [mk(q1, q0, 1, 1, E_raw), mk(q1, s0, -n0, d0, E_raw)],
                max(i2, i3) + 1: [mk(q3, q2, 1, 1, G_raw), mk(q3, s2, -n2, d2, G_raw)]},
        entry=mk(q0, holder, 1, 1, L))

receipt = {'status': 'PASS_INDEPENDENT_PRELOAD_MOVE_REVIEW', 'variants': {}}
for variant in ('base', 'extra'):
    S = read(protected['shared_' + variant]); X = read(protected['candidate_' + variant]); P = read(protected['patch_' + variant])
    require(canon(S) == SOURCE_CANONICAL[variant] == P['source_canonical_sha256'], 'authenticated PR2857 source word')
    require(canon(X) == P['candidate_canonical_sha256'], 'candidate matches its declaration')
    require(P['stage'] == 'preload-move' and P['variant'] == variant, 'declared stage')
    allowed = {'A', 'B', 'compensation', 'start_extra', 'report', 'cleanup'}
    require({k for k in S if S[k] != X[k]} <= allowed and set(S) == set(X), 'only declared sections change')
    require(X['warps'] == S['warps'] and X['helper_final'] == S['helper_final'] and X['removed'] == S['removed'] and X['prelude_events'] == S['prelude_events'], 'phase and buffer ABI unchanged')
    # ---- A: expected edits, derived independently
    expectedA = [dict(g) if False else g for g in S['A']]
    ins = {}      # source position -> gates inserted before it (exact order not required within a position)
    seq = list(S['A'])
    added = []; groups = []; removed_old = []; entries = []
    for Q in QUARTETS:
        e = expected_gates(S, Q['q'], Q['holder'])
        for pos, gs in e['kernel'].items():
            ins.setdefault(pos, []).extend(gs); added += gs
        entries.append((e['entry'], e['i0'], Q['q'][0], Q['holder'])); added.append(e['entry'])
        pi, op, tq, car = Q['preload_old']
        require(S['A'][pi][:3] == [op, tq, car] and S['A'][pi][3:] == [1, 1, []], ('old preload gate', pi))
        seq[pi] = Q['preload_new']; removed_old.append(S['A'][pi]); added.append(Q['preload_new'])
        ui, ug = Q['undo_after']
        require(S['A'][ui][1] != ug[1] and S['A'][ui][2] == ug[2] and S['A'][ui][3:] == [1, 1, []], ('undo follows its carrier preload', ui))
        ins.setdefault(ui + 1, []).append(ug); added.append(ug)
        groups.append(dict(group=list(Q['q']), holder=Q['holder'], entry_frame=e['L'], source_pair_positions=e['i0']))
    # walk the candidate against the sequence with replacements
    actual = {}; j = 0
    for g in X['A']:
        if j < len(seq) and g == seq[j]:
            j += 1
        else:
            actual.setdefault(j, []).append(g)
    require(j == len(seq), 'candidate A is the source A with the replacements and only the declared insertions')
    enc = lambda g: json.dumps(g, separators=(',', ':'))
    # a delivery entry may sit anywhere at or before its register's staged pair gate, as long as no
    # gate between it and that pair gate touches the raised register or the carrier holder (so it commutes to the canonical slot)
    for entry, i0, q0, holder in entries:
        where = [p for p, gs in actual.items() if entry in gs]
        require(len(where) == 1 and actual[where[0]].count(entry) == 1 and where[0] <= i0, ('entry placement', entry))
        require(not any(q0 in regs(g) or holder in regs(g) for g in S['A'][where[0]:i0]), ('entry commutes to its staged slot', entry))
        actual[where[0]].remove(entry)
        if not actual[where[0]]: del actual[where[0]]
    require(set(actual) == set(ins), ('insertion positions', sorted(actual), sorted(ins)))
    for pos in actual:
        require(Counter(map(enc, actual[pos])) == Counter(map(enc, ins[pos])), ('inserted gates at', pos))
    # entry is placed at or before q0's staged pair gate and never moved relative to the declared positions
    n_ins = sum(map(len, actual.values())) + len(entries)
    require(n_ins == 14 and len(X['A']) == len(S['A']) + 14, 'fourteen inserted and two replaced A gates')
    require(Counter(map(enc, added)) == Counter(map(enc, [g for gs in actual.values() for g in gs] + [e[0] for e in entries] + [Q['preload_new'] for Q in QUARTETS])), 'declared gate census')
    # ---- B: exactly the two carrier raises, each a one-dimensional frame extension containing the entry line
    bdiff = [i for i, (a, b) in enumerate(zip(S['B'], X['B'])) if a != b]
    require(len(S['B']) == len(X['B']) and len(bdiff) == 2, 'exactly two B gates change')
    for i in bdiff:
        a, b = S['B'][i], X['B'][i]
        h = [Q['holder'] for Q in QUARTETS if a[1] == Q['holder']]
        require(h and a[:5] == b[:5] and a[0] == 'add', 'raise keeps registers/coefficient')
        first = [k for k, g in enumerate(S['B']) if g[0] == 'add' and g[1] == a[1] and g[-1]][0]
        require(first == i, 'carrier is raised at its first nonzero B gate')
        fa, fb = basis(a[-1]), basis(b[-1])
        L = [e['L'] for e in [expected_gates(S, Q['q'], Q['holder']) for Q in QUARTETS if Q['holder'] == a[1]]][0]
        require(basis(list(fa) + list(fb)) == fb and len(fb) == len(fa) + 1 and basis(list(fb) + L) == fb, 'one-dimensional raise by the entry line')
    # ---- compensation: same length, zero-frame helper additions only
    cdiff = [i for i, (a, b) in enumerate(zip(S['compensation'], X['compensation'])) if a != b]
    require(len(S['compensation']) == len(X['compensation']) and len(cdiff) == len(P['compensation_edits']) and all(S['compensation'][i][0] == 'add' == X['compensation'][i][0] and X['compensation'][i][-1] == [] and S['compensation'][i][-1] == [] for i in cdiff), 'zero-frame compensation rewrite of declared size')
    require(not any(e[2] in (457, 458) for e in X['compensation']) or True, 'informational')
    newstart = dict(S['start_extra'])
    for g in groups: newstart[str(g['group'][0])] = g['entry_frame']
    require(X['start_extra'] == newstart, 'start_extra gains exactly the two entry lines')
    require(X['report']['local_profile'] == {'1': 2404, '2': 642, '3': 262, '4': 128, '5': 26, '8': 8}, 'complete paid profile')
    require(X['report']['width_inventory'] == {'4': 26, '5': 2, '7': 62, '8': 86, '9': 232}, 'complete helper inventory')
    # ---- positive audit
    cpath = protected['candidate_' + variant]
    pos_json = OUT / f'POSITIVE-AUDIT-{variant}.json'
    run = subprocess.run([sys.executable, '-B', str(ROOT / 'audit_local.py'), '--word', str(cpath), '--output', str(pos_json)], text=True, capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    (OUT / f'POSITIVE-AUDIT-{variant}.log').write_text(run.stdout + run.stderr, encoding='utf-8', newline='\n')
    require(run.returncode == 0, ('positive candidate audit', variant, run.stdout[-400:], run.stderr[-400:]))
    pr = json.loads(pos_json.read_text())
    require(pr.get('status') == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD', 'positive auditor status')
    # ---- controls
    def find(m, g):
        h = [i for i, x in enumerate(m['A']) if x == g]
        require(len(h) == 1, ('unique gate', g)); return h[0]
    ENTRY = [g for g in added if g[1] in (457, 458) and g[2] in (499, 510)]
    def drop_helper_entry(m): m['A'].pop(find(m, ['add', 464, 458, -1, 1, [42]]))
    def drop_entry_gate(m): m['A'].pop(find(m, ENTRY[0]))
    def flip_sign(m): m['A'][find(m, ['add', 466, 457, -1, 1, [42]])][3] = 1
    def flip_partner_sign(m): m['A'][find(m, ['add', 456, 475, 1, 1, [82, 42]])][3] = -1
    def no_raise(m):
        i = [i for i, g in enumerate(m['B']) if g == X['B'][bdiff[0]]][0]; m['B'][i] = copy.deepcopy(S['B'][bdiff[0]])
    def no_raise_b(m):
        i = [i for i, g in enumerate(m['B']) if g == X['B'][bdiff[1]]][0]; m['B'][i] = copy.deepcopy(S['B'][bdiff[1]])
    def moved_back(m): m['A'][find(m, ['add', 456, 498, -1, 1, []])] = ['add', 457, 498, 1, 1, []]
    def moved_back_b(m): m['A'][find(m, ['add', 459, 510, -1, 1, []])] = ['add', 458, 510, 1, 1, []]
    def undo_removed(m): m['A'].pop(find(m, ['add', 467, 500, -1, 1, []]))
    def wrong_start(m): m['start_extra']['457'] = [75]
    def wrong_comp(m): m['compensation'][cdiff[0]][3] *= -1
    def stale_cleanup(m): m['cleanup'] = copy.deepcopy(S['cleanup'])
    cases = [('dropped_quartet_helper_entry', drop_helper_entry, 'endpoint', True), ('dropped_entry_delivery', drop_entry_gate, 'endpoint', True),
             ('flipped_sign', flip_sign, 'endpoint', True), ('flipped_partner_sign', flip_partner_sign, 'endpoint', True),
             ('missing_carrier_raise', no_raise, 'frame', True), ('missing_carrier_raise_second', no_raise_b, 'frame', True),
             ('preload_gate_moved_back', moved_back, 'frame', True), ('preload_gate_moved_back_second', moved_back_b, 'frame', True),
             ('preload_undo_removed', undo_removed, 'endpoint', True), ('wrong_start_extra', wrong_start, 'frame', True),
             ('wrong_compensation_sign', wrong_comp, 'endpoint', True), ('stale_cleanup', stale_cleanup, 'cleanup', False)]
    controls = []
    for name, mut, kind, rd in cases:
        m = copy.deepcopy(X); mut(m)
        if rd: m['cleanup'] = rederive(m)
        mp = OUT / f'control-{variant}-{name}.json.gz'
        mp.write_bytes(gzip.compress(json.dumps(m, separators=(',', ':')).encode(), mtime=0))
        res = subprocess.run([sys.executable, '-B', str(ROOT / 'audit_local.py'), '--word', str(mp), '--output', str(OUT / f'control-{variant}-{name}-audit.json')], text=True, capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        log = res.stdout + res.stderr
        (OUT / f'control-{variant}-{name}.log').write_text(log, encoding='utf-8', newline='\n')
        require(res.returncode != 0, ('control not rejected', name))
        reason = next((z for z in reversed(log.splitlines()) if z.startswith('RuntimeError:')), log.splitlines()[-1])
        if kind == 'frame':
            require('frame' in reason, (name, reason))
        elif kind == 'cleanup':
            require('cleanup' in reason, (name, reason))
        else:
            require('target map failed' in reason or 'all-column endpoint failure' in reason or 'paid profile mismatch' in reason, (name, reason))
        controls.append({'name': name, 'cleanup_rederived': rd, 'expected_failure_kind': kind, 'rejected_for': reason})
    receipt['variants'][variant] = {'source_canonical_sha256': canon(S), 'candidate_canonical_sha256': canon(X), 'candidate_file_sha256': sha(cpath),
        'positive_audit': {'status': pr['status'], 'checked_columns': pr['checked_columns'], 'orientations': pr['orientations'], 'receipt_sha256': sha(pos_json)},
        'groups': groups, 'inserted_A_gates': n_ins, 'replaced_A_gates': 2, 'carrier_raises': 2, 'compensation_rewrites': len(cdiff), 'controls': controls}
after = {k: sha(ROOT / f) for k, (f, h) in PINS.items()}; after.update({k: sha(p) for k, p in protected.items()})
require(after == before and tree_snapshot(ROOT) == tree_before, 'source, dependency or candidate bytes changed during review')
receipt['source_authentication'] = {'pins': {k: h for k, (f, h) in PINS.items()}, 'all_protected_files_unchanged': True, 'source_tree_files': len(tree_before), 'reviewer_sha256': sha(Path(__file__).resolve())}
(OUT / 'PRELOAD-MOVE-INDEPENDENT-REVIEW.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'status': receipt['status'], 'variants': {k: {'inserted_A_gates': v['inserted_A_gates'], 'controls': [(c['name'], c['rejected_for']) for c in v['controls']]} for k, v in receipt['variants'].items()}}, indent=1))
