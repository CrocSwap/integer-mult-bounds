"""Check the fixed-root and contracted-source composition.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The earlier contracted-mixed-query-local package supplies this adapter.
All retained sources and proof engines keep their original notices.
"""
from collections import Counter
from copy import deepcopy
from contextlib import contextmanager
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
ROOT_SOURCE = 'research/mixed-projector-query-root/'
CONTRACT_SOURCE = 'research/p104-joint-output-contraction/'
STATUS = 'PASS_MIXED_ROOT_SOURCE_COMPOSITION_KAPPA_00328551'


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
    need(sha256(data).hexdigest() == pin['sha256'], 'Source SHA256: '+pin['path'])
    blob = b'blob '+str(len(data)).encode()+b'\0'+data
    need(sha1(blob).hexdigest() == pin['git_blob'], 'Source Git blob: '+pin['path'])


@contextmanager
def sources():
    manifest = read(HERE/'INPUTS.json')
    archive = HERE/'sources.tar'
    need(sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256'], 'Source archive hash')
    pins = {p['path']:p for p in manifest['files']}
    need(len(pins) == len(manifest['files']) == 38, 'Exact source inventory')
    with tempfile.TemporaryDirectory(prefix='contracted-mixed-sources-') as temp:
        root = Path(temp)
        with tarfile.open(archive, 'r:') as tar:
            members = tar.getmembers()
            need(len(members) == len(pins) and {m.name for m in members} == set(pins),
                 'No extra, missing or duplicate archive members')
            for member in members:
                path = PurePosixPath(member.name)
                need(member.isfile() and not path.is_absolute() and '..' not in path.parts,
                     'Regular relative source file')
                data = tar.extractfile(member).read()
                authenticate(data, pins[member.name])
                out = root/member.name
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
        yield root, manifest


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid control accepted')


def delta(after, before):
    out = Counter(after)
    out.subtract(before)
    return {r:n for r,n in out.items() if n}


def run():
    with sources() as (root, manifest):
        source = root/ROOT_SOURCE
        joint = root/CONTRACT_SOURCE
        text = (source/'pricing.py').read_text()
        for before, after in read(HERE/'PRICING-EDITS.json'):
            need(text.count(before) == 1, 'One occurrence of each declared pricing edit')
            text = text.replace(before, after)
        need(text == (HERE/'pricing.py').read_text(), 'Exact declared price adapter')
        text = (source/'ceiling.py').read_text()
        for before, after in read(HERE/'CEILING-EDITS.json'):
            need(text.count(before) == 1, 'One occurrence of each declared ceiling edit')
            text = text.replace(before, after)
        need(text == (HERE/'ceiling.py').read_text(), 'Exact declared ceiling adapter')
        ceiling = load(HERE/'ceiling.py', 'composed_fixed_ceiling')
        load(source/'algebra.py', 'algebra')
        controller = load(source/'controller.py', 'controller')
        module = load(source/'module_check.py', 'composed_root_module')
        physical = load(source/'physical.py', 'composed_physical')
        price = load(HERE/'pricing.py', 'composed_price')
        support = load(joint/'support.py', 'support')
        constructor = load(joint/'construct.py', 'construct')
        checks = load(joint/'verify.py', 'composed_source_checks')
        binary = load(root/'research/balanced-query-tree/module_check.py', 'composed_binary')
        native_source = json.loads(gzip.decompress(support.inputs()[support.WORD]))
        native_word, witness = constructor.construct(native_source)
        need(constructor.payload(native_word) == gzip.decompress((joint/'WORD.json.gz').read_bytes()),
             'Every contracted native word byte')
        need(constructor.encode(witness) == read(joint/'BASIS.json'), 'Every joint-basis witness')
        word = controller.construct()
        need(word == read(source/'CONTROLLER.json'), 'Every fixed root and child event')
        root_check, binary_check = module.run(), binary.run()
        caller = controller.replay(word)
        controls = controller.controls(word)
        print('PASS fixed root, normalization, binary children, complete caller and controls', flush=True)
        with support.checkers() as (L, frozen):
            old, local = L.replay(native_source), L.replay(native_word)
            need(price.encode(local) == read(joint/'RESULT.json')['local'], 'Published contracted local receipt')
            pd, td = delta(local['paid'], old['paid']), delta(local['helpers'], old['helpers'])
            need(pd == {1:14,2:-4,3:-3,4:4,5:-5}, 'Exact paid source change')
            need(td == {5:1,8:8,9:-9}, 'Exact productive target debit')
            controls.update(checks.word_controls(L, native_word, witness))
            columns = L.reverse_columns(native_word)
            need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'All separate native columns')
            print('PASS joint bases, arbitrary inputs, owned lifetimes and separate dense transpose', flush=True)
            native = L.native(native_word)
            maps = physical.physical(word, native_word, L)
            need(maps['full_calls'] == 18 and maps['physical_contacts'] == 7488, 'Every physical caller contact')
            print('PASS native absolute phases, all main contacts and whole idle jobs', flush=True)
            bound = price.run(local, native, word, maps, L)
            old_targets, old_paid = controller.formula_invoice(old)
            targets = {int(r):n for r,n in bound['targets'].items()}
            paid = {int(r):n for r,n in bound['paid'].items()}
            need(delta(targets, old_targets) == {r:18*n for r,n in td.items()}, 'All eighteen target debits')
            need(delta(paid, old_paid) == {r:18*n for r,n in pd.items()}, 'All eighteen paid changes')
            E = L.load(frozen/'research/higher-moment-strictification/verify.py', 'composed_comparison')
            def margin(t, p, k):
                a,b = E.moment(t,1-k),E.moment(p,1-k)
                return a[0]-b[1],a[1]-b[0]
            fixed_ceiling = ceiling.run(local,E,read(source/'ROOT.json'))
            old_upper = margin(old_targets,old_paid,price.KAPPA)[1]
            need(old_upper < 0, 'Unchanged native source fails at the new claim')
            old_root = [Q('0.00328468791927'),Q('0.00328468791928')]
            need(margin(old_targets,old_paid,old_root[0])[0]>0 and
                 margin(old_targets,old_paid,old_root[1])[1]<0, 'Exact same-caller old crossing')
            bad = deepcopy(local);bad['paid'][1]-=1
            controls['unpaid_native_move'] = reject(lambda:price.assemble(bad,native,word,maps))
            bad = deepcopy(local);bad['helpers'][9]+=1;bad['helpers'][8]-=1
            controls['missing_target_debit'] = reject(lambda:price.assemble(bad,native,word,maps))
            for pin in manifest['files']:
                data = (root/pin['path']).read_bytes()
                controls['damaged_'+pin['path']] = reject(lambda data=data,pin=pin:authenticate(bytes([data[0]^1])+data[1:],pin))
            print('PASS complete bill, both rational prices, compiler, outer checks and source controls', flush=True)
        return price.encode(dict(status=STATUS,source_files=len(manifest['files']),
            root_source=manifest['root_head'],contracted_source=manifest['contract_head'],
            root=root_check,binary=binary_check,caller=caller,local=local,paid_delta=pd,target_delta=td,
            fixed_root_ceiling=fixed_ceiling,
            columns=columns,native=native,physical=maps,price=bound,
            same_caller_old_root=old_root,same_caller_old_margin_upper=old_upper,
            gain_over_pr6353=price.KAPPA-Q('.00315057'),
            relative_gain_over_pr6353_percent=100*(price.KAPPA/Q('.00315057')-1),
            negative_controls=controls,
            assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
            selected_frontier_changed=False,published=False))


def main():
    with tempfile.TemporaryDirectory(prefix='contracted-mixed-cache-') as cache:
        sys.pycache_prefix=cache
        result=run()
    if sys.argv[1:]==['--write-result']:
        (HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        need(not sys.argv[1:], 'Only --write-result is supported')
        need(result==read(HERE/'RESULT.json'), 'Exact retained scientific receipt')
    print(STATUS,flush=True)


if __name__=='__main__':
    main()
