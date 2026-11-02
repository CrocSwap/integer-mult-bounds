"""Run the complete frozen primary CLI with one optional exact kernel binding."""

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
KERNEL_PATH = HERE / "exp_series.py"
KERNEL = {"__name__": "integer_exp_series"}
exec(compile(KERNEL_PATH.read_bytes(), str(KERNEL_PATH), "exec"), KERNEL)
exp_interval = KERNEL["exp_interval"]
ORIGINS_SHA256 = "29931ccabb96aa7fe7798baca1baecdaa05665344be10cfa23cf7e2c288ddd25"
SOURCE_SHA256 = "2f3306ed5c52a71bf7f16b5c76e253d49ce20c37a0af3f047e2b2a24809ad478"


def check_payload(raw: bytes, expected: str, limit: int, label: str) -> bytes:
    if len(raw) > limit or sha256(raw).hexdigest() != expected:
        raise ValueError("retained source SHA256/size: " + label)
    return raw


def checked_bytes(path: Path, expected: str, limit: int = 4_194_304) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    return check_payload(raw, expected, limit, path.name)


def authenticate(root: Path = HERE) -> bytes:
    raw = checked_bytes(root / "ORIGINS.json", ORIGINS_SHA256, 32_768)
    origin = json.loads(raw)
    for row in origin["files"]:
        data = checked_bytes(root / "source" / row["path"], row["sha256"])
        if len(data) != row["bytes"]:
            raise ValueError("retained source byte count")
    return checked_bytes(root / "source/verify_tariff.py", SOURCE_SHA256)


def load_primary(root: Path = HERE) -> tuple[dict, ast.Module]:
    raw = authenticate(root)
    source = root / "source/verify_tariff.py"
    tree = ast.parse(raw, filename=str(source))
    if not isinstance(tree.body[-1], ast.If):
        raise ValueError("frozen primary CLI boundary")
    namespace = {"__name__": "retained_tariff", "__file__": str(source)}
    exec(compile(tree, str(source), "exec"), namespace)
    if namespace["EXP_DEGREE"] != 24:
        raise ValueError("frozen Taylor degree")
    return namespace, ast.Module(body=[tree.body[-1]], type_ignores=[])


def replay(arm: str) -> None:
    if arm not in ("original", "integer"):
        raise ValueError("unknown replay arm")
    namespace, cli = load_primary()
    if arm == "integer":
        namespace["exp_positive"] = exp_interval
    old_argv = sys.argv
    try:
        sys.argv = [namespace["__file__"]]
        namespace["__name__"] = "__main__"
        exec(compile(cli, namespace["__file__"], "exec"), namespace)
    finally:
        sys.argv = old_argv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=("original", "integer"), default="integer")
    replay(parser.parse_args().arm)
