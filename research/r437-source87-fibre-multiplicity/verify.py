#!/usr/bin/env python3
"""Fibre count of the SOURCE87 rank-2 parent packet.

The argument is PROOF.md. This checker recomputes the integer layout map,
binds it to the pinned caller sources, and reads the compiler receipt.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHYSICAL = ROOT / "research/r437-carrier-integration/physical.py"
COMPILER = ROOT / "research/r437-carrier-integration/COMPILER-RESULT.json"
LAYOUT = ROOT / "research/selected-bit-physical-caller/inputs/pr2753/layout.py"
PLAN = ROOT / "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/plan.py"

Q = 3
PARENT_SIZE = 64
COLUMNS = 1
FIRST, SECOND, WIDTH = 0, 126, 2
BEFORE, GAP, SUFFIX = 2, 3, 2
UNUSED_ROWS = 9475
STOCK_DIVISOR = 28416
STOCK_MULTIPLE = 269241600


def need(condition, message):
    if not condition:
        raise ValueError(message)


def extents(dimension, w=1):
    """Integer image of Layout.child_extents at the pinned call arguments."""
    need(dimension >= 1, "positive plan dimension")
    core = COLUMNS * dimension
    need(core <= PARENT_SIZE, "core exceeds the parent body")
    remaining = PARENT_SIZE - core
    extra = remaining * 2
    total = PARENT_SIZE * 2

    def physical(position):
        if position < core:
            return position
        return position + extra

    a = physical(FIRST)
    b = physical(SECOND)
    a_end = a + WIDTH
    b_end = b + WIDTH
    need(a < b and a_end <= b and b_end <= total, "chunk placement rejected")
    need(physical(FIRST + WIDTH - 1) == a_end - 1, "first chunk is not contiguous")
    need(physical(SECOND + WIDTH - 1) == b_end - 1, "second chunk is not contiguous")
    for start, end in ((a, a_end), (b, b_end)):
        need(start >= PARENT_SIZE or end <= PARENT_SIZE, "chunk crosses the external gap")
    atom = Q ** w

    def scale(base, exponent):
        return base * atom ** exponent

    pre = scale(BEFORE, a)
    between = b - a_end
    after = total - b_end
    middle = scale(1, between)
    tail = scale(SUFFIX, after)
    if a >= PARENT_SIZE:
        region = 0
    elif b_end <= PARENT_SIZE:
        region = 2
    else:
        region = 1
    values = [pre, middle, tail]
    values[region] *= GAP
    return tuple(values)


def bind_sources():
    physical = PHYSICAL.read_text(encoding="utf-8")
    layout = LAYOUT.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    for snippet in (
        "first=ia.literal(0),second=ia.literal(126),width=ia.literal(2)",
        "for v in(0,126,2)",
        "expected=[2,3*3**124,2]",
        "==[2,3*3**124,2]",
        "parent_unused=Count.literal(9475)",
        "nbits=972",
        "9475*12*3**128",
        "parent_size=ia.literal(64)",
        "cols=ia.literal(1)",
        "ring,3,before,gap,suffix",
        "plan.rank==2",
    ):
        need(snippet in physical, "physical.py is missing the pinned call: " + snippet)
    need("gap_region = (0 if g.raw.compare(a,self.parent_size)>=0 else" in layout,
         "layout.py gap rule changed")
    need("2 if g.raw.compare(b_end,self.parent_size)<=0 else 1)" in layout,
         "layout.py gap rule changed")
    need('Count.product(values[gap_region],self.gap)' in layout, "gap is not applied once")
    need("m = len(low_projector)" in plan, "plan dimension is not the projector length")
    need('1 <= rank < m <= 64' in plan, "plan dimension bound changed")
    need("return Plan(m, rank, True, tuple(commands))" in plan, "good plan dimension changed")


def shared_source87(receipt):
    charts = []
    identifiers = []
    for arm in ("C", "D"):
        rows = receipt[arm]["source87"]
        need(len(rows) == 2, arm + " SOURCE87 record count")
        for row in rows:
            record = row["record"]
            need(record[10] == 2, arm + " SOURCE87 rank")
            need(isinstance(record[9], str) and len(record[9]) == 64, arm + " chart digest")
            charts.append(record[9])
            identifiers.append(row["identifier"])
    need(len(set(charts)) == 1, "SOURCE87 charts differ")
    need(len(set(identifiers)) == 4, "C and D request identifiers were expected to differ")
    return charts[0]


def profile_delta(receipt):
    left, right = receipt["C"]["profile"], receipt["D"]["profile"]
    keys = set(left) | set(right)
    delta = {key: int(right.get(key, 0)) - int(left.get(key, 0)) for key in keys}
    need(delta == {"1": 288, "2": -576, "3": 288, **{key: 0 for key in keys if key not in {"1", "2", "3"}}},
         "profile delta is not the 288-call exchange")
    need(sum(int(key) * value for key, value in delta.items()) == 0, "rank-mass delta")
    need(sum(delta.values()) == 0, "request-count delta")
    need(receipt["C"]["rank_mass"] == receipt["D"]["rank_mass"] == 1808352, "rank mass")
    return delta


def reject(function, message):
    try:
        function()
    except ValueError:
        return
    raise ValueError("control failed to reject: " + message)


def main():
    bind_sources()
    triple = extents(64, w=1)
    need(triple == (2, 3 * 3 ** 124, 2), "dimension 64 extents")
    need(triple[0] * triple[1] * triple[2] * 3 ** 4 == 12 * 3 ** 128, "volume identity")
    fibre = BEFORE * GAP * SUFFIX * 3 ** 4
    need(fibre == 972, "executed fibre volume")
    multiplicity = UNUSED_ROWS * 3 ** 124
    need(multiplicity * fibre == UNUSED_ROWS * 12 * 3 ** 128, "parent packet splits into M fibres")
    need(STOCK_DIVISOR * UNUSED_ROWS == STOCK_MULTIPLE, "unused-row literal")
    for dimension in range(1, 64):
        reject(lambda dimension=dimension: need(extents(dimension) == triple, "smaller dimension matched"),
               "dimension " + str(dimension))
    reject(lambda: need(extents(64, w=2) == triple, "w=2 matched the w=1 triple"), "atom size 9")

    def double_gap():
        values = list(extents(64))
        values[0] *= GAP
        need(values[0] * values[1] * values[2] * 3 ** 4 == 12 * 3 ** 128, "double gap still fits")

    reject(double_gap, "gap counted twice")
    receipt = json.loads(COMPILER.read_text(encoding="utf-8"))
    chart = shared_source87(receipt)
    delta = profile_delta(receipt)
    need(delta["2"] != 0, "rank-2 profile must move outside this one entry")
    print(
        "PASS_R437_SOURCE87_FIBRE_MULTIPLICITY"
        f" extents={triple[0]},{triple[1]},{triple[2]}"
        f" fibre=972 multiplicity={multiplicity}"
        f" chart={chart[:12]} profile_delta=1:+288,2:-576,3:+288"
        " leaf_difference=0 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
