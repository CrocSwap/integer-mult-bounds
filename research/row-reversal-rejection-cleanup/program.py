"""Compile local visit tracking and retirement on acceptance or rejection.

The graph, not the Python compiler, executes the cleanup. The visit-marker
technique is classical. This transformer and its reversal application were
produced by Nick Petalas. Apache-2.0.
"""
from pathlib import Path
import hashlib
import importlib.util

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "inputs/reversal/reverse.py"
MACHINE_SOURCE = HERE / "inputs/reversal/inputs/controller_reference.py"
PINS = {
    "inputs/reversal/NOTICE.md": "940493cde2626cb55438be8abda72b9ad971bf059f7c9046591665163e266904",
    "inputs/reversal/reverse.py": "4b516d85baf3303db809bc1174394009b1fc71a8f7d17fb6c729ec8bb6aba245",
    "inputs/reversal/inputs/controller_reference.py":
        "e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73",
}


def load_source():
    for name, digest in PINS.items():
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != digest:
            raise ValueError("retained source drift: " + name)
    spec = importlib.util.spec_from_file_location("retained_reverse", SOURCE)
    if spec is None or spec.loader is None:
        raise ValueError("missing retained source loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(code, alphabet, tapes, private):
    if type(tapes) is not int or not 1 <= tapes <= 32 or not 1 <= len(code) <= 10000:
        raise ValueError("compiler size outside supported boundary")
    if (len(set(alphabet)) != len(alphabet) or not 1 <= len(alphabet) <= 16
            or "_" not in alphabet):
        raise ValueError("invalid finite alphabet")
    if any(type(t) is not int or not 0 <= t < tapes for t in private):
        raise ValueError("invalid private tape")
    for instruction in code:
        if not isinstance(instruction, (tuple, list)) or not instruction:
            raise ValueError("invalid instruction shape")
        op, *args = instruction
        arities = {"read": 2, "write": 2, "move": 2, "goto": 1, "halt": 0}
        if op not in arities or len(args) != arities[op]:
            raise ValueError("invalid instruction arity")
        if op in ("read", "write", "move"):
            if type(args[0]) is not int or not 0 <= args[0] < tapes:
                raise ValueError("invalid tape index")
        if op == "read":
            if not isinstance(args[1], dict) or not set(args[1]).issubset(alphabet):
                raise ValueError("invalid read branches")
            targets = tuple(args[1].values())
        elif op == "goto":
            targets = (args[0],)
        elif op == "write" and len(args) == 2 and args[1] in alphabet:
            targets = ()
        elif op == "move" and len(args) == 2 and args[1] in (-1, 1):
            targets = ()
        elif op == "halt" and not args:
            targets = ()
        else:
            raise ValueError("unsupported local instruction")
        if any(type(pc) is not int or not 0 <= pc < len(code) for pc in targets):
            raise ValueError("invalid control target")
    if code[-1][0] not in ("read", "goto", "halt"):
        raise ValueError("fallthrough outside program")


def cleanup(builder, tapes, private, status):
    """Retire one interval at a time, retaining its origin until the return."""
    for tape in range(tapes):
        tag = tapes + tape
        stem = f"{status}_{tape}_"
        builder.mark(stem + "left")
        builder.op("read", tag, {"_": stem + "begin", "1": stem + "back",
                                 "|": stem + "back"})
        builder.mark(stem + "back")
        builder.op("move", tape, -1)
        builder.op("move", tag, -1)
        builder.op("goto", stem + "left")
        builder.mark(stem + "begin")
        builder.op("move", tape, 1)
        builder.op("move", tag, 1)
        builder.mark(stem + "sweep")
        builder.op("read", tag, {"1": stem + "erase", "|": stem + "origin",
                                 "_": stem + "end"})
        builder.mark(stem + "erase")
        builder.op("write", tag, "_")
        builder.op("goto", stem + "cell")
        builder.mark(stem + "origin")
        builder.op("goto", stem + "cell")
        builder.mark(stem + "cell")
        if tape in private:
            builder.op("write", tape, "_")
        builder.op("move", tape, 1)
        builder.op("move", tag, 1)
        builder.op("goto", stem + "sweep")
        builder.mark(stem + "end")
        builder.op("move", tape, -1)
        builder.op("move", tag, -1)
        builder.mark(stem + "return")
        builder.op("read", tag, {"_": stem + "return_step", "|": stem + "done"})
        builder.mark(stem + "return_step")
        builder.op("move", tape, -1)
        builder.op("move", tag, -1)
        builder.op("goto", stem + "return")
        builder.mark(stem + "done")
        builder.op("write", tag, "_")
    builder.mark(status + "_halt")
    builder.op("halt")


def compile_tidy(source, code, alphabet, tapes=13, private=tuple(range(4, 13))):
    validate(code, alphabet, tapes, private)
    builder = source.Builder()
    for tape in range(tapes):
        builder.op("write", tapes + tape, "|")
    for pc, instruction in enumerate(code):
        builder.mark(f"source_{pc}")
        op, *args = instruction
        if op == "read":
            branches = {s: f"source_{target}" for s, target in args[1].items()}
            builder.op("read", args[0], {s: branches.get(s, "reject_0_left")
                                        for s in alphabet})
        elif op == "goto":
            builder.op("goto", f"source_{args[0]}")
        elif op == "halt":
            builder.op("goto", "accept_0_left")
        elif op == "move":
            tape, direction = args
            builder.op("move", tape, direction)
            builder.op("move", tapes + tape, direction)
            builder.op("read", tapes + tape,
                       {"_": f"new_{pc}", "1": f"source_{pc+1}",
                        "|": f"source_{pc+1}"})
            builder.mark(f"new_{pc}")
            builder.op("write", tapes + tape, "1")
            builder.op("goto", f"source_{pc+1}")
        else:
            builder.op(*instruction)
    cleanup(builder, tapes, private, "accept")
    cleanup(builder, tapes, private, "reject")
    graph, result_alphabet = builder.finish(tuple(dict.fromkeys((*alphabet, "_", "1", "|"))))
    halts = {status: builder.labels[status + "_halt"] for status in ("accept", "reject")}
    return graph, result_alphabet, halts
