# SPDX-License-Identifier: Apache-2.0
"""One-port signed caller cut, using exact pinned Laurent and modular engines."""
from collections import Counter
from itertools import combinations
import gzip
import hashlib
import json

import sys
from fractions import Fraction
from pathlib import Path

CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
NATIVE = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
HOST, FIRST, SECOND = 1423, 1580, 1659
HOST_ROLES = (8, 0, 18, 26)
PORT = 0
HERE = Path(__file__).resolve().parent
INPUT_NAMES = ('CALLER.json', 'WORD.json.gz', 'full_body.py', 'host_rank.py')
READ = (
    (CALLER, "research/signed-caller-8x9/expected/ODD-TYPE-AB-CALLER.json",
     "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"),
    (NATIVE, "research/p104-helper-319-fused-return/WORD.json.gz",
     "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"),
    ("b567f9a4f5699c5e447100c38b5745526b15b770",
     "research/p104-type-a-query-fixed-cut/engines/lead/full_body.py",
     "352c7d594f357333f027dc46eef0e82226b9552ab31d6890b1695fe994e8c3b4"),
    ("ebb2b1c5b62344f56c62d526558f059c99dd7077",
     "research/p104-paired-query-host-rank-bound/engines/host_rank.py",
     "ffbcde67a1f0a7595233baf0e5b40e73ab75fe1324139ecf374040a88d62a13e"),
)


def read_source(name, spec):
    data = (HERE / "inputs" / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != spec[2]:
        raise ValueError(f"changed pinned input: {name}")
    return data


def load_engine(raw, filename):
    env = {"__name__": "_pinned_engine"}
    exec(compile(raw, filename, "exec"), env)
    return env


def uses(e):
    if e[0] == "J":
        return set(e[2])
    if e[0] == "B":
        return set()
    return set(e[2:4] if e[1] in ("ADD", "QUERY", "SWAP") else e[2:3])


def writes(e):
    if e[0] == "J" or e[:2] == ["A", "SWAP"]:
        return uses(e)
    return {e[2]} if e[0] == "A" else set()


def idle_moves(events):
    """Both pre-idle ADDs cancel, with no intervening observation of that row."""
    moves = []
    for t in range(HOST + 1, 1489):
        e = events[t]
        if e[:2] != ["A", "IDLE_ONE"]:
            continue
        r, mask = e[2:]
        donor = 0 if r < 18 else 18
        assert r not in HOST_ROLES
        assert len(mask) and 8 in mask
        contacts = [s for s in range(HOST, t) if r in uses(events[s])]
        assert len(contacts) == 2
        early, late = contacts
        assert events[early] == ["A", "ADD", r, donor, "2"]
        assert events[late] == ["A", "ADD", r, donor, "-2"]
        assert all(donor not in writes(events[s]) for s in range(early + 1, late))
        moves.append({"idle": t, "role": r, "mask": mask, "canceled_adds": contacts})
    assert len(moves) == 14 and len({m["role"] for m in moves}) == 14
    return moves


def value(poly, flipped=()):
    result = [Fraction(0), Fraction(0)]
    for (imag, powers), coefficient in poly.items():
        sign = (-1) ** (sum(powers[j - 1] for j in flipped) % 2)
        result[imag] += sign * coefficient
    return tuple(result)


def describe(poly):
    return [
        [imag, [[j + 1, e] for j, e in enumerate(powers) if e], str(coefficient)]
        for (imag, powers), coefficient in sorted(poly.items())
    ]


def diff(a, b):
    result = dict(a)
    for key, v in b.items():
        x = result.get(key, 0) - v
        if x:
            result[key] = x
        else:
            result.pop(key, None)
    return result


def apply_matrix(matrix, column, engine):
    out = [{} for _ in matrix[0]]
    for j, src in enumerate(column):
        for (imag, powers), coeff in src.items():
            for r, row in enumerate(matrix[j]):
                if row:
                    engine["add_scaled"](out[r], row, coeff, imag, powers)
    return out


def native_main_roles(word):
    return (set(word["live"]) | {r + 112 for r in word["live"]}
            | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))


def chart_phase(axes):
    phase = Counter()
    for axis in axes:
        bits = [i for i in range(9) if axis >> i & 1]
        for i in bits:
            phase[i,] += 1
        for i, j in combinations(bits, 2):
            phase[i, j] -= 2
    return phase


def add_entry(state, role, value):
    total = state.get(role, 0) + value
    if total:
        state[role] = total
    else:
        state.pop(role, None)


def walk(program, state, reverse=False):
    result = dict(state)
    copy_guards = []
    for clock, event in reversed(program) if reverse else program:
        op, dest, *args = event
        if op == "ADD":
            source, scalar = args[:2]
            if reverse:
                if dest in result:
                    add_entry(result, source, Fraction(scalar) * result[dest])
            elif source in result:
                add_entry(result, dest, Fraction(scalar) * result[source])
        elif op == "SCALE":
            if dest in result:
                result[dest] *= Fraction(args[0])
        elif op == "COPY":
            source = args[0]
            assert args[1] == "1"
            if reverse:
                add_entry(result, source, result.pop(dest, 0))
            else:
                if result.get(dest):
                    copy_guards.append(clock)
                result.pop(dest, None)
                add_entry(result, dest, result.get(source, 0))
        elif op in ("INIT", "CLEAR"):
            result.pop(dest, None)
        else:
            assert op == "MOVE"
    return result, copy_guards


def determinant(matrix):
    a = [list(row) for row in matrix]
    total = Fraction(1)
    for j in range(len(a)):
        pivot = next((k for k in range(j, len(a)) if a[k][j]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != j:
            a[pivot], a[j] = a[j], a[pivot]
            total = -total
        f = a[j][j]
        total *= f
        for k in range(j + 1, len(a)):
            m = a[k][j] / f
            a[k] = [x - m * y for x, y in zip(a[k], a[j], strict=True)]
    return total


def examine_carriers(word, binding):
    native_main = native_main_roles(word)
    helpers = set(range(word["public"])) - native_main
    assert len(native_main) == 400 and len(helpers) == 1101
    program = list(enumerate(word["program"]))
    phases = [chart_phase(frame) for frame in word["frames"]]
    central_axis = word["ports"][PORT]
    assert central_axis == 11
    central = chart_phase([central_axis])
    live_chart = dict(enumerate(word["initial"]))
    pure = []
    candidates = []
    witnesses = {988: 988, 225: 225, 224: 224, 989: 377}
    for clock, (op, role, *args) in program:
        if op == "INIT":
            live_chart[role] = args[0]
        elif op == "CLEAR":
            del live_chart[role]
        elif op == "MOVE":
            a, b, owned = args
            assert live_chart[role] == a
            live_chart[role] = b
            if abs(len(word["frames"][a]) - len(word["frames"][b])) != 1:
                continue
            gap = {key: phases[b][key] - phases[a][key] - central[key]
                   for key in phases[b].keys() | phases[a].keys() | central.keys()}
            if any(value % (2 if len(key) == 1 else 4) for key, value in gap.items()):
                continue
            exact = all(value % 4 == 0 for value in gap.values())
            pure.append([clock, role, a, b, "helper" if role in helpers else "owned" if owned else "main", exact])
            if role in helpers:
                assert exact and (a, b) == (3, 0)
                bank = sorted(r for r, c in live_chart.items() if c == b)
                candidates.append((clock, role, bank))
    assert [(t,r) for t,r,_ in candidates] == [(32194,988),(32641,225),(32643,224),(35131,989)]
    assert len(pure) == 8 and all(e[5] for e in pure)
    receipt, exits = [], []
    for clock, role, bank in candidates:
        before, after = program[:clock + 1], program[clock + 1:]
        assert role in bank and witnesses[role] in helpers
        read = next((t,e) for t,e in after if role in
                    (e[1:3] if e[0] in ("ADD","COPY") else e[1:2]))
        assert read[0] == clock + 1 and read[1][-1] == 0
        dirty = witnesses[role]
        observed, guard = walk(before, {dirty: Fraction(1)})
        assert not guard
        seen = [observed.get(r, 0) for r in bank]
        reverse_seen = [walk(before, {r: Fraction(1)}, reverse=True)[0].get(dirty, 0) for r in bank]
        assert seen == reverse_seen
        assert seen[bank.index(role)] != 0 and sum(bool(v) for v in seen) == 1
        response, guard = walk(after, {role: Fraction(1)})
        assert not guard
        exits.append(response)
        receipt.append({"move": clock, "native_helper": role, "chart_0_bank": bank,
                        "first_contact": list(read), "dirty_input": dirty,
                        "normalized_dirty_bank_column": [str(x) for x in seen],
                        "changed_helper_returns": len(set(response) & helpers),
                        "changed_main_returns": len(set(response) & native_main),
                        "port_0_changes": {r: str(response[r]) for r in binding.values() if r in response}})
    returns = [317, 929, 61, 1344]
    assert set(returns) <= helpers
    minor = [[Fraction(col.get(r, 0)) for col in exits] for r in returns]
    assert minor == [
        [2, 0, 0, 2], [0, Fraction(1,4), 0, 0], [0, 0, Fraction(-5,8), 0], [0, 0, 0, 2]
    ]
    reverse_minor = [[walk(program[t+1:], {r: Fraction(1)}, reverse=True)[0].get(role, 0)
                      for t,role,_ in candidates] for r in returns]
    assert minor == reverse_minor
    assert determinant(minor) == Fraction(-5,8)
    assert receipt[0]["changed_main_returns"] == receipt[3]["changed_main_returns"] == 0
    assert [case["port_0_changes"] for case in receipt] == [{}, {112: "1"}, {}, {}]
    return {"central_axis": central_axis, "rank_one_central_moves": pure,
            "helper_readouts": receipt, "helper_return_rows": returns,
            "helper_return_minor": [[str(x) for x in row] for row in minor],
            "determinant": str(determinant(minor)),
            "evidence": "Chart-0 bank and helper-return minor checked in independent forward and reverse directions."}


def main():
    caller_raw, native_raw, laurent_raw, modular_raw = [read_source(name, spec) for name, spec in zip(INPUT_NAMES, READ, strict=True)]
    caller = json.loads(caller_raw)
    word = json.loads(gzip.decompress(native_raw))
    events = caller["events"]
    assert events[HOST] == ["J", 8, list(HOST_ROLES), [36, 37, "-1", "1/2"]]
    assert all(events[k] == ["A", "QUERY", 0, 1, -1] for k in (FIRST, SECOND))
    i = word["hosted"]["Dports"].index(PORT)
    assert caller["types"]["A"]["ports"][i] == PORT
    first = word["live"][PORT]
    binding = dict(zip(HOST_ROLES, (first, first + 112,
                                   word["hosted"]["X2"][i], word["hosted"]["Y2"][i]), strict=True))
    assert binding == {8: 0, 0: 112, 18: 772, 26: 882}
    moves = idle_moves(events)
    skipped = {m["idle"] for m in moves} | {s for m in moves for s in m["canceled_adds"]}
    engine = load_engine(laurent_raw, READ[2][1])
    mod = load_engine(modular_raw, READ[3][1])
    steps, hosts, _ = mod["compile_type_a"](caller)
    assert hosts[8] == HOST
    prime = mod["PRIME"]
    old_modular = list(mod["solve"](steps, FIRST, SECOND, HOST))

    def emit(t, phase, edit=False):
        engine["FIRST"] = engine["SECOND"] = t
        return engine["operators"](caller, phase, edit and t in (FIRST, SECOND))

    def tape(clocks, phase, edit=False):
        return [op for t in clocks for op in emit(t, phase, edit)]

    basis, apply = engine["basis"], engine["apply"]
    phases = []
    controls = []
    group_a = [*range(1, 8), *range(9, 18)]
    group_b = [*range(19, 26), *range(27, 36)]
    signs = {j: (-1) ** (j + int(j < pivot))
             for group,pivot in ((group_a,8),(group_b,26)) for j in group}
    for phase in range(4):
        original = tape(range(HOST, SECOND + 1), phase)
        new_suffix = tape(range(HOST + 1, SECOND + 1), phase, True)
        native = emit(HOST, phase)
        diagonal = tape([m["idle"] for m in moves], phase)
        kept = [t for t in range(HOST + 1, SECOND + 1) if t not in skipped]
        before = tape(kept, phase)
        after = tape(kept, phase, True)
        original_columns = [apply(original, basis(j)) for j in range(36)]
        required = [apply(new_suffix, [a.copy() for a in col], undo=True)
                    for col in original_columns]
        n = [apply(native, basis(j)) for j in range(36)]
        assert all(apply(before, apply(native, apply(diagonal, basis(j)))) == original_columns[j]
                   for j in range(36))
        retimed = [apply(diagonal, apply_matrix(required, apply(diagonal, basis(j), undo=True), engine))
                   for j in range(36)]
        assert all(apply(after, apply_matrix(retimed, apply(diagonal, basis(j)), engine)) == original_columns[j]
                   for j in range(36))

        d = {(i, j): f for j in range(36) for i in range(36)
             if (f := diff(required[j][i], n[j][i]))}
        shifted = {(i, j): f for j in range(36) for i in range(36)
                   if (f := diff(retimed[j][i], n[j][i]))}
        stages = sorted({k+1 for p in shifted.values() for _, powers in p
                         for k, v in enumerate(powers) if v})
        assert all(k == 8 for k in stages)
        for group, representative in ((group_a, 1), (group_b, 19)):
            for j in group:
                for i in range(36):
                    scaled = {key: c * signs[j] for key,c in shifted.get((i,representative),{}).items()}
                    assert scaled == shifted.get((i,j), {})
        for i in group_a:
            assert all((i,j) not in shifted for j in range(36))
        for i in group_b:
            assert all(shifted.get((i,j),{}) == shifted.get((19,j),{}) for j in range(36))
        summary = {
            "q_i_power": phase,
            "original_extra_entries": len(d),
            "retimed_extra_entries": len(shifted),
            "retimed_body_stages": stages,
            "retimed_extra_columns": sorted({j for _, j in shifted}),
            "retimed_extra_rows": sorted({i for i, _ in shifted}),
        }
        if phase == 0:
            assert not d and not shifted
            broken = sorted(set(kept) | {moves[0]["canceled_adds"][0]})
            uncancelled = apply(tape(broken, phase), apply(native, apply(diagonal, basis(0))))
            assert uncancelled != original_columns[0]
            controls.append("restoring one canceled ADD breaks the retiming equality")
        if phase == 2:
            assert value(d[8,1]) == (2,0) and value(d[8,1], (2,)) == (-2,0)
            assert value(shifted[8,1]) == (2,0) and value(shifted[8,1], (2,)) == (2,0)
            assert value(shifted[19,19]) == (4,0)
            assert value(shifted.get((8,19), {})) == value(shifted.get((19,1), {})) == (0,0)
            for j, column in enumerate(required):
                for i, coefficient in enumerate(column):
                    x, imag = value(diff(coefficient, apply(emit(HOST, 0), basis(j))[i]))
                    assert not imag and (x.numerator * pow(x.denominator, -1, prime)) % prime == old_modular[j][i]
            summary.update(
                spectator_witness=[describe(d[8,1]), str(value(d[8,1])[0]), str(value(d[8,1], (2,))[0])],
                retimed_witnesses=[[8,1,describe(shifted[8,1])], [19,19,describe(shifted[19,19])]],
                outside_input_minor_rows=[8,19], outside_input_minor_columns=[1,19],
                outside_input_minor_determinant=8,
            )
        phases.append(summary)
        summary["representative_columns"] = {
            j: {i: describe(p) for (i,k),p in sorted(shifted.items()) if j == k}
            for j in (*HOST_ROLES,1,19)
        }

    return {"source_pins": READ, "port": PORT, "stage_host": HOST, "queries": [FIRST, SECOND],
            "native_role_binding": binding, "hoisted_paid_idles": moves,
            "replay": "36 independent columns at each of four phases, 17 independent Laurent body variables",
            "proof_scope": "retiming preserves the full normalized Type A map, other ports and Type B retain their word",
            "phase_receipts": phases,
            "additional_input_aggregates": [dict((j,signs[j]) for j in g) for g in (group_a,group_b)],
            "additional_output_scatter": group_b,
            "carrier_checks": examine_carriers(word, binding), "controls": controls}


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Run this exact replay with assertions enabled")
    result = main()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif sys.argv[1:]:
        raise SystemExit("usage: verify.py [--emit]")
    else:
        assert (HERE / "RESULT.json").read_text() == json.dumps(result, indent=2, sort_keys=True) + "\n", "receipt changed"
        print("PASS stage-8 caller retiming, 144 Laurent columns, and four native carrier bounds")
