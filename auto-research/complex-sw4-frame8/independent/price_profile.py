"""Independent arithmetic for the frozen gauge44 profile.

The two rational moment engines and outer.assembly are imported unchanged from
the pinned main dependencies; no constructor, owner emitter or invoice is run.
The outer driver is the seven-step formula retained in PR635.
The bit side is the cited merged PR589 supplier (package inputs/PR589-EXPECTED.json,
pinned by git blob), with its rank-mass deficit T(2Kv - L*cst) re-derived here
independently of code/assemble.py.
Prepared for icekylinx with OpenAI GPT-6 Astra assistance. Apache-2.0.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = Path('research/complex-k492-owner-repair/vendor/multicold')
BIT_PATH = HERE.parent/'inputs/PR589-EXPECTED.json'
BIT_BLOB = 'e293ddc557742637f9f679f083a1a282d87b1b13'


def pr589_deficit(word, live):
    # Nine stages, 32 replicas, four pairs: deficit = 32*(2*4*v - 9*cst), cst = sum of the nine COPY ranks.
    v, cst, ranks = word['v'], word['decoder_constant'], word['copy_ranks']
    require(len(ranks) == word['retained_totals'] == 9 and cst == sum(ranks), 'bit decoder constant')
    require(live == 2*4*v*32, 'bit live wires')
    return 32*(2*4*v-9*cst)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def decimal(q):
    with localcontext() as ctx:
        ctx.prec = 75
        return str(Decimal(q.numerator) / Decimal(q.denominator))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location('independent_' + name, path / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def moment_checks(M, B, H, m, W, lower, deficit, bad):
    require(m*W-sum(r*n for r, n in H.items()) == deficit, 'rank deficit')
    require(m*m > 2*max(H)**2, 'halving guard')
    rows = []
    for z, accept in [(lower, True), (lower+Q(1, 10**24), False)]:
        l, u = M.moment(H, m, W, z, bad)
        ll, uu = B.moment(m, W, list(H.items()), z)
        if bad:
            fl, fu = B.moment(m, W, [(1, 32*m*m*sum(H.values()))], z)
            ll, uu = ll+fl/10**16, uu+fu/10**16
        require((u < 1 and uu < 1) if accept else (l > 1 and ll > 1), 'two exact moment signs')
        rows.append(dict(endpoint=str(z), accept=accept,
                         mercator_residual=[str(l-1), str(u-1)],
                         base_two_residual=[str(ll-1), str(uu-1)]))
    return rows


def outer47(c, b, engine):
    eta = beta = Q(1, 10**24)
    s = min(c, (1-beta)*b)-Q(1, 10**27)
    require(0 < s < c and s < (1-beta)*b, 'strict common saving')
    a = Q(384599, 10**10)
    for _ in range(7):
        old = a
        a = (1-s)*s+s*old
        gap = min(s-a, 1-a-s, 1-a-s*(1-old), 1-s)
        require(old < a < s < 1-a and gap > 0, 'bootstrap gap')
        ceil = lambda x: -(-x.numerator//x.denominator)
        cut = max(ceil(36/gap**2), ceil(2*(4+512)/gap))
        require(cut*gap**2 >= 36 and cut*gap >= 2*(4+512), 'finite bootstrap cutoff')
    q = a*(1-2*eta)
    margin = (1-eta)*q/(1+q)
    ticks = margin*10**18
    k = Q((ticks.numerator-1)//ticks.denominator, 10**18)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
              'rows': {'degree_gap': Q(10**6)-Q(51*20161, 25)}}
    result = engine.assembly(a, b, bridge, k, eta=eta, beta=beta)
    require(len(result['strict_constraints']) == 47, '47 outer constraints')
    require(all(x > 0 for x in result['strict_constraints'].values()), 'strict outer constraints')
    rejected = []
    for name, kk, ee, be in [('next_grid', k+Q(1, 10**18), eta, beta),
                             ('zero_eta', k, Q(0), beta), ('zero_beta', k, eta, Q(0)),
                             ('unit_beta', k, eta, Q(1))]:
        try:
            engine.assembly(a, b, bridge, kk, eta=ee, beta=be)
        except AssertionError:
            rejected.append(name)
        else:
            raise RuntimeError('accepted negative control: '+name)
    return dict(complex_b=str(b), bit_c=str(c), kappa=str(k), kappa_decimal=decimal(k),
                binding='bit' if c < (1-beta)*b else 'complex',
                strict_constraints_passed=47, controls_rejected=rejected)


def main():
    require(__debug__, 'Do not use python -O: the retained outer engine requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', type=Path, required=True, help='Pinned main checkout')
    parser.add_argument('--profile', type=Path, default=HERE.parent/'data/PLAN.json',
                        help='Raw profile or a JSON object containing profile/global_profile')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--headroom-c', help='Optional alternative bit saving, for comparison only')
    args = parser.parse_args()
    inputs = json.loads((HERE.parent/'data/UPSTREAM-PINS.json').read_text())
    selected = [SOURCE/'engines'/(n+'.py') for n in ('moment', 'base_two_moment', 'outer')]
    for relative in selected:
        require(sha(args.main/relative) == inputs[relative.as_posix()], 'pinned input '+str(relative))
    M, B, A = [load(args.main/SOURCE/'engines', n) for n in ('moment', 'base_two_moment', 'outer')]
    supplied = json.loads(args.profile.read_text())
    H = {int(r): n for r, n in supplied.get('profile', supplied.get('global_profile', supplied)).items()}
    bit_data = BIT_PATH.read_bytes()
    require(hashlib.sha1(b'blob '+str(len(bit_data)).encode()+b'\0'+bit_data).hexdigest() == BIT_BLOB, 'PR589 blob pin')
    record = json.loads(bit_data)
    bit = record['nine']
    require('nine-stage' in bit['pipeline'] and '32 replicas' in bit['pipeline'], 'nine-stage bit record')
    bit_deficit = pr589_deficit(record['word'], bit['bit']['live'])
    require(sum(int(r)*n for r, n in bit['profile'].items()) == bit['bit']['rank_mass'], 'bit rank mass')
    c = Q(bit['bit_lower'])
    bit_checks = moment_checks(M, B, {int(r): n for r, n in bit['profile'].items()},
                               64, bit['bit']['live'], c, bit_deficit, True)
    prices = {}
    for mode, bad in [('native', False), ('conservative', True)]:
        root = M.certify(H, 73, 7168, bad)
        root = {key: root[key] for key in ('lower', 'upper', 'lower_endpoint_residual_upper',
                                          'upper_endpoint_residual_lower', 'strict_rational_signs')}
        b = Q(root['lower'])
        row = dict(root=root, exact_moments=moment_checks(M, B, H, 73, 7168, b, 2560, bad),
                   outer_with_bit=outer47(c, b, A))
        if args.headroom_c:
            alternate = outer47(Q(args.headroom_c), b, A)
            require(alternate['kappa'] == row['outer_with_bit']['kappa'], 'headroom comparison changed kappa')
            row.update(outer_with_alternative_bit_rate=alternate, same_kappa_with_either_bit_rate=True)
        prices[mode] = row
    native_k = Q(prices['native']['outer_with_bit']['kappa'])
    result = dict(status='PASS_FROZEN_PROFILE_TWO_EXACT_ENGINE_AND_OUTER47_CROSSCHECK',
                  profile_input_file=args.profile.name, profile_input_sha256=sha(args.profile),
                  global_profile=H, live=7168, m=73, rank_mass=sum(r*n for r, n in H.items()), deficit=2560,
                  prices=prices, bit_supplier_pr=589, bit_deficit=bit_deficit, bit_moments_with_surcharge=bit_checks,
                  gain_over_pr635_percent=decimal(100*(native_k/Q('0.001636241501576388')-1)),
                  input_sha256={**{relative.as_posix(): sha(args.main/relative) for relative in selected}, 'package:inputs/PR589-EXPECTED.json': sha(BIT_PATH)},
                  scope='Independent arithmetic for the exact nominated all72 profile. Complete local, controller and finite invoice admission are separately replayed by the package driver; this receipt does not replace them. The cited PR589 bit supplier is unchanged and its exceptional-residue surcharge is retained. Any alternative c is only a headroom comparison.')
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], prices['native']['outer_with_bit']['kappa_decimal'], result['gain_over_pr635_percent'])


if __name__ == '__main__':
    main()
