#!/usr/bin/env python3
"""Source-bound error budget for the QQ16 decoder; no predecessor imports.

BigCactusLabs, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHANNELS = ('add', 'line', 'stage')
COUNTS = {'add': 1688, 'clear': 320, 'line': 224, 'current_map': 208,
          'stage': 16, 'private_begin': 2, 'private_end': 2,
          'checkpoint': 2, 'history_boundary': 1}
# Keys are (power of X, power of Y, error channel), where
# X=2^ceil(lambda/2), Y=2^(4*lambda). Coefficients are nonnegative rationals.
OWNED = {(0, 0, 'add'): Q(928), (0, 1, 'add'): Q(784),
         (0, 0, 'line'): Q(49), (0, 0, 'stage'): Q(392)}
BORROWED = {(0, 0, 'line'): Q(1), (1, 0, 'line'): Q(1)}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def encode(poly):
    return [[i, j, channel, str(c)] for (i, j, channel), c in sorted(poly.items())]


def add(a, b, scale=Q(1)):
    out = dict(a)
    require(scale >= 0, 'nonnegative error scale')
    for key, value in b.items():
        out[key] = out.get(key, Q(0)) + scale * value
    return {key: value for key, value in out.items() if value}


def gain(poly, line=0, stage=0):
    return {(i + line, j + stage, channel): c
            for (i, j, channel), c in poly.items()}


def value(poly, depth, tolerances=None):
    require(type(depth) is int and depth >= 1, 'positive integral tensor depth')
    eps = {channel: Q(1) for channel in CHANNELS} if tolerances is None else tolerances
    return sum(c * (1 << ((depth + 1)//2 * i + 4*depth*j)) * eps[channel]
               for (i, j, channel), c in poly.items())


def dominates(bound, poly):
    return all(c <= bound.get(key, 0) for key, c in poly.items())


def update_maximum(bound, poly):
    for key, c in poly.items():
        bound[key] = max(bound.get(key, Q(0)), c)


def authenticated_word(directory=HERE):
    manifest = json.loads((directory / 'SNAPSHOTS.json').read_text(encoding='utf-8'))
    expected_paths = {'inputs/PR2540-WORD.json', 'inputs/PR2540-PROOF.md',
                      'inputs/PR2540-native_support.py', 'inputs/PR2603-PROOF.md'}
    require(len(manifest['files']) == len(expected_paths), 'snapshot inventory count')
    raw_files = {}
    for item in manifest['files']:
        name = item['path']
        require(name in expected_paths and name not in raw_files, 'snapshot path/inventory')
        raw = (directory / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source SHA256: ' + name)
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == item['git_blob'], 'source Git blob: ' + name)
        raw_files[name] = raw
    require(set(raw_files) == expected_paths, 'complete source inventory')
    word = json.loads(raw_files['inputs/PR2540-WORD.json'])
    require(len(word) == 2463 and Counter(e['op'] for e in word) == COUNTS,
            'complete literal word coverage')
    return word


def forward(word):
    """Propagate componentwise triangle errors, separately for three channels."""
    rows = {}
    active = set()
    peaks = {'owned': {}, 'borrowed': {}}
    history = []
    seen_history = False
    for index, event in enumerate(word):
        op = event['op']
        changed = []
        if op == 'add':
            dst, src = event['dst'], event['src']
            require(dst != src, 'nonaliased ADD')
            q = abs(Q(event['coefficient']))
            require(q in (Q(1), Q(1, 4)), 'declared ADD coefficient')
            rows[dst] = add(add(rows.get(dst, {}), rows.get(src, {}), q),
                            {(0, 0, 'add'): Q(1)})
            changed = [dst]
        elif op in ('line', 'stage'):
            field = event['field']
            if op == 'stage':
                require(type(event['rank']) is int and event['rank'] == 8, 'rank-eight child')
            require(type(event['sign']) is int and event['sign'] in (-1, 1), 'native sign')
            rows[field] = add(gain(rows.get(field, {}), line=int(op == 'line'),
                                   stage=int(op == 'stage')), {(0, 0, op): Q(1)})
            changed = [field]
        elif op == 'clear':
            rows[event['field']] = {}
            changed = [event['field']]
        elif op == 'current_map':
            require(type(event['inverse']) is bool, 'cover-map orientation type')
            # Exact owner/payload permutations are isometries for this norm.
        elif op == 'history_boundary':
            require(not seen_history and not active, 'one external B1 boundary')
            seen_history = True
            # Current arrays are new reference inputs. B1 errors are not part
            # of this added-word contract; retained R errors survive the cut.
            for p in range(112):
                for side in ('X', 'Y'):
                    rows[f'{side}{p}'] = {}
        elif op == 'private_begin':
            require(not active, 'nonoverlapping local lifetimes')
            active = set(event['fields'])
            for field in active:
                rows[field] = {}
        elif op == 'private_end':
            require(active == set(event['fields']), 'matched local lifetime')
            require(all(not rows[field] for field in active), 'scratch error reset')
            for field in active:
                del rows[field]
            active = set()
        elif op == 'checkpoint':
            require(not active, 'checkpoint outside local body')
        else:
            raise ValueError('unknown word event: ' + op)
        for field in changed:
            group = 'borrowed' if field.startswith(('X', 'Y')) else 'owned'
            update_maximum(peaks[group], rows[field])
            bound = BORROWED if group == 'borrowed' else OWNED
            require(dominates(bound, rows[field]), 'error envelope at ' + str((index, field)))
            history.append([index, field, encode(rows[field])])
    require(seen_history and not active, 'complete error timeline')
    require(all(not rows[f'X{p}'] for p in range(112)), 'X inputs unchanged')
    require(all(rows[f'Y{p}'] == BORROWED for p in range(112)), 'borrowed Y return bound')
    require(all(not row for field, row in rows.items() if field.startswith('R')), 'early retirement')
    require(peaks == {'owned': OWNED, 'borrowed': BORROWED}, 'exact coefficient maxima')
    # One actual row attains all four coefficients of the *triangle recurrence*.
    # This does not say physical perturbations attain all triangle equalities.
    require(rows['W0'] == OWNED, 'complete output-envelope witness')
    return rows, history


def calculation(word):
    rows, history = forward(word)
    output_rows = {f'{s}{p}': rows[f'{s}{p}'] for s in ('Z', 'W') for p in range(112)}
    require(all(dominates(OWNED, row) for row in output_rows.values()), 'all output bounds')
    require(value(OWNED, 1) == 13913, 'one-layer accumulated-error coefficient')
    require(1369 + 784*16 < 1024*16, 'all-layer 4*lambda+10 guard base inequality')
    table = json.dumps(history, separators=(',', ':')).encode()
    return {
        'status': 'PASS_QQ16_DECODER_ERROR_BUDGET',
        'word_events': len(word), 'event_counts': dict(sorted(COUNTS.items())),
        'changed_field_boundaries': len(history), 'final_fields': len(rows),
        'outputs': len(output_rows), 'owned_envelope': encode(OWNED),
        'borrowed_y_envelope': encode(BORROWED),
        'output_error': '(928+784*2^(4*lambda))*eps_add+49*eps_line+392*eps_stage',
        'borrowed_y_error': '(1+2^ceil(lambda/2))*eps_line',
        'common_tolerance_bound': '(1369+784*2^(4*lambda))*epsilon',
        'common_tolerance_lambda1': 13913,
        'sufficient_error_reserve_bits': '4*lambda+10',
        'coefficient_witness': 'final W0 (triangle recurrence, not physical sharpness)',
        'prefix_error_table_sha256': hashlib.sha256(table).hexdigest(),
        'final_error_table_sha256': hashlib.sha256(json.dumps(
            [[field, encode(row)] for field, row in sorted(rows.items())],
            separators=(',', ':')).encode()).hexdigest(),
        'scope': 'Conditional local error propagation; inherited native semantics; no new kappa.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true', help='explicitly regenerate the receipt')
    args = parser.parse_args()
    result = calculation(authenticated_word())
    path = HERE / 'RESULT.json'
    if args.write_result:
        path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    else:
        # JSON text equality also rejects booleans substituted for integers.
        expected = json.loads(path.read_text(encoding='utf-8'))
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                'committed result mismatch')
    print(result['status'] + ' events=2463 outputs=224 lambda1=13913 no_new_kappa')


if __name__ == '__main__':
    main()
