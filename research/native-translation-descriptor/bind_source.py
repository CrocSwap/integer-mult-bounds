"""Bind the one actual post-matrix translation, without claiming a native body."""
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def main():
    records = json.loads((HERE / 'SOURCES.json').read_text())['files']
    checked = 0
    for row in records:
        if 'local_path' not in row:
            continue
        data = (HERE / row['local_path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256 ' + row['local_path'])
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'],
             'source Git blob ' + row['local_path'])
        checked += 1
    C = module('translation_binding_compiler', HERE / 'reference/clifford_exact.py')
    V = module('translation_binding_independent', HERE / 'reference/native_verify.py')
    record = json.loads((HERE / 'RECIPE.json').read_text())
    raw = (HERE / 'reference/selected-native.json.gz').read_bytes()
    word = json.loads(gzip.decompress(raw))
    need(hashlib.sha256(raw).hexdigest() == record['native_compressed_sha256'], 'selected compressed source')
    need(hashlib.sha256(json.dumps(word, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
         == record['native_canonical_sha256'], 'selected canonical JSON')
    event = word['program'][24472]
    need(event == ['MOVE', 415, 3, 99, False] == record['event'], 'exact current MOVE')
    a = C.canonical_frame(9, tuple(word['frames'][3]))
    b = C.canonical_frame(9, tuple(word['frames'][99]))
    recipe, _ = C.lower_child(a.adjoint().then(b))
    recipe = json.loads(json.dumps(recipe))
    need(recipe == record['lowered_recipe'], 'unchanged full source recipe')
    need(recipe['rank'] == 1 and recipe['right']['offset'] == 1, 'right offset is output bit zero')
    target = V.adjoint(V.frame(word['frames'][3], 9)) + V.frame(word['frames'][99], 9)
    V.equal(V.recipe(recipe), target, 'actual complete source decomposition')
    right = recipe['right']
    no_translation = copy.deepcopy(right)
    no_translation['offset'] = 0
    # Separate retained evaluator: the translation acts on the coordinate
    # after the source matrix. Every complete basis coefficient is checked.
    for x in range(512):
        baseline, denominator = V.state(V.monomial(no_translation), x)
        translated, denominator2 = V.state(V.monomial(right), x)
        need(denominator == denominator2 and translated == {y ^ 1: v for y, v in baseline.items()},
             'post-matrix coordinate-zero translation')
    wrong = copy.deepcopy(recipe)
    wrong['right']['offset'] = 1 << 8
    try:
        V.equal(V.recipe(wrong), target, 'changed translation axis')
    except ValueError:
        pass
    else:
        raise ValueError('wrong-axis source control escaped')
    result = dict(status='PASS_SELECTED_TRANSLATION_SOURCE_BINDING', local_source_files=checked,
                  native_event=24472, actual_native_owner=415, side='right', offset=1,
                  packed_coordinate=0, basis_states=512,
                  ordering='diagonal, linear matrix, translation, commuting global phase',
                  negative_controls=['changed translation from output bit0 to output bit8'],
                  scope='Source factor only; no implementation of the preceding matrix or whole native MOVE.')
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
