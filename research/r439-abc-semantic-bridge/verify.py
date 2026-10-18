#!/usr/bin/env python3
"""Independent application of PR1194's bridge to PR1122. Apache-2.0.
Arham Tahir, with substantial OpenAI Codex assistance.
No candidate producer or predecessor semantic verifier is imported.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
PARENT = 'research/r439-bsection-stars-seed01/candidate.json.gz'
CHECKER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
CANDIDATE_SHA = '2b09a7a3851cdf2a7f19350d1555cf75788d001c9507a37e459cd931881ee066'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def load_word(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def source_check():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    inputs = {f['path']: f for f in manifest['files'] if f['usage'] == 'input'}
    require(set(inputs) == {OLD, PARENT, CHECKER}, 'input inventory')
    for name, pin in inputs.items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin['sha256'], 'source pin: ' + name)
    require(hashlib.sha256((HERE / 'inputs/candidate.json.gz').read_bytes()).hexdigest() == CANDIDATE_SHA, 'candidate pin')


def matrix(word, sections):
    """Sets of input columns; simultaneous donors, independent of owner bitmasks."""
    n = 2 * word['v'] + word['R']
    rows = [{i} for i in range(n)]
    for section in sections:
        if section == 'scatter':
            gates = [(word['v'] + t, [word['ret'][j] for j in uses]) for t, uses in enumerate(word[section])]
        else:
            gates = [(d, donors) for _, d, donors in word[section]]
        for d, donors in gates:
            delta = set()
            for s in donors:
                delta.symmetric_difference_update(rows[s])
            rows[d].symmetric_difference_update(delta)
    return rows


def compensation(word):
    v, n = word['v'], 2 * word['v'] + word['R']
    zeros = [i for i, frame in enumerate(word['frames']) if not frame]
    require(len(zeros) == 1, 'unique zero frame')
    zero = zeros[0]
    require(all(word['start'][r] == zero for r in range(v, n)), 'entry frame')
    for f, d, donors in word['D']:
        require(type(f) is int and f == zero, 'zero-frame gate')
        require(type(d) is int and v <= d < n and type(donors) is list and donors, 'D operand')
        require(all(type(s) is int and v <= s < n for s in donors), 'D operand')
        require(len(set([d] + donors)) == len(donors) + 1, 'distinct D operands')
        require(d < 2 * v or all(s >= 2 * v for s in donors), 'H1 feedback')
    rows = matrix(word, ['D'])
    result = []
    for r, row in enumerate(rows):
        delta = row ^ {r}
        if v <= r < 2 * v:
            require(all(2 * v <= j < n for j in delta), 'target basis/source response')
            result.append(sorted(j - 2 * v for j in delta))
        else:
            require(not delta, 'source/helper restoration')
    return result


def boundary(word):
    N = compensation(word)
    v, n = word['v'], 2 * word['v'] + word['R']
    raw = matrix(word, ['A', 'scatter', 'B'])
    for r in range(n):
        if not v <= r < 2 * v:
            require(not any(v <= j < 2 * v for j in raw[r]), 'raw U block')
    for t in range(v):
        row = raw[v + t]
        require({j for j in row if v <= j < 2 * v} == {v + t}, 'raw V identity')
        require({j for j in row if j < v} == {t}, 'raw J identity')
        require(sorted(j - 2 * v for j in row if j >= 2 * v) == N[t], 'raw K compensation')
    return N


def local_bill(word, owner):
    n = 2 * word['v'] + word['R']
    paths = [[f] for f in word['start']]
    events = []
    copy_ranks = []
    for phase in ['D', 'A', 'scatter', 'B', 'C']:
        if phase == 'scatter':
            for j, center in enumerate(word['ret']):
                copy_ranks.append(owner.fdim[paths[center][-1]])
                events.append(('copy', n, center))
                events.extend(('add', word['v'] + t, n) for t, uses in enumerate(word['scatter']) if j in uses)
                events.append(('erase', n, center))
            continue
        for f, d, donors in word[phase]:
            for r in [d] + donors:
                if paths[r][-1] != f:
                    require(owner.nested(paths[r][-1], f) and owner.fdim[f] > owner.fdim[paths[r][-1]], 'frame climb')
                    paths[r].append(f)
            events.extend(('add', d, s) for s in donors)
    for r, f in enumerate(word['final']):
        if paths[r][-1] != f:
            require(owner.nested(paths[r][-1], f) and owner.fdim[f] > owner.fdim[paths[r][-1]], 'final climb')
            paths[r].append(f)
    counts = Counter(copy_ranks)
    for path in paths:
        counts.update(owner.fdim[b] - owner.fdim[a] for a, b in zip(path, path[1:]))
    peaks = []
    expected = [{r} ^ ({r - word['v']} if word['v'] <= r < 2 * word['v'] else set()) for r in range(n)]
    for backward in [False, True]:
        rows = [{r} for r in range(n)] + [set()]
        sizes = [1] * n + [0]
        opened, peak = False, 1
        for kind, d, s in reversed(events) if backward else events:
            if backward and kind != 'add':
                kind = 'erase' if kind == 'copy' else 'copy'
            if kind == 'add':
                require(s != n or opened, 'read outside copy lifetime')
                rows[d] ^= rows[s]
                sizes[d] += sizes[s]
            elif kind == 'copy':
                require(not opened and not rows[d], 'copy overlap')
                rows[d], sizes[d], opened = rows[s].copy(), sizes[s], True
            else:
                require(opened and rows[d] == rows[s], 'erase boundary')
                rows[d], sizes[d], opened = set(), 0, False
            peak = max(peak, sizes[d])
        require(not opened and rows[:-1] == expected, 'complete dirty boundary')
        peaks.append(peak)
    F, B = peaks
    local, nine = 64 * F**3 * B**2, 2**18 * F**5 * B**4
    require(local < 2**104 and nine < 2**192, 'precision cap')
    return {'ADDs': sum(k == 'add' for k, _, _ in events), 'D_ADDs': sum(len(g[2]) for g in word['D']),
            'COPY': len(copy_ranks), 'ERASE': len(copy_ranks), 'copy_ranks': copy_ranks,
            'profile': dict(sorted(counts.items())), 'rank_mass': sum(r*c for r,c in counts.items()),
            'F': F, 'B': B, 'local_bound': str(local), 'nine_bound': str(nine),
            'local_bits': local.bit_length(), 'nine_bits': nine.bit_length(),
            'frame_paths_sha256': hashlib.sha256(canonical(paths).encode()).hexdigest()}


def controls(word, N, owner, old):
    failures = []
    v, h = word['v'], 2 * word['v']
    zero = next(i for i, f in enumerate(word['frames']) if not f)
    def reject(name, gate, reason, phase='D', twice=False):
        mutant = copy.deepcopy(word)
        mutant[phase].extend([gate] * (2 if twice else 1))
        try:
            boundary(mutant)
        except ValueError as error:
            require(reason in str(error), 'wrong rejection: ' + name)
            failures.append(name)
        else:
            raise ValueError('accepted control: ' + name)
    reject('unrestored helper', [zero, h, [h+1]], 'restoration')
    reject('target basis changed', [zero, v, [v+1]], 'target basis')
    reject('wrong dirty compensation', [zero, v, [h]], 'raw K')
    reject('neutral target feedback', [zero, h, [v]], 'H1', twice=True)
    reject('neutral source access', [zero, v, [0]], 'D operand', twice=True)
    reject('neutral nonzero frame', [word['final'][h], v, [h]], 'zero-frame', twice=True)
    reject('raw source response changed', [zero, v, [0]], 'raw J', phase='B')
    reject('raw target response changed', [zero, v, [v+1]], 'raw V', phase='B')
    # A semantically equivalent cleanup still need not satisfy the inherited bridge.
    bad = copy.deepcopy(word)
    bad['C'] = copy.deepcopy(old['C'])
    require(boundary(bad) == N, 'D/raw boundary unchanged with stale cleanup')
    current = copy.copy(owner)
    current.w = bad
    current.full()
    hypotheses, _, _ = current.interface()
    require(not hypotheses['H4_C_literal_reverse_at_full'], 'stale cleanup must fail H4')
    failures.append('semantically equivalent stale cleanup violates H4')
    good = copy.deepcopy(word)
    good['D'] += [[zero, h, [h+1]], [zero, h, [h+1]]]
    require(boundary(good) == N, 'neutral helper positive control')
    return failures


def compute():
    source_check()
    old, parent = load_word(ROOT / OLD), load_word(ROOT / PARENT)
    word = load_word(HERE / 'inputs/candidate.json.gz')
    require(set(word) == set(old), 'word fields')
    require(all(word[k] == old[k] for k in old if k not in ['A','B','C','D']), 'fixed geometry')
    require(word['A'] != parent['A'] and word['D'] == parent['D'], 'changed A, same parent D')
    N = boundary(word)
    require(N == compensation(parent) == compensation(old), 'predecessor compensation equality')
    spec = importlib.util.spec_from_file_location('pinned_owner', ROOT / CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    owner = mod.Word(old)
    labels = owner.labels()
    reports, bills = {}, {}
    bridge = copy.deepcopy(word)
    bridge['D'] = old['D']
    for label, w in [('baseline', old), ('candidate', word), ('virtual_bridge', bridge)]:
        current = copy.copy(owner)
        current.w = w
        full = current.full()
        hyp, conclusion, _ = current.interface()
        failed = [key for key, value in {**hyp, **conclusion}.items() if not value]
        require(failed == (['H2_D_frame0_targets_from_helpers','K_equals_D'] if label == 'candidate' else []), 'owner flags: ' + label)
        reports[label] = {'hypotheses': hyp, 'conclusions': conclusion, 'columns': full['columns']}
        if label != 'virtual_bridge':
            bills[label] = local_bill(w, current)
    for key in ['profile','rank_mass','copy_ranks','COPY','ERASE','frame_paths_sha256']:
        require(bills['candidate'][key] == bills['baseline'][key], 'paid interface: ' + key)
    require(bills['candidate']['ADDs'] == 10652, 'candidate ADD bill')
    require(boundary(bridge) == N, 'virtual bridge compensation')
    return {'status': 'PASS_R439_ABC_SEMANTIC_BRIDGE', 'candidate_sha256': CANDIDATE_SHA,
            'compensation_rows_hex': [hex(sum(1 << j for j in row)) for row in N], 'labels': labels, 'owner': reports, 'bills': bills,
            'negative_controls': controls(word, N, owner, old), 'positive_control': 'restored neutral helper pair',
            'native_replayed': False, 'hosted_admission': False, 'new_kappa': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = compute()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2) + '\n')
    else:
        require(canonical(result) == canonical(json.loads(path.read_text())), 'receipt mismatch')
    print(result['status'], 'columns=661 ADDs=10652 controls=9 no_new_kappa')


if __name__ == '__main__':
    main()
