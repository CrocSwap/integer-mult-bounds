#!/usr/bin/env python3
"""Replay the unchanged PR1240 ceiling against its exact PR1094 context.

Mihir Srivastava (@mihir-s-05), substantial OpenAI Codex assistance.
Apache-2.0. This is historical reproduction, not a current supplier bound.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "research/historical-complex-ceiling-replay"
ORIGINAL = "research/complex-local-word-ceiling"
SELECTED = "certificates/selected-result.json"
RETAINED = PACKAGE + "/historical-selected.json"
PREVIOUS = "research/community-frontier1042-audit/ASSEMBLY.json"
INDEPENDENT = "research/community-frontier1094-audit/INDEPENDENT1094.json"
# Complete read closure of the unchanged verifier: code, expected output,
# original pins and the previously unpinned #1042 comparison. Only RETAINED
# moves, to SELECTED inside a fresh temporary tree.
PINS = {
    RETAINED: "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
    "certificates/checkpoints/frontier1042.json": "207d1f49f113c585024b9d3c17eadbb8b1be17c1321e3d190aabe2f18ce1c5b7",
    PREVIOUS: "093f35445812ea96fe1bfe6a3af7d769cb7f274e08f4fb30f71a17ed1161e54e",
    "research/community-frontier1094-audit/ASSEMBLY.json": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    INDEPENDENT: "301fb8a0e4ab7e3c383ff974c54c08178283b2a3453c5282757f692a3c7a4bfd",
    ORIGINAL + "/RESULT.json": "d91d6c46509875abf1f61de67c2609656d3dc685451299f83caa6f922493692d",
    ORIGINAL + "/SOURCES.json": "df587fbef4bb7c00f827f4a4eaddf2f4910ef19f6decf32984f1d32ac036de6a",
    ORIGINAL + "/ceiling.py": "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
    ORIGINAL + "/verify.py": "06b59955c69a2e7f49aa031d2ebaac2f39dbe107f4087122704f2a37ce9806d5",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def authenticated_inputs(root):
    payload = {}
    for name, expected in PINS.items():
        path = root / name
        require(path.is_file() and not path.is_symlink(), "Missing/non-file input: " + name)
        raw = path.read_bytes()
        require(digest(raw) == expected, "Input SHA256 mismatch: " + name)
        payload[SELECTED if name == RETAINED else name] = raw
    # Reconcile the historical manifest itself, not just the new digest table.
    historical = json.loads(payload[ORIGINAL + "/SOURCES.json"])
    for row in historical["files"]:
        if row["usage"] == "input":
            require(row["path"] in payload, "Uncovered historical input: " + row["path"])
            require(digest(payload[row["path"]]) == row["sha256"],
                    "Historical source pin mismatch: " + row["path"])
    return payload


def write_payload(root, payload):
    for name, raw in payload.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)


def run_original(root):
    # No bytecode or unrelated code is copied. -I ignores inherited Python
    # environment options; explicitly retain the requested optimization level.
    options = ["-I", "-W", "error", "-B"]
    if sys.flags.optimize:
        options.append("-" + "O" * sys.flags.optimize)
    return subprocess.run(
        [sys.executable, *options, str(root / ORIGINAL / "verify.py")],
        cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=90,
        check=False,
    )


def require_unchanged(root, payload):
    for name, raw in payload.items():
        require((root / name).is_file() and (root / name).read_bytes() == raw,
                "Replay changed input: " + name)


def input_controls(payload):
    """Every declared input must reject both corruption and absence."""
    original_paths = {RETAINED if p == SELECTED else p: raw for p, raw in payload.items()}
    with tempfile.TemporaryDirectory(prefix="ceiling-input-controls-") as directory:
        root = Path(directory)
        write_payload(root, original_paths)
        for name, raw in original_paths.items():
            path = root / name
            path.write_bytes(raw + b"\n")
            try:
                authenticated_inputs(root)
            except ValueError as error:
                require(str(error) == "Input SHA256 mismatch: " + name,
                        "Wrong corruption rejection: " + str(error))
            else:
                raise ValueError("Corrupt input accepted: " + name)
            path.unlink()
            try:
                authenticated_inputs(root)
            except ValueError as error:
                require(str(error) == "Missing/non-file input: " + name,
                        "Wrong omission rejection: " + str(error))
            else:
                raise ValueError("Missing input accepted: " + name)
            path.write_bytes(raw)
    return 2 * len(original_paths)


def scientific_controls(payload):
    """Exercise the old guards on disposable data after the wrapper's pin gate.

    The original checker code stays unchanged; these intentional mutations
    require it to independently reject the damaged scientific evidence.
    """
    cases = []
    independent = json.loads(payload[INDEPENDENT])
    independent["owner"]["profile"]["1"] += 1
    cases.append((INDEPENDENT, independent, "profile mismatch"))
    previous = json.loads(payload[PREVIOUS])
    previous["complex_lower"] = "1"
    cases.append((PREVIOUS, previous, "previous endpoint above the ceiling"))
    receipt = json.loads(payload[ORIGINAL + "/RESULT.json"])
    receipt["status"] = "INVALID_CONTROL"
    cases.append((ORIGINAL + "/RESULT.json", receipt, "RESULT.json differs"))
    for name, damaged, message in cases:
        with tempfile.TemporaryDirectory(prefix="ceiling-science-control-") as directory:
            root = Path(directory)
            write_payload(root, payload)
            (root / name).write_text(json.dumps(damaged), encoding="utf-8")
            result = run_original(root)
            require(result.returncode != 0 and result.stdout.strip() == "FAIL: " + message,
                    "Historical guard did not reject: " + message + "\n" + result.stderr)
    return len(cases)


def main():
    payload = authenticated_inputs(ROOT)
    receipt = json.loads(payload[ORIGINAL + "/RESULT.json"])
    expected = (receipt["status"] + " a_ceiling " + receipt["ceiling"]["a_ceiling_decimal"]
                + " kappa<= " + receipt["ceiling"]["kappa_upper_bound"])
    # The live selection is not an executable input. If present, ensure it is
    # byte-identical at return; Git-free exports need not contain it.
    active = ROOT / SELECTED
    active_before = active.read_bytes() if active.is_file() else None
    with tempfile.TemporaryDirectory(prefix="historical-complex-ceiling-") as directory:
        root = Path(directory)
        write_payload(root, payload)
        result = run_original(root)
        require(result.returncode == 0, "Historical replay failed:\n" + result.stdout + result.stderr)
        require(result.stdout.strip() == expected and not result.stderr,
                "Unexpected historical output:\n" + result.stdout + result.stderr)
        require_unchanged(root, payload)
    controls = input_controls(payload)
    science = scientific_controls(payload)
    require(authenticated_inputs(ROOT) == payload, "Source inputs changed during replay")
    if active_before is not None:
        require(active.read_bytes() == active_before, "Live selected record changed")
    print(expected)
    print("PASS_HISTORICAL_COMPLEX_CEILING_REPLAY",
          "context=PR1094", "current_supplier_bound=false",
          "inputs=" + str(len(PINS)), "input_controls=" + str(controls),
          "scientific_controls=" + str(science), "unchanged=true")


if __name__ == "__main__":
    main()
