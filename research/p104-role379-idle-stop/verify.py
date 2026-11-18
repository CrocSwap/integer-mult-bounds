#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild and check each pinned role-379 mutation in a private temporary directory."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile


PACKAGE = Path(__file__).resolve().parent
CHECKERS = PACKAGE / "src"
PRICING = PACKAGE / "retained/pricing"
PARENTS = (7636, 7658)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_bytes())


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def git_blob(blob):
    return hashlib.sha1(f"blob {len(blob)}\0".encode("ascii") + blob).hexdigest()


def pinned_sources():
    manifest = read_json(PACKAGE / "SOURCE-PINS.json")
    require(manifest["schema_version"] == 1, "source pin schema")
    pins = {}
    for pin in manifest["files"]:
        local = pin["local_path"]
        name = PurePosixPath(local)
        require(not name.is_absolute() and name.as_posix() == local and ".." not in name.parts
                and local not in pins, f"invalid pinned path {local!r}")
        path = PACKAGE / local
        require(path.is_file() and path.resolve() == path, f"missing or aliased source {local}")
        payload = path.read_bytes()
        require(len(payload) == pin["bytes"] and digest(payload) == pin["sha256"]
                and git_blob(payload) == pin["git_blob"], f"source bytes differ for {local}")
        pins[local] = pin
    return pins


def run_checker(work, filename, *args):
    command = [
        sys.executable, "-I", "-B", "-W", "error",
        "-X", f"pycache_prefix={work / 'bytecode-cache'}",
        str(CHECKERS / filename), *map(str, args),
    ]
    subprocess.run(command, cwd=work, check=True)


def run_mutation(pr, work, evidence, pins):
    expected = read_json(evidence / "mutation/RESULT.json")
    expected_price = read_json(evidence / "mutation/PRICE.json")
    source = expected["source"]
    require(expected["role"] == 379 and source["pr"] == pr, "role and parent binding")
    parent = f"retained/pr{pr}"
    word = f"{parent}/data/word.json.gz"
    invoice = f"{parent}/data/invoice-new.json"
    certificates = f"{parent}/data/clear-certificates.json"
    phase = next(local for local, pin in pins.items()
                 if pin["sha256"] == source["physical_checker_sha256"] and local.endswith("/check.py"))
    require(all(pins[k]["commit"] == source["head"] and pins[k]["pull_request"] == pr
                for k in (word, invoice, certificates)), "pinned parent head mismatch")
    require(source["gzip_sha256"] == pins[word]["sha256"]
            and source["invoice_sha256"] == pins[invoice]["sha256"]
            and source["certificates_sha256"] == pins[certificates]["sha256"], "pinned parent digest mismatch")
    first, second = expected["cut"]["anchors"]
    witness_by_clock = read_json(PACKAGE / certificates)["clear_event_index"]
    interval_witnesses = [terms for clock, terms in witness_by_clock.items() if first < int(clock) < second]
    require(len(interval_witnesses) == expected["cut"]["CLEARs_in_open_interval"]
            and all(str(expected["role"]) not in terms for terms in interval_witnesses),
            "a CLEAR certificate observes the edited role during its hold")

    result_dir = work / "mutation"
    run_checker(
        work, "idle_direct.py",
        "--word", PACKAGE / word, "--word-sha", source["word_sha256"],
        "--word-gzip-sha", source["gzip_sha256"], "--source-pr", pr, "--source-head", source["head"],
        "--role", expected["role"], "--anchors", *expected["cut"]["anchors"], "--clears", expected["ordered_clears"],
        "--invoice", PACKAGE / invoice, "--invoice-sha", source["invoice_sha256"],
        "--certificates", PACKAGE / certificates, "--certificates-sha", source["certificates_sha256"],
        "--source-check", PACKAGE / phase, "--source-check-sha", source["physical_checker_sha256"],
        "--pricing-dir", PRICING, "--base-upper", expected_price["source_upper"],
        "--out", result_dir,
    )
    actual = read_json(result_dir / "RESULT.json")
    require(actual["status"] == "PASS_SILENT_PUBLIC_MOVE_SUBSTITUTION", "mutation checker did not pass")
    candidate = result_dir / "WORD.json.gz"
    raw = candidate.read_bytes()
    candidate_word_sha = digest(gzip.decompress(raw))
    candidate_gzip_sha = digest(raw)
    require(candidate_word_sha == actual["candidate"]["word_sha256"]
            and candidate_gzip_sha == actual["candidate"]["gzip_sha256"], "generated candidate custody")

    for report in (actual, expected):
        del report["started_at"], report["finished_at"], report["candidate"]["gzip_sha256"]
    require(actual == expected, "generated mutation receipt differs")
    for name in ("EDITS.json", "INVOICE.json", "PRICE.json", "CLEAR-CERTIFICATES.json"):
        require(read_json(result_dir / name) == read_json(evidence / "mutation" / name),
                f"generated {name} differs")
    return candidate, candidate_word_sha, candidate_gzip_sha


def comparable_independent(report):
    """Allow run times and generated gzip transport to vary across environments."""
    for key in ("started", "finished", "elapsed_seconds", "resource_usage"):
        del report[key]
    del report["limits"]["cpu"]
    del report["candidate"]["gzip_sha256"]
    del report["input_bytes_rechecked"]["candidate_gzip"]
    return report


def run_independent(pr, work, evidence, candidate, candidate_word_sha, candidate_gzip_sha):
    expected = read_json(evidence / "INDEPENDENT.json")
    optional_claim = []
    if "claim" in expected["candidate"]["price"]:
        optional_claim = ["--claim", expected["candidate"]["price"]["claim"]]
    receipt = work / "INDEPENDENT.json"
    run_checker(
        work, "direct_replay.py",
        "--source-pr", pr, "--data", PACKAGE / f"retained/pr{pr}/data", "--variant", "B",
        "--candidate", candidate, "--candidate-gzip-sha", candidate_gzip_sha,
        "--candidate-json-sha", candidate_word_sha, *optional_claim, "--out", receipt,
    )
    actual = read_json(receipt)
    require(actual["result"] == "PASS_PAIRED_EXACT_REPLAY_AND_CONDITIONAL_PRICE"
            and actual["source"]["pr"] == pr and actual["candidate"]["variant"] == "B",
            "independent checker did not pass the pinned comparison")
    require(actual["candidate"]["literal_sha256"] == candidate_word_sha
            and actual["candidate"]["gzip_sha256"] == candidate_gzip_sha
            and actual["input_bytes_rechecked"]["candidate_gzip"] == candidate_gzip_sha,
            "independent candidate custody")
    generated_invoice = read_json(candidate.parent / "INVOICE.json")
    require(actual["candidate"]["full_signed_invoice"] == generated_invoice,
            "independent and mutation-derived signed invoices differ")
    generated_price = read_json(candidate.parent / "PRICE.json")
    require(actual["candidate"]["price"]["kappa"] == generated_price["bracket"],
            "independent and mutation-derived price brackets differ")
    require(comparable_independent(actual) == comparable_independent(expected),
            "generated independent receipt differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parent", type=int, choices=PARENTS)
    args = parser.parse_args()
    require(sys.version_info[:2] == (3, 12) and sys.flags.isolated and sys.dont_write_bytecode and __debug__,
            "use Python 3.12 with -I -B and assertions enabled")
    pins = pinned_sources()
    evidence = PACKAGE / f"evidence/pr{args.parent}"
    with tempfile.TemporaryDirectory(prefix=f"p104-role379-pr{args.parent}-") as directory:
        work = Path(directory)
        generated = run_mutation(args.parent, work, evidence, pins)
        run_independent(args.parent, work, evidence, *generated)
    print(f"PASS_ROLE379_PINNED_MUTATION_PHASE_INVOICE_AND_INDEPENDENT_REPLAY PR#{args.parent}", flush=True)


if __name__ == "__main__":
    main()
