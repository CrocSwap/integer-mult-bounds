# SPDX-License-Identifier: Apache-2.0
"""Bounded exact arithmetic only; no native/controller/full-release replay.

check(profile) accepts the complete paid histogram and returns a JSON-serializable
receipt. Default inputs are immutable exports and a fresh T488 owner replay.
The caller supplies the physical histogram; this module derives its expected
value from actual before/after local-word bills and the old owner histogram.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal, localcontext
import gzip, hashlib, importlib.util, json

HERE = Path(__file__).resolve().parent
ROOT_LOWER = Q('0.001730418899766071163804')
ROOT_UPPER = ROOT_LOWER + Q(1, 10**24)
SCOPE = ('Finite two-engine rational moment and source-bound profile composition only. '
         'The modern kappa expression is conditional on the separately checked outer transfer. '
         'No native, controller, prefix, precision/tape, exact recovery, all-size compiler, '
         'common-label/mutable-source, whole-call hosting, SCALAR/COPY/CLEAR, zero allocation, '
         'analytic/BIT premises or complete release is established by this module.')

def need(ok, message):
    if not ok:
        raise ValueError(message)

def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def dec(x):
    with localcontext() as context:
        context.prec = 90
        return str(Decimal(x.numerator) / Decimal(x.denominator))

def profile_dict(raw):
    need(isinstance(raw, dict) and bool(raw), 'nonempty profile mapping required')
    result = {}
    for rank, count in raw.items():
        need(type(rank) is int or (type(rank) is str and rank.isdigit() and str(int(rank)) == rank),
             'canonical integer rank required')
        rank = int(rank)
        need(0 < rank < 73 and rank not in result, 'unique child rank in 1..72 required')
        need(type(count) is int and count >= 0, 'nonnegative exact integer count required')
        result[rank] = count
    return {rank: count for rank, count in sorted(result.items()) if count}

def authenticate():
    provenance = read(HERE / 'PROVENANCE.json')
    for item in provenance['files']:
        path = HERE / item['local_path']
        need(sha(path) == item['sha256'], 'source SHA256 mismatch: ' + item['local_path'])
        if 'git_blob' in item:
            raw = path.read_bytes()
            git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            need(git_blob == item['git_blob'], 'Git blob mismatch: ' + item['local_path'])
    return provenance

def load_engine(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def derive_inputs():
    """Authenticate sources and derive the candidate histogram from actual bills."""
    provenance = authenticate()
    owner = read(HERE / 'inputs/OWNER-EXPECTED.json')
    replay = read(HERE / 'inputs/OWNER-PORTABLE-REPLAY.json')
    arithmetic = read(HERE / 'inputs/OLD-ARITHMETIC.json')
    old = profile_dict(read(HERE / 'inputs/OWNER-PROFILE.json'))
    need(old == profile_dict(owner['profile']) == profile_dict(arithmetic['profile']) ==
         profile_dict(replay['primal']['profile']), 'owner-derived old histogram mismatch')
    need(sha(HERE / 'inputs/OWNER-PROFILE.json') == owner['literal_files']['PROFILE.json'],
         'published owner histogram digest')
    need(replay['status'] == 'PASS_STANDARD_LIBRARY_SEMANTIC_LITERAL_REPLAY', 'portable owner status')
    for key in ('replicas', 'calls', 'physical'):
        need(owner[key] == replay[key] == arithmetic[key], 'owner normalization: ' + key)
    need(owner['rows'] == replay['roles'] == arithmetic['roles'], 'owner roles/rows normalization')
    replicas, calls = owner['replicas'], owner['calls']
    need(replicas == 488 and calls == 9 * replicas, 'T488 4392-call normalization')
    need(owner['payload_sha256'] == replay['materialized']['payload_sha256'], 'literal owner payload binding')
    live = replicas * 896
    deltas, bills = [], {}
    for tag in ('base', 'extra'):
        before = read(HERE / f'inputs/OLD-{tag}.json.gz')
        after = read(HERE / f'inputs/NEW-{tag}.json.gz')
        for field in ('start_extra', 'helper_final', 'removed', 'warps', 'center_frames', 'cut', 'restore', 'A'):
            need(field in before and field in after and before[field] == after[field], 'preserved word field ' + field)
        need(before['report']['width_inventory'] == after['report']['width_inventory'], 'unchanged width inventory')
        first, second = (profile_dict(x['report']['local_profile']) for x in (before, after))
        delta = {r: second.get(r, 0) - first.get(r, 0) for r in first.keys() | second.keys()}
        delta = {r: n for r, n in delta.items() if n}
        need(sum(r * n for r, n in delta.items()) == 0, 'local rank mass must remain unchanged')
        deltas.append(delta)
        bills[tag] = {'old': first, 'new': second, 'delta': delta}
    need(deltas[0] == deltas[1], 'two providers must have identical arithmetic delta')
    delta = deltas[0]
    need(delta == {1: -2, 2: -2, 3: 2}, 'authenticated release-retiming delta')
    derived = {r: old.get(r, 0) + calls * delta.get(r, 0) for r in old.keys() | delta.keys()}
    derived = profile_dict(derived)
    need(sum(r * n for r, n in derived.items()) == sum(r * n for r, n in old.items()), 'global rank mass invariant')
    need(73 * live - sum(r * n for r, n in derived.items()) == live - 64 * calls, 'same complete coverage deficit')
    comparator = read(HERE / 'inputs/PR3642-CLAIM.json')
    outer = read(HERE / 'inputs/PR3642-OUTER-CLAIM.json')
    moment = read(HERE / 'inputs/PR3642-MOMENT.json')
    prior = Q(comparator['kappa'])
    need(prior == Q(outer['kappa_rational']) == Q(outer['kappa']) == Q(moment['candidate_modern_kappa']),
         'PR3642 recorded and exported modern claims must agree')
    return dict(provenance=provenance, replicas=replicas, calls=calls, live=live,
                old=old, derived=derived, delta=delta, bills=bills, prior=prior,
                old_arithmetic=arithmetic, comparator_moment=moment)

def check(profile):
    """Return exact arithmetic receipt, or raise ValueError; perform no writes.

    profile: dict[int|canonical-decimal-string, nonnegative-int]. It must be the
    complete paid histogram, including idle ranks. The independent caller is
    responsible for deriving it from physical admission; equality is checked.
    """
    data = derive_inputs()
    candidate = profile_dict(profile)
    need(candidate == data['derived'], 'complete profile differs from owner/local-word composition')
    first = load_engine('t488_rational_price', HERE / 'vendor/price.py')
    second = load_engine('t488_prime_interval', HERE / 'vendor/arith.py')
    live = data['live']
    signed = dict(candidate)
    signed[73] = -live
    margins = []
    for endpoint, expect in ((ROOT_LOWER, 'negative'), (ROOT_UPPER, 'positive')):
        a = first.interval(signed, endpoint)
        b = second.moment(candidate, 73, live, endpoint, surcharge=False)
        need(a[1] < 0 and b.hi < 1 if expect == 'negative' else a[0] > 0 and b.lo > 1,
             'two-engine strict root bracket: ' + expect)
        margins.append({'endpoint': str(endpoint), 'endpoint_decimal': dec(endpoint),
                        'signed_sum_interval': first.compact(a),
                        'normalized_moment_minus_one_interval': first.compact((b.lo-1, b.hi-1)),
                        'required_sign': expect})
    # Independently bind both predecessor roots, not merely their title claims.
    predecessors = []
    for label, hist, width, roots in (
        ('PR3633_T488_unretimed', data['old'], live, data['old_arithmetic']['root_interval']),
        ('PR3642_T530_retimed', profile_dict(data['comparator_moment']['new_profile']),
         data['comparator_moment']['live'], data['comparator_moment']['root_interval'])):
        p = dict(hist); p[73] = -width
        lo, hi = map(Q, roots)
        a, z = first.interval(p, lo), first.interval(p, hi)
        b, c = second.moment(hist, 73, width, lo), second.moment(hist, 73, width, hi)
        need(a[1] < 0 < z[0] and b.hi < 1 < c.lo, 'authenticated predecessor root: ' + label)
        predecessors.append({'label': label, 'root_interval': [str(lo), str(hi)],
                             'first_lower': first.compact(a), 'first_upper': first.compact(z),
                             'second_lower': first.compact((b.lo-1,b.hi-1)),
                             'second_upper': first.compact((c.lo-1,c.hi-1))})
    endpoint = ROOT_LOWER - Q(1,10**46) - Q(1,10**70)
    need(endpoint > data['prior'], 'strict gain over authenticated PR3642 modern claim')
    per_call = first.interval(data['delta'], Q(data['old_arithmetic']['root_interval'][1]))
    need(per_call[1] < 0, 'retiming improves paid moment at predecessor upper endpoint')
    return {'status': 'PASS_SOURCE_BOUND_TWO_ENGINE_RETIMED_T488_ARITHMETIC',
            'replicas': data['replicas'], 'calls': data['calls'], 'live': live,
            'old_profile': data['old'], 'new_profile': candidate, 'local_bills': data['bills'],
            'delta_per_call': data['delta'], 'rank_mass': sum(r*n for r,n in candidate.items()),
            'coverage_deficit': 73*live-sum(r*n for r,n in candidate.items()),
            'root_interval': [str(ROOT_LOWER), str(ROOT_UPPER)],
            'root_decimal_interval': [dec(ROOT_LOWER), dec(ROOT_UPPER)],
            'root_margins': margins, 'predecessor_margins': predecessors,
            'strict_delta_interval_per_call': first.compact(per_call),
            'conditional_modern_kappa': str(endpoint), 'conditional_modern_kappa_decimal': dec(endpoint),
            'authenticated_PR3642_modern_kappa': str(data['prior']),
            'gain': str(endpoint-data['prior']), 'gain_decimal': dec(endpoint-data['prior']),
            'gain_percent': dec(100*(endpoint/data['prior']-1)),
            'source_provenance_sha256': sha(HERE/'PROVENANCE.json'),
            'rounding': 'Exact rational interval signs; reported margins rounded outward to 60 decimal places.',
            'scope': SCOPE}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    receipt = check(read(args.profile))
    text = json.dumps(receipt, indent=2) + '\n'
    if args.out:
        args.out.write_text(text)
    else:
        print(text, end='')
