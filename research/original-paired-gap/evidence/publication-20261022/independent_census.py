"""Check source bytes, literal costs, and six mutation witnesses.

This check imports no package or producer module. It evaluates one exact
input vector for each witness. The old native core contract is inherited.
OpenAI Codex assisted this review.
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import subprocess


def need(condition, message):
    if not condition:
        raise ValueError(message)


def git_blob(repo, commit, path):
    return subprocess.check_output(["git", "-C", str(repo), "show", commit + ":" + path])


def digest(raw):
    return sha256(raw).hexdigest()


def allowance(op):
    if op[0] in ("copy", "clear"):
        return 1
    value = F(*op[-2:])
    numerator, denominator = abs(value.numerator), value.denominator
    need(numerator > 0 and denominator & (denominator - 1) == 0, "Nonzero dyadic coefficient")
    if op[0] == "scale":
        need(numerator & (numerator - 1) == 0, "Power-of-two scale")
        return abs(numerator.bit_length() - denominator.bit_length()) + (value < 0)
    need(op[0] == "add", "Known scalar operation")
    return 1 + numerator.bit_length() + numerator.bit_count() + denominator.bit_length()


def rotate(value, power):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def add(left, right, coefficient):
    return left[0] + coefficient * right[0], left[1] + coefficient * right[1]


def evaluate(parts, core, labels, character, input_column):
    values = [(F(0), F(0)) for _ in range(1408)]
    values[input_column] = F(1), F(0)
    parity = [(character & label).bit_count() % 2 for label in labels]

    def endpoint(events, bank, power):
        for replica in range(2):
            for port in range(112):
                index = replica * 704 + bank + port
                values[index] = rotate(values[index], power * parity[port])
        for event in events:
            replica, slot = event["target"]
            index = replica * 704 + slot
            if event["kind"] == "physical_translation":
                values[index] = rotate(values[index], 2 * parity[slot % 112])
            else:
                need(event["kind"] == "physical_add", "Known wrapper event")
                source_replica, source_slot = event["source"]
                values[index] = add(values[index], values[source_replica * 704 + source_slot], F(event["coefficient"]))
        for replica in range(2):
            for port in range(112):
                index = replica * 704 + bank + port
                values[index] = rotate(values[index], -power * parity[port])

    endpoint(parts["prefix"], 0, 1)
    for replica in range(2):
        for event in core:
            if event[0] != "scalar":
                continue
            op = event[1]
            need(op[1][0] == "L", "The core does not use a private target")
            index = replica * 704 + op[1][1]
            if op[0] == "scale":
                values[index] = tuple(F(op[2], op[3]) * value for value in values[index])
            else:
                need(op[0] == "add" and op[2][0] == "L", "The core does not use a private source")
                values[index] = add(values[index], values[replica * 704 + op[2][1]], F(op[3], op[4]))
    endpoint(parts["suffix"], 112, -1)
    return values


def main(args):
    package = args.package.resolve()
    source = json.loads((package / "SOURCES.json").read_bytes())
    source_checks = {}
    for item in source["copied_files"]:
        if "source_commit" in item:
            raw = git_blob(args.repo, item["source_commit"], item["source_path"])
            need(raw == (package / item["file"]).read_bytes(), "Exact retained source notice")
            source_checks[item["file"]] = digest(raw)
    for name in ("loader_origin", "route_method_origin"):
        item = source[name]
        raw = git_blob(args.repo, item["commit"], item["path"])
        if name == "loader_origin":
            need(raw == (package / "source_data.py").read_bytes(), "Unchanged loader source")
        source_checks[name] = {"commit": item["commit"], "path": item["path"], "sha256": digest(raw)}
    t16 = (package / "notices/research/gauge44-slots-t16/t16/NOTICE.md").read_text()
    need("Hao Yan (@FanPUYen)" in t16, "The named account has source evidence")
    cores = json.loads(gzip.decompress((package / "data/FULL-MODE-PROGRAMS.json.gz").read_bytes()))
    packet = json.loads(gzip.decompress((package / "data/PAIRED-PROGRAMS.json.gz").read_bytes()))
    labels = [item["label"] for item in json.loads((package / "data/INPUT-LINES.json").read_bytes())["recipes"]]
    costs, witnesses = {}, {}
    cases = {
        "forward": {"missing_input_graph": (0, 0, 112, (-1, 0)),
                    "missing_translations": (1, 0, 112, (-2, 0)),
                    "wrong_order": (0, 704, 112, (-1, 0))},
        "backward": {"missing_input_graph": (0, 112, 0, (-1, 0)),
                     "missing_translations": (1, 929, 0, (0, 4)),
                     "wrong_order": (0, 816, 0, (1, 0))},
    }
    for direction, core in cores.items():
        parts = packet["programs"][direction]
        wrapper = parts["prefix"] + parts["suffix"]
        adds = [event for event in wrapper if event["kind"] == "physical_add"]
        coefficients = Counter(str(abs(F(event["coefficient"]))) for event in adds)
        profile = Counter(event[5] for event in core if event[0] == "climb")
        core_cost = 2 * sum(allowance(event[1]) for event in core if event[0] == "scalar")
        wrapper_cost = 2 * sum(allowance(["add", None, None, F(event["coefficient"]).numerator, F(event["coefficient"]).denominator]) for event in adds)
        native_count = sum(event[0] in ("climb", "adapter", "residual_adapter") for event in core)
        need(core_cost == 204418 and native_count == 5056, "Exact core invoice")
        need(len(adds) == 2688 and len(wrapper) == 3136, "Exact wrapper event count")
        need(wrapper_cost == (25088 if direction == "forward" else 34048), "Exact wrapper invoice")
        need(2 * sum(rank * count for rank, count in profile.items()) == 11044, "Exact native rank mass")
        costs[direction] = {"wrapper_ADDs": len(adds), "wrapper_translations": len(wrapper) - len(adds),
                            "wrapper_abs_coefficients": dict(coefficients), "core_scalar_allowance": core_cost,
                            "wrapper_scalar_allowance": wrapper_cost, "complete_scalar_allowance": 2 * core_cost + wrapper_cost,
                            "native_profile_per_core": dict(profile), "native_events_per_pair": 2 * native_count,
                            "native_rank_mass_per_pair": 11044}
        witnesses[direction] = {}
        for name, (character, column, row, expected) in cases[direction].items():
            mutant = deepcopy(parts)
            if name == "missing_input_graph":
                mutant["prefix"] = []
            elif name == "missing_translations":
                for side in ("prefix", "suffix"):
                    mutant[side] = [event for event in mutant[side] if event["kind"] != "physical_translation"]
            elif direction == "forward":
                mutant["suffix"] = mutant["suffix"][896:] + mutant["suffix"][:896]
            else:
                mutant["prefix"] = mutant["prefix"][-896:] + mutant["prefix"][:-896]
            original = evaluate(parts, core, labels, character, column)
            changed = evaluate(mutant, core, labels, character, column)
            error = add(changed[row], original[row], -1)
            need(error == expected and error != (0, 0), "Exact actual-character mutation witness")
            witnesses[direction][name] = {"character": character, "input_column": column, "output_row": row, "error": [str(x) for x in error]}
    result = {"status": "PASS_INDEPENDENT_PUBLICATION_CENSUS_AND_WITNESSES",
              "imports": "Python standard library only; no package or producer imports",
              "source_checks": source_checks, "costs": costs, "witnesses": witnesses,
              "scope": "Exact source bytes, literal scalar costs, and six depth-one actual-character mutation witnesses",
              "limits": "The vector evaluation strips the admitted native frames. It does not recheck old core native kernels, the owner schedule, or a complete supplier."}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    main(parser.parse_args())
