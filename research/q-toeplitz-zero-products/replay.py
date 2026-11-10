"""Source-bound opt-in replay. The predecessor's files remain unchanged."""

import hashlib
import json
from pathlib import Path
from types import ModuleType

from kernel import multiply

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/q-toeplitz-factorization/verify.py"


def check_sources(root: Path = ROOT) -> dict[str, bytes]:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    if len(manifest["files"]) != 5:
        raise ValueError("unexpected source inventory")
    payloads = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = root / row["path"]
            if path.stat().st_size > 131072:
                raise ValueError("source exceeds fixed 128 KiB read bound")
            payload = path.read_bytes()
            if hashlib.sha256(payload).hexdigest() != row["sha256"]:
                raise ValueError(f"source changed: {row['path']}")
            payloads[row["path"]] = payload
    if len(payloads) != 3:
        raise ValueError("unexpected live input inventory")
    return payloads


def load_source() -> ModuleType:
    payloads = check_sources()
    module = ModuleType("q_toeplitz_predecessor")
    module.__file__ = str(ROOT / SOURCE)
    # Compile the authenticated bytes, rather than accepting a cached .pyc.
    exec(compile(payloads[SOURCE], module.__file__, "exec"), module.__dict__)
    return module


def main() -> None:
    source = load_source()
    source.multiply = multiply
    source.main()


if __name__ == "__main__":
    main()
