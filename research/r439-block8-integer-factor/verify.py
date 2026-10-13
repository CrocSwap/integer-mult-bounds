"""Exact finite R439 block-8 substitution; no new rate claim.

Adapted from mtpsl PR691 quad verifier by @zeusinsight with substantial
OpenAI Codex assistance. Apache-2.0; see README.md for predecessor credit.
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
    for j in range(12):
        values = [int(i == j) for i in range(12)]
        for d, s in ops:
            need(type(d) is int and type(s) is int and 0 <= d < 12 and
                 0 <= s < 12 and d != s, "invalid circuit gate")
            values[d] = values[d] + values[s] if positive else values[d] ^ values[s]
        cols.append(values)
    return [list(r) for r in zip(*cols)]


def circuit_check(old, new):
    need(matrix(old) == matrix(new), "circuit F2 map changed")
    need(matrix(old, True) == matrix(new, True), "forward integer map changed")
    return {direction: {"original": matrix(a, True), "replacement": matrix(b, True)}
            for direction, a, b in (("forward", old, new), ("reverse", old[::-1], new[::-1]))}


def cleanup(w):
    return [[1, d, list(ss)] for _, d, ss in reversed(w["A"] + w["B"])
            if not 111 <= d < 222]


def build(base, recipe):
    need((recipe["phase"], recipe["start"], recipe["stop"], recipe["frame"])
         == ("B", 404, 449, 523), "unexpected circuit location")
    regs = recipe["registers"]
    need(regs == [2, 4, 14, 16, 18, 20, 88, 90, 93, 95, 103, 109],
         "unexpected circuit registers")
    original = [[523, regs[d], [regs[s]]] for d, s in recipe["original"]]
    need(base["B"][404:449] == original, "original gate slice mismatch")
    circuit_check(recipe["original"], recipe["replacement"])
    out = copy.deepcopy(base)
    out["B"][404:449] = [[523, regs[d], [regs[s]]] for d, s in recipe["replacement"]]
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
    bounds = prefix_bounds(records)
    return {"prefix": bounds, "records": len(records), "adds": counts[1], "moves": counts[0],
            "copies": counts[2], "erasures": counts[3],
            "paid_histogram": dict(sorted(hist.items())),
            "rank_mass": sum(k * v for k, v in hist.items()),
            "records_sha256": sha(raw)}


def prefix_bounds(records):
    """Exact cancellation-free scalar envelope, same formula as columns_h.cpp."""
    peaks = []
    for reverse in (False, True):
        values, peak, opened = [1] * 662, 1, False
        for op, a, b, c, d, e in (reversed(records) if reverse else records):
            if op == 0:
                continue
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                values[a] += abs(c) * values[b]
                peak = max(peak, values[a])
            elif op == 2:
                need(not opened, "nested prefix copy")
                values[b], opened = values[a], True
            elif op == 3:
                need(opened, "unmatched prefix erase")
                values[b], opened = 0, False
            else:
                raise Reject("unknown prefix opcode")
        need(not opened, "unclosed prefix copy")
        peaks.append(peak)
    payload = 64 * peaks[0] ** 3 * peaks[1] ** 2
    need(payload < 2 ** 104, "payload exceeds existing 104-bit cap")
    return {"forward": peaks[0], "reverse": peaks[1], "payload": str(payload),
            "payload_bits": payload.bit_length(), "cap_bits": 104}


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

    # Independent exhaustive evaluation of the twelve-register Boolean map.
    for bits in range(4096):
        endings = []
        for gates in (recipe["original"], recipe["replacement"]):
            value = bits
            for d, s in gates:
                value ^= ((value >> s) & 1) << d
            endings.append(value)
        need(endings[0] == endings[1], "exhaustive twelve-bit map differs")

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
    bad["B"][404][0] = 0
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
        if rec[0] == 1 and rec[5] == 4 and rec[4] == 523:
            rawpath.write_bytes(raw[:24*i] + raw[24*(i+1):])
            break
    try:
        controls.append(rejected("dropped exported block ADD", lambda: records_check(directory, revised), fail))
    finally:
        rawpath.write_bytes(raw)

    need(a["prefix"]["payload_bits"] == 93 and b["prefix"]["payload_bits"] == 94,
         "unexpected prefix tradeoff")
    overflow = [(1, 0, 1, 1, 0, 0), (1, 1, 0, 1, 0, 0)] * 50
    controls.append(rejected("payload overflow", lambda: prefix_bounds(overflow), fail))
    wrong = copy.deepcopy(recipe)
    wrong["registers"][0] = 3
    controls.append(rejected("wrong source register", lambda: build(base, wrong), fail))
    cert = {"status": "PASS_R439_BLOCK8_INTEGER_FACTOR", "block": 8,
            "old_gates": 45, "new_gates": 40, "saved_with_cleanup": 10,
            "labels": labels, "columns": revised_audit["columns"],
            "old_phase_gates": baseline["gates"], "new_phase_gates": revised_audit["gates"],
            "boolean_inputs": 4096, "F2_matrix": matrix(recipe["replacement"]),
            "positive_matrices": positive, "native_records": evidence,
            "reconstructed_word_sha256": sha(canonical(revised)), "controls_rejected": controls,
            "kappa_claim": "none; unchanged paid rank profile, no hosted replay"}
    path = HERE / "CERTIFICATE.json"
    if write_certificate:
        path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(cert) == canonical(json.loads(path.read_text())), "certificate mismatch")
    print("PASS_R439_BLOCK8_INTEGER_FACTOR gates=45->40 native_adds=24305->24295 "
          "columns=661 rank_mass=5129 payload_bits=93->94 controls=10")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new directory for reconstructed word and records")
    parser.add_argument("--write-certificate", action="store_true", help="regenerate this package's certificate")
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve(), args.write_certificate)
    else:
        with tempfile.TemporaryDirectory(prefix="r439-block8-") as temporary:
            run(Path(temporary), args.write_certificate)


if __name__ == "__main__":
    main()
