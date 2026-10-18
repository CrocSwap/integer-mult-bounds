# SPDX-License-Identifier: Apache-2.0
"""Independent four-kernel review and semantic fault controls.

Contribution: Yiyang Lu (@Lyy-iiis), with substantial OpenAI Codex assistance,
including separate analysis and review agents. Retains Jeremy Kothe's PR2833
source construction and credited PR2802/earlier lineage. This reviewer does not
import the construction producer. Source cleanup and auditor dependencies are
SHA256-authenticated before execution. All output is confined to a fresh external
directory; input bytes and the source directory tree are checked unchanged.
"""

def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)

import os, sys, json, gzip, copy, hashlib, subprocess
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import argparse, importlib.util
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-dir', type=Path, required=True, help='Pinned PR2833 new/borrow directory containing audit_local.py and word_patch.py')
parser.add_argument('--source-base', type=Path, required=True, help='Original pinned PR2833 base word, before overlay')
parser.add_argument('--source-extra', type=Path, required=True, help='Original pinned PR2833 extra word, before overlay')
parser.add_argument('--candidate-base', type=Path, required=True)
parser.add_argument('--candidate-extra', type=Path, required=True)
parser.add_argument('--out-dir', type=Path, required=True, help='Fresh external directory; must not already exist or be inside source-dir')
args = parser.parse_args()
ROOT = args.source_dir.resolve()
OUT = args.out_dir.resolve()
sources = {'base': args.source_base.resolve(), 'extra': args.source_extra.resolve()}
candidates = {'base': args.candidate_base.resolve(), 'extra': args.candidate_extra.resolve()}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def tree_snapshot(root):
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}

def manifest_sha(manifest):
    return hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
require(not OUT.exists(), 'out-dir must be fresh')
require(OUT != ROOT and ROOT not in OUT.parents and (OUT not in ROOT.parents), 'out-dir must be external to source-dir')
protected = {'source_base': sources['base'], 'source_extra': sources['extra'], 'word_patch': ROOT / 'word_patch.py', 'audit_local': ROOT / 'audit_local.py', 'candidate_base': candidates['base'], 'candidate_extra': candidates['extra']}
pins = {'source_base': 'dda9878455b3a3bec64ca16b1ac7789bbf5ffb603d5713b8df8644485e85b1b7', 'source_extra': 'bbe6bcba59e45e827a8e932ee4b23650d56ed4a0b8e0875c14f23c36b9e47eac', 'word_patch': '9b3287f189c4f29c1a8bdb1ba01fdcfe14a57d87b50fa4f2f646fb2346ab01ce', 'audit_local': 'a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90'}
before = {k: sha(p) for k, p in protected.items()}
for key, digest in pins.items():
    require(before[key] == digest, ('pinned source mismatch', key, before[key], digest))
source_tree_before = tree_snapshot(ROOT)
OUT.mkdir(parents=True)
spec = importlib.util.spec_from_file_location('_authenticated_pr2833_cleanup', ROOT / 'word_patch.py')
require(spec is not None and spec.loader is not None, 'cannot load pinned cleanup helper')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
derive_cleanup = module.derive_cleanup
restored_of = module.restored_of
GROUPS = [(478, 479, 490, 491), (460, 461, 468, 469), (462, 463, 470, 471), (480, 481, 492, 493)]

def regs(g):
    return g[1:3] if g[0] == 'add' else g[1:2]

def enc(g):
    return json.dumps(g, separators=(',', ':'))

def add(a, b, c):
    for k, v in b.items():
        z = a.get(k, F(0)) + c * v
        if z:
            a[k] = z
        else:
            a.pop(k, None)

def columns(gs):
    out = {}
    for g in gs:
        require(g[0] == 'add', "check failed: g[0] == 'add'")
        a = out.setdefault(g[2], {})
        z = a.get(g[1], F(0)) + F(g[3], g[4])
        if z:
            a[g[1]] = z
        else:
            a.pop(g[1], None)
    return out
receipt = {'status': 'PASS_INDEPENDENT_FOUR_GROUP_REVIEW', 'variants': {}}
for variant in ('base', 'extra'):
    source = sources[variant]
    path = candidates[variant]
    w = json.load(gzip.open(source))
    x = json.load(gzip.open(path))
    oldA = w['A']
    newA = x['A']
    expected = {}
    all_support = set()
    all_targets = set()
    groups = []
    changes = {}
    newstart = dict(w['start_extra'])
    oldC = columns(w['compensation'])
    expectedC = copy.deepcopy(oldC)
    for q, p, r, t in GROUPS:
        info = {}
        for h in (q, p, r, t):
            touches = [(i, g) for i, g in enumerate(oldA) if h in regs(g)]
            require(len(touches) == 1, 'check failed: len(touches) == 1')
            i, g = touches[0]
            require(g[0] == 'add' and g[1] == h, "check failed: g[0] == 'add' and g[1] == h")
            a = g[2]
            require(not any((e[1] == a for e in oldA)), 'check failed: not any((e[1] == a for e in oldA))')
            info[h] = (i, a, F(g[3], g[4]), g[-1])
        i0, a0, c0, E = info[q]
        i1, a1, c1, E1 = info[p]
        i2, a2, c2, G = info[r]
        i3, a3, c3, G1 = info[t]
        require(E == E1 and G == G1, 'check failed: E == E1 and G == G1')

        def span(U):
            s = {0}
            for z in U:
                s |= {z ^ v for v in list(s)}
            return s
        line = list((span(E) & span(G)) - {0})
        require(len(line) == 1, 'check failed: len(line) == 1')
        mk = lambda d, s, c, U: ['add', d, s, c.numerator, c.denominator, U]
        ops = [(min(i0, i2), mk(r, q, F(-1), line)), (max(i0, i1) + 1, mk(p, q, F(1), E)), (max(i0, i1) + 1, mk(p, a0, -c0, E)), (max(i2, i3) + 1, mk(t, r, F(1), G)), (max(i2, i3) + 1, mk(t, a2, -c2, G))]
        for pos, g in ops:
            expected.setdefault(pos, []).append(g)
        support = set((q, p, r, t, a0, a1, a2, a3))
        require(len(support) == 8 and (not support & all_support), 'check failed: len(support) == 8 and (not support & all_support)')
        all_support |= support
        targets = set().union(*(set(oldC[h]) for h in (q, p, r, t)))
        require(not targets & all_targets, 'check failed: not targets & all_targets')
        all_targets |= targets
        z = {}
        for h, c in ((q, 1), (p, 1), (r, -1), (t, -1)):
            add(z, oldC[h], F(c))
        require(not z, 'check failed: not z')
        rows = {h: {h: F(1)} for h in support}
        sched = {}
        for h, (i, a, c, U) in info.items():
            sched.setdefault(i, []).append(mk(h, a, c, U))
        for pos in sorted(set(sched) | {p for p, g in ops}):
            for pp, g in ops:
                if pp == pos:
                    add(rows[g[1]], rows[g[2]], F(g[3], g[4]))
            for g in sched.get(pos, []):
                add(rows[g[1]], rows[g[2]], F(g[3], g[4]))
        H = {h: {h: F(1)} for h in support}
        add(H[p], {q: F(1)}, F(1))
        add(H[r], {q: F(1)}, F(-1))
        add(H[t], {r: F(1), q: F(-1)}, F(1))
        for h, (i, a, c, U) in info.items():
            add(H[h], {a: F(1)}, c)
        require(rows == H, 'check failed: rows == H')
        expectedC[q] = {}
        add(expectedC[r], oldC[t], F(1))
        newstart[str(q)] = line
        groups.append({'helpers': [q, p, r, t], 'source_A_positions': {str(h): info[h][0] for h in info}, 'partners': {str(h): info[h][1] for h in info}, 'raw_dirt_map': {str(p): f'd{p}+d{q}', str(r): f'd{r}-d{q}', str(t): f'd{t}+d{r}-d{q}'}, 'target_support': sorted(targets), 'operand_support': sorted(support)})
    actual = {}
    j = 0
    for g in newA:
        if j < len(oldA) and g == oldA[j]:
            j += 1
        else:
            actual.setdefault(j, []).append(g)
    require(j == len(oldA) and sum(map(len, actual.values())) == 20, 'check failed: j == len(oldA) and sum(map(len, actual.values())) == 20')
    require(set(actual) == set(expected), 'check failed: set(actual) == set(expected)')
    for pos in actual:
        require(Counter(map(enc, actual[pos])) == Counter(map(enc, expected[pos])), 'check failed: Counter(map(enc, actual[pos])) == Counter(map(enc, expected[pos]))')
    require(x['start_extra'] == newstart, "check failed: x['start_extra'] == newstart")
    gotC = columns(x['compensation'])
    require({k: v for k, v in gotC.items() if v} == {k: v for k, v in expectedC.items() if v}, 'check failed: {k: v for k, v in gotC.items() if v} == {k: v for k, v in expectedC.items() if v}')
    removed = [g for g in w['compensation'] if g[2] in {q for q, p, r, t in GROUPS}]
    retained = [g for g in w['compensation'] if g[2] not in {q for q, p, r, t in GROUPS}]
    require(len(removed) == 28 and x['compensation'][:len(retained)] == retained and (len(x['compensation']) - len(retained) == 28), "check failed: len(removed) == 28 and x['compensation'][:len(retained)] == retained and (len(x['compensation']) - len(retained) == 28)")
    allowed = {'A', 'compensation', 'start_extra', 'report', 'cleanup'}
    require({k for k in w if w[k] != x[k]} <= allowed, 'check failed: {k for k in w if w[k] != x[k]} <= allowed')
    require(x['report']['local_profile'] == {'1': 2394, '2': 642, '3': 266, '4': 128, '5': 26, '8': 8}, "check failed: x['report']['local_profile'] == {'1': 2394, '2': 642, '3': 266, '4': 128, '5': 26, '8': 8}")
    require(x['report']['width_inventory'] == {'4': 26, '5': 2, '7': 62, '8': 84, '9': 234}, "check failed: x['report']['width_inventory'] == {'4': 26, '5': 2, '7': 62, '8': 84, '9': 234}")
    positive_path = OUT / f'POSITIVE-AUDIT-{variant}.json'
    positive_cmd = [sys.executable, '-B', str(ROOT / 'audit_local.py'), '--word', str(path), '--output', str(positive_path)]
    positive_run = subprocess.run(positive_cmd, text=True, capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    (OUT / f'POSITIVE-AUDIT-{variant}.log').write_text(positive_run.stdout + positive_run.stderr)
    require(positive_run.returncode == 0, ('positive candidate audit failed', variant, positive_run.stdout, positive_run.stderr))
    positive_receipt = json.loads(positive_path.read_text())
    require(positive_receipt.get('status') == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD', 'positive auditor status mismatch')
    controls = []

    def remove_exact(m, needle):
        hits = [i for i, g in enumerate(m['A']) if g == needle]
        require(len(hits) == 1, 'check failed: len(hits) == 1')
        m['A'].pop(hits[0])

    def drop_primary(m):
        remove_exact(m, ['add', 479, 478, 1, 1, [75, 25]])

    def drop_partner(m):
        remove_exact(m, ['add', 479, 526, 1, 1, [75, 25]])

    def flip_cross(m):
        needle = ['add', 468, 460, -1, 1, [7]]
        hits = [i for i, g in enumerate(m['A']) if g == needle]
        require(len(hits) == 1, 'check failed: len(hits) == 1')
        m['A'][hits[0]][3] = 1

    def omit_comp(m):
        m['compensation'] = copy.deepcopy(retained)

    def wrong_comp(m):
        m['compensation'][len(retained)][3] *= -1

    def wrong_start(m):
        m['start_extra']['478'] = [75]

    def suppress_without_transport(m):
        m['A'] = copy.deepcopy(w['A'])
        m['compensation'] = copy.deepcopy(retained)
        m['report']['local_profile'] = dict(w['report']['local_profile'])
        m['report']['local_profile']['1'] += 4
        m['report']['local_profile']['2'] -= 4

    def stale_cleanup(m):
        m['cleanup'] = copy.deepcopy(w['cleanup'])
    cases = [('wrong_kernel_sign', flip_cross, 'endpoint', True), ('drop_primary_A_injection', drop_primary, 'endpoint', True), ('missing_raw_dirt_reconstruction', drop_partner, 'endpoint', True), ('missing_compensation_regeneration', omit_comp, 'endpoint', True), ('wrong_compensation_sign', wrong_comp, 'endpoint', True), ('wrong_start_extra', wrong_start, 'frame', True), ('suppressed_compensation_without_transport', suppress_without_transport, 'endpoint', True), ('stale_cleanup', stale_cleanup, 'cleanup', False)]
    for name, mut, expected_kind, rederive in cases:
        m = copy.deepcopy(x)
        mut(m)
        if rederive:
            t = copy.deepcopy(m)
            t['A'] = t['A'][t['prelude_events']:]
            m['cleanup'] = derive_cleanup(t, restored_of(m))
        mp = OUT / f'control-{variant}-{name}.json.gz'
        mp.write_bytes(gzip.compress(json.dumps(m, separators=(',', ':')).encode(), mtime=0))
        ap = OUT / f'control-{variant}-{name}-audit.json'
        cmd = [sys.executable, '-B', str(ROOT / 'audit_local.py'), '--word', str(mp), '--output', str(ap)]
        res = subprocess.run(cmd, text=True, capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        log = res.stdout + res.stderr
        (OUT / f'control-{variant}-{name}.log').write_text(log)
        require(res.returncode != 0, (name, log))
        reason = next((z for z in reversed(log.splitlines()) if z.startswith('RuntimeError:')), log.splitlines()[-1])
        if expected_kind == 'endpoint':
            require('frames/profile PASS' in log and ('target map failed' in reason or 'all-column endpoint failure' in reason), (name, log))
        elif expected_kind == 'frame':
            require('frame' in reason, (name, log))
        else:
            require('cleanup' in reason, (name, log))
        controls.append({'name': name, 'cleanup_rederived': rederive, 'expected_failure_kind': expected_kind, 'frames_profile_pass': 'frames/profile PASS' in log, 'rejected_for': reason})
    receipt['variants'][variant] = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'candidate_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'positive_audit': {'status': positive_receipt['status'], 'checked_columns': positive_receipt['checked_columns'], 'orientations': positive_receipt['orientations'], 'receipt_sha256': sha(positive_path)}, 'inserted_A_gates': 20, 'compensation_removed': 28, 'compensation_added': 28, 'groups': groups, 'all_four_operand_and_target_supports_disjoint': True, 'all_other_sections_unchanged': True, 'controls': controls}
after = {k: sha(p) for k, p in protected.items()}
source_tree_after = tree_snapshot(ROOT)
require(after == before, 'source, dependency or candidate bytes changed during review')
require(source_tree_after == source_tree_before, 'source-dir tree changed during review')
receipt['source_authentication'] = {'pins': pins, 'before': before, 'after': after, 'all_protected_files_unchanged': True, 'source_tree_before_sha256': manifest_sha(source_tree_before), 'source_tree_after_sha256': manifest_sha(source_tree_after), 'source_tree_files': len(source_tree_before), 'source_tree_unchanged': True, 'reviewer_sha256': sha(Path(__file__).resolve())}
(OUT / 'FOUR-GROUP-INDEPENDENT-REVIEW.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'variants': {k: {'inserted_A_gates': v['inserted_A_gates'], 'compensation_removed': v['compensation_removed'], 'compensation_added': v['compensation_added'], 'controls': v['controls']} for k, v in receipt['variants'].items()}}, indent=2))
