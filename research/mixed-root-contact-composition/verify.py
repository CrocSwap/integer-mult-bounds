"""Compose the fixed mixed root with the exact PR6372 native word.

The source constructors and proof engines retain their original notices.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
import gzip
import importlib.util
import json
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT/'research/mixed-root-source-composition'
CONTACT = 'research/p104-contact-block-contraction/'
STATUS = 'PASS_MIXED_ROOT_CONTACT_COMPOSITION_KAPPA_00328584'


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


def authenticate(data, pin):
    need(sha256(data).hexdigest() == pin['sha256'], 'Exact source SHA256: '+pin['path'])
    need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == pin['git_blob'],
         'Exact source Git blob: '+pin['path'])


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid control accepted')


def delta(after, before):
    result = Counter(after)
    result.subtract(before)
    return {r: n for r, n in result.items() if n}


def contact_source(root):
    manifest = read(HERE/'CONTACT-INPUTS.json')
    archive = HERE/'contact-source.tar'
    need(sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256'], 'Exact PR6372 archive')
    pins = {p['path']: p for p in manifest['files']}
    need(len(pins) == len(manifest['files']) == 8, 'Exact contact-source inventory')
    with tarfile.open(archive, 'r:') as tar:
        members = tar.getmembers()
        need(len(members) == 8 and {m.name for m in members} == set(pins), 'Every retained contact-source file')
        for member in members:
            path = PurePosixPath(member.name)
            need(member.isfile() and not path.is_absolute() and '..' not in path.parts, 'Regular relative retained path')
            data = tar.extractfile(member).read()
            authenticate(data, pins[member.name])
            target = root/member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return manifest


def run():
    live = read(HERE/'SOURCES.json')['files']
    for pin in live:
        if pin['usage'] == 'input':
            authenticate((ROOT/pin['path']).read_bytes(), pin)
    previous = load(PREVIOUS/'verify.py', 'prior_mixed_composition')
    for filename, edits in [('pricing.py', 'PRICING-EDITS.json'), ('ceiling.py', 'CEILING-EDITS.json')]:
        text = (PREVIOUS/filename).read_text()
        for before, after in read(HERE/edits):
            need(text.count(before) == 1, 'One occurrence of each declared '+filename+' edit')
            text = text.replace(before, after)
        need(text == (HERE/filename).read_text(), 'Exact declared '+filename+' adapter')
    with previous.sources() as (root, old_manifest):
        manifest = contact_source(root)
        original = root/previous.ROOT_SOURCE
        joint = root/previous.CONTRACT_SOURCE
        new = root/CONTACT
        load(original/'algebra.py', 'algebra')
        controller = load(original/'controller.py', 'controller')
        physical = load(original/'physical.py', 'contact_root_physical')
        module = load(original/'module_check.py', 'contact_root_module')
        binary = load(root/'research/balanced-query-tree/module_check.py', 'contact_root_binary')
        support = load(joint/'support.py', 'support')
        legacy = load(joint/'construct.py', 'legacy_basis')
        constructor = load(new/'construct.py', 'contact_root_constructor')
        need((joint/'construct.py').read_bytes() == (new/'inputs/pr6353-construct.py').read_bytes(),
             'The exact retained PR6353 basis constructor')
        need((joint/'WORD.json.gz').read_bytes() == (new/'inputs/pr6353-WORD.json.gz').read_bytes(),
             'The exact retained PR6353 native word')
        old_word = json.loads(gzip.decompress((joint/'WORD.json.gz').read_bytes()))
        native_word, witness = constructor.construct(old_word)
        need(native_word == json.loads(gzip.decompress((new/'WORD.json.gz').read_bytes())), 'Every rebuilt PR6372 native word field')
        need(legacy.encode(witness) == read(new/'BASIS.json'), 'Every new rational basis witness')
        need(all(native_word[k] == value for k, value in old_word.items() if k not in ('program', 'final')),
             'Unchanged native interface, inputs and frames')
        need({r: native_word['final'][r] for r in range(770) if native_word['final'][r] != old_word['final'][r]}
             == {224: 245, 227: 245}, 'Only the two declared helper outputs change')
        caller = controller.construct()
        need(caller == read(original/'CONTROLLER.json'), 'Every unchanged mixed caller event')
        root_result, binary_result = module.run(), binary.run()
        caller_result = controller.replay(caller)
        controls = controller.controls(caller)
        price = load(HERE/'pricing.py', 'contact_root_price')
        ceiling = load(HERE/'ceiling.py', 'contact_root_ceiling')
        print('PASS exact source reconstruction, root, normalization and complete caller', flush=True)
        with support.checkers() as (L, frozen):
            old, local = L.replay(old_word), L.replay(native_word)
            need(price.encode(local) == read(new/'RESULT.json')['local'], 'Published PR6372 local receipt')
            need(price.encode(old) == read(PREVIOUS/'RESULT.json')['local'], 'Prior complete composition source')
            pd, td = delta(local['paid'], old['paid']), delta(local['helpers'], old['helpers'])
            need(pd == {4: 2, 5: -2} and td == {8: 2, 9: -2}, 'Exact signed source changes')
            need((local['public_inputs'], local['owned_fields'], local['owned_lifetimes'], local['peak_owned_fields'])
                 == (770, 29, 43, 13), 'All inputs and both new owned lifetimes')
            for label, index in witness['control_indices'].items():
                bad = deepcopy(native_word)
                del bad['program'][index]
                controls['missing_'+label] = reject(lambda: L.replay(bad))
            for role in (224, 227):
                bad = deepcopy(native_word)
                bad['final'][role] = old_word['final'][role]
                controls['missing_target_'+str(role)] = reject(lambda: L.replay(bad))
            columns = L.reverse_columns(native_word)
            need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'All independent native columns')
            native = L.native(native_word)
            maps = physical.physical(caller, native_word, L)
            need(maps['full_calls'] == 18 and maps['physical_contacts'] == 7488, 'All physical caller contacts')
            print('PASS source inputs, dense transpose, native phases, physical caller and owned controls', flush=True)
            bound = price.run(local, native, caller, maps, L)
            old_targets, old_paid = controller.formula_invoice(old)
            need(delta({int(r): n for r, n in bound['paid'].items()}, old_paid) == {r: 18*n for r, n in pd.items()},
                 'All eighteen paid changes')
            need(delta({int(r): n for r, n in bound['targets'].items()}, old_targets) == {r: 18*n for r, n in td.items()},
                 'All eighteen productive target debits')
            E = load(frozen/'research/higher-moment-strictification/verify.py', 'contact_root_comparison')
            fixed_ceiling = ceiling.run(local, E, read(original/'ROOT.json'))
            old_margin = E.moment(old_targets, 1-price.KAPPA)[1]-E.moment(old_paid, 1-price.KAPPA)[0]
            need(old_margin < 0, 'The previous source fails at the new complete claim')
            bad = deepcopy(local); bad['paid'][4] -= 1
            controls['unpaid_native_move'] = reject(lambda: price.assemble(bad, native, caller, maps))
            bad = deepcopy(local); bad['helpers'][9] += 1; bad['helpers'][8] -= 1
            controls['missing_productive_debit'] = reject(lambda: price.assemble(bad, native, caller, maps))
            for pin in manifest['files']:
                data = (root/pin['path']).read_bytes()
                controls['damaged_'+pin['path']] = reject(lambda data=data, pin=pin: authenticate(bytes([data[0]^1])+data[1:], pin))
            print('PASS both prices, complete compiler and outer ledger, source controls and all-size ceiling', flush=True)
        return price.encode({'status': STATUS, 'source_head': manifest['source_head'],
            'root_source': old_manifest['root_head'], 'native_events': len(native_word['program']),
            'root': root_result, 'binary': binary_result, 'caller': caller_result,
            'local': local, 'paid_delta': pd, 'target_delta': td, 'columns': columns,
            'native': native, 'physical': maps, 'price': bound, 'fixed_root_ceiling': fixed_ceiling,
            'prior_source_margin_upper': old_margin, 'controls': controls,
            'gain_over_pr6372': price.KAPPA-Q('.00315087'),
            'relative_gain_over_pr6372_percent': 100*(price.KAPPA/Q('.00315087')-1),
            'assumptions': ['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
            'selected_frontier_changed': False})


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    with tempfile.TemporaryDirectory(prefix='mixed-contact-cache-') as cache:
        sys.pycache_prefix = cache
        result = run()
    if sys.argv[1:] == ['--write-result']:
        (HERE/'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    else:
        need(not sys.argv[1:], 'Only --write-result is supported')
        need(result == read(HERE/'RESULT.json'), 'Exact complete scientific receipt')
    print(STATUS, flush=True)
