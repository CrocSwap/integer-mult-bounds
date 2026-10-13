"""Exact finite quad replacement and native-word checks; no new rate claim.

Prepared for mtpsl with substantial OpenAI Codex assistance, Apache-2.0.
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
WORD = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
AUDITOR = "research/e8-bit-r420/code/xcheck.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"


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
    for j in range(6):
        values = [int(i == j) for i in range(6)]
        for d, s in ops:
            need(type(d) is int and type(s) is int and 0 <= d < 6 and
                 0 <= s < 6 and d != s, "invalid circuit gate")
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


def cleanup(w):
    return [[1, d, list(ss)] for _, d, ss in reversed(w["A"] + w["B"])
            if not 120 <= d < 240]


def build(base, recipe):
    need((recipe["phase"], recipe["start"], recipe["stop"], recipe["frame"], recipe["quad"])
         == ("A", 873, 892, 315, 13), "unexpected circuit location")
    regs = recipe["registers"]
    need(regs == [267, 347, 349, 376, 467, 491], "unexpected circuit registers")
    original = [[315, regs[d], [regs[s]]] for d, s in recipe["original"]]
    need(base["A"][873:892] == original, "original gate slice mismatch")
    circuit_check(recipe["original"], recipe["replacement"])
    out = copy.deepcopy(base)
    out["A"][873:892] = [[315, regs[d], [regs[s]]] for d, s in recipe["replacement"]]
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
    values = [{i} for i in range(660)] + [set()]
    pths = [[f] for f in frames[:660]]
    hist, counts = Counter(), Counter()
    for op, a, b, c, d, e in records:
        counts[op] += 1
        if op == 0:
            need(a < 660 and frames[a] == b and dim[c] - dim[b] == d and d > 0,
                 "bad MOVE")
            need(set(word["frames"][b]) <= set(word["frames"][c]), "MOVE not nested")
            frames[a] = c
            pths[a].append(c)
            hist[d] += 1
        elif op == 1:
            need(a != b and c == 1 and frames[a] == frames[b] == d, "bad ADD frame")
            values[a] = values[a].symmetric_difference(values[b])
        elif op == 2:
            need(b == 660 and not values[b] and frames[b] is None and frames[a] == c,
                 "COPY lifecycle")
            need(d == 0 and e == dim[c], "COPY rank")
            values[b] = set(values[a])
            frames[b] = d
            hist[e] += 1
        elif op == 3:
            need(b == 660 and frames[a] == c and frames[b] == d == 0
                 and values[b] == values[a], "ERASE lifecycle")
            values[b] = set()
            frames[b] = None
        else:
            raise Reject("unknown record opcode")
    expected = [{i} if not 120 <= i < 240 else {i, i - 120} for i in range(660)]
    need(values[:660] == expected and not values[660], "record dirty-column endpoint")
    need(frames[:660] == word["final"] and frames[660] is None, "record frame endpoint")
    need(pths == paths(word), "record frame paths differ")
    return {"records": len(records), "adds": counts[1], "moves": counts[0],
            "copies": counts[2], "erasures": counts[3],
            "paid_histogram": dict(sorted(hist.items())),
            "rank_mass": sum(k * v for k, v in hist.items()),
            "records_sha256": sha(raw)}


def rejected(label, fn, exceptions):
    try:
        fn()
    except exceptions:
        return label
    raise Reject("negative control accepted: " + label)


def run(output, write_certificate):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path in pins["execution_inputs"]:
        pin = pins["files"][path]
        need(sha((ROOT / path).read_bytes()) == pin["sha256"], "source hash mismatch: " + path)
    base = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    recipe = json.loads((HERE / "WITNESS.json").read_text())
    revised = build(base, recipe)
    positive = circuit_check(recipe["original"], recipe["replacement"])
    need(positive["forward"]["original"] == positive["forward"]["replacement"],
         "integer forward map changed")
    need(paths(base) == paths(revised), "physical frame path changed")

    spec = importlib.util.spec_from_file_location("predecessor_xcheck", ROOT / AUDITOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    geometry, labels, baseline, h, c, _ = module.check(base)
    need(all(h.values()) and all(c.values()), "baseline interface failed")
    revised_audit = audit(revised, module, geometry)

    # Independent exhaustive evaluation of the six-register Boolean map.
    for bits in range(64):
        endings = []
        for gates in (recipe["original"], recipe["replacement"]):
            value = bits
            for d, s in gates:
                value ^= ((value >> s) & 1) << d
            endings.append(value)
        need(endings[0] == endings[1], "exhaustive six-bit map differs")

    evidence = {}
    for name, word in (("original", base), ("replacement", revised)):
        path = output / (name + ".json")
        path.write_text(json.dumps(word, separators=(",", ":")) + "\n")
        directory = output / name
        subprocess.run([sys.executable, "-B", str(ROOT / EXPORTER), str(path), str(directory)],
                       check=True, capture_output=True, text=True)
        evidence[name] = records_check(directory, word)
    a, b = evidence["original"], evidence["replacement"]
    need(a["adds"] == 26916 and b["adds"] == 26902, "unexpected native ADD count")
    for key in ("moves", "copies", "erasures", "paid_histogram", "rank_mass"):
        need(a[key] == b[key], "native cost changed: " + key)
    need(b["rank_mass"] == 5112 and b["copies"] == 9, "incorrect native cost")

    controls = []
    fail = (Reject, module.Reject)
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
    bad["A"][873][0] = 0
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
        if rec[0] == 1 and rec[5] == 2 and rec[4] == 315:
            rawpath.write_bytes(raw[:24*i] + raw[24*(i+1):])
            break
    try:
        controls.append(rejected("dropped exported quad ADD", lambda: records_check(directory, revised), fail))
    finally:
        rawpath.write_bytes(raw)

    cert = {"status": "PASS_R420_QUAD13", "quad": 13, "old_gates": 19, "new_gates": 12,
            "saved_with_cleanup": 14, "labels": labels, "columns": revised_audit["columns"],
            "old_phase_gates": baseline["gates"], "new_phase_gates": revised_audit["gates"],
            "boolean_inputs": 64, "F2_matrix": matrix(recipe["replacement"]),
            "positive_matrices": positive, "native_records": evidence,
            "reconstructed_word_sha256": sha(canonical(revised)), "controls_rejected": controls,
            "kappa_claim": "none; unchanged paid rank profile, no hosted replay"}
    path = HERE / "CERTIFICATE.json"
    if write_certificate:
        path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(cert) == canonical(json.loads(path.read_text())), "certificate mismatch")
    print("PASS_R420_QUAD13 gates=19->12 native_adds=26916->26902 columns=660 rank_mass=5112 controls=8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new directory for reconstructed word and records")
    parser.add_argument("--write-certificate", action="store_true", help="regenerate this package's certificate")
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve(), args.write_certificate)
    else:
        with tempfile.TemporaryDirectory(prefix="r420-quad13-") as temporary:
            run(Path(temporary), args.write_certificate)


if __name__ == "__main__":
    main()
