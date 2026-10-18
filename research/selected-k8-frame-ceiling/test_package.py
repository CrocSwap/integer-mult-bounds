#!/usr/bin/env python3
"""Native-auditor fixtures, finite-domain controls and external corruptions."""
from contextlib import redirect_stdout
import copy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def need(ok, why):
    if not ok:
        raise ValueError(why)


def fails(action, text):
    try:
        action()
    except (ValueError, RuntimeError, AssertionError) as error:
        need(text in str(error), "wrong failure: "+str(error))
    else:
        raise ValueError("control did not reject: "+text)


def inventory(path):
    return {str(f.relative_to(path)): sha256(f.read_bytes()).hexdigest()
            for f in path.rglob("*") if f.is_file()}


def main():
    V = module("tested_k8_primary", HERE / "verify.py")
    I = module("tested_k8_independent", HERE / "independent.py")
    U = V.U
    U.source_bindings()
    M, C, auditor = U.retained("frame_model.py"), U.retained("ceiling.py"), U.retained("audit_local.py")
    word = U.word()
    model = M.Model(word)
    duals = U.duals()
    bounds = {"cap": V.charges(C, V.BASE_HI), "target": V.charges(C, V.TARGET)}
    controls = []
    with tempfile.TemporaryDirectory(prefix="k8-frame-controls-") as directory:
        root = Path(directory)
        # The existing all-column auditor checks scalar endpoints in both
        # orientations, exact frame bills and the low-end cones independently.
        native_profiles = {}
        for label, assignment in (("baseline", model.baseline()),
                                  ("all-upper-frames", {n: model.hi[n] for n in model.domain})):
            fixture = copy.deepcopy(word)
            for (kind, i), f in assignment.items():
                need(kind == "G", "gate node")
                if i < len(word["A"]):
                    fixture["A"][i][-1] = list(f)
                elif i < len(word["A"])+len(word["B"]):
                    fixture["B"][i-len(word["A"])][-1] = list(f)
                else:
                    fixture["early_cleanup"][i-len(word["A"])-len(word["B"])][1] = list(f)
            profile = model.profile(assignment)
            fixture["report"]["local_profile"] = {str(r): n for r, n in profile.items()}
            path, receipt = root/(label+".json.gz"), root/(label+"-audit.json")
            path.write_bytes(gzip.compress(U.canonical(fixture), mtime=0))
            with redirect_stdout(io.StringIO()):
                auditor.run(path, receipt)
            checked = json.loads(receipt.read_text())
            need(checked["status"] == "PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES",
                 "legacy native auditor")
            need(checked["checked_columns"] == 704 and checked["local_profile"] == fixture["report"]["local_profile"],
                 "all-column native fixture coverage")
            native_profiles[label] = profile
        need(native_profiles["baseline"] != native_profiles["all-upper-frames"], "nontrivial legal frame fixture")
        controls.append("baseline-and-all-upper-native-audits-704-columns-both-orientations")

        broken = copy.deepcopy(model)
        node = next(n for n in broken.domain if len(broken.domain[n]) > 2)
        broken.domain[node].pop()
        fails(lambda: V.check_duals(M, broken, duals, bounds), "complete frame interval")
        controls.append("omitted-feasible-frame-choice")

        broken = copy.deepcopy(model)
        broken.centre_children = []
        fails(lambda: V.check_duals(M, broken, duals, bounds), "full fixed and variable cost coverage")
        controls.append("omitted-centre-work")

        broken = copy.deepcopy(model)
        edge = next(e for e in broken.edges if e[0] in broken.domain and e[1] in broken.domain)
        del broken.edges[edge]
        fails(lambda: V.check_duals(M, broken, duals, bounds), "dual row domain")
        controls.append("omitted-common-gate-edge")

        old = I.isqrt
        I.isqrt = lambda n: old(n)+3
        I.child.cache_clear()
        fails(I.main, "square-root oracle calibration")
        I.isqrt = old
        I.child.cache_clear()
        controls.append("invalid-square-root-oracle")

        target = root/"relocated"
        shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        def run(script="verify.py", error=None):
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(target/script)],
                                    cwd=directory, text=True, capture_output=True, timeout=120)
            if error is None:
                need(result.returncode == 0 and "PASS_" in result.stdout, "relocated replay: "+result.stderr)
            else:
                need(result.returncode != 0 and error in result.stderr, "wrong corruption rejection: "+result.stderr)
        before = inventory(target)
        for f in target.rglob("*"):
            if f.is_file():
                f.chmod(0o444)
        run()
        run("independent.py")
        need(inventory(target) == before, "read-only package changed")
        controls.append("both-optimized-read-only-relocated-checkers")
        for f in target.rglob("*"):
            if f.is_file():
                f.chmod(0o644)

        def mutate(label, file, change, error):
            path = target/file
            raw = path.read_bytes()
            path.write_bytes(change(raw))
            try:
                run(error=error)
                controls.append(label)
            finally:
                path.write_bytes(raw)
        def edit(raw, change):
            data = json.loads(raw)
            change(data)
            return U.canonical(data)
        def change_dual(raw, change):
            return gzip.compress(edit(gzip.decompress(raw), change), mtime=0)
        mutate("omitted-dual-component", "DUALS.json.gz",
               lambda raw: change_dual(raw, lambda x: x["components"].pop()), "component coverage")
        def overstate(x):
            record = x["components"][0]["duals"]
            key = next(k for k in record if json.loads(k)[0] == "N")
            record[key]["2"] = str(Q(record[key].get("2", "0"))-1)
        mutate("overstated-dual-objective", "DUALS.json.gz",
               lambda raw: change_dual(raw, overstate), "negative or uncertified reduced cost")
        mutate("false-gate-coverage", "EXPECTED.json",
               lambda raw: edit(raw, lambda x: x.update(free_gates=1740)), "receipt mismatch")
        mutate("missing-source-inventory", "SOURCES.json",
               lambda raw: edit(raw, lambda x: x["files"].pop()), "source inventory")
        mutate("retained-model-drift", "references/frame_model.py", lambda raw: raw+b"\n", "retained source SHA256")
        mutate("selected-word-drift", "references/WORD.json.gz", lambda raw: raw+b"\n", "retained source SHA256")
        mutate("duplicate-receipt-key", "EXPECTED.json", lambda raw: b'{"x":0,"x":1}', "duplicate JSON key")
        mutate("nonfinite-receipt", "EXPECTED.json", lambda raw: b'{"x":NaN}', "noninteger/nonfinite JSON number")
        need(inventory(target) == before, "corruptions not restored")
    print("PASS_K8_FRAME_PACKAGE_CONTROLS", "checks="+str(len(controls)))
    print(json.dumps(controls))
    print("native_profiles="+json.dumps(native_profiles, sort_keys=True))


if __name__ == "__main__":
    main()
