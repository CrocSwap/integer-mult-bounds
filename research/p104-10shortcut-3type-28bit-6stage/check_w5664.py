"""Verify the 10-shortcut Gaussian word w5664_shortcut10.json.gz from #8027 by exact replay."""
from collections import defaultdict
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from math import gcd, prod
from pathlib import Path
import random
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()
from charts import native_catalogue as verify_catalogue
from check_complex import all_images
from phase_atlas import catalogue as phase_catalogue
from spool import short_divisors
from strong_complex import DYADIC, GRID, LAYOUT, ODD, WORD, digest

W5664_GZ_SHA = "ce395afbf5c32be64c4e62389acaf9ce8cf8a9aaaa2fb7a278135bcfa0e635aa"
W5664_DIGEST = "668125b34a34c9a59a97bd66a236118d1d32f19b60dcd872b29f7dd690be0c3e"
CAT_DIGEST = "34eef62b6701db0565dce3471f165f4224194ff2782be822774f9c1255553a8d"


def reconstruct_g0(inputs_dir):
    source = inputs_dir / "complex-source"
    for name, pin in json.loads((inputs_dir / "complex-source.json").read_bytes()).items():
        if sha256((source / name).read_bytes()).hexdigest() != pin:
            raise ValueError(f"Complex source differs at {name}")
    sys.path.insert(0, str(source))
    from sparse_helpers import rebuild
    from verify_split_helpers import read, reconstruct

    parent, layout = rebuild()
    g0, _ = reconstruct(parent, read("BANK-FACTORS.json.gz"))
    assert digest(g0) == WORD and digest(layout) == LAYOUT
    return g0, layout


def verify_linear_maps(g0, w10):
    n_in = len(g0["initial"])
    n_out = len(g0["final"])
    assert len(w10["initial"]) == n_in and len(w10["final"]) == n_out
    for key in ("initial", "final", "frames", "first_output"):
        assert w10[key] == g0[key], f"Changed field {key}"
    assert (len(g0["moves"]), len(w10["moves"])) == (5674, 5664)
    for P in (1000000007, 1000000009, 998244353):
        rng = random.Random(P)
        x = {~i: rng.randrange(1, P) for i in range(n_in)}
        y_w = [rng.randrange(1, P) for _ in range(n_out)]

        def fwd(g):
            fm = {
                fid: [(d, (Q(q).numerator * pow(Q(q).denominator, -1, P)) % P) for d, q in terms]
                for fid, terms in g["forms"]
            }
            val = dict(x)
            for fid in g["schedule"]:
                val[fid] = sum(c * val[d] for d, c in fm[fid]) % P
            fo = g["first_output"]
            return [val[fo + i] for i in range(n_out)]

        def trans(g):
            fm = {
                fid: [(d, (Q(q).numerator * pow(Q(q).denominator, -1, P)) % P) for d, q in terms]
                for fid, terms in g["forms"]
            }
            adj = defaultdict(int)
            fo = g["first_output"]
            for i, w in enumerate(y_w):
                adj[fo + i] = w
            for fid in reversed(g["schedule"]):
                af = adj.get(fid, 0)
                if af:
                    for d, c in fm[fid]:
                        adj[d] = (adj[d] + af * c) % P
            return [adj[~i] for i in range(n_in)]

        fg = fwd(w10)
        tg = trans(w10)
        assert fwd(g0) == fg
        assert trans(g0) == tg
        assert sum(w * v for w, v in zip(y_w, fg)) % P == sum(x[~i] * t for i, t in enumerate(tg)) % P


def verify_literal_grid(graph, layout):
    size = len(graph["initial"])
    stocks = {~i: {i: GRID} for i in range(size)}
    moves = {k for k, _, _ in graph["moves"]}
    rows = {k: [(s, Q(q)) for s, q in row] for k, row in graph["forms"]}
    masses = {~i: Q(1) for i in range(size)}
    expected = [{i: GRID} for i in range(size)]
    hosted = layout["hosted"]
    for i, x in enumerate(layout["live"]):
        y = x + 112
        if i in hosted["Dports"]:
            expected[y][x] = GRID
        else:
            expected[x][y] = -GRID
            expected[y] = {x: GRID // 2, y: GRID // 2}
    for x, y in zip(hosted["X2"], hosted["Y2"], strict=True):
        expected[x][y] = -GRID

    peak = Q(1)
    largest_limb = maximum_literal = products = nontrivial = 0
    common = GRID
    literals = set()
    for node in graph["schedule"]:
        values, mass = {}, Q(0)
        for src, coeff in rows[node]:
            a, b = coeff.numerator, coeff.denominator
            literals.add(coeff)
            mass += abs(coeff) * masses[src]
            for i, old in stocks[src].items():
                q, rem = divmod(old, b)
                assert rem == 0, "inexact term before multiplication"
                term = a * q
                if common != 1:
                    common = gcd(common, term)
                values[i] = values.get(i, 0) + term
            products += len(stocks[src])
            nontrivial += (b != 1) * len(stocks[src])
        peak = max(peak, mass)
        result = {i: v for i, v in values.items() if v}
        if node in moves:
            stocks[node] = result
            masses[node] = mass
        else:
            assert result == expected[node - graph["first_output"]], "wrong inverse endpoint"

    for coeff in literals | {Q(1, ODD), Q(ODD)}:
        factors = short_divisors(coeff.denominator)
        assert prod(factors) == coeff.denominator and all(1 < v < 2**24 for v in factors)
        maximum_literal = max(maximum_literal, coeff.numerator.bit_length(), coeff.denominator.bit_length())
        largest_limb = max(largest_limb, *factors, 0)
    assert common == 1 and (ODD << DYADIC) == GRID and ODD % 2 == 1
    assert products == 25142049 and nontrivial == 17229517
    assert (
        str(peak)
        == "205356183613811630452617549443093585249505045823/1621896683681232672237748224000"
    )
    assert len(literals) == 60189 and largest_limb == 16641408 and maximum_literal == 87


def main():
    if not __debug__:
        raise RuntimeError("Enable assertions for w5664 checks")
    gz_path = RUNTIME / "w5664_shortcut10.json.gz"
    raw_gz = gz_path.read_bytes()
    assert sha256(raw_gz).hexdigest() == W5664_GZ_SHA
    w10 = json.loads(gzip.decompress(raw_gz).decode("utf-8"))
    assert digest(w10) == W5664_DIGEST
    g0, layout = reconstruct_g0(RUNTIME / "inputs")
    verify_linear_maps(g0, w10)
    cat = phase_catalogue(w10, layout)
    assert digest(cat) == CAT_DIGEST and len(cat["pairs"]) == 2961
    checked = verify_catalogue(w10, layout, cat)
    imgs = all_images(checked)
    assert imgs == {
        "factor_occurrences": 6130,
        "distinct_factors": 3783,
        "basis_images": 1936896,
        "maximum_factor_records": 93,
    }
    verify_literal_grid(w10, layout)
    print(
        "PASS_W5664_SHORTCUT10",
        json.dumps(
            {
                "gz_sha256": W5664_GZ_SHA,
                "word_digest": W5664_DIGEST,
                "catalogue_digest": CAT_DIGEST,
                "moves": len(w10["moves"]),
                "images": imgs,
                "products": 25142049,
                "nontrivial": 17229517,
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
