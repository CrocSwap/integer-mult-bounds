#!/usr/bin/env python3
"""Replay the chart-595 certificate using the individual authenticated executors."""

from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from time import monotonic
import gzip
import json
import os
import resource
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
BASE = "e54523517d0f03e58352e647c403a5af3e525a57"
BRIDGE = "0eabc624a9bc9ed2847719efd63390db4d297df4"
PARENT_HEAD = "1b4a4d6f9370b8c93b3f769a6229a9111ef3940e"
PARENT = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
CANDIDATE = "d5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b"
CANDIDATE_GZIP = "789c51223158f816b4046321e28449e1db540d20b75ce57e0699a20706bc3510"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
EDIT = "c8a914049eb36f5f307dfabef080169bbee06c024eab77b75249566028ca3fcf"
PARENT_UPPER = Fraction("0.0037261023901")
CLAIM = "0.0037266288"
GRAPHS = {"peer": PARENT, "candidate": CANDIDATE}
TARGET_DELTA = {"1": 16, "8": 16, "9": -16}
LIMITS = {"core": 300, "catalogue": 260, "dense": 360}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def asset(relative):
    name = PurePosixPath(relative)
    require(name.parts and not name.is_absolute() and ".." not in name.parts and name.as_posix() == relative,
            f"invalid asset path {relative}")
    path = ROOT.joinpath(*name.parts)
    require(path.resolve() == path and path.is_file(), f"missing or aliased asset {relative}")
    return path


def digest(raw):
    return sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, payload):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, sort_keys=True, indent=2)
        stream.write("\n")


def decoded_sha(path):
    return digest(gzip.decompress(path.read_bytes()))


def match_evidence(fresh, name, observed=()):
    recorded = read(asset(f"evidence/{name}"))
    require({k: v for k, v in fresh.items() if k not in observed}
            == {k: v for k, v in recorded.items() if k not in observed},
            f"all reproducible fields match the frozen {name} receipt")


def authenticate():
    manifest = read(asset("ASSETS.json"))
    require(manifest["schema_version"] == 1 and manifest["base_commit"] == BASE
            and manifest["ci_bridge_commit"] == BRIDGE and manifest["parent_head"] == PARENT_HEAD
            and manifest["graph_pins"] == GRAPHS and manifest["caller_sha256"] == CALLER,
            "exact source and caller manifest")
    verified = {}
    for row in manifest["files"]:
        name = row["path"]
        require(name not in verified, f"duplicate asset {name}")
        raw = asset(name).read_bytes()
        require(len(raw) == row["bytes"] and digest(raw) == row["sha256"], f"asset bytes {name}")
        if "git_blob" in row:
            require(sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == row["git_blob"],
                    f"original Git blob {name}")
        verified[name] = row["sha256"]
    actual = set()
    for path in ROOT.rglob("*"):
        require(not path.is_symlink(), f"aliased package entry {path.relative_to(ROOT)}")
        if path.is_file():
            actual.add(path.relative_to(ROOT).as_posix())
    require(actual == verified.keys() | {"ASSETS.json"}, "complete package file inventory")
    require(verified["EDIT.json"] == EDIT and verified["data/CANDIDATE-GRAPH.json.gz"] == CANDIDATE_GZIP,
            "frozen literal edit and candidate transport")
    require(decoded_sha(asset("data/PARENT-GRAPH.json.gz")) == PARENT
            and decoded_sha(asset("data/CANDIDATE-GRAPH.json.gz")) == CANDIDATE
            and decoded_sha(asset("data/CALLER.json.gz")) == CALLER, "canonical graph and caller bytes")
    return verified


def invoke(out, name, script, deadline, *args):
    remaining = deadline - monotonic()
    require(remaining > 0, f"stage deadline before {name}")
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    stdout = out / f"{name}.stdout"
    stderr = out / f"{name}.stderr"
    argv = [sys.executable, "-I", "-B", "-X", f"pycache_prefix={out / 'fresh-bytecode'}",
            str(asset(script)), *(str(arg) for arg in args)]
    with stdout.open("xb") as output, stderr.open("xb") as error:
        process = subprocess.run(argv, cwd=ROOT, stdout=output, stderr=error, env=env, timeout=remaining)
    if process.returncode:
        sys.stderr.write(stderr.read_text(encoding="utf-8", errors="replace"))
        process.check_returncode()
    print(f"Finished {name}", flush=True)
    return stdout


def construct(out, deadline):
    output = out / "CANDIDATE-GRAPH.json.gz"
    summary = invoke(out, "construction", "construct.py", deadline,
                     "--parent", asset("data/PARENT-GRAPH.json.gz"), "--edit", asset("EDIT.json"), "--out", output)
    require(f"PASS_P104_CHART595_CONSTRUCTION {CANDIDATE}" in summary.read_text().splitlines()
            and decoded_sha(output) == CANDIDATE, "fresh candidate reconstruction")


def verify_core(out, deadline):
    normalized_path = invoke(out, "normalized", "operator.py", deadline)
    normalized = read(normalized_path)
    require(normalized["status"] == "PASS_CHART595_EXACT_NORMALIZED_OPERATOR"
            and normalized["parent_graph_sha256"] == PARENT and normalized["candidate_graph_sha256"] == CANDIDATE
            and normalized["operator_sizes"] == {"original": 1501, "candidate": 1502}
            and normalized["all_normalized_forward_and_adjoint_coefficients_exact"],
            "full normalized operator on both exact graphs")
    match_evidence(normalized, "OPERATOR.json")

    parent = asset("data/PARENT-GRAPH.json.gz")
    candidate = asset("data/CANDIDATE-GRAPH.json.gz")
    caller = asset("data/CALLER.json.gz")
    physical_path = out / "PHYSICAL.json"
    invoke(out, "physical", "physical.py", deadline,
           "--parent", parent, "--candidate", candidate, "--caller", caller,
           "--candidate-sha256", CANDIDATE, "--out", physical_path)
    physical = read(physical_path)
    child_storage = physical["native"]["candidate"]
    require(physical["status"] == "PASS_CHART595_BANK_PHYSICAL" and physical["graphs"] == GRAPHS
            and physical["caller_sha256"] == CALLER and physical["both_graphs_respect_historical_numeric_homes_and_streams"]
            and child_storage["short_return_sealed_at_public_role"] == 281
            and child_storage["short_return_public_install_schedule_position"] == 996
            and child_storage["short_return_original_entrance_retired_at_install"]
            and child_storage["nonretired_public_inputs_preserved_until_final_installs"],
            "paired common root, early public installation and finite ordinary accounting")
    match_evidence(physical, "PHYSICAL.json")

    caller_path = out / "CALLER.json"
    invoke(out, "caller", "caller.py", deadline,
           "--parent", parent, "--candidate", candidate, "--caller", caller,
           "--candidate-sha256", CANDIDATE, "--out", caller_path)
    signed = read(caller_path)
    require(signed["status"] == "PASS_CHART595_ACTUAL16_CALLER" and signed["graphs"] == GRAPHS
            and signed["caller_sha256"] == CALLER and signed["signed"]["calls"] == 16
            and signed["signed_paid_delta"] == {} and signed["signed_target_delta"] == TARGET_DELTA,
            "complete signed caller and exact productive substitution")
    for name, targets in (("peer", 21152), ("candidate", 21168)):
        receipt = signed["invoices"][name]
        require(sum(receipt["paid"].values()) == 101824 and sum(receipt["targets"].values()) == targets,
                f"whole signed invoice counts {name}")
    match_evidence(signed, "CALLER.json")

    price_path = out / "PRICE.json"
    invoke(out, "price", "price.py", deadline,
           "--caller-proof", caller_path, "--physical", physical_path, "--out", price_path)
    price = read(price_path)
    outer = price["compiler"]["outer"]
    require(price["status"] == "PASS_CHART595_DIRECTED_PRICE_OUTER" and price["graphs"] == GRAPHS
            and price["caller_sha256"] == CALLER and price["physical_join"]
            and outer["strict_count"] == 54 and outer["functional_count"] == 4
            and Fraction(price["published_peer_upper"]) == PARENT_UPPER
            and price["candidate_directed_conditional_lower"] == CLAIM and Fraction(CLAIM) > PARENT_UPPER,
            "complete directed lower exceeds the matched upper")
    match_evidence(price, "PRICE.json")
    cross_path = out / "CROSSPRICE.json"
    invoke(out, "crosscheck", "price_crosscheck.py", deadline,
           "--caller", caller_path, "--claim", CLAIM, "--out", cross_path)
    cross = read(cross_path)
    require(cross["status"] == "PASS_INDEPENDENT_DIRECTED_PRICE" and cross["claim"] == CLAIM
            and cross["parent_graph_sha256"] == PARENT and cross["candidate_graph_sha256"] == CANDIDATE
            and tuple(map(Fraction, cross["child_bracket"])) == tuple(map(Fraction, price["candidate_raw_bracket"])),
            "independent directed endpoints")
    match_evidence(cross, "CROSSPRICE.json")
    review_path = out / "INDEPENDENT-REVIEW.json"
    invoke(out, "independent-review", "review/check_cut_and_price.py", deadline,
           "--caller-receipt", caller_path, "--outer-receipt", price_path, "--out", review_path)
    review = read(review_path)
    require(review["status"] == "PASS_INDEPENDENT_CUT_SECTORS_AND_DIRECTED_PRICE_CONTROL"
            and review["candidate_graph"] == CANDIDATE and review["parent_graph"] == PARENT
            and review["signed_caller"] == CALLER
            and review["actual_signed_caller_receipt_sha256"] == digest(caller_path.read_bytes())
            and review["joined_outer_receipt_sha256"] == digest(price_path.read_bytes()),
            "independent typed cut, caller sectors, and price bound to the fresh application")
    match_evidence(review, "INDEPENDENT-REVIEW.json")
    return {"status": "PASS_CHART595_CORE", "graph_pins": GRAPHS, "caller_sha256": CALLER,
            "conditional_lower": price["candidate_directed_conditional_lower"],
            "raw_bracket": price["candidate_raw_bracket"],
            "fresh_receipts": {path.name: digest(path.read_bytes()) for path in
                               (normalized_path, physical_path, caller_path, price_path, cross_path, review_path)}}


def verify_catalogue(out, deadline):
    native_out = out / "native"
    invoke(out, "native", "native.py", deadline,
           "--candidate-sha", CANDIDATE, "--candidate-gzip-sha", CANDIDATE_GZIP, "--out", native_out)
    phase_path = native_out / "PHASE-RESULT.json"
    phase = read(phase_path)
    recipe = native_out / "SPLIT-RECIPES.json"
    require(phase["status"] == "PASS_CHART595_NATIVE_PHASE_AND_BINDING"
            and phase["recipient_graph_sha256"] == PARENT and phase["candidate_graph_sha256"] == CANDIDATE
            and phase["caller_sha256"] == CALLER and phase["paid_occurrences_rebound"] == 6142
            and phase["ordered_pairs_rechecked"] == 3024
            and phase["main_boundaries_rechecked"] == 104 and phase["fresh_split_maps"] == 2
            and phase["columns_each_direction_per_split_map"] == 512 and phase["wrong_phase_controls_rejected"] == 2
            and phase["artifact_sha256"][recipe.name] == digest(recipe.read_bytes()),
            "complete native recipe binding with fresh split forward and adjoint columns")
    match_evidence(phase, "PHASE-RESULT.json", ("started_at", "completed_at", "start_sha256", "cpu_seconds", "peak_rss_kib"))
    match_evidence(read(recipe), "SPLIT-RECIPES.json")
    return {"status": "PASS_CHART595_CATALOGUE", "graph_pins": GRAPHS,
            "fresh_receipts": {path.name: digest(path.read_bytes()) for path in (phase_path, recipe)}}


def verify_dense(out, deadline):
    receipt_path = invoke(out, "held-arrays", "dense.py", deadline)
    receipt = read(receipt_path)
    cases = {data["prime"]: data["cases"] for data in receipt["fields"]}
    controls = {name: status for samples in cases.values() for case in samples
                for name, status in case["actual_negative_controls"].items()}
    require(receipt["status"] == "PASS_P104_CHART595_DENSE_HELD_ARRAYS"
            and receipt["graph_pins"] == {"parent": PARENT, "candidate": CANDIDATE}
            and receipt["caller_sha256"] == CALLER and receipt["field_width"] == 512
            and receipt["paid_slots_per_word"] == 6142 and receipt["main_outputs"] == 400
            and receipt["candidate_helper_outputs"] == 1102
            and set(cases) == {1000000009, 998244353} and all(len(samples) == 2 for samples in cases.values())
            and set(controls) == {"injection_coefficient_sign", "prefix_return_quarter_phase"}
            and all(control["one_actual_mutation_verified"] for control in controls.values()),
            "whole typed held-array gate with two seeds per prime and both actual faults")
    match_evidence(receipt, "DENSE.json")
    return {"status": "PASS_CHART595_DENSE", "graph_pins": GRAPHS,
            "fresh_receipts": {receipt_path.name: digest(receipt_path.read_bytes())}}


def run_stage(stage, out, authenticated):
    deadline = monotonic() + LIMITS[stage] - 2
    construct(out, deadline)
    if stage == "core":
        result = verify_core(out, deadline)
    elif stage == "catalogue":
        result = verify_catalogue(out, deadline)
    else:
        result = verify_dense(out, deadline)
    require(authenticated == authenticate(), "immutable assets before and after replay")
    write(out / "RESULT.json", result)
    print(json.dumps(result, sort_keys=True), flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("integrity", *LIMITS))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    require(sys.version_info[:2] == (3, 12) and sys.flags.isolated and sys.dont_write_bytecode and __debug__,
            "use CPython 3.12 -I -B with assertions enabled")
    authenticated = authenticate()
    if args.stage == "integrity":
        require(args.out is None, "integrity writes no outputs")
        print(json.dumps({"status": "PASS_CHART595_PACKAGE_INTEGRITY", "assets": len(authenticated)}))
        return
    cap = 2 * 1024**3
    current, hard = resource.getrlimit(resource.RLIMIT_AS)
    kept = min(n for n in (cap, current, hard) if n != resource.RLIM_INFINITY)
    resource.setrlimit(resource.RLIMIT_AS, (kept, kept))
    if args.out is not None:
        out = args.out.resolve()
        require(out != ROOT and ROOT not in out.parents, "replay output must be outside the authenticated package")
        out.mkdir()
        run_stage(args.stage, out, authenticated)
    else:
        with TemporaryDirectory(prefix="chart595-replay-") as directory:
            run_stage(args.stage, Path(directory), authenticated)


if __name__ == "__main__":
    main()
