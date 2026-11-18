"""Check exact scalar arithmetic, lifetimes, and public endpoints on the literal word."""
from collections import Counter
from fractions import Fraction
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from word import encoded, main_roles, need, words

SCALE = 225
HEIGHT = 14
UNIT = SCALE << HEIGHT


@cache
def rational(literal):
    return Fraction(literal)


def span(basis):
    members = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in members, "independent frame basis")
        members |= {w ^ v for w in members}
    return members


def divided(value, denominator):
    q, remainder = divmod(value, denominator)
    need(remainder == 0, "grid remainder")
    return q


def multiply(row, scalar):
    a, b = scalar.numerator, scalar.denominator
    return {k: divided(a * v, b) for k, v in row.items()}


def add_to(row, term):
    for k, v in term.items():
        result = row.get(k, 0) + v
        if result:
            row[k] = result
        else:
            row.pop(k, None)


def endpoints(word):
    result = [{i: UNIT} for i in range(word["public"])]
    h = word["hosted"]
    two = set(h["Dports"])
    for i, x in enumerate(word["live"]):
        y = x + 112
        if i in two:
            result[y][x] = UNIT
        else:
            result[x][y] = -UNIT
            result[y] = {x: UNIT // 2, y: UNIT // 2}
    for x, y in zip(h["X2"], h["Y2"], strict=True):
        result[x][y] = -UNIT
    return result


def scalar_trace(word):
    return [[*e[:-1]] for e in word["program"] if e[0] != "MOVE"]


def verify_cleared(row, records, terms, owner):
    total = {}
    for label, literal in terms.items():
        donor = int(label)
        need(0 <= donor < len(records) and donor != owner and records[donor] is not None, "invalid CLEAR donor")
        weight = rational(literal)
        for col, value in records[donor].items():
            total[col] = total.get(col, 0) + weight * value
    need({k: v for k, v in total.items() if v} == row and (row or not terms), "CLEAR reconstruction")


def execute(word, certificates):
    n = word["public"]
    slots = n + word["owned_fields"]
    masks = [span(frame) for frame in word["frames"]]
    frames = word["initial"][:] + [None] * (slots - n)
    rows = [{r: UNIT} for r in range(n)] + [None] * (slots - n)
    mass = [UNIT] * n + [0] * (slots - n)
    peak_mass = UNIT
    live, labels, closed = {}, set(), []
    max_live = 0
    paid = Counter()
    moves = Counter()
    visits = 0
    seam = None
    for clock, event in enumerate(word["program"]):
        op, r = event[:2]
        need(type(r) is int and 0 <= r < slots, "field index")
        if op == "INIT":
            need(n <= r and rows[r] is None and 0 <= event[2] < len(masks), "inactive INIT")
            live[r] = (clock, event[2])
            labels.add(r)
            max_live = max(max_live, len(live))
            rows[r], frames[r], mass[r] = {}, event[2], 0
            continue
        need(rows[r] is not None, "inactive operand")
        if op == "MOVE":
            _, _, a, b, owned = event
            need(type(owned) is bool and owned == (r >= n) and frames[r] == a and 0 <= b < len(masks), "MOVE origin")
            need(masks[a] < masks[b] or (owned and masks[b] < masks[a]), "MOVE nesting")
            paid[abs(len(word["frames"][a]) - len(word["frames"][b]))] += 1
            moves[owned] += 1
            frames[r] = b
            continue
        need(frames[r] == event[-1], "scalar or retirement chart")
        if op == "CLEAR":
            need(r in live, "live CLEAR")
            verify_cleared(rows[r], rows, certificates[len(closed)], r)
            start, first = live.pop(r)
            closed.append([r, start, clock, first, frames[r]])
            rows[r], frames[r], mass[r] = None, None, 0
            continue
        need(op in ("ADD", "COPY", "SCALE"), "native operation")
        scalar = rational(event[-2])
        need(scalar, "nonzero scalar")
        if op == "SCALE":
            term = multiply(rows[r], scalar)
            rows[r] = term
            mass[r] = sum(map(abs, term.values()))
            visits += len(term)
        else:
            donor = event[2]
            need(0 <= donor < slots and donor != r and frames[donor] == frames[r] and rows[donor] is not None, "donor contact")
            need(op != "COPY" or not rows[r], "COPY overwrites nonzero")
            if event == ["ADD", 210, 457, "-1/2", 218]:
                need(seam is None and clock and word["program"][clock-1] == ["MOVE", 457, 966, 218, False], "signed half seam")
                seam = [clock, len(rows[donor]), all(x % 2 == 0 for x in rows[donor].values())]
            term = multiply(rows[donor], scalar)
            peak_mass = max(peak_mass, sum(map(abs, term.values())))
            old = sum(abs(rows[r].get(k, 0)) for k in term)
            add_to(rows[r], term)
            mass[r] += sum(abs(rows[r].get(k, 0)) for k in term) - old
            visits += 2 * len(term)
        peak_mass = max(peak_mass, mass[r])
    need(rows[:n] == endpoints(word), "arbitrary-input port or helper map")
    need(not live and len(closed) == len(certificates) and frames[:n] == word["final"], "terminal ownership")
    need(seam and seam[1] and seam[2], "native half-grid witness")
    mains = main_roles(word)
    helper = Counter()
    for r in set(range(n)) - mains:
        a, b = word["initial"][r], word["final"][r]
        need(masks[a] < masks[b], "positive helper")
        helper[len(word["frames"][b]) - len(word["frames"][a])] += 1
    return dict(events=len(word["program"]), paid=dict(sorted(paid.items())), helper=dict(sorted(helper.items())),
                all_public_rows=n, mains=len(mains), lifetimes=len(closed), used_labels=len(labels),
                peak_live=max_live, owned_moves=moves[True], peak_scaled_mass=str(Fraction(peak_mass, 2**HEIGHT)),
                grid=[SCALE, HEIGHT], visits=visits, half_grid=seam,
                lifetime_sha256=sha256(encoded(closed)).hexdigest())


def run():
    source, candidate = words()
    need(scalar_trace(source) == scalar_trace(candidate), "source scalar coefficients, incidence and lifetime order")
    cert = json.loads((HERE / "data/clear.json").read_bytes())["clear_event_index"]
    clocks = [i for i, e in enumerate(source["program"]) if e[0] == "CLEAR"]
    need(set(cert) == {str(t) for t in clocks}, "certificate coverage")
    terms = [cert[str(t)] for t in clocks]
    result = execute(candidate, terms)
    program = candidate["program"].copy()
    i = max(j for j, e in enumerate(program) if e[0] == "ADD")
    program[i] = program[i].copy()
    program[i][3] = str(-rational(program[i][3]))
    try:
        execute(dict(candidate, program=program), terms)
    except ValueError as exc:
        need(str(exc) == "arbitrary-input port or helper map", "equal-price mutation failure reason")
    else:
        raise ValueError("equal-price scalar corruption escaped")
    result["equal_price_sign_rejected"] = True
    for fault in ("self", "odd"):
        try:
            if fault == "self":
                verify_cleared({0: 1}, [{0: 1}], {"0": "1"}, 0)
            else:
                divided(-1, 2)
        except ValueError:
            pass
        else:
            raise ValueError("negative control escaped")
    return result


if __name__ == "__main__":
    receipt = json.loads(json.dumps(run()))
    need(receipt == json.loads((HERE / "RESULT.json").read_bytes())["native"], "native receipt")
    print("PASS_JOINT_NATIVE", receipt["all_public_rows"], receipt["lifetimes"], receipt["half_grid"])
