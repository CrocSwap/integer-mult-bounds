"""Replay the retained source, the merged-paid-job native word and the rebalanced retirement caller.

The archive checks and explicit extension use the PR6545 verifier. Native,
caller, phase, interval and compiler sources keep their original credit.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
import importlib.util
import json
import sys
import tarfile
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
STATUS = 'PASS_PAID_JOB_MERGES_KAPPA_00329700'


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


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid candidate accepted')


def unpack(record, root):
    archive = HERE/record['archive']
    need(sha256(archive.read_bytes()).hexdigest() == record['archive_sha256'],
         'Exact retained archive')
    pins = {p['path']: p for p in record['files']}
    seen = set()
    with tarfile.open(archive, 'r:') as tar:
        for member in tar.getmembers():
            path = PurePosixPath(member.name)
            need(member.isfile() and not path.is_absolute() and '..' not in path.parts
                 and member.name in pins and member.name not in seen,
                 'Declared regular source member')
            seen.add(member.name)
            data = tar.extractfile(member).read()
            pin = pins[member.name]
            need(sha256(data).hexdigest() == pin['sha256'] and
                 sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == pin['git_blob'],
                 'Exact source SHA256 and Git blob')
            target = root/member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    need(seen == set(pins), 'Complete retained inventory')


def adapted(source, kind):
    text = source.read_text()
    for before, after in read(HERE/'ADAPTERS.json')[kind]:
        need(text.count(before) == 1, 'Unique declared '+kind+' edit')
        text = text.replace(before, after)
    return text


class Extension:
    def __init__(self, source_candidate, source, temporary, write):
        self.source_candidate = source_candidate
        self.source = source
        self.temporary = temporary
        self.write = write

    def run(self, native_word, old_caller, local, native, L):
        # The source runs all its checks and compares its frozen caller receipt.
        source_result = self.source_candidate.run(native_word, old_caller, local, native, L)
        controller = sys.modules['controller']
        original = Path(controller.__file__)
        constructor_path = self.temporary/'tree_constructor.py'
        constructor_path.write_text(adapted(original, 'controller'))
        constructor = load(constructor_path, 'tree_constructor')
        data = read(HERE/'ROOT.json')
        original_data = read(original.with_name('ROOT.json'))
        need({k: v for k, v in data.items() if k not in ('children', 'child_sizes')} ==
             {k: v for k, v in original_data.items() if k not in ('children', 'child_sizes')},
             'Only the child trees and their size declaration change')
        need(data['child_sizes'] == [7, 2, 5, 4], 'Declared child allocation')
        base = constructor.construct(data)
        controller.replay(base)
        need(base['events'][:329] == old_caller['events'][:329],
             'The complete source prefix through the retirement cut is unchanged')
        sizes = Counter(len(node['stages']) for node in base['nodes'])
        need(sizes == {2: 8, 3: 2, 4: 2, 5: 1, 7: 1}, 'Every binary supplier size')
        make = load(self.source/'retirement.py', 'tree_retirement')
        checks = load(self.source/'check_caller.py', 'tree_independent')
        word, witness = make.construct(base)
        forward = controller.replay(word)
        reverse = checks.transpose(word)
        pair = checks.dual_pair(base, make.G, make.J)
        controls = controller.controls(word)
        for label, index in [('boundary', 0), ('cut', witness['handoff_after']),
                             ('return', len(word['events'])-1)]:
            bad = deepcopy(word)
            del bad['events'][index]
            controls['missing_'+label] = reject(lambda bad=bad: controller.replay(bad))
        bad = deepcopy(word)
        bad['diagonal'][-1][0] = -1
        controls['unearned_central_target'] = reject(lambda: checks.transpose(bad))
        bad = deepcopy(word)
        bad['events'][witness['handoff_after']][-1] = '-1'
        controls['wrong_cut_sign'] = reject(lambda: controller.replay(bad))

        def jobs(caller):
            return [(e[0], e[1] if e[0] == 'LOCAL' else e[3] if e[0] == 'QUERY' else
                     tuple(e[3] if e[0] == 'IDLE' else e[2]))
                    for e in caller['events'] if e[0] in ('LOCAL', 'QUERY', 'IDLE', 'IDLE_ONE')]

        need(jobs(base) == jobs(word), 'Retirement keeps every rebalanced paid job')
        physical = load(self.source/'physical.py', 'tree_physical').physical(word, native_word, L)
        invoice = load(HERE/'invoice.py', 'tree_invoice')
        need(adapted(self.source/'pricing.py', 'pricing') == (HERE/'pricing.py').read_text(),
             'Every price edit is declared')
        price = load(HERE/'pricing.py', 'tree_price')
        bound = price.run(local, native, word, physical, L)
        changes = invoice.compare(bound, source_result['complete_cost'])
        old_T = {int(k): v for k, v in source_result['complete_cost']['targets'].items()}
        old_P = {int(k): v for k, v in source_result['complete_cost']['paid'].items()}
        E = L.load(L.ROOT/'research/higher-moment-strictification/verify.py', 'tree_comparison')
        other = L.load(L.ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py', 'tree_second_comparison')
        first = E.moment(old_T, 1-price.KAPPA), E.moment(old_P, 1-price.KAPPA)
        tl, th = other.moment(old_T, price.KAPPA)
        pl, ph = other.moment(old_P, price.KAPPA)
        need(first[0][1] < first[1][0] and th < pl,
             'Both rational engines reject PR6545 at the new claim')
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        controls['unpaid_native_job'] = reject(lambda: price.assemble(bad, native, word, physical))
        bad = deepcopy(physical)
        bad['main_targets'][1] += 104
        controls['extra_gaussian_credit'] = reject(lambda: price.assemble(local, native, word, bad))
        for name, value in [('CONTROLLER.json', word), ('WITNESS.json', witness)]:
            if self.write:
                (HERE/name).write_text(json.dumps(value, indent=2)+'\n')
            else:
                need(value == read(HERE/name), 'Exact '+name)
        print('PASS rebalanced caller, independent reverse rows, dual pairs, physical maps and complete price', flush=True)
        candidate = price.encode(dict(caller=forward, reverse=reverse, dual_pair=pair,
            child_sizes=data['child_sizes'], internal_node_sizes=dict(sizes),
            physical=physical, complete_cost=bound, changes=changes, controls=controls,
            source_margin_first=E.display((first[0][0]-first[1][1], first[0][1]-first[1][0])),
            source_margin_second=E.display((tl-ph, th-pl))))
        return {'source': source_result, 'candidate': candidate}


def run(write=False):
    with tempfile.TemporaryDirectory(prefix='paid-job-merges-') as directory:
        root = Path(directory)
        old_cache = sys.pycache_prefix
        sys.pycache_prefix = str(root/'bytecode')
        try:
            pins = read(HERE/'RETAINED.json')
            unpack(pins, root)
            source = root/'research/gaussian-root-retirement'
            # The two edits add one explicit extension parameter. They do not
            # remove or alter a source check, price, receipt or archive.
            driver_path = source/'tree_extension_driver.py'
            driver_path.write_text(adapted(source/'verify.py', 'driver'))
            driver = load(driver_path, 'tree_source_driver')
            result = driver.run(extension=lambda candidate: Extension(candidate, source, root, write))
            candidate = result['candidate']['candidate']
            result['candidate'] = result['candidate']['source']
            need(result == read(source/'RESULT.json'), 'Every PR6545 result and control is unchanged')
            return {'status': STATUS, 'source_head': pins['source_head'],
                    'source_result_sha256': sha256((source/'RESULT.json').read_bytes()).hexdigest(),
                    'candidate': candidate, 'assumptions': result['assumptions'],
                    'selected_frontier_changed': False}
        finally:
            sys.pycache_prefix = old_cache


if __name__ == '__main__':
    need(sys.argv[1:] in ([], ['--write-result']), 'Only --write-result is supported')
    write = bool(sys.argv[1:])
    result = run(write)
    if write:
        (HERE/'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    else:
        need(result == read(HERE/'RESULT.json'), 'Exact complete scientific receipt')
    print(STATUS, flush=True)
