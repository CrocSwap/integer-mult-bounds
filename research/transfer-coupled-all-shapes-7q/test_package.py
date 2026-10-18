#!/usr/bin/env python3
"""Package fault controls for transfer-coupled 7q obstruction. Wentao Li + AI."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PKG_NAME = "transfer-coupled-all-shapes-7q"


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_TEST: {message}")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True)


def seed_tree(tmp_path: Path):
    research = tmp_path / "research" / PKG_NAME
    shutil.copytree(HERE, research)
    pinned = tmp_path / "research" / "mutable-source-shear-cost"
    pinned.mkdir(parents=True)
    shutil.copy2(
        ROOT / "research" / "mutable-source-shear-cost" / "CERTIFICATE.json",
        pinned / "CERTIFICATE.json",
    )
    return research


def main():
    # 1) X=0 lemma + tariff arithmetic smoke (fast; full census is verify/independent).
    proc = run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            "import sys; sys.path.insert(0, %r); from model import x0_covering_count_511, tariff_qrx, need, champion_checks; "
            "x=x0_covering_count_511(); need(x['covering']==0,'x0'); "
            "need(tariff_qrx(7,84,2,1)==439,'floor'); "
            "need(tariff_qrx(7,86,0,1)==439,'floor86'); "
            "champion_checks(); print('PASS_SMOKE_X0_TARIFF_CHAMPIONS')"
            % str(HERE),
        ]
    )
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_SMOKE_X0_TARIFF_CHAMPIONS" in proc.stdout, proc.stdout)

    # 2) Same smoke under -O (need() admission).
    proc = run(
        [
            sys.executable,
            "-I",
            "-O",
            "-B",
            "-c",
            "import sys; sys.path.insert(0, %r); from model import x0_covering_count_511, tariff_qrx, need, champion_checks; "
            "x=x0_covering_count_511(); need(x['covering']==0,'x0'); "
            "need(tariff_qrx(7,84,2,1)==439,'floor'); "
            "champion_checks(); print('PASS_SMOKE_O_NEED')"
            % str(HERE),
        ]
    )
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_SMOKE_O_NEED" in proc.stdout, proc.stdout)

    # 3) Certificate claim corruption fails against live census.
    with tempfile.TemporaryDirectory() as tmp:
        research = seed_tree(Path(tmp))
        cert = research / "CERTIFICATE.json"
        data = json.loads(cert.read_text(encoding="utf-8"))
        data["claim"]["global_covering_min_R"] = 0
        cert.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        proc = run([sys.executable, "-I", "-B", str(research / "verify.py")], cwd=tmp)
        need(proc.returncode != 0, "corrupted certificate should fail")

    # 4) Source pin corruption rejection.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        research = tmp_path / "research" / PKG_NAME
        shutil.copytree(HERE, research)
        pinned = tmp_path / "research" / "mutable-source-shear-cost"
        pinned.mkdir(parents=True)
        src = ROOT / "research" / "mutable-source-shear-cost" / "CERTIFICATE.json"
        (pinned / "CERTIFICATE.json").write_bytes(src.read_bytes() + b"\n")
        proc = run([sys.executable, "-I", "-B", str(research / "verify.py")], cwd=tmp_path)
        need(proc.returncode != 0, "source drift should fail")

    # 5) Duplicate JSON key rejection.
    with tempfile.TemporaryDirectory() as tmp:
        research = seed_tree(Path(tmp))
        cert = research / "CERTIFICATE.json"
        raw = cert.read_text(encoding="utf-8")
        corrupted = raw.replace(
            '"schema_version": 1,',
            '"schema_version": 1,\n  "schema_version": 2,',
            1,
        )
        need(corrupted != raw, "failed to inject duplicate key")
        cert.write_text(corrupted, encoding="utf-8")
        proc = run([sys.executable, "-I", "-B", str(research / "verify.py")], cwd=tmp)
        need(proc.returncode != 0, "duplicate JSON key should fail")

    # 6) Independent tariff helper matches the abstract invoice.
    proc = run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            "def tariff(q,r,x,c=1): return 38*q+2*r+2*x+c\n"
            "assert tariff(7,84,2,1)==439\n"
            "assert tariff(7,86,0,1)==439\n"
            "assert tariff(7,84,0,1)==435\n"
            "print('PASS_INDEPENDENT_TARIFF_FN')",
        ]
    )
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_INDEPENDENT_TARIFF_FN" in proc.stdout, proc.stdout)

    print("PASS_TRANSFER_COUPLED_7Q_PACKAGE_TESTS groups=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
