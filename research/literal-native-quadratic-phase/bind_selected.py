"""Exact current-source recipe binding; retained independent Clifford check."""
from pathlib import Path
import copy
import gzip
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def main():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for record in pins['files']:
        need(hashlib.sha256((HERE/record['local_path']).read_bytes()).hexdigest() == record['sha256'],
             'source bytes '+record['local_path'])
    C = module('binding_compiler', HERE/'reference/clifford_exact.py')
    V = module('binding_independent', HERE/'reference/native_verify.py')
    raw = (HERE/'reference/selected-native.json.gz').read_bytes()
    word = json.loads(gzip.decompress(raw))
    record = json.loads((HERE/'RECIPE.json').read_text())
    need(hashlib.sha256(raw).hexdigest() == record['native_compressed_sha256'], 'compressed selected word')
    need(hashlib.sha256(json.dumps(word,separators=(',',':'),sort_keys=True).encode()).hexdigest() == record['native_canonical_sha256'], 'canonical selected word')
    event = word['program'][record['native_event_index']]
    need(event == ['MOVE',415,3,99,False] == record['event'], 'actual selected event')
    before, after = event[2:4]
    a = C.canonical_frame(9,tuple(word['frames'][before]))
    b = C.canonical_frame(9,tuple(word['frames'][after]))
    recipe, _ = C.lower_child(a.adjoint().then(b))
    recipe = json.loads(json.dumps(recipe))
    need(recipe == record['lowered_recipe'], 'exact source lowering')
    need(recipe['rank'] == 1 and recipe[record['side']] == record['recipe'], 'selected right factor')
    # Retained independent signed-Pauli/global-Gaussian method. This is not
    # a new independent review of the complete selected native catalogue.
    target = V.adjoint(V.frame(word['frames'][before],9)) + V.frame(word['frames'][after],9)
    V.equal(V.recipe(recipe),target,'selected MOVE complete kernel')
    selected = record['recipe']
    J = (0,1,2,3,5,6)
    for x in range(512):
        h = sum((x >> i) & 1 for i in J)
        mode = (1-(h % 2)+2*((x >> 7) & 1)) % 4
        y = sum(((row & x).bit_count() % 2) << i for i,row in enumerate(selected['matrix_rows'])) ^ selected['offset']
        expected = {y: ((1,0),(0,1),(-1,0),(0,-1))[mode]}
        value, denominator = V.state(V.monomial(selected),x)
        need(denominator == 0 and value == expected, 'input-coordinate absolute phase')
    wrong = copy.deepcopy(recipe)
    wrong['right']['phase'] = (wrong['right']['phase']+1) % 4
    try:
        V.equal(V.recipe(wrong),target,'changed absolute phase')
    except ValueError:
        pass
    else:
        raise ValueError('global phase control missed')
    print(json.dumps({'status':'PASS_CURRENT_SELECTED_QUADRATIC_RECIPE_BINDING',
          'native_event_index':record['native_event_index'],'frames':[before,after],
          'owner':415,'side':'right','rank':1,'basis_states':512,
          'source_files':len(pins['files']),'negative_controls':['changed absolute phase'],
          'note':'Retained exact compiler and independent interpreter, plus new XOR-parity phase oracle. No full native catalogue replay.'},indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
