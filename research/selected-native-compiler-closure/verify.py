"""Source-authenticated standalone replay of the joint construction evidence.

Authenticate every vendored scientific input before either engine is loaded.
Execute Python source directly so stale bytecode cannot replace checked bytes.
This checks finite evidence, not the universal theorem or retained contracts.
"""
from contextlib import redirect_stdout
from hashlib import sha1, sha256
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256 mismatch: " + pin["local"])
    blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    need(sha1(blob).hexdigest() == pin["git_blob"], "source Git blob mismatch: " + pin["local"])


def check_sources():
    manifest = json.loads((HERE / "ORIGINS.json").read_text())
    inputs = [p for p in manifest["files"] if p["usage"] == "input"]
    need(len(inputs) >= 5, "missing scientific source pins")
    checked, controls = [], []
    for pin in inputs:
        path = HERE / pin["local"]
        need(path.resolve().is_relative_to(HERE), "input escapes package")
        raw = path.read_bytes()
        authenticate(raw, pin)
        checked.append({"path": pin["local"], "sha256": pin["sha256"]})
        try:
            authenticate(raw + b"\n", pin)
        except ValueError as error:
            need(str(error).startswith("source SHA256 mismatch:"), "wrong binding control gate")
            controls.append(pin["local"])
        else:
            raise ValueError("source mutation survived: " + pin["local"])
    return {"authenticated": checked, "dirty_byte_controls_rejected": controls}


def run_engine(filename, marker):
    path = HERE / filename
    scope = {"__name__": "review_" + path.stem, "__file__": str(path)}
    exec(compile(path.read_bytes(), str(path), "exec"), scope)
    capture = io.StringIO()
    with redirect_stdout(capture):
        scope["main"]()
    lines = capture.getvalue().strip().splitlines()
    need(lines and lines[-1] == marker, "missing engine completion: " + filename)
    return json.loads("\n".join(lines[:-1]))


def main():
    sources = check_sources()
    if sys.argv[1:] == ["--binding-only"]:
        print(json.dumps(sources, indent=2))
        print("PASS_JOINT_SOURCE_BINDING")
        return
    need(not sys.argv[1:], "usage: verify.py [--binding-only]")
    funding = run_engine("independent_funding.py", "PASS_INDEPENDENT_SELECTED_JOINT_FUNDING")
    syntax = run_engine("check_joint_syntax.py", "PASS_JOINT_FULL_FIELD_SYNTAX")
    result = {"status": "finite checks passed; universal theorem provisional",
              "sources": sources, "independent_funding": funding,
              "full_field_syntax": syntax}
    print(json.dumps(result, indent=2))
    print("PASS_SELECTED_JOINT_COMPILER_NATIVE_EVIDENCE")


if __name__ == "__main__":
    main()
