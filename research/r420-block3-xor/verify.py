"""Verify the frozen block-3 circuit, without running the nomination search.

Prepared for yongjae321 with substantial OpenAI Codex assistance; Apache-2.0.
The inherited source word is read-only; each export uses a fresh directory.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import uuid

# Imported predecessor packages are immutable evidence, including their inventory.
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
REGISTERS = [21, 29, 37, 45, 53, 62, 71, 73, 81, 89, 97, 105]
START, STOP, FRAME = 263, 313, 545


class Reject(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_pins():
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    need(pins["base_commit"] == BASE, "wrong base pin")
    for name, entry in pins["files"].items():
        raw = (ROOT / name).read_bytes()
        if entry["encoding"] == "LF-normalized text":
            raw = raw.replace(b"\r\n", b"\n")
        need(digest(raw) == entry["sha256"], "source pin mismatch: " + name)
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == entry["git_blob"], "source Git blob mismatch: " + name)
    return pins


def load_checker():
    path = ROOT / "research/e8-bit-r420/code/xcheck.py"
    spec = importlib.util.spec_from_file_location("pinned_r420_xcheck", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def validate_ops(ops):
    need(isinstance(ops, list) and ops, "empty or malformed operations")
    for pair in ops:
        need(isinstance(pair, list) and len(pair) == 2, "not a binary XOR")
        need(all(type(x) is int and 0 <= x < 12 for x in pair), "operand outside original registers")
        need(pair[0] != pair[1], "self XOR is not invertible")


def matrix(ops, positive=False):
    rows = [[int(i == j) for j in range(12)] for i in range(12)]
    for a, b in ops:
        rows[a] = [x + y if positive else x ^ y for x, y in zip(rows[a], rows[b])]
    return rows


def no_worse(old, new):
    return all(b <= a for ra, rb in zip(old, new) for a, b in zip(ra, rb))


def local_check(w, candidate):
    need(candidate["schema"] == "r420-block3-xor-candidate/1", "candidate schema")
    need(candidate["source_sha256"] == digest(SOURCE.read_bytes()), "candidate source pin")
    need(candidate["source_path"] == SOURCE.relative_to(ROOT).as_posix(), "candidate source path")
    need((candidate["block_index"], candidate["b_start"], candidate["b_stop"], candidate["frame"])
         == (3, START, STOP, FRAME), "candidate changed the claimed block")
    need(candidate["registers"] == REGISTERS, "candidate changed physical register assignment")
    old, new = candidate["original_local_ops"], candidate["replacement_local_ops"]
    validate_ops(old)
    validate_ops(new)
    baseline = [[FRAME, REGISTERS[a], [REGISTERS[b]]] for a, b in old]
    need(w["B"][START:STOP] == baseline, "baseline circuit differs from the pinned word")
    need(len(old) == candidate["original_gate_count"] == 50, "original gate count")
    need(len(new) == candidate["replacement_gate_count"] < len(old), "replacement must save gates")
    old_map, new_map = matrix(old), matrix(new)
    need(old_map == new_map, "different exact F2 block map")
    rows = [sum(value << j for j, value in enumerate(row)) for row in new_map]
    need(rows == candidate["endpoint_rows"], "endpoint certificate mismatch")
    transfers = {}
    for key, ops0, ops1 in (("forward", old, new), ("reverse", old[::-1], new[::-1])):
        before, after = matrix(ops0, True), matrix(ops1, True)
        need(no_worse(before, after), key + " nonnegative transfer increased")
        transfers[key] = {"original": before, "replacement": after}
    return transfers


def rebuild(w, candidate):
    revised = deepcopy(w)
    revised["B"][START:STOP] = [[FRAME, REGISTERS[a], [REGISTERS[b]]]
                                  for a, b in candidate["replacement_local_ops"]]
    # Full frame is identified from the source's final frame for source register 0.
    full = w["final"][0]
    v = w["v"]
    revised["C"] = [[full, d, list(src)] for _, d, src in reversed(revised["A"] + revised["B"])
                    if not v <= d < 2 * v]
    return revised


def frame_accounting(w, geometry):
    paths = [[f] for f in w["start"]]
    hist = Counter()

    def move(r, f):
        old = paths[r][-1]
        if f != old:
            need(geometry.nested(old, f), "frame not nested")
            step = geometry.fdim[f] - geometry.fdim[old]
            need(step > 0, "nonpositive climb")
            hist[step] += 1
            paths[r].append(f)

    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            for r in w["ret"]:
                hist[geometry.fdim[paths[r][-1]]] += 1
        else:
            for f, d, src in w[section]:
                for r in [d] + src:
                    move(r, f)
    for r, f in enumerate(w["final"]):
        move(r, f)
    return paths, {str(k): v for k, v in sorted(hist.items())}


def scalar_stream(w):
    # Matches the scalar recipe of pinned export_records.py; COPY has a separate
    # temporary register, its source is held immutable until ERASE.
    temp = 2 * w["v"] + w["R"]
    stream = []
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            for k, q in enumerate(w["ret"]):
                stream.append(("copy", temp, q))
                for t, row in enumerate(w["scatter"]):
                    if k in row:
                        stream.append(("add", w["v"] + t, temp))
                stream.append(("erase", temp, q))
        else:
            for _, d, src in w[section]:
                stream.extend(("add", d, s) for s in src)
    return stream


def prefix_bill(w):
    stream = scalar_stream(w)
    n = 2 * w["v"] + w["R"]
    answer = {}
    for reverse in (False, True):
        weights = [1] * (n + 1)
        largest, opened = 1, False
        for op, d, s in (reversed(stream) if reverse else stream):
            if reverse and op != "add":
                op = "erase" if op == "copy" else "copy"
            if op == "add":
                weights[d] += weights[s]
                largest = max(largest, weights[d])
            elif op == "copy":
                need(not opened, "overlapping temporary copy")
                opened = True
                weights[d] = weights[s]
            else:
                need(opened, "erase without temporary copy")
                opened = False
                weights[d] = 0
        need(not opened, "unclosed temporary copy")
        answer["reverse" if reverse else "forward"] = largest
    payload = 64 * answer["forward"] ** 3 * answer["reverse"] ** 2
    answer.update(payload_upper=payload, payload_bits=payload.bit_length(),
                  scalar_additions=sum(op == "add" for op, _, _ in stream))
    need(payload < 2 ** 104, "local cohort prefix allowance exceeded")
    return answer


def require_full(checker, word):
    geometry = checker.Word(word)
    full = geometry.full()
    hypotheses, conclusion, info = geometry.interface()
    need(all(hypotheses.values()), "interleaved interface hypotheses failed")
    need(all(conclusion.values()), "interleaved interface conclusion failed")
    return geometry, full, hypotheses, conclusion


def negative_controls(checker, w, candidate, revised):
    passed = []

    def rejects(name, action):
        try:
            action()
        except (Reject, checker.Reject):
            passed.append(name)
        else:
            raise Reject("negative control was accepted: " + name)

    bad = deepcopy(candidate)
    bad["source_sha256"] = "0" * 64
    rejects("wrong source fingerprint", lambda: local_check(w, bad))
    bad = deepcopy(candidate)
    bad["replacement_local_ops"][0][1] = 12
    rejects("new register outside the claimed interface", lambda: local_check(w, bad))
    bad = deepcopy(candidate)
    bad["replacement_local_ops"][0][1] = bad["replacement_local_ops"][0][0]
    rejects("singular self XOR", lambda: local_check(w, bad))
    bad = deepcopy(candidate)
    bad["endpoint_rows"][0] ^= 1
    rejects("incorrect endpoint certificate", lambda: local_check(w, bad))
    bad = deepcopy(candidate)
    bad["replacement_local_ops"].pop()
    bad["replacement_gate_count"] -= 1
    rejects("dropped gate changes the F2 map", lambda: local_check(w, bad))
    # Rebuild the matching reverse as well: restoration alone cannot detect this.
    corrupt = rebuild(w, bad)
    rejects("changed B map with matching cleanup", lambda: require_full(checker, corrupt))
    corrupt = deepcopy(revised)
    corrupt["C"] = deepcopy(w["C"])
    # This remains F2-correct, but violates the inherited literal-reversal H4.
    checker.Word(corrupt).full()
    rejects("F2-correct old cleanup violates literal-reversal H4", lambda: require_full(checker, corrupt))
    corrupt = deepcopy(revised)
    corrupt["B"][START][0] = w["start"][REGISTERS[candidate["replacement_local_ops"][0][0]]]
    rejects("illegal line frame for a block gate", lambda: require_full(checker, corrupt))
    corrupt = deepcopy(revised)
    corrupt["D"][0][2].pop()
    rejects("missing dirty-helper compensation", lambda: require_full(checker, corrupt))
    bad = deepcopy(candidate)
    # Even repetition is F2-neutral and stays below 50 gates, but grows the
    # positive matrix beyond the baseline. This catches a parity-only verifier.
    bad["replacement_local_ops"] += [[0, 1]] * 16
    bad["replacement_gate_count"] += 16
    need(matrix(bad["replacement_local_ops"]) == matrix(candidate["replacement_local_ops"]),
         "nonnegative control is not F2-neutral")
    rejects("F2-neutral repeated gates increase the positive bill", lambda: local_check(w, bad))
    return passed


def verify():
    source_pins()
    w = json.loads(gzip.decompress(SOURCE.read_bytes()))
    candidate = json.loads((HERE / "candidate.json").read_text(encoding="utf-8"))
    transfers = local_check(w, candidate)
    revised = rebuild(w, candidate)
    checker = load_checker()
    # Labels/frames are identical; validate the shared exact geometry once.
    base_geometry, base_full, _, _ = require_full(checker, w)
    labels = base_geometry.labels()
    new_geometry, new_full, hypotheses, conclusion = require_full(checker, revised)
    old_paths, old_hist = frame_accounting(w, base_geometry)
    new_paths, new_hist = frame_accounting(revised, new_geometry)
    need(old_paths == new_paths, "per-register physical frame paths changed")
    need(old_hist == new_hist == {"1": 1320, "2": 1440, "4": 60, "5": 120, "8": 9},
         "paid rank profile changed")
    old_bill, new_bill = prefix_bill(w), prefix_bill(revised)
    need(new_bill["forward"] <= old_bill["forward"] and new_bill["reverse"] <= old_bill["reverse"],
         "whole local prefix bill increased")
    controls = negative_controls(checker, w, candidate, revised)
    import independent
    audit = independent.audit(w, candidate, supplied_word=revised)
    for key, bill in (("baseline", old_bill), ("candidate", new_bill)):
        independent_bill = audit["exported_local_scalar_prefix"][key]
        need(all(bill[k] == independent_bill[k] for k in ("forward", "reverse", "scalar_additions")),
             "independent prefix engine disagrees")
        need(bill["payload_upper"] == independent_bill["payload_prefix_upper"], "independent payload disagrees")
    need(audit["paid_frame_profile"]["per_register_frame_paths_sha256"] == digest(canonical(old_paths)),
         "independent frame paths disagree")
    receipt = json.loads((ROOT / "research/community-family588-audit/pr543/cout/columns_k4.json").read_text())
    for entry in receipt["signed_lift_prefix"]:
        key = "reverse" if entry["reverse"] else "forward"
        need(old_bill[key] == int(entry["cancellation_free_signed_row_l1_upper"]),
             "baseline differs from archived official prefix receipt")
    need(old_bill["payload_upper"] == int(receipt["payload_prefix_upper"]) and
         old_bill["scalar_additions"] == receipt["local_scalar_additions"], "baseline official receipt mismatch")
    result = dict(schema="r420-block3-xor-verification/1", base_commit=BASE,
                  source_sha256=digest(SOURCE.read_bytes()),
                  candidate_sha256=digest(canonical(candidate)),
                  revised_content_sha256=digest(canonical(revised)),
                  block={"index": 3, "frame": FRAME, "registers": REGISTERS,
                         "original_gates": STOP - START,
                         "replacement_gates": len(candidate["replacement_local_ops"])},
                  positive_transfer_matrices=transfers, labels=labels,
                  original_gates=base_full["gates"], replacement_gates=new_full["gates"],
                  symbolic_columns=new_full["columns"], hypotheses=hypotheses,
                  conclusion=conclusion, frame_paths_equal=True,
                  frame_paths_sha256=digest(canonical(old_paths)),
                  local_histogram=new_hist,
                  rank_mass=sum(int(k) * v for k, v in new_hist.items()),
                  original_prefix_bill=old_bill, replacement_prefix_bill=new_bill,
                  negative_controls=controls, independent=audit,
                  scope="Finite local circuit improvement; no new kappa, paid supplier or global optimality claim")
    return json.loads(canonical(result)), revised


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="fresh output directory (existing paths are refused)")
    args = parser.parse_args()
    output = args.output or ROOT / "build" / ("r420-block3-xor-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                                             + "-" + uuid.uuid4().hex[:8])
    need(not output.exists(), "output already exists; choose a fresh directory")
    result, revised = verify()
    expected = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(result == expected, "computed evidence differs from CERTIFICATE.json")
    output.mkdir(parents=True, exist_ok=False)
    with (output / "word.json.gz").open("xb") as stream:
        stream.write(gzip.compress(canonical(revised), mtime=0))
    report = dict(result=result, environment={"python": platform.python_version(),
                                              "platform": platform.platform()})
    with (output / "verification.json").open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print("Output:", output.resolve())
    print("PASS_R420_BLOCK3_XOR gates=50->33 saved_with_cleanup=34 columns=660 rank_mass=5112 controls="
          + str(len(result["negative_controls"])))


if __name__ == "__main__":
    try:
        main()
    except (Reject, OSError, KeyError, ValueError) as error:
        print("REJECT:", error, file=sys.stderr)
        sys.exit(1)
