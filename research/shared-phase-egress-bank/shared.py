"""Share successful phase/egress lifetimes on twenty physical tapes.

The retained component programs keep their original credit and exact bytes.
This module authenticates them and changes only finite control addresses.
"""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
MAX_LOCATIONS = 25000
SYMBOLS = frozenset(("_", "0", "1", "|"))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    rows = json.loads((HERE / "EXPORT-PINS.json").read_text())["files"]
    need(len(rows) == 7, "seven retained source files required")
    for row in rows:
        data = (HERE / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob")
    return rows


def validate(code, tapes):
    need(0 < len(code) <= MAX_LOCATIONS, "fixed graph size")
    need(2 <= tapes <= 20, "tape capacity")
    for instruction in code:
        op, *args = instruction
        need(op in ("read", "write", "move", "goto", "halt"), "literal opcode")
        if op in ("read", "write", "move"):
            need(type(args[0]) is int and 0 <= args[0] < tapes, "tape index")
        if op == "read":
            need(set(args[1]) <= SYMBOLS, "scanned alphabet")
            need(all(type(v) is int and 0 <= v < len(code) for v in args[1].values()),
                 "branch target")
        elif op == "goto":
            need(type(args[0]) is int and 0 <= args[0] < len(code), "jump target")
        elif op == "move":
            need(args[1] in (-1, 1), "unit movement")
        elif op == "write":
            need(args[1] in SYMBOLS, "written alphabet")
        else:
            need(not args, "halt arity")


def relocate(code, offset):
    result = []
    for instruction in code:
        op, *args = instruction
        if op == "read":
            args[1] = {symbol: target + offset for symbol, target in args[1].items()}
        elif op == "goto":
            args[0] += offset
        result.append((op, *args))
    return result


def compile_shared():
    authenticate()
    # Only two authenticated, fixed-size generators are loaded at compile time.
    sys.path.insert(0, str(HERE / "inputs"))
    from native import egress, phase
    egress_code, _ = egress.compile_egress()
    phase_code, _ = phase.compile_phase()
    validate(egress_code, 18)
    validate(phase_code, 20)
    need(sum(op[0] == "halt" for op in egress_code) == 1, "unique egress success")
    need(sum(op[0] == "halt" for op in phase_code) == 1, "unique phase success")
    entry_phase = len(egress_code)
    code = [("goto", entry_phase) if op[0] == "halt" else op for op in egress_code]
    code.extend(relocate(phase_code, entry_phase))
    validate(code, 20)
    return tuple(code), entry_phase
