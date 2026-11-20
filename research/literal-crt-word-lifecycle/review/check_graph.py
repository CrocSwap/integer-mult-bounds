"""Independent review of the CRT lifecycle graph, without its verifier/runtime.

Imports only lifecycle.py as the candidate compiler. This interpreter, boundary
oracle, fixtures, cost formulas, and controls are independently written.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
spec = spec_from_file_location("candidate_lifecycle", CANDIDATE / "lifecycle.py")
candidate = module_from_spec(spec)
spec.loader.exec_module(candidate)

NUM, TEMPLATE, STACK, SOURCE, OUTPUT = 64, 64, 65, 66, 67
ALPHABET = "_01LR"
DEFAULT_HEADS = [1] * 65 + [0] * 3
COUNTS = Counter()
STEPS = Counter()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def selector(slot):
    return ["L", *[str((slot // (2 ** j)) % 2) for j in range(6)], "R"]


def stack_frame(order, length=338):
    out = ["L"]
    for slot in order:
        out.extend(selector(slot)[1:7])
    out.append("R")
    require(len(out) <= length, "stack capacity")
    return out + ["_"] * (length - len(out))


def new_fixture(p, order, pattern=0, heterogeneous=True):
    cells = []
    for slot in range(64):
        digits = [str((pattern >> (i % 4)) & 1) for i in range(p)]
        active = ["_"] * (p + 1) if slot in order else digits + ["R"]
        length = p + 2 + (3 + ((slot * 29) % 53) if heterogeneous else 0)
        cells.append(["L", *active, *(["_"] * (length - p - 2))])
    cells.append(["L", *(["0"] * p), "R", *(["_"] * 11)])
    cells.extend([stack_frame(order), ["_"] * 8, ["_"] * 8])
    return cells, DEFAULT_HEADS.copy()


def copy_state(cells, heads):
    return deepcopy(cells), list(heads)


def execute(code, cells, heads, entry, *, logical=False, stop=None, free_slot=None):
    """Literal interpreter; no candidate runtime, fixtures, or metadata helpers."""
    require(len(cells) == len(heads) == 68, "fixed role count")
    require(len({id(t) for t in cells}) == 68, "physical owners must be disjoint")
    pc, count, ordinal = entry, 0, 0
    first_stack_write = None
    while True:
        if stop is not None and count and pc in stop:
            return {"pc": pc, "instructions": count, "status": None}
        ins = code[pc]
        op = ins[0]
        ordinal += 1
        require(ordinal < 3000000, "bounded independent replay watchdog")
        if op in ("NR", "NW", "NM"):
            require(logical, "no nonliteral physical opcode")
            selected = SOURCE if ins[1] == 0 else OUTPUT
            require(heads[selected] == 0 and cells[selected][0] == "L"
                    and cells[selected][7] == "R", "dispatch frame")
            bits = cells[selected][1:7]
            require(all(b in ("0", "1") for b in bits), "dispatch bits")
            tape = sum(int(b) * 2 ** j for j, b in enumerate(bits))
            count += 31 if op == "NR" else 32
            op = op[1:]
            ins = (op, tape, ins[2])
        else:
            count += 1
        if op == "R":
            pc = ins[2][cells[ins[1]][heads[ins[1]]]]
        elif op == "W":
            tape = ins[1]
            if free_slot is not None and tape == STACK and first_stack_write is None:
                first_stack_write = ordinal
                require(set(cells[free_slot][1:]) <= {"_"},
                        "FREE advertises owner before whole admitted body is blank")
            cells[tape][heads[tape]] = ins[2]
            pc += 1
        elif op == "M":
            tape = ins[1]
            heads[tape] += ins[2]
            require(ins[2] in (-1, 1) and 0 <= heads[tape] < len(cells[tape]),
                    "unit move within supplied physical backing")
            pc += 1
        elif op == "J":
            pc = ins[1]
        elif op == "H":
            return {"pc": pc, "instructions": count, "status": ins[1],
                    "first_stack_write": first_stack_write}
        else:
            raise ValueError("unrecognized instruction")


def boundary(cells, heads, expected, free, original_lengths):
    require(heads == DEFAULT_HEADS, "all physical heads restored")
    require(cells[:65] == expected[:65], "same physical bodies and full old tails")
    require(cells[STACK] == stack_frame(free, original_lengths[STACK]),
            "exact ordered stack and blank suffix")
    require(cells[SOURCE] == ["_"] * original_lengths[SOURCE]
            and cells[OUTPUT] == ["_"] * original_lengths[OUTPUT], "selector retirement")
    require([len(t) for t in cells] == original_lengths, "no backing shrink or growth")
    require(len(free) == len(set(free)) and all(8 <= s < 64 for s in free),
            "owned, unique free partition")


def cost(kind, p, m, found=None):
    if kind == "TAKE":
        return 36 * m + 155
    if kind == "ZERO":
        return 165 * p + 36 * m + 417
    if kind == "COPY":
        return 287 * p + 97 * m + 676
    if kind == "FREE":
        return 160 * p + 61 * m + 409
    if kind == "IS_LIVE":
        return 61 * found + 89 if found is not None else 61 * m + 90
    return {"INIT": 2744, "CLOSE": 1395}[kind]


def single_service(code, entries, setters, cells, heads, p, order, kind,
                   source=None, logical=False, check_count=True):
    old = deepcopy(cells)
    lengths = [len(t) for t in cells]
    expected = deepcopy(cells)
    expected_free = list(order)
    m = len(order)
    if source is not None:
        bound = execute(code, cells, heads, setters[source], logical=logical)
        require(bound["status"] == "BOUND" and bound["instructions"] == 31,
                "paid constant setter")
        COUNTS["setters"] += 1
        STEPS["setters"] += bound["instructions"]
    result = execute(code, cells, heads, entries[kind], logical=logical,
                     free_slot=source if kind == "FREE" else None)
    found = None
    if kind in ("TAKE", "ZERO", "COPY"):
        out = expected_free.pop()
        want = "ALLOC_" + str(out)
        if kind == "ZERO":
            expected[out][1:p + 2] = ["0"] * p + ["R"]
        elif kind == "COPY":
            require(out != source, "input/output physical alias")
            expected[out][1:p + 2] = old[source][1:p + 2]
    elif kind == "FREE":
        want = "FREED"
        expected_free.append(source)
        expected[source][1:p + 2] = ["_"] * (p + 1)
    elif kind == "IS_LIVE":
        want = "FREE" if source in order else "LIVE"
        if source in order:
            found = order.index(source) + 1
    else:
        raise ValueError("not an ordinary service")
    require(result["status"] == want, "returned physical owner or liveness")
    if check_count:
        require(result["instructions"] == cost(kind, p, m, found), "exact path invoice")
    boundary(cells, heads, expected, expected_free, lengths)
    COUNTS[("logical_" if logical else "physical_") + kind] += 1
    STEPS[("logical_" if logical else "physical_") + kind] += result["instructions"]
    return expected_free


def compiler_dispatch_checks(physical, logical, metadata):
    packet = 0
    op_counts = Counter()
    for pc, ins in enumerate(logical):
        if ins[0] not in ("NR", "NW", "NM"):
            continue
        for slot in range(64):
            symbols = tuple(ALPHABET) if ins[0] == "NR" else ("0",)
            for symbol in symbols:
                cells = [["L", "0", "0", "0", "0", "R"] for _ in range(65)]
                cells.extend([stack_frame([]), selector(0), selector(0)])
                heads = DEFAULT_HEADS.copy()
                cells[SOURCE if ins[1] == 0 else OUTPUT] = selector(slot)
                cells[slot][1] = symbol
                expected, expected_heads = copy_state(cells, heads)
                if ins[0] == "NR":
                    target = ins[2][symbol]
                    expected_cost = 31
                else:
                    target = pc + 1
                    expected_cost = 32
                    if ins[0] == "NW":
                        expected[slot][1] = ins[2]
                    else:
                        expected_heads[slot] += ins[2]
                physical_target = metadata["logical_to_physical"][target]
                got = execute(physical, cells, heads, metadata["logical_to_physical"][pc],
                              stop={physical_target})
                require(got["instructions"] == expected_cost, "all dispatch path lengths")
                require(cells == expected and heads == expected_heads, "dispatch macro refinement")
                packet += 1
                op_counts[ins[0]] += 1
    return {"packets": packet, "by_macro": dict(op_counts),
            "numeric_read": 31, "numeric_write_or_move": 32}


def permutation_tests(logical, labels):
    setters = [labels["SET_" + str(s)] for s in range(64)]
    precisions = (4, 5, 19, 83)
    permutations = [
        list(range(63, 7, -1)),
        [8 + ((17 * i + 23) % 56) for i in range(56)],
    ]
    for p in precisions:
        for perm in permutations:
            for m in range(1, 57):
                order = perm[:m]
                for kind in ("TAKE", "ZERO", "COPY"):
                    cells, heads = new_fixture(p, order, pattern=(m + p) % 16)
                    single_service(logical, labels, setters, cells, heads, p, order,
                                   kind, source=(m % 8) if kind == "COPY" else None,
                                   logical=True)
            for m in range(56):
                order = perm[:m]
                source = next(s for s in range(8, 64) if s not in order)
                cells, heads = new_fixture(p, order, pattern=(m + p) % 16)
                single_service(logical, labels, setters, cells, heads, p, order,
                               "FREE", source=source, logical=True)
    for perm in permutations:
        for m in range(57):
            order = perm[:m]
            cells, heads = new_fixture(4, order, pattern=15)
            for source in range(64):
                single_service(logical, labels, setters, cells, heads, 4, order,
                               "IS_LIVE", source=source, logical=True)
    return {"precisions": list(precisions), "permutations": permutations,
            "all_stack_lengths": True, "all_liveness_handles": True}


def physical_copy_tests(code, metadata):
    for p in (4, 33):
        for source in range(64):
            for pattern in (0, 5, 10, 15):
                order = [8 + ((17 * i + 23) % 56) for i in range(56)]
                order = [s for s in order if s != source]
                order = order[:1 + ((source * 11 + pattern) % len(order))]
                cells, heads = new_fixture(p, order, pattern=pattern)
                single_service(code, metadata["entries"], metadata["setters"],
                               cells, heads, p, order, "COPY", source=source)
    return {"precisions": [4, 33], "source_handles": list(range(64)),
            "four_periodic_patterns": [0, 5, 10, 15],
            "numerical_values_equal_across_all_live_owners": True}


def history_chronology(code, metadata):
    rng = random.Random(7596)
    order = list(range(63, 7, -1))
    cells, heads = new_fixture(4, order, pattern=15)
    physical_ids = [id(t) for t in cells]
    initial_lengths = [len(t) for t in cells]
    protected = deepcopy(cells[:8])
    precision_sequence = (41, 4, 17, 6)
    report = []
    for p in precision_sequence:
        for slot in range(8, 65):
            cells[slot].extend(["_"] * max(0, p + 2 - len(cells[slot])))
        cells[TEMPLATE][:] = ["L", *(["0"] * p), "R",
                            *(["_"] * (len(cells[TEMPLATE]) - p - 2))]
        for slot in range(8, 64):
            require(cells[slot][0] == "L" and set(cells[slot][1:]) <= {"_"},
                    "all old inactive tails actually blank")
        initial = execute(code, cells, heads, metadata["entries"]["INIT"])
        require(initial["status"] == "READY" and initial["instructions"] == 2744,
                "INIT count and halt")
        order = list(range(63, 7, -1))
        live = []
        for step in range(96):
            if live and (not order or rng.randrange(3) == 0):
                source = rng.choice(live)
                order = single_service(code, metadata["entries"], metadata["setters"],
                                       cells, heads, p, order, "FREE", source=source)
                live.remove(source)
            elif live and step % 2:
                source = rng.choice(live)
                out = order[-1]
                order = single_service(code, metadata["entries"], metadata["setters"],
                                       cells, heads, p, order, "COPY", source=source)
                live.append(out)
            else:
                out = order[-1]
                order = single_service(code, metadata["entries"], metadata["setters"],
                                       cells, heads, p, order, "ZERO")
                live.append(out)
            if step % 7 == 0:
                source = rng.randrange(64)
                order = single_service(code, metadata["entries"], metadata["setters"],
                                       cells, heads, p, order, "IS_LIVE", source=source)
        rng.shuffle(live)
        for source in live:
            order = single_service(code, metadata["entries"], metadata["setters"],
                                   cells, heads, p, order, "FREE", source=source)
        retired = execute(code, cells, heads, metadata["entries"]["CLOSE"])
        require(retired["status"] == "RETIRED" and retired["instructions"] == 1395,
                "CLOSE count and halt")
        require(all(set(cells[s]) <= {"_"} for s in (STACK, SOURCE, OUTPUT)),
                "actual metadata retired")
        require(cells[:8] == protected, "protected equal-valued owners unchanged")
        require([id(t) for t in cells] == physical_ids, "physical history never renamed")
        require(all(len(cells[s]) >= initial_lengths[s] for s in range(68)),
                "old capacity never refunded")
        report.append({"p": p, "numeric_role_capacities": [len(t) for t in cells[:64]],
                       "sum_numeric_capacities": sum(len(t) for t in cells[:64]),
                       "final_free_order": order})
    return {"seed": 7596, "operations_per_lifetime": 96,
            "precision_sequence": list(precision_sequence), "lifetimes": report,
            "external_setup_outside_service_invoice": True}


def controls(code, metadata):
    controls = []
    entries, setters = metadata["entries"], metadata["setters"]
    for source, kind, name in ((0, "FREE", "protected_release"),
                                (8, "FREE", "duplicate_release"),
                                (8, "COPY", "copy_inactive_owner")):
        order = list(range(63, 7, -1))
        cells, heads = new_fixture(4, order)
        before = deepcopy(cells)
        execute(code, cells, heads, setters[source])
        got = execute(code, cells, heads, entries[kind])
        require(got["status"] == "MALFORMED" and cells[:66] == before[:66],
                "invalid ownership rejected before body or stack mutation")
        controls.append(name)
    cells, heads = new_fixture(4, [])
    before = copy_state(cells, heads)
    got = execute(code, cells, heads, entries["TAKE"])
    require(got["status"] == "EXHAUSTED" and (cells, heads) == before,
            "empty reserve exact rejection")
    controls.append("empty_reserve_boundary")
    cells, heads = new_fixture(4, list(range(63, 7, -1)))
    cells[8] = cells[9]
    try:
        execute(code, cells, heads, entries["ZERO"])
    except ValueError as exc:
        require(str(exc) == "physical owners must be disjoint", "alias premise control")
    else:
        raise ValueError("alias premise accepted")
    controls.append("distinct_physical_owner_entry_premise")
    # The graph does not sweep external dirty history. This is an exclusion
    # witness, not an admitted positive packet or an expected rejection.
    cells, heads = new_fixture(4, list(range(63, 7, -1)))
    cells[8][-1] = "1"
    got = execute(code, cells, heads, entries["ZERO"])
    require(got["status"] == "ALLOC_8" and cells[8][-1] == "1",
            "dirty inactive tail outside current extent is not erased")
    execute(code, cells, heads, setters[8])
    got = execute(code, cells, heads, entries["FREE"])
    require(got["status"] == "FREED" and cells[8][-1] == "1",
            "dirty external tail remains outside admitted full-history conclusion")
    controls.append("dirty_tail_exclusion_witness")
    # A semantically correct extra jump changes the exact receipt.
    extended = tuple(code) + (("J", entries["ZERO"]),)
    changed = dict(entries, ZERO=len(code))
    cells, heads = new_fixture(4, list(range(63, 7, -1)))
    try:
        single_service(extended, changed, setters, cells, heads, 4,
                       list(range(63, 7, -1)), "ZERO")
    except ValueError as exc:
        require(str(exc) == "exact path invoice", "exact count mutation detected")
    else:
        raise ValueError("extra paid jump escaped invoice oracle")
    controls.append("extra_paid_jump_preserves_semantics_but_rejects_invoice")
    # Equal numerical values cannot conceal a returned owner mismatch.
    mutated = tuple(("H", "ALLOC_9") if row == ("H", "ALLOC_8") else row for row in code)
    cells, heads = new_fixture(4, list(range(63, 7, -1)), pattern=0)
    try:
        single_service(mutated, entries, setters, cells, heads, 4,
                       list(range(63, 7, -1)), "ZERO")
    except ValueError as exc:
        require(str(exc) == "returned physical owner or liveness", "wrong-owner control")
    else:
        raise ValueError("wrong physical owner escaped")
    controls.append("equal_value_wrong_owner_return")
    return controls


def main():
    logical, labels, _ = candidate.logical_graph()
    physical, metadata = candidate.compile_program()
    require(set(row[0] for row in physical) == {"R", "W", "M", "J", "H"},
            "only literal fixed opcodes")
    result = {
        "status": "PASS_INDEPENDENT_CRT_LIFECYCLE_REVIEW",
        "candidate_sha256": sha256((CANDIDATE / "lifecycle.py").read_bytes()).hexdigest(),
        "physical_graph_sha256": sha256(json.dumps(physical, separators=(",", ":"),
                                                  sort_keys=True).encode()).hexdigest(),
        "physical_locations": len(physical),
        "compiler_dispatch": compiler_dispatch_checks(physical, logical, metadata),
        "weighted_logical_paths": permutation_tests(logical, labels),
        "physical_equal_value_copy": physical_copy_tests(physical, metadata),
        "physical_history_chronology": history_chronology(physical, metadata),
        "negative_and_scope_controls": controls(physical, metadata),
        "successful_service_counts": dict(COUNTS),
        "successful_service_instructions": dict(STEPS),
        "scope": "Local graph only; retained raw source arithmetic and full #7596 composition are not executed here.",
    }
    require(json.loads(json.dumps(result)) == json.loads((HERE / "RESULT.json").read_text()), "independent receipt mismatch")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

