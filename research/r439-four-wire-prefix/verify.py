#!/usr/bin/env python3
"""Independent finite certificate checks and full unchanged source/native replay.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance.
Apache-2.0. Python 3.12+, a C++17 compiler, and Boost headers are required.
"""
import argparse
from collections import Counter, deque
import copy
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need = C["need"]


def same(a, b, message):
    # Canonical serialization distinguishes bool from int and rejects NaN.
    need(C["canonical"](a) == C["canonical"](b), message)


def transition(columns, destination, source):
    # Column images, independent of build.py's row representation and tie order.
    return tuple(c ^ (((c >> source) & 1) << destination) for c in columns)


def groups():
    tables, receipt = {}, {}
    for n in (2, 3, 4):
        identity = tuple(1 << k for k in range(n))
        distances = {identity: 0}
        pending = deque([identity])
        generators = [(d, s) for s in range(n) for d in range(n) if d != s]
        while pending:
            state = pending.popleft()
            for d, s in generators:
                next_state = transition(state, d, s)
                if next_state not in distances:
                    distances[next_state] = distances[state] + 1
                    pending.append(next_state)
        order = 1
        for k in range(n):
            order *= 2 ** n - 2 ** k
        need(len(distances) == order, "incomplete GL enumeration")
        edges = 0
        for state, distance in distances.items():
            need((distance == 0) == (state == identity), "distance origin")
            for d, s in generators:
                next_state = transition(state, d, s)
                need(abs(distances[next_state] - distance) <= 1, "distance edge potential")
                edges += 1
        tables[n] = distances
        receipt[str(n)] = {"states": order, "edges_checked": edges,
                           "distance_histogram": {str(k): v for k, v in sorted(Counter(distances.values()).items())}}
    return tables, receipt


def image(ops, n, positive=False):
    columns = []
    for input_column in range(n):
        values = [int(k == input_column) for k in range(n)]
        for destination, source in ops:
            if positive:
                values[destination] += values[source]
            else:
                values[destination] ^= values[source]
        columns.append(values)
    return columns


def boolean_image(ops, n):
    return tuple(sum(bit << k for k, bit in enumerate(col)) for col in image(ops, n))


def positive_guard(old, new, n):
    for reverse in (False, True):
        a = image(old[::-1] if reverse else old, n, True)
        b = image(new[::-1] if reverse else new, n, True)
        need(all(y <= x for ac, bc in zip(a, b) for x, y in zip(ac, bc)), "positive domination")


def flat(word, section):
    return [[f, d, [s]] for f, d, srcs in word[section] for s in srcs]


def check_rewrites(baseline, candidate, certificate, tables):
    need(certificate["format"] == "r439-prefix/1" and type(certificate["seed"]) is int
         and certificate["seed"] == 11, "certificate version/seed")
    need(C["digest"](baseline) == certificate["baseline_sha256"], "baseline content hash")
    need(C["digest"](candidate) == certificate["candidate_sha256"], "candidate content hash")
    selected = certificate["selected"]
    need(len(selected) == 95, "selected rewrite count")
    v, nregs = baseline["v"], 2 * baseline["v"] + baseline["R"]
    expected = copy.deepcopy(baseline)
    counts, widths = {}, Counter()
    for section in ("A", "B"):
        original = flat(baseline, section)
        chosen = [x for x in selected if x["section"] == section]
        previous, saved = 0, 0
        for item in chosen:
            for key in ("start", "stop", "frame", "saving"):
                need(type(item[key]) is int, "noninteger rewrite field")
            start, stop, frame = (item[key] for key in ("start", "stop", "frame"))
            need(previous <= start < stop <= len(original), "overlapping/out-of-range windows")
            previous = stop
            registers = item["registers"]
            need(all(type(r) is int and 0 <= r < nregs and not v <= r < 2 * v for r in registers),
                 "only physical z registers permitted")
            need(registers == sorted(set(registers)) and 2 <= len(registers) <= 4, "register set")
            width = len(registers)
            old, new = item["old"], item["new"]
            for ops in (old, new):
                need(all(type(op) is list and len(op) == 2 and all(type(i) is int and 0 <= i < width for i in op)
                         and op[0] != op[1] for op in ops), "invalid transvection")
                need({i for op in ops for i in op} == set(range(width)), "participant set changed")
            decoded = [[frame, registers[d], [registers[s]]] for d, s in old]
            same(decoded, original[start:stop], "window does not match source word")
            need(len(old) > len(new) and item["saving"] == len(old) - len(new), "strict shorter cost")
            old_map, new_map = boolean_image(old, width), boolean_image(new, width)
            need(old_map == new_map, "local F2 map changed")
            need(len(new) == tables[width][old_map], "nonminimal replacement")
            positive_guard(old, new, width)
            widths[width] += 1
            saved += item["saving"]
        # Reverse-index splice, independent of the builder's forward emitter.
        result = copy.deepcopy(original)
        for item in reversed(chosen):
            result[item["start"]:item["stop"]] = [
                [item["frame"], item["registers"][d], [item["registers"][s]]] for d, s in item["new"]]
        expected[section] = result
        counts[section] = {"rewrites": len(chosen), "saved": saved}
    need(sum(x["rewrites"] for x in counts.values()) == len(selected), "unknown section")
    full = next(i for i, labels in enumerate(baseline["frames"]) if set(labels) == set(range(v)))
    cleanup = []
    for section in ("B", "A"):
        for _, d, sources in reversed(expected[section]):
            if not v <= d < 2 * v:
                cleanup.append([full, d, sources[:]])
    expected["C"] = cleanup
    same(expected, candidate, "candidate differs from exact splice and paired cleanup")
    need(counts == {"A": {"rewrites": 85, "saved": 115}, "B": {"rewrites": 10, "saved": 12}},
         "unexpected selected savings")
    return {"sections": counts, "widths": {str(k): v for k, v in sorted(widths.items())},
            "strict_minima": len(selected), "both_order_positive_guards": 2 * len(selected)}


def full_checks(root, baseline, candidate):
    checker = C["module"]("pinned_xcheck", Path(root) / C["CHECKER"])
    results = {}
    for name, word in (("baseline", baseline), ("candidate", candidate)):
        _, labels, full, hypotheses, conclusions, info = checker.check(word)
        need(all(value is True for value in hypotheses.values()), "source interface hypotheses")
        need(all(value is True for value in conclusions.values()), "source interface conclusions")
        results[name] = dict(labels=labels, full=full, hypotheses=hypotheses, conclusions=conclusions, info=info)
    return checker, results


def controls(baseline, candidate, certificate, tables, checker):
    rejected = []

    def reject(name, action, reason):
        try:
            action()
        except (ValueError, checker.Reject) as error:
            need(reason in str(error), "wrong rejection for " + name + ": " + str(error))
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)

    def mutated_certificate(name, edit, reason):
        changed = copy.deepcopy(certificate)
        edit(changed)
        reject(name, lambda: check_rewrites(baseline, candidate, changed, tables), reason)

    mutated_certificate("wrong local XOR gate", lambda x: x["selected"][0]["new"][0].__setitem__(0, 0), "local F2")
    mutated_certificate("wrong source frame", lambda x: x["selected"][0].__setitem__("frame", 1), "source word")
    mutated_certificate("target participant", lambda x: x["selected"][0]["registers"].__setitem__(0, 111), "physical z")
    mutated_certificate("self addition", lambda x: x["selected"][0]["new"][0].__setitem__(1, 2), "transvection")
    mutated_certificate("boolean index", lambda x: x["selected"][0].__setitem__("start", True), "noninteger")
    mutated_certificate("unpaid saving", lambda x: x["selected"][0].__setitem__("saving", 3), "shorter cost")
    mutated_certificate("overlapping windows", lambda x: x["selected"][1].__setitem__("start", x["selected"][0]["start"]),
                        "overlapping")
    # Same F2 identity, but strictly growing positive transfer in both orders.
    need(boolean_image([], 2) == boolean_image([[0, 1], [0, 1]], 2), "positive control premise")
    reject("F2 cancellation hides positive growth", lambda: positive_guard([], [[0, 1], [0, 1]], 2), "positive")

    changed = copy.deepcopy(candidate)
    changed["C"] = copy.deepcopy(baseline["C"])
    stale = checker.Word(changed)
    stale.full()
    h, conclusions, _ = stale.interface()
    need(h["H4_C_literal_reverse_at_full"] is False, "stale cleanup not rejected")
    need(all(value for key, value in h.items() if key != "H4_C_literal_reverse_at_full")
         and all(conclusions.values()), "stale cleanup control lost its semantic premise")
    rejected.append("unpaired stale literal cleanup")
    # An elementary gate cannot be deleted from an invertible full program.
    changed = copy.deepcopy(candidate)
    del changed["A"][0]
    reject("dropped actual prefix gate", lambda: checker.Word(changed).full(), "not restored")
    # A valid source hash alone cannot license an unrelated change elsewhere.
    changed = copy.deepcopy(candidate)
    changed["stats"]["junk_wires"] += 1
    changed_certificate = copy.deepcopy(certificate)
    changed_certificate["candidate_sha256"] = C["digest"](changed)
    reject("unrelated payload edit with recomputed hash",
           lambda: check_rewrites(baseline, changed, changed_certificate, tables), "exact splice")
    reject("boolean receipt equality", lambda: same({"count": 1}, {"count": True}, "receipt changed"), "receipt changed")
    return rejected


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    source_manifest = C["pins"](root)
    output.mkdir(parents=True, exist_ok=False)
    baseline = C["load"](root / C["WORD"])
    candidate = C["load"](C["HERE"] / "candidate.json.gz")
    certificate = C["load"](C["HERE"] / "CERTIFICATE.json")
    generated = output / "regenerated"
    print("reproduce bounded seed-11 nomination", flush=True)
    subprocess.run([sys.executable, "-I", "-B", C["HERE"] / "build.py", "--source-root", root,
                    "--output", generated], check=True)
    same(C["load"](generated / "CERTIFICATE.json"), certificate, "certificate not reproducible")
    same(C["load"](generated / "candidate.json.gz"), candidate, "candidate not reproducible")
    print("independent column-state enumeration and local certificates", flush=True)
    tables, group_receipt = groups()
    rewrites = check_rewrites(baseline, candidate, certificate, tables)
    print("unchanged source geometry, 661-column replay, and literal H1-H5", flush=True)
    checker, local = full_checks(root, baseline, candidate)
    negatives = controls(baseline, candidate, certificate, tables, checker)
    print("compile unchanged native checkers: legality and 5/9/11 stages", flush=True)
    native = C["module"]("r439_native", C["HERE"] / "native.py").run(
        root, root / C["WORD"], C["HERE"] / "candidate.json.gz", output / "native")
    return {"status": "PASS_R439_FOUR_WIRE_PREFIX", "source_files": source_manifest["files"],
            "baseline_sha256": C["digest"](baseline), "candidate_sha256": C["digest"](candidate),
            "certificate_sha256": C["digest"](certificate), "groups": group_receipt, "rewrites": rewrites,
            "local": local, "controls_rejected": negatives, "native": native}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path, help="fresh directory for logs and binaries (default: temporary)")
    parser.add_argument("--receipt", type=Path, help="new deterministic JSON receipt; never overwrite")
    parser.add_argument("--expected", type=Path, default=C["HERE"] / "EXPECTED.json")
    args = parser.parse_args()
    if args.output:
        need(not args.output.exists(), "output already exists")
    if args.receipt:
        need(not args.receipt.exists(), "receipt already exists")
    expected = C["load"](args.expected)
    with tempfile.TemporaryDirectory(prefix="r439-four-wire-") as temp:
        report = run(args.source_root, args.output or Path(temp) / "run")
        same(report, expected, "receipt differs from EXPECTED.json")
        if args.receipt:
            C["write"](args.receipt, report)
    print("PASS_R439_FOUR_WIRE_PREFIX: 95 rewrites; 254 ADDs saved; H1-H5; 5/9/11 stages; 12 controls; kappa unchanged")
