#!/usr/bin/env python3
"""Exact cross-fed endpoint and a matched-baseline obstruction; stdlib only."""
import itertools
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def apply(matrix, vector):
    return sum(((row & vector).bit_count() & 1) << i
               for i, row in enumerate(matrix))


def macro_word(a, b, c, mutant=None):
    n = len(a)
    identity = tuple(1 << i for i in range(n))
    word = [(1, 2, a), (2, 0, b), (1, 2, a),
            (0, 1, identity), (2, 0, b), (0, 1, identity),
            (0, 2, c), (2, 1, b), (0, 2, c)]
    if mutant == "omit_patch":
        del word[4]
    elif mutant == "omit_undo":
        del word[5]
    elif mutant == "wrong_close_source":
        word[7] = (2, 0, b)
    elif mutant == "second_read_before_patch":
        word.insert(4, word.pop(6))
    return word


def execute(word, state):
    state = list(state)
    for target, source, matrix in word:
        state[target] ^= apply(matrix, state[source])
    return tuple(state)


def endpoint(a, b, c, state):
    x, y, z = state
    y ^= apply(a, apply(b, x))
    x ^= apply(c, apply(b, y))
    return x, y, z


def direct(matrix, target, source, n):
    return [(target*n+i, source*n+j) for i, row in enumerate(matrix)
            for j in range(n) if row >> j & 1]


def parity(source, n):
    return [(source*n, source*n+j) for j in range(1, n)]


def scatter(source, n):
    return [(2*n+i, source*n) for i in range(n)]


def b_call(source, n):
    p = parity(source, n)
    return p + scatter(source, n) + p[::-1]


def scalar_words(n):
    identity = tuple(1 << i for i in range(n))
    a = list(identity)
    c = list(identity)
    if n > 1:
        a[0] ^= 2
        c[1] ^= 1
    a, c = tuple(a), tuple(c)
    ay = direct(a, 1, 2, n)
    cx = direct(c, 0, 2, n)
    shear = direct(identity, 0, 1, n)
    bx, by = b_call(0, n), b_call(1, n)
    eager = ay + bx + ay + bx + cx + by + cx + by
    carried = ay + bx + ay + shear + bx + shear + cx + by + cx
    # Same parity computation retained across both scatters in EACH CLOSED call.
    px, py = parity(0, n), parity(1, n)
    closed = (ay + px + scatter(0, n) + ay + scatter(0, n) + px[::-1]
              + cx + py + scatter(1, n) + cx + scatter(1, n) + py[::-1])
    return a, c, {"eager_complete_calls": eager,
                  "carried_complete_calls": carried,
                  "parity_retained_closed_calls": closed}


def scalar_execute(word, value):
    for target, source in word:
        value ^= ((value >> source) & 1) << target
    return value


def unpack(value, n):
    mask = (1 << n) - 1
    return tuple((value >> (n*i)) & mask for i in range(3))


def bill(word):
    gates = len(word)
    moves = sum(2 * (source+1 + abs(source-target)) for target, source in word)
    return {"scalar_xors": gates, "head_moves": moves,
            "data_reads": 3*gates, "data_writes": gates,
            "scalar_xors_with_scratch": 3*gates, "dispatches": gates,
            "unit_tape_total_excluding_common_admission": moves + 8*gates}


def tape_execute(word, value, width):
    """Literal origin/source/target/source/origin walk, independent of bill."""
    tape = [0] + [(value >> bit) & 1 for bit in range(width)]
    head, moves, temporary = 0, 0, 0
    for target, source in word:
        require(0 <= target < width and 0 <= source < width and target != source,
                "invalid scalar tape ports")
        source, target = source+1, target+1
        for address, action in ((source, "read"), (target, "write"),
                                (source, "read"), (0, "return")):
            moves += abs(address-head)
            head = address
            if action == "read":
                temporary ^= tape[head]
            elif action == "write":
                tape[head] ^= temporary
        require(temporary == 0 and head == 0, "dirty scalar or head exit")
    return sum(bit << i for i, bit in enumerate(tape[1:])), moves


def formal_check():
    # Free noncommutative module; each term is (operator word, dirty input).
    state = [{("", row)} for row in range(3)]
    operations = [(1, 2, "A"), (2, 0, "B"), (1, 2, "A"),
                  (0, 1, ""), (2, 0, "B"), (0, 1, ""),
                  (0, 2, "C"), (2, 1, "B"), (0, 2, "C")]
    for index, (target, source, operator) in enumerate(operations):
        state[target] ^= {(operator + word, row) for word, row in state[source]}
        if index == 2:
            require(state == [{("", 0)}, {("", 1), ("AB", 0)},
                              {("", 2), ("B", 0)}],
                    "first delivered boundary mismatch")
        if index == 5:
            require(state == [{("", 0)}, {("", 1), ("AB", 0)},
                              {("", 2), ("B", 1), ("BAB", 0)}],
                    "handoff boundary is not coherent")
    require(state == [{("", 0), ("CB", 1), ("CBAB", 0)},
                      {("", 1), ("AB", 0)}, {("", 2)}],
            "free noncommutative endpoint mismatch")
    return [sorted(row) for row in state]

def main():
    formal = formal_check()
    require(bill([(0, 2)])["head_moves"] == 10,
            "backward source-return travel undercount")
    require(tape_execute([(0, 2)], 4, 3) == (5, 10),
            "literal backward-visit control")
    matrices = list(itertools.product(range(4), repeat=2))
    basis = [(1 << bit, 0, 0) for bit in range(2)]
    basis += [(0, 1 << bit, 0) for bit in range(2)]
    basis += [(0, 0, 1 << bit) for bit in range(2)]
    cases = 0
    controls = {}
    for a, b, c in itertools.product(matrices, repeat=3):
        word = macro_word(a, b, c)
        for state in basis:
            expected = endpoint(a, b, c, state)
            require(execute(word, state) == expected, "matrix endpoint mismatch")
            require(execute(word[::-1], expected) == state, "inverse mismatch")
            cases += 1
        for mutant in ("omit_patch", "omit_undo", "second_read_before_patch", "wrong_close_source"):
            if mutant not in controls:
                for state in basis:
                    actual = execute(macro_word(a, b, c, mutant), state)
                    if actual != endpoint(a, b, c, state):
                        controls[mutant] = {"a": a, "b": b, "c": c,
                                             "input": state, "actual": actual,
                                             "expected": endpoint(a, b, c, state)}
                        break
    require(len(controls) == 4, "a malformed boundary was not rejected")
    invoices = {}
    dirty_cases = 0
    for n in range(1, 5):
        a, c, words = scalar_words(n)
        b = ((1 << n)-1,) * n
        for value in range(1 << (3*n)):
            expected = endpoint(a, b, c, unpack(value, n))
            for label, word in words.items():
                result = scalar_execute(word, value)
                require(unpack(result, n) == expected, label + " scalar mismatch")
                require(scalar_execute(word[::-1], result) == value,
                        label + " scalar inverse mismatch")
                tape_result, moves = tape_execute(word, value, 3*n)
                require(tape_result == result and moves == bill(word)["head_moves"],
                        label + " literal tape replay or bill mismatch")
            dirty_cases += 1
        readouts = 2*sum(row.bit_count() for row in a+c)
        require(len(words["eager_complete_calls"]) == 12*n-8+readouts, "eager bill")
        require(len(words["carried_complete_calls"]) == 11*n-6+readouts, "carried bill")
        require(len(words["parity_retained_closed_calls"]) == 8*n-4+readouts, "closed bill")
        require(len(words["carried_complete_calls"]) - len(words["parity_retained_closed_calls"]) == 3*n-2,
                "false strict saving against matched comparator")
        invoices[str(n)] = {label: bill(word) for label, word in words.items()}
    # Noncommuting pilot is explicit, not a commuting-only positive fixture.
    a, c, _ = scalar_words(4)
    b = (15,)*4
    require(any(apply(a, apply(b, x)) != apply(b, apply(a, x)) for x in range(16)),
            "pilot A and B commute")
    require(any(apply(c, apply(b, x)) != apply(b, apply(c, x)) for x in range(16)),
            "pilot C and B commute")
    print(json.dumps({"status": "PASS_CROSS_FED_HANDOFF_OBSTRUCTION",
                      "free_endpoint": formal, "matrix_triples": len(matrices)**3,
                      "matrix_basis_cases_forward_and_inverse": cases,
                      "dirty_states_all_three_words_and_inverses": dirty_cases,
                      "literal_tape_state_cases": 3*dirty_cases,
                      "backward_travel_control": "0->3->1->3->0 costs 10 moves",
                      "controls": controls, "invoices": invoices,
                      "scope": "typed identity; fixed parity-lowering obstruction, no recurrence or kappa"},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
