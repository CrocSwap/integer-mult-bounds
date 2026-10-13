#!/usr/bin/env python3
"""Compose the pinned PR670 and PR674 circuits and verify their complete word.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The input circuits are by yongjae321 and x0hu, respectively.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
CHECKER = ROOT / "research/e8-bit-r420/code/xcheck.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_check():
    for name, pin in json.loads((HERE / "SOURCES.json").read_text())["files"].items():
        data = (ROOT / name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin["sha256"], "Source changed: " + name)
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == pin["git_blob"], "Blob changed: " + name)


def cleanup(word):
    v = word["v"]
    full = next(i for i, f in enumerate(word["frames"]) if len(f) == v)
    word["C"] = [[full, d, s[:]] for _, d, s in (word["A"] + word["B"])[::-1]
                 if not v <= d < 2 * v]


def blocks():
    a = json.loads((HERE / "vendor/pr670/candidate.json").read_text())
    b = json.loads((HERE / "vendor/pr674/certificate.json").read_text())
    return [
        {"pr": 670, "start": 263, "stop": 313, "frame": 545, "registers": a["registers"],
         "gates": [[545, a["registers"][d], [a["registers"][s]]] for d, s in a["replacement_local_ops"]],
         "single_word_sha256": json.loads((HERE / "vendor/pr670/CERTIFICATE.json").read_text())["revised_content_sha256"]},
        {"pr": 674, "start": 371, "stop": 417, "frame": 547, "registers": b["registers"],
         "gates": [[547, d, [s]] for d, s in b["replacement_ops"]],
         "single_word_sha256": b["candidate_canonical_sha256"]}]


def build(original, changes):
    word = copy.deepcopy(original)
    for block in sorted(changes, key=lambda b: b["start"], reverse=True):
        word["B"][block["start"]:block["stop"]] = copy.deepcopy(block["gates"])
    cleanup(word)
    return word


def truth_table(gates, registers):
    index = {r: i for i, r in enumerate(registers)}
    ops = [(index[d], index[s[0]]) for _, d, s in gates]
    table = []
    for value in range(4096):
        bits = [(value >> i) & 1 for i in range(12)]
        for destination, source in ops:
            bits[destination] = (bits[destination] + bits[source]) % 2
        table.append(sum(bit << i for i, bit in enumerate(bits)))
    return table


def positive_matrix(gates, registers):
    index = {r: i for i, r in enumerate(registers)}
    rows = [[int(i == j) for j in range(12)] for i in range(12)]
    for _, d, sources in gates:
        require(len(sources) == 1 and d != sources[0], "Not a binary transvection")
        d, s = index[d], index[sources[0]]
        rows[d] = [a + b for a, b in zip(rows[d], rows[s])]
    return rows


def paths(word):
    result = [[f] for f in word["start"]]
    for phase in ("D", "A", "B", "C"):
        for frame, destination, sources in word[phase]:
            for register in [destination] + sources:
                if result[register][-1] != frame:
                    result[register].append(frame)
    for register, frame in enumerate(word["final"]):
        if result[register][-1] != frame:
            result[register].append(frame)
    return result


def additions(word):
    return sum(len(s) for phase in ("D", "A", "B", "C") for _, _, s in word[phase]) + sum(
        len(row) for row in word["scatter"])


def check(original, word, changes):
    require(set(changes[0]["registers"]).isdisjoint(changes[1]["registers"]), "Blocks share a register")
    component_checks = []
    for block in changes:
        registers = block["registers"]
        old, new = original["B"][block["start"]:block["stop"]], block["gates"]
        require(len(registers) == len(set(registers)) == 12, "Need twelve distinct registers")
        require(all(f == block["frame"] for f, _, _ in old + new), "A block frame changed")
        require(truth_table(old, registers) == truth_table(new, registers), "Block map differs")
        single = build(original, [block])
        require(hashlib.sha256(canonical(single)).hexdigest() == block["single_word_sha256"],
                "Single-word reconstruction differs from its author's certificate")
        for before, after in ((old, new), (old[::-1], new[::-1])):
            a, b = positive_matrix(before, registers), positive_matrix(after, registers)
            require(all(y <= x for ar, br in zip(a, b) for x, y in zip(ar, br)), "Positive transfer increased")
        component_checks.append({"pr": block["pr"], "inputs": 4096, "before": len(old), "after": len(new)})
    require(paths(original) == paths(word), "A register frame path changed")
    require(additions(original) == 26916 and additions(word) == 26858, "Wrong composed XOR count")
    require(all(original[k] == word[k] for k in original if k not in ("B", "C")), "An exterior field changed")
    reference = load_module("r420_reference_check", CHECKER)
    checked, labels, full, hypotheses, conclusion, _ = reference.check(word)
    require(all(hypotheses.values()) and all(conclusion.values()), "Interface failed")
    controls = {}

    def reject(name, mutant, expected):
        audit = copy.copy(checked)
        audit.w = mutant
        try:
            audit.full()
        except reference.Reject as error:
            require(expected in str(error), name + " failed for a different reason: " + str(error))
            controls[name] = str(error)
        else:
            raise ValueError("Control was accepted: " + name)

    offset = 0
    for block in changes:
        start = block["start"] - offset
        mutant = copy.deepcopy(word)
        del mutant["B"][start]
        cleanup(mutant)
        reject("wrong_block_%d_with_correct_inverse" % block["pr"], mutant, "targets not y + x")
        offset += block["stop"] - block["start"] - len(block["gates"])
    mutant = copy.deepcopy(word)
    z_prefix = sum(not 120 <= d < 240 for _, d, _ in word["A"] + word["B"][:263])
    del mutant["C"][len(word["C"]) - 1 - z_prefix]
    reject("missing_cleanup_gate", mutant, "sources not restored")
    mutant = copy.deepcopy(word)
    mutant["B"][263][0] = word["start"][mutant["B"][263][1]]
    reject("unpaid_low_frame", mutant, "climb not nested")
    mutant = copy.deepcopy(original)
    for block in changes:
        mutant["B"][block["start"]:block["stop"]] = copy.deepcopy(block["gates"])
    cleanup(mutant)
    reject("ascending_stale_slice_offsets", mutant, "targets not y + x")
    mutant = copy.deepcopy(word)
    mutant["C"] = copy.deepcopy(original["C"])
    audit = copy.copy(checked)
    audit.w = mutant
    audit.full()
    h, c, _ = audit.interface()
    require(not h["H4_C_literal_reverse_at_full"] and all(c.values()), "Stale cleanup control failed")
    controls["stale_cleanup"] = "scalar map accepted; H4 literal-reversal contract rejected"
    return {"status": "PASS_R420_TWO_BLOCK_COMPOSITION", "components": component_checks,
            "labels": labels, "full_word": full, "hypotheses": hypotheses, "conclusion": conclusion,
            "controls": controls, "unchanged_register_paths": len(paths(word)),
            "original_additions": additions(original), "replacement_additions": additions(word),
            "replacement_canonical_sha256": hashlib.sha256(canonical(word)).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New output directory; default is a temporary directory")
    parser.add_argument("--native", action="store_true", help="Run native 5-, 9- and 11-stage checks")
    parser.add_argument("--hosted", action="store_true", help="Also run the nine-stage whole-owner and price checks")
    args = parser.parse_args()
    require(not sys.flags.optimize, "Run with assertions enabled for the inherited checks")
    out = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix="r420-compose-"))
    if args.output:
        out.mkdir(parents=True, exist_ok=False)
    source_check()
    original = json.loads(gzip.decompress(WORD.read_bytes()))
    changes = blocks()
    word = build(original, changes)
    result = check(original, word, changes)
    for name, value in (("baseline", original), ("replacement", word)):
        (out / (name + ".json.gz")).write_bytes(gzip.compress(canonical(value) + b"\n", mtime=0))
    if args.native or args.hosted:
        result["native"] = load_module("r420_compose_native", HERE / "native.py").run(ROOT, out)
    if args.hosted:
        result["hosted"] = load_module("r420_compose_hosted", HERE / "hosted.py").run(ROOT, out)
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print("OUTPUT", out)
    print("PASS_R420_TWO_BLOCK_COMPOSITION local_additions=26916->26858 saved=58 kappa=unchanged")


if __name__ == "__main__":
    main()
