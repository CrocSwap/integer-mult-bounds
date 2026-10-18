#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Isolated CLI mutation/relocation tests; never edits the supplied package."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    checker = Path(__file__).with_name("independent.py").resolve()
    receipt = Path(__file__).with_name("INDEPENDENT.json").read_bytes()
    source = args.package.resolve().parent.parent / "research/universal-connector-boundary/CERTIFICATE.json"
    source_bytes = source.read_bytes()
    result_bytes = (args.package / "RESULT.json").read_bytes()
    count = 0
    with tempfile.TemporaryDirectory(prefix="tariff-independent-") as tmp:
        work = Path(tmp)
        root = work / "relocated"
        package = root / "research/mutable-source-uniform-tariff"
        package.mkdir(parents=True)
        pinfile = root / "research/universal-connector-boundary/CERTIFICATE.json"
        pinfile.parent.mkdir()
        pinfile.write_bytes(source_bytes)
        parent_result = package / "RESULT.json"
        own_result = package / "INDEPENDENT.json"
        parent_result.write_bytes(result_bytes)
        own_result.write_bytes(receipt)

        def snapshot():
            return [(str(p.relative_to(root)), p.stat().st_mode,
                     hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
                    for p in sorted(root.rglob("*"))]

        def run(name, good, optimized=False, extra=()):
            nonlocal count
            before = snapshot()
            cmd = [sys.executable, "-I", "-B"] + (["-O"] if optimized else []) + [str(checker), "--package", str(package), *extra]
            execution = subprocess.run(cmd, capture_output=True, text=True, cwd=work,
                                       env={"PATH": "/no-programs", "PYTHONDONTWRITEBYTECODE": "1"}, timeout=30)
            need((execution.returncode == 0) == good,
                 f"{name}: unexpected exit {execution.returncode}: {execution.stdout} {execution.stderr}")
            need(snapshot() == before, f"{name}: verification changed input files")
            count += 1
            print(f"PASS {name}{' [-O]' if optimized else ''}")

        for optimized in (False, True):
            for path in (pinfile, parent_result, own_result):
                path.chmod(0o444)
            for path in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
                path.chmod(0o555)
            root.chmod(0o555)
            run("read-only relocated default verification", True, optimized)
            for path in (root, *sorted(p for p in root.rglob("*") if p.is_dir())):
                path.chmod(0o755)
            for path in (pinfile, parent_result, own_result):
                path.chmod(0o644)

            own_result.unlink()
            run("missing required receipt", False, optimized)
            own_result.write_bytes(receipt)
            pinfile.write_bytes(source_bytes + b" ")
            run("changed pinned input", False, optimized)
            pinfile.write_bytes(source_bytes)
            mutations = {
                "bool schema": lambda x: x.__setitem__("schema_version", True),
                "float census": lambda x: x["nine_points"].__setitem__("count", 2600.0),
                "wrong histogram": lambda x: x["pairings"]["histogram"].__setitem__("31", 23),
                "wrong source projection": lambda x: x["source_projections"]["identity_by_length"].__setitem__(3, 1),
                "wrong root word": lambda x: x["witnesses"]["four_x"]["root_word"].pop(),
                "wrong invoice": lambda x: x["witnesses"]["extra_output"].__setitem__("unit_tariff", 2811),
                "bad digest type": lambda x: x["nine_points"].__setitem__("records_sha256", False),
                "unexpected field": lambda x: x.__setitem__("surprise", 1),
            }
            for label, mutate in mutations.items():
                data = json.loads(result_bytes)
                mutate(data)
                parent_result.write_text(json.dumps(data))
                run(label, False, optimized)
            parent_result.write_bytes(b'{"schema_version":1,"schema_version":1}')
            run("duplicate key", False, optimized)
            parent_result.write_bytes(b'{"schema_version":NaN}')
            run("nonfinite JSON", False, optimized)
            parent_result.write_bytes(result_bytes)
            own_data = json.loads(receipt)
            own_data["root_checks"]["forward_and_reverse"] = 1
            own_result.write_text(json.dumps(own_data))
            run("receipt bool-to-int corruption", False, optimized)
            own_result.write_bytes(receipt)
            run("export inside input checkout", False, optimized,
                ("--write-receipt", str(root / "blocked.json")))
            run("export would overwrite file", False, optimized,
                ("--write-receipt", str(checker)))
            alias = work / f"alias-{optimized}"
            alias.symlink_to(root, target_is_directory=True)
            run("symlink export into input checkout", False, optimized,
                ("--write-receipt", str(alias / "blocked.json")))
            exported = work / f"external-{optimized}.json"
            run("explicit external export", True, optimized, ("--write-receipt", str(exported)))
            need(exported.read_bytes() == receipt, "export receipt not reproducible")
            parent_result.unlink()
            run("export still requires parent RESULT", False, optimized,
                ("--write-receipt", str(work / f"missing-parent-{optimized}.json")))
            parent_result.write_bytes(result_bytes)
    print(f"{count} CLI controls passed; package and source were never written")


if __name__ == "__main__":
    main()
