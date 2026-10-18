#!/usr/bin/env python3
"""Native binding of PR2995's F0 dirty-helper fault. Exact and read-only.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import tarfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# Compile current local source directly; default-import bytecode is not used.
N = types.ModuleType("native_vectors")
exec(compile((HERE / "native.py").read_bytes(), str(HERE / "native.py"), "exec"), N.__dict__)
need = N.need
FAULT = 24438
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/CLIFFORD-RECIPES.json": "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731",
    "slots/local/RESIDUAL-ADAPTERS.json": "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c",
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(root):
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for entry in sources["files"]:
        if entry["usage"] == "input":
            need(hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                 "source pin: " + entry["path"])
    objects = []
    with tarfile.open(root / "research/community-frontier1042-audit/selected-replay.tar.gz") as archive:
        for name, expected in MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), "unique regular source member")
            raw = archive.extractfile(matches[0]).read()
            need(hashlib.sha256(raw).hexdigest() == expected, "source member pin: " + name)
            objects.append(json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw))
    packet = json.loads(gzip.decompress((root / "research/joint-query/certificate.json.gz").read_bytes()))
    return packet, *objects


def expand(packet):
    need(packet["schema"] == "conserved-qq16-full-cover-native-words-v1", "packet schema")
    result = []
    for event in packet["programs"]["F_0"]:
        if event[0] == "retained_core":
            need(event[1:3] == ["forward", 0], "stage-zero forward core")
            result.extend(packet["core_words"]["forward"])
        elif event[0] in ("cover_sweep", "private_sweep"):
            result.extend(event[2])
        else:
            result.append(event)
    need(len(result) == 26099 and len(packet["core_words"]["forward"]) == 25155, "event counts")
    need(Counter(e[0] for e in result) == {
        "scalar": 21025, "climb": 3486, "adapter": 1090,
        "residual_adapter": 480, "phase": 10, "native_line": 8}, "complete event inventory")
    need(result[FAULT] == ["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1],
         "fault event binding")
    return result


def reg(token):
    need(isinstance(token, list) and len(token) == 2, "register token")
    kind, index = token
    need(type(index) is int and kind in ("L", "C"), "register type")
    need(0 <= index < (704 if kind == "L" else 8), "register bounds")
    return index + 704 * (kind == "C")


def scalar(state, gate):
    kind, dst = gate[0], reg(gate[1])
    if kind == "clear":
        need(dst >= 704 and len(gate) == 2, "owned CLEAR")
        state[dst] = Q(0)
    elif kind == "scale":
        need(len(gate) == 4 and gate[2] != 0, "SCALE syntax")
        state[dst] *= Q(gate[2], gate[3])
    else:
        need(kind == "add" and len(gate) == 5, "ADD syntax")
        src = reg(gate[2])
        need(src != dst, "distinct ADD operands")
        state[dst] += Q(gate[3], gate[4]) * state[src]


def scalar_run(events, initial, inject=None, require_zero_wrappers=False):
    state, cut = list(initial), None
    for i, event in enumerate(events):
        if i == FAULT:
            cut = (state[39], state[359])
        if event[0] == "scalar":
            scalar(state, event[1])
        elif event[0] == "residual_adapter" and require_zero_wrappers:
            need(state[event[2]] == 0, "zero witness at residual boundary")
        if inject is not None and i == inject[0]:
            state[reg(event[1][1])] += inject[1]
    return state, cut


def recipes_by_key(recipes):
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    adapters = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
    need(len(children) == len(recipes["children"]) and len(adapters) == 224, "unique recipes")
    return children, adapters


def native_checks(packet, word, recipes, residuals):
    """One exact vector per frame, not a claim about every operator column."""
    children, adapters = recipes_by_key(recipes)
    events = packet["core_words"]["forward"]
    frames = [N.frame(axes) for axes in word["frames"]]
    need(frames[0] == frames[1] == N.ONE, "identity/full-frame constant")
    used = sorted({tuple(e[3:]) for e in events if e[0] == "climb"})
    for a, b, rank in used:
        child = children[a, b]
        need(child["rank"] == rank, "child rank binding")
        need(N.recipe(frames[a], child) == frames[b], "native frame-vector transition")
    for (role, port), entry in adapters.items():
        index = port + 112 * (role == "target")
        f = word["start"][index] if role == "source" else word["final"][index]
        need(entry["frame"] == f and entry["rank"] == 0 and entry["right"] is None,
             "endpoint adapter binding")
        key = N.monomial_key(entry["left"])
        need(N.mono(N.ONE, key) == frames[f], "native endpoint frame vector")
        need(N.mono(frames[f], key, True) == N.ONE, "endpoint inverse vector")
    wrapped = {i for i in range(224, 704) if (word["start"][i], word["final"][i]) != (0, 1)}
    wrapper_keys = set()
    for i in wrapped:
        a, b = word["start"][i], word["final"][i]
        key = str(a) if b == 1 else f"{a}:{b}"
        rec = residuals["recipes"][key]
        need(rec["frame"] == a and rec.get("terminal", 1) == b, "residual binding")
        N.monomial_key(rec["left"])
        N.monomial_key(rec["right"])
        wrapper_keys.add(key)
    used_lines = sorted({e[2] for e in expand(packet) if e[0] == "native_line"})
    for key in used_lines:
        entry = packet["native_line_recipes"][key]
        need(entry["rank"] == entry["recipe"]["rank"] == 1, "wrapper line rank")
        need(N.recipe(N.ONE, entry["recipe"]) == N.ONE, "native wrapper fixes constant")
    # Extended boundary labels prevent treating an adapter as a harmless relabel.
    labels = [("preS", i) if i < 112 else ("preW", i) if i in wrapped
              else ("T", word["start"][i]) for i in range(704)] + [None] * 8
    conversions = Counter()
    for event in events:
        kind = event[0]
        if kind == "phase":
            continue  # control labels, not scalar rotations
        if kind == "climb":
            _, _, i, a, b, _ = event
            need(labels[i] == ("T", a), "child entry label")
            labels[i] = ("T", b)
        elif kind == "scalar":
            gate, f = event[1:]
            i = reg(gate[1])
            if gate[0] == "clear":
                need(i >= 704, "private clear label")
                labels[i] = ("T", f)
            else:
                need(labels[i] == ("T", f), "scalar target frame")
                if gate[0] == "add":
                    need(labels[reg(gate[2])] == ("T", f), "scalar source frame")
        elif kind == "adapter":
            _, direction, i, f = event
            conversions[direction, i] += 1
            if direction == "old_to_new":
                need(f == word["start"][i], "entry frame binding")
                need(labels[i] == (("preS", i) if i < 112 else ("T", 0)), "entry label")
                labels[i] = ("T", f)
            else:
                need(direction == "new_to_old" and f == word["final"][i], "exit frame binding")
                need(labels[i] == ("T", f), "exit label")
                if 112 <= i < 224:
                    labels[i] = ("postT", i)
                else:
                    need(f == 1, "identity exit frame")
        elif kind == "residual_adapter":
            direction, i, a = event[1:4]
            b = event[4] if len(event) == 5 else 1
            need(i in wrapped and (a, b) == (word["start"][i], word["final"][i]),
                 "residual event binding")
            conversions[direction, i] += 1
            if direction == "pre":
                need(labels[i] == ("preW", i), "residual entry label")
                labels[i] = ("T", a)
            else:
                need(direction == "post" and labels[i] == ("T", b), "residual exit label")
                labels[i] = ("doneW", i)
        else:
            raise ValueError("unknown core event")
    expected = Counter()
    for i in range(704):
        if i in wrapped:
            expected["pre", i] = expected["post", i] = 1
        else:
            expected["old_to_new", i] = 1
        if i < 224 or word["final"][i] == 1:
            expected["new_to_old", i] = 1
        end = ("T", 1) if i < 112 or (i >= 224 and i not in wrapped) else (
            ("postT", i) if i < 224 else ("doneW", i))
        need(labels[i] == end, "complete native endpoint label")
    need(conversions == expected and labels[704:] == [("T", 0)] * 8, "complete conversion multiplicity")
    need((word["start"][359], word["final"][359]) == (0, 1), "dirty witness unwrapped")
    return {"used_child_recipes": len(used), "child_occurrences": 3486,
            "frame_vectors": len(frames), "frame_vector_sha256": digest(frames),
            "used_edges_sha256": digest(used), "data_adapters": len(adapters),
            "residual_records": len(wrapper_keys), "wrapper_lines": len(used_lines),
            "scalar_frame_checks": 20089, "local_payload_coordinates": N.DIM}


def physical_run(events, packet, recipes, residuals, initial, inject=None):
    """Literal vector execution, without frame reduction or scalar projection."""
    children, adapters = recipes_by_key(recipes)
    state = [N.scaled(N.ONE, x) for x in initial]
    cut = None
    for index, event in enumerate(events):
        if index == FAULT:
            cut = state[39], state[359]
        kind = event[0]
        if kind == "scalar":
            gate = event[1]
            dst = reg(gate[1])
            if gate[0] == "clear":
                state[dst] = N.ZERO
            elif gate[0] == "scale":
                state[dst] = N.scaled(state[dst], Q(gate[2], gate[3]))
            else:
                need(gate[0] == "add", "physical scalar kind")
                state[dst] = N.plus(state[dst], N.scaled(state[reg(gate[2])], Q(gate[3], gate[4])))
        elif kind == "climb":
            _, _, dst, old, new, _ = event
            if state[dst] != N.ZERO:
                state[dst] = N.recipe(state[dst], children[old, new])
        elif kind == "adapter":
            _, direction, dst, _ = event
            if direction == "old_to_new" and dst < 112:
                state[dst] = N.mono(state[dst], N.monomial_key(adapters["source", dst]["left"]))
            elif direction == "new_to_old" and 112 <= dst < 224:
                state[dst] = N.mono(state[dst], N.monomial_key(adapters["target", dst-112]["left"]), True)
        elif kind == "residual_adapter":
            direction, dst, a = event[1:4]
            b = event[4] if len(event) == 5 else 1
            key = str(a) if b == 1 else f"{a}:{b}"
            part = "right" if direction == "pre" else "left"
            state[dst] = N.mono(state[dst], N.monomial_key(residuals["recipes"][key][part]), True)
        elif kind == "native_line":
            dst = reg(event[1])
            state[dst] = N.recipe(state[dst], packet["native_line_recipes"][event[2]]["recipe"])
        else:
            need(kind == "phase", "unknown physical event")
        if inject is not None and index == inject[0]:
            state[reg(event[1][1])] = N.plus(state[reg(event[1][1])], N.scaled(N.ONE, inject[1]))
    return state, cut


def witness(events):
    unit = lambda i: [Q(j == i) for j in range(712)]
    dirty, data = unit(359), unit(112)
    out_dirty, cut_dirty = scalar_run(events, dirty, require_zero_wrappers=True)
    out_data, cut_data = scalar_run(events, data, require_zero_wrappers=True)
    need(out_dirty == dirty and out_data == data, "ideal witness endpoints")
    need(cut_dirty == (-4, 1) and cut_data == (0, 0), "marked cut coefficients")
    response, _ = scalar_run(events, [Q(0)] * 712, (FAULT, Q(1)), require_zero_wrappers=True)
    need(sum(bool(x) for x in response) == 52 and not any(response[224:]), "fault support/restoration")
    need(set(abs(x) for x in response if x) == {Q(1, 2)} and response[2] == -Q(1, 2), "fault magnitude")
    return response


def audit(root):
    packet, word, recipes, residuals = load(root)
    events = expand(packet)
    bindings = native_checks(packet, word, recipes, residuals)
    response = witness(events)
    # The quantified theorem uses the frame identities, not extrapolation in T/u.
    initial = [Q(0)] * 712
    initial[112], initial[359] = Q(1), Q(256)
    u = Q(1, 2**20)
    eta = 8 * u * initial[359]
    expected = [x + eta*r for x, r in zip(initial, response)]
    physical, cut = physical_run(events, packet, recipes, residuals, initial, (FAULT, eta))
    need(cut == (N.scaled(N.ONE, Q(-1024)), N.scaled(N.ONE, Q(256))), "literal physical cut")
    need(physical == [N.scaled(N.ONE, x) for x in expected], "literal complete native witness")
    return {"schema_version": 1, "status": "PASS_QQ16_NATIVE_DIRTY_FAULT",
            "scope": "exact local native F0 and tensor/owner lift under retained access contract",
            "expanded_events": len(events), "event_sha256": digest(events),
            "native_binding": bindings, "fault_index": FAULT,
            "unit_fault_response": [[i, str(x)] for i, x in enumerate(response) if x],
            "dirty_register": 359, "original_data_register": 112,
            "zero_residual_boundary_checks": 3*480,
            "data_error": "4*u*T", "all_480_physical_helpers_restore_on_witness": True,
            "all_8_private_outputs_zero": True, "local_relative_allowance": "8*u*T",
            "literal_check": {"T": "256", "u": str(u), "eta": str(eta),
                              "max_data_error": str(4*u*256), "coordinates": 712*N.DIM},
            "meaning": "permissive completed-ADD fault, not a concrete rounding failure"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", type=Path, help="create an absent receipt")
    args = parser.parse_args()
    result = audit(args.root.resolve())
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(json.loads((HERE / "RESULT.json").read_text()) == result, "result receipt mismatch")
    print(result["status"])
    print("2880 native transitions; 26099 literal events; 364544 endpoint amplitudes.")


if __name__ == "__main__":
    main()
