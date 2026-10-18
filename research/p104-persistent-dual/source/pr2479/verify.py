#!/usr/bin/env python3
"""Source-bound finite inverse-transpose using explicit private accumulators.

Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
No producer/compiler is imported. Default replay is read-only.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BASE = "research/p104-native-channel/"
INPUTS = {BASE+x for x in ("inputs/LOWRANK-WITNESS.json", "inputs/P104-FIXTURE.json",
                           "NATIVE-RECIPES.json.gz", "check_native.py", "vendor/native_verify.py")}


class Invalid(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Invalid(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def unique(pairs):
    out = {}
    for k, v in pairs:
        need(k not in out, "duplicate JSON key")
        out[k] = v
    return out


def read(path):
    return json.loads(path.read_text(encoding="utf8"), object_pairs_hook=unique)


def load():
    pins = {x["path"]: x["sha256"] for x in read(HERE/"SOURCES.json")["files"] if x["usage"] == "input"}
    need(set(pins) == INPUTS, "source inventory")
    for path, digest in pins.items():
        need(sha256((ROOT/path).read_bytes()).hexdigest() == digest, "source hash: " + path)
    # All executable inputs are authenticated before either interpreter imports.
    spec = importlib.util.spec_from_file_location("p104_retained_native_checker", ROOT/BASE/"check_native.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    word = read(ROOT/BASE/"inputs/LOWRANK-WITNESS.json")
    fixture = read(ROOT/BASE/"inputs/P104-FIXTURE.json")["section4_explicit_P104"]
    cert = json.loads(gzip.decompress((ROOT/BASE/"NATIVE-RECIPES.json.gz").read_bytes()), object_pairs_hook=unique)
    need(cert["source_witness_sha256"] == pins[BASE+"inputs/LOWRANK-WITNESS.json"], "certificate witness binding")
    need(cert["source_native_checker_sha256"] == pins[BASE+"vendor/native_verify.py"], "certificate interpreter binding")
    return checker, word, fixture, cert, pins


def span(vectors):
    values = {0}
    for v in vectors:
        need(type(v) is int and 0 <= v < 512, "binary generator")
        values |= {w ^ v for w in tuple(values)}
    return tuple(sorted(values))


def conjugate(circuit):
    out = []
    for gate in circuit:
        if gate[0] == "C":
            out.append(("C", gate[1], -gate[2]))
        elif gate[0] == "D":
            out.append(("D", gate[1], tuple(-x % 4 for x in gate[2])))
        elif gate[0] == "phase":
            out.append(("phase", -gate[1] % 4))
        else:
            need(gate[0] in ("P", "X"), "conjugation gate")
            out.append(gate)
    return tuple(out)


def transpose(circuit, native):
    # Ordinary transpose, with no complex conjugation of diagonal entries.
    out = []
    for gate in reversed(circuit):
        if gate[0] == "P":
            out.append(("P", native.inverse(gate[1])))
        else:
            need(gate[0] in ("C", "D", "X", "phase"), "transpose gate")
            out.append(gate)
    return tuple(out)


def native_dual(record, mode, native):
    """Exactly one positive child of the inherited rank, or a monomial."""
    rank = record["rank"]
    left = native.monomial(record["left"])
    if rank == 0:
        need(mode == "conjugate", "unexpected rank-zero private transpose")
        return conjugate(left)
    right = native.monomial(record["right"])
    if mode == "conjugate":
        # conjugate(F_r)=F_r^-1=X_(2^r-1) F_r. The X is monomial.
        return conjugate(right) + (("X", (1 << rank)-1),) + native.fourier(rank) + conjugate(left)
    need(mode == "transpose", "native dual mode")
    return transpose(left, native) + native.fourier(rank) + transpose(right, native)


def build(word):
    """Replace precisely eight uninterrupted fanout intervals by their duals."""
    original = word["program"]
    program, binding, macros = [], [], []
    i = 0
    while i < len(original):
        event = original[i]
        op = event[0]
        if op == "zero":
            start = i
            need(event[1] == "C" and i+3 < len(original), "private macro allocation")
            copy, move = original[i+1], original[i+2]
            need(copy[:2] == ["copy", "C"] and copy[2] == f"Q{len(macros)}"
                 and span(copy[3]) == span(event[2]), "private macro copy")
            need(move[:2] == ["transport", "C"] and span(move[2]) == span(event[2])
                 and len(span(move[2])) == 256 and len(span(move[3])) == 2 and move[4] == 7,
                 "private macro descent")
            cap, line, query = event[2], move[3], copy[2]
            fanout = []
            i += 3
            while i < len(original) and original[i][0] == "add":
                add = original[i]
                need(add[1].startswith("D") and add[2] == "C" and add[3] == 1
                     and span(add[4]) == span(line), "private macro fanout")
                fanout.append(add[1])
                i += 1
            need(3 <= len(fanout) <= 5 and len(set(fanout)) == len(fanout), "private macro fanout inventory")
            need(i < len(original) and original[i][:2] == ["erase", "C"]
                 and span(original[i][2]) == span(line), "uninterrupted private macro")
            begin = len(program)
            program.append(["zero", "C", line])
            program.extend(["add", "C", d, 1, line] for d in fanout)
            transport_index = len(program)
            program.extend([["transport", "C", line, cap, 7],
                            ["add", query, "C", -1, cap], ["erase", "C", cap]])
            binding.append({"dual_event": transport_index, "original_event": start+2, "mode": "transpose"})
            macros.append({"original_interval": [start, i], "dual_interval": [begin, len(program)-1],
                           "query": query, "readers": fanout, "line": line, "cap": cap})
        elif op == "add":
            _, dst, src, a, frame = event
            program.append(["add", src, dst, str(-F(a)), frame])
        else:
            need(op == "transport" and event[1] != "C", "unrecognized event outside private macro")
            binding.append({"dual_event": len(program), "original_event": i, "mode": "conjugate"})
            program.append(deepcopy(event))
        i += 1
    need(len(macros) == 8 and len(program) == len(original) == 4058, "dual event inventory")
    return {"schema_version": 1, "initial_frames": word["initial_frames"], "final_frames": word["final_frames"],
            "program": program, "native_bindings": binding, "private_macros": macros,
            "chart_contract": "Gamma_V^(-T); explicit owned zero-accumulator allocation and nonzero discard"}


def add_row(dst, src, a):
    for k, v in tuple(src.items()):
        v = dst.get(k, F(0)) + a*v
        if v:
            dst[k] = v
        else:
            dst.pop(k, None)


def expected_rows(word, ports, dual):
    expected = {r: {r: F(1)} for r in word["initial_frames"]}
    for t in range(104):
        for s in range(104):
            a = F(sum(x*y for x, y in zip(ports[t], ports[s])), 8)
            if a:
                expected[f"X{s}" if dual else f"Y{t}"][f"Y{t}" if dual else f"X{s}"] = -a if dual else a
    return expected


def replay(program, initial, final):
    values = {r: {r: F(1)} for r in initial}
    frames = {r: span(v) for r, v in initial.items()}
    operations, rank_profile, discarded = Counter(), Counter(), []
    private = False
    for index, event in enumerate(program):
        op = event[0]
        operations[op] += 1
        if op == "zero":
            _, r, frame = event
            need(r == "C" and r not in frames and not private, "owned zero allocation")
            private = True
            values[r], frames[r] = {}, span(frame)
        elif op == "erase":
            _, r, frame = event
            need(r == "C" and private and frames[r] == span(frame), "owned accumulator discard")
            discarded.append({"event": index, "frame": frame,
                              "row": {k: str(v) for k, v in sorted(values[r].items())}})
            del values[r], frames[r]
            private = False
        elif op == "transport":
            _, r, old, new, rank = event
            a, b = span(old), span(new)
            need(r in frames and frames[r] == a and (set(a) < set(b) or set(b) < set(a)), "literal transport frame")
            need(type(rank) is int and rank == abs(len(a).bit_length()-len(b).bit_length()), "native rank")
            frames[r] = b
            rank_profile[rank] += 1
        elif op == "copy":
            _, r, src, frame = event
            need(not values[r] and frames[r] == frames[src] == span(frame), "known-zero COPY")
            values[r] = dict(values[src])
        else:
            need(op == "add", "scalar event")
            _, dst, src, a, frame = event
            need(dst != src and frames[dst] == frames[src] == span(frame), "common scalar chart")
            add_row(values[dst], values[src], F(a))
    need(not private and frames == {r: span(v) for r, v in final.items()}, "final private/frame boundary")
    return values, dict(sorted(operations.items())), {str(k): v for k, v in sorted(rank_profile.items())}, discarded


def native_check(checker, word, cert, dual):
    native = checker.N
    iso = cert["label_isometry"]
    dual_gram = iso["compressed_dual_gram"]
    orth = iso["orthonormal_basis_compressed"]
    def convert(x):
        return sum(((x & native.mul(tuple(dual_gram), b)).bit_count() % 2) << j for j, b in enumerate(orth))
    def key(raw):
        return span(convert(x) for x in raw)
    source_events = {}
    checked, converted_recipes = {}, []
    by_dual_event = {b["dual_event"]: b for b in dual["native_bindings"]}
    need(len(by_dual_event) == 1410, "native binding uniqueness")
    for record in cert["transports"]:
        for event in record["events"]:
            need(event not in source_events, "original native event uniqueness")
            source_events[event] = record
    private_columns = 0
    for index, event in enumerate(dual["program"]):
        if event[0] != "transport":
            need(index not in by_dual_event, "native binding on nontransport")
            continue
        binding = by_dual_event[index]
        source = binding["original_event"]
        record = source_events[source]
        original = word["program"][source]
        mode = binding["mode"]
        need(original[0] == "transport" and event[1] == original[1], "native occurrence register")
        old, new = (record["old"], record["new"]) if mode == "conjugate" else (record["new"], record["old"])
        need(key(event[2]) == span(old) and key(event[3]) == span(new)
             and event[4] == original[4] == record["rank"], "native occurrence frames/rank")
        ident = (tuple(record["old"]), tuple(record["new"]), mode)
        if ident not in checked:
            actual = native_dual(record["recipe"], mode, native)
            expected = native.adjoint(conjugate(native.frame(tuple(old), 9))) + conjugate(native.frame(tuple(new), 9))
            need(sum(g[0] == "C" for g in actual) == record["rank"]
                 and all(g[2] == 1 for g in actual if g[0] == "C"), "one positive child rank")
            native.equal(actual, expected, "complete native dual edge")
            checked[ident] = (actual, expected)
            converted_recipes.append([list(record["old"]), list(record["new"]), mode, actual])
            if mode == "transpose":
                for basis in range(512):
                    need(native.state(actual, basis) == native.state(expected, basis), "private transpose Gaussian column")
                    private_columns += 1
    need(set(by_dual_event) == {i for i, e in enumerate(dual["program"]) if e[0] == "transport"}, "all dual occurrences")
    for adapter in cert["endpoint_adapters"]:
        actual = native_dual(adapter["recipe"], "conjugate", native)
        expected = conjugate(native.recipe(adapter["recipe"]))
        need(not any(g[0] == "C" for g in actual), "dual endpoint adapter monomial")
        native.equal(actual, expected, "dual intrinsic endpoint adapter")
    return {"distinct_dual_edges": len(checked), "occurrences": 1410, "intrinsic_adapters": 208,
            "private_gaussian_columns": private_columns,
            "derived_recipe_sha256": sha256(canonical(converted_recipes).encode()).hexdigest()}, checked


def controls(checker, word, cert, dual, expected, discarded, checked):
    native = checker.N
    passed = []
    # The tempting atomwise inverse-transpose does not dualize rectangular boundaries.
    naive = []
    for event in word["program"]:
        if event[0] == "add":
            naive.append(["add", event[2], event[1], str(-F(event[3])), event[4]])
        elif event[0] == "copy":
            naive.append(["add", event[2], event[1], -1, event[3]])
        else:
            naive.append(deepcopy(event))
    values, _, _, _ = replay(naive, word["initial_frames"], word["final_frames"])
    need(values["X0"].get("D0") == -2 and values["X0"].get("Y0", 0) == 0
         and expected["X0"]["Y0"] == -1 and values["Q0"].get("D0") == 1,
         "naive boundary fault witness")
    passed.append("atomwise dual loses private boundary and fails dirty/input identities")
    bad = deepcopy(dual["program"])
    macro = dual["private_macros"][0]
    bad[macro["dual_interval"][1]-1][3] = 1
    values, _, _, _ = replay(bad, dual["initial_frames"], dual["final_frames"])
    need(values != expected, "wrong gather sign accepted")
    passed.append("wrong private gather sign rejected by full columns")
    bad = deepcopy(dual["program"])
    # All D readers are required; removing one must not be hidden by final dirt.
    bad[macro["dual_interval"][0]+1][3] = 0
    values, _, _, _ = replay(bad, dual["initial_frames"], dual["final_frames"])
    need(values != expected, "missing private reader accepted")
    passed.append("missing private gather reader rejected by full columns")
    actual, exp = next(iter(checked.values()))
    phased = actual + (("phase", 1),)
    need(native.tableau(phased) == native.tableau(actual) and native.state(phased) != native.state(exp), "phase fault not detected")
    passed.append("global phase-only native fault detected")
    private_key = next(k for k in checked if k[2] == "transpose")
    original = next(r for r in cert["transports"]
                    if tuple(r["old"]) == private_key[0] and tuple(r["new"]) == private_key[1])
    wrong = native.adjoint(native.recipe(original["recipe"]))
    _, exp = checked[private_key]
    need(native.tableau(wrong) != native.tableau(exp) or native.state(wrong) != native.state(exp), "adjoint confused with transpose")
    passed.append("private adjoint substitution fails ordinary transpose")
    # The private end is generally nonzero; this is an explicit accumulator contract.
    need(len(discarded) == 8 and all(any(k.startswith("D") and F(v) for k, v in row["row"].items())
                                   for row in discarded), "nonzero private discard witness")
    passed.append("all eight discarded accumulators contain independent D dirt")
    # Equivalent basis order is a positive check on frame equality, not array order.
    permuted = deepcopy(dual["program"])
    for event in permuted:
        positions = (2, 3) if event[0] == "transport" else ((4,) if event[0] == "add" else (2,))
        for p in positions:
            event[p] = list(reversed(event[p]))
    values, _, _, _ = replay(permuted, dual["initial_frames"], dual["final_frames"])
    need(values == expected, "frame basis permutation")
    passed.append("equivalent binary frame bases preserve logical word")
    return passed


def compute():
    checker, word, fixture, cert, pins = load()
    retained = checker.validate(cert, word, fixture, False)
    ports = [r for r in checker.roots() if r not in {tuple(v) for v in fixture["F0"]+fixture["C"]}]
    need(len(ports) == 104, "port count")
    dual = build(word)
    values, operations, profile, discarded = replay(dual["program"], dual["initial_frames"], dual["final_frames"])
    expected = expected_rows(word, ports, True)
    need(values == expected, "full dual endpoint")
    need(operations == {"add": 2632, "erase": 8, "transport": 1410, "zero": 8}, "dual operation invoice")
    need(profile == {str(k): v for k, v in retained["paid_profile"].items()}, "dual native profile")
    native_result, checked = native_check(checker, word, cert, dual)
    checks = controls(checker, word, cert, dual, expected, discarded, checked)
    receipt = {"schema_version": 1, "claim": "finite public ordinary inverse-transpose under explicit owned accumulator semantics",
               "sources": pins, "events": len(dual["program"]), "inputs": len(values), "operations": operations,
               "rank_profile": profile, "rank_mass": sum(int(k)*v for k, v in profile.items()),
               "word_sha256": sha256(canonical(dual).encode()).hexdigest(),
               "endpoint_rows_sha256": sha256(canonical({r: {k: str(v) for k, v in sorted(row.items())}
                                                          for r, row in sorted(values.items())}).encode()).hexdigest(),
               "native": native_result, "private_discards": discarded, "controls": checks,
               "limits": "no inherited pure-copy contract, physical scalar lowering, side correction, global supplier, precision or new kappa"}
    return receipt, dual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result, dual = compute()
    need(canonical(result) == canonical(read(HERE/"RESULT.json")), "receipt mismatch")
    need(canonical(dual) == canonical(read(HERE/"WORD.json")), "complete dual word mismatch")
    if args.out:
        with args.out.open("x", encoding="utf8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print(f"PASS_P104_PRIVATE_MACRO_DUAL inputs=280 private=8 native=1410 rank_mass=2368 controls={len(result['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
