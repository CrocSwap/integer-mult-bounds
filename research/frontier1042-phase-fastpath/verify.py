#!/usr/bin/env python3
"""Check the merged exact phase fast path on the three frontier1042 `phases` steps.

The cold frontier1042 replay (the `baseline1042-cold` stage of `make frontier1094-verify`) runs the
pinned serial `phases_full.py` three times: in the cells, chain and slots stages. This verifier takes
the three canonical words from the maintainer's archived replay, checks them against the k8 pins,
compiles each with `research/selected-replay-fastpath/run.py` (unchanged; it checks its own source
pins), and requires the recipe bytes to equal both the pinned `clifford_recipes_sha256` and the
archived recipes. Two corrupted words must fail. Nothing is wired into the pinned replay.

Josie Elliston with Claude Code. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / 'research/community-frontier1042-audit/selected-replay.tar.gz'
RUN = ROOT / 'research/selected-replay-fastpath/run.py'
PINS = {
    'cells': ROOT / 'research/gauge44-leaver8/construction/leaver/LEAVER-PINS-k8.json',
    'chain': ROOT / 'research/gauge44-leaver8/construction/leaver/CHAIN-PINS-k8.json',
    'slots': ROOT / 'research/gauge44-slots/construction/slots/SLOT-PINS-k8.json',
}
# Review fields that describe the computation (everything except scope prose and seconds). The T16 provider
# binder asserts status, both digests, the global-phase flag and the adapter count of this file.
REVIEW_FIELDS = ('status', 'canonical_word_sha256', 'frames', 'directed_edges', 'ranks', 'endpoint_adapters',
                 'all_child_equalities_include_global_phase', 'recipe_sha256')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def require(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def member(tar, name):
    f = tar.extractfile(name)
    require(f is not None, 'missing archive member ' + name)
    return f.read()


def compile_word(word, out, engine):
    t = time.monotonic()
    p = subprocess.run([sys.executable, '-B', str(RUN), '--word', str(word), '--out', str(out),
                        '--engine', engine], capture_output=True, text=True)
    return p, time.monotonic() - t


def canonical_gz(obj):
    return gzip.compress(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode(), mtime=0)


def main():
    require(not sys.flags.optimize, 'assertions must stay enabled')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--engine', choices=('sparse', 'dense', 'reference'), default='sparse',
                    help='evaluator inside run.py (reference = the retained original lowering, slow)')
    ap.add_argument('--skip-controls', action='store_true')
    a = ap.parse_args()
    report = dict(engine=a.engine, python=sys.version.split()[0], archive_sha256=sha(ARCHIVE.read_bytes()),
                  stages={}, controls={})
    with tempfile.TemporaryDirectory(prefix='f1042-phases-') as tmp, tarfile.open(ARCHIVE) as tar:
        tmp = Path(tmp)
        words = {}
        for stage, pin_file in PINS.items():
            pins = json.loads(pin_file.read_text())
            raw = member(tar, stage + '/local/CANONICAL-WORD.json.gz')
            recipes = member(tar, stage + '/local/CLIFFORD-RECIPES.json')
            review = json.loads(member(tar, stage + '/local/CLIFFORD-REVIEW.json'))
            # The archived word is the one the pinned replay checked (payload pin), and the archived
            # recipes are the ones the pinned serial phases_full.py wrote (recipe pin).
            require(sha(gzip.decompress(raw)) == pins['canonical_sha256'], stage + ': canonical word pin')
            require(sha(recipes) == pins['clifford_recipes_sha256'], stage + ': archived recipes pin')
            require(review['recipe_sha256'] == pins['clifford_recipes_sha256'] and
                    review['canonical_word_sha256'] == sha(raw), stage + ': archived review binding')
            word = tmp / stage / 'CANONICAL-WORD.json.gz'
            word.parent.mkdir()
            word.write_bytes(raw)
            words[stage] = word
            out = tmp / stage / 'out'
            p, dt = compile_word(word, out, a.engine)
            require(p.returncode == 0, stage + ': run.py failed\n' + p.stdout[-400:] + p.stderr[-800:])
            got = (out / 'CLIFFORD-RECIPES.json').read_bytes()
            mine = json.loads((out / 'CLIFFORD-REVIEW.json').read_text())
            require(got == recipes, stage + ': recipe bytes differ from the archived pinned recipes')
            require(sha(got) == pins['clifford_recipes_sha256'], stage + ': recipe pin')
            for k in REVIEW_FIELDS:
                require(mine[k] == review[k], stage + ': review field ' + k)
            report['stages'][stage] = dict(
                recipe_sha256=sha(got), canonical_sha256=pins['canonical_sha256'],
                frames=mine['frames'], directed_edges=mine['directed_edges'],
                endpoint_adapters=mine['endpoint_adapters'], wall_seconds=round(dt, 2),
                archived_serial_seconds=round(review['seconds'], 2))
            print('PASS', stage, a.engine, 'byte-identical', '%.1fs' % dt,
                  '(archived serial %.1fs)' % review['seconds'], flush=True)

        if not a.skip_controls:
            base = json.loads(gzip.decompress(words['cells'].read_bytes()))
            # C1: a one-dimensional frame <u> becomes a different line <u ^ e>. (A bit flip inside a
            # full-rank frame leaves its span, hence its canonical frame and recipes, unchanged, so it
            # is not a corruption.) Either an assertion fires or the recipes change.
            c1 = json.loads(json.dumps(base))
            i = next(i for i, U in enumerate(c1['frames']) if len(U) == 1)
            u = c1['frames'][i][0]
            c1['frames'][i][0] = u ^ (2 if u & 1 and u != 2 else 1)
            require(c1['frames'][i][0] not in (0, u), 'C1 setup')
            # C2: one directed edge is redirected to a frame of a different dimension. The per-edge
            # rank assertion may or may not fire; either way the pinned recipes must not come back.
            c2 = json.loads(json.dumps(base))
            a0, b0 = c2['edges'][0]
            other = next(f for f in range(len(c2['frames']))
                         if f not in (a0, b0) and len(c2['frames'][f]) != len(c2['frames'][b0]))
            c2['edges'][0] = [a0, other]
            pin = json.loads(PINS['cells'].read_text())['clifford_recipes_sha256']
            for name, obj in (('C1_frame_bit', c1), ('C2_edge_redirect', c2)):
                w = tmp / name / 'CANONICAL-WORD.json.gz'
                w.parent.mkdir()
                w.write_bytes(canonical_gz(obj))
                p, _ = compile_word(w, tmp / name / 'out', a.engine)
                rp = tmp / name / 'out' / 'CLIFFORD-RECIPES.json'
                reproduced = p.returncode == 0 and rp.exists() and sha(rp.read_bytes()) == pin
                require(not reproduced, name + ': corrupted word reproduced the pinned recipes')
                # Pin the observed behaviour exactly, so a change in how the compiler treats either
                # corruption is noticed rather than absorbed by "any failure counts".
                if name == 'C1_frame_bit':
                    require(p.returncode != 0 and 'AssertionError' in p.stderr and not rp.exists(),
                            name + ': expected an assertion and no recipes')
                    outcome = 'rejected by AssertionError, no recipes written'
                else:
                    require(p.returncode == 0 and rp.exists(), name + ': expected a compiled, different word')
                    outcome = 'compiled to different recipes ' + sha(rp.read_bytes())[:16]
                report['controls'][name] = outcome
                print('PASS control', name, '-', outcome, flush=True)
    print(json.dumps(report, indent=1))
    print('PASS_FRONTIER1042_PHASE_FASTPATH')


if __name__ == '__main__':
    main()
