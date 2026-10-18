#!/usr/bin/env python3
"""Source-bound quad17 minimum and sharp inverse envelope; no new kappa.

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor checker or search implementation is imported.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
WORD = "research/r439-six-wire-boolean/candidate.json.gz"
PARENT_CERTIFICATE = "research/r439-six-wire-boolean/CERTIFICATE.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def load(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out

    def invalid(value):
        raise ValueError("nonfinite JSON constant: "+value)

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE/(name+".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sources(root):
    pins = load((HERE/"SOURCES.json").read_bytes())
    need(pins["base_commit"] == BASE, "wrong source base")
    paths = {row["path"] for row in pins["files"]}
    need(WORD in paths and PARENT_CERTIFICATE in paths, "missing circuit source")
    out = {}
    for row in pins["files"]:
        path = row["path"]
        need(not Path(path).is_absolute() and ".." not in Path(path).parts, "invalid source path")
        raw = subprocess.check_output(["git", "show", BASE+":"+path], cwd=root)
        blob = subprocess.check_output(["git", "rev-parse", BASE+":"+path], cwd=root, text=True).strip()
        need(blob == row["git_blob"], "source blob mismatch: "+path)
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash mismatch: "+path)
        if row["usage"] == "input":
            need((root/path).read_bytes() == raw, "working source drift: "+path)
        else:
            need(row["usage"] == "provenance", "invalid source usage")
        out[path] = raw
    return pins, out


def extract(word):
    indices = [i for i, gate in enumerate(word["A"]) if gate[0] == 283]
    need(indices and indices == list(range(indices[0], indices[-1]+1)), "frame283 not contiguous")
    gates = word["A"][indices[0]:indices[-1]+1]
    need(all(len(ss) == 1 for _, _, ss in gates), "non-elementary ADD")
    wires = sorted({v for _, dst, ss in gates for v in [dst]+ss})
    need(wires == [312, 355, 412, 429, 434, 490], "quad17 register mismatch")
    index = {v: i for i, v in enumerate(wires)}
    return [indices[0], indices[-1]+1], wires, [[index[d], index[ss[0]]] for _, d, ss in gates]


def validate_statement(result, target, reverse, oracle):
    need(result["minimum"] == 12, "wrong minimum")
    need(result["shortest_programs"] == 1_008_032, "wrong shortest count")
    inv, lower = oracle.inverse_envelope(target, reverse)
    need(reverse == lower, "parent does not saturate inverse bound")
    return inv, lower


def verify(root):
    _, inputs = sources(root)
    candidate = load(gzip.decompress(inputs[WORD]))
    receipt = load(inputs[PARENT_CERTIFICATE])
    need(hashlib.sha256(canonical(candidate)).hexdigest() == receipt["candidate_sha256"],
         "PR952 artifact not bound to certificate")
    interval, registers, program = extract(candidate)
    v = candidate["v"]
    need(all(2*v <= r < 2*v+candidate["R"] for r in registers), "block is not helper-only")
    expected_cleanup = [[1, dst, ss] for _, dst, ss in (candidate["A"]+candidate["B"])[::-1]
                        if not v <= dst < 2*v]
    need(candidate["C"] == expected_cleanup, "parent lacks mandatory literal cleanup")
    discovery, oracle = module("analyze"), module("independent")
    target, reverse = oracle.signed_map(program), oracle.signed_map(program[::-1])
    flat = tuple(v for row in target for v in row)
    need(discovery.positive_map(program) == flat, "map implementations disagree")
    result, independent = discovery.graph(flat), oracle.first_gate_bfs(target)
    need(result["minimum"] == independent["minimum"] == len(program), "minima disagree")
    need(result["shortest_programs"] == independent["shortest_programs"], "path counts disagree")
    inv, lower = validate_statement(result, target, reverse, oracle)
    predecessor_masses = {}
    for name in ("research/r439-frame267-seed01/WITNESS.json",
                 "research/r439-frame281-seed15/WITNESS.json"):
        earlier = load(inputs[name])
        old_mass = sum(map(sum, oracle.signed_map(earlier["original"])))
        need(old_mass != sum(flat), "target may be a relabelled predecessor")
        predecessor_masses[name] = old_mass
    identity = oracle.signed_map([])
    need(oracle.product(target, inv) == oracle.product(inv, target) == identity, "inverse failed")
    need(oracle.signed_map(program[::-1], -1) == inv, "literal cleanup not inverse")
    reverse_flat = [v for row in reverse for v in row]
    census = result["reverse_census"]
    need(hashlib.sha256(canonical(census["endpoints"])).hexdigest()
         == independent["reverse_census_sha256"], "independent reverse censuses disagree")
    need(census["pareto_minima"] == [reverse_flat], "unexpected Pareto frontier")
    need(all(all(a <= b for a, b in zip(reverse_flat, item["matrix"]))
             for item in census["endpoints"]), "endpoint below algebraic floor")
    budgets = [[1]*6, [1, 2, 4, 8, 16, 32], [0, 3, 0, 7, 0, 11]]
    extrema = []
    for u in budgets:
        for r in range(6):
            y = [u[c]*(1 if inv[r][c] >= 0 else -1) for c in range(6)]
            actual = sum(inv[r][c]*y[c] for c in range(6))
            need(actual == sum(lower[r][c]*u[c] for c in range(6)), "envelope not attained")
        extrema.append([sum(row[c]*u[c] for c in range(6)) for row in lower])
    controls = []

    def reject(name, check):
        try:
            check()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("negative control accepted: "+name)

    reject("drop_one_ADD", lambda: need(oracle.signed_map(program[:-1]) == target, "map changed"))
    pair = next(i for i in range(len(program)-1) if oracle.signed_map(
        program[:i]+[program[i+1], program[i]]+program[i+2:]) != target)
    swapped = program[:pair]+[program[pair+1], program[pair]]+program[pair+2:]
    reject("same_count_wrong_order", lambda: need(oracle.signed_map(swapped) == target, "order changed"))
    parity_lift = copy.deepcopy(target)
    parity_lift[0][1] += 2
    need(all((a-b) % 2 == 0 for x, y in zip(target, parity_lift) for a, b in zip(x, y)), "parity control")
    reject("Boolean_equality_is_not_integer_equality", lambda: need(parity_lift == target, "lift changed"))
    bad_distance = copy.deepcopy(result)
    bad_distance["minimum"] = 11
    reject("falsified_minimum_11", lambda: validate_statement(bad_distance, target, reverse, oracle))
    bad_bound = copy.deepcopy(reverse)
    bad_bound[0][0] -= 1
    reject("below_absolute_inverse", lambda: oracle.inverse_envelope(target, bad_bound))
    reject("discovery_cap_is_incomplete", lambda: discovery.graph(flat, limit=1))
    reject("independent_cap_is_incomplete", lambda: oracle.first_gate_bfs(target, limit=1))
    bad_count = copy.deepcopy(result)
    bad_count["shortest_programs"] += 1
    reject("falsified_multiplicity", lambda: validate_statement(bad_count, target, reverse, oracle))
    return {
        "format": "r439-quad17-exact/1", "assignment_seed": 17, "base_commit": BASE,
        "source_pr": 952, "source_pr_head": "11d24706f06e95271804c9438869546724c67aab",
        "source_word_sha256": hashlib.sha256(inputs[WORD]).hexdigest(),
        "phase": "A", "frame": 283, "quad": 17, "slice": interval, "registers": registers,
        "parent_program": program, "target_matrix": target, "signed_inverse": inv,
        "reverse_positive_matrix": reverse, "discovery": result,
        "parent_literal_cleanup_checked": True, "predecessor_entry_sums": predecessor_masses,
        "independent_first_gate_BFS": independent,
        "budget_examples": {"budgets": budgets, "attained_bounds": extrema},
        "controls_rejected": controls,
        "cost": {"forward_ADDs": 12, "literal_cleanup_ADDs": 12,
                 "minimum_including_literal_cleanup": 24, "claimed_saving": 0},
        "scope": "Exact six-register positive integer minimum and sharp independent-coordinate reverse envelope. No Boolean-lift optimum, paid-profile change, new kappa, whole-supplier/native replay.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = verify(args.root.resolve())
    certificate = HERE/"CERTIFICATE.json"
    if args.write_certificate:
        certificate.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n")
    else:
        need(canonical(result) == canonical(load(certificate.read_bytes())), "certificate drift")
    print("PASS_R439_QUAD17 minimum=12 shortest_programs=1008032 reverse_endpoints=57 "
          "sharp_absolute_inverse controls=8 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        raise SystemExit(str(exc))
