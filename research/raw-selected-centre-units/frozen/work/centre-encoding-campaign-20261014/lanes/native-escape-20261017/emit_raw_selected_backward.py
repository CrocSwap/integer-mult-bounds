"""Check a raw selected exchange with explicit line operators."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parent
REPO = LANES.parents[2]
A = [0, 7, 20, 27, 36, 46, 57, 111]
PINS = {
    "core": "fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877",
    "word": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "interface": "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
    "uniform": "17122a343fb8a3dd804b2d7042d523aa209d0684447cdba63d84cc5561b6144f",
}


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def read(path, pin, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Source pin: " + str(path))
    return json.loads(raw)


def plus(dst, src, coefficient=F(1)):
    for key, value in src.items():
        value = dst.get(key, F(0)) + coefficient * value
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def line(row, port, power):
    """Apply one ordered operator. Cancel only adjacent inverse pairs."""
    out = {}
    for (source, word), value in row.items():
        if word and word[0] == (port, -power):
            new = word[1:]
        else:
            new = ((port, power),) + word
        plus(out, {(source, new): value})
    return out


def slot(wire):
    need(wire[0] in ("L", "C"), "Core namespace")
    return wire[1] + (704 if wire[0] == "C" else 0)


def core_replay(events, initial, word):
    state = deepcopy(initial)
    frames = word["start"][:] + [None] * 8
    for event in events:
        kind = event[0]
        if kind == "scalar":
            gate, frame = event[1:]
            op, dst = gate[0], slot(gate[1])
            if op == "clear":
                need(dst >= 704, "Owned clear")
                state[dst], frames[dst] = {}, frame
            else:
                need(frames[dst] == frame, "Core scalar target frame")
                if op == "scale":
                    c = F(*gate[2:4])
                    state[dst] = {key: c * value for key, value in state[dst].items() if c * value}
                else:
                    need(op == "add", "Core ADD")
                    src = slot(gate[2])
                    need(frames[src] == frame, "Core scalar source frame")
                    plus(state[dst], state[src], F(*gate[3:5]))
        elif kind == "climb":
            dst, old, new = event[2:5]
            need(frames[dst] == old, "Core child input frame")
            frames[dst] = new
        else:
            need(kind in ("phase", "adapter", "residual_adapter"), "Retained event")
    need(frames == word["final"] + [0] * 8, "Retained core final frames")
    return state


def boundary(events, state):
    state = deepcopy(state)
    for e in events:
        kind, dst = e["kind"], e["target"]
        if kind == "clear":
            need(dst == 704, "Only C0 is cleared")
            state[dst] = {}
        elif kind == "copy":
            need(dst == 704 and not state[dst], "Owned copy")
            state[dst] = dict(state[e["source"]])
        elif kind == "line":
            need(dst == 704 and e["port"] in A, "Serial selected line")
            state[dst] = line(state[dst], e["port"], e["power"])
        elif kind == "add":
            plus(state[dst], state[e["source"]], F(e["coefficient"]))
        elif kind == "scale":
            c = F(e["coefficient"])
            state[dst] = {k: c * v for k, v in state[dst].items() if c * v}
        else:
            raise RuntimeError("Unknown boundary event")
    return state


def scalar_price(events):
    total = 0
    for e in events:
        if e["kind"] == "line":
            continue
        if e["kind"] in ("clear", "copy"):
            total += 2
            continue
        c = F(e["coefficient"])
        a, b = abs(c.numerator), c.denominator
        need(b & (b - 1) == 0, "Dyadic coefficient")
        if e["kind"] == "scale":
            need(a & (a - 1) == 0, "Power-of-two scale")
            total += 2 * (abs(a.bit_length() - b.bit_length()) + int(c < 0))
        else:
            total += 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)
    return total


def raw_scalar(kind, target, source=None, coefficient=None):
    out = dict(kind=kind, target=target)
    if source is not None:
        out["source"] = source
    if coefficient is not None:
        out["coefficient"] = str(coefficient)
    return out


def bit_map(rows, x):
    return sum(((r & x).bit_count() & 1) << j for j, r in enumerate(rows))


def check_recipes(recipes, ports):
    count = 0
    alpha, beta = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    for item in recipes:
        p, inverse, recipe = item["port"], item["inverse"], item["recipe"]
        need(p in A and recipe["rank"] == 1, "Selected rank-one recipe")
        left, right = recipe["left"], recipe["right"]
        for side in (left, right):
            need(not side["phase"] and not any(side["linear_Z4"] + side["quadratic_rows"]), "Exact wrapper phases")
        for x in range(512):
            y = bit_map(right["matrix_rows"], x) ^ right["offset"]
            actual = {bit_map(left["matrix_rows"], y) ^ left["offset"]: alpha,
                      bit_map(left["matrix_rows"], y ^ 1) ^ left["offset"]: beta}
            expected = {x: beta if inverse else alpha,
                        x ^ ports[p]: alpha if inverse else beta}
            need(actual == expected, "Signed native kernel")
            count += 1
    need(count == 8192, "All signed line basis columns")
    return count


def main():
    core = read(LANES / "circuit-interface/CENTRE-FREE-PROGRAMS.json.gz", PINS["core"], True)["backward"]
    word_raw = (REPO / "work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz").read_bytes()
    need(sha256(word_raw).hexdigest() == PINS["word"], "Canonical word pin")
    word = json.loads(gzip.decompress(word_raw))
    interface = read(LANES / "circuit-interface/INTERFACE.json", PINS["interface"])
    uniform = read(LANES / "paired-package-review/upstream-followthrough-20261015/current-query-encoder/UNIFORM-SIGNED-PROGRAMS.json.gz", PINS["uniform"], True)
    R = [{int(p): F(c) for p, c in row.items()} for row in interface["R"]]
    U = [p for p in range(112) if p not in A]
    D = {p: {a: sum(row.get(p, 0) * row.get(a, 0) for row in R) / 4 for a in A} for p in U}
    D = {p: {a: c for a, c in row.items() if c} for p, row in D.items()}
    B = {a: {p: D[p][a] for p in U if a in D[p]} for a in A}
    need(all(sum(B[a].get(p, 0) * D[p].get(b, 0) for p in U) == (13 if a == b else 0) for a in A for b in A), "BD=13I")
    prefix = []
    for a in A:
        prefix += [raw_scalar("clear", 704), raw_scalar("copy", 704, 112 + a),
                   dict(kind="line", target=704, port=a, power=-1)]
        prefix += [raw_scalar("add", 112 + p, 704, -D[p][a]) for p in U if a in D[p]]
        prefix += [raw_scalar("clear", 704)]
    exchange = []
    for a in A:
        exchange += [raw_scalar("add", a, 112 + a, 1), raw_scalar("add", 112 + a, a, -1),
                     raw_scalar("add", a, 112 + a, 1), raw_scalar("scale", 112 + a, coefficient=-1)]
    post = [raw_scalar("add", p, a, -c) for p in U for a, c in sorted(D[p].items())]
    correction = []
    for a in A:
        correction += [raw_scalar("clear", 704), raw_scalar("copy", 704, 112 + a),
                       dict(kind="line", target=704, port=a, power=1)]
        correction += [raw_scalar("add", p, 704, -D[p][a]) for p in U if a in D[p]]
        correction += [raw_scalar("clear", 704)]
    identity = [{(p, ()): F(1)} for p in range(712)]

    def evaluate(pre=prefix, swap=exchange, tail=post, fix=None):
        physical = deepcopy(identity)
        for p in range(112):
            physical[p] = line(physical[p], p, 1)
        physical = boundary(pre + swap, physical)
        logical = deepcopy(physical)
        for p in range(112):
            logical[p] = line(logical[p], p, -1)
        logical = core_replay(core, logical, word)
        # The common full F operator is removed from all data for this boundary.
        physical = deepcopy(logical)
        for p in range(112):
            physical[112 + p] = line(physical[112 + p], p, -1)
        physical = boundary(tail + (fix or []), physical)
        logical = deepcopy(physical)
        for p in range(112):
            logical[112 + p] = line(logical[112 + p], p, 1)
        return logical, physical

    expected = deepcopy(identity)
    expected[704:] = [{} for _ in range(8)]
    for a in A:
        expected[a] = line(identity[112 + a], a, -1)
        expected[a] = {key: -12 * c for key, c in expected[a].items()}
        for p, c in B[a].items():
            plus(expected[a], identity[112 + p], c)
        expected[112 + a] = line(identity[a], a, 1)
    for p in U:
        expected[p] = dict(identity[p]); plus(expected[p], identity[112 + p], -1)
        expected[112 + p] = dict(identity[112 + p])
        for a, c in D[p].items():
            plus(expected[p], line(identity[a], a, 1), c)
            plus(expected[112 + p], line(identity[112 + a], a, -1), -c)
    actual, physical = evaluate()
    need(actual == expected, "All 712 noncommutative operator columns")
    need(all(physical[112 + a] == identity[a] for a in A), "Physical selected Y=F original selected X")
    need(actual[224:704] == identity[224:704] and actual[704:] == [{}] * 8, "Arbitrary helper and owned-private contract")
    corrected = deepcopy(expected)
    for p in U:
        corrected[p] = dict(identity[p]); plus(corrected[p], identity[112 + p], -1)
    actual_corrected, _ = evaluate(fix=correction)
    need(actual_corrected == corrected, "Optional eight-line ordinary correction")
    for a in A:
        recovered = dict(expected[a])
        for p, c in B[a].items():
            plus(recovered, expected[112 + p], -c)
        need(line(recovered, a, 1) == identity[112 + a], "Selected original Y inverse")
    for p in U:
        recovered = dict(expected[112 + p])
        for a, c in D[p].items():
            r = dict(expected[a])
            for q, b in B[a].items():
                plus(r, expected[112 + q], -b)
            plus(recovered, r, c)
        need(recovered == identity[112 + p], "Ordinary original Y inverse")
    wrong_line = deepcopy(prefix)
    for e in wrong_line:
        if e["kind"] == "line":
            e["power"] = 1
    controls = {
        "omit_prefix": evaluate(pre=[])[0] != expected,
        "wrong_inverse_line": evaluate(pre=wrong_line)[0] != expected,
        "omit_physical_exchange": evaluate(swap=[])[0] != expected,
        "omit_post_lower_shear": evaluate(tail=[])[0] != expected,
        "omit_optional_correction": actual != corrected,
    }
    need(all(controls.values()), "Negative controls")
    priced_core = []
    for e in core:
        if e[0] != "scalar":
            continue
        g = e[1]
        if g[0] == "clear":
            priced_core.append(raw_scalar("clear", slot(g[1])))
        elif g[0] == "scale":
            priced_core.append(raw_scalar("scale", slot(g[1]), coefficient=F(*g[2:4])))
        else:
            need(g[0] == "add", "Priced core ADD")
            priced_core.append(raw_scalar("add", slot(g[1]), slot(g[2]), F(*g[3:5])))
    base_scalar = scalar_price(priced_core)
    need(base_scalar == 202138, "Independent core scalar invoice")
    profile = Counter(e[5] for e in core if e[0] == "climb")
    need(sum(k * v for k, v in profile.items()) == 5522, "Inherited native profile")
    scalar = base_scalar + scalar_price(prefix + exchange + post)
    scalar_corrected = scalar + scalar_price(correction)
    columns = check_recipes(uniform["line_recipes"], word["ports"])
    payload = dict(schema="raw-selected-backward-local-v1", source_pins=PINS, selected=A,
                   prefix=prefix, physical_exchange=exchange, retained_core=core,
                   post_lower_shear=post, optional_ordinary_correction=correction,
                   line_recipes=uniform["line_recipes"],
                   boundary_rule="ADD uses common physical addresses. It does not equate the logical native frames.")
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    (HERE / "RAW-SELECTED-BACKWARD-PROGRAM.json.gz").write_bytes(gzip.compress(encoded, mtime=0))
    receipt = dict(status="PASS_RAW_SELECTED_BACKWARD_LOCAL_OPERATOR", source_pins=PINS,
                   checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                   payload_sha256=sha256(encoded).hexdigest(), all_formal_input_columns=712,
                   arbitrary_helpers_restored=480, owned_private_zero=8,
                   exact_signed_line_columns=columns, D_nonzero_entries=sum(map(len, D.values())),
                   complete_scalar=scalar, native_mass=5530, added_native_rank_one=8,
                   complete_scalar_with_ordinary_correction=scalar_corrected,
                   native_mass_with_ordinary_correction=5538,
                   scalar_parts=dict(prefix=scalar_price(prefix), physical_exchange=scalar_price(exchange),
                                     post_lower=scalar_price(post), optional_correction=scalar_price(correction)),
                   controls=controls,
                   scope="Literal local boundary operators, all retained logical core events, exact intrinsic line kernels, arbitrary helpers, and local invoice. The complete old native core phase proof is inherited.",
                   open=["Independent review", "Actual inter-call physical views and changed controller", "New child hosting", "Complete recursive scalar, storage, and precision invoice"])
    (HERE / "RAW-SELECTED-BACKWARD.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    print(json.dumps({k: receipt[k] for k in ("complete_scalar", "native_mass", "complete_scalar_with_ordinary_correction", "native_mass_with_ordinary_correction", "exact_signed_line_columns")}, sort_keys=True))


if __name__ == "__main__":
    main()
