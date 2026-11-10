"""Read-only author-side audit of the odd-grid package.

Independent fixed-grid integer word engine and positive transfer matrix caller
engine. This does not prove native/endpoint identities or run a physical tape.
Prepared for @CubeJerry with substantial OpenAI assistance.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import ast
import gzip
import json

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source/data"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rational(text):
    bits = str(text).split("/")
    return (int(bits[0]), int(bits[1]) if len(bits) == 2 else 1)


def height(n):
    need(n > 0 and n & (n - 1) == 0, "dyadic denominator")
    return n.bit_length() - 1


def reduced(n, d):
    g = gcd(n, d)
    return str(n // g) if d // g == 1 else f"{n//g}/{d//g}"


def word_run(word, scale=1125, frac=24):
    """Store every formal row on the *one fixed* scale*2^frac integer grid."""
    n = len(word["initial"])
    unit = 1 << frac
    rows = [{i: scale * unit} for i in range(n)]
    rows += [{} for _ in range(word["owned_fields"])]
    frames = list(word["initial"]) + [None] * word["owned_fields"]
    live = set()
    peak, odd_lcm, high, visits = scale * unit, 1, 0, 0
    numerator_bits = 0
    witness = None

    def observe(row, index, kind):
        nonlocal peak, odd_lcm, high, visits, witness
        mass = sum(abs(value) for value in row.values())
        if mass > peak:
            peak, witness = mass, (index, kind)
        for value in row.values():
            if not value:
                continue
            odd_lcm = lcm(odd_lcm, scale // gcd(value, scale))
            trailing = (abs(value) & -abs(value)).bit_length() - 1
            high = max(high, frac - trailing)
            visits += 1

    def multiply(row, q, index):
        a, b = rational(q)
        result = {}
        for key, value in row.items():
            quotient, residue = divmod(value * a, b)
            need(residue == 0, f"integer grid rejection at event {index}: denominator {b}")
            if quotient:
                result[key] = quotient
        return result

    for index, event in enumerate(word["program"]):
        op, target = event[:2]
        if op == "INIT":
            need(target >= n and target not in live, "fresh owner")
            live.add(target); rows[target] = {}; frames[target] = event[2]
        elif op == "CLEAR":
            need(target in live and frames[target] == event[2], "owner clear")
            live.remove(target); rows[target] = {}; frames[target] = None
        elif op == "MOVE":
            need(frames[target] == event[2], "source chart")
            frames[target] = event[3]
        elif op == "SCALE":
            need(frames[target] == event[3], "scale chart")
            numerator_bits = max(numerator_bits, abs(rational(event[2])[0]).bit_length())
            rows[target] = multiply(rows[target], event[2], index)
            observe(rows[target], index, "scale")
        elif op in ("ADD", "COPY"):
            source = event[2]
            need(target != source and frames[target] == frames[source] == event[4], "common chart")
            need(op != "COPY" or target in live and not rows[target], "copy zero")
            numerator_bits = max(numerator_bits, abs(rational(event[3])[0]).bit_length())
            product = multiply(rows[source], event[3], index)
            observe(product, index, "pre-add product")
            result = rows[target].copy()
            for key, value in product.items():
                result[key] = result.get(key, 0) + value
                if not result[key]:
                    del result[key]
            rows[target] = result
            observe(result, index, "stored add")
        else:
            raise ValueError(op)
    need(not live and frames[:n] == word["final"], "completed owned/frame endpoints")
    need(all(value % scale == 0 for row in rows[:n] for value in row.values()), "unscaled public rows dyadic")
    need(all(not row for row in rows[n:]), "private rows gone")
    return dict(odd_scale_lcm=odd_lcm, dyadic_height=high,
                maximum_scaled_mass=reduced(peak, unit), mass_witness=witness,
                numerator_bits=numerator_bits, coefficient_visits=visits)


def caller_run(caller):
    """Propagate all 78 positive input contributions on a common integer grid.

    Matrix entries count triangle-inequality contributions; they do not commute
    Clifford words or evaluate numerical characters. The common scale only
    grows and all divisions below are integer-exact after that scale change.
    """
    count = caller["roles"]
    rows = [[int(i == j) for j in range(count)] for i in range(count)]
    debts = [0] * count
    scale = 0
    maximum = pre_joint = (1, 0)
    maximum_debt = joint_debt = 0

    def larger(pair, candidate):
        a, k = pair; b, ell = candidate
        return candidate if (b << k) > (a << ell) else pair

    def denominator(bits):
        nonlocal scale, rows
        if bits:
            rows = [[value << bits for value in row] for row in rows]
            scale += bits

    for event in caller["events"]:
        if event[0] == "J":
            pre_joint = larger(pre_joint, (max(map(sum, rows)), scale))
            joint_debt = max(joint_debt, *debts)
            s, t, x, y = event[2]
            bs, bt, alpha, beta = event[3]
            need(len({s, t, x, y, bs, bt}) == 6, "joint owner separation")
            need(rational(alpha) == (-1, 1) and rational(beta) == (1, 2), "actual B pair")
            a, b = rational(caller["types"]["A"]["alpha2"])
            need(b == 1, "actual A integer shear")
            denominator(1)
            rows[t] = [u + v for u, v in zip(rows[t], rows[s])]
            rows[x] = [u + abs(a) * v for u, v in zip(rows[x], rows[y])]
            combo = [u + v for u, v in zip(rows[bs], rows[bt])]
            need(all(v % 2 == 0 for v in combo), "B integer halving")
            rows[bs], rows[bt] = combo, [v // 2 for v in combo]
            debts[t], debts[x] = max(debts[t], debts[s]), max(debts[x], debts[y])
            newdebt = max(debts[bs], debts[bt])
            debts[bs], debts[bt] = newdebt, newdebt + 1
        else:
            op, t = event[1:3]
            if op in ("ADD", "SCALE"):
                a, b = rational(event[4] if op == "ADD" else event[3])
                k = height(b); denominator(k)
                if op == "ADD":
                    source = event[3]
                    need(all(abs(a) * v % b == 0 for v in rows[source]), "ADD integer grid")
                    rows[t] = [u + abs(a) * v // b for u, v in zip(rows[t], rows[source])]
                    debts[t] = max(debts[t], debts[source] + k)
                else:
                    need(all(abs(a) * v % b == 0 for v in rows[t]), "SCALE integer grid")
                    rows[t] = [abs(a) * v // b for v in rows[t]]
                    debts[t] += k
            elif op == "QUERY":
                source = event[3]
                rows[t] = [u + v for u, v in zip(rows[t], rows[source])]
                debts[t] = max(debts[t], debts[source])
            elif op == "SWAP":
                source = event[3]
                rows[t], rows[source] = rows[source], rows[t]
                debts[t], debts[source] = debts[source], debts[t]
            elif op == "LAMBDA":
                rows[t] = [2 * v for v in rows[t]]
                debts[t] += 1
            elif op != "IDLE_ONE":
                raise ValueError(op)
        maximum = larger(maximum, (max(map(sum, rows)), scale))
        maximum_debt = max(maximum_debt, *debts)
    return dict(maximum_mass=reduced(maximum[0], 1 << maximum[1]),
                pre_joint_mass=reduced(pre_joint[0], 1 << pre_joint[1]),
                denominator_height=maximum_debt, pre_joint_height=joint_debt)


def threshold_run():
    """Read source literals by AST and regenerate the threshold by integers."""
    check = SOURCE.parent / "check.py"
    nodes = ast.parse(check.read_text()).body
    values = {}
    for node in nodes:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Tuple) and all(isinstance(x, ast.Name) for x in target.elts):
            names = [x.id for x in target.elts]
            if names == ["KAPPA", "TESTED"]:
                for name, value in zip(names, node.value.elts):
                    need(isinstance(value, ast.Call) and isinstance(value.args[0], ast.Constant), "price source literal")
                    digits = value.args[0].value
                    before, after = digits.split(".")
                    values[name] = (int((before or "0") + after), 10 ** len(after))
            elif names == ["LPMIN", "LP"]:
                values["LP"] = node.value.elts[1].value
    a, b = values["KAPPA"]
    c, d = values["TESTED"]
    numerator, denominator = c*b-a*d, 7*b*d
    common = gcd(numerator, denominator)
    need(numerator // common == 1, "unit exact source gap")
    step = denominator // common
    power = values["LP"]
    def wins(j):
        return pow(step*j+1, power) < 1 << j
    lo, hi = 1, 2
    while not wins(hi):
        lo, hi = hi, hi*2
    while hi-lo > 1:
        mid = (hi+lo)//2
        if wins(mid):
            hi = mid
        else:
            lo = mid
    h = step*hi
    need(wins(hi) and not wins(hi-1), "threshold neighbors")
    kstar = 1920*pow(153, 1920)*pow(h+1, 2)
    need(h == 1339210000000000000 and kstar.bit_length() == 14066
         and (357*kstar).bit_length() == 14075 < h, "symbolic threshold margin")
    return {"H": h, "integer_threshold_index": hi, "gap_denominator": step,
            "logarithm_power": power, "Kstar_bits": kstar.bit_length(),
            "357Kstar_bits": (357*kstar).bit_length(),
            "source_check_sha256": sha256(check.read_bytes()).hexdigest()}


def main():
    word = json.loads(gzip.decompress((SOURCE / "word.json.gz").read_bytes()))
    caller = json.loads((SOURCE / "caller.json").read_text())
    result = {"source_sha256": {n: sha256((SOURCE/n).read_bytes()).hexdigest()
                                 for n in ("word.json.gz", "caller.json")},
              "word": word_run(word), "caller": caller_run(caller), "negative_scales": {}}
    for scale in (375, 225):
        try:
            word_run(word, scale=scale)
        except ValueError as error:
            result["negative_scales"][str(scale)] = str(error)
        else:
            raise ValueError("insufficient odd scale was accepted")
    expected = json.loads((ROOT / "EXPECTED-BOUNDS.json").read_text())
    for key in ("dyadic_height", "maximum_scaled_mass", "coefficient_visits"):
        need(result["word"][key] == expected["word"][key], "independent word agreement: " + key)
    need(result["word"]["odd_scale_lcm"] == 1125, "minimal source-derived scale")
    need(result["word"]["numerator_bits"] == 24, "literal numerator width")
    for key in ("maximum_mass", "denominator_height", "pre_joint_height"):
        need(result["caller"][key] == expected["caller"][key], "independent caller agreement: " + key)
    result["threshold"] = threshold_run()
    print(json.dumps(result, sort_keys=True, indent=2))
    print("PASS_INDEPENDENT_ODD_GRID_BOUNDS")


if __name__ == "__main__":
    main()
