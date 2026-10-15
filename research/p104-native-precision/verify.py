#!/usr/bin/env python3
"""Exact P104 local precision interface; standard library, no producer imports.

Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/p104-native-channel/"
INPUTS = {
    SOURCE + name for name in (
        "inputs/LOWRANK-WITNESS.json", "inputs/P104-FIXTURE.json",
        "NATIVE-RECIPES.json.gz", "vendor/native_verify.py", "PROOF.md", "SOURCES.json"
    )
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def authenticate(root=ROOT):
    pins = json.loads((HERE / "SOURCES.json").read_text())["files"]
    found = {item["path"] for item in pins if item["usage"] == "input"}
    need(found == INPUTS, "complete precision source inventory")
    for item in pins:
        if item["usage"] == "input":
            actual = hashlib.sha256((root / item["path"]).read_bytes()).hexdigest()
            need(actual == item["sha256"], "source authentication: " + item["path"])


def span(values):
    result = {0}
    for value in values:
        result.update(x ^ value for x in tuple(result))
    return tuple(sorted(result))


def add(dst, src, coefficient):
    for key, value in src.items():
        total = dst.get(key, Q(0)) + coefficient * value
        if total:
            dst[key] = total
        else:
            dst.pop(key, None)


def norm(row):
    return sum(map(abs, row.values()), Q(0))


def serial_row(row):
    return [[key, str(value)] for key, value in sorted(row.items())]


def root_ports(fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1, *signs) for signs in product((-1, 1), repeat=7)
              if signs.count(-1) % 2 == 0]
    removed = {tuple(row) for row in fixture["F0"] + fixture["C"]}
    ports = [row for row in sorted(roots) if row not in removed]
    need(len(ports) == 104, "P104 geometry")
    return ports


def endpoint_check(rows, ports):
    for reg, actual in rows.items():
        expected = {reg: Q(1)}
        if reg.startswith("Y"):
            target = ports[int(reg[1:])]
            expected.update({"X" + str(i): Q(sum(a * b for a, b in zip(target, source)), 8)
                             for i, source in enumerate(ports)
                             if sum(a * b for a, b in zip(target, source))})
        need(actual == expected, "arbitrary-input endpoint: " + reg)


def forward(word):
    """Independent input and error symbols, retaining signs until each cut norm."""
    names = list(word["initial_frames"])
    rows = {reg: {reg: Q(1)} for reg in names}
    errors = {reg: {} for reg in names}
    frames = {reg: span(f) for reg, f in word["initial_frames"].items()}
    kinds, weights = {}, {}
    peaks = {"input": (Q(1), -1, names[0]),
             "absolute": (Q(0), -1, names[0]),
             "relative": (Q(0), -1, names[0])}
    witnesses = {key: {} for key in peaks}
    by_kind = {kind: (Q(0), -1, names[0]) for kind in ("transport", "add", "copy")}
    stream = hashlib.sha256()
    cuts, paid = [], Counter()
    for index, event in enumerate(word["program"]):
        op, reg = event[:2]
        if op == "zero":
            need(reg == "C" and reg not in rows, "fresh owned private lifetime")
            rows[reg], errors[reg], frames[reg] = {}, {}, span(event[2])
            continue
        need(reg in rows, "live destination")
        if op == "erase":
            need(reg == "C" and frames[reg] == span(event[2]), "owned discard frame")
            rows.pop(reg); errors.pop(reg); frames.pop(reg)
            continue
        if op == "transport":
            _, _, old, new, rank = event
            old, new = span(old), span(new)
            need(frames[reg] == old, "transport entry")
            need(set(old) <= set(new) or set(new) <= set(old), "nested source transport")
            need(rank == abs((len(old).bit_length() - 1) - (len(new).bit_length() - 1)),
                 "literal paid rank")
            frames[reg] = new
            paid[rank] += 1
        elif op in ("add", "copy"):
            src = event[2]
            need(src != reg and src in rows, "distinct live scalar operands")
            need(frames[src] == frames[reg] == span(event[-1]), "common physical chart")
            if op == "copy":
                need(reg == "C" and not rows[reg] and not errors[reg], "zero private copy destination")
                rows[reg], errors[reg] = dict(rows[src]), dict(errors[src])
            else:
                add(rows[reg], rows[src], Q(event[3]))
                add(errors[reg], errors[src], Q(event[3]))
        else:
            raise ValueError("unknown source instruction")
        kinds[index] = op
        weights[index] = 1 + abs(Q(event[3])) if op == "add" else Q(1)
        errors[reg][index] = Q(1)
        values = {"input": norm(rows[reg]), "absolute": norm(errors[reg]),
                  "relative": sum((abs(v) * weights[j] for j, v in errors[reg].items()), Q(0))}
        for key, value in values.items():
            if value > peaks[key][0]:
                peaks[key] = (value, index, reg)
                witnesses[key] = dict(rows[reg] if key == "input" else errors[reg])
        for kind in by_kind:
            value = sum((abs(v) for j, v in errors[reg].items() if kinds[j] == kind), Q(0))
            if value > by_kind[kind][0]:
                by_kind[kind] = (value, index, reg)
        cuts.append([index, reg, *[str(values[k]) for k in ("input", "absolute", "relative")]])
        stream.update(canonical([index, reg, serial_row(rows[reg]), serial_row(errors[reg])]) + b"\n")
    need(set(rows) == set(names), "all private lifetimes closed")
    need(frames == {reg: span(f) for reg, f in word["final_frames"].items()}, "final frame contract")
    return {"rows": rows, "errors": errors, "kinds": kinds, "weights": weights,
            "peaks": peaks, "witnesses": witnesses, "by_kind": by_kind, "cuts": cuts,
            "cut_coefficients_sha256": stream.hexdigest(), "paid": dict(sorted(paid.items()))}


def reverse(word):
    """Reverse adjoints of scalar instructions, with private lifetimes explicit."""
    columns = {reg: {reg: Q(1)} for reg in word["final_frames"]}
    responses = {}
    for index in range(len(word["program"]) - 1, -1, -1):
        event = word["program"][index]
        op, reg = event[:2]
        if op == "erase":
            need(reg not in columns, "reverse private birth")
            columns[reg] = {}
        elif op == "zero":
            columns.pop(reg)
        else:
            responses[index] = dict(columns[reg])
            if op == "add":
                add(columns[event[2]], columns[reg], Q(event[3]))
            elif op == "copy":
                add(columns[event[2]], columns[reg], Q(1))
                columns[reg] = {}
            else:
                need(op == "transport", "reverse instruction")
    return responses, columns


def unitary_circuit(native, circuit):
    """Structural proof premises, not a floating singular-value calculation."""
    for gate in circuit:
        kind = gate[0]
        if kind == "P":
            need(len(gate[1]) == 9 and all(0 <= x < 512 for x in gate[1]), "nine-bit permutation")
            native.inverse(gate[1])
        elif kind == "D":
            need(len(gate[1]) == len(gate[2]) == 9, "nine-bit diagonal")
            need(all(0 <= x < 512 for x in gate[1]), "diagonal bit range")
            need(all(isinstance(x, int) for x in gate[2]), "unit-modulus Gaussian phase")
        elif kind == "C":
            need(0 < gate[1] < 512 and gate[2] in (-1, 1), "normalized nonzero C direction")
        elif kind == "X":
            need(0 <= gate[1] < 512, "translation permutation")
        else:
            need(kind == "phase" and isinstance(gate[1], int), "scalar unit phase")


def native_binding(word, certificate):
    # authenticate() has run before this retained interpreter is imported.
    path = ROOT / (SOURCE + "vendor/native_verify.py")
    spec = importlib.util.spec_from_file_location("p104_precision_gaussian", path)
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    iso = certificate["label_isometry"]
    def multiply(rows, value):
        return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(rows))
    def convert(value):
        dual_value = multiply(iso["compressed_dual_gram"], value)
        return sum(((dual_value & vector).bit_count() % 2) << i
                   for i, vector in enumerate(iso["orthonormal_basis_compressed"]))
    need(len(span(convert(1 << i) for i in range(9))) == 512, "invertible physical label map")
    def key(frame):
        return span(convert(value) for value in frame)
    def compare(actual, expected, label):
        unitary_circuit(native, actual)
        unitary_circuit(native, expected)
        need(native.tableau(actual) == native.tableau(expected), label + " signed Pauli action")
        actual_state, denominator = native.state(actual)
        need((actual_state, denominator) == native.state(expected), label + " exact scalar phase")
        need(sum(a*a + b*b for a, b in actual_state.values()) == 4 ** denominator,
             label + " normalized Gaussian column")
    used = set()
    for record in certificate["transports"]:
        a, b = tuple(record["old"]), tuple(record["new"])
        compare(native.recipe(record["recipe"]), native.adjoint(native.frame(a, 9)) + native.frame(b, 9),
                "native transport")
        for index in record["events"]:
            need(index not in used, "unique native event binding")
            used.add(index)
            e = word["program"][index]
            need(e[0] == "transport" and key(e[2]) == span(a) and key(e[3]) == span(b),
                 "physical source-witness edge")
            need(e[4] == record["rank"] == record["recipe"]["rank"], "native rank binding")
    need(used == {i for i, e in enumerate(word["program"]) if e[0] == "transport"}, "complete native coverage")
    adapters = set()
    for record in certificate["endpoint_adapters"]:
        reg, where = record["register"], record["position"]
        normal, frame = record["normal"], tuple(record["frame"])
        need((where, reg) not in adapters and record["recipe"]["rank"] == 0, "unique monomial endpoint")
        adapters.add((where, reg))
        if where == "entry":
            need(key(word["initial_frames"][reg]) == span(frame), "entry frame binding")
            expected = native.adjoint((("C", normal, 1),)) + native.frame(frame, 9)
        else:
            need(where == "exit" and key(word["final_frames"][reg]) == span(frame), "exit frame binding")
            expected = native.adjoint(native.frame(frame, 9)) + (("C", normal, -1),) + native.fourier(9)
        compare(native.recipe(record["recipe"]), expected, "endpoint adapter")
    need(adapters == {("entry", "X"+str(i)) for i in range(104)} |
                     {("exit", "Y"+str(i)) for i in range(104)}, "complete endpoint coverage")
    return native, {"transport_recipes": len(certificate["transports"]), "paid_occurrences": len(used),
                    "monomial_endpoints": len(adapters), "exact_normalized_columns": len(certificate["transports"]) + len(adapters)}


def injected_run(word, defects=None, inputs=None, stop=None):
    """Scalar forward evaluation, independent of the coefficient-row machinery."""
    state = {reg: Q(0) for reg in word["initial_frames"]}
    if inputs:
        state.update(inputs)
    for index, event in enumerate(word["program"]):
        op, reg = event[:2]
        if op == "zero":
            state[reg] = Q(0)
        elif op == "erase":
            state.pop(reg)
        elif op == "copy":
            state[reg] = state[event[2]]
        elif op == "add":
            state[reg] += Q(event[3]) * state[event[2]]
        else:
            need(op == "transport", "injected execution opcode")
        if defects and index in defects:
            state[reg] += defects[index]
        if index == stop:
            break
    return state


def reject(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("control accepted: " + label)


def controls(word, ports, result, certificate, native):
    passed = []
    for which in ("input", "absolute", "relative"):
        value, index, reg = result["peaks"][which]
        row = result["witnesses"][which]
        signs = {key: (1 if coefficient > 0 else -1) for key, coefficient in row.items()}
        if which == "input":
            actual = injected_run(word, inputs=signs, stop=index)[reg]
        else:
            defects = {j: Q(sign) * (result["weights"][j] if which == "relative" else 1)
                       for j, sign in signs.items()}
            actual = injected_run(word, defects=defects, stop=index)[reg]
        need(actual == value, "constructive signed attainment: " + which)
        passed.append("attained_" + which)
    need(norm(result["rows"]["Y0"]) == 26 and result["peaks"]["input"][0] == 106,
         "endpoint magnitude cannot replace interior magnitude")
    passed.append("endpoint_only_input_cap_rejected")
    need(norm(result["errors"]["Q7"]) == 450, "restored dirt has nonzero accumulated defects")
    passed.append("error_free_dirty_restoration_rejected")
    copy_effect = max(sum((abs(v) for j, v in row.items() if result["kinds"][j] == "copy"), Q(0))
                      for name, row in result["errors"].items() if name.startswith("Y"))
    need(copy_effect == Q(3, 2), "discarded copies retain propagated errors")
    passed.append("discard_erases_prior_output_errors_rejected")
    for index, label in ((0, "missing_initial_compensation"), (len(word["program"])-1, "missing_final_cleanup")):
        bad = copy.deepcopy(word)
        bad["program"][index][3] = 0
        passed.append(reject(lambda: endpoint_check(forward(bad)["rows"], ports), label))
    bad = copy.deepcopy(word)
    erase = next(i for i, e in enumerate(bad["program"]) if e[0] == "erase")
    del bad["program"][erase]
    passed.append(reject(lambda: forward(bad), "private_lifetime_alias"))
    # Normalization is essential: omitting C's factor 1/2 multiplies its squared norm by four.
    vector, denominator = native.state((("C", 1, 1),))
    need(sum(a*a+b*b for a, b in vector.values()) == 4**denominator, "normalized child control")
    need(sum((2*a)**2+(2*b)**2 for a, b in vector.values()) != 4**denominator, "unnormalized child rejected")
    passed.append("unnormalized_native_child_rejected")
    # The norm is Hilbert, not pointwise: C(e_0+i e_1)=(1+i)e_0.
    other, other_denominator = native.state((("C", 1, 1),), 1)
    common = max(denominator, other_denominator)
    combined = {}
    for address in set(vector) | set(other):
        a, b = vector.get(address, (0, 0))
        c, d = other.get(address, (0, 0))
        combined[address] = (a*2**(common-denominator) - d*2**(common-other_denominator),
                             b*2**(common-denominator) + c*2**(common-other_denominator))
    squared = [Q(a*a+b*b, 4**common) for a, b in combined.values()]
    need(sum(squared) == 2 and max(squared) == 2, "Hilbert versus pointwise norm")
    passed.append("pointwise_contraction_rejected")
    # A pure phase leaves this norm interface unchanged; exact native identity must still reject it.
    rec = certificate["transports"][0]
    circuit = native.recipe(rec["recipe"])
    phased = circuit + (("phase", 1),)
    need(native.tableau(circuit) == native.tableau(phased) and native.state(circuit) != native.state(phased),
         "phase cannot be authenticated by a norm bound")
    passed.append("norm_only_phase_blindness_exhibited")
    K, P = Q(668), Q(106)
    for bits in (0, 1, 32, 128, 1024):
        u = Q(1, 2**(bits+17))
        need(K*u < 1 and P*K*u/(1-K*u) <= Q(1, 2**bits), "complete relative feedback")
        insufficient = Q(1, 2**(bits+16))
        need(P*K*insufficient/(1-K*insufficient) > Q(1, 2**bits), "one fewer uniform guard bit fails bound")
    need(K * Q(1, 512) >= 1, "feedback threshold is not an endpoint-only test")
    passed.append("relative_feedback_and_guard_boundary")
    return passed


def summarize(word, result, native_report):
    endpoint = {}
    for reg, row in sorted(result["errors"].items()):
        categories = {kind: sum((abs(v) for j, v in row.items() if result["kinds"][j] == kind), Q(0))
                      for kind in ("transport", "add", "copy")}
        endpoint[reg] = {**{kind: str(value) for kind, value in categories.items()},
                         "absolute": str(norm(row)),
                         "relative": str(sum((abs(v)*result["weights"][j] for j, v in row.items()), Q(0)))}
    groups = {}
    for group in ("source", "target", "dirty_helper"):
        names = [reg for reg in endpoint if (reg.startswith("X") if group == "source" else
                 reg.startswith("Y") if group == "target" else not reg.startswith(("X", "Y")))]
        groups[group] = {}
        for kind in ("transport", "add", "copy", "absolute", "relative"):
            maximum = max(Q(endpoint[reg][kind]) for reg in names)
            groups[group][kind] = {"value": str(maximum), "attainers": [reg for reg in names if Q(endpoint[reg][kind]) == maximum]}
    return {"status": "PASS_P104_NATIVE_PRECISION", "events": len(word["program"]),
            "initial_independent_roles": len(word["initial_frames"]),
            "defect_sites": dict(sorted(Counter(result["kinds"].values()).items())),
            "paid_profile": result["paid"], "rank_mass": sum(k*v for k, v in result["paid"].items()),
            "native_binding": native_report,
            "all_cut_peaks": {key: {"value": str(value), "event": index, "register": reg,
                                    "attaining_row_sha256": digest(serial_row(result["witnesses"][key]))}
                              for key, (value, index, reg) in result["peaks"].items()},
            "all_cut_type_peaks": {key: {"value": str(value), "event": index, "register": reg}
                                   for key, (value, index, reg) in result["by_kind"].items()},
            "all_cut_count": len(result["cuts"]), "all_cut_norms_sha256": digest(result["cuts"]),
            "all_cut_coefficients_sha256": result["cut_coefficients_sha256"],
            "endpoint_response_nonzeros": sum(map(len, result["errors"].values())),
            "endpoint_responses_sha256": digest({reg: serial_row(row) for reg, row in result["errors"].items()}),
            "endpoint_group_maxima": groups, "endpoint_rows": endpoint,
            "uniform_relative_guard_bits": 17,
            "scope": "Exact finite source-bound native local precision interface; arbitrary independent absolute defects are sharp. State-relative feedback is a sufficient bound, not an attained numerical-kernel error. No side correction, global hosting, tape/all-size supplier admission or new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new canonical receipt exclusively")
    args = parser.parse_args()
    authenticate()
    raw = (ROOT / (SOURCE + "inputs/LOWRANK-WITNESS.json")).read_bytes()
    word = json.loads(raw)
    fixture = json.loads((ROOT / (SOURCE + "inputs/P104-FIXTURE.json")).read_text())["section4_explicit_P104"]
    certificate = json.loads(gzip.decompress((ROOT / (SOURCE + "NATIVE-RECIPES.json.gz")).read_bytes()))
    need(hashlib.sha256(raw).hexdigest() == certificate["source_witness_sha256"], "native/scalar source binding")
    native, native_report = native_binding(word, certificate)
    result = forward(word)
    ports = root_ports(fixture)
    endpoint_check(result["rows"], ports)
    backward, inputs = reverse(word)
    transposed = {reg: {} for reg in result["errors"]}
    for index, column in backward.items():
        for reg, value in column.items():
            transposed[reg][index] = value
    need(transposed == result["errors"], "all signed endpoint sensitivities agree in both directions")
    need({out: {src: row[out] for src, row in inputs.items() if out in row}
          for out in result["rows"]} == result["rows"], "reverse arbitrary-input map")
    receipt = summarize(word, result, native_report)
    receipt["controls"] = controls(word, ports, result, certificate, native)
    receipt["source_witness_sha256"] = hashlib.sha256(raw).hexdigest()
    if args.write:
        with args.write.open("x") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        need(canonical(receipt) == canonical(json.loads((HERE / "RESULT.json").read_text())), "complete canonical receipt")
    print("PASS_P104_NATIVE_PRECISION input=106 absolute=450 relative=668 guard_bits=17 "
          f"native_recipes={native_report['transport_recipes']} endpoint_coefficients={receipt['endpoint_response_nonzeros']} "
          f"controls={len(receipt['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
