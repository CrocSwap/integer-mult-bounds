"""Independent exact scalar sensitivity of the pinned PR2497 clean dual.

No predecessor executable, native interpreter or compiler is imported.
Completed native calls are assumed to have the certified unitary chart action.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HOME = Path(__file__).resolve().parent
ROOT = HOME.parents[1]
EVENTS = 4982
INPUTS = 358
MAX_BYTES = 2_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_bytes(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "bounded input bytes")
    return data


def load_json(path):
    return json.loads(bounded_bytes(path))


def source_check():
    sources = load_json(HOME / "SOURCES.json")["files"]
    predecessors = load_json(HOME / "PREDECESSOR.json")["files"]
    require(len(sources) <= 16 and len(predecessors) <= 16, "bounded source pin inventory")
    for row in sources:
        if row["usage"] == "input":
            check_bytes(ROOT / row["path"], row)
    for row in predecessors:
        check_bytes(HOME / row["local"], row)


def check_bytes(path, pin):
    data = bounded_bytes(path)
    require(hashlib.sha256(data).hexdigest() == pin["sha256"], "source SHA256: " + str(path))
    blob = b"blob " + str(len(data)).encode() + b"\0" + data
    require(hashlib.sha1(blob).hexdigest() == pin["git_blob"], "source Git blob: " + str(path))


@lru_cache(maxsize=2048)
def span(frame):
    require(len(frame) <= 9 and all(type(v) is int and 0 < v < 512 for v in frame), "binary frame")
    values = {0}
    for vector in frame:
        values |= {x ^ vector for x in tuple(values)}
    require(len(values) == 1 << len(frame), "independent frame basis")
    return frozenset(values)


def add_scaled(destination, source, coefficient):
    for key, value in source.items():
        result = destination.get(key, Q(0)) + coefficient * value
        if result:
            destination[key] = result
        else:
            destination.pop(key, None)


def weights(event):
    op = event[0]
    return {"absolute": Q(1),
            "weighted": Q(1) + abs(Q(event[3])) if op == "add" else Q(1),
            "native_only": Q(op == "transport"),
            "absolute_exact_sign": Q(op != "sign"),
            "weighted_exact_sign": (Q(1) + abs(Q(event[3])) if op == "add" else Q(op != "sign"))}


def update(event, inputs, errors, frames, site):
    op, reg = event[:2]
    if op == "zero":
        require(reg == "C" and reg not in frames, "fresh private collector")
        inputs[reg], errors[reg], frames[reg] = {}, {}, span(tuple(event[2]))
    elif op == "erase":
        require(reg == "C" and frames[reg] == span(tuple(event[2])), "private erase frame")
        require(not inputs[reg], "ideal private erasure must be zero")
        del inputs[reg], errors[reg], frames[reg]
    elif op == "transport":
        old, new, rank = event[2:]
        a, b = span(tuple(old)), span(tuple(new))
        require(frames[reg] == a and (a <= b or b <= a), "nested transport entry")
        require(type(rank) is int and 0 < rank == abs(len(old) - len(new)), "paid transport rank")
        frames[reg] = b
        errors[reg][site] = Q(1)
    elif op == "add":
        src, coefficient = event[2], Q(event[3])
        require(reg != src and frames[reg] == frames[src] == span(tuple(event[4])), "common ADD chart")
        require(coefficient.denominator <= 4 and abs(coefficient) <= 2, "bounded scalar coefficient")
        add_scaled(inputs[reg], inputs[src], coefficient)
        add_scaled(errors[reg], errors[src], coefficient)
        errors[reg][site] = Q(1)
    elif op == "sign":
        require(event[2] == "-1" and frames[reg] == span(tuple(event[3])), "source sign")
        inputs[reg] = {k: -v for k, v in inputs[reg].items()}
        errors[reg] = {k: -v for k, v in errors[reg].items()}
        errors[reg][site] = Q(1)
    else:
        raise ValueError("unsupported operation")


def consider(peaks, metric, value, cut, register, row):
    if metric not in peaks or value > peaks[metric]["value"]:
        peaks[metric] = dict(value=value, cut=cut, register=register, row=dict(row))


def forward(word):
    program, initial = word["program"], word["initial_frames"]
    require(len(program) == EVENTS and len(initial) == INPUTS, "fixed word size")
    require(set(initial) == set(word["final_frames"]) and "C" not in initial, "persistent boundary")
    inputs = {r: {r: Q(1)} for r in initial}
    errors = {r: {} for r in initial}
    frames = {r: span(tuple(f)) for r, f in initial.items()}
    site_weights, peaks, erased = {}, {}, []
    private_start = None
    digest = hashlib.sha256()
    consider(peaks, "input", Q(1), 0, next(iter(initial)), inputs[next(iter(initial))])
    for index, event in enumerate(program):
        reg, op = event[1], event[0]
        if op == "zero":
            require(private_start is None, "nonoverlapping private lifetimes")
            private_start = index
        if op == "erase":
            require(private_start is not None, "live private lifetime")
            erased.append(dict(start=private_start, cut=index, input_row=dict(inputs[reg]), error_row=dict(errors[reg])))
            private_start = None
        update(event, inputs, errors, frames, index)
        if op not in ("add", "transport", "sign"):
            continue
        site_weights[index] = weights(event)
        consider(peaks, "input", sum(map(abs, inputs[reg].values())), index + 1, reg, inputs[reg])
        for metric in site_weights[index]:
            value = sum(abs(v) * site_weights[k][metric] for k, v in errors[reg].items())
            consider(peaks, metric, value, index + 1, reg, errors[reg])
        payload = [index + 1, reg, encode_row(inputs[reg]), encode_row(errors[reg])]
        digest.update(json.dumps(payload, separators=(",", ":")).encode() + b"\n")
    require(frames == {r: span(tuple(f)) for r, f in word["final_frames"].items()}, "all exit frames")
    require(private_start is None and len(erased) == 8 and len(site_weights) == 4966, "private lifetimes and defect sites")
    return inputs, errors, site_weights, peaks, erased, digest.hexdigest()


def reverse_functional(program, cut, register):
    """Reverse one output functional, independently of forward row updates."""
    require(0 <= cut <= len(program), "reverse cut range")
    adjoint, defects = {register: Q(1)}, {}
    for index in range(cut - 1, -1, -1):
        event = program[index]
        op, reg = event[:2]
        coefficient = adjoint.get(reg, Q(0))
        if op in ("add", "transport", "sign") and coefficient:
            defects[index] = coefficient
        if op == "add":
            source = event[2]
            value = adjoint.get(source, Q(0)) + Q(event[3]) * coefficient
            if value:
                adjoint[source] = value
            else:
                adjoint.pop(source, None)
        elif op == "sign" and coefficient:
            adjoint[reg] = -coefficient
        elif op in ("zero", "erase"):
            adjoint.pop(reg, None)
    return adjoint, defects


def ports():
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, sign * 2
            roots.add(tuple(root))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    fixture = load_json(ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json")["section4_explicit_P104"]
    removed = set(map(tuple, fixture["F0"] + fixture["C"]))
    require(len(roots) == 120 and len(removed) == 16 and removed <= roots, "root fixture")
    return sorted(roots - removed)


def boundary_check(inputs, errors, word):
    roots = ports()
    count = 0
    for register in word["initial_frames"]:
        expected = {register: Q(1)}
        if register.startswith("X"):
            source = int(register[1:])
            for target, root in enumerate(roots):
                value = -Q(int(target == source)) if target < 2 else -Q(sum(a*b for a, b in zip(root, roots[source])), 8)
                if value:
                    expected["Y" + str(target)] = value
        require(inputs[register] == expected, "complete inverse-transpose boundary: " + register)
        a, e = reverse_functional(word["program"], EVENTS, register)
        require(a == inputs[register] and e == errors[register], "reverse endpoint row: " + register)
        count += len(a) + len(e)
    return count


def encode_row(row):
    return [[str(k), str(v)] for k, v in sorted(row.items(), key=lambda pair: str(pair[0]))]


def scalar_execute(word, cut, register, values, defects):
    state = {r: values.get(r, Q(0)) for r in word["initial_frames"]}
    for index, event in enumerate(word["program"][:cut]):
        op, reg = event[:2]
        if op == "zero":
            state[reg] = Q(0)
        elif op == "erase":
            del state[reg]
        elif op == "add":
            state[reg] += Q(event[3]) * state[event[2]]
        elif op == "sign":
            state[reg] = -state[reg]
        if op in ("add", "transport", "sign"):
            state[reg] += defects.get(index, Q(0))
    return state if register is None else state[register]


def dense_check(word, inputs, errors, site_weights):
    values = {r: Q((i % 13) - 6, 7) for i, r in enumerate(word["initial_frames"])}
    injections = {i: Q((i % 7) + 1, 11) * (-1 if i % 2 else 1) for i in site_weights}
    state = scalar_execute(word, EVENTS, None, values, injections)
    for register in values:
        expected = sum(v*values[k] for k, v in inputs[register].items())
        expected += sum(v*injections[k] for k, v in errors[register].items())
        require(state[register] == expected, "literal dense defect endpoint: " + register)
    return len(injections)


def witness_check(word, site_weights, peaks, erased):
    for metric, peak in peaks.items():
        a, e = reverse_functional(word["program"], peak["cut"], peak["register"])
        row = a if metric == "input" else e
        require(row == peak["row"], "reverse peak row: " + metric)
        signed = {k: (Q(1) if v > 0 else Q(-1)) for k, v in row.items()}
        if metric == "input":
            actual = scalar_execute(word, peak["cut"], peak["register"], signed, {})
        else:
            injections = {k: v * site_weights[k][metric] for k, v in signed.items()}
            actual = scalar_execute(word, peak["cut"], peak["register"], {}, injections)
        require(actual == peak["value"], "literal peak attainment: " + metric)
    for row in erased:
        a, e = reverse_functional(word["program"], row["cut"], "C")
        require(a == row["input_row"] == {} and e == row["error_row"], "private residual reverse row")
        local = {i: Q(1) for i in range(row["start"], row["cut"])
                 if word["program"][i][0] in ("add", "transport") and word["program"][i][1] == "C"}
        require(e == local, "private debt is exactly the local collector update defects")
    first = erased[0]
    native_sites = [i for i in first["error_row"] if word["program"][i][0:2] == ["transport", "C"]]
    cleanup_site = max(first["error_row"])
    witnesses = []
    for site in [min(native_sites), max(native_sites), cleanup_site]:
        residual = scalar_execute(word, first["cut"], "C", {}, {site: Q(1)})
        require(residual == first["error_row"][site] == 1, "unit defect survives until erase")
        endpoint = scalar_execute(word, EVENTS, None, {}, {site: Q(1)})
        witnesses.append(dict(site=site, erase_cut=first["cut"], residual=str(residual),
                              event=word["program"][site], endpoint=encode_row({r:v for r,v in endpoint.items() if v})))
    require(scalar_execute(word, max(native_sites), "C", {"D31": Q(1)}, {}) == 1,
            "state-relative return witness has unit preinstruction norm")
    state_residual = scalar_execute(word, first["cut"], "C", {"D31": Q(1)}, {max(native_sites): Q(1, 1024)})
    require(state_residual == Q(1, 1024), "state-relative permitted return defect breaks zero erasure")
    return {"unit_impulses": witnesses,
            "state_relative_return": {"input": "D31=1, other inputs zero", "site": max(native_sites),
                                      "u": "1/1024", "preinstruction_norm": "1",
                                      "erase_cut": first["cut"], "residual": str(state_residual)}}


def report(word):
    inputs, errors, site_weights, peaks, erased, digest = forward(word)
    checked = boundary_check(inputs, errors, word)
    dense_sites = dense_check(word, inputs, errors, site_weights)
    residual = witness_check(word, site_weights, peaks, erased)
    require(all(not r["input_row"] for r in erased), "all exact private zeros")
    counts = dict(Counter(e[0] for e in word["program"]))
    profile = Counter(e[4] for e in word["program"] if e[0] == "transport")
    metrics = {m: {"value": str(p["value"]), "cut": p["cut"], "register": p["register"],
                   "row": encode_row(p["row"])} for m, p in peaks.items()}
    private = []
    for row in erased:
        private.append({"start_cut": row["start"], "erase_cut": row["cut"],
                        "native_only": str(sum(abs(v)*site_weights[k]["native_only"] for k,v in row["error_row"].items())),
                        "absolute": str(sum(map(abs, row["error_row"].values()))),
                        "weighted": str(sum(abs(v)*site_weights[k]["weighted"] for k,v in row["error_row"].items())),
                        "error_row": encode_row(row["error_row"])})
    guards = {}
    for metric in ("weighted", "weighted_exact_sign"):
        p, k = peaks["input"]["value"], peaks[metric]["value"]
        candidates = [bits for bits in range(64) if Q(2)**bits >= k*(p+1)]
        require(bool(candidates), "guard within64 bits")
        guards[metric] = {"bits": candidates[0], "P_times_K": str(p*k), "K_times_P_plus_1": str(k*(p+1))}
    return dict(status="PASS_P104_CLEAN_DUAL_PRECISION", events=EVENTS, boundary_inputs=INPUTS,
                update_sites=len(site_weights), exact_sign_sites=sum(e[0] in ("add", "transport") for e in word["program"]),
                counts=counts, positive_profile=dict(sorted(profile.items())), rank_mass=sum(r*n for r,n in profile.items()),
                peaks=metrics, private_residuals=private, residual_witness=residual,
                reverse_endpoint_nonzero_coefficients=checked, dense_nonzero_defect_sites=dense_sites,
                signed_stream_sha256=digest, guards=guards,
                scope="Finite scalar sensitivity conditional on certified unitary native charts, exact allocation and residual-tolerant disposal in perturbed runs. Strict zero-only erasure is not preserved. Not a rounded supplier implementation.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    source_check()
    result = report(load_json(HOME / "WORD.json"))
    if args.write_result:
        with args.write_result.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        expected = load_json(HOME / "RESULT.json")
        require(json.dumps(result, sort_keys=True, allow_nan=False) ==
                json.dumps(expected, sort_keys=True, allow_nan=False), "committed scientific receipt mismatch")
    print("PASS_P104_CLEAN_DUAL_PRECISION " + " ".join(m + "=" + p["value"] for m, p in result["peaks"].items()) + " no_new_kappa")


if __name__ == "__main__":
    main()
