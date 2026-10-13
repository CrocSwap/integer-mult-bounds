#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild the X54 slot on the PR1148 joint-entrance k8 word and its native locals.

Steps (each checked against WORD-PINS.json):
  1. research/k8-joint-entrances/build_word.py (tomdif, PR1148, unchanged) builds the joint-entrance word.
  2. NewBArch's unchanged build_tri.py applies RECIPE-X54-joint.json: jeremykothe2's PR1130 X54/E589
     edits and frames, byte-identical to PR1178's RECIPE-X54-dem.json except the base/result pins and profile.
  3. NewBArch's unchanged run_controls.py: the recipe passes and its nine mutants are rejected.
  4. research/gauge44-slots/independent/audit_local.py (unchanged) audits the raw word.
  5. research/k8-eight-ends/replay_native.py (unchanged) runs the PR635 native chain:
     native, ledgers, local-replay, wrappers and phases.
The resulting local directory must match inputs/local on every pinned identity.
"""
import argparse, gzip, hashlib, importlib.util, json, os, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]
BARCH = 'research/complex-t21-owners/vendor/pr870/construction/barch'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def csha(p):
    return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()


def identities(local):
    spec = importlib.util.spec_from_file_location('gi', PKG/'vendor/pr1074/code/generated_identity.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.artifact_identities(local)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, default=PKG.parents[1])
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    main, out = a.main.resolve(), a.out.resolve()
    assert not out.exists(), 'Choose a new output directory'
    out.mkdir(parents=True)
    pins = json.loads((HERE/'WORD-PINS.json').read_text())
    recipe = HERE/'RECIPE-X54-joint.json'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    env.pop('PYTHONOPTIMIZE', None)

    def run(label, script, *args):
        with (out/(label+'.log')).open('w') as f:
            rc = subprocess.call([sys.executable, '-B', str(script), *map(str, args)], cwd=main, env=env,
                                 stdout=f, stderr=subprocess.STDOUT)
        assert rc == 0, label + ' failed: ' + (out/(label+'.log')).read_text()[-4000:]
        print('PASS', label, flush=True)

    joint = out/'JOINT-WORD.json.gz'
    run('joint', main/'research/k8-joint-entrances/build_word.py', '--out', joint)
    assert csha(joint) == pins['joint_content_sha256'], 'joint word content'
    word = out/'FULL-WORD.json.gz'
    run('x54', main/BARCH/'build_tri.py', joint, recipe, word)
    assert csha(word) == pins['word_content_sha256'], 'X54 word content'
    run('x54-controls', main/BARCH/'run_controls.py', joint, recipe,
        main/'research/complex-t21-owners/vendor/pr870/independent/audit_local.py', out/'controls')
    controls = json.loads((out/'controls/controls.json').read_text())
    assert sorted(controls) == sorted(pins['controls']) and all(x['ok'] for x in controls.values())
    run('audit-local', main/'research/gauge44-slots/independent/audit_local.py', '--word', word,
        '--main', main, '--output', out/'AUDIT-LOCAL.json')
    run('native', main/'research/k8-eight-ends/replay_native.py', word, out/'native')
    local = out/'native/local'
    assert csha(local/'FULL-WORD.json.gz') == pins['word_content_sha256']
    checks = json.loads((local/'LOCAL-CHECKS.json').read_text())
    assert {o: checks[o]['sha256'] for o in ('forward', 'backward')} == pins['program_sha256']
    assert checks['forward']['paid_profile'] == pins['local_profile']
    assert sha(local/'CLIFFORD-RECIPES.json') == pins['clifford_recipes_sha256']
    got = identities(local)
    assert got == pins['artifact_semantic_sha256'] == identities(PKG/'inputs/local'), 'semantic identities'
    print('PASS_K8_JOINT_X54_LOCALS', local, flush=True)


if __name__ == '__main__':
    main()
