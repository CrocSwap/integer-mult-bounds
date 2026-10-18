#!/usr/bin/env python3
"""Focused optimized-Python corruption and minimal offline relocation checks.

All mutations occur in temporary copies. Only package execution inputs and the
SOURCES.json closure are copied, without Git metadata, into a path with spaces.
The default test includes two full verifier runs: one receipt corruption and
one successful untouched reproduction. No third-party dependency is required.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)
PACKAGE_FILES = ("verify.py", "independent.py", "CERTIFICATE.json", "EXPECTED.json", "SOURCES.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_closure():
    """Read declared source manifests transitively, without scanning the repo."""
    paths = {PACKAGE / name for name in PACKAGE_FILES}
    pending = [PACKAGE / "SOURCES.json"]
    seen = set()
    while pending:
        manifest_path = pending.pop()
        if manifest_path in seen:
            continue
        seen.add(manifest_path)
        manifest = json.loads((ROOT / manifest_path).read_bytes())
        for entry in manifest["files"]:
            path = Path(entry["path"])
            require(not path.is_absolute() and ".." not in path.parts, "Nonlocal source path")
            require((ROOT / path).is_file(), "Missing declared source: " + str(path))
            paths.add(path)
            if path.name == "SOURCES.json":
                pending.append(path)
    return sorted(paths)


def run_child(arguments, cwd, env, success, marker, timeout=240):
    process = subprocess.run([sys.executable, "-I", "-O", "-B", *arguments],
                             cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    output = process.stdout + process.stderr
    require((process.returncode == 0) == success,
            f"Unexpected return code {process.returncode}: {output[-8000:]}")
    require(marker in output, "Missing expected result " + marker + ": " + output[-8000:])
    return output


def test_package():
    paths = source_closure()
    source_hashes = {str(path): sha256(ROOT / path) for path in paths}
    checks = []
    with tempfile.TemporaryDirectory(prefix="ck dyadic package ") as directory:
        base = Path(directory)
        relocated = base / "minimal checkout with spaces"
        cwd = base / "unrelated working directory"
        cwd.mkdir()
        empty_bin = base / "empty command path"
        empty_bin.mkdir()
        env = os.environ.copy()
        env["PATH"] = str(empty_bin)  # Git and external network commands unavailable.
        for path in paths:
            destination = relocated / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, destination)
        require(not (relocated / ".git").exists(), "Unexpected Git metadata")
        script = relocated / PACKAGE / "verify.py"
        copied_sources = json.loads((relocated / PACKAGE / "SOURCES.json").read_bytes())
        canonical = next(relocated / entry["path"] for entry in copied_sources["files"]
                         if entry["path"].endswith("/ck/CANONICAL-WORD.json.gz"))
        recipe = relocated / "research/complex-ck-two-sided/RECIPE.json"
        for label, path, compressed in (("altered_canonical_payload", canonical, True),
                                        ("altered_predecessor_recipe", recipe, False)):
            original = path.read_bytes()
            value = json.loads(gzip.decompress(original) if compressed else original)
            if compressed:
                value["compensation"][0][3] *= -1
            else:
                value["target_forest"][0][2] *= -1
            raw = json.dumps(value).encode()
            path.write_bytes(gzip.compress(raw, mtime=0) if compressed else raw)
            try:
                run_child([str(script)], cwd, env, False, "source pin:", timeout=15)
            finally:
                path.write_bytes(original)
            checks.append(label)
        # Exercise the main checker's proof rejection in optimized Python. One
        # census per cost model is reused for every certificate corruption.
        certificate_checks = r"""
import copy, importlib.util, json, sys
from pathlib import Path
path=Path(sys.argv[1]); spec=importlib.util.spec_from_file_location('verify_under_test',path)
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
i=v.module('independent_under_test',path.with_name('independent.py'))
C,D,recipe,panel=i.read_matrix()
certificate=json.loads(path.with_name('CERTIFICATE.json').read_bytes())
for modern,key in ((False,'matchings'),(True,'pr696_matchings')):
    edges,_=v.census(D,modern=modern)
    original=certificate[key]['extended']
    v.dual_check(original,edges)
    corruptions=[]
    bad=copy.deepcopy(original); bad['matching'][0]['gain']+=1
    corruptions.append(('wrong_gain',bad))
    bad=copy.deepcopy(original); bad['matching'][1]=copy.deepcopy(bad['matching'][0])
    corruptions.append(('overlap',bad))
    bad=copy.deepcopy(original); bad['vertex_dual_twice']=[0]*254
    corruptions.append(('uncovered_dual',bad))
    bad=copy.deepcopy(original); bad['odd_sets'].append({'vertices':[0,1],'dual':1})
    corruptions.append(('even_odd_set',bad))
    bad=copy.deepcopy(original); bad['odd_sets'].append({'vertices':[0,0,1],'dual':1})
    corruptions.append(('duplicate_odd_vertex',bad))
    bad=copy.deepcopy(original); bad['vertex_dual_twice'][0]=True
    corruptions.append(('boolean_dual',bad))
    for name,bad in corruptions:
        try: v.dual_check(bad,edges)
        except ValueError: pass
        else: raise ValueError('accepted certificate corruption: '+name)
print('PASS_OPTIMIZED_CERTIFICATE_CORRUPTIONS models=2 controls=12')
"""
        run_child(["-c", certificate_checks, str(script)], cwd, env, True,
                  "PASS_OPTIMIZED_CERTIFICATE_CORRUPTIONS", timeout=30)
        checks.append("optimized_certificate_corruptions_12")
        expected = script.with_name("EXPECTED.json")
        original_expected = expected.read_bytes()
        bad = json.loads(original_expected)
        require("pr696" in bad and "pr696" in bad["independent"], "Modern EXPECTED receipt not ready")
        bad["seed"] = 23
        expected.write_text(json.dumps(bad))
        try:
            run_child([str(script)], cwd, env, False, "EXPECTED.json mismatch")
        finally:
            expected.write_bytes(original_expected)
        checks.append("altered_expected_receipt")
        run_child([str(script)], cwd, env, True, "PASS_CK_DYADIC_HELPERS")
        checks.append("minimal_relocation_with_spaces_optimized_full_replay")
        for path in paths:
            require(sha256(relocated / path) == source_hashes[str(path)],
                    "Relocated input mutated: " + str(path))
        require(not (relocated / ".git").exists(), "Unexpected Git metadata after verification")
    for path in paths:
        require(sha256(ROOT / path) == source_hashes[str(path)], "Original input changed: " + str(path))
    print("PASS_CK_DYADIC_PACKAGE copied_files=" + str(len(paths)) + " checks=" + str(len(checks)) + " optimized_python no_git")
    return checks


if __name__ == "__main__":
    test_package()
