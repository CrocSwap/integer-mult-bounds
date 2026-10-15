#!/usr/bin/env python3
"""Exact QQ16 source-coordinate tap obstruction; standard library, read-only.

Pinned PR2093 code supplies source reconstruction and logical F/B maps.
The support argument, parity minors, witness synthesis, interface, tail
interpreter and controls here are new. Apache-2.0.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
import argparse
import copy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
REFERENCE_HASH = "1009fc5dc4843051d6d8e40edfbf1f5254b024623b5e8f73f10a4cfd756df15c"
NEW_WITNESS = {1: 1, 16: -1, 88: -1}
OLD_WITNESS = {2: -1, 8: 1, 85: 1}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    # Text comparison preserves JSON scalar types (unlike Python 1 == True).
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate(raw, digest, label):
    need(sha256(raw).hexdigest() == digest, "source hash: " + label)
    return raw


def load():
    reference = PACKAGE / "references/pr2093/verify.py"
    authenticate(reference.read_bytes(), REFERENCE_HASH, "PR2093 verifier")
    spec = importlib.util.spec_from_file_location("qq16_pr2093", reference)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = {r["path"]: r["sha256"] for r in sources["files"] if r["usage"] == "input"}
    for name, digest in inputs.items():
        need(old.INPUTS.get(name) == digest, "inherited source pin: " + name)
    required = {old.ARCHIVE, old.CERTIFICATE,
                old.EVIDENCE + "JOINT-QUERY-TRANSFER.md",
                old.EVIDENCE + "QQ16-SELECTED-WITNESS.json",
                old.EVIDENCE + "QQ16-RATIONAL-OBSERVATION-REVIEW.md"}
    need(set(inputs) == required, "complete live source inventory")
    raw = {n: authenticate((ROOT / n).read_bytes(), h, n) for n, h in inputs.items()}
    members = {}
    with tarfile.open(fileobj=BytesIO(raw[old.ARCHIVE]), mode="r:gz") as archive:
        for name, digest in old.MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), "unique archive member")
            data = authenticate(archive.extractfile(matches[0]).read(), digest, name)
            members[name.rsplit("/", 1)[-1]] = json.loads(gzip.decompress(data) if name.endswith(".gz") else data)
    cert = json.loads(gzip.decompress(raw[old.CERTIFICATE]))
    previous = json.loads(raw[old.EVIDENCE + "QQ16-SELECTED-WITNESS.json"])
    R = old.reconstruct_R(members["CANONICAL-WORD.json.gz"], members["LOCAL-PROGRAMS.json.gz"])
    need(R == [[Q(row.get(str(p), "0")) for p in range(112)] for row in cert["R_rows"]],
         "operation-derived R binding")
    need((cert["A_ports"], cert["T_ports"], cert["U_ports"]) ==
         (list(old.A), list(old.T), list(old.U)), "port partition binding")
    need(all(sum(R[i][p] * R[j][p] for p in old.U) == (48 if i == j else 0)
             for i in range(8) for j in range(8)), "ordinary Gram")
    phases, word = members["DATA-PHASES.json"], members["CANONICAL-WORD.json.gz"]
    need(all(phases["recipes"][p]["q"] == word["ports"][p] for p in range(112)), "phase/root binding")
    model = old.Model(R, phases)
    registry = {tuple(row["owner_right_matrix_columns"]) for row in cert["map_registry"].values()}
    bind_routes(model, registry)
    template = members["GLOBAL-TEMPLATE.json.gz"]
    bind_template(template)
    return old, model, template, previous, inputs, phases, registry


def bind_routes(model, registry):
    need(all(columns in registry for stages in model.routes for columns in stages),
         "actual route absent from packet registry")


def bind_template(template):
    need(template["recipe"][:2] == [
        {"kind": "local", "pair": 0, "reverse": False, "stage": 0},
        {"kind": "local", "pair": 0, "reverse": True, "stage": 1}], "first pair")
    recipe_calls = {(e["stage"], e["pair"], "backward" if e["reverse"] else "forward")
                    for e in template["recipe"] if e["kind"] == "local"}
    need(recipe_calls == {(c["stage"], c["pair"], c["orientation"])
                         for c in template["calls"]}, "recipe/hosted-call binding")


def pivots(matrix):
    """Rational row reduction, separate from the inherited matrix inverse."""
    rows, found = [list(map(Q, row)) for row in matrix], []
    for col in range(len(rows[0])):
        row = len(found)
        pivot = next((i for i in range(row, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        q = rows[row][col]
        rows[row] = [x / q for x in rows[row]]
        for i in range(row + 1, len(rows)):
            q = rows[i][col]
            if q:
                rows[i] = [x - q * y for x, y in zip(rows[i], rows[row])]
        found.append(col)
        if len(found) == len(rows):
            break
    return found


def determinant(matrix):
    """Separate fraction-free Bareiss check of each displayed integer minor."""
    need(all(Q(x).denominator == 1 for row in matrix for x in row), "integer minor")
    a = [[int(x) for x in row] for row in matrix]
    n, sign, previous = len(a), 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:
            row = next((i for i in range(k + 1, n) if a[i][k]), None)
            if row is None:
                return 0
            a[k], a[row], sign = a[row], a[k], -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                need(numerator % previous == 0, "Bareiss exact division")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1]


def minor(R, ports):
    return [[R[k][p] for p in ports] for k in range(8)]


def source_certificate(old, model):
    R = model.R
    C = minor(R, old.U)
    D = [[R[k][p] * (model.bases[p][0] & 1) for p in old.U] for k in range(8)]
    need((len(pivots(C)), len(pivots(C + D))) == (8, 16), "eight-dimensional defect")
    rows, fixture = [], []
    for excluded in old.U:
        bases, dets, inverses = [], [], []
        for bit in (0, 1):
            pool = [p for p in old.U if p != excluded and model.bases[p][0] & 1 == bit]
            chosen = [pool[i] for i in pivots(minor(R, pool))]
            need(len(chosen) == 8, "rank-eight parity class after one deletion")
            matrix = minor(R, chosen)
            det = determinant(matrix)
            need(det != 0, "nonzero parity minor")
            inv = old.inverse(matrix)
            need(all(sum(matrix[i][k] * inv[k][j] for k in range(8)) == (i == j)
                     for i in range(8) for j in range(8)), "inverse/minor cross-check")
            bases.append(chosen)
            dets.append(det)
            inverses.append(inv)
        for j in range(8):
            coeff = {p: sign * inverses[bit][i][j]
                     for bit, sign in ((0, -1), (1, 1))
                     for i, p in enumerate(bases[bit]) if inverses[bit][i][j]}
            need(excluded not in coeff, "zero tapped source")
            need(all(sum(R[k][p] * c for p, c in coeff.items()) == 0 for k in range(8)), "constructed kernel vector")
            need(all(sum(R[k][p] * c * (model.bases[p][0] & 1) for p, c in coeff.items())
                     == (k == j) for k in range(8)), "constructed identity defect")
            if excluded == 2:
                fixture.append(coeff)
        rows.append({"excluded_source": excluded, "even_basis": bases[0], "odd_basis": bases[1],
                     "determinants": dets, "initial_A_defect_dimension_at_identity": 8})
    return {"rank_R_U": 8, "rank_stacked_R_D": 16, "single_source_cases": rows,
            "synthesized_vectors": len(old.U) * 8,
            "u2_kernel_basis": [{str(p): str(c) for p, c in sorted(vector.items())} for vector in fixture],
            "k_source_dimension_floor": {str(k): 8 if k == 0 else 9 - k for k in range(9)}}, fixture


def start(old, model, coefficients, omit_initial=False):
    h = [{model.bases[p][0]: Q(coefficients[p])} if p in coefficients else {} for p in range(112)]
    need(all(not any(model.query(s, h)) for s in range(1, 9)), "all nonzero-chart queries")
    b0 = model.query(0, h)
    need(any(old.at_identity(row) for row in b0), "nonzero B0 at identity")
    cancel = model.inject(0, old.A, b0)
    x, y = copy.deepcopy(h), [{} for _ in range(112)]
    for p in old.A:
        x[p] = {} if omit_initial else old.linear((-1, cancel[p]))
        y[p] = old.linear((-1, x[p]))
    initial = [str(old.at_identity(x[p])) for p in old.A]
    x, y, f0 = model.forward(0, x, y)
    need(not any(f0), "zero F0 history")
    need(x == h and y == h, "post-F0 ordinary-only state")
    return h, x, y, f0, initial


def interface(old, x, y, source, target, sign=-1):
    x, y = copy.deepcopy(x), copy.deepcopy(y)
    for a, t in zip(old.A, old.T):
        x[t] = old.linear((1, x[t]), (1, x[a]))
        y[t] = old.linear((1, y[t]), (-1, x[a]))
    before = old.linear((1, x[target]), (1, y[target]))
    value = x[source].copy()
    x[target] = old.linear((1, x[target]), (1, value))
    y[target] = old.linear((1, y[target]), (sign, value))
    need(before == old.linear((1, x[target]), (1, y[target])), "paired selected sum")
    return x, y


def run_tail(old, model, template, x, y, f0, omit_minus=False):
    empty = lambda: [{} for _ in range(112)]
    banks = [[x, y]] + [[empty(), empty()] for _ in range(3)]
    histories, trajectory, completed = {0: f0}, [], []
    selected_cuts = [[fields[p] for fields in (x, y) for p in old.A + old.T if fields[p]]]
    for event in template["recipe"][2:]:
        if omit_minus and event == {"kind": "bridge", "src": 1, "dst": 0, "coefficient": -1}:
            continue
        kind = event["kind"]
        if kind == "bridge":
            src, dst, c = event["src"], event["dst"], event["coefficient"]
            for p in old.U:
                banks[dst][0][p] = old.linear((1, banks[dst][0][p]), (c, banks[src][0][p]))
                banks[src][1][p] = old.linear((1, banks[src][1][p]), (-c, banks[dst][1][p]))
            record = dict(event)
        elif kind == "local":
            pair, stage = event["pair"], event["stage"]
            if event["reverse"]:
                banks[pair] = list(model.backward(stage, stage + 1, *banks[pair]))
            else:
                bx, by, f = model.forward(stage, *banks[pair])
                banks[pair] = [bx, by]
                histories[stage] = f
            record = {"kind": "local", "stage": stage}
        else:
            need(kind == "terminal", "tail event alphabet")
            completed = [row.copy() for bx, _ in banks for row in bx]
            banks = [[by, [old.linear((-1, row)) for row in bx]] for bx, by in banks]
            record = {"kind": "terminal"}
        selected_cuts.append([fields[p] for pair in banks for fields in pair for p in old.A + old.T if fields[p]])
        trajectory.append((record, copy.deepcopy(banks)))
    return banks, histories, completed, selected_cuts, trajectory


def invisible(old, model, template, previous, coefficients, source=2, target=21,
              omit_minus=False, wrong_endpoint=False):
    h, x, y, f0, initial = start(old, model, coefficients)
    x, y = interface(old, x, y, source, target)
    need(x == h and y == h, "tap must vanish on this witness")
    x, y = model.backward(1, 2, x, y)
    need(not any(x) and y == h, "exact B1 erasure")
    banks, histories, completed, cuts, trace = run_tail(old, model, template, x, y, f0, omit_minus=omit_minus)
    need(not any(cuts), "all selected cuts zero")
    need(not any(completed), "completed-X descendants zero")
    need(sorted(histories) == [0, 2, 4, 6, 8] and not any(row for q in histories.values() for row in q),
         "all five histories zero")
    need(banks[0][0] == h and not any(row for bx, by in banks[1:] for fields in (bx, by) for row in fields)
         and not any(row for _, by in banks for row in by), "old-Y-typed final X0 only")
    actual_trace = []
    for record, states in trace:
        multipliers = []
        for pair in states:
            for fields in pair:
                c = next((c for c in (0, 1, -1) if all(fields[p] == old.linear((c, h[p])) for p in old.U)), None)
                need(c is not None, "ordinary trajectory closure")
                multipliers.append(c)
        actual_trace.append(dict(record, ordinary=multipliers))
    need(actual_trace == previous["trajectory_after_B1"], "complete retained tail binding")
    if wrong_endpoint:
        need(not any(banks[0][0]), "old-Y endpoint is not completed-X")
    return {"coefficients": {str(p): str(c) for p, c in sorted(coefficients.items())},
            "axes": {str(p): model.bases[p][0] for p in sorted(coefficients)},
            "B0_at_identity": [str(old.at_identity(r)) for r in model.query(0, h)],
            "initial_X_A_at_identity": initial, "tap": [source, target],
            "zero_selected_cuts": len(cuts), "zero_nonzero_chart_queries": 8,
            "zero_forward_histories": 5, "tail": actual_trace}


def rejection(name, action, expected, records):
    try:
        action()
    except ValueError as error:
        need(expected in str(error), "wrong rejection for " + name + ": " + str(error))
        records.append(name)
    else:
        raise ValueError("negative control accepted: " + name)


def build_result():
    old, model, template, previous, inputs, phases, registry = load()
    ranks, fixture = source_certificate(old, model)
    witness = invisible(old, model, template, previous, NEW_WITNESS)
    old_witness = invisible(old, model, template, previous, OLD_WITNESS, source=1)
    need(set(NEW_WITNESS).isdisjoint(OLD_WITNESS), "disjoint witness supports")
    coverage = []
    for source in old.U:
        coeff = OLD_WITNESS if source not in OLD_WITNESS else NEW_WITNESS
        h, x, y, _, _ = start(old, model, coeff)
        for target in old.T:
            tx, ty = interface(old, x, y, source, target)
            need(tx == h and ty == h, "single-tap interface coverage")
        coverage.append({"source": source, "witness": "old" if coeff is OLD_WITNESS else "new"})
    for coeff in fixture:
        invisible(old, model, template, previous, coeff)
    # An eight-port example: U2 plus the first seven odd basis ports.
    # U2 was excluded in this family; the last odd column kills the other seven.
    odd_basis = next(row["odd_basis"] for row in ranks["single_source_cases"]
                     if row["excluded_source"] == 2)
    seven_coeff = {}
    for j, vector in enumerate(fixture):
        for p, c in vector.items():
            seven_coeff[p] = seven_coeff.get(p, Q(0)) + model.R[j][odd_basis[-1]] * c
    seven_coeff = {p: c for p, c in seven_coeff.items() if c}
    need(not set(odd_basis[:7]).intersection(seven_coeff), "seven zero source coordinates")
    h7, x7, y7, _, _ = start(old, model, seven_coeff)
    for source, target in zip([2] + odd_basis[:7], old.T):
        x7, y7 = interface(old, x7, y7, source, target)
    need(x7 == h7 and y7 == h7, "eight-tap interface remains invisible")
    seven_witness = invisible(old, model, template, previous, seven_coeff,
                              source=odd_basis[0], target=old.T[0])
    # Positive control: the existing tap still repairs PR2093's old witness.
    h, x, y, f0, _ = start(old, model, OLD_WITNESS)
    tx, ty = interface(old, x, y, 2, 21)
    bx, by = model.backward(1, 2, tx, ty)
    banks, histories, completed, _, _ = run_tail(old, model, template, bx, by, f0)
    need(banks[0][0][21] == {37: Q(11)}, "PR2268 positive tail control")
    counts = {"selected": sum(bool(fields[p]) for pair in banks for fields in pair for p in old.A + old.T),
              "history": sum(bool(r) for q in histories.values() for r in q),
              "completed_X": sum(bool(r) for r in completed)}
    need(counts == {"selected": 34, "history": 4, "completed_X": 65}, "PR2268 observation census")
    controls = []
    rejection("wrong dependency coefficient", lambda: start(old, model, {1: 1, 16: 1, 88: -1}),
              "all nonzero-chart queries", controls)
    rejection("missing initial A cancellation", lambda: start(old, model, NEW_WITNESS, omit_initial=True),
              "zero F0 history", controls)
    rejection("tap reads a live witness port", lambda: invisible(old, model, template, previous, NEW_WITNESS, source=1),
              "tap must vanish", controls)
    rejection("wrong tap sign", lambda: interface(old, x, y, 2, 21, sign=1), "paired selected sum", controls)
    rejection("missing negative bridge", lambda: invisible(old, model, template, previous, NEW_WITNESS, omit_minus=True),
              "completed-X descendants zero", controls)
    rejection("wrong final observation type", lambda: invisible(old, model, template, previous, NEW_WITNESS, wrong_endpoint=True),
              "old-Y endpoint", controls)
    rejection("old-chart B0 read detects the witness", lambda: need(not any(model.query(0, [
        {model.bases[p][0]: Q(NEW_WITNESS[p])} if p in NEW_WITNESS else {} for p in range(112)])),
        "old-chart observation"), "old-chart observation", controls)
    corrupted_phases = copy.deepcopy(phases)
    corrupted_phases["recipes"][1]["idle_children"][0]["orthogonal_axes"][0] ^= 1
    rejection("changed chart axis", lambda: old.Model(model.R, corrupted_phases), "orthonormal chart", controls)
    rejection("missing actual packet route", lambda: bind_routes(model, registry - {model.routes[1][1]}),
              "actual route absent", controls)
    corrupted_template = copy.deepcopy(template)
    for event in corrupted_template["recipe"]:
        if event.get("stage") == 2:
            event["pair"] = 1
    rejection("wrong later pair binding", lambda: bind_template(corrupted_template), "recipe/hosted-call binding", controls)
    rejection("duplicate parity-minor column", lambda: need(determinant(minor(model.R, [
        ranks["single_source_cases"][0]["even_basis"][0]] * 8)) != 0, "minor singular"), "minor singular", controls)
    rejection("corrupt inherited source", lambda: authenticate(b"changed", REFERENCE_HASH, "reference"), "source hash", controls)
    result = {"schema": "qq16-coordinate-tap-kernel-v1", "status": "PASS_QQ16_COORDINATE_TAP_KERNEL",
              "inputs": inputs, "reference_sha256": REFERENCE_HASH, "rank_certificate": ranks,
              "route_bindings": sum(len(stages) for stages in model.routes),
              "new_witness": witness, "old_disjoint_witness": old_witness,
              "single_source_coverage": coverage, "single_tap_cases": len(coverage) * len(old.T),
              "eight_port_fixture": {"sources": [2] + odd_basis[:7], "witness": seven_witness},
              "u2_full_tail_basis_vectors": len(fixture), "positive_PR2268_counts": counts,
              "positive_PR2268_final_X21": {"37": "11"}, "rejecting_controls": controls,
              "scope": "Logical source-coordinate taps at F0/B1; no native tariff, full supplier or new kappa."}
    mutated = copy.deepcopy(result)
    mutated["single_tap_cases"] = True
    rejection("receipt scalar-type corruption", lambda: need(canonical(mutated) == canonical(result), "receipt mismatch"),
              "receipt mismatch", controls)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", type=Path, help="create a receipt exclusively")
    args = parser.parse_args()
    result = build_result()
    if args.emit_result:
        with args.emit_result.open("x") as output:
            output.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        need(canonical(json.loads((PACKAGE / "RESULT.json").read_text())) == canonical(result), "complete canonical receipt mismatch")
    print("PASS_QQ16_COORDINATE_TAP_KERNEL single_taps=768 A_defect=8 ports<=8_excluded controls=13 no_new_kappa")


if __name__ == "__main__":
    main()
