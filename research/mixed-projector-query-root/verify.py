"""Replay the exact source, mixed root, physical caller and complete bound.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor authors and proof engines retain their credit in NOTICE.
"""
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIFT = ROOT/'research/p104-native-input-lifting'
TREE = ROOT/'research/balanced-query-tree'
STATUS = 'PASS_MIXED_PROJECTOR_QUERY_ROOT_KAPPA_00327980'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate():
    pins = [p for p in read(HERE/'SOURCES.json')['files'] if p['usage'] == 'input']
    for pin in pins:
        raw = (ROOT/pin['path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'Source SHA256: '+pin['path'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
             'Source Git blob: '+pin['path'])
    need(len(pins) == 17, 'Complete live source inventory')
    return len(pins)


def run():
    sources = authenticate()
    load(HERE/'algebra.py', 'algebra')
    controller = load(HERE/'controller.py', 'controller')
    module = load(HERE/'module_check.py', 'mixed_root_module')
    physical = load(HERE/'physical.py', 'mixed_root_physical')
    price = load(HERE/'pricing.py', 'mixed_root_price')
    support = load(LIFT/'support.py', 'support')
    constructor = load(LIFT/'construct.py', 'mixed_source_constructor')
    lift_checks = load(LIFT/'verify.py', 'mixed_source_checks')
    binary = load(TREE/'module_check.py', 'mixed_binary_module')
    source = json.loads(gzip.decompress(support.inputs()[support.WORD]))
    local_word = constructor.construct(source)
    need(constructor.payload(local_word) == gzip.decompress((LIFT/'WORD.json.gz').read_bytes()),
         'Every unchanged lifted source byte')
    word = controller.construct()
    need(word == read(HERE/'CONTROLLER.json'), 'Every emitted caller event')
    root_check, binary_check = module.run(), binary.run()
    caller = controller.replay(word)
    controls = controller.controls(word)
    print('PASS exact root, ordinary normalization, binary children, full caller and controls', flush=True)
    with support.checkers() as (L, root):
        directions = lift_checks.preparation(L, source, local_word)
        local = L.replay(local_word)
        need(price.encode(local) == read(LIFT/'RESULT.json')['local'], 'Complete unchanged local receipt')
        controls.update(lift_checks.word_controls(L, local_word))
        columns = L.reverse_columns(local_word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'Every arbitrary source input')
        print('PASS source arbitrary inputs, preparation, ownership and dense transpose', flush=True)
        native = L.native(local_word)
        maps = physical.physical(word, local_word, L)
        need(maps['full_calls'] == 18 and maps['physical_contacts'] == 7488, 'Every native contact')
        print('PASS native absolute phases, whole idles and physical caller', flush=True)
        result_price = price.run(local, native, word, maps, L)
        print('PASS complete invoice, both rational price engines, compiler and outer predicates', flush=True)
    return price.encode({'status':STATUS, 'source_inputs':sources, 'root':root_check,
                         'binary_module':binary_check, 'caller':caller,
                         'local':local, 'lifted_directions':directions, 'columns':columns,
                         'native':native, 'physical':maps, 'price':result_price,
                         'negative_controls':controls,
                         'assumptions':['native_all_columns','owned_erasure','compiler',
                                        'precision_tape','analytic_recovery'],
                         'selected_frontier_changed':False})


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write-result']:
        (HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        need(not sys.argv[1:], 'Only --write-result is supported')
        need(result == read(HERE/'RESULT.json'), 'Exact retained scientific receipt')
    print(STATUS, flush=True)
