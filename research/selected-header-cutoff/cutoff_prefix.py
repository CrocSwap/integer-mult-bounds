"""Literal Gamma-header cutoff prefix joined to the published controller.

Apache-2.0. Prepared for CubeJerry with substantial OpenAI assistance.
All arithmetic below that chooses program edges is compile-time arithmetic.
The executing machine has only its program counter and scanned tape symbols.
"""
import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
PINS = {
    "controller_reference.py": "e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73",
    "selected_control.py": "1c977e9f4864d338f874aa4943d9f3422d964c3ab0cc2f877d9bc4c2d9e20237",
}
for name, expected in PINS.items():
    if hashlib.sha256((INPUTS / name).read_bytes()).hexdigest() != expected:
        raise ValueError("frozen controller dependency hash: " + name)
sys.path.insert(0, str(INPUTS))
from controller_reference import Builder, Machine, Tape, BLANK, ONE, MARK
from selected_control import compile_selected

WIDTH, CHILD, STACK, CUTOFF, HEADER, TRACE, LENGTH, D, ACC, FACTOR, PRODUCT = range(11)
SELECTED_Q = 100000000000000
NEW_BANKS = (CUTOFF, TRACE, LENGTH, D, ACC, FACTOR, PRODUCT)


def fresh(a, stem):
    a.serial += 1
    return stem + str(a.serial)


def clear(a, tape):
    """Erase one marked unary stream and return its head; initial head at start."""
    k = fresh(a, "clear")
    a.mark(k)
    a.op("read", tape, {ONE: k + "bit", BLANK: k + "done"})
    a.mark(k + "bit")
    a.op("write", tape, BLANK)
    a.op("move", tape, 1)
    a.op("goto", k)
    a.mark(k + "done")
    a.rewind(tape, (BLANK,))


def copy_unary(a, source, target, *, erase=False, repeat=1, extra=0):
    """Emit repeat copies per input symbol and extra ones, all fixed constants."""
    k = fresh(a, "copy")
    a.mark(k)
    a.op("read", source, {ONE: k + "bit", BLANK: k + "done"})
    a.mark(k + "bit")
    for _ in range(repeat):
        a.op("write", target, ONE)
        a.op("move", target, 1)
    if erase:
        a.op("write", source, BLANK)
    a.op("move", source, 1)
    a.op("goto", k)
    a.mark(k + "done")
    for _ in range(extra):
        a.op("write", target, ONE)
        a.op("move", target, 1)
    a.rewind(source, (BLANK,) if erase else (ONE,))
    a.rewind(target, (ONE,))


def header_step(a):
    """One borrowed-header right move, logged locally for exact restoration."""
    a.op("write", TRACE, ONE)
    a.op("move", TRACE, 1)
    a.op("move", HEADER, 1)


def decode_header(a):
    """Skip Gamma(p), decode Gamma(d) to unary D, then restore HEADER."""
    a.mark("p_scan")
    a.op("read", HEADER, {"0": "p_zero", ONE: "p_one"})
    a.mark("p_zero")
    a.op("write", LENGTH, ONE)
    a.op("move", LENGTH, 1)
    header_step(a)
    a.op("goto", "p_scan")
    a.mark("p_one")
    header_step(a)
    a.op("move", LENGTH, -1)
    a.mark("p_tail")
    a.op("read", LENGTH, {ONE: "p_tail_bit", MARK: "p_done"})
    a.mark("p_tail_bit")
    a.op("write", LENGTH, BLANK)
    a.op("read", HEADER, {"0": "p_tail_valid", ONE: "p_tail_valid"})
    a.mark("p_tail_valid")
    header_step(a)
    a.op("move", LENGTH, -1)
    a.op("goto", "p_tail")
    a.mark("p_done")
    a.op("move", LENGTH, 1)
    a.mark("d_scan")
    a.op("read", HEADER, {"0": "d_zero", ONE: "d_one"})
    a.mark("d_zero")
    a.op("write", LENGTH, ONE)
    a.op("move", LENGTH, 1)
    header_step(a)
    a.op("goto", "d_scan")
    a.mark("d_one")
    header_step(a)
    a.op("write", D, ONE)
    a.op("move", LENGTH, -1)
    a.mark("d_tail")
    a.op("read", LENGTH, {ONE: "d_tail_bit", MARK: "header_rewind"})
    a.mark("d_tail_bit")
    a.op("write", LENGTH, BLANK)
    a.op("read", HEADER, {"0": "double_zero", ONE: "double_one"})
    for bit in (0, 1):
        a.mark("double_one" if bit else "double_zero")
        copy_unary(a, D, PRODUCT, repeat=2, extra=bit)
        clear(a, D)
        copy_unary(a, PRODUCT, D, erase=True)
        header_step(a)
        a.op("move", LENGTH, -1)
        a.op("goto", "d_tail")
    a.mark("header_rewind")
    a.op("move", LENGTH, 1)
    a.op("move", TRACE, -1)
    a.mark("header_back")
    a.op("read", TRACE, {ONE: "header_back_bit", MARK: "header_back_done"})
    a.mark("header_back_bit")
    a.op("write", TRACE, BLANK)
    a.op("move", HEADER, -1)
    a.op("move", TRACE, -1)
    a.op("goto", "header_back")
    a.mark("header_back_done")
    a.op("move", TRACE, 1)


def saturated_multiply(a):
    """PRODUCT=min(ACC*FACTOR,D); positive inputs <=D; preserve all inputs."""
    k = fresh(a, "mul")
    a.mark(k)
    a.op("read", ACC, {ONE: k + "inner", BLANK: k + "done"})
    a.mark(k + "inner")
    a.op("read", D, {ONE: k + "factor", BLANK: k + "done"})
    a.mark(k + "factor")
    a.op("read", FACTOR, {ONE: k + "emit", BLANK: k + "next"})
    a.mark(k + "emit")
    a.op("write", PRODUCT, ONE)
    a.op("move", PRODUCT, 1)
    a.op("move", D, 1)
    a.op("move", FACTOR, 1)
    a.op("goto", k + "inner")
    a.mark(k + "next")
    a.rewind(FACTOR, (ONE,))
    a.op("move", ACC, 1)
    a.op("goto", k)
    a.mark(k + "done")
    for tape in (ACC, FACTOR, D, PRODUCT):
        a.rewind(tape, (ONE,))


def power_step(a, source):
    """Replace ACC by its saturated product with source (ACC or CUTOFF)."""
    copy_unary(a, source, FACTOR)
    saturated_multiply(a)
    clear(a, ACC)
    clear(a, FACTOR)
    copy_unary(a, PRODUCT, ACC, erase=True)


def compile_prefix(q=SELECTED_Q):
    if type(q) is not int or q < 2:
        raise ValueError("fixed root denominator must be an integer at least two")
    a = Builder()
    # Each private bank's guard cell is initially owned and blank.
    # Establish its delimiter physically; no supplied marker oracle is used.
    for tape in NEW_BANKS:
        a.op("move", tape, -1)
        a.op("write", tape, MARK)
        a.op("move", tape, 1)
    decode_header(a)
    a.op("write", CUTOFF, ONE)
    a.mark("cap_compare")
    a.op("read", CUTOFF, {BLANK: "within_cap", ONE: "cap_width"})
    a.mark("cap_width")
    a.op("read", WIDTH, {BLANK: "at_sentinel", ONE: "cap_step"})
    a.mark("cap_step")
    a.op("move", CUTOFF, 1)
    a.op("move", WIDTH, 1)
    a.op("goto", "cap_compare")
    a.mark("at_sentinel")
    a.rewind(CUTOFF, (ONE,))
    a.rewind(WIDTH, (ONE,))
    a.op("goto", "cutoff_ready")
    a.mark("within_cap")
    a.rewind(CUTOFF, (ONE,))
    a.rewind(WIDTH, (ONE,))
    a.op("write", ACC, ONE)
    for bit in bin(q)[2:]:
        power_step(a, ACC)
        if bit == "1":
            power_step(a, CUTOFF)
    a.mark("power_compare")
    a.op("read", D, {BLANK: "power_equal", ONE: "power_acc"})
    a.mark("power_acc")
    a.op("read", ACC, {BLANK: "power_short", ONE: "power_compare_step"})
    a.mark("power_compare_step")
    a.op("move", D, 1)
    a.op("move", ACC, 1)
    a.op("goto", "power_compare")
    a.mark("power_equal")
    a.op("read", ACC, {BLANK: "power_equal_valid"})
    a.mark("power_equal_valid")
    a.rewind(D, (ONE,))
    a.rewind(ACC, (ONE,))
    clear(a, ACC)
    a.op("goto", "cutoff_ready")
    a.mark("power_short")
    a.rewind(D, (ONE,))
    a.rewind(ACC, (ONE,))
    clear(a, ACC)
    a.mark("increment_trial")
    a.op("read", CUTOFF, {ONE: "increment_scan", BLANK: "increment_end"})
    a.mark("increment_scan")
    a.op("move", CUTOFF, 1)
    a.op("goto", "increment_trial")
    a.mark("increment_end")
    a.op("write", CUTOFF, ONE)
    a.op("move", CUTOFF, 1)
    a.rewind(CUTOFF, (ONE,))
    a.op("goto", "cap_compare")
    a.mark("cutoff_ready")
    clear(a, D)
    for tape in NEW_BANKS[1:]:
        a.op("move", tape, -1)
        a.op("write", tape, BLANK)
        a.op("move", tape, 1)
    a.op("emit", "READY")
    a.op("halt")
    return a.finish((BLANK, "0", ONE, MARK))


def relocate(code, offset, halt_target=None):
    result = []
    for ins in code:
        if ins[0] == "goto":
            result.append(("goto", offset + ins[1]))
        elif ins[0] == "read":
            result.append(("read", ins[1], {s: offset + pc for s, pc in ins[2].items()}))
        elif ins[0] == "halt" and halt_target is not None:
            result.append(("goto", halt_target))
        else:
            result.append(ins)
    return tuple(result)


def compile_joined(n, sites, q=SELECTED_Q):
    prefix, _ = compile_prefix(q)
    selected, alphabet = compile_selected(n, sites)
    a = Builder()
    clear(a, CUTOFF)
    a.op("move", CUTOFF, -1)
    a.op("write", CUTOFF, BLANK)
    a.op("move", CUTOFF, 1)
    a.op("emit", "RETIRED")
    a.op("halt")
    cleanup, _ = a.finish(alphabet)
    core_at = len(prefix)
    cleanup_at = core_at + len(selected)
    if sum(ins[0] == "halt" for ins in prefix) != 1 or sum(ins[0] == "halt" for ins in selected) != 1:
        raise ValueError("single completed-call link required")
    code = (relocate(prefix, 0, core_at) +
            relocate(selected, core_at, cleanup_at) +
            relocate(cleanup, cleanup_at))
    return code, alphabet, {"prefix": core_at, "selected": len(selected),
                            "cleanup": len(cleanup), "cleanup_at": cleanup_at,
                            "power_stages": q.bit_length() + q.bit_count()}


def gamma(value):
    """Verifier input encoding; never called by Machine.step."""
    if type(value) is not int or value < 1:
        raise ValueError("positive Gamma input")
    bits = bin(value)[2:]
    return "0" * (len(bits) - 1) + bits


def initial(p, d, e, origins=None, ancestors=None, tail=None):
    """Build a finite input fixture, outside the literal machine execution."""
    if type(e) is not int or not 1 <= e <= d:
        raise ValueError("positive active width at most global d")
    origins = (0,) * 11 if origins is None else tuple(origins)
    if len(origins) != 11:
        raise ValueError("eleven tape origins")
    if ancestors is None:
        ancestors = ("1", "0", "t0", MARK, BLANK, "1")
    if tail is None:
        tail = "".join(gamma(v) for v in (1, e, 1, 1, 1, 1, max(p + 2, 3)))
    text = gamma(p) + gamma(d) + tail
    tapes = []
    for j, origin in enumerate(origins):
        cells = {} if j in NEW_BANKS else {origin - 1: MARK}
        cells.update({origin - 2 - k: s for k, s in enumerate(ancestors) if s != BLANK})
        if j == WIDTH:
            cells.update({origin + k: ONE for k in range(e)})
        elif j == HEADER:
            cells.update({origin + k: s for k, s in enumerate(text)})
        tapes.append(Tape(cells, origin))
    return tapes
