"""Rebuild the retained lowering and match every exact source column.

SOURCE-FRAMES.json is the 151-byte extraction of the pinned archive, whose
350,722 bytes are deliberately not vendored. --source-repo re-extracts it
read-only from the exact commit:path and authenticates the complete archive.
"""
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import move as m


def need(ok, message):
    if not ok:
        raise ValueError(message)


def verify_source(repo=None):
    m.authenticate()
    record = json.loads((HERE / 'reference/RECIPE.json').read_text())
    witness = json.loads((HERE / 'reference/SOURCE-FRAMES.json').read_text())
    need(witness['event_index'] == record['native_event_index'] == 24472, 'event index')
    need(witness['event'] == record['event'] == ['MOVE', 415, 3, 99, False], 'actual MOVE')
    if repo is not None:
        pin = json.loads((HERE / 'SOURCES.json').read_text())['upstream_artifacts'][0]
        raw = subprocess.check_output(['git', 'show', pin['commit'] + ':' + pin['path']], cwd=repo)
        need(len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256'],
             'complete selected archive binding')
        word = json.loads(gzip.decompress(raw))
        canonical = json.dumps(word, separators=(',', ':'), sort_keys=True).encode()
        need(hashlib.sha256(canonical).hexdigest() == record['native_canonical_sha256'],
             'complete selected canonical word')
        extracted = dict(event_index=24472, event=word['program'][24472],
                         frames={str(i): word['frames'][i] for i in word['program'][24472][2:4]})
        need(extracted == witness, 'compact frame extraction')
    compiler = m.load('move_join_source_compiler', 'source/clifford_exact.py')
    independent = m.load('move_join_source_independent', 'source/native_verify.py')
    before, after = witness['event'][2:4]
    a, b = (compiler.canonical_frame(9, tuple(witness['frames'][str(i)])) for i in (before, after))
    recipe, _ = compiler.lower_child(a.adjoint().then(b))
    recipe = json.loads(json.dumps(recipe))
    need(recipe == record['lowered_recipe'] and recipe['rank'] == 1, 'source lowering')
    target = independent.adjoint(independent.frame(witness['frames'][str(before)], 9))
    target += independent.frame(witness['frames'][str(after)], 9)
    independent.equal(independent.recipe(recipe), target, 'complete selected MOVE kernel')
    # Compare all 512 columns, including Gaussian normalization and phase,
    # with a separate explicit two-term formula for the joined recipe.
    from verify import linear, phase, rotate
    right, left = recipe['right'], recipe['left']
    for source in range(512):
        x = tuple((source >> i) & 1 for i in range(9))
        t = tuple(a ^ ((right['offset'] >> i) & 1)
                  for i, a in enumerate(linear(right['matrix_rows'], x)))
        expected = {}
        for bit in (0, 1):
            z = (bit,) + t[1:]
            out = linear(left['matrix_rows'], z)
            address = sum(a << i for i, a in enumerate(out))
            expected[address] = rotate((1, 1 if bit == t[0] else -1),
                                       phase(right, x, 1) + phase(left, z, 1))
        values, denominator = independent.state(target, source)
        need(denominator == 1 and values == expected, 'source column ' + str(source))
    wrong = copy.deepcopy(recipe)
    wrong['right']['phase'] = (wrong['right']['phase'] + 1) % 4
    try:
        independent.equal(independent.recipe(wrong), target, 'absolute phase mutation')
    except ValueError:
        pass
    else:
        raise ValueError('source phase mutation missed')
    return dict(marker='PASS_COMPLETE_MOVE_SOURCE_BINDING', source_index=24472,
                owner=415, frames=[before, after], basis_columns=512,
                full_archive_reextracted=repo is not None, negative_controls=['absolute phase'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-repo', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_source(args.source_repo), indent=2, sort_keys=True))
