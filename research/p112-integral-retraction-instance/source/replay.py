#!/usr/bin/env python3
"""Operator-only, exact-toolchain bounded replay. No installation or networking.

Audit the complete package before executing this program. Uses only the supplied
absolute compiler, in a fresh isolated source tree. Outputs actual logs and an
operator report outside this package. The presence of this script is NOT replay.
Python 3.12+, standard library. SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any
from audit_sources import audit, verify_manifest
from check_axioms import ALLOWED, QUERY, parse_records
from generate import ROOT, require

LEAN = "/Users/andrejmas/.elan/toolchains/leanprover--lean4---v4.30.0/bin/lean"
VERSION = "4.30.0"
COMMIT = "d024af099ca4bf2c86f649261ebf59565dc8c622"
UNIT_LIMIT = 120.0
TOTAL_LIMIT = 600.0


class ReplayFailure(RuntimeError):
    pass


def validate_version(short: str, commit: str) -> None:
    if short.strip() != VERSION or commit.strip() != COMMIT:
        raise ReplayFailure("Compiler version/commit differs from the exact pin")


def check_positive(source: str, stdout: str, stderr: str,
                   returncode: int, olean_present: bool) -> dict[str, list[str]]:
    if returncode != 0 or not olean_present:
        raise ReplayFailure("Positive unit did not produce an .olean with exit 0")
    if stderr.strip() or re.search(r"(?mi)^.*\b(?:error|warning):", stdout):
        raise ReplayFailure("Positive compilation has diagnostics/stderr")
    actual = parse_records(stdout)
    expected = QUERY.findall(source)
    if not expected or len(expected) != len(set(expected)) or set(expected) != set(actual):
        raise ReplayFailure("Positive axiom census missing, duplicated, or unexpected")
    return actual


def check_negative(stdout: str, stderr: str, returncode: int,
                   olean_present: bool) -> None:
    if returncode != 1 or olean_present or stderr.strip():
        raise ReplayFailure("Negative control did not fail cleanly without an .olean")
    errors = re.findall(r"(?m)^.*:\d+:\d+: error:", stdout)
    diagnostic = re.search(r"Tactic [`']decide[`'] proved that the proposition\s+"
                           r"1\s*=\s*-1\s+is false", stdout)
    if len(errors) != 1 or not diagnostic or re.search(r"(?mi)\bwarning:", stdout):
        raise ReplayFailure("Negative failure was not the intended decide rejection of 1 = -1")


def run_process(args: list[str], cwd: Path, env: dict[str, str], timeout: float,
                stdout_path: Path, stderr_path: Path) -> tuple[int, float]:
    if timeout <= 0:
        raise ReplayFailure("Global successor wall-clock budget exhausted before next unit")
    start = time.monotonic()
    with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
        proc = subprocess.Popen(args, cwd=cwd, env=env, stdout=out, stderr=err,
                                start_new_session=True)
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            # No task is left running. This runner is for the specified macOS/Unix host.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            raise ReplayFailure(f"External wall-clock cap reached ({timeout:.3f}s): {args[-1]}") from exc
        except BaseException:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            raise
    return rc, time.monotonic() - start


def replay(root: Path, compiler: Path, output: Path) -> None:
    start = time.monotonic()
    excluded_dependency = 0.0
    report: dict[str, Any] = {
        "status": "RUNNING_NOT_YET_ACCEPTED", "compiler_requested": str(compiler),
        "required_version": VERSION, "required_commit": COMMIT,
        "per_unit_wall_limit_seconds": UNIT_LIMIT,
        "successor_total_wall_limit_seconds": TOTAL_LIMIT,
        "allowed_axioms": sorted(ALLOWED), "units": [],
        "observed_axiom_dependencies": {},
    }
    report_path = output / "OPERATOR_REPLAY.json"
    current = "preflight"
    try:
        audit(root)
        verify_manifest(root)
        require(compiler.is_absolute() and compiler.is_file(),
                "Supply the existing exact compiler at an absolute path; no PATH/elan fallback")
        source_dir = output / "source"
        logs = output / "logs"
        source_dir.mkdir()
        logs.mkdir()
        plan = json.loads((root / "REPLAY_PLAN.json").read_text(encoding="utf-8"))
        for rel in plan["positive_units"] + plan["negative_units"]:
            src, dst = root / rel, source_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            data = src.read_bytes()
            dst.write_bytes(data)
            require(dst.read_bytes() == data, "Source-copy mismatch")
        env = os.environ.copy()
        for key in ("LEAN_PATH", "LEAN_SRC_PATH", "LEAN_SYSROOT"):
            env.pop(key, None)
        env["LEAN_PATH"] = str(source_dir.resolve())
        versions: dict[str, str] = {}
        for flag in ("--short-version", "--githash", "--version"):
            label = flag[2:]
            out, err = logs / f"compiler-{label}.stdout", logs / f"compiler-{label}.stderr"
            rc, _ = run_process([str(compiler), flag], source_dir, env, 10.0, out, err)
            require(rc == 0 and not err.read_bytes(), f"Compiler {flag} check failed")
            versions[flag] = out.read_text(encoding="utf-8")
        validate_version(versions["--short-version"], versions["--githash"])
        report["observed_version_output"] = versions

        for rel in plan["positive_units"] + plan["negative_units"]:
            current = rel
            stage_start = time.monotonic()
            dependency = rel == "PR1497Bridge.lean"
            remaining = TOTAL_LIMIT - (stage_start - start - excluded_dependency)
            timeout = UNIT_LIMIT if dependency else min(UNIT_LIMIT, remaining)
            src = source_dir / rel
            olean = src.with_suffix(".olean")
            require(not olean.exists(), f"Non-fresh output {olean}")
            label = rel[:-5].replace("/", "_")
            out, err = logs / f"{label}.stdout", logs / f"{label}.stderr"
            record: dict[str, Any] = {
                "source": rel, "source_utf8_bytes": len(src.read_bytes()),
                "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
                "stdout_log": str(out.relative_to(output)), "stderr_log": str(err.relative_to(output)),
                "external_timeout_seconds": timeout, "accepted": False,
            }
            report["units"].append(record)
            rc, elapsed = run_process([str(compiler), "-o", str(olean), rel], source_dir, env,
                                      timeout, out, err)
            record.update(returncode=rc, process_seconds=elapsed,
                          olean_produced=olean.is_file() and olean.stat().st_size > 0)
            stdout, stderr = out.read_text(encoding="utf-8"), err.read_text(encoding="utf-8")
            if rel in plan["positive_units"]:
                actual = check_positive(src.read_text(encoding="utf-8"), stdout, stderr,
                                        rc, record["olean_produced"])
                require(not set(actual) & set(report["observed_axiom_dependencies"]),
                        "Duplicate declaration across compiled units")
                report["observed_axiom_dependencies"].update(actual)
                record["axiom_query_count"] = len(actual)
                record["olean_sha256"] = hashlib.sha256(olean.read_bytes()).hexdigest()
            else:
                check_negative(stdout, stderr, rc, record["olean_produced"])
                record["negative_control"] = "intended decide rejection of 1 = -1"
            record["accepted"] = True
            if dependency:
                excluded_dependency += time.monotonic() - stage_start
            require(time.monotonic() - start - excluded_dependency <= TOTAL_LIMIT,
                    "Global successor wall-clock budget exhausted")
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(f"ACCEPTED {rel}: {elapsed:.3f}s", flush=True)
        report["status"] = "ACCEPTED_ON_THIS_ACTUAL_OPERATOR_REPLAY"
        report["complete_named_axiom_census"] = len(report["observed_axiom_dependencies"])
    except BaseException as exc:
        report["status"] = "STOPPED_NOT_ACCEPTED"
        report["stopped_at"] = current
        report["failure"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        report["total_seconds"] = time.monotonic() - start
        report["excluded_unchanged_dependency_seconds"] = excluded_dependency
        report["successor_seconds_including_preflight"] = report["total_seconds"] - excluded_dependency
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Actual operator report: {report_path}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", type=Path, default=Path(LEAN))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path,
                        help="New output directory; it must not already exist")
    args = parser.parse_args()
    if args.output is None:
        output = Path(tempfile.mkdtemp(prefix="p112-lean430-replay-"))
    else:
        output = args.output.resolve()
        output.mkdir(parents=True, exist_ok=False)
    print(f"Fresh replay directory: {output}", flush=True)
    replay(args.root.resolve(), args.lean, output)


if __name__ == "__main__":
    main()
