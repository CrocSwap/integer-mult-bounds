"""Authenticate retained source bytes before the deterministic route cross-review."""
from hashlib import sha1, sha256
from pathlib import Path
from types import ModuleType
import json
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    rows = [row for row in sources["files"] if "local_input" in row]
    declared = json.loads((HERE / "VERIFY.json").read_text())["inputs"]
    require(sorted(row["local_input"] for row in rows) == sorted(declared),
            "all retained source inputs must be declared")
    for row in rows:
        path = REPO / row["local_input"]
        require(path.is_relative_to(HERE / "inputs") and path.is_file() and not path.is_symlink(),
                "retained source must be a package-local regular file")
        data = path.read_bytes()
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == row["git_blob"] and sha256(data).hexdigest() == row["sha256"],
                "source-byte mismatch: " + row["local_input"])
    return len(rows)


def main():
    count = authenticate()
    module = ModuleType("independent_composition")
    path = HERE / "check_composition.py"
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", dont_inherit=True), module.__dict__)
    result = module.run()
    if "--record" not in sys.argv:
        require(result == json.loads((HERE / "RESULT.json").read_text()),
                "complete deterministic review receipt changed")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("AUTHENTICATED_RETAINED_INPUTS", count)
    print("PASS_GRADE14_WEIGHTED_ROUTE_CROSS_REVIEW")


if __name__ == "__main__":
    main()
