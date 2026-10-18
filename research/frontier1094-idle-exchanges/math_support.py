"""Exact local helpers and pinned pricing engine loader for this candidate."""
import gzip
import hashlib
import importlib.util
import json
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE_ROOT = ROOT / 'research/complex-k492-owner-repair/vendor/multicold/engines'
ENGINE_SHA256 = {
    'moment': '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
    'base_two_moment': 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098',
    'outer': 'c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c',
}


def read(path):
    raw = Path(path).read_bytes()
    if str(path).endswith('.gz'):
        raw = gzip.decompress(raw)
    return json.loads(raw)


def dot(a, b):
    return (int(a) & int(b)).bit_count() & 1


def rank(vectors):
    pivots = {}
    for x in map(int, vectors):
        while x:
            bit = x.bit_length() - 1
            if bit in pivots:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                break
    return len(pivots)


def load_engine(name):
    path = ENGINE_ROOT / (name + '.py')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == ENGINE_SHA256[name], (name, digest)
    spec = importlib.util.spec_from_file_location('frontier1094_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decimal(q):
    with localcontext() as ctx:
        ctx.prec = 60
        return str(Decimal(q.numerator) / Decimal(q.denominator))


def price(profile, bad, current, moment, base_two, outer):
    M, W, deficit = 73, 14336, 5120
    assert M * W - sum(r * n for r, n in profile.items()) == deficit
    assert M * M > 2 * max(profile) ** 2
    certified = moment.certify(profile, M, W, bad)
    endpoint = Q(certified['lower'])
    rows = []
    for z, accept in ((endpoint, True), (endpoint + Q(1, 10**24), False)):
        lo, hi = moment.moment(profile, M, W, z, bad)
        blo, bhi = base_two.moment(M, W, list(profile.items()), z)
        if bad:
            slo, shi = base_two.moment(M, W, [(1, 32 * M * M * sum(profile.values()))], z)
            blo += slo / 10**16
            bhi += shi / 10**16
        assert (hi < 1 and bhi < 1) if accept else (lo > 1 and blo > 1)
        rows.append(dict(endpoint=str(z), accept=accept,
                         mercator=[str(lo - 1), str(hi - 1)],
                         base_two=[str(blo - 1), str(bhi - 1)]))

    bit = Q(current['bit_lower'])
    eta = beta = Q(1, 10**24)
    s = min(bit, (1 - beta) * endpoint) - Q(1, 10**27)
    chain = [Q(384599, 10**10)]
    cutoffs = []
    ceil = lambda x: -(-x.numerator // x.denominator)
    for _ in range(7):
        old = chain[-1]
        a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        assert old < a < s < 1 - a and gap > 0
        cutoff = max(ceil(36 / gap**2), ceil(2 * (4 + 512) / gap))
        assert cutoff * gap**2 >= 36 and cutoff * gap >= 2 * (4 + 512)
        cutoffs.append(str(cutoff))
        chain.append(a)
    q = chain[-1] * (1 - 2 * eta)
    ticks = (1 - eta) * q / (1 + q) * 10**18
    kappa = Q((ticks.numerator - 1) // ticks.denominator, 10**18)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000},
                           'strict_literal_gap': 1},
              'rows': {'degree_gap': Q(10**6) - Q(51 * 20161, 25)}}
    assembled = outer.assembly(chain[-1], endpoint, bridge, kappa,
                                eta=eta, beta=beta)
    assert len(assembled['strict_constraints']) == 47
    assert all(x > 0 for x in assembled['strict_constraints'].values())
    try:
        outer.assembly(chain[-1], endpoint, bridge, kappa + Q(1, 10**18),
                       eta=eta, beta=beta)
    except AssertionError:
        pass
    else:
        raise AssertionError('next kappa grid point accepted')
    return dict(endpoint=str(endpoint), endpoint_decimal=decimal(endpoint),
                moments=rows, kappa=str(kappa), kappa_decimal=decimal(kappa),
                cutoffs=cutoffs,
                strict_outer_constraints={k: str(v) for k, v in assembled['strict_constraints'].items()},
                next_grid_rejected=True, binding='complex')
