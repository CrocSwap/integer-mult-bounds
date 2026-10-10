#!/usr/bin/env python3
"""Reconstruct and check the changed finite supplier; inherited all-size interfaces remain conditional."""
import argparse
from fractions import Fraction
import gzip
import json
from pathlib import Path
import sys
import time

from candidate import (PINS, BIT_PACKAGE, SERVED_PACKAGE, canonical, check_sources,
                       construct, load, sha)

if sys.flags.optimize:
    raise SystemExit('Assertions must be enabled')
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent


def serial(x):
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, dict):
        return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [serial(v) for v in x]
    return x


def prime_check(word, bit, output):
    """Recompute the Gram determinant for every distinct used basis, including passive stops."""
    helper = load('composition_prime_helper', bit / 'bit/prime_witnesses.py')
    used = set(word.opframe) | set(word.w['source_frame']) | set(word.w['root_frame'])
    used.add(word.w['full_frame'])
    used.update(z['frame'] for z in word.w['gauges'])
    for e in word.k['entries']:
        used.update(e['carrier_chain'])
        used.update(e['passive_chain'])
        used.update((e['mix_frame'], e['deliver_frame']))
    grouped = {}
    for f in sorted(used):
        basis = tuple(map(tuple, word.C.B[f]))
        grouped.setdefault(basis, []).append(f)
    records = []
    for basis, ids in sorted(grouped.items()):
        sums = list(map(sum, basis))
        gram = [[9 * sum(a*b for a, b in zip(x, y)) - sums[i]*sums[j]
                 for j, y in enumerate(basis)] for i, x in enumerate(basis)]
        determinant = helper.det(gram)
        powers, residual = helper.factor_witness(determinant)
        records.append(dict(frame_ids=ids, basis_sha256=sha(canonical(basis)),
                            dimension=len(basis), determinant=determinant,
                            prime_powers=powers, residual=residual))
    def coverage(items):
        seen = set()
        for item in items:
            assert not seen.intersection(item['frame_ids'])
            seen.update(item['frame_ids'])
            helper.validate_factor(item['determinant'], item['prime_powers'], item['residual'])
        assert seen == used, 'incomplete prime witness coverage'
    coverage(records)
    try:
        coverage(records[:-1])
    except AssertionError:
        pass
    else:
        raise AssertionError('missing prime witness admitted')
    payload = canonical(records)
    (output / 'prime-witnesses.json.gz').write_bytes(gzip.compress(payload, mtime=0))
    return dict(used_frames=len(used), distinct_bases=len(records),
                canonical_sha256=sha(payload), missing_record_rejected=True,
                rule='Every used cleared Gram determinant is nonzero and has no prime divisor above 2^80.')


def controls(word, meta):
    outcomes = {}
    for name in ('omit_compensation', 'missing_partner', 'stale', 'served_from_carrier'):
        try:
            word.formal(2, name)
        except ValueError:
            outcomes[name] = 'REJECTED'
        else:
            raise AssertionError('word mutation accepted: ' + name)
    i, j, _ = meta['first_butterfly_operations']
    saved = word.ops[i][1]
    word.ops[i][1] = word.ops[j][1]  # undo just one leg of the paired rewrite
    try:
        try:
            word.formal(2)
        except ValueError:
            outcomes['one_leg_butterfly'] = 'REJECTED'
        else:
            raise AssertionError('one-leg butterfly admitted')
    finally:
        word.ops[i][1] = saved
    entry = next(e for e in word.k['entries'] if e.get('early'))
    saved = entry['passive_chain']
    entry['passive_chain'] = [saved[0], saved[1], saved[-1]]
    try:
        try:
            word.C.chains()
        except ValueError:
            outcomes['missing_passive_stop'] = 'REJECTED'
        else:
            raise AssertionError('missing passive stop admitted')
    finally:
        entry['passive_chain'] = saved
    entry['early'] = False
    try:
        try:
            word.C.chains()
        except ValueError:
            outcomes['late_served_mix'] = 'REJECTED'
        else:
            raise AssertionError('late served mix admitted')
    finally:
        entry['early'] = True
    return outcomes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in PINS:
        parser.add_argument('--' + name + '-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    roots = {name: getattr(args, name + '_root').resolve() for name in PINS}
    output = args.output.resolve()
    assert not output.exists(), 'Use a fresh output directory'
    for root in (*roots.values(), HERE):
        assert output != root and root not in output.parents, 'Output must be outside source packages'
    check_sources(roots)
    output.mkdir(parents=True)
    start = time.monotonic()
    def stage(name, fn):
        print('START ' + name, flush=True)
        value = fn()
        print('PASS ' + name, flush=True)
        return value
    bit = roots['bit'] / BIT_PACKAGE
    served = roots['served'] / SERVED_PACKAGE
    # Reproduce PR223's inputs before using them as a dependency.
    parent = load('composition_parent_verify', served / 'verify.py')
    derivation = stage('served-word derivation from PR200', lambda: parent.rederive(roots['bit']))
    word, meta = stage('compose and reload complete emitted word', lambda: construct(roots, output / 'effective'))
    stage('exact decoder and frame geometry', word.exact_frames)
    baseline = stage('complete physical chains and ledger', word.row)
    formal = stage('all unsunk F2 columns', lambda: word.formal(2))
    mutations = stage('adversarial word controls', lambda: controls(word, meta))
    terminal_module = load('composition_terminal', served / 'bit/served_terminal.py')
    selection = json.loads((bit / 'selected/bit/sinks.json').read_bytes())
    terminal = stage('terminal F2 and both integer directions', lambda: terminal_module.prove(word, selection))
    terminal.pop('seconds')
    terminal.pop('maxrss')
    primes = stage('exact prime witnesses for all used frames', lambda: prime_check(word, bit, output))
    certify = load('composition_paid_certifier', bit / 'bit/prove.py')
    row = terminal['profile']
    row['child_histogram'] = {int(k): n for k, n in row['child_histogram'].items()}
    coarse = stage('unpacked paid moment and ordinary seed', lambda: certify.certify(row))
    sys.path.insert(0, str(served))
    import packing, arithmetic, audit
    # Packing uses only gauges, roles, aliases and sink IDs, all unchanged by our overlay.
    original = json.loads(gzip.decompress((served / 'selected/served/word_p12.json.gz').read_bytes()))
    for key in ('gauges', 'pairs', 'rootroles'):
        assert word.w[key] == original[key], ('packing interface changed', key)
    physical = stage('completed banks and exact charts',
                     lambda: packing.build(roots['bit'], served / 'selected/served', serial(row)))
    physical['word_sha256'] = meta['emitted_sha256']['word_p12.json']
    physical['served_word'] = 'effective/selected/bit/word_p12.json (canonical SHA-256)'
    result = stage('finite leaves and 47 assembly constraints',
                   lambda: arithmetic.build(roots['complex'], roots['bit'], physical,
                                            dict(profile=row, coarse=coarse)))
    result['bit_word'] = 'PR223 served word + PR211 frames + 67 compatible PR217 butterflies'
    independent = stage('independent rational moment engine', lambda: audit.run(result, result['unpacked_profile']))
    previous = Fraction(692144604250060, 10**18)
    kappa = result['after_packing']['kappa']
    assert kappa > previous
    check_sources(roots)
    record = serial(dict(scope='Changed finite supplier and conditional inherited composition; no full theorem verification',
                         source_commits=PINS, derivation=derivation, composition=meta,
                         baseline_profile=baseline, unsunk_formal=formal, controls=mutations,
                         terminal=terminal, primes=primes, coarse=coarse, physical=physical,
                         arithmetic=result, independent=independent, prior_pr223_kappa=previous,
                         kappa=kappa, relative_gain_over_pr223=kappa/previous-1,
                         inherited_complex_proof_freshly_replayed=False))
    (output / 'certificate.json').write_bytes(canonical(record))
    expected = HERE / 'certificate.json'
    if args.write_certificate:
        expected.write_text(json.dumps(record, sort_keys=True, indent=2) + '\n')
    else:
        assert record == json.loads(expected.read_bytes()), 'certificate differs'
    (output / 'execution.json').write_bytes(canonical(dict(seconds=time.monotonic()-start,
        python=sys.version, verifier_sha256=sha(Path(__file__).read_bytes()),
        candidate_sha256=sha((HERE/'candidate.py').read_bytes()), status='PASS')))
    print('PASS conditional kappa = ' + str(kappa) + ' = ' + str(float(kappa)), flush=True)


if __name__ == '__main__':
    main()
