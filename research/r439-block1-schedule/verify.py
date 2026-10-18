"""Exact finite punctured-block replacement and native-word checks; no new rate claim.

Adapted from mtpsl / PR691 verifier structure, originally prepared with
substantial OpenAI Codex assistance, Apache-2.0.
Prepared for Krishnendu Purohit (@Deftsalt-debug) with substantial OpenAI Codex assistance.
Python 3.10+, standard library only. No assertions are used for acceptance.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
AUDITOR = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
EXECUTION_INPUTS = [WORD, AUDITOR, EXPORTER]


class Reject(Exception):
    pass


def need(condition, reason):
    if not condition:
        raise Reject(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def matrix(ops, positive=False):
    # Each column is evolved separately; search.py evolves whole rows.
    cols = []
    for j in range(10):
        values = [int(i == j) for i in range(10)]
        for d, s in ops:
            need(type(d) is int and type(s) is int and 0 <= d < 10 and
                 0 <= s < 10 and d != s, "invalid circuit gate")
            values[d] = values[d] + values[s] if positive else values[d] ^ values[s]
        cols.append(values)
    return [list(r) for r in zip(*cols)]


def circuit_check(old, new):
    need(matrix(old) == matrix(new), "circuit F2 map changed")
    positive = {}
    for direction, a, b in (("forward", old, new), ("reverse", old[::-1], new[::-1])):
        before, after = matrix(a, True), matrix(b, True)
        need(all(y <= x for rr, ss in zip(before, after) for x, y in zip(rr, ss)),
             direction + " positive matrix increased")
        positive[direction] = {"original": before, "replacement": after}
    return positive


def optimality(recipe):
    """Independent of nomination: solve each donor equation by F2 elimination,
    then check its lift entry by entry over Z. No packed subset sums imported.

    Every reachable current matrix is invertible, since its path consists of
    elementary row additions. Thus the F2 donor subset is unique. The positive
    binary target and unit diagonal forbid repeated donors in any exact Z sum.
    """
    need(recipe["split"] == 14, "wrong factor boundary")
    need(len(recipe["factors"]) == 2, "wrong factor coverage")
    results, combined = [], []
    for old, recorded in zip((recipe["original"][:14], recipe["original"][14:]), recipe["factors"]):
        target = matrix(old, True)
        need(all(x in (0, 1) for row in target for x in row) and
             all(target[i][i] == 1 for i in range(10)), "factor outside binary unit-diagonal class")
        rows = [sum(x << j for j, x in enumerate(row)) for row in target]
        distance = [None] * 1024
        distance[0] = 0
        edges = 0
        attempts = 0
        for state in range(1024):
            if distance[state] is None:
                continue
            current = [rows[i] if state >> i & 1 else 1 << i for i in range(10)]
            basis = {}
            for i, value in enumerate(current):
                expression = 1 << i
                while value:
                    p = value.bit_length() - 1
                    if p not in basis:
                        basis[p] = (value, expression)
                        break
                    v, e = basis[p]
                    value ^= v
                    expression ^= e
                need(value != 0, "reachable donor matrix is singular")
            for r in range(10):
                if state >> r & 1:
                    continue
                attempts += 1
                value = rows[r] ^ (1 << r)
                donors = 0
                while value:
                    p = value.bit_length() - 1
                    v, e = basis[p]
                    value ^= v
                    donors ^= e
                if donors >> r & 1:
                    continue
                actual = [sum((current[s] >> j) & 1 for s in range(10) if donors >> s & 1)
                          for j in range(10)]
                if actual != [target[r][j] - int(j == r) for j in range(10)]:
                    continue
                edges += 1
                nxt = state | (1 << r)
                candidate = distance[state] + donors.bit_count()
                if distance[nxt] is None or candidate < distance[nxt]:
                    distance[nxt] = candidate
        need(distance == recorded["distance"], "distance certificate mismatch")
        need(distance[-1] == recorded["minimum"], "minimum certificate mismatch")
        need(sum(d is not None for d in distance) == recorded["reachable_states"] and
             edges == recorded["reachable_edges"], "state/edge coverage mismatch")
        batches = recorded["batches"]
        need(len(batches) == 10 and sorted(r for r, _ in batches) == list(range(10)),
             "not a destination-once schedule")
        gates = [[r, s] for r, donors in batches for s in donors]
        need(gates == recorded["gates"] and len(gates) == distance[-1] and
             matrix(gates, True) == target, "schedule fails to attain minimum")
        combined.extend(gates)
        results.append({"minimum": distance[-1], "states": sum(d is not None for d in distance),
                        "state_destination_checks": attempts, "feasible_edges": edges,
                        "distance_sha256": sha(canonical(distance))})
    need(combined == recipe["replacement"], "replacement differs from factor schedules")
    return results


def cleanup(w):
    return [[1, d, list(ss)] for _, d, ss in reversed(w["A"] + w["B"])
            if not 111 <= d < 222]


def build(base, recipe):
    need((recipe["phase"], recipe["start"], recipe["stop"], recipe["frame"], recipe["block"])
         == ("B", 128, 163, 507, 1), "unexpected circuit location")
    regs = recipe["registers"]
    need(regs == [0, 3, 11, 61, 62, 63, 68, 69, 72, 465], "unexpected circuit registers")
    original = [[507, regs[d], [regs[s]]] for d, s in recipe["original"]]
    need(base["B"][128:163] == original, "original gate slice mismatch")
    circuit_check(recipe["original"], recipe["replacement"])
    out = copy.deepcopy(base)
    out["B"][128:163] = [[507, regs[d], [regs[s]]] for d, s in recipe["replacement"]]
    out["C"] = cleanup(out)
    return out


def paths(w):
    result = [[f] for f in w["start"]]
    for sec in ("D", "A", "B", "C"):
        for f, d, ss in w[sec]:
            for r in [d] + ss:
                if result[r][-1] != f:
                    result[r].append(f)
    for r, f in enumerate(w["final"]):
        if result[r][-1] != f:
            result[r].append(f)
    return result


def audit(w, module, geometry):
    # Geometry is unchanged; reuse the baseline's already checked exact spaces.
    obj = copy.copy(geometry)
    obj.w = w
    result = obj.full()
    h, c, _ = obj.interface()
    need(all(h.values()) and all(c.values()), "interface H1-H5 or decomposition failed")
    return result


def records_check(directory, word):
    """Independent set-valued interpreter of the actual exported instructions.

    This checks the scalar projection and literal MOVE/COPY/ERASE lifecycle,
    not the multistage formal-column or hosted-recursion contracts.
    """
    raw = (directory / "249-records.bin").read_bytes()
    need(len(raw) % 24 == 0, "truncated record")
    records = list(struct.iter_unpack("<6i", raw))
    dim = {int(k): v["dim"] for k, v in
           json.loads((directory / "frames.json").read_text())["frames"].items()}
    frames = list(word["start"]) + [None]
    values = [{i} for i in range(661)] + [set()]
    pths = [[f] for f in frames[:661]]
    hist, counts = Counter(), Counter()
    for op, a, b, c, d, e in records:
        counts[op] += 1
        if op == 0:
            need(a < 661 and frames[a] == b and dim[c] - dim[b] == d and d > 0,
                 "bad MOVE")
            need(set(word["frames"][b]) <= set(word["frames"][c]), "MOVE not nested")
            frames[a] = c
            pths[a].append(c)
            hist[d] += 1
        elif op == 1:
            need(a != b and c == 1 and frames[a] == frames[b] == d, "bad ADD frame")
            values[a] = values[a].symmetric_difference(values[b])
        elif op == 2:
            need(b == 661 and not values[b] and frames[b] is None and frames[a] == c,
                 "COPY lifecycle")
            need(d == 0 and e == dim[c], "COPY rank")
            values[b] = set(values[a])
            frames[b] = d
            hist[e] += 1
        elif op == 3:
            need(b == 661 and frames[a] == c and frames[b] == d == 0
                 and values[b] == values[a], "ERASE lifecycle")
            values[b] = set()
            frames[b] = None
        else:
            raise Reject("unknown record opcode")
    expected = [{i} if not 111 <= i < 222 else {i, i - 111} for i in range(661)]
    need(values[:661] == expected and not values[661], "record dirty-column endpoint")
    need(frames[:661] == word["final"] and frames[661] is None, "record frame endpoint")
    need(pths == paths(word), "record frame paths differ")
    prefix = []
    for reverse in (False, True):
        norms = [1] * 661 + [0]
        maximum = 1
        opened = False
        for op, a, b, c, d, e in (reversed(records) if reverse else records):
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norms[a] += abs(c) * norms[b]
                maximum = max(maximum, norms[a])
            elif op == 2:
                need(not opened, "prefix COPY lifecycle")
                norms[b], opened = norms[a], True
            elif op == 3:
                need(opened, "prefix ERASE lifecycle")
                norms[b], opened = 0, False
        need(not opened, "prefix open copy")
        prefix.append(maximum)
    payload = 64 * prefix[0] ** 3 * prefix[1] ** 2
    need(payload < 2**104, "native payload cap exceeded")
    return {"records": len(records), "adds": counts[1], "moves": counts[0],
            "copies": counts[2], "erasures": counts[3],
            "paid_histogram": dict(sorted(hist.items())),
            "rank_mass": sum(k * v for k, v in hist.items()),
            "records_sha256": sha(raw), "positive_prefix": prefix,
            "payload_prefix_upper": str(payload), "payload_prefix_bits": payload.bit_length()}


def rejected(label, fn, exceptions):
    try:
        fn()
    except exceptions:
        return label
    raise Reject("negative control accepted: " + label)


def run(output, write_certificate):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    need(pins["execution_inputs"] == EXECUTION_INPUTS, "source pin coverage mismatch")
    for path in pins["execution_inputs"]:
        pin = pins["files"][path]
        need(sha((ROOT / path).read_bytes()) == pin["sha256"], "source hash mismatch: " + path)
    base = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    recipe = json.loads((HERE / "CANDIDATE.json").read_text())
    need(recipe["source_sha256"] == sha((ROOT / WORD).read_bytes()), "candidate source mismatch")
    need(recipe["reverse_dominated"] is True, "candidate dominance claim mismatch")
    factor_report = optimality(recipe)
    revised = build(base, recipe)
    positive = circuit_check(recipe["original"], recipe["replacement"])
    need(positive["forward"]["original"] == positive["forward"]["replacement"],
         "integer forward map changed")
    need(paths(base) == paths(revised), "physical frame path changed")

    spec = importlib.util.spec_from_file_location("predecessor_xcheck_p", ROOT / AUDITOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    geometry, labels, baseline, h, c, _ = module.check(base)
    need(all(h.values()) and all(c.values()), "baseline interface failed")
    revised_audit = audit(revised, module, geometry)

    # Independent exhaustive evaluation of the ten-register Boolean map.
    for bits in range(1024):
        endings = []
        for gates in (recipe["original"], recipe["replacement"]):
            value = bits
            for d, s in gates:
                value ^= ((value >> s) & 1) << d
            endings.append(value)
        need(endings[0] == endings[1], "exhaustive ten-bit map differs")

    evidence = {}
    for name, word in (("original", base), ("replacement", revised)):
        path = output / (name + ".json")
        path.write_text(json.dumps(word, separators=(",", ":")) + "\n")
        directory = output / name
        subprocess.run([sys.executable, "-B", str(ROOT / EXPORTER), str(path), str(directory)],
                       check=True, capture_output=True, text=True)
        evidence[name] = records_check(directory, word)
    a, b = evidence["original"], evidence["replacement"]
    need(a["adds"] == 24305 and b["adds"] == 24295, "unexpected native ADD count")
    for key in ("moves", "copies", "erasures", "paid_histogram", "rank_mass"):
        need(a[key] == b[key], "native cost changed: " + key)
    need(b["rank_mass"] == 5129 and b["copies"] == 9, "incorrect native cost")
    need(all(y <= x for x, y in zip(a["positive_prefix"], b["positive_prefix"])),
         "complete positive prefix increased")

    controls = []
    fail = (Reject, module.Reject)
    for label, mutate in (
        ("understated factor minimum", lambda r: r["factors"][1].update(minimum=15)),
        ("altered distance potential", lambda r: r["factors"][0]["distance"].__setitem__(1, 1)),
        ("missing factor", lambda r: r["factors"].pop()),
    ):
        wrong = copy.deepcopy(recipe)
        mutate(wrong)
        controls.append(rejected(label, lambda: optimality(wrong), fail))
    controls.append(rejected("self addition", lambda: matrix([[0, 0]]), fail))
    controls.append(rejected("boolean register index", lambda: matrix([[True, 0]]), fail))
    controls.append(rejected("drop circuit gate", lambda: circuit_check(
        recipe["original"], recipe["replacement"][1:]), fail))
    wrong = copy.deepcopy(recipe["replacement"])
    wrong[0].reverse()
    controls.append(rejected("reverse circuit operand", lambda: circuit_check(
        recipe["original"], wrong), fail))
    inflated = recipe["replacement"] + [[0, 1], [0, 1]]
    need(matrix(inflated) == matrix(recipe["replacement"]), "inflation control is not F2-neutral")
    controls.append(rejected("F2-neutral positive-cost inflation", lambda: circuit_check(
        recipe["original"], inflated), fail))
    bad = copy.deepcopy(revised)
    bad["C"].pop()
    controls.append(rejected("dropped cleanup", lambda: audit(bad, module, geometry), fail))
    bad = copy.deepcopy(revised)
    bad["C"] = copy.deepcopy(base["C"])
    # Same endpoint but not the literal reverse required by H4.
    obj = copy.copy(geometry)
    obj.w = bad
    obj.full()
    controls.append(rejected("nonliteral original cleanup", lambda: audit(bad, module, geometry), fail))
    bad = copy.deepcopy(revised)
    bad["B"][128][0] = 0
    controls.append(rejected("illegal lower frame", lambda: audit(bad, module, geometry), fail))
    bad = copy.deepcopy(revised)
    bad["D"][0][2].pop()
    controls.append(rejected("missing dirty compensation", lambda: audit(bad, module, geometry), fail))

    # The record endpoint checker must see literal instruction corruption too.
    directory = output / "replacement"
    rawpath = directory / "249-records.bin"
    raw = rawpath.read_bytes()
    recs = list(struct.iter_unpack("<6i", raw))
    for i, rec in enumerate(recs):
        if rec[0] == 1 and rec[5] == 4 and rec[4] == 507:
            rawpath.write_bytes(raw[:24*i] + raw[24*(i+1):])
            break
    else:
        raise Reject("negative control has no exported block ADD to remove")
    try:
        controls.append(rejected("dropped exported block ADD", lambda: records_check(directory, revised), fail))
    finally:
        rawpath.write_bytes(raw)

    cert = {"status": "PASS_R439_BLOCK1_SCHEDULE", "block": 1, "old_gates": 35, "new_gates": 30,
            "saved_with_cleanup": 10, "labels": labels, "columns": revised_audit["columns"],
            "old_phase_gates": baseline["gates"], "new_phase_gates": revised_audit["gates"],
            "boolean_inputs": 1024, "F2_matrix": matrix(recipe["replacement"]),
            "positive_matrices": positive, "native_records": evidence,
            "factor_optimality": factor_report,
            "reconstructed_word_sha256": sha(canonical(revised)), "controls_rejected": controls,
            "kappa_claim": "none; unchanged paid rank profile, no hosted replay"}
    path = HERE / "CERTIFICATE.json"
    if write_certificate:
        path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(cert) == canonical(json.loads(path.read_text())), "certificate mismatch")
    print("PASS_R439_BLOCK1_SCHEDULE gates=35->30 native_adds=24305->24295 columns=661 rank_mass=5129 controls=" + str(len(controls)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new directory for reconstructed word and records")
    parser.add_argument("--write-certificate", action="store_true", help="regenerate this package's certificate")
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve(), args.write_certificate)
    else:
        with tempfile.TemporaryDirectory(prefix="r439-block1-") as temporary:
            run(Path(temporary), args.write_certificate)


if __name__ == "__main__":
    main()
