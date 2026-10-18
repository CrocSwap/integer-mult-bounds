"""kappa: exact conditional kappa of a gauge44/k8-lineage global paid profile, computed as the packages' assemble.py does:
the certified complex moment root on the 1e-24 grid (k492/multicold engines), then the retained outer assembly (47 strict
constraints) with the PR589 bit supplier. Any replica count T: live = 896 T, deficit = 320 T, m = 73.

usage: python -B kappa.py --local '{"1":2412,"2":418,"3":432,"4":142,"5":82,"8":8}' --calls 144 --T 16 \\
           --idle '{"1":2276,"3":377,"7":7,"48":4866}'          # prints 0.001672660197076918 (#1094)"""
import argparse, collections, importlib.util, json
from fractions import Fraction as Q
from paths import MULTICOLD, PR589_EXPECTED

def _load(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
M, B2, A = [_load("eft_" + n, MULTICOLD / "engines" / (n + ".py")) for n in ("moment", "base_two_moment", "outer")]
C_BIT_589 = Q(json.loads(PR589_EXPECTED.read_text())["nine"]["bit_lower"])
M_DIM = 73

def live_deficit(T): return 896 * T, 320 * T

def complex_lower(H, T):
    """certified lower endpoint b of the complex moment problem for global profile H with T replicas."""
    live, deficit = live_deficit(T); H = {int(r): n for r, n in H.items() if n}
    assert M_DIM * live - sum(r * n for r, n in H.items()) == deficit, ("rank mass must leave the fixed deficit", M_DIM * live - sum(r * n for r, n in H.items()), deficit)
    return Q(M.certify(H, M_DIM, live, False)["lower"])

def outer_witness(bb, c=C_BIT_589):
    """assemble.py's outer witness: kappa on the 1e-18 grid from the complex endpoint bb and the bit endpoint c."""
    eta = beta = Q(1, 10 ** 24); s = min(c, (1 - beta) * bb) - Q(1, 10 ** 27); assert 0 < s < c and s < (1 - beta) * bb
    chain = [Q(384599, 10 ** 10)]
    for _ in range(7):
        old = chain[-1]; a = (1 - s) * s + s * old; gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s); assert old < a < s < 1 - a and gap > 0
        ceil = lambda x: -(-x.numerator // x.denominator); cut = max(ceil(36 / gap ** 2), ceil(2 * (4 + 512) / gap)); assert cut * gap ** 2 >= 36 and cut * gap >= 2 * (4 + 512)
        chain.append(a)
    q = chain[-1] * (1 - 2 * eta); margin = (1 - eta) * q / (1 + q); ticks = margin * 10 ** 18; k = Q((ticks.numerator - 1) // ticks.denominator, 10 ** 18)
    bridge = {"semantic": {"C0": {"base": 2, "exponent": 210000}, "strict_literal_gap": 1}, "rows": {"degree_gap": Q(10 ** 6) - Q(51 * 20161, 25)}}
    outer = A.assembly(chain[-1], bb, bridge, k, eta=eta, beta=beta); assert len(outer["strict_constraints"]) == 47 and all(v > 0 for v in outer["strict_constraints"].values())
    return k

def kappa(H, T):
    b = complex_lower(H, T); return outer_witness(b), b

def global_profile(calls_by_local, idle):
    """calls_by_local: [(n_calls, local paid profile incl. centre descents)]; idle: idle remainder children of the owner map."""
    g = collections.Counter()
    for n, loc in calls_by_local:
        for r, c in loc.items(): g[int(r)] += n * c
    for r, c in idle.items(): g[int(r)] += c
    return dict(g)

def price(local, calls, T, idle):
    """kappa of one local word hosted by an owner map with the given idle remainder profile (widths unchanged)."""
    return kappa(global_profile([(calls, local)], idle), T)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--local", required=True); ap.add_argument("--calls", type=int, required=True); ap.add_argument("--T", type=int, required=True)
    ap.add_argument("--idle", required=True); a = ap.parse_args()
    k, b = price({int(r): n for r, n in json.loads(a.local).items()}, a.calls, a.T, {int(r): n for r, n in json.loads(a.idle).items()})
    print("complex_lower", b, "| kappa", k, "=", f"{float(k):.18f}")
