"""Independent forward-impulse certificate for the chart-242 temporal span."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "price/PRICE-STOCK.json": "ac4207f548684468b9d09369f3a7866192ae9ffa5e3c3adb284b41bb3f61166d",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def checked(relative, zipped=False):
    data = (ROOT / relative).read_bytes()
    if sha256(data).hexdigest() != PINS[relative]:
        raise ValueError(f"changed dependency {relative}")
    if zipped:
        data = decompress(data)
        assert sha256(data).hexdigest() == PAYLOAD
    return loads(data, object_pairs_hook=unique)


def add(row, other, scalar):
    for axis, value in other.items():
        updated = row.get(axis, 0) + scalar * value
        if updated:
            row[axis] = updated
        else:
            row.pop(axis, None)


def dot(row, other):
    return sum(value * other.get(axis, 0) for axis, value in row.items())


def separation(columns, target):
    basis = {}
    for vector in columns:
        work = vector.copy()
        for axis, row in sorted(basis.items()):
            add(work, row, -work.get(axis, 0))
        if work:
            axis = min(work)
            basis[axis] = {j: value / work[axis] for j, value in work.items()}
    residual = target.copy()
    for axis, row in sorted(basis.items()):
        add(residual, row, -residual.get(axis, 0))
    if not residual:
        return len(basis), None
    dual = {min(residual): Q(1)}
    for axis, row in reversed(sorted(basis.items())):
        correction = dot(dual, row)
        if correction:
            add(dual, {axis: Q(1)}, -correction)
    assert all(dot(dual, vector) == 0 for vector in columns)
    assert dot(dual, target) != 0
    return len(basis), dual


def controls():
    rank, dual = separation([{1: Q(2), 9: Q(1)}, {9: Q(1)}], {1: Q(1)})
    assert rank == 2 and dual is None
    rank, dual = separation([{1: Q(2), 9: Q(1)}], {1: Q(1)})
    assert rank == 1 and dual == {9: Q(1), 1: Q(-1, 2)}
    return ["guarded combination passes", "nonzero COPY guard separates"]


def abort(*_):
    raise TimeoutError("hard runner limit")


def walk(word, price, deadline):
    tape = word["program"]
    public, owned = word["public"], word["owned_fields"]
    state = word["initial"][:] + [None] * owned
    width = len(state)
    wanted = {r["cut"]: r["injection_targets"] for r in price["injection_banks"]}
    begin, end = min(wanted), max(wanted)
    chart = price["retirement"]["chart"]
    pivot = price["retirement"]["pivot"]
    maximum = max(wanted, key=lambda t: (len(wanted[t]), t))
    assert (begin, maximum, end) == (41740, 45472, 45592)
    assert (public, owned, len(tape)) == (1501, 68, 76466)
    assert all(r["injection_targets"] == r["public"] for r in price["injection_banks"])
    maximal_bank = wanted[maximum]
    assert len(maximal_bank) == 20 and pivot in maximal_bank
    effects, guards, contacts, snapshots = None, {}, [], []
    for t in range(len(tape) + 1):
        if t % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError(f"cooperative stop before cut {t}")
        if t in wanted:
            roles = [r for r, frame in enumerate(state) if frame == chart]
            assert roles == wanted[t] and all(r < public for r in roles)
            snapshots.append(t)
        if t == maximum:
            effects = [{} for _ in state]
            for role in maximal_bank:
                effects[role][role] = Q(1)
        if t == len(tape):
            break
        op, dst, *args = tape[t]
        old = state[dst]
        if op == "MOVE":
            assert args[0] == old and args[2] == (dst >= public)
            new = args[1]
        elif op == "INIT":
            assert old is None and dst >= public
            new = args[0]
        elif op == "CLEAR":
            assert old == args[0] and dst >= public
            new = None
        else:
            assert old == args[-1] and op in ("ADD", "COPY", "SCALE")
            if op in ("ADD", "COPY"):
                assert state[args[0]] == old and dst != args[0]
            new = old
        if begin <= t < end and chart in (old, new):
            assert dst < public
            if op == "MOVE":
                assert old != new
                assert (new == chart) if t < maximum else (old == chart)
            else:
                assert op in ("ADD", "SCALE") and Q(args[-2])
                assert op == "SCALE" or args[0] < public
            contacts.append({"clock": t, "event": tape[t]})
        state[dst] = new
        if effects is None:
            continue
        if op in ("INIT", "CLEAR"):
            effects[dst] = {}
        elif op == "ADD":
            add(effects[dst], effects[args[0]], Q(args[-2]))
        elif op == "SCALE":
            factor = Q(args[-2])
            assert factor
            effects[dst] = {j: factor * v for j, v in effects[dst].items()}
        elif op == "COPY":
            guards[width + t] = effects[dst].copy()
            effects[dst] = {j: Q(args[-2]) * v for j, v in effects[args[0]].items()}
    assert state == word["final"] + [None] * owned
    assert snapshots == sorted(wanted)
    assert [r["clock"] + 1 for r in contacts] == snapshots[1:]
    assert sum(map(len, wanted.values())) == 354
    cohort = set(price["cohort"])
    axes = {axis: value for axis, value in enumerate(effects) if axis not in cohort or axis == pivot}
    axes.update(guards)
    columns = [{axis: row[role] for axis, row in axes.items() if role in row} for role in maximal_bank]
    return maximum, maximal_bank, columns, contacts, snapshots, sorted(guards)


def formatted(vector):
    return {axis: str(value) for axis, value in sorted(vector.items())}


def main():
    assert __debug__
    started = monotonic()
    signal(SIGALRM, abort)
    alarm(35)
    controls_result = controls()
    price = checked("price/PRICE-STOCK.json")
    word = checked("inputs/7334-WORD.json.gz", zipped=True)
    maximum, bank, columns, contacts, cuts, guards = walk(word, price, started + 32)
    target = {price["retirement"]["pivot"]: Q(1)}
    rank, dual = separation(columns, target)
    if monotonic() >= started + 32:
        raise TimeoutError("cooperative stop after exact elimination")
    alarm(0)
    print(dumps(dict(head=price["head"], caller=price["caller"], pins=PINS, controls=controls_result,
        maximal_cut=maximum, maximal_bank=bank, cuts=cuts, chronology=contacts,
        excluded_injection_keys=354 if dual is not None else 0, support_rank=rank,
        target=formatted(target), dual=None if dual is None else formatted(dual),
        dual_on_target=None if dual is None else str(dot(dual,target)),
        guarded_post_maximal_coordinates=guards, projected_columns=list(map(formatted, columns)),
        status="separated" if dual is not None else "rational solution possible"), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
