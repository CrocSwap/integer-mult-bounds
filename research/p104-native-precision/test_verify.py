#!/usr/bin/env python3
"""Independent executions and packaging controls for the finite precision bound."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_precision", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def main():
    V.authenticate()
    word = json.loads((V.ROOT / (V.SOURCE + "inputs/LOWRANK-WITNESS.json")).read_text())
    result = V.forward(word)
    inputs = {name: Q((i % 11) - 5, 7) for i, name in enumerate(word["initial_frames"])}
    defects = {index: Q((-1 if index % 2 else 1) * (1 + index % 3), 1 + index % 7)
               for index in result["kinds"]}
    noisy = V.injected_run(word, defects=defects, inputs=inputs)
    for name in noisy:
        expected = sum((a*inputs[src] for src, a in result["rows"][name].items()), Q(0))
        expected += sum((a*defects[index] for index, a in result["errors"][name].items()), Q(0))
        V.need(noisy[name] == expected, "independent dense rational defect execution")
    # One impulse per distinct native rank, every private-copy lifetime, and boundary additions.
    selected = {0, len(word["program"])-1}
    rank_seen = set()
    for index, event in enumerate(word["program"]):
        if event[0] == "copy":
            selected.add(index)
        if event[0] == "transport" and event[4] not in rank_seen:
            selected.add(index)
            rank_seen.add(event[4])
    for index in sorted(selected):
        actual = V.injected_run(word, defects={index: Q(1)})
        V.need(all(actual[name] == result["errors"][name].get(index, Q(0)) for name in actual),
               "individual forward physical-role response")
    with tempfile.TemporaryDirectory(prefix="p104-precision-export-") as temp:
        root = Path(temp)
        destination = root / "research" / HERE.name
        shutil.copytree(HERE, destination, ignore=shutil.ignore_patterns("__pycache__"))
        for name in V.INPUTS:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(V.ROOT / name, target)
        V.authenticate(root)
        victim = root / (V.SOURCE + "vendor/native_verify.py")
        original = victim.read_bytes()
        victim.write_bytes(b"raise RuntimeError('must not execute a changed interpreter')\n")
        try:
            V.authenticate(root)
        except ValueError as error:
            V.need("source authentication" in str(error), "source drift rejected for the intended reason")
        else:
            raise ValueError("modified interpreter authenticated")
        victim.write_bytes(original)
        files = [path for path in root.rglob("*") if path.is_file()]
        before = {str(path.relative_to(root)): path.read_bytes() for path in files}
        for path in files:
            path.chmod(0o444)
        directories = sorted((path for path in root.rglob("*") if path.is_dir()), reverse=True)
        for path in directories:
            path.chmod(0o555)
        try:
            replay = subprocess.run([sys.executable, "-I", "-O", "-B", str(destination / "verify.py")],
                                    cwd=root, capture_output=True, text=True, timeout=300)
            V.need(replay.returncode == 0 and "PASS_P104_NATIVE_PRECISION" in replay.stdout,
                   "optimized read-only export replay: " + replay.stdout + replay.stderr)
            after = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            V.need(before == after, "read-only export preserved every byte")
        finally:
            for path in directories:
                path.chmod(0o755)
            for path in files:
                path.chmod(0o644)
    print(f"PASS_P104_NATIVE_PRECISION_TESTS dense_defects={len(defects)} independent_impulses={len(selected)} "
          "source_drift=reject read_only_optimized_export=pass")


if __name__ == "__main__":
    main()
