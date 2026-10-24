#!/usr/bin/env python3
"""Exact quotient-port and source-action certificate. Produced by Nick Petalas."""

import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREFIX = "research/selected-bit-recursive-caller/predecessor"
LANES = ("reads", "writes", "moves")


def require(test, message):
    if not test:
        raise AssertionError(message)


def authenticate():
    rows = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    hashes = {}
    for row in rows:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "changed live input: " + row["path"])
            hashes[row["path"]] = digest
    return hashes


SOURCE_HASHES = authenticate()
sys.path[:0] = [str(PACKAGE), str(ROOT / PREFIX), str(ROOT / PREFIX / "vendor")]
import adapter
import cardinality
from cardinal_counts import Count
import fresh_rows
from records import Tape
from words import Arena, BLANK, Meter, ONE, RIGHT, Ring, Word, ZERO


def vector(meter):
    return tuple(getattr(meter, lane) for lane in LANES)


def decode(value):
    cells = value.tape.cells
    end = cells.index(RIGHT, 1)
    require(all(bit in (ZERO, ONE) for bit in cells[1:end]), "binary output")
    require(value.tape.head == 1, "restored Count head")
    return sum(bit << i for i, bit in enumerate(cells[1:end]))


def gl_order(q, m):
    result = 1
    for j in range(m):
        result *= q ** m - q ** j
    return result


def make_context(q, m, w):
    modulus = q ** w
    arena = Arena(modulus.bit_length() + 1, capacity=32)
    ring = Ring(arena.input(modulus))
    dirt = arena.input(modulus - 1)
    context = SimpleNamespace(q=q, dimension=m, ring=ring,
                              codes=SimpleNamespace(size=gl_order(q, m)))
    return context, dirt


def protected_state(arena):
    return {slot: (bytes(arena.words[slot].cells), arena.words[slot].head)
            for slot in arena.live}


def no_inspect(self):
    raise AssertionError("runtime Word.inspect is forbidden")


def execute(function, q, m, w, families, rows):
    tapes, divisions = [], []
    original_init, original_divide = Tape.__init__, cardinality.Natural.divide_small

    def track(tape):
        original_init(tape)
        tapes.append(tape)

    def divide(value, constant):
        width = value.tape.cells.index(RIGHT, 1) - 1
        remainder = original_divide(value, constant)
        divisions.append((constant, width, remainder))
        return remainder

    Tape.__init__ = track
    cardinality.Natural.divide_small = divide
    old_inspect = Word.inspect
    Word.inspect = no_inspect
    try:
        return execute_tracked(function, q, m, w, families, rows, tapes, divisions)
    finally:
        Tape.__init__, cardinality.Natural.divide_small = original_init, original_divide
        Word.inspect = old_inspect


def execute_tracked(function, q, m, w, families, rows, tapes, divisions):
    context, dirt = make_context(q, m, w)
    fresh, bystander = Count.literal(rows), Count.literal(37)
    arena = context.ring.arena
    state = protected_state(arena)
    borrowed = [(x.tape, bytes(x.tape.cells), x.tape.head) for x in (fresh, bystander)]
    for tape in tapes:
        tape.meter = Meter()
    arena.meter = Meter()
    arena.meter.peak_live = len(arena.live)
    error, output = None, None
    try:
        unused = function(fresh, context, families)
    except ValueError as exc:
        error = str(exc)
    else:
        output = decode(unused)
        unused.close()
    bill = {"residue": vector(arena.meter),
            "record": tuple(sum(getattr(t.meter, lane) for t in tapes) for lane in LANES),
            "peak_live": arena.meter.peak_live,
            "allocations": arena.meter.allocations}
    require(protected_state(arena) == state, "residue ownership/bytes/head restoration")
    for tape, cells, head in borrowed:
        require((bytes(tape.cells), tape.head) == (cells, head), "borrowed Count restoration")
    owned = [t for t in tapes if all(t is not b[0] for b in borrowed)]
    require(all(all(c == BLANK for c in t.cells[1:]) and t.head == 1 for t in owned),
            "owned record cleanup")
    require(all(all(c == BLANK for c in word.cells[1:]) and word.head == 1
                for word in arena.words if word.slot not in arena.live), "owned Word cleanup")
    fresh.close()
    bystander.close()
    context.ring.close()
    arena.free_many(context.ring.modulus, dirt)
    require(not arena.live, "complete fixture disposal")
    return {"output": output, "error": error, "bill": bill, "divisions": divisions}


def radix_bill(q, w):
    context, dirt = make_context(q, 1, w)
    arena = context.ring.arena
    state = protected_state(arena)
    arena.meter = Meter()
    arena.meter.peak_live = len(arena.live)
    yields = sum(1 for _ in cardinality.radix_power(context.ring, q))
    require(yields == w, "complete radix validation")
    require(protected_state(arena) == state, "radix restoration")
    result = {"actions": vector(arena.meter), "allocations": arena.meter.allocations}
    context.ring.close()
    arena.free_many(context.ring.modulus, dirt)
    require(not arena.live, "radix fixture disposal")
    return result


def verify_pair(q, m, w, factor):
    families = 4
    high = q ** (m * m * (w - 1))
    rows = families * gl_order(q, m) * high * factor
    old = execute(fresh_rows.quotient, q, m, w, families, rows)
    new = execute(adapter.quotient, q, m, w, families, rows)
    require(old["error"] is None and new["error"] is None, "accepted complete stock")
    require(old["output"] == new["output"] == factor, "independent quotient oracle")
    require(old["divisions"] == new["divisions"], "identical division calls/widths/remainders")
    require(len(new["divisions"]) == 2 + m * m * (w - 1), "exact small-q division count")
    rho = radix_bill(q, w)
    delta = tuple(a - b for a, b in zip(old["bill"]["residue"], new["bill"]["residue"]))
    require(delta == tuple((m * m - 1) * x for x in rho["actions"]), "exact radix saving")
    require(old["bill"]["record"] == new["bill"]["record"], "unchanged whole Count bill")
    require(old["bill"]["peak_live"] == new["bill"]["peak_live"], "unchanged residue peak")
    require(old["bill"]["allocations"] - new["bill"]["allocations"] ==
            (m * m - 1) * rho["allocations"], "exact allocation-call saving")
    return {"q": q, "m": m, "w": w, "factor": factor, "rows_bits": rows.bit_length(),
            "old": old["bill"], "new": new["bill"], "rho": rho, "saved": delta}


def verify_rejections():
    q, m, w, families = 3, 2, 3, 4
    low = families * gl_order(q, m)
    fixtures = [(0, "independent positive cardinality tape"),
                (1, "complete fresh family factor"),
                (families, "complete fresh GL low factor")]
    fixtures += [(low * q ** k, "complete fresh high factor") for k in range(8)]
    for rows, error in fixtures:
        old = execute(fresh_rows.quotient, q, m, w, families, rows)
        new = execute(adapter.quotient, q, m, w, families, rows)
        require(old["output"] is None and new["output"] is None, "reject deficient stock")
        require(old["error"] == new["error"] == error, "preserved rejection class")
        require(old["divisions"] == new["divisions"], "preserved rejecting division trace")
    return len(fixtures)


def bad_quotient(divisions, validate=True):
    def run(fresh, context, families):
        unused = Count(fresh)
        try:
            for divisor in (families, context.codes.size):
                require(unused.divide_small(divisor) == 0, "control low factor")
            if validate:
                for _ in cardinality.radix_power(context.ring, context.q):
                    pass
            for _ in range(divisions):
                if unused.divide_small(context.q):
                    raise ValueError("control excess high division")
            return unused
        except (ValueError, AssertionError):
            unused.close()
            raise
    return run


def verify_controls():
    q, m, w, f = 3, 2, 2, 4
    rows = f * gl_order(q, m) * q ** 4
    missing = execute(bad_quotient(3), q, m, w, f, rows)
    require(missing["output"] == q and missing["output"] != 1, "omitted-division control")
    extra = execute(bad_quotient(5), q, m, w, f, rows)
    require(extra["error"] is not None, "extra-division control")
    trivial_rows = f * gl_order(q, m)
    skipped = execute(bad_quotient(0, False), q, m, 1, f, trivial_rows)
    correct = execute(adapter.quotient, q, m, 1, f, trivial_rows)
    require(skipped["output"] == correct["output"] == 1, "same-output validation control")
    require(skipped["bill"]["residue"] != correct["bill"]["residue"], "validation invoice control")
    rho = radix_bill(q, w)["actions"]
    require(tuple(m * m * x for x in rho) != tuple((m * m - 1) * x for x in rho),
            "forgotten retained traversal control")
    return 4


def main():
    # First discriminating example, then bounded coverage of its same contract.
    fixtures = [(3, 2, 2, 7), (2, 1, 3, 5), (3, 1, 1, 1), (2, 2, 3, 9),
                (5, 2, 2, 3), (3, 3, 2, 17), (3, 2, 4, 11), (3, 64, 1, 9475)]
    cases = [verify_pair(*fixture) for fixture in fixtures]
    receipt = {"claim_type": "scoped successful-input refinement and exact local source invoice",
               "cases": cases, "rejections": verify_rejections(), "controls": verify_controls(),
               "source_sha256": SOURCE_HASHES,
               "package_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(PACKAGE.iterdir()) if p.is_file()}}
    print(json.dumps(receipt, sort_keys=True, indent=2))
    print("PASS_R437_SHARED_RADIX_QUOTIENT cases=8 rejections=11 controls=4")


if __name__ == "__main__":
    main()
