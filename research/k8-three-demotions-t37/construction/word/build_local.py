#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild the PR1148 three-demotion k8 word and its native locals.

Steps (each checked against WORD-PINS.json):
  1. research/k8-three-demotions/build_word.py (tomdif, PR1148, unchanged) applies its frozen recipe
     to the eight-endpoint k8 word of research/k8-eight-ends.
  2. research/gauge44-slots/independent/audit_local.py (unchanged) audits the raw word.
  3. research/k8-eight-ends/replay_native.py (unchanged) runs the PR635 native chain:
     native, ledgers, local-replay, wrappers and phases.
The resulting local directory must match inputs/local on every pinned identity.
"""
import argparse, gzip, hashlib, importlib.util, json, os, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]


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
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    env.pop('PYTHONOPTIMIZE', None)

    def run(label, script, *args):
        with (out/(label+'.log')).open('w') as f:
            rc = subprocess.call([sys.executable, '-B', str(script), *map(str, args)], cwd=main, env=env,
                                 stdout=f, stderr=subprocess.STDOUT)
        assert rc == 0, label + ' failed: ' + (out/(label+'.log')).read_text()[-4000:]
        print('PASS', label, flush=True)

    word = out/'FULL-WORD.json.gz'
    run('build', main/'research/k8-three-demotions/build_word.py', '--out', word)
    assert csha(word) == pins['word_content_sha256'], 'word content'
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
    print('PASS_K8_THREE_DEMOTIONS_LOCALS', local, flush=True)


if __name__ == '__main__':
    main()
