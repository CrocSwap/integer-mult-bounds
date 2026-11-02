"""Check the complete composition of the published input lifts and tree.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source constructions and all proof engines retain the credits in NOTICE.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TREE = ROOT / 'research/balanced-query-tree'
LIFT = ROOT / 'research/p104-native-input-lifting'
STATUS = 'PASS_P104_INPUT_LIFT_TREE_KAPPA_00314980'


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
    pins = [p for p in read(HERE / 'SOURCES.json')['files'] if p['usage'] == 'input']
    for pin in pins:
        raw = (ROOT / pin['path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'Source SHA256: ' + pin['path'])
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'],
             'Source Git blob: ' + pin['path'])
    need(len(pins) == 17, 'Complete live input inventory')
    return len(pins)


def run():
    source_count = authenticate()
    support = load(LIFT / 'support.py', 'support')
    constructor = load(LIFT / 'construct.py', 'composition_constructor')
    lift_checks = load(LIFT / 'verify.py', 'composition_lift_checks')
    controller = load(TREE / 'controller.py', 'controller')
    module = load(TREE / 'module_check.py', 'composition_module')
    physical = load(TREE / 'physical.py', 'composition_physical')
    text = (TREE / 'pricing.py').read_text()
    for before, after in read(HERE / 'PRICING-EDITS.json'):
        need(text.count(before) == 1, 'Unique declared pricing edit')
        text = text.replace(before, after)
    need(text == (HERE / 'pricing.py').read_text(), 'Only declared pricing edits')
    price_module = load(HERE / 'pricing.py', 'composition_price')
    raw = support.inputs()
    source = json.loads(gzip.decompress(raw[support.WORD]))
    local_word = constructor.construct(source)
    need(constructor.payload(local_word) == gzip.decompress((LIFT / 'WORD.json.gz').read_bytes()),
         'Every source word byte')
    word = controller.construct()
    need(price_module.encode(word) == read(TREE / 'CONTROLLER.json'), 'Every retained caller event')
    module_result = module.run()
    caller = controller.replay(word)
    controls = controller.controls(word)
    print('PASS source regeneration, exact module, complete Laurent caller and controls', flush=True)
    with support.checkers() as (L, root):
        directions = lift_checks.preparation(L, source, local_word)
        local = L.replay(local_word)
        need(price_module.encode(local) == read(LIFT / 'RESULT.json')['local'], 'Complete lifted local invoice')
        controls.update(lift_checks.word_controls(L, local_word))
        columns = L.reverse_columns(local_word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'All native input columns')
        print('PASS arbitrary inputs, lifted bases, ownership and separate dense transpose', flush=True)
        native = L.native(local_word)
        maps = physical.physical(word, local_word, L)
        need(maps['full_calls'] == 19 and maps['physical_contacts'] == 7904, 'Every native caller contact')
        print('PASS native maps, absolute phases and complete caller binding', flush=True)
        price = price_module.run(local, native, word, maps, L)
        E = L.load(root / 'research/higher-moment-strictification/verify.py', 'composition_comparison')
        previous = read(TREE / 'RESULT.json')['price']
        old_targets = {int(r): n for r, n in previous['targets'].items()}
        old_paid = {int(r): n for r, n in previous['paid'].items()}
        old_margin = E.moment(old_targets, 1-price_module.KAPPA)[1] - E.moment(old_paid, 1-price_module.KAPPA)[0]
        need(old_margin < 0, 'The prior complete tree bill fails at the new claim')
        for label, kind, rank, count in [('unpaid_carrier', 'paid', 3, -1),
                                         ('missing_target_debit', 'helpers', 9, 1)]:
            bad = deepcopy(local)
            bad[kind][rank] += count
            controls[label] = lift_checks.reject(lambda: price_module.assemble(bad, native, word, maps))
        paid_delta = Counter({int(r): n for r, n in price['paid'].items()})
        paid_delta.subtract(old_paid)
        target_delta = Counter({int(r): n for r, n in price['targets'].items()})
        target_delta.subtract(old_targets)
        paid_delta = {r: n for r, n in paid_delta.items() if n}
        target_delta = {r: n for r, n in target_delta.items() if n}
        need(paid_delta == {1: 19, 2: 19, 3: 19, 4: 38, 5: -76}, 'Exact complete paid change')
        need(target_delta == {6: 19, 8: 57, 9: -76}, 'Exact complete target change')
        print('PASS full invoice, two exact price engines, compiler, outer ledger and debit controls', flush=True)
        return price_module.encode(dict(
            status=STATUS, source_files_authenticated=source_count, module=module_result,
            caller=caller, directions=directions, local=local, columns=columns, native=native,
            physical=maps, price=price, paid_delta=paid_delta, target_delta=target_delta,
            previous_margin_upper=old_margin, controls=controls,
            assumptions=['native_all_columns', 'owned_erasure', 'compiler',
                         'precision_tape', 'analytic_recovery']))


def main():
    with tempfile.TemporaryDirectory(prefix='input-lift-tree-cache-') as cache:
        sys.pycache_prefix = cache
        sys.dont_write_bytecode = True
        result = run()
    if '--write-result' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == read(HERE / 'RESULT.json'), 'Complete retained receipt')
    print(STATUS, flush=True)


if __name__ == '__main__':
    main()
