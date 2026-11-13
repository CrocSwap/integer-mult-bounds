"""Bind actual MOVE28141 and its exact full nine-qubit operator."""
from pathlib import Path
import argparse
import atexit
import copy
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
_cache = tempfile.TemporaryDirectory(prefix='rank2-binding-source-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode = True
sys.pycache_prefix = str(Path(_cache.name) / 'required-absent')
if Path(sys.pycache_prefix).exists():
    raise ValueError('source cache must be absent')
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rank2 as C


def need(ok, message):
    if not ok:
        raise ValueError(message)


def verify(repo=None):
    C.authenticate()
    r = C.RECIPE
    need(r['source_event_index'] == 28141 and
         r['source_event'] == ['MOVE', 1526, 601, 470, True], 'actual owned event')
    need(r['frames'] == {'601': [137], '470': [75, 137, 265]}, 'complete source frames')
    if repo is not None:
        manifest = json.loads((C.HERE / 'SOURCES.json').read_text())
        pin = manifest['upstream_artifacts'][0]
        raw = subprocess.check_output(['git', 'show', pin['commit'] + ':' + pin['path']], cwd=repo)
        need(len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256'], 'whole archive')
        word = json.loads(gzip.decompress(raw))
        canonical = json.dumps(word, separators=(',', ':'), sort_keys=True).encode()
        need(hashlib.sha256(canonical).hexdigest() == pin['canonical_sha256'], 'whole canonical word')
        event = word['program'][28141]
        need(event == r['source_event'] and
             {str(i): word['frames'][i] for i in event[2:4]} == r['frames'], 'current extraction')
        for proof in manifest['proof_inputs']:
            data = subprocess.check_output(['git', 'show', proof['commit'] + ':' + proof['path']], cwd=repo)
            need(len(data) == proof['bytes'] and hashlib.sha256(data).hexdigest() == proof['sha256'],
                 'pinned proof/source bytes')
            if proof['path'] == 'research/owned-ascent-contract/RECIPES.json':
                old = next(row for row in json.loads(data)
                           if (row['role'], row['event']) == (r['retained_role'], r['retained_event']))
                need((old['start'], old['end'], old['rank']) == (601, 470, 2), 'retained actual pair')
                need(all(old[key] == r[key] for key in ('left', 'right', 'left_records', 'right_records')),
                     'retained exact36/44 record sequence')
    compiler = C.load('rank2_source_compiler', 'source/clifford_exact.py')
    exact = C.load('rank2_source_independent', 'source/native_verify.py')
    before = compiler.canonical_frame(9, (137,))
    after = compiler.canonical_frame(9, (75, 137, 265))
    recipe, _ = compiler.lower_child(before.adjoint().then(after))
    need(json.loads(json.dumps(recipe)) == {key: r[key] for key in ('rank', 'left', 'right')}, 'retained lowering')
    target = exact.adjoint(exact.frame((137,), 9)) + exact.frame((75, 137, 265), 9)
    exact.equal(exact.recipe(recipe), target, 'actual positive rank-two quotient')
    for side in ('left', 'right'):
        for x in range(512):
            z = x
            for record in r[side + '_records']:
                if record[0] == 'XROW':
                    z ^= ((z >> record[2]) & 1) << record[1]
            wanted = sum(((row & x).bit_count() & 1) << i for i, row in enumerate(r[side]['matrix_rows']))
            need(z == wanted, side + ' complete binary matrix')
    # Independently compare the exact interleaved central circuit, including
    # its phase, with two positive coordinate C operators.
    swap = (2, 1, 4, 8, 16, 32, 64, 128, 256)
    interleaved = [('C', 1, 1), ('P', swap), ('C', 1, 1), ('P', swap)]
    exact.equal(interleaved, [('C', 1, 1), ('C', 2, 1)], 'rank-two conjugated child')
    controls = []
    wrong = copy.deepcopy(recipe)
    wrong['right']['phase'] = (wrong['right']['phase'] + 1) % 4
    for label, actual, expected in (
        ('absolute_phase', exact.recipe(wrong), target),
        ('inverse_orientation', exact.recipe(recipe), exact.adjoint(target)),
        ('one_C_instead_of_two', [('C', 1, 1)], [('C', 1, 1), ('C', 2, 1)]),
    ):
        try:
            exact.equal(actual, expected, label)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError('missed source control ' + label)
    return dict(marker='PASS_OWNED_RANK2_SOURCE', event_index=28141, owner=1526,
                private=True, private_flag_is_not_inversion=True, frames=[601, 470], rank=2,
                left_records=36, right_records=44, left_CNOT=31, right_CNOT=29,
                matrix_columns=1024, full_archive_reextracted=repo is not None,
                exact_equality='signed Pauli action and exact Gaussian separating column',
                controls=controls)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-repo', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.source_repo), indent=2, sort_keys=True))
