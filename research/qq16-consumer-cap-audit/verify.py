#!/usr/bin/env python3
"""Independent exact lower bound for the scoped QQ16 consumer budget."""
from fractions import Fraction as Q
from hashlib import sha1, sha256
from math import factorial
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise ValueError(why)


def pinned_bytes(relpath):
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    rows = [x for x in manifest['files'] if x['path'] == relpath and x['usage'] == 'input']
    require(len(rows) == 1, f'missing or duplicate source pin: {relpath}')
    raw = (ROOT / relpath).read_bytes()
    row = rows[0]
    require(sha256(raw).hexdigest() == row['sha256'], f'SHA256 mismatch: {relpath}')
    blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob == row['git_blob'], f'Git blob mismatch: {relpath}')
    return raw


def git_blob(raw):
    return sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def ln_unit_lower(y, terms=32):
    """Lower bound for ln(y), 1 <= y < 2, by a positive atanh series."""
    require(Q(1) <= y <= Q(2), 'log range reduction')
    z = (y - 1) / (y + 1)
    return 2 * sum((z ** (2*j + 1)) / (2*j + 1) for j in range(terms))


def ln_ratio_lower(x):
    """Lower bound for ln(x), x >= 1, reducing to [1, 2)."""
    require(x >= 1, 'log ratio must be at least one')
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    return k * ln_unit_lower(Q(2)) + ln_unit_lower(x)


def exp_lower(x, terms=5):
    """Positive Taylor partial sum, hence a lower bound for exp(x), x >= 0."""
    require(x >= 0, 'exponential argument must be nonnegative')
    return sum(x**j / factorial(j) for j in range(terms))


def child_cost_lower(rank, m, a):
    require(0 < rank < m, 'child rank outside local range')
    return Q(rank, m) * exp_lower(a * ln_ratio_lower(Q(m, rank)))


def derive_profile(f_profile, b_profile, decoder_children, calls=2):
    require(calls > 0 and decoder_children % calls == 0, 'uneven decoder split across calls')
    profile = {}
    for key in set(f_profile) | set(b_profile):
        rank = int(key)
        profile[rank] = (Q(f_profile.get(str(rank), 0)) + Q(b_profile.get(str(rank), 0))) / calls
    profile[1] = profile.get(1, Q(0)) + Q(decoder_children, calls)
    return {r: n for r, n in profile.items() if n}


def moment_lower(profile, m, w, centre, idle_rank, unpaid=1):
    require(2 * idle_rank * idle_rank < m * m, 'idle rank cap violates the halving guard')
    total = (m - unpaid) * w + centre
    local_mass = sum(Q(r) * Q(n) for r, n in profile.items())
    idle_mass = total - local_mass
    require(idle_mass >= 0, 'local word pays more mass than coverage law allows')
    local = sum(Q(n) * child_cost_lower(r, m, selected_a) for r, n in profile.items())
    idle = idle_mass / idle_rank * child_cost_lower(idle_rank, m, selected_a)
    return (local + idle) / w, total, local_mass, idle_mass


selected_a = Q(836330098538459, 499163669901461541)


def main():
    selected_raw = pinned_bytes('certificates/selected-result.json')
    ceiling_raw = pinned_bytes('research/complex-local-word-ceiling/RESULT.json')
    ceiling_code = pinned_bytes('research/complex-local-word-ceiling/ceiling.py')
    producer_raw = pinned_bytes('research/joint-query/evidence/CONSERVED-QQ16.json')
    decoder_raw = pinned_bytes('research/qq16-line-normalized-decoder/RESULT.json')
    selected = json.loads(selected_raw)
    ceiling = json.loads(ceiling_raw)
    producer = json.loads(producer_raw)
    decoder = json.loads(decoder_raw)
    target = json.loads((PACKAGE / 'TARGET.json').read_text())

    require(selected['kappa'] == '836330098538459/500000000000000000', 'selected kappa pin')
    require(ceiling['status'] == 'PASS_COMPLEX_LOCAL_WORD_CEILING', 'ceiling source status')
    model = ceiling['model']
    require((model['m'], model['stages'], model['centre_per_call'], model['idle_rank_cap']) == (73, 9, 64, 51), 'selected coverage model')
    require(Q(model['live_families_per_call']) == Q(896, 9), 'live families per call')
    require('non-increasing in r' in ceiling_code.decode(), 'pinned ceiling argument source')
    require('2 * R * R < m * m' in ceiling_code.decode(), 'pinned halving guard source')

    claim = target['audited_claim']
    source = target['source']
    external = gzip.decompress((PACKAGE / source['local_archive']).read_bytes())
    require(source['pr'] == 3181 and source['state_at_check'] == 'OPEN', 'PR state premise')
    require(source['head'] == '80fc72d14546088e9fce3c06dc12bc67270da0af', 'PR head premise')
    require(git_blob(external) == source['git_blob'], 'external PR README Git blob mismatch')
    require(sha256(external).hexdigest() == source['sha256'], 'external PR README SHA256 mismatch')
    external_text = external.decode()
    require('`{1: 2596, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}`' in external_text, 'PR profile text premise')
    require('`0.001631159602`' in external_text and '`centre = 64`' in external_text, 'PR cap/coverage text premise')
    require(claim['producer_pair_calls'] == 2 and claim['decoder_rank_one_children_per_pair'] == 336, 'PR pair/decoder premise')
    require(claim['coverage'] == {'m': 73, 'families_per_nine_stage_replica': 896, 'stages': 9, 'centre_per_call': 64, 'idle_rank_cap': 51}, 'PR coverage premise')

    f_profile = producer['invoices']['F']['native_profile']
    b_profile = producer['invoices']['B']['native_profile']
    child_count = decoder['invoice']['rank_one_children']
    require(decoder['events'] == 3823 and child_count == claim['decoder_rank_one_children_per_pair'], 'decoder count pin')
    require(producer['native_cases']['B_1_2']['added_rank1_children'] == 24, 'selected B1_2 producer case')
    derived = derive_profile(f_profile, b_profile, child_count, calls=claim['producer_pair_calls'])
    full = dict(derived)
    full[8] = Q(claim['reported_profile_per_call']['8'])
    reported = {int(r): Q(n) for r, n in claim['reported_profile_per_call'].items()}
    require(full == reported, f"reconstructed profile mismatch: {full}")

    # Remove the eight rank-eight children and give their 64 mass units to the
    # most favorable permitted idle rank. This can only lower the moment because
    # (r/m)^(1-a)/r decreases with rank for a >= 0.
    relaxed = {r: n for r, n in full.items() if r != 8}
    moment, total, local_mass, idle = moment_lower(relaxed, 73, Q(896, 9), 64, 51)
    require((total, local_mass, idle) == (Q(7232), Q(5706), Q(1526)), 'centre-64 coverage mass')
    require(moment > Q(100009, 100000), 'selected exponent is not excluded with margin')

    full_moment, _, _, _ = moment_lower(full, 73, Q(896, 9), 64, 51)
    require(full_moment > moment, 'dropping rank-eight children must be favorable')
    no_centre, _, _, _ = moment_lower(relaxed, 73, Q(896, 9), 0, 51)
    require(no_centre < 1, 'centre-free law must remain outside the proved obstruction')

    try:
        moment_lower(relaxed, 73, Q(896, 9), 64, 52)
    except ValueError as exc:
        require('halving guard' in str(exc), 'wrong illegal-rank failure')
    else:
        raise ValueError('rank-52 idle child incorrectly accepted')
    try:
        derive_profile(f_profile, b_profile, 335, calls=2)
    except ValueError as exc:
        require('uneven decoder split' in str(exc), 'wrong uneven-split failure')
    else:
        raise ValueError('uneven decoder split incorrectly accepted')

    print(json.dumps({
        'status': 'PASS_QQ16_CONSUMER_CAP_BELOW_SELECTED no_new_kappa',
        'selected_a': str(selected_a),
        'relaxed_profile': {str(r): str(n) for r, n in sorted(relaxed.items())},
        'coverage_mass': {'total': str(total), 'local': str(local_mass), 'idle': str(idle)},
        'checked_strictly_above': '100009/100000',
        'display_decimal': f'{float(moment):.15f}',
        'rank8_profile_lower_bound_decimal': f'{float(full_moment):.15f}',
        'centre_free_control_decimal': f'{float(no_centre):.15f}',
        'external_pr_source': {'head': source['head'], 'blob': source['git_blob'], 'sha256': source['sha256']}
    }, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
