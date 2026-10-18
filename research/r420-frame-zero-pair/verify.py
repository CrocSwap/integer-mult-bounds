#!/usr/bin/env python3
# Mikhail R. Gadelha, with substantial OpenAI Codex assistance; Apache-2.0.
"""A paid, restored helper-pair factorization of PR543's frame-zero D circuit."""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import importlib.util
from itertools import combinations
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
XCHECK = ROOT / "research/e8-bit-r420/code/xcheck.py"
BIT = ROOT / "research/e8-bit-carrier-skeleton/code/bit"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def pair_census(word):
    v, n = word["v"], 2 * word["v"] + word["R"]
    counts = Counter()
    need(len({g[1] for g in word["D"]}) == len(word["D"]), "baseline D repeats a target")
    for frame, dst, sources in word["D"]:
        need(word["frames"][frame] == [] and v <= dst < 2 * v,
             "baseline D must write targets at frame zero")
        need(len(set(sources)) == len(sources) and all(2 * v <= s < n for s in sources),
             "baseline D must have distinct helper sources")
        counts.update(combinations(sorted(sources), 2))
    domain = list(combinations(range(2 * v, n), 2))
    # Independent column-incidence census, including all zero-support pairs.
    columns = {s: sum(1 << i for i, g in enumerate(word["D"]) if s in g[2])
               for s in range(2 * v, n)}
    need(all(counts[(a, b)] == (columns[a] & columns[b]).bit_count() for a, b in domain),
         "pair and incidence-column censuses differ")
    best = min(domain, key=lambda p: (-counts[p], p))
    return best, counts[best], Counter(counts[p] for p in domain)


def factor(word, pair):
    """Run unaffected terms first; prepare a+b, share it, then restore a."""
    a, b = pair
    need(a != b and all(2 * word["v"] <= r < 2 * word["v"] + word["R"] for r in pair),
         "pair must contain distinct helpers")
    zero = word["frames"].index([])
    residual, targets = [], []
    for frame, dst, sources in word["D"]:
        shared = a in sources and b in sources
        rest = [s for s in sources if not shared or s not in pair]
        if rest:
            residual.append([frame, dst, rest])
        if shared:
            targets.append(dst)
    result = deepcopy(word)
    result["D"] = residual + [[zero, a, [b]]] + [
        [zero, dst, [a]] for dst in targets
    ] + [[zero, a, [b]]]
    return result, targets


def d_map(word):
    """Separate set-valued interpreter: each set lists symbolic input columns."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    values = [{r} for r in range(n)]
    for frame, dst, sources in word["D"]:
        need(word["frames"][frame] == [], "D gate off frame zero")
        need(v <= dst < n and sources and len(set([dst] + sources)) == len(sources) + 1,
             "invalid D destination or operands")
        need(all(2 * v <= s < n for s in sources), "D may read only helpers")
        for source in sources:
            values[dst].symmetric_difference_update(values[source])
    return values


def check_d(original, candidate):
    need(d_map(candidate) == d_map(original), "D map differs, including dirty-helper restoration")


def record_metrics(records, n, reverse=False):
    """Independent exact F2 and nonnegative prefix interpreter, with COPY/ERASE."""
    values = [1 << r for r in range(n)] + [0]
    norms = [1] * (n + 1)
    largest = 1
    open_center = None
    adds = copies = 0
    histogram = Counter()
    stream = reversed(records) if reverse else records
    for opcode, a, b, coefficient, frame, rank in stream:
        if opcode == 0:
            if frame:
                histogram[frame] += 1
            continue
        if reverse and opcode in (2, 3):
            opcode = 5 - opcode
        if opcode == 1:
            need(0 <= a < n and 0 <= b <= n and a != b, "bad scalar record")
            need(b != n or open_center is not None, "read of closed copy")
            need(a != open_center, "write to copied center")
            if coefficient & 1:
                values[a] ^= values[b]
            norms[a] += abs(coefficient) * norms[b]
            largest = max(largest, norms[a])
            adds += 1
        elif opcode == 2:
            need(open_center is None and b == n, "bad copy opening")
            open_center = a
            values[n], norms[n] = values[a], norms[a]
            copies += 1
            if not reverse:
                histogram[rank] += 1
        elif opcode == 3:
            need(open_center == a and b == n, "bad copy closing")
            values[n] = norms[n] = 0
            open_center = None
        else:
            raise ValueError("unknown record opcode")
    need(open_center is None and values[n] == 0, "unclosed copy")
    return values[:n], largest, adds, copies, dict(sorted(histogram.items()))


def export(word, directory):
    directory.mkdir()
    path = directory / "word.json"
    path.write_bytes(canonical(word))
    subprocess.run([sys.executable, "-I", "-B", str(BIT / "export_records.py"),
                    str(path), str(directory)], check=True, capture_output=True, text=True)
    return list(struct.iter_unpack("<6i", (directory / "249-records.bin").read_bytes()))


def inspect_records(word, records):
    v, n = word["v"], 2 * word["v"] + word["R"]
    expected = [(1 << r) ^ (1 << (r - v) if v <= r < 2 * v else 0) for r in range(n)]
    forward = record_metrics(records, n)
    reverse = record_metrics(records, n, reverse=True)
    need(forward[0] == reverse[0] == expected, "record endpoint is not the restored shear")
    need(forward[2:4] == reverse[2:4] and forward[3] == 9, "record counts differ")
    payload = 64 * forward[1] ** 3 * reverse[1] ** 2
    need(payload < 1 << 104, "native five-stage payload exceeds inherited 104-bit allowance")
    return dict(records=len(records), scalar_adds=forward[2], copies=forward[3],
                histogram=forward[4], rank_mass=sum(k * c for k, c in forward[4].items()),
                forward_prefix=forward[1], reverse_prefix=reverse[1],
                payload=str(payload), payload_bits=payload.bit_length())


def rejected(name, original, candidate):
    try:
        check_d(original, candidate)
    except ValueError as error:
        return {"name": name, "reason": str(error)}
    raise ValueError("control was accepted: " + name)


def run(command, log):
    result = subprocess.run([str(x) for x in command], capture_output=True, text=True)
    log.write_text(result.stdout + result.stderr)
    need(result.returncode == 0, "command failed: " + " ".join(map(str, command)) + "\n" + result.stderr)


def cohort_check(output, metrics):
    """Unmodified predecessor C++ legality, nine-stage columns and prefix bill."""
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    checkers = BIT / "checkers"
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=120", "-DRHELP=420",
             "-DKPAIRS=4", "-I" + str(checkers)]
    if os.environ.get("BOOST_INCLUDE"):
        flags.append("-I" + os.environ["BOOST_INCLUDE"])
    for name, source in (("columns", "columns_k.cpp"), ("legality", "legality_h.cpp")):
        run(compiler + flags + ["-o", str(output / name), str(checkers / source)],
            output / (name + "-compile.log"))
    receipts = {}
    for name in ("baseline", "candidate"):
        directory = output / name
        cin, cout = directory / "cin", directory / "cout"
        run([sys.executable, "-I", "-B", BIT / "regression/stage_cohort.py",
             directory, directory, cin, cout], directory / "stage.log")
        run([output / "legality", cin, cout, directory / "legality.json"], directory / "legality.log")
        run([output / "columns", directory / "249-records.bin", directory / "columns.json"],
            directory / "columns.log")
        legality = json.loads((directory / "legality.json").read_text())
        columns = json.loads((directory / "columns.json").read_text())
        need(legality["common_frame_ADDs"] == columns["local_scalar_additions"] == metrics[name]["scalar_adds"],
             "C++ scalar counts differ")
        need(legality["rank_mass"] == metrics[name]["rank_mass"] == 5112, "C++ rank mass differs")
        need(legality["records"] == metrics[name]["records"] and legality["copies"] == legality["erasures"] == 9,
             "C++ record or copy counts differ")
        need(dict(legality["paid_histogram"]) == metrics[name]["histogram"],
             "C++ paid histogram differs")
        need([int(r["cancellation_free_signed_row_l1_upper"]) for r in columns["signed_lift_prefix"]]
             == [metrics[name]["forward_prefix"], metrics[name]["reverse_prefix"]], "C++ prefix differs")
        need(columns["payload_prefix_upper"] == metrics[name]["payload"], "C++ payload differs")
        need(columns["formal_columns_checked"] == 1380 and len(columns["stages"]) == 9,
             "nine-stage coverage changed")
        need(len(columns["negative_controls"]) == 18 and all(c["rejected"] for c in columns["negative_controls"]),
             "omitted-bridge controls changed")
        receipts[name] = dict(formal_columns=1380, stages=9, bridge_controls=18,
                              legality_status=legality["status"], column_status=columns["status"])
    # Scalar-neutral but bill-inflating control: alternating repeated dirty-helper echoes.
    # It must fail at the positive-prefix guard, not at the F2 endpoint check.
    directory = output / "candidate"
    records = (directory / "249-records.bin").read_bytes()
    echo = b"".join(struct.pack("<6i", 1, a, b, 1, 0, 1)
                    for _ in range(48) for a, b in ((552, 521), (521, 552)))
    echo_inverse = b"".join(echo[i:i + 24] for i in range(len(echo) - 24, -1, -24))
    inflated = output / "inflated.bin"
    inflated.write_bytes(echo + echo_inverse + records)
    inflated_records = list(struct.iter_unpack("<6i", inflated.read_bytes()))
    original_records = list(struct.iter_unpack("<6i", records))
    need(record_metrics(inflated_records, 660)[0] == record_metrics(original_records, 660)[0],
         "prefix-inflation control must preserve every F2 column")
    result = subprocess.run([str(output / "columns"), str(inflated), str(output / "inflated.json")],
                            capture_output=True, text=True)
    need(result.returncode != 0 and "payloadfiniteprefix2^104" in result.stderr,
         "F2-neutral positive-prefix inflation control did not fail at its bill")
    return receipts


def verify(output):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for relative, digest in pins["sha256"].items():
        need(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, "source pin mismatch: " + relative)
    with gzip.open(SOURCE, "rt") as source:
        original = json.load(source)
    pair, support, census = pair_census(original)
    need(pair == (521, 552) and support == 110, "unexpected best pair")
    # The assignment seed is 1: reverse the canonical pair, selecting destination 552.
    candidate, targets = factor(original, pair[::-1])
    check_d(original, candidate)
    need(all(original[k] == candidate[k] for k in original if k != "D"), "changed exterior")
    spec = importlib.util.spec_from_file_location("r420_original_xcheck", XCHECK)
    xc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(xc)
    baseline = xc.Word(original)
    baseline.labels()
    baseline.full()
    hypotheses, conclusion, _ = baseline.interface()
    need(all(hypotheses.values()) and all(conclusion.values()), "baseline interface failed")
    # All geometric data are byte-for-byte equal; reuse the exact frame tables.
    baseline.w = candidate
    baseline.full()
    raw_hypotheses, raw_conclusion, _ = baseline.interface()
    need([k for k, ok in raw_hypotheses.items() if not ok] == ["H2_D_frame0_targets_from_helpers"],
         "candidate violates an interface hypothesis beyond the documented H2 extension")
    need([k for k, ok in raw_conclusion.items() if not ok] == ["K_equals_D"],
         "unexpected legacy conclusion mismatch")
    normalized = deepcopy(candidate)
    normalized["D"] = deepcopy(original["D"])
    need(normalized == original, "normalization changed the retained word")

    controls = []
    bad = deepcopy(candidate)
    bad["D"].pop()
    controls.append(rejected("omitted helper restoration", original, bad))
    bad = deepcopy(candidate)
    bad["D"].pop(-2)
    controls.append(rejected("omitted shared target read", original, bad))
    bad = deepcopy(candidate)
    bad["D"][-1][2] = [520]
    controls.append(rejected("wrong restoration source", original, bad))
    bad = deepcopy(candidate)
    bad["D"][-2][0] = 1
    controls.append(rejected("F2-correct read at nonzero frame", original, bad))
    bad = deepcopy(candidate)
    bad["D"] += [[0, 552, [120]], [0, 552, [120]]]
    controls.append(rejected("F2-neutral target-to-helper contamination", original, bad))
    bad = deepcopy(candidate)
    bad["D"] += [[0, 552, [0]], [0, 552, [0]]]
    controls.append(rejected("F2-neutral source access at frame zero", original, bad))
    # Positive control: a restored helper update independent of all target reads.
    good = deepcopy(candidate)
    good["D"] += [[0, 240, [241]], [0, 240, [241]]]
    check_d(original, good)

    words = {"baseline": original, "candidate": candidate,
             "other_orientation": factor(original, pair)[0]}
    metrics = {}
    baseline_nonscalar = None
    for name, word in words.items():
        check_d(original, word)
        records = export(word, output / name)
        metrics[name] = inspect_records(word, records)
        if name == "baseline":
            baseline_nonscalar = [r for r in records if r[0] != 1]
        else:
            need([r for r in records if r[0] != 1] == baseline_nonscalar, "MOVE/COPY/ERASE sequence changed")
    need(metrics["baseline"]["scalar_adds"] - metrics["candidate"]["scalar_adds"] == support - 2 == 108,
         "incorrect complete XOR saving")
    cohort = cohort_check(output, metrics)
    return dict(status="PASS_R420_FRAME_ZERO_PAIR", base_commit="66849e1475c930fd7732b1a0067ffee7e1e95f60",
                assignment_seed=1, pair=list(pair[::-1]), shared_targets=targets,
                domain_pairs=sum(census.values()), pair_support_histogram=dict(sorted(census.items())),
                D_adds_before=sum(len(g[2]) for g in original["D"]),
                D_adds_after=sum(len(g[2]) for g in candidate["D"]),
                candidate_content_sha256=hashlib.sha256(canonical(candidate)).hexdigest(),
                input_content_sha256=hashlib.sha256(canonical(original)).hexdigest(),
                native=metrics, cohort=cohort, mutation_controls=controls, columns=660,
                F2_neutral_prefix_inflation_rejected=True,
                legacy_H2_rejected_as_expected=True, normalized_H1_H5_pass=True,
                scope="Finite F2 circuit, D interface, unchanged geometry, nine-stage columns and native positive prefixes; no hosted invoice or new kappa")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New directory for generated words, records and receipt")
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        result = verify(args.output)
        (args.output / "certificate.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        with tempfile.TemporaryDirectory(prefix="r420-frame-zero-pair-") as temporary:
            result = verify(Path(temporary))
    expected = json.loads((HERE / "certificate.json").read_text())
    need(json.loads(canonical(result)) == expected, "certificate mismatch")
    print("Pair census: 87990/87990 pairs, unique maximum support 110; six D controls rejected")
    print("Nine-stage C++ replay: 1380 columns, 18 bridge controls; F2-neutral prefix inflation rejected")
    if args.output:
        print("Generated evidence:", args.output.resolve())
    print("PASS_R420_FRAME_ZERO_PAIR D=19922->19814 native_adds=26916->26808 columns=660 kappa=unchanged")


if __name__ == "__main__":
    main()
