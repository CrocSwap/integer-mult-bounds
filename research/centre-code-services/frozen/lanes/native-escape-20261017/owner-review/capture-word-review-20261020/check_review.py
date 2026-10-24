"""Review the literal capture word by two exact operator methods."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
LANE = HERE.parents[1]
LANES = LANE.parent
PRODUCER = LANE / "rational-code-admission-20261020"
PINS = {
    "section": (
        LANES / "coherent-port/section-entry-20261020/SECTION.json",
        "23568099ea426947015eca86f7d86742a4758f33327e725b047441daab7c8bd7",
    ),
    "response": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json",
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
    ),
    "code": (
        PRODUCER / "unnormalised-final-normal/UNNORMALISED-CODE.json",
        "8dd0706ad41a843c9e74346b181389712a81ba6f354fdd019688e2d6b094908e",
    ),
    "code_review": (
        HERE.parent / "unnormalised-code-review-20261020/FREEZE.json",
        "c7f9f066f751828fd7199abb88f968e6a7aa51219cf37841d06ddd3594f25575",
    ),
    "constants": (
        PRODUCER / "centre-constants-normal/CENTRE-CONSTANTS.json",
        "9f45130ccde5bf1624bf051f4b10023411d6f35f0ac99bd6ab13572d4c530368",
    ),
    "proof": (
        PRODUCER / "CAPTURE-WORD.md",
        "29386ef90deb1eff60f88a42d74b35d9474fad73a50e540485b212bdb3f9891a",
    ),
    "checker": (
        PRODUCER / "check_capture_word.py",
        "44a122a50ee63a82002501eacb4b9eed84f8b423b757d940c5e509f9c852ca0d",
    ),
    "literal": (
        PRODUCER / "capture-word-normal/CAPTURE-WORD.json",
        "8761a302a154e4e19fedb22a9ccfe1db710ce16b3edf2a0e3704a6d0b837d303",
    ),
    "receipt": (
        PRODUCER / "capture-word-normal/CHECKS.json",
        "b3d5eb3b3bc5e25668ac49452aae2012dda387f8a735d0be8b2e036a1ac1f472",
    ),
    "odd_grid": (
        PRODUCER / "CLIQUE-CODE-GRID.md",
        "c06fab014b9dee89b45b1c18c7e3c8a3140a04416f3c63fe52a3f39ac0159639",
    ),
    "scan_proof": (
        LANES / "independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md",
        "e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01",
    ),
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def rows(data):
    result = []
    for row in data:
        pairs = row.items() if isinstance(row, dict) else enumerate(row)
        result.append({int(j): F(x) for j, x in pairs if F(x)})
    return result


def unit(n):
    return [{i: F(1)} for i in range(n)]


def combine(a, b, q):
    keys = a.keys() | b.keys()
    result = {j: a.get(j, F(0)) + q * b.get(j, F(0)) for j in keys}
    return {j: x for j, x in result.items() if x}


def product(a, b):
    columns = {}
    for k, row in enumerate(b):
        for j, x in row.items():
            columns.setdefault(j, {})[k] = x
    result = []
    for row in a:
        target = {}
        for j, col in columns.items():
            value = sum(row[k] * col[k] for k in row.keys() & col.keys())
            if value:
                target[j] = value
        result.append(target)
    return result


def extend(a):
    return [row.copy() for row in a] + unit(640)[len(a):]


def selected_map(a, selected):
    result = unit(112)
    for i, p in enumerate(selected):
        result[p] = {selected[j]: x for j, x in a[i].items()}
    return result


def scalar(gate):
    op = gate[0]
    if op == "NEG":
        return F(-1)
    if op == "SCALE2":
        need(gate[2] in (-1, 1), "Only one-bit binary scales")
        return F(2) ** gate[2]
    need(op in ("MULTIPLY_ODD", "DIVIDE_ODD") and gate[2] in (3, 5),
         "Only admitted fixed-odd scalar gates")
    return F(gate[2]) if op == "MULTIPLY_ODD" else F(1, gate[2])


def gate_inverse(gate):
    result = gate[:]
    if gate[0] == "ADD":
        result[3] *= -1
    elif gate[0] == "SCALE2":
        result[2] *= -1
    elif gate[0] in ("MULTIPLY_ODD", "DIVIDE_ODD"):
        result[0] = "DIVIDE_ODD" if gate[0] == "MULTIPLY_ODD" else "MULTIPLY_ODD"
    else:
        need(gate[0] == "NEG", "Known inverse event")
    return result


def backward(word):
    result = []
    for output in range(640):
        form = {output: F(1)}
        for gate in reversed(word):
            target = gate[1]
            q = form.get(target)
            if not q:
                continue
            if gate[0] == "ADD":
                source = gate[2]
                value = form.get(source, F(0)) + gate[3] * q
                if value:
                    form[source] = value
                else:
                    form.pop(source, None)
            else:
                form[target] = q * scalar(gate)
        result.append(form)
    return result


def valuation(denominator, p):
    h = 0
    while denominator % p == 0:
        denominator //= p
        h += 1
    return h


def replay(word, initial=None, exact=False, integral=False):
    state = unit(640) if initial is None else [row.copy() for row in initial]
    need(len(state) == 640, "All formal input roles")
    original_other = [row.copy() for row in state[112:]]
    stored = max(sum(abs(x) for x in row.values()) for row in state)
    operand = F(0)
    levels = {p: max(valuation(x.denominator, p) for row in state for x in row.values())
              for p in (2, 3, 5)}
    divisions = Counter()
    witnesses = {"stored": None, "operand": None}
    for step, gate in enumerate(word):
        op, target = gate[:2]
        need(0 <= target < 112, "No role outside the data bank is written")
        if op == "ADD":
            source, sign = gate[2:]
            need(0 <= source < 112 and source != target and sign in (-1, 1),
                 "No other role is read")
            bound = sum(abs(x) for x in state[target].values()) + sum(abs(x) for x in state[source].values())
            if bound > operand:
                operand, witnesses["operand"] = bound, step
            state[target] = combine(state[target], state[source], sign)
        else:
            if op == "DIVIDE_ODD" and exact:
                p = gate[2]
                need(all(x.denominator % p != 0 and x.numerator % p == 0
                         for x in state[target].values()), "Exact division on every input coefficient")
                divisions[str(p)] += 1
            q = scalar(gate)
            state[target] = {j: q * x for j, x in state[target].items()}
        if integral:
            need(all(x.denominator == 1 for x in state[target].values()), "Integer common-grid prefix")
        if exact:
            need(all(x.denominator & (x.denominator - 1) == 0
                     for x in state[target].values()), "No odd denominator at a valid prefix")
        bound = sum(abs(x) for x in state[target].values())
        if bound > stored:
            stored, witnesses["stored"] = bound, step
        for p in levels:
            levels[p] = max(levels[p], max((valuation(x.denominator, p)
                                           for x in state[target].values()), default=0))
    need(state[112:] == original_other, "All 528 arbitrary other rows are unchanged")
    need(all(j < 112 for row in state[:112] for j in row), "All 528 other columns are absent from data")
    return state, {
        "max_stored_row_l1": str(stored), "max_ADD_operand_l1": str(operand),
        "denominator_heights": {str(p): h for p, h in levels.items()},
        "checked_exact_complex_divisions": dict(sorted(divisions.items())),
    }, witnesses


def invoice(word):
    counts = Counter(g[0] for g in word)
    scans = Counter(g[0] + "_" + str(g[2]) for g in word
                    if g[0] in ("MULTIPLY_ODD", "DIVIDE_ODD"))
    return {"old_real_scalar_units": 8 * counts["ADD"] + 2 * (counts["NEG"] + counts["SCALE2"]),
            "gate_counts": dict(sorted(counts.items())),
            "real_fixed_odd_scans": {key: 2 * value for key, value in sorted(scans.items())},
            "new_owned_fields": 0, "native_children": 0, "maps_inside_common_chart": 0}


def parse_scatter(word):
    terms, i = [], 0
    while i < len(word):
        gate = word[i]
        if gate[0] == "ADD":
            terms.append((gate[1], gate[2], F(gate[3])))
            i += 1
        else:
            need(i + 2 < len(word) and gate[0] == "SCALE2", "Temporary source scale")
            middle, last = word[i + 1:i + 3]
            need(middle[0] == "ADD" and middle[2] == gate[1] and
                 middle[1] != gate[1] and last == ["SCALE2", gate[1], -gate[2]],
                 "Literal source restoration before the next term")
            terms.append((middle[1], middle[2], F(middle[3]) * F(2) ** gate[2]))
            i += 3
    return terms


def relabel(word, selected):
    result = []
    for gate in word:
        copy = gate[:]
        copy[1] = selected[copy[1]]
        if copy[0] == "ADD":
            copy[2] = selected[copy[2]]
        result.append(copy)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    need(shutil.disk_usage(HERE).free >= 3 * 2**30, "Disk floor")
    data, manifest = {}, {}
    for name, (path, digest) in PINS.items():
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == digest, "Source pin " + name)
        manifest[name] = {"path": str(path), "sha256": digest, "bytes": len(raw)}
        if path.suffix == ".json":
            data[name] = json.loads(raw)
    for name in ("CAPTURE-WORD.json", "CHECKS.json"):
        need((PRODUCER / "capture-word-normal" / name).read_bytes() ==
             (PRODUCER / "capture-word-optimized" / name).read_bytes(), "Producer run equality")
    source, section, literal, published = (data[k] for k in ("response", "section", "literal", "receipt"))
    selected, ordinary = section["selected_carriers"], section["ordinary_carriers"]
    need(literal["selected_carriers"] == selected and literal["ordinary_carriers"] == ordinary,
         "Actual carrier lists")
    u, v = rows(source["correction_U"]), rows(source["correction_V"])
    ua, uai = [u[p] for p in selected], rows(section["minor_inverse"])
    need(product(ua, uai) == product(uai, ua) == unit(30), "Both actual minor inverse orders")
    b, bi = rows(section["B0"]), rows(section["B0_inverse"])
    need(product(v, u) == b and product(b, bi) == product(bi, b) == unit(30), "Actual B0")
    pivot_map = [{selected[j]: x for j, x in row.items()} for row in uai]
    projection = product(u, pivot_map)
    capture = unit(112)
    for i, p in enumerate(selected):
        capture[p] = v[i].copy()
    for p in ordinary:
        capture[p] = combine({p: F(1)}, projection[p], F(-1))
    pre = [{selected[i]: F(1), **{p: -v[i][p] for p in ordinary if p in v[i]}} for i in range(30)]
    decode = product(u, product(bi, pre))
    for p in ordinary:
        decode[p] = combine(decode[p], {p: F(1)}, F(1))
    need(capture == rows(data["code"]["capture"]) and decode == rows(data["code"]["decode"]),
         "Source reconstruction agrees with the reviewed code")
    word, inverse = literal["capture"], literal["decode"]
    need(len(word) == len(inverse) == 550 and inverse == [gate_inverse(g) for g in reversed(word)],
         "Exact reversed inverse word")
    boundaries = literal["capture_boundaries"]
    need(boundaries == {"minor_inverse": 102, "complement": 354, "B0": 430, "capture": 550},
         "Exact block boundaries")
    minor = selected_map(uai, selected)
    scatter = unit(112)
    for p in ordinary:
        scatter[p].update({selected[j]: -x for j, x in u[p].items()})
    gather = unit(112)
    for i, p in enumerate(selected):
        gather[p].update({q: x for q, x in v[i].items() if q in ordinary})
    segment_checks = {}
    start = 0
    for label, target in (("minor_inverse", minor), ("complement", scatter),
                          ("B0", selected_map(b, selected)), ("capture", gather)):
        end = boundaries[label]
        segment = word[start:end]
        need(backward(segment) == extend(target), "Independent reverse block " + label)
        segment_checks[label] = invoice(segment)
        start = end
    scatter_terms = parse_scatter(word[102:354])
    need(Counter(scatter_terms) == Counter((p, selected[j], -x) for p in ordinary for j, x in u[p].items()),
         "Every U_O scatter term and restored source")
    need(Counter(abs(x) for _, _, x in scatter_terms) == {F(1, 2): 64, F(1): 60},
         "Actual scatter coefficient counts")
    need(Counter(parse_scatter(word[430:])) ==
         Counter((selected[i], p, x) for i, row in enumerate(v) for p, x in row.items() if p in ordinary),
         "Every V_O gather term")
    for label, events, expected in (("capture", word, capture), ("generic_decode", inverse, decode)):
        state, bounds, witnesses = replay(events)
        need(state == backward(events) == extend(expected), "Both 640-column methods " + label)
        need(bounds == published[label]["prefix_bounds"] and invoice(events) == published[label]["invoice"],
             "Exact published bounds and invoice " + label)
        segment_checks[label + "_peak_steps"] = witnesses
    decoded, valid_bounds, valid_peaks = replay(inverse, extend(capture), exact=True)
    need(decoded == unit(640) and valid_bounds == published["valid_decode"], "Valid-code decode")
    need(replay(word, extend(decode))[0] == unit(640), "Other complete inverse order")
    scaled_identity = [{i: F(60)} for i in range(640)]
    generic_scaled, generic_grid_bounds, _ = replay(inverse, scaled_identity, exact=True, integral=True)
    need(generic_scaled == [{j: 60 * x for j, x in row.items()} for row in extend(decode)],
         "Generic inverse on an explicit common integer grid")
    constants = data["constants"]["families"]["rank30"]["words"]
    chains = {}
    for label, target_name in (("G0", "response"), ("G0_inverse", "response_inverse")):
        full = word + relabel(constants[label], selected) + inverse
        state, bounds, peaks = replay(full, exact=True)
        target = extend(rows(source[target_name]))
        need(state == backward(full) == target, "Both complete chain methods " + label)
        need(bounds == published["complete_scalar_chains"][label]["prefix_bounds"] and
             invoice(full) == published["complete_scalar_chains"][label]["invoice"],
             "Complete chain costs and prefixes " + label)
        chains[label] = {"invoice": invoice(full), "prefix_bounds": bounds, "peak_steps": peaks}
    for name, (path, digest) in PINS.items():
        need(sha256(path.read_bytes()).hexdigest() == digest, "Input bytes unchanged " + name)
    result = {
        "status": "PASS_INDEPENDENT_CAPTURE_WORD_REVIEW",
        "source_pins": manifest,
        "all_input_columns": 640, "unchanged_other_roles": 528,
        "forward_and_backward_methods": True,
        "both_inverse_orders": True,
        "blocks": segment_checks,
        "capture": published["capture"],
        "generic_decode": published["generic_decode"],
        "valid_decode": {"prefix_bounds": valid_bounds, "peak_steps": valid_peaks},
        "generic_integer_grid": {"input_scale": 60, "prefix_bounds": generic_grid_bounds,
                                 "all_prefixes_integral": True},
        "complete_scalar_chains": chains,
        "odd_arithmetic_head_coefficients": {"one_direction": 176, "complete_chain": 352},
        "preserved_inputs": True,
        "scope": "Common-chart scalar word. No physical cut, native endpoint, outer map cost, or complete supplier invoice.",
    }
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "CHECKS.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    (args.out / "SOURCE-MANIFEST.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
