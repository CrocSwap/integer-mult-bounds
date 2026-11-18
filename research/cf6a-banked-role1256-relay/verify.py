"""Rebuild the role-1256 banked application and compare its scientific receipts."""

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def check_assets():
    manifest = read(PACKAGE / "ASSETS.json")
    for record in manifest["files"]:
        path = PACKAGE / record["path"]
        require(path.is_file() and not path.is_symlink(), f"Missing package input {path}")
        require(path.stat().st_size == record["bytes"] and digest(path) == record["sha256"],
                f"Incorrect package bytes for {record['path']}")


def invoke(tmp, name, script, *arguments, directory=False, expected_path=None):
    target = tmp / name if directory else tmp / f"{name}.json"
    if directory:
        target.mkdir()
    command = [sys.executable, "-I", "-B", "-X", f"pycache_prefix={tmp / 'bytecode'}",
               str(PACKAGE / script), *map(str, arguments), "--out", str(target)]
    print(f"Replaying {name}", flush=True)
    subprocess.run(command, cwd=PACKAGE, check=True)
    result = target / f"{name}.json" if directory else target
    actual = read(result)
    expected = read(expected_path or PACKAGE / "evidence" / f"{name}.json")
    if name == "NATIVE":
        start = target / "START.json"
        require(actual["start_sha256"] == digest(start) and
                read(start)["runner_sha256"] == digest(PACKAGE / script) and
                read(start)["started_at"] == actual["started_at"] and
                datetime.fromisoformat(actual["started_at"]) <= datetime.fromisoformat(actual["completed_at"]) and
                actual["cpu_seconds"] > 0 and actual["peak_rss_kib"] > 0,
                "Invalid native run metadata")
        for key in ("started_at", "completed_at", "start_sha256", "cpu_seconds", "peak_rss_kib"):
            del actual[key], expected[key]
    require(actual == expected, f"Scientific receipt differs for {name}")
    return result


def replay(group):
    check_assets()
    with TemporaryDirectory(prefix="cf6a-relay-") as temp:
        tmp = Path(temp)
        if group == "core":
            invoke(tmp, "OPERATOR", "check_operator.py")
            physical = invoke(tmp, "PHYSICAL", "physical.py")
            caller = invoke(tmp, "CALLER", "caller.py")
            invoke(tmp, "PRICE", "price.py", "--caller-proof", caller, "--physical", physical)
            invoke(tmp, "INDEPENDENT", "review/check.py")
            invoke(tmp, "JOIN", "review/check_join.py", expected_path=PACKAGE / "review/JOIN.json")
        elif group == "native":
            native = invoke(tmp, "NATIVE", "native.py", directory=True)
            require(digest(native.parent / "RECIPES.json.gz") ==
                    digest(PACKAGE / "native_support/RECIPES.json.gz"),
                    "Ordered native recipes differ from the committed catalogue")
        else:
            invoke(tmp, "DENSE", "dense.py")
    print(f"PASS_CF6A_ROLE1256_{group.upper()}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=("core", "native", "dense"))
    replay(parser.parse_args().group)
