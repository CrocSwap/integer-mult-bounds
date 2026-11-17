"""Independent finite scalar-model audit. Reads inputs; writes only stdout.

This is NOT a proof of physical reset, tariff, compiler, common-U, or precision.
MOVE is identity in conjugated scalar coordinates. INIT creates zero; CLEAR
discards the owned row. Certificates must use OTHER currently live fields.
Run without -O: assertions are intentional fail-closed verification checks.
"""
import argparse
import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

PIN = '8ab3d9dbe2e2e24202ac96c6122b010b3e7980912f935cc0cc2db2e9d85f83aa'
OUTPUT_PIN = '6133019f0d26e96e2afd15e89d69204350126334c1cf9eb895bfb671a3a66135'
GRID = 1125 * 2**25

def digest(b):
    return hashlib.sha256(b).hexdigest()

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def scaled(row, q):
    result = {}
    for col, value in row.items():
        value, rem = divmod(value * q.numerator, q.denominator)
        require(rem == 0, 'nonintegral intermediate on exact grid')
        if value:
            result[col] = value
    return result

def certificate_valid(coeffs, target, rows, live, erased):
    if not coeffs or erased in coeffs or any(k not in live for k in coeffs):
        return False
    denominator = 1
    for q in coeffs.values():
        denominator = math.lcm(denominator, q.denominator)
    result = {}
    for k, q in coeffs.items():
        integer = q.numerator * (denominator // q.denominator)
        for col, v in rows[k].items():
            value = result.get(col, 0) + integer * v
            if value:
                result[col] = value
            else:
                result.pop(col, None)
    return result == {k: denominator*v for k,v in target.items()}

def metadata_matches(c, index, event, field, chart):
    return (c['clear_index'], c['event'], c['field'], c['chart']) == (index, event, field, chart)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True, help='New receipt file; must not exist')
    args = ap.parse_args()
    require(not args.output.exists(), 'refusing to overwrite output')
    raw_word = (args.snapshot/'word-joint-final.json.gz').read_bytes()
    raw_certs = (args.snapshot/'certs-joint-final.json').read_bytes()
    word = json.loads(gzip.decompress(raw_word))
    package = json.loads(raw_certs)
    require(digest(canonical(word)) == PIN, 'wrong candidate')
    require(package['candidate'] == PIN, 'certificate candidate mismatch')
    certs = package['clears']
    require(len(certs) == 233, 'certificate count')
    n = word['public']
    total = n + word['owned_fields']
    require(len(word['initial']) == n, 'initial charts length')
    rows = [{r: GRID} if r < n else {} for r in range(total)]
    charts = list(word['initial']) + [None]*word['owned_fields']
    live = set(range(n))
    opened = {}
    checked = peak = 0
    checks = {'coefficient_plus_one': 0, 'coefficient_deleted': 0,
              'self_reference': 0, 'cleared_field_metadata': 0}
    owned_certificate_terms = 0
    for event, e in enumerate(word['program']):
        op, r = e[:2]
        require(type(r) is int and 0 <= r < total, 'field out of bounds')
        if op == 'INIT':
            require(r >= n and r not in live and not rows[r], 'invalid INIT')
            live.add(r)
            charts[r] = e[2]
            opened[r] = (event, e[2], [])
            peak = max(peak, len(opened))
        elif op == 'CLEAR':
            require(r in opened and r in live and charts[r] == e[2], 'invalid CLEAR')
            require(checked < len(certs), 'missing certificate')
            c = certs[checked]
            require(metadata_matches(c, checked, event, r, e[2]), 'certificate event/field/chart mismatch')
            require(c['dim'] == len(word['frames'][e[2]]), 'certificate dimension mismatch')
            start, chart, moves = opened[r]
            require((c['init_event'], c['init_chart'], c['owned_moves']) == (start, chart, moves), 'certificate lifetime mismatch')
            target = rows[r]
            require(bool(target), 'unexpected zero CLEAR')
            erased = {int(k): Fraction(v) for k,v in c['erased'].items()}
            require(erased == {k: Fraction(v, GRID) for k,v in target.items()}, 'erased row mismatch')
            require(c['erased_support'] == len(target), 'support mismatch')
            coeffs = {int(k): Fraction(v) for k,v in c['certificate'].items()}
            require(all(0 <= k < n for k in coeffs), 'final certificate must use public fields only')
            require(c['terms'] == len(coeffs), 'terms mismatch')
            require(certificate_valid(coeffs, target, rows, live, r), 'certificate identity or live-other-field violation')
            owned_certificate_terms += sum(k >= n for k in coeffs)
            # Independently exercise every certificate, not just the first one.
            k = next(k for k,q in coeffs.items() if q and rows[k])
            bad = dict(coeffs); bad[k] += 1
            require(not certificate_valid(bad, target, rows, live, r), 'coefficient mutation accepted')
            checks['coefficient_plus_one'] += 1
            bad = dict(coeffs); del bad[k]
            require(not certificate_valid(bad, target, rows, live, r), 'deleted coefficient accepted')
            checks['coefficient_deleted'] += 1
            require(not certificate_valid({r: Fraction(1)}, target, rows, live, r), 'self-reference accepted')
            checks['self_reference'] += 1
            bad_metadata = dict(c); bad_metadata['field'] = (r + 1) % total
            require(not metadata_matches(bad_metadata, checked, event, r, e[2]), 'cleared-field metadata mutation accepted')
            checks['cleared_field_metadata'] += 1
            checked += 1
            rows[r] = {}
            charts[r] = None
            live.remove(r)
            del opened[r]
            print(json.dumps({'progress_clear': checked, 'event': event}), flush=True)
        elif op == 'MOVE':
            require(r in live and charts[r] == e[2] and bool(e[4]) == (r >= n), 'invalid MOVE')
            charts[r] = e[3]
            if r >= n:
                opened[r][2].append([event, e[2], e[3]])
        elif op in ('SCALE', 'ADD', 'COPY'):
            s = r if op == 'SCALE' else e[2]
            require(r in live and s in live and charts[r] == charts[s] == e[-1], 'inactive or chart-mismatched arithmetic')
            require(op == 'SCALE' or s != r, 'aliasing arithmetic')
            q = Fraction(e[2] if op == 'SCALE' else e[3])
            require(q != 0, 'zero coefficient')
            update = scaled(rows[s], q)
            if op == 'ADD':
                for k,v in update.items():
                    value = rows[r].get(k, 0) + v
                    if value:
                        rows[r][k] = value
                    else:
                        rows[r].pop(k, None)
            else:
                require(op != 'COPY' or not rows[r], 'COPY to nonzero destination')
                rows[r] = update
        else:
            raise ValueError('unknown opcode ' + str(op))
    require(checked == 233 and not opened and live == set(range(n)), 'final lifetime mismatch')
    require(charts[:n] == word['final'], 'final charts mismatch')
    require(peak == 50, 'peak mismatch')
    final = [{str(k): v for k,v in sorted(row.items())} for row in rows[:n]]
    output_hash = digest(canonical(final))
    require(output_hash == OUTPUT_PIN, 'final public linear output mismatch')
    receipt = {'status': 'PASS_INDEPENDENT_FINITE233', 'candidate': PIN,
        'word_file_sha256': digest(raw_word), 'cert_file_sha256': digest(raw_certs),
        'script_sha256': digest(Path(__file__).read_bytes()), 'exact_grid': GRID,
        'verified_nonzero_clears': checked, 'owned_peak': peak,
        'negative_controls_rejected': checks, 'owned_certificate_terms': owned_certificate_terms,
        'public_output_scaled_hash': output_hash,
        'scope': 'Exact scalar projection and other-live-field recoverability; no physical reset, pricing, compiler, precision, or common-U proof.'}
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write('\n')
    print(json.dumps(receipt, sort_keys=True), flush=True)

if __name__ == '__main__':
    main()
