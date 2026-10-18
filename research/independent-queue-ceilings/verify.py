#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent offline audit of the frozen PR1264 census; see README.md.

Hanson Sun with substantial OpenAI Codex assistance. No predecessor executable
is imported. Default operation checks the complete deterministic receipt;
--write explicitly regenerates only this package's RESULT.json.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bounds import child_cost, rational_power, relaxation, require, side

ROOT = HERE.parents[1]
SNAPSHOT = 'research/complex-queue-ceiling-census/SNAPSHOT.json'
CENSUS = 'research/complex-queue-ceiling-census/RESULT.json'
ASSEMBLY = 'research/community-frontier1094-audit/ASSEMBLY.json'
SELECTED_AUDIT = 'research/community-frontier1094-audit/INDEPENDENT1094.json'
REQUIRED = {SNAPSHOT, CENSUS, ASSEMBLY, SELECTED_AUDIT}
GRID = Q(1, 10**15)


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + '\n'


def same(a, b, message):
    # JSON comparison must distinguish bool/int and float/int, unlike ==.
    require(canonical(a) == canonical(b), message)


def load_external(root=ROOT, package=HERE):
    sources = json.loads((package / 'SOURCES.json').read_text())
    inputs = [r for r in sources['files'] if r['usage'] == 'input']
    require(len(inputs) == len(REQUIRED) and {r['path'] for r in inputs} == REQUIRED,
            'external source inventory differs')
    out = {}
    for row in inputs:
        raw = (root / row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'],
                'external source drift: ' + row['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == row['git_blob'], 'external Git blob differs')
        out[row['path']] = json.loads(raw)
    return out


def load_upstream(snapshot, package=HERE):
    manifest = json.loads((package / 'UPSTREAM.json').read_text())
    require(manifest['repository'] == 'CrocSwap/integer-mult-bounds', 'wrong upstream repository')
    expected = {(c['head'], c[k+'_file'], c[k+'_blob'])
                for c in snapshot['claims'] for k in ('profile', 'idle')}
    rows = manifest['records']
    keys = [(r['head'], r['path'], r['git_blob']) for r in rows]
    require(len(keys) == len(set(keys)) and set(keys) == expected,
            'upstream input inventory differs')
    out = {}
    for row in rows:
        blob = row['git_blob']
        require(row['local'] == 'inputs/' + blob + '.json.gz', 'noncanonical input path')
        raw = gzip.decompress((package / row['local']).read_bytes())
        require(type(row['size']) is int and len(raw) == row['size'], 'upstream input size differs')
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'upstream SHA256 differs')
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == blob,
                'upstream Git blob differs')
        out[row['head'], row['path']] = json.loads(raw)
    return out


def histogram(raw):
    require(type(raw) is dict and bool(raw), 'empty histogram')
    out = {}
    for key, value in raw.items():
        require(type(key) is str and key.isdigit() and str(int(key)) == key,
                'noncanonical rank')
        rank = int(key)
        require(0 < rank < 73 and type(value) is int and value >= 0,
                'invalid histogram entry')
        if value:
            out[rank] = value
    return out


def split(profile, idle, calls, live):
    require(type(calls) is int and calls > 0 and calls % 9 == 0,
            'invalid complete call count')
    require(type(live) is int and live > 0 and 9 * live == 896 * calls,
            'wrong live-family normalization')
    p, i = histogram(profile), histogram(idle)
    require(all(rank <= 51 and count <= p.get(rank, 0) for rank, count in i.items()),
            'idle profile is not a guard-admissible subprofile')
    mass = sum(rank * count for rank, count in p.items())
    require(mass == 72 * live + 64 * calls, 'coverage mass differs')
    local = {rank: Q(count - i.get(rank, 0), calls)
             for rank, count in p.items() if count != i.get(rank, 0)}
    idle_mass = Q(sum(rank * count for rank, count in i.items()), calls)
    require(sum(rank * count for rank, count in local.items()) + idle_mass == 7232,
            'per-call mass does not reconcile')
    return local, idle_mass


def at(obj, pointer):
    require(type(pointer) is str and pointer.startswith('/'), 'invalid source JSON pointer')
    for key in pointer[1:].split('/'):
        obj = obj[key]
    return obj


def source_counts(profile, idle):
    """Bind N to original fields; explicitly distinguish four inferred W values."""
    call_evidence = []
    live_evidence = []
    for label, obj in (('profile', profile), ('idle', idle)):
        for key in ('calls', 'complete_invocations'):
            if key in obj:
                n = obj[key]
                require(type(n) is int and n > 0, 'invalid source calls')
                call_evidence.append((label + '/' + key, n))
        if 'provider_counts' in obj:
            counts = obj['provider_counts']
            require(type(counts) is dict and bool(counts)
                    and all(type(n) is int and n > 0 for n in counts.values()),
                    'invalid provider counts')
            call_evidence.append((label + '/provider_counts:sum', sum(counts.values())))
        for prefix, block in (('', obj), ('/expected', obj.get('expected', {}))):
            if 'live' in block:
                w = block['live']
                require(type(w) is int and w > 0, 'invalid source live stock')
                live_evidence.append((label + prefix + '/live', w))
    require(call_evidence and len({v for _, v in call_evidence}) == 1,
            'missing or inconsistent source call counts')
    n = call_evidence[0][1]
    w = Q(896 * n, 9)
    require(w.denominator == 1, 'source count is not complete replicas')
    if live_evidence:
        require(all(v == w for _, v in live_evidence), 'source live stock differs from template')
        mode = 'direct source field and template agreement'
    else:
        mode = 'inferred from source N under the 896/9 template premise'
    return n, int(w), dict(calls=call_evidence, live=live_evidence, live_mode=mode)


def reconstruct(claim, upstream):
    p = upstream[claim['head'], claim['profile_file']]
    i = upstream[claim['head'], claim['idle_file']]
    profile = p['complex_profile']
    idle = {r: n for r, n in at(i, claim['idle_json_path']).items() if n}
    same(profile, claim['profile'], 'source aggregate differs')
    same(idle, claim['idle'], 'source idle histogram differs')
    same(p['complex_lower'], claim['complex_lower'], 'source complex endpoint differs')
    same(p['kappa'], claim['kappa'], 'source kappa differs')
    require(Q(claim['title_kappa']) == Q(p['kappa']), 'title kappa differs')
    calls, live, count_evidence = source_counts(p, i)
    same(calls, claim['calls'], 'source call count differs')
    same(live, claim['live'], 'source live count differs')
    local, idle_mass = split(profile, idle, calls, live)
    return local, idle_mass, count_evidence


def profile_json(local):
    return {str(rank): str(count) for rank, count in sorted(local.items())}


def sign_record(local, a, expected):
    interval = relaxation(local, a)
    require(side(interval) == expected, 'claimed endpoint sign differs')
    fine = relaxation(local, a, exponent_bits=128, precision=256)
    require(side(fine) == expected, 'refined endpoint sign differs')
    require(max(interval[0], fine[0]) <= min(interval[1], fine[1]),
            'enclosures are disjoint')
    return {'a': str(a), 'moment_minus_one': [str(x - 1) for x in interval],
            'refined_moment_minus_one': [str(x - 1) for x in fine], 'sign': expected}


def audit(snapshot, census, upstream, assembly, selected):
    claims = snapshot['claims']
    require(len(claims) == 14 and len({c['pr'] for c in claims}) == 14, 'wrong frozen claim domain')
    require(len(census['words']) == 9 and len({w['id'] for w in census['words']}) == 9,
            'wrong frozen profile domain')
    groups, claim_rows = {}, []
    for claim in claims:
        local, idle_mass, evidence = reconstruct(claim, upstream)
        key = canonical(profile_json(local))
        groups.setdefault(key, []).append(claim['pr'])
        claim_rows.append({'pr': claim['pr'], 'head': claim['head'],
                           'local': profile_json(local), 'idle_mass_per_call': str(idle_mass),
                           'count_evidence': evidence})
    require(len(groups) == 9, 'reconstructed profile count differs')
    observed = set()
    records = []
    for word in census['words']:
        key = canonical(word['local_profile_per_call'])
        require(key in groups and key not in observed, 'unknown or repeated census profile')
        observed.add(key)
        same(sorted(groups[key]), word['claims'], 'profile membership differs')
        local = {int(r): Q(n) for r, n in word['local_profile_per_call'].items()}
        require(str(sum(r * n for r, n in local.items())) == word['local_mass_per_call'],
                'reported local mass differs')
        hi = Q(word['a_ceiling'])
        require((hi / GRID).denominator == 1 and GRID < hi < 1, 'off-grid ceiling')
        lo = hi - GRID
        cap = hi / (1 + hi)
        for claim in claims:
            if claim['pr'] in groups[key]:
                require(Q(claim['complex_lower']) < lo and Q(claim['kappa']) < cap,
                        'claim exceeds its relaxation bracket')
        records.append({'id': word['id'], 'claims': word['claims'],
                        'local': profile_json(local),
                        'idle_mass_per_call': str(7232 - sum(r * n for r, n in local.items())),
                        'lower': sign_record(local, lo, 'below'),
                        'upper': sign_record(local, hi, 'above'),
                        'kappa_cap_exact': str(cap)})
    same(assembly['complex_profile'], selected['owner']['profile'], 'selected profile differs')
    n, w = selected['price']['calls'], selected['price']['live']
    local, idle_mass = split(assembly['complex_profile'], selected['owner']['idle'], n, w)
    w2 = next(row for row in records if row['id'] == 'W2')
    same(profile_json(local), w2['local'], 'selected profile is not W2')
    require(idle_mass == 1646, 'selected idle mass differs')
    same(assembly['complex_lower'], selected['price']['complex_lower'], 'selected endpoint differs')
    require(Q(assembly['complex_lower']) < Q(w2['lower']['a']), 'selected endpoint above W2 bracket')
    maximum = max(Q(r['kappa_cap_exact']) for r in records)
    require(maximum < Q('0.001687314840'), 'published rounded global cap is too small')
    return dict(status='PASS_INDEPENDENT_QUEUE_CEILINGS', claims=claim_rows,
                profiles=records, endpoint_decisions=18, refinement_endpoint_decisions=18,
                arithmetic={'exponent_bits': 96, 'fractional_bits': 192,
                            'refined_exponent_bits': 128, 'refined_fractional_bits': 256},
                max_kappa_cap_exact=str(maximum), published_strict_cap='0.001687314840',
                selected={'word': 'W2', 'calls': n, 'live': w, 'idle_mass_per_call': str(idle_mass)},
                scope='Frozen PR1264 extraction and coverage-law relaxation arithmetic only. '
                      'No realized circuit, owner, physical cost, supplier or full multiplication theorem check.')


def controls(snapshot, census, upstream):
    out = []
    def rejects(name, action):
        try:
            action()
        except ValueError:
            out.append(name)
        else:
            raise ValueError('negative control accepted: ' + name)

    claim = snapshot['claims'][0]
    local, _, _ = reconstruct(claim, upstream)
    rejects('idle_rank_52', lambda: relaxation(local, Q(1, 1000), cap=52))
    rejects('negative_local_count', lambda: relaxation({1: -1}, Q(1, 1000)))
    rejects('local_mass_over_budget', lambda: relaxation({1: 7233}, Q(1, 1000)))
    rejects('inconclusive_is_not_rejection', lambda: side((Q(999, 1000), Q(1001, 1000))))
    rejects('wrong_live_normalization', lambda: split(claim['profile'], claim['idle'],
                                                      claim['calls'], 69120))
    bad_idle = deepcopy(claim['idle']); bad_idle['2'] = claim['profile']['2'] + 1
    rejects('idle_not_subprofile', lambda: split(claim['profile'], bad_idle,
                                                claim['calls'], claim['live']))
    changed = deepcopy(claim); changed['calls'] *= 2; changed['live'] *= 2
    rejects('same_ratio_wrong_absolute_call_count', lambda: reconstruct(changed, upstream))
    changed2 = deepcopy(claim); changed2['profile']['1'] = True
    rejects('boolean_in_aggregate', lambda: reconstruct(changed2, upstream))
    # Spread two rank-2 children into rank 1 and rank 3, preserving both child
    # count and rank mass. Strict concavity lowers the moment for 0<a<1.
    w2 = next(row for row in census['words'] if row['id'] == 'W2')
    baseline = {int(r): Q(n) for r, n in w2['local_profile_per_call'].items()}
    shifted = dict(baseline); shifted[1] += 1; shifted[2] -= 2; shifted[3] += 1
    require(sum(shifted.values()) == sum(baseline.values())
            and sum(r*n for r,n in shifted.items()) == sum(r*n for r,n in baseline.items()),
            'control failed to preserve count and mass')
    require(side(relaxation(shifted, Q(w2['a_ceiling']))) == 'below',
            'count/mass-preserving profile mutation was not detected')
    out.append('count_and_mass_preserving_profile_changes_sign')
    require(side(relaxation(baseline, Q(w2['a_ceiling']), centre=0)) == 'below',
            'missing centre control did not change sign')
    out.append('missing_centre_changes_sign')
    require(side(relaxation(baseline, Q(w2['a_ceiling']) - GRID, cap=48)) == 'above',
            'wrong idle cap control did not change sign')
    out.append('rank_48_instead_of_51_changes_lower_sign')
    rejects('upper_endpoint_used_as_lower', lambda: sign_record(baseline, Q(w2['a_ceiling']), 'below'))
    rejects('lower_endpoint_used_as_upper', lambda: sign_record(baseline, Q(w2['a_ceiling']) - GRID, 'above'))
    w7 = next(row for row in census['words'] if row['id'] == 'W7')
    rounded = {1: Q(2353), 2: Q(509), 3: Q(825, 2), 4: Q(255, 2), 5: Q(82), 8: Q(8)}
    require(side(relaxation(rounded, Q(w7['a_ceiling']) - GRID)) == 'above',
            'mixed-provider display rounding did not change lower sign')
    out.append('W7_display_rounding_changes_lower_sign')
    return out


def exact_power_controls():
    cases = 0
    for width in range(2, 13):
        for rank in range(1, width):
            for denominator in (1, 2, 4, 8, 16):
                for numerator in range(denominator + 1):
                    a = Q(numerator, denominator)
                    lo, hi = rational_power(width, rank, a, 8, 64)
                    target = Q(width, rank) ** a.numerator
                    require(lo ** a.denominator <= target <= hi ** a.denominator,
                            'exact algebraic power control failed')
                    cases += 1
            for a in (Q(1, 3), Q(2, 3), Q(1, 99), Q(37, 100)):
                lo, hi = rational_power(width, rank, a, 12, 80)
                target = Q(width, rank) ** a.numerator
                require(lo ** a.denominator <= target <= hi ** a.denominator,
                        'non-dyadic exponent bracketing failed')
                cases += 1
    for r in range(1, 73):
        require(child_cost(r, 73, Q(0)) == (Q(r, 73), Q(r, 73)), 'zero-saving control')
    return {'algebraic_comparisons': cases, 'exact_zero_saving_ranks': 72}


def generate(root=ROOT, package=HERE):
    external = load_external(root, package)
    snapshot, census = external[SNAPSHOT], external[CENSUS]
    upstream = load_upstream(snapshot, package)
    result = audit(snapshot, census, upstream, external[ASSEMBLY], external[SELECTED_AUDIT])
    result['semantic_controls'] = controls(snapshot, census, upstream)
    result['exact_power_controls'] = exact_power_controls()
    result['upstream_blob_count'] = len(upstream)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = generate()
    text = canonical(result)
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(text)
    else:
        require(path.read_text() == text, 'committed receipt differs')
    print(result['status'], 'claims=14 profiles=9 endpoint_signs=18 refined_signs=18',
          'semantic_controls=' + str(len(result['semantic_controls'])),
          'source_blobs=' + str(result['upstream_blob_count']), 'no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print('FAIL:', exc, file=sys.stderr)
        sys.exit(1)
