#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact maximal invariant guard on one complete two-digit quotient."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Y = 128
C = 4
SIZE = Y * C * C * C
State = tuple[int, int, int, int]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def checked_state(state: State) -> State:
    need(isinstance(state, tuple) and len(state) == 4, "four-field state")
    need(all(type(x) is int for x in state), "integer state fields")
    need(0 <= state[0] < Y, "target quotient range")
    need(all(0 <= x < C for x in state[1:]), "compact/source range")
    return state


def mask(source: int) -> int:
    return (source & 1) + 8 * ((source >> 1) & 1)


def pack(target: int) -> int:
    return (target & 1) + 2 * ((target >> 3) & 1)


def early(target: int, temporary: int, controls: int) -> tuple[int, int]:
    target = (target + 2 * ((controls & 1) * (temporary & 1)
              + 8 * ((controls >> 1) & 1) * ((temporary >> 1) & 1))) % Y
    temporary = (temporary + pack(target)) % C
    target = (target + (controls & 1) * (1 - 2 * (temporary & 1))
              + 8 * ((controls >> 1) & 1)
              * (1 - 2 * ((temporary >> 1) & 1))) % Y
    temporary = (temporary - pack(target ^ mask(controls))) % C
    return target, temporary


def raw(state: State) -> State:
    target, temporary, control, source = state
    target, temporary = early(target, temporary, control)
    target, temporary = early(target, temporary, (control + source) % C)
    return target, temporary, control, source


def ideal(state: State) -> State:
    target, temporary, control, source = state
    return target ^ mask(source), temporary, control, source


def carry_guard(state: State) -> bool:
    """PR1603's H, specialized to n=2, K=3, G=1, rho=2."""
    target, temporary, control, source = state
    carry = 0
    for i in range(2):
        ti = (temporary >> i) & 1
        ui = (control >> i) & 1
        ci = (source >> i) & 1
        active = ui | ci
        parity = (target >> (3 * i)) & 1
        wide = (target >> (3 * i + 1)) & 3
        if active and (carry or ti == 1):
            return False
        if i == 0 and (ui + ci >= 2 or wide + active * ti >= 4):
            return False
        carry = (ti + parity + carry) // 2
    return True


def safe(state: State) -> bool:
    target, temporary, control, source = checked_state(state)
    extra = source == 0 and temporary == 1 and control == 2 and target % 2 == 1
    return carry_guard(state) or extra


def literal_full(state: State, low: int) -> tuple[int, int, int, int]:
    """Ten full-field rotations; uses division, full 9-bit targets and digits."""
    target, temporary, control, source = state
    target = 4 * target + low
    loaded = (control + source) % 4
    for current_control in (control, loaded):
        z = [current_control % 2, current_control // 2]
        for phase in range(4):
            if phase in (0, 2):
                digits = [temporary % 2, temporary // 2]
                offset = 0
                for i, place in enumerate((4, 32)):
                    value = 2 * digits[i] if phase == 0 else 1 - 2 * digits[i]
                    offset += z[i] * value * place
                target = (target + offset) % 512
            else:
                amount = 0
                for i, place in enumerate((4, 32)):
                    bit = (target // place) % 2
                    if phase == 3:
                        bit = (bit + z[i]) % 2
                    amount += bit * (i + 1)
                temporary = (temporary + (amount if phase == 1 else -amount)) % 4
    restored_control = (loaded - source) % 4
    return target, temporary, restored_control, source


def index(state: State) -> int:
    target, temporary, control, source = state
    return (((source * C + control) * C + temporary) * Y + target)


def decode(number: int) -> State:
    number, target = divmod(number, Y)
    number, temporary = divmod(number, C)
    source, control = divmod(number, C)
    return target, temporary, control, source


def literal_permutation() -> tuple[list[int], list[int], int]:
    actual = [0] * SIZE
    wanted = [0] * SIZE
    full_cases = 0
    for number in range(SIZE):
        state = decode(number)
        need(index(state) == number, "index round trip")
        target_state = ideal(state)
        wanted[number] = index(target_state)
        for low in range(4):
            result = literal_full(state, low)
            quotient, retained_low = divmod(result[0], 4)
            need(retained_low == low, "low target spectator")
            normalized = (quotient, *result[1:])
            need(normalized == raw(state), "full/lifted execution mismatch")
            if low == 0:
                actual[number] = index(normalized)
            full_cases += 1
    need(sorted(actual) == list(range(SIZE)), "raw permutation")
    need(sorted(wanted) == list(range(SIZE)), "ideal permutation")
    return actual, wanted, full_cases


def invariant_cycles(actual: list[int], wanted: list[int]) -> list[bool]:
    """Keep exactly the complete raw-permutation cycles contained in agreement."""
    visited = [False] * SIZE
    core = [False] * SIZE
    for start in range(SIZE):
        if visited[start]:
            continue
        cycle = []
        current = start
        for _ in range(SIZE):
            if visited[current]:
                break
            cycle.append(current)
            visited[current] = True
            current = actual[current]
        need(current == start, "permutation cycle closure")
        if all(actual[v] == wanted[v] for v in cycle):
            for v in cycle:
                core[v] = True
    need(all(visited), "complete permutation partition")
    return core


def core_check(actual: list[int], wanted: list[int], core: list[bool]) -> dict:
    old = [carry_guard(decode(i)) for i in range(SIZE)]
    formula = [safe(decode(i)) for i in range(SIZE)]
    need(formula == core, "explicit guard is not the maximal invariant core")
    need(all(not old[i] or core[i] for i in range(SIZE)), "old guard inclusion")
    need(all(core[i] == core[wanted[i]] for i in range(SIZE)), "T invariance")
    need(all(core[i] == core[actual[i]] for i in range(SIZE)), "S invariance")
    extra = [i for i in range(SIZE) if core[i] and not old[i]]
    need((sum(old), sum(core), len(extra)) == (2368, 2432, 64), "guard counts")
    need(all(decode(i)[1:] == (1, 2, 0) and decode(i)[0] % 2 for i in extra),
         "complete extra-branch classification")
    bitmap = bytes(sum(core[8 * j + k] << k for k in range(8))
                   for j in range(SIZE // 8))
    return {"old_good": sum(old), "maximal_good": sum(core), "extra": len(extra),
            "core_bitmap_sha256": sha256(bitmap).hexdigest(),
            "extra_witness": list(decode(extra[0]))}


def repair_check(actual: list[int], wanted: list[int], core: list[bool]) -> dict:
    inverse = [0] * SIZE
    payload = [0] * SIZE
    for original, current in enumerate(actual):
        inverse[current] = original
        payload[current] = original
    holes = [current for current in range(SIZE) if not core[current]]
    records = sorted((wanted[inverse[current]], payload[current]) for current in holes)
    need([key for key, _ in records] == holes, "repair destinations are exact holes")
    for key, tag in records:
        payload[key] = tag
    need(all(payload[wanted[i]] == i for i in range(SIZE)), "full payload endpoint")
    wrong = payload[:]
    for current in holes:
        wrong[wanted[current]] = inverse[current]
    wrong_count = sum(wrong[wanted[i]] != i for i in range(SIZE))
    need(wrong_count > 0, "wrong current-key repair control")
    need(len(holes) == 5760, "exact repair-record count")
    return {"records": len(holes), "old_records": SIZE - 2368,
            "endpoint_tags": SIZE, "wrong_key_misplacements": wrong_count}


def controls(actual: list[int], wanted: list[int], core: list[bool]) -> dict:
    agreement = [actual[i] == wanted[i] for i in range(SIZE)]
    need(any(agreement[i] and not agreement[wanted[i]] for i in range(SIZE)),
         "agreement-only predicate unexpectedly invariant")
    witness = next(i for i in range(SIZE) if agreement[i] and not core[i])
    need(safe((1, 1, 2, 0)) and not carry_guard((1, 1, 2, 0)),
         "missing new branch control")
    need(safe((0, 1, 2, 0)) and carry_guard((0, 1, 2, 0)),
         "even parity is already covered by the old guard")
    altered = 0
    for field in (1, 2, 3):
        found = False
        for state in product(range(Y), range(C), range(C), range(C)):
            extra = state[0] % 2 == 1
            for j, value in ((1, 1), (2, 2), (3, 0)):
                if j != field:
                    extra = extra and state[j] == value
            if extra and not core[index(state)]:
                found = True
                break
        need(found, "deleted extra-branch condition was not rejected")
        altered += 1
    invalid = [(-1, 0, 0, 0), (Y, 0, 0, 0), (0, -1, 0, 0),
               (0, 0, C, 0), (0, 0, 0, C), (False, 0, 0, 0), (0, 0, 0)]
    for state in invalid:
        try:
            safe(state)
        except ValueError:
            continue
        raise ValueError("invalid state accepted")
    return {"agreement_only_witness": list(decode(witness)),
            "extra_condition_mutations": altered, "invalid_inputs": len(invalid),
            "new_branch_required": True, "even_branch_already_in_old_guard": True}


def source_pins() -> int:
    entries = json.loads((HERE / "SOURCES.json").read_text())["files"]
    live = [entry for entry in entries if entry["usage"] == "input"]
    for entry in live:
        data = (ROOT / entry["path"]).read_bytes()
        need(sha256(data).hexdigest() == entry["sha256"], "source drift: " + entry["path"])
    return len(live)


def main() -> None:
    pins = source_pins()
    actual, wanted, full_cases = literal_permutation()
    core = invariant_cycles(actual, wanted)
    result = {"status": "PASS_COMPACT_MAXIMAL_INVARIANT_GUARD",
              "claim_type": "finite optimal-guard certificate and scoped repair proof",
              "geometry": {"n": 2, "K": 3, "G": 1, "rho": 2},
              "quotient_states": SIZE, "full_target_cases": full_cases,
              "guard": core_check(actual, wanted, core),
              "repair": repair_check(actual, wanted, core),
              "controls": controls(actual, wanted, core), "live_source_pins": pins}
    result["package_sha256"] = {
        p.name: sha256(p.read_bytes()).hexdigest()
        for p in sorted(HERE.iterdir()) if p.is_file()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
