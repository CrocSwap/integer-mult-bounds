"""Exact selected-source binding; independent of predecessor executables.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ident(n):
    return [{i: F(1)} for i in range(n)]


def plus(a, b, scale=1):
    require(len(a) == len(b), "row count mismatch")
    out = [row.copy() for row in a]
    for dst, src in zip(out, b):
        for j, x in src.items():
            v = dst.get(j, F(0)) + scale*x
            if v:
                dst[j] = v
            else:
                dst.pop(j, None)
    return out


def mul(a, b):
    out = []
    for row in a:
        dst = {}
        for k, x in row.items():
            for j, y in b[k].items():
                dst[j] = dst.get(j, F(0)) + x*y
        out.append({j: x for j, x in dst.items() if x})
    return out


def chart(R, K, P, L):
    r, n = len(R), len(K)
    require(mul(R, P) == ident(r), "RP is not identity")
    require(mul(L, K) == ident(r), "LK is not identity")
    require(not any(mul(L, P)), "LP is not zero")
    M = mul(R, K)
    Q = plus(R, L, -1)
    Z = plus(K, mul(P, plus(M, ident(r), -1)), -1)
    G = plus(plus(ident(n), mul(Z, Q)), mul(P, R), -1)
    Gi = plus(plus(ident(n), mul(P, L)), mul(Z, R), -1)
    require(mul(Q, P) == mul(L, Z) == ident(r), "section left inverses")
    require(not any(mul(Q, Z)), "sections not disjoint")
    require(mul(G, P) == Z and mul(G, Z) == plus(Z, P, -1), "active action")
    require(mul(Gi, P) == plus(P, Z, -1) and mul(Gi, Z) == P, "active inverse")
    require(mul(R, G) == Q and mul(R, Gi) == L, "query action")
    projection = plus(mul(P, Q), mul(Z, L))
    W = plus(ident(n), projection, -1)
    require(mul(G, W) == W and mul(Gi, W) == W, "fixed complement")
    require(mul(projection, projection) == projection, "not a projection")
    require(sum(projection[i].get(i, 0) for i in range(n)) == 2*r, "section rank")
    return {"G": G, "inverse": Gi, "M": M, "P": P, "L": L,
            "fixed_dimension": n-2*r}


def sources():
    pins = json.loads((HERE / "ARCHIVE.json").read_text())
    path = ROOT / pins["path"]
    require(sha256(path.read_bytes()).hexdigest() == pins["sha256"], "archive pin")
    out = {}
    with tarfile.open(path, "r:gz") as archive:
        for name, pin in pins["members"].items():
            entries = [m for m in archive.getmembers() if m.name == name]
            require(len(entries) == 1 and entries[0].isfile(), "ambiguous archive member")
            raw = archive.extractfile(entries[0]).read()
            require(sha256(raw).hexdigest() == pin["sha256"], "member pin")
            raw = gzip.decompress(raw)
            require(sha256(raw).hexdigest() == pin["payload_sha256"], "payload pin")
            out[Path(name).name] = json.loads(raw)
    predecessor = json.loads((HERE / "PREDECESSOR.json").read_text())
    for item in predecessor["sources"]:
        require(sha256((HERE/item["local_path"]).read_bytes()).hexdigest()
                == item["sha256"], "predecessor text pin")
    return out


def extract_query(word, program):
    """Replay source columns only; helper/private outputs are not audited."""
    v = word["v"]
    n = 2*v + word["R"]
    require((v, n, word["h"]) == (112, 704, 9), "supplier dimensions")
    rows = ident(v) + [{} for _ in range(n+8-v)]
    cut = ["phase", "centers"]
    require(program.count(cut) == 1, "ambiguous centre cut")
    for event in program[:program.index(cut)]:
        if event[0] != "scalar":
            continue
        op = event[1]
        def at(port):
            require(port[0] in ("C", "L"), "unknown field")
            return port[1] + (n if port[0] == "C" else 0)
        dst = at(op[1])
        if op[0] == "clear":
            rows[dst] = {}
        elif op[0] == "copy":
            rows[dst] = rows[at(op[2])].copy()
        elif op[0] == "scale":
            c = F(op[2], op[3])
            rows[dst] = {j: c*x for j, x in rows[dst].items() if c*x}
        else:
            require(op[0] == "add", "unknown scalar operation")
            rows[dst] = plus([rows[dst]], [rows[at(op[2])]], F(op[3], op[4]))[0]
    R = [rows[c] for c in word["centers"]]
    require(len(R) == 8, "query dimension")
    return R


def cyclo_mul(x, y):
    # Q[t]/(t^2-t+1), represented by a+b*t.
    a, b = x
    c, d = y
    return (a*c-b*d, a*d+b*c+b*d)


def cyclo_power(k):
    t = (0, 1) if k >= 0 else (1, -1)
    out = (1, 0)
    for _ in range(abs(k)):
        out = cyclo_mul(out, t)
    return out


def winding(operations):
    tariff = {"B": 1, "F": -1, "B_inverse": -1, "F_inverse": 1}
    require(all(x in tariff for x in operations), "unknown macro")
    return sum(tariff[x] for x in operations)


def run():
    data = sources()
    R = extract_query(data["CANONICAL-WORD.json.gz"], data["LOCAL-PROGRAMS.json.gz"]["forward"])
    K = [{k: R[k][p]/4 for k in range(8) if p in R[k]} for p in range(112)]
    A = [0, 7, 20, 27, 36, 46, 57, 111]
    T = [21, 37, 47, 76, 81, 87, 92, 110]
    def make(a, t):
        P = [row.copy() if p in a else {} for p, row in enumerate(K)]
        L = [{p: c for p, c in row.items() if p in t} for row in R]
        return chart(R, K, P, L)
    base, alternate = make(A, T), make(T, A)
    require(base["M"] == [{k: F(14)} for k in range(8)], "RK is not 14I")
    require(base["fixed_dimension"] == 96, "fixed complement dimension")
    for b in (base, alternate):
        for c in (base, alternate):
            defect = mul(mul(R, plus(b["G"], c["inverse"], -1)), K)
            require(defect == [{k: F(12)} for k in range(8)], "three-call rank witness")
    locals_ = [x for x in data["GLOBAL-TEMPLATE.json.gz"]["recipe"] if x["kind"] == "local"]
    require([(x["pair"], x["reverse"], x["stage"]) for x in locals_] == [
        (0, False, 0), (0, True, 1), (0, False, 2),
        (1, True, 3), (1, False, 4), (2, True, 5),
        (2, False, 6), (3, True, 7), (3, False, 8)], "four-pair nine-stage recipe")
    sequence = ["B" if x["reverse"] else "F" for x in locals_]
    require(Counter(sequence) == {"B": 4, "F": 5}, "orientation count")
    require(winding(sequence) == -1, "selected signed winding")
    residues = [list(cyclo_power(k)) for k in range(6)]
    require(len(set(map(tuple, residues))) == 6 and cyclo_power(6) == (1, 0), "exact order six")
    for k in range(-60, 61):
        require((cyclo_power(k) == (1, 0)) == (k % 6 == 0), "congruence control")
    require(cyclo_power(winding(sequence)) != (1, 0), "nine-stage obstruction lost")
    require(winding(["B", "B_inverse"]) == winding(["B", "F"]) == 0, "inverse sign control")
    require(cyclo_power(3) == (-1, 0), "third power must not be called identity")
    # An active-sector-only determinant could incorrectly cancel this -1.
    require((-1)*cyclo_power(3)[0] == 1 and -1 != 1, "missing-complement control")
    badP = [row.copy() for row in base["P"]]
    badP[A[0]] = {}
    try:
        chart(R, K, badP, base["L"])
    except ValueError:
        pass
    else:
        raise ValueError("broken selected minor accepted")
    serial = [[str(row.get(j, 0)) for j in range(112)] for row in R]
    return {
        "status": "PASS_NATIVE_CONTROLLER_CONGRUENCE",
        "selected_source_query_sha256": sha256(json.dumps(serial, separators=(",", ":")).encode()).hexdigest(),
        "ports": 112, "query_rank": 8, "fixed_dimension": 96,
        "minimal_polynomial_low_to_high": [-1, 2, -2, 1],
        "active_powers_0_to_5": residues, "recipe": sequence, "signed_winding": -1,
        "required_winding_modulus": 6, "changed_chart_pairs_checked": 4,
        "changed_chart_defect_compression": "12 I_8",
        "changed_chart_defect_rank_lower_bound": 8,
        "selected_frontier_changed": False,
        "coverage": "Source-column prefix and scalar-controller algebra; no native or all-size cold replay."
    }


if __name__ == "__main__":
    result = run()
    raw = json.dumps(result, indent=2) + "\n"
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT.json").write_text(raw)
    else:
        require(not sys.argv[1:], "unknown option")
        require(json.loads((HERE / "RESULT.json").read_text()) == result, "recorded result mismatch")
    print(raw, end="")
