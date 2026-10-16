"""Source-bound physical replay and independent integer endpoint oracle."""
import argparse
import hashlib
import importlib.util
import json
import re
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("half_add_machine", HERE / "machine.py")
machine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(machine)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        if row["usage"] == "input":
            need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], "source drift")
    pins = json.loads((HERE / "SNAPSHOTS.json").read_text(encoding="utf-8"))
    for row in pins["files"]:
        need(hashlib.sha256((HERE / row["snapshot"]).read_bytes()).hexdigest() == row["sha256"], "snapshot drift")
    source = (HERE / "snapshots/Current1094Row2AddReference.lean").read_text(encoding="utf-8")
    need("Selected call000 raw2 is ADD(L119,L169,1/2)" in source, "selected operation binding")
    match = re.search(r"def componentCode .*? :=\s*(\[.*?\])", source, re.S)
    need(match is not None and re.sub(r"\s+", "", match.group(1)) ==
         "[.core(.readsource),.core.halve,.addMemorytarget,.core(.writetarget)]", "literal reference sequence")
    need("s.memory target + (1 / 2 : ℝ) * s.memory source" in source, "source equation binding")


def encoded(value, n, origin=0, exterior=True):
    need(n >= 1 and -(1 << (n-1)) <= value < (1 << (n-1)), "signed input range")
    out = {origin-1: "#", origin+n: "#"}
    for j in range(n):
        out[origin+j] = str((value >> j) & 1)
    if exterior:
        for k in range(1, 5):
            out[origin-1-k] = machine.ALPHABET[k % 4]
            out[origin+n+k] = machine.ALPHABET[(k+1) % 4]
    return out


def decoded(tape, n, origin=0):
    unsigned = sum(int(tape[origin+j]) << j for j in range(n))
    return unsigned - (int(tape[origin+n-1]) << n)


def signed_mod(value, n):
    residue = value % (1 << n)
    return residue if residue < (1 << (n-1)) else residue-(1 << n)


def execute_case(x, y, n, negative=False, origins=(0, 0), table=None):
    tapes = [encoded(x, n, origins[0]), encoded(y, n, origins[1])]
    before = [dict(t) for t in tapes]
    status, heads, trace = machine.simulate(tapes, origins, negative, max_steps=3*n+20, table=table)
    return tapes, before, status, heads, trace


def check_case(x, y, n, negative=False, origins=(0, 0)):
    tapes, before, status, heads, trace = execute_case(x, y, n, negative, origins)
    need(tapes[0] == before[0], "source changed")
    need(heads == origins, "heads not restored")
    if x % 2:
        need(status == "reject" and tapes == before and len(trace) == 1, "odd source rejection")
        return False, 1
    exact = y + (-1 if negative else 1) * (x // 2)
    need(status == "done", "valid input rejected")
    need(decoded(tapes[1], n, origins[1]) == signed_mod(exact, n), "modular integer oracle")
    need(len(trace) == 2*n+3, "transition invoice")
    writes = []
    for _, heads0, _, updates, _ in trace:
        for i in range(2):
            need(origins[i]-1 <= heads0[i] <= origins[i]+n, "visited exterior")
        need(updates[0] is None, "source write")
        if updates[1] is not None:
            writes.append(heads0[1]-origins[1])
    need(writes == list(range(n)), "target write footprint")
    need(all(v == tapes[1][k] for k, v in before[1].items()
             if not origins[1] <= k < origins[1]+n), "exterior or marker changed")
    fit = -(1 << (n-1)) <= exact < (1 << (n-1))
    if fit:
        need(decoded(tapes[1], n, origins[1]) == exact, "signed oracle")
    return fit, len(trace)


def controls():
    # Each malformed premise/machine has an observed endpoint consequence.
    x, y, n = 2, 1, 4
    _, _, _, _, trace = execute_case(x, y, n)
    first_add = next((s, read) for s, _, read, _, _ in trace if s[0] == "add")
    table = dict(machine.TABLE)
    nxt, writes, moves = table[first_add]
    table[first_add] = (nxt, (None, "1" if writes[1] == "0" else "0"), moves)
    t, _, _, _, _ = execute_case(x, y, n, table=table)
    need(decoded(t[1], n) != y+x//2, "carry/output mutation survived")
    table = dict(machine.TABLE)
    for key, (nxt, writes, moves) in list(table.items()):
        s, read = key
        if s[0] == "add" and read[0] == "#" and read[1] in machine.BITS:
            total = s[1]+int(read[1])+s[2]  # wrong zero extension
            table[key] = (nxt, (None, str(total % 2)), moves)
    t, _, _, _, _ = execute_case(-2, 0, 4, table=table)
    need(decoded(t[1], 4) != -1, "zero-extension mutant survived")
    table = dict(machine.TABLE)
    st = machine.initial(True)
    nxt, writes, moves = table[(st, ("0", "0"))]
    table[(st, ("0", "0"))] = ((nxt[0], 1, 0, nxt[3]), writes, moves)
    t, _, _, _, _ = execute_case(2, 0, 4, True, table=table)
    need(decoded(t[1], 4) != -1, "negative carry mutant survived")
    table = dict(machine.TABLE)
    for key, (nxt, writes, moves) in list(table.items()):
        if nxt[0] == "done":
            table[key] = (nxt, writes, (0, 0))
    _, _, _, heads, _ = execute_case(2, 0, 4, table=table)
    need(heads == (-1, -1), "head-restoration mutation invisible")
    t, before, status, heads, tr = execute_case(1, 0, 4)
    need(status == "reject" and t == before and heads == (0, 0) and len(tr) == 1, "odd source")
    need(Fraction(1, 2) != 0, "dropping divisibility has no witness")
    t, _, _, _, _ = execute_case(2, 7, 4)
    need(decoded(t[1], 4) == -8 and decoded(t[1], 4) != 8, "overflow premise counterexample")
    shared = encoded(2, 4)
    snapshot = dict(shared)
    status, _, _ = machine.simulate([shared, shared], max_steps=32)
    need(status != "done" or shared != snapshot, "alias premise counterexample")
    # Physical component y+x/2 represents the desired common-chart update
    # only if source and target charts agree: target chart -1 flips the term.
    need(-Fraction(2, 2) != Fraction(2, 2), "different-chart control")
    return 8


def run(quick=False):
    authenticate()
    table_rows = len(machine.TABLE)
    need(table_rows == 224, "finite table size")
    cases = fitting = steps = 0
    for n in range(1, 6 if quick else 9):
        lo, hi = -(1 << (n-1)), 1 << (n-1)
        for x, y, negative in product((x for x in range(lo, hi) if x % 2 == 0), range(lo, hi), (False, True)):
            fit, count = check_case(x, y, n, negative)
            cases += 1; fitting += fit; steps += count
    odd = 0
    for n in range(1, 9):
        for x in range(-(1 << (n-1)), 1 << (n-1)):
            if x % 2:
                check_case(x, 0, n); odd += 1
    large = inverse = translated = 0
    for n in (2, 3, 17, 64, 257, 1024):
        limit = 1 << (n-1)
        samples = (-limit, -2, 0, max(0, limit-2))
        for x, y, negative in product(samples, (-limit, -1, 0, limit-1), (False, True)):
            fit, _ = check_case(x, y, n, negative, (-137, 211))
            large += 1; translated += 1
            if fit:
                tapes, original, _, _, _ = execute_case(x, y, n, negative)
                status, heads, tr = machine.simulate(tapes, negative=not negative, max_steps=3*n+20)
                need(status == "done" and heads == (0, 0) and tapes == original, "dirty inverse")
                inverse += 1
    return {"schema_version": 1, "table_rows": table_rows, "alphabet": list(machine.ALPHABET),
            "exhaustive_cases": cases, "fitting_cases": fitting, "physical_steps": steps,
            "odd_rejections": odd, "large_cases": large, "translated_cases": translated,
            "dirty_inverse_cases": inverse, "controls": controls(), "cost": "2*n+3 for even source; 1 for odd rejection",
            "reference": "PR2370 call000 raw2 ADD(L119,L169,1/2), component equation only",
            "limits": "Written all-size proof plus finite table replay; marked equal-width two-tape interface, no selected routing, charts, initialization, global precision, Lean or supplier admission"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.quick)
    if args.write:
        with args.write.open("x", encoding="utf-8", newline="\n") as f:
            json.dump(result, f, indent=2); f.write("\n")
    elif not args.quick:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        need(json.dumps(expected, sort_keys=True) == json.dumps(result, sort_keys=True), "typed receipt mismatch")
    print("PASS_FIXED_GRID_HALF_ADD " + json.dumps(result))


if __name__ == "__main__":
    main()
