#!/usr/bin/env python3
"""Independent phase-order/bank-bit audit. Apache-2.0.
Dennis / antunishdPursuit, with substantial OpenAI Codex assistance.
No predecessor implementation is imported or executed.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(order, colors):
    f = len(order)
    require(f > 0 and sorted(order) == list(range(f)), 'not a consumer permutation')
    require(len(colors) == f and all(type(c) is int and 0 <= c < f for c in colors),
            'invalid independent-bank assignment')
    return f, max(colors) + 1


def pauli_polynomial(order, colors):
    """Replay X(v_j)Z(u_j) on symbolic arbitrary incoming bank bits.

    Integer bit j*(f+b)+k encodes u_j times v_k (k<f), or incoming
    bank bit c_(k-f). XOR is exact polynomial addition over F2.
    """
    f, b = validate(order, colors)
    state = [1 << (f+k) for k in range(b)]
    phase = 0
    for j in (*range(f), *order):
        k = colors[j]
        phase ^= state[k] << (j*(f+b))
        state[k] ^= 1 << j
    require(state == [1 << (f+k) for k in range(b)], 'bank did not return')
    return phase


def target_polynomial(f, b):
    return sum(1 << (j*(f+b)+j) for j in range(f))


def conflicts(order, colors):
    f, _ = validate(order, colors)
    position = {j:k for k,j in enumerate(order)}
    return [(i,j) for i in range(f) for j in range(i+1,f)
            if colors[i] == colors[j] and position[i] < position[j]]


def predicted_polynomial(order, colors):
    f, b = validate(order, colors)
    result = target_polynomial(f,b)
    for i,j in conflicts(order,colors):
        result ^= (1 << (i*(f+b)+j)) | (1 << (j*(f+b)+i))
    return result


def increasing_certificate(order):
    """DP ranks color decreasing subsequences; retain a lower-bound clique."""
    length, witness = {}, {}
    for index,j in enumerate(order):
        previous = [k for k in order[:index] if k < j]
        best = max(previous,key=lambda k:(length[k],-k)) if previous else None
        length[j] = 1 if best is None else length[best]+1
        witness[j] = [] if best is None else witness[best][:]
        witness[j].append(j)
    end = max(order,key=lambda k:(length[k],-k))
    return [length[j]-1 for j in range(len(order))], witness[end]


def partitions(f):
    """Every set partition once, as a restricted-growth color sequence."""
    def visit(prefix):
        if len(prefix) == f:
            yield tuple(prefix)
        else:
            for c in range(max(prefix)+2):
                yield from visit(prefix+[c])
    yield from visit([0])


def evaluate(poly, f, b, u, v, bank=0):
    second = v | (bank << f)
    value = 0
    for j in range(f):
        if (u >> j) & 1:
            value ^= ((poly >> (j*(f+b))) & second).bit_count() & 1
    return value


def source_record():
    sources = json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    row = sources['predecessor']
    require(row['commit'] == 'a007c32f992195ad372806db38c9359dd49382ad', 'predecessor head drift')
    expected = {
        'README.md': ('b9a6966efaa8901b7ccc3b88a133aec661258fca',
                      '65d18a905d30ef2d411ad85cd22ab1a689ca0687bf6c78dda6cd7e0ea529d7d6'),
        'model.py': ('8ff27dbcc82b0f365d8a76d0525300062a635b2d',
                     '78785eda409a767094381c737ee7347d2412c6a0c02779087a3d403e923a7bc1')}
    actual = {r['path'].split('/')[-1]:(r['git_blob'],r['sha256']) for r in row['files']}
    require(actual == expected and len(row['files']) == 2, 'predecessor reference pin drift')
    # These are inspected reference pins, not a claim of runtime source authentication.
    return row['commit']


def symbolic_checks():
    rows, total, digest = [], 0, sha256()
    for f in range(1,8):
        hist = Counter()
        for order in permutations(range(f)):
            colors, witness = increasing_certificate(order)
            b = max(colors)+1
            require(len(witness) == b and witness == sorted(witness), 'invalid LIS lower witness')
            pos = {j:k for k,j in enumerate(order)}
            require(all(pos[i] < pos[j] for i,j in zip(witness,witness[1:])), 'not a subsequence')
            require(len({colors[j] for j in witness}) == b, 'lower witness shares a bank')
            actual = pauli_polynomial(order,colors)
            require(actual == predicted_polynomial(order,colors) == target_polynomial(f,b),
                    'constructive assignment fails')
            one = pauli_polynomial(order,[0]*f)
            require(one == predicted_polynomial(order,[0]*f), 'cross-term formula fails')
            require((one == target_polynomial(f,1)) == (order == tuple(reversed(range(f)))),
                    'single-bank order criterion fails')
            digest.update(json.dumps([order,colors,witness,hex(actual)],separators=(',',':')).encode())
            hist[b] += 1
            total += 1
        rows.append({'f':f,'consumer_permutations':sum(hist.values()),'minimum_bank_bits_histogram':{str(k):v for k,v in sorted(hist.items())}})
    # A second minimum calculation checks every bank equality pattern, not just the DP solution.
    assignments, minimums = 0, 0
    for f in range(1,6):
        choices = list(partitions(f))
        for order in permutations(range(f)):
            valid = []
            for colors in choices:
                b = max(colors)+1
                actual = pauli_polynomial(order,colors)
                require(actual == predicted_polynomial(order,colors),'arbitrary partition formula fails')
                correct = actual == target_polynomial(f,b)
                require(correct == (not conflicts(order,colors)), 'partition criterion fails')
                if correct:
                    valid.append(b)
                assignments += 1
            colors,_ = increasing_certificate(order)
            require(min(valid) == max(colors)+1,'brute minimum disagrees')
            minimums += 1
    return {'permutations':total,'by_f':rows,'canonical_schedule_sha256':digest.hexdigest(),
            'all_partition_schedules':assignments,'brute_minimum_permutations':minimums}


def controls():
    caught = []
    for order,colors,name in [((0,1),(0,0),'same-order shared bank'),
                               ((2,0,1),(0,0,0),'partial reversal'),
                               ((2,0,1),(0,0,1),'insufficient two-bank assignment')]:
        # Last case is incorrect because columns 0 and 1 share a bank.
        f,b = validate(order,colors)
        bad = pauli_polynomial(order,colors)
        require(bad != target_polynomial(f,b), 'mutant escaped: '+name)
        i,j = conflicts(order,colors)[0]
        for bank in range(1 << b):
            require(evaluate(bad,f,b,1 << i,1 << j,bank) == 1,
                    'cross-term witness failed')
            require(((1 << i) & (1 << j)).bit_count() % 2 == 0, 'target witness not zero')
        caught.append(name)
    for order,colors,name in [((0,0),(0,0),'duplicate consumer'),
                               ((0,1),(0,),'missing assignment'),
                               ((0,1),(0,-1),'invalid bank label')]:
        try:
            pauli_polynomial(order,colors)
        except ValueError:
            caught.append(name)
        else:
            raise ValueError('malformed schedule accepted: '+name)
    # The aggregate shortcut is rank one: (u0+u1)(v0+v1), not dot product.
    require(((1).bit_count()%2)*((2).bit_count()%2) != ((1 & 2).bit_count()%2),
            'aggregate shortcut escaped')
    caught.append('aggregate parity shortcut')
    return caught


def result():
    import importlib.util
    spec = importlib.util.spec_from_file_location('phase_order_physical',HERE/'physical.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    run_checks = module.run_checks
    return {'schema_version':1,'status':'PASS_PHASE_ORDER_BANK_AUDIT',
            'predecessor':source_record(),'symbolic':symbolic_checks(),
            'physical':run_checks(),'rejected_controls':controls(),
            'cost_boundary':{'one_axis_C_calls_per_column':4,'independent_of_bank_assignment':True,
                             'schedule':'literal unfused word only; no minimum C-call claim',
                             'native_wrappers_and_full_operand_volume':'additional; not recertified here'},
            'scope':'Producer prefix, consumer permutation, independent formal labels and one assigned tensor-bank bit per column. No encoded/general bank optimum, all-size supplier or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true')
    args = parser.parse_args()
    actual = result()
    if args.emit:
        print(json.dumps(actual,indent=2,sort_keys=True))
    else:
        expected = json.loads((HERE/'RESULT.json').read_text(encoding='utf-8'))
        require(actual == expected, 'typed result receipt mismatch')
        print(actual['status'])
        print(json.dumps({'symbolic_permutations':actual['symbolic']['permutations'],
                          'partition_schedules':actual['symbolic']['all_partition_schedules'],
                          'physical_columns':actual['physical']['complete_columns'],
                          'controls':len(actual['rejected_controls'])+actual['physical']['rejected_controls']}))


if __name__ == '__main__':
    main()
