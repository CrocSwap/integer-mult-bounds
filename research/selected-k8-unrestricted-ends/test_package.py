#!/usr/bin/env python3
"""Native fixtures, endpoint/idle-accounting controls and external corruptions.

Adapts Gareth Davidson PR1995 (73e323159d65c974debb180189694fd59144da5f).
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import redirect_stdout
from collections import Counter
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
    M, C, auditor = V.local("model"), U.retained("ceiling.py"), U.retained("audit_local.py")
    P = V.local("materialize")
    word = U.word()
    model = M.Model(word)
    duals = U.duals()
    expected = U.parse((HERE/"EXPECTED.json").read_bytes())
    cap = Q(expected["a_bracket"][1])
    assignment, profile = P.primal(U, model)
    bounds = {"cap": V.charges(C, cap), "target": V.charges(C, V.TARGET)}
    controls = []
    with tempfile.TemporaryDirectory(prefix="k8-frame-controls-") as directory:
        root = Path(directory)
        # The existing all-column auditor checks scalar endpoints in both
        # orientations, exact frame bills and the low-end cones independently.
        native_profiles = {}
        credited = model.baseline()
        recipe = U.parse((HERE/"references/END-RECIPE.json").read_bytes())
        for q, old, new in recipe["ends"]:
            need(list(model.original_caps[q]) == old, "credited old endpoint")
            credited[("E",q)] = M.M.basis(new)
        for i, old, new in recipe["B_frames"]:
            need(word["B"][i][-1] == old, "credited old B frame")
            credited[("G",model.nA+i)] = M.M.basis(new)
        for i, k, old, new in recipe["early_cleanup"]:
            need(word["early_cleanup"][i] == [k,old], "credited old early tail")
            credited[("G",model.nA+model.nB+i)] = M.M.basis(new)
        for label, chosen in (("baseline", model.baseline()), ("credited-two-ends", credited),
                              ("four-end-optimum", assignment)):
            fixture = P.native_word(word,model,chosen)
            for section in ("A","cut","B","precondition","cleanup"):
                need([e[:-1] for e in fixture[section]] == [e[:-1] for e in word[section]],
                     "native scalar chronology unchanged")
            chosen_profile = model.profile(chosen)
            path, receipt = root/(label+".json.gz"), root/(label+"-audit.json")
            path.write_bytes(gzip.compress(U.canonical(fixture), mtime=0))
            with redirect_stdout(io.StringIO()):
                auditor.run(path, receipt)
            checked = json.loads(receipt.read_text())
            need(checked["status"] == "PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES",
                 "legacy native auditor")
            need(checked["checked_columns"] == 704 and checked["local_profile"] == fixture["report"]["local_profile"],
                 "all-column native fixture coverage")
            native_profiles[label] = chosen_profile
        need(len({tuple(sorted(p.items())) for p in native_profiles.values()})==3,
             "three distinct native profiles")
        controls.append("three-704-column-both-orientation-native-audits")

        # A reduced local mass is exposed idle work, not free removed work.
        correct=C.relax(profile,73,896,9,64,V.TARGET)
        fake_upper=(sum((n*C.child_cost(r,73,V.TARGET)[1] for r,n in profile.items()),Q(0))
                    +Q(1646,51)*C.child_cost(51,73,V.TARGET)[1])/Q(896,9)
        need(correct[0]>1 and fake_upper<1,"missing four idle ranks creates a false target pass")
        controls.append("omitted-idle-mass-false-positive")

        # Both directions beyond the old cap are in the new quantified class.
        broken=copy.deepcopy(model)
        endpoint=("E",574)
        rotated=next(f for f in broken.domain[endpoint]
                     if len(f)==8 and not M.M.contained(f,model.original_caps[574]))
        broken.domain[endpoint].remove(rotated)
        fails(lambda:V.check_duals(M,broken,duals,assignment,profile,bounds),"complete frame interval")
        controls.append("omitted-feasible-rotated-end")

        broken=copy.deepcopy(model)
        broken.domain[("E",273)].remove(M.M.FULL)
        fails(lambda:V.check_duals(M,broken,duals,assignment,profile,bounds),"complete frame interval")
        controls.append("omitted-feasible-full-end")

        # The retained vector-subset enumerator is an independent finite oracle
        # through dimension four. For dimension five, unique valid spaces plus
        # the Gaussian count certify coverage, separately matched by bitsets.
        retained_model=U.retained("frame_model.py")
        for k in range(5):
            hi=retained_model.basis([1<<j for j in range(k)])
            need(set(M.complete_interval((),hi))==set(retained_model.interval((),hi)),
                 "quotient enumeration differs from retained oracle")
        spaces=M.quotient_spaces(5)
        need(len(spaces)==len(set(spaces))==V.subspace_count(5)==374,"five-dimensional quotient count")
        need(Counter(map(len,spaces))=={0:1,1:31,2:155,3:155,4:31,5:1},"quotient dimension histogram")
        need({I.frame(f) for f in spaces}==set(I.small_spaces(5)),"separate bitset quotient enumeration")
        controls.append("complete-five-dimensional-quotient-and-smaller-oracles")

        broken = copy.deepcopy(model)
        node = next(n for n in broken.domain if n[0]=="G" and len(broken.domain[n]) > 2)
        broken.domain[node].pop()
        fails(lambda: V.check_duals(M, broken, duals, assignment, profile, bounds), "complete frame interval")
        controls.append("omitted-feasible-frame-choice")

        broken = copy.deepcopy(model)
        broken.centre_children = []
        fails(lambda: V.check_duals(M, broken, duals, assignment, profile, bounds), "full fixed and variable cost coverage")
        controls.append("omitted-centre-work")

        broken = copy.deepcopy(model)
        edge = next(e for e in broken.edges if e[0] in broken.domain and e[1] in broken.domain)
        del broken.edges[edge]
        fails(lambda: V.check_duals(M, broken, duals, assignment, profile, bounds), "dual row domain")
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
                                    cwd=directory, text=True, capture_output=True, timeout=300)
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
            record[key]["1"] = str(Q(record[key].get("1", "0"))+1)
        mutate("overstated-dual-objective", "DUALS.json.gz",
               lambda raw: change_dual(raw, overstate), "negative or uncertified reduced cost")
        mutate("omitted-primal-node", "PRIMAL.json.gz",
               lambda raw: change_dual(raw, lambda x: x["assignment"].pop(next(iter(x["assignment"])))),
               "complete primal node coverage")
        mutate("false-idle-mass", "EXPECTED.json",
               lambda raw: edit(raw, lambda x: x.update(idle_mass=1646)), "receipt mismatch")
        mutate("false-gate-coverage", "EXPECTED.json",
               lambda raw: edit(raw, lambda x: x.update(free_gates=2588)), "receipt mismatch")
        mutate("missing-source-inventory", "SOURCES.json",
               lambda raw: edit(raw, lambda x: x["files"].pop()), "source inventory")
        mutate("retained-model-drift", "references/frame_model.py", lambda raw: raw+b"\n", "retained source SHA256")
        mutate("selected-word-drift", "references/WORD.json.gz", lambda raw: raw+b"\n", "retained source SHA256")
        mutate("duplicate-receipt-key", "EXPECTED.json", lambda raw: b'{"x":0,"x":1}', "duplicate JSON key")
        mutate("nonfinite-receipt", "EXPECTED.json", lambda raw: b'{"x":NaN}', "noninteger/nonfinite JSON number")
        need(inventory(target) == before, "corruptions not restored")
    print("PASS_K8_UNRESTRICTED_END_CONTROLS", "checks="+str(len(controls)))
    print(json.dumps(controls))
    print("native_profiles="+json.dumps(native_profiles, sort_keys=True))


if __name__ == "__main__":
    main()
