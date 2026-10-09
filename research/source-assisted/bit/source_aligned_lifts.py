#!/usr/bin/env python3
"""Export exact low-frame lifts for SOURCE_ALIGNED_BIT_WORD.txt.

Author: GPT-6 Astra. Source: eumemic PR168 @
fd25adb7fbaa12ee761d02c733c54d1d2a7687ee, with its existing credits.
The certificate is compact: complete elementary templates, exact instance
counts/hashes, and one representative per template. --instances optionally
exports every physical phase/frame instance for a downstream word emitter.
"""
from collections import Counter, defaultdict
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE.parent / 'public' / 'pr168_fd25adb7'
COMMIT = 'fd25adb7fbaa12ee761d02c733c54d1d2a7687ee'


def apply(word, values):
    values = list(values)
    for operation, a, b in word:
        if operation == 'xor':
            values[a] ^= values[b]
        else:
            assert operation == 'swap'
            values[a], values[b] = values[b], values[a]
    return values


def template(kind, t):
    assert t >= 1
    if kind == 'source_pair':
        n = t + 2
        word = [('xor', j, control) for j in range(t) for control in (t, t+1)]
        fresh = [0] * t + [1, 2]
        expected = [3] * t + [1, 2]
        auxiliary_block_size = t
    else:
        assert kind == 'pair_sum'
        n = t + 1
        word = [('xor', j, control) for j in range(2, n) for control in (0, 1)]
        word.append(('xor', 0, 1))
        word.extend(('swap', j, j+1) for j in range(1, t))
        fresh = [1, 2] + [0] * (t-1)
        expected = [3] * t + [2]
        auxiliary_block_size = n
    identity = [1 << j for j in range(n)]
    matrix = apply(word, identity)
    assert apply(word, fresh) == expected
    assert apply(list(reversed(word)), matrix) == identity
    assert apply(word, apply(list(reversed(word)), identity)) == identity
    if kind == 'source_pair':
        assert matrix[-2:] == identity[-2:]
        assert [row & ((1 << t)-1) for row in matrix[:t]] == identity[:t]
    return dict(kind=kind, requested_outputs=t, dimension=n,
                auxiliary_block_size=auxiliary_block_size,
                matrix_rows=matrix, forward=word, inverse=list(reversed(word)),
                fresh_input=fresh, fresh_output=expected,
                exact_two_sided_inverse=True)


def extract(source):
    sys.path.insert(0, str(source / 'scripts'))
    import paired_cube_bit_physical as P
    from check_paired_cube_bit import reduce_rows
    chk = P.loaded()
    g, w, h = chk.g, chk.w, chk.h
    frame = chk.fr['frames']
    dims = {int(f): r['dim'] for f, r in frame.items()}
    ops, opf = w['ops'], w['op_frame']
    R = 1 + max(max(a, b) for a, b, _ in ops)
    content, current = [0] * R, [None] * R
    for leaf, role in w['sources'].items():
        leaf = int(leaf)
        content[role] = 1 << leaf
        current[role] = (0, w['source_frame'][leaf])
    edges = defaultdict(set)
    phase0 = set(w['phase1'])
    order = sorted(phase0) + [i for i in range(len(ops)) if i not in phase0]
    def move(role, target):
        origin = current[role]
        if origin is not None and origin != target and content[role]:
            edges[origin, target].add(content[role])
        current[role] = target
    for i in order:
        a, b, _ = ops[i]
        vertex = (0 if i in phase0 else 1, opf[i])
        move(a, vertex)
        move(b, vertex)
        assert not content[a] & content[b]
        content[a] ^= content[b]
    for root, role, f in zip(g['roots'], w['rootroles'], w['root_frame']):
        move(role, (0 if root['kind'] == 'center' else 1, f))
    outgoing = defaultdict(list)
    candidates = defaultdict(set)
    for (u, v), rows in edges.items():
        for row in rows:
            outgoing[u].append((v, row))
            if dims[u[1]] == 3:
                candidates[row].add(u)
    by_cube = defaultdict(dict)
    for leaf, label in enumerate(g['labels']):
        by_cube[tuple(c//2 for c in label)][tuple(c%2 for c in label)] = leaf
    pairs = {}
    for entry in chk.k['entries']:
        a, b, f = entry['carrier'], entry['passive'], entry['mix_frame']
        assert dims[f] == 2
        assert len(set(g['labels'][a]) & set(g['labels'][b])) == 1
        pairs[(1 << a) | (1 << b)] = (a, b, f)
    def signature(f):
        rows, pivots = reduce_rows(frame[str(f)]['b'], h)
        return tuple(tuple(row) for _,row in sorted(zip(pivots, rows)))
    source_planes = {f for _,_,f in pairs.values()}
    old_rank2_frames = {f for f in opf if dims[f] == 2}
    assert not {signature(f) for f in source_planes} & {signature(f) for f in old_rank2_frames}
    instances = []
    source_instances = defaultdict(list)
    for cube, leaves in sorted(by_cube.items()):
        for value in range(2):
            requests = [
                ('A0', sum(1 << i for bits, i in leaves.items() if bits[0] == value)),
                ('G12', sum(1 << i for bits, i in leaves.items() if bits[1] ^ bits[2] == value))]
            for channel, mask in requests:
                vertex = min(candidates[mask])
                out = sorted(outgoing[vertex])
                assert all(row == mask for _, row in out)
                inputs = sorted(p for p in pairs if p & mask == p)
                assert len(inputs) == 2 and inputs[0] ^ inputs[1] == mask
                basis = frame[str(vertex[1])]['b']
                assert len(basis) == 3
                pair_records = []
                for pair in inputs:
                    a, b, f = pairs[pair]
                    chi = [[int(j in g['labels'][i]) for j in range(h)] for i in (a,b)]
                    assert len(reduce_rows(basis + chi, h)[0]) == 3
                    source_vertex = (vertex[0], f)
                    source_instances[source_vertex].append((vertex, a, b, pair))
                    pair_records.append(dict(source_frame=f, controls=[a,b], mask=hex(pair)))
                t = len(out)
                T = template('pair_sum', t)
                actual_fresh = inputs + [0] * (t-1)
                assert apply(T['forward'], actual_fresh) == [mask] * t + [inputs[1]]
                instances.append(dict(kind='pair_sum', channel=channel, cube=cube,
                    phase=vertex[0], frame=vertex[1], t=t,
                    inputs=pair_records, output_frames=[target for target,_ in out],
                    output_mask=hex(mask), complement_mask=hex(inputs[1])))
    for vertex, outputs in sorted(source_instances.items()):
        a, b = outputs[0][1:3]
        assert all((x,y)==(a,b) for _,x,y,_ in outputs)
        t = len(outputs)
        T = template('source_pair', t)
        fresh = [0] * t + [1 << a, 1 << b]
        pair = (1 << a) | (1 << b)
        assert apply(T['forward'], fresh) == [pair] * t + [1 << a, 1 << b]
        instances.append(dict(kind='source_pair', phase=vertex[0], frame=vertex[1],
            controls=[a,b], t=t, output_frames=[target for target,_,_,_ in outputs],
            output_mask=hex(pair)))
    assert sum(i['kind']=='pair_sum' for i in instances) == 880
    assert sum(i['kind']=='source_pair' for i in instances) == 1760
    assert set(source_instances) == {(phase, f) for phase in (0,1) for f in source_planes}
    return instances


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--output', type=Path, default=HERE / 'source_aligned_lifts.json')
    parser.add_argument('--instances', type=Path)
    args = parser.parse_args()
    instances = extract(args.source.resolve())
    counts = Counter((i['kind'], i['t']) for i in instances)
    templates = {f'{kind}:{t}': template(kind,t) for kind,t in sorted(counts)}
    representatives = {key: next(i for i in instances if f"{i['kind']}:{i['t']}"==key)
                       for key in templates}
    manifest = json.dumps(instances, sort_keys=True, separators=(',', ':')).encode()
    result = dict(author='GPT-6 Astra', source_commit=COMMIT,
        interpretation='Matrix rows are binary masks on incoming physical coordinates; every XOR/swap is at one exact common frame; inverses run in reverse chronology at full frame',
        instances=len(instances), instance_sha256=hashlib.sha256(manifest).hexdigest(),
        template_counts={f'{kind}:{t}': n for (kind,t),n in sorted(counts.items())},
        templates=templates, representatives=representatives,
        checks=dict(source_controls_unchanged=True, exact_two_sided_inverse_on_every_instance=True,
                    every_required_fresh_output_verified=True,
                    every_source_pair_inside_its_rank3_frame=True,
                    full_source_control_span_present_in_both_phases_of_every_M=True,
                    no_old_rank2_operation_frame_equals_a_source_M=True,
                    all_rank3_fresh_complements_retained=True))
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    if args.instances:
        args.instances.write_text(json.dumps(instances, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('templates','representatives')}, indent=2))


if __name__ == '__main__':
    main()
