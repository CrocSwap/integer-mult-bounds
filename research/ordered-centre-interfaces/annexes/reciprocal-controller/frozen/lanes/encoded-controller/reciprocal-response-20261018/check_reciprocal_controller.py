"""Check the ordered reciprocal controller and its physical terminal."""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
ONE = {(): 1}
ZERO = {}


def need(test, message):
    if not test:
        raise ValueError(message)


def normalize(word):
    out = []
    for name, exponent in word:
        if out and out[-1][0] == name:
            exponent += out.pop()[1]
        if name == "Q":
            exponent %= 4
        if exponent:
            out.append((name, exponent))
    return tuple(out)


def letter(name, exponent=1):
    return {normalize(((name, exponent),)): 1}


def add(a, b, sign=1):
    out = dict(a)
    for word, value in b.items():
        out[word] = out.get(word, 0) + sign * value
        if not out[word]:
            del out[word]
    return out


def mul(a, b):
    out = {}
    for wa, ca in a.items():
        for wb, cb in b.items():
            out = add(out, {normalize(wa + wb): ca * cb})
    return out


def identity(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def product(a, b):
    out = [[ZERO for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for j in range(len(b[0])):
            for k in range(len(b)):
                out[i][j] = add(out[i][j], mul(row[k], b[k][j]))
    return out


def row_code(state, row, code):
    state[row] = [mul(code, cell) for cell in state[row]]


def row_add(state, target, source, sign=1, code=ONE):
    state[target] = [add(a, mul(code, b), sign)
                     for a, b in zip(state[target], state[source])]


def recipe(m):
    out = [{"kind": "local", "stage": 0, "pair": 0, "reverse": False}]
    for i in range(m):
        s, t = 2 * i + 1, 2 * i + 2
        out.append({"kind": "local", "stage": s, "pair": i, "reverse": True})
        if i + 1 < m:
            out.extend([
                {"kind": "idle", "pair": i + 1, "from": -1, "to": s},
                {"kind": "bridge", "dst": i, "src": i + 1, "coefficient": 1}])
        out.append({"kind": "local", "stage": t, "pair": i, "reverse": False})
        if i + 1 < m:
            out.extend([
                {"kind": "idle", "pair": i + 1, "from": s, "to": t},
                {"kind": "bridge", "dst": i, "src": i + 1, "coefficient": -1}])
    out.extend({"kind": "idle", "pair": i, "from": 2 * i + 2, "to": 2 * m}
               for i in range(m))
    out.extend({"kind": "bridge", "dst": i, "src": i - 1, "coefficient": 1}
               for i in range(m - 1, 0, -1))
    out.append({"kind": "terminal", "pairs": m})
    return out


def run(m, common=False, control=None):
    state, placements = identity(2 * m), []

    def e(stage, exponent=1):
        return letter("E" if common else "E" + str(stage), exponent)

    def code(row, op, cut, level):
        placements.append({"row": row, "cut": cut,
                           "completed_X_level" if row % 2 == 0 else "current_Y_stage": level,
                           "operator": [[[name, power] for name, power in word]
                                        for word in op]})
        if control != cut:
            row_code(state, row, op)

    code(1, e(0), "initial_Y_before_F0", 0)
    for event in recipe(m):
        kind = event["kind"]
        if kind == "local":
            s, i = event["stage"], event["pair"]
            x, y = 2 * i, 2 * i + 1
            if s == 0:
                row_add(state, y, x, code=e(0))
                code(x, e(1, -1), "X_after_F0", 0)
            elif event["reverse"]:
                if s == 1:
                    code(y, e(0, -1), "Y_before_B1", 1)
                row_add(state, x, y, -1, e(s, -1))
                transition = mul(e(s + 1, -1), e(s))
                if control == "reverse_B_transition_order":
                    transition = mul(e(s), e(s + 1, -1))
                code(x, transition, "X_after_B" + str(s), s)
            else:
                row_add(state, y, x, code=e(s))
        elif kind == "idle" and event["from"] == -1:
            i, s = event["pair"], event["to"]
            code(2 * i, e(s + 1, -1), "first_idle_X" + str(i), s)
        elif kind == "idle" and event["to"] == 2 * m:
            i = event["pair"]
            code(2 * i, e(2 * i + 2), "final_FULL_X" + str(i), 2 * m)
        elif kind == "bridge":
            dst, src, c = event["dst"], event["src"], event["coefficient"]
            row_add(state, 2 * dst, 2 * src, c)
            row_add(state, 2 * src + 1, 2 * dst + 1, -c)
            if c == -1:
                t = 2 * dst + 2
                code(2 * src, mul(e(t + 1, -1), e(t)),
                     "next_X_after_minus" + str(t), t)
        elif kind == "terminal":
            pass
    return state, placements


def rotation(m):
    out = [[ZERO for _ in range(2 * m)] for _ in range(2 * m)]
    for i in range(m):
        out[2 * i][2 * i + 1] = {(): -1}
        out[2 * i + 1][2 * i] = ONE
    return out


def triple():
    e0, e1, e2 = [letter("E" + str(i)) for i in range(3)]
    a0, b0 = letter("A"), letter("B")
    b1 = mul(mul(e1, a0), letter("E0", -1))
    a1 = mul(letter("E2", -1), letter("A", -1))
    b2 = mul(letter("A", -1), letter("E1", -1))
    a2 = mul(mul(letter("B", -1), e0), e2)
    f0 = [[a0, ZERO], [e0, b0]]
    b = [[a1, mul(mul(a1, letter("E1", -1)), b1)], [ZERO, b1]]
    b[0][1] = {w: -c for w, c in b[0][1].items()}
    f2 = [[a2, ZERO], [e2, b2]]
    need(product(f2, product(b, f0)) == rotation(1), "General ordered triple")
    e, ei = letter("E"), letter("E", -1)
    f = [[ONE, ZERO], [e, ONE]]
    middle = [[ei, {(("E", -2),): -1}], [ZERO, ONE]]
    last = [[letter("E", 2), ZERO], [e, ei]]
    need(product(last, product(middle, f)) == rotation(1), "Three-code common triple")


def main():
    schedule_path = LANES / "encoded-controller/NORMALIZATION-PROGRAMS.json"
    schedule_bytes = schedule_path.read_bytes()
    need(sha256(schedule_bytes).hexdigest() ==
         "7ce02810ecaca13ba084c365ec9c781a211e3c94dbf0f64e8717ca6d1c0b0ca9",
         "Retained schedule pin")
    actual = [e for e in json.loads(schedule_bytes)["schedule"]
              if e["kind"] in ("local", "idle", "bridge", "terminal")]
    need(actual == recipe(4), "Exact retained 19-event word and 10 idle sites")
    tests = []
    for m in range(1, 9):
        for common in (False, True):
            state, placements = run(m, common)
            need(state == rotation(m), "All arbitrary input blocks")
            need(len(placements) == 4 * m + 1, "General factor count")
            nonidentity = sum(p["operator"] != [[]] for p in placements)
            need(nonidentity == (2 * m + 2 if common else 4 * m + 1),
                 "Nonidentity factor count")
            tests.append({"pairs": m, "common_response": common,
                          "blocks_checked": (2 * m) ** 2,
                          "nonidentity_codes": nonidentity})
    for control in ("Y_before_B1", "X_after_B1", "first_idle_X1",
                    "next_X_after_minus2", "final_FULL_X0",
                    "reverse_B_transition_order"):
        need(run(4, False, control)[0] != rotation(4), "Mutation: " + control)
    triple()
    q, qi, q2 = letter("Q"), letter("Q", -1), letter("Q", 2)
    terminal = [[ZERO, q2], [{(): -1}, ZERO]]
    v, w = [[ONE, ZERO], [ZERO, qi]], [[q, ZERO], [ZERO, ONE]]
    need(product(terminal, product(v, rotation(1))) == w,
         "Physical terminal has the exact original W input")
    raw = [[ZERO, {(("E", -1),): -1}], [letter("E"), ZERO]]
    raw_code = product(terminal, product(v, product(raw, [[qi, ZERO], [ZERO, ONE]])))
    need(raw_code == [[mul(q, mul(letter("E"), qi)), ZERO],
                      [ZERO, letter("E", -1)]], "Uncorrected physical code")
    need(mul(q, letter("E")) != mul(letter("E"), q), "No Q/E commutation")
    candidate_path = LANES / "oblique-native-20261017/interior-cut/UNIT-MODE-CANDIDATE.json"
    interface_path = LANES / "circuit-interface/INTERFACE.json"
    need(sha256(candidate_path.read_bytes()).hexdigest() ==
         "d61d7447a499973afe49b7e422c51070262fc83229a82b7ff0ebb0238605d2fd",
         "Actual interior response pin")
    need(sha256(interface_path.read_bytes()).hexdigest() ==
         "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
         "Actual port interface pin")
    candidate = json.loads(candidate_path.read_bytes())
    ports = json.loads(interface_path.read_bytes())["ports"]
    entries = [(i, int(j), Fraction(c)) for i, row in enumerate(candidate["J"])
               for j, c in row.items() if Fraction(c)]
    need(len(entries) == 564 and all(i != j for i, j, c in entries),
         "Actual response support")
    need(len(set(ports)) == 112, "Distinct actual port directions")
    witnesses = []
    for i, j, c in entries:
        difference = ports[i] ^ ports[j]
        bit = (difference & -difference).bit_length() - 1
        need(((ports[i] >> bit) & 1) != ((ports[j] >> bit) & 1),
             "An actual one-column character separates each coupling")
        witnesses.append([i, j, str(c), bit])
    receipt = {
        "status": "PASS_RECIPROCAL_RESPONSE_CONTROLLER",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_pins": {str(p.relative_to(LANES)): sha256(p.read_bytes()).hexdigest()
                        for p in (schedule_path, candidate_path, interface_path)},
        "tests": tests,
        "actual_four_pair_placements": run(4)[1],
        "actual_noncommuting_entries": len(witnesses),
        "first_noncommuting_entry": witnesses[0],
        "physical_endpoint": "A V J = W; no residual code when every stated factor is implemented",
        "unwrapped_common_response_endpoint": "diag(Q E Q^-1,E^-1)",
        "scope": "Ordered content theorem and exact phase equation. The actual local backward word is E^T, not E^-1. No new native transfer, owner fit, outer twiddle, price, or kappa claim."
    }
    (HERE / "CHECKS.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
