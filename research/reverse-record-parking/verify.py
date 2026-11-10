"""Exact new-controller conformance and action counts. Apache-2.0."""

import ast
from dataclasses import replace
import hashlib
from itertools import product
import json
from pathlib import Path

from controller import ALPHABET, Action, compile_table, run, validate_table

ROOT = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def charge(command: str, n: int = 0) -> tuple[int, int, int, int]:
    if command == "begin":
        return 1, 2, 1, 1
    if command == "end":
        return 2, 4, 1, 1
    return 2 * n + 3, 4 * n + 6, 2 * n + 2, 3 * n + 3


def dense_run(table: dict, tapes: list[dict], heads: list[int], command: str,
              limit: int) -> tuple[list[dict], list[int], str, tuple]:
    """A separate bounded array interpreter; shares the finite table only."""
    low = min(*heads, *(min(t, default=0) for t in tapes)) - limit - 2
    high = max(*heads, *(max(t, default=0) for t in tapes)) + limit + 2
    require(high - low < 500_000, "dense allocation budget")
    arrays = [[t.get(i, "_") for i in range(low, high + 1)] for t in tapes]
    cursor = [h - low for h in heads]
    state, writes, moves = command, 0, 0
    for count in range(1, limit + 1):
        action = table[state, arrays[0][cursor[0]], arrays[1][cursor[1]]]
        for i, symbol in enumerate((action.write_p, action.write_b)):
            if symbol is not None:
                arrays[i][cursor[i]] = symbol
                writes += 1
        cursor = [cursor[0] + action.move_p, cursor[1] + action.move_b]
        moves += abs(action.move_p) + abs(action.move_b)
        state = action.next_state
        if state in ("done", "reject"):
            output = [{i + low: v for i, v in enumerate(a) if v != "_"}
                      for a in arrays]
            return output, [c + low for c in cursor], state, (count, 2*count, writes, moves)
    raise RuntimeError("dense step budget exhausted")


def base_tapes(h: int = 0, a: int = 0) -> tuple[list[dict], list[int]]:
    # Opaque caller data deliberately includes every symbol, except blank.
    parking = {h - 12 + i: symbol for i, symbol in enumerate(ALPHABET[1:])}
    port = {a - 1: "^", a - 9: "R", a - 8: "1"}
    return [parking, port], [h, a]


def execute(table: dict, tapes: list[dict], heads: list[int], command: str,
            n: int, dense: bool) -> tuple[int, int, int, int]:
    limit = 2 * n + 12
    if dense:
        other = dense_run(table, tapes, heads, command, limit)
    status, bill = run(table, tapes, heads, command, limit)
    require(status == "done", "valid command rejected")
    require(bill == charge(command, n), "literal action count differs from formula")
    if dense:
        require((tapes, heads, status, bill) == other, "interpreter disagreement")
    return bill


def one_packet(table: dict, bits: str, h: int = 0, a: int = 0,
               dense: bool = True) -> tuple[int, int, int, int]:
    tapes, heads = base_tapes(h, a)
    initial = [dict(t) for t in tapes]
    n = len(bits)
    tapes[1].update({a + i: bit for i, bit in enumerate(bits + "$")})
    bill = list(execute(table, tapes, heads, "begin", 0, dense))
    pushed = execute(table, tapes, heads, "push", n, dense)
    expected = dict(initial[0])
    expected[h] = "F"
    expected[h + 1] = "R"
    expected.update({h + 2 + i: bit for i, bit in enumerate(reversed(bits))})
    require(tapes == [expected, initial[1]], "wrong reversed record or consumed port")
    require(heads == [h + n + 2, a], "wrong PUSH boundary heads")
    popped = execute(table, tapes, heads, "pop", n, dense)
    expected_port = dict(initial[1])
    expected_port.update({a + i: bit for i, bit in enumerate(bits + "$")})
    require(tapes == [initial[0] | {h: "F"}, expected_port], "POP packet/prefix mismatch")
    require(heads == [h + 1, a], "wrong POP boundary heads")
    ended = execute(table, tapes, heads, "end", 0, dense)
    require(tapes == [initial[0], expected_port] and heads == [h, a], "END mismatch")
    for item in (pushed, popped, ended):
        bill = [x + y for x, y in zip(bill, item)]
    require(bill == [4*n+9, 8*n+18, 4*n+6, 6*n+8], "complete pair invoice")
    return tuple(bill)


def nested(table: dict, depth: int) -> tuple[int, int]:
    tapes, heads = base_tapes(-17, 13)
    initial = [dict(t) for t in tapes]
    records = []
    ledger = [0, 0, 0, 0]
    volume = 0
    for level in range(depth):
        bills = [execute(table, tapes, heads, "begin", 0, False)]
        pair = ("", ("01101" * ((level % 7) + 1))[:level % 23])
        records.append(pair)
        for bits in pair:
            a = heads[1]
            tapes[1].update({a + i: bit for i, bit in enumerate(bits + "$")})
            bills.append(execute(table, tapes, heads, "push", len(bits), False))
            volume += len(bits)
        for bill in bills:
            ledger = [x + y for x, y in zip(ledger, bill)]
    for pair in reversed(records):
        for bits in reversed(pair):
            bill = execute(table, tapes, heads, "pop", len(bits), False)
            a = heads[1]
            actual = "".join(tapes[1].get(a + i, "_") for i in range(len(bits) + 1))
            require(actual == bits + "$", "nested LIFO/order/extent")
            for i in range(len(bits) + 1):
                del tapes[1][a + i]  # Caller consumes its returned packet.
            ledger = [x + y for x, y in zip(ledger, bill)]
        bill = execute(table, tapes, heads, "end", 0, False)
        ledger = [x + y for x, y in zip(ledger, bill)]
    r = 2 * depth
    expected = [4*volume+6*r+3*depth, 8*volume+12*r+6*depth,
                4*volume+4*r+2*depth, 6*volume+6*r+2*depth]
    require(ledger == expected, "nested aggregate invoice")
    require(tapes == initial and heads == [-17, 13], "nested ancestor/port/head return")
    return volume, r


def rejection_checks(table: dict) -> int:
    count = 0
    for command, contents in (("pop", "F"), ("end", "FR"), ("end", "FR1")):
        tapes, heads = base_tapes()
        tapes[0].update(enumerate(contents))
        heads[0] = len(contents)
        before = [dict(t) for t in tapes], list(heads)
        status, bill = run(table, tapes, heads, command, 12)
        require(status == "reject" and bill[2] == 0, "boundary rejection wrote data")
        require((tapes, heads) == before, "boundary rejection changed heads or cells")
        count += 1
    for bad in ({}, table | {("bogus", "_", "_"): Action("done")},
                table | {("begin", "_", "_"): Action("done", move_p=2)},
                table | {("begin", "_", "_"): Action("done", write_p="bad")}):
        try:
            validate_table(bad)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid table accepted")
    return count


def mutation_checks(table: dict) -> int:
    mutations = (("copy", "_", "0", {"write_p": "1"}),
                 ("deliver", "1", "_", {"write_b": "0"}),
                 ("deliver", "R", "_", {"write_p": None}),
                 ("rewind", "_", "^", {"move_b": 0}),
                 ("end_check", "F", "0", {"write_p": None}))
    for state, p, b, changes in mutations:
        mutant = dict(table)
        mutant[state, p, b] = replace(table[state, p, b], **changes)
        try:
            one_packet(mutant, "010", dense=False)
        except (ValueError, RuntimeError):
            continue
        raise ValueError("semantic mutant survived")
    # Deliberately demonstrate the weaker malformed-port guarantee.
    tapes, heads = base_tapes()
    tapes[0].update(enumerate("FR10"))
    heads[0] = 4
    tapes[1][1] = "1"
    before = [dict(t) for t in tapes]
    status, bill = run(table, tapes, heads, "pop", 20)
    require(status == "reject" and bill[2] > 0 and tapes != before,
            "malformed-port scope control")
    return len(mutations) + 1


def syntax_checks() -> None:
    for name in ("controller.py", "verify.py"):
        source = (ROOT / name).read_text()
        tree = ast.parse(source)
        compile(source, str(ROOT / name), "exec")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                require(node.end_lineno - node.lineno + 1 <= 60, "function over one page")


def main() -> None:
    table = compile_table()
    syntax_checks()
    totals = [0, 0, 0, 0]
    cases = volume = 0
    for n in range(11):
        for letters in product("01", repeat=n):
            bill = one_packet(table, "".join(letters))
            totals = [x + y for x, y in zip(totals, bill)]
            cases += 1
            volume += n
    translated = 0
    for h, a in ((-103, 37), (71, -89), (0, 0)):
        for n in (0, 1, 2, 7, 64, 1024, 16384):
            bits = ("0110100" * ((n + 6) // 7))[:n]
            one_packet(table, bits, h, a, dense=n <= 1024)
            translated += 1
    nesting = [nested(table, d) for d in (1, 2, 7, 32, 129)]
    controls = rejection_checks(table) + mutation_checks(table)
    require(totals[0] == 4*volume + 9*cases, "enumerated aggregate steps")
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(ROOT.iterdir()) if p.is_file()}
    receipt = {"status": "PASS_REVERSE_RECORD_PARKING", "table_entries": len(table),
               "packets": cases, "payload_bits": volume, "complete_pair_bill": totals,
               "translated_cases": translated, "nested_volume_records": nesting,
               "controls": controls, "sha256": hashes,
               "scope": "new finite controller and scoped written all-size proof; no new kappa"}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
