#!/usr/bin/env python3
"""Exact installed-return composition; finite executions plus source-bound bill.

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
The original caller and protected-return transaction retain their authors.
"""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CALLER = 'research/qq16-caller-install'
SELECTED = 'research/r437-leaf-dispatch/retained/selected-result.json'
CASE_NAMES = ('fixed', 'adopt', 'stale-engines', 'stale-external',
              'output-alias', 'service-stop')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def authenticate():
    rows = json.loads((HERE/'SOURCES.json').read_text())['files']
    inputs = [row for row in rows if row['usage'] == 'input']
    need(len(inputs) == len({r['path'] for r in inputs}), 'unique declared input closure')
    for row in inputs:
        path = ROOT/row['path']
        need(path.is_file() and not path.is_symlink(), 'regular source: '+row['path'])
        raw = path.read_bytes()
        need(sha(raw) == row['sha256'], 'source integrity: '+row['path'])
    return inputs


def projection(root, inputs):
    # Only the historical selected record differs from the current source tree.
    for row in inputs:
        target = root/row['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/row['path']).read_bytes())
    selected = root/'certificates/selected-result.json'
    selected.parent.mkdir(parents=True, exist_ok=True)
    raw = (ROOT/SELECTED).read_bytes()
    need(sha(raw) == 'bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129',
         'exact historical complete selected record')
    selected.write_bytes(raw)


def original_adoption(fixture):
    with tarfile.open(ROOT/'research/qq16-complete-cost/inputs/PR4172.tar') as t:
        nested = t.extractfile('research/qq16-native-history/inputs/PR4167.tar').read()
    need(sha(nested) == '68ff3b4b541434cb9df15884d027838cbc80300e9d78015eb82c395c5168d166',
         'exact retained protocol archive')
    with tarfile.open(fileobj=io.BytesIO(nested)) as t:
        raw = t.extractfile('research/qq16-protocol-comparison/adapter.py').read()
    need(sha(raw) == '77c01376ac43339a7c99ab377c7947cb89b44e96ff4a826becb545cccd045fef',
         'exact retained adoption source')
    matches = [n for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.FunctionDef)
               and n.name == 'adopt_return']
    need(len(matches) == 1, 'exact original return method')
    from words import LEFT
    env = {'need': need, 'LEFT': LEFT, 'erase_marker': fixture.erase_marker}
    exec(compile(ast.Module(body=matches, type_ignores=[]), 'retained-4167/adopt_return', 'exec'), env)
    return env['adopt_return']


def actions(tapes):
    return {key: sum(getattr(t.meter, key) for t in tapes)
            for key in ('reads', 'writes', 'moves')}


def case(name):
    inputs = authenticate()
    with tempfile.TemporaryDirectory(prefix='qq16-return-source-') as td:
        root = Path(td).resolve()
        projection(root, inputs)
        path = root/CALLER/'integrated-fixture.py'
        sys.path.insert(0, str(path.parent))
        fixture = types.ModuleType('retained_integrated_fixture')
        fixture.__file__ = str(path)
        sys.modules[fixture.__name__] = fixture
        exec(compile(path.read_bytes(), str(path), 'exec'), fixture.__dict__)
        adapter = types.ModuleType('return_inventory_adapter')
        adapter.__file__ = str(HERE/'adapter.py')
        exec(compile(Path(adapter.__file__).read_bytes(), adapter.__file__, 'exec'), adapter.__dict__)
        need(fixture.Tape.__eq__ is object.__eq__, 'retained Tape equality is identity')
        adopt_return = original_adoption(fixture)
        original_install = fixture.C.install
        registry, calls, attempts, protocols, cleanup = [], [], [], [], []
        original_tape_init = fixture.Tape.__init__

        def tape_init(tape, *args, **kwargs):
            original_tape_init(tape, *args, **kwargs)
            registry.append(tape)
        fixture.Tape.__init__ = tape_init

        def install(*args, **kwargs):
            installed = original_install(*args, **kwargs)
            parent = args[0].machine
            mode = name if name in ('fixed', 'adopt', 'stale-engines', 'stale-external') else 'adopt'

            def observe(phase, caller, old, result, before=None):
                label = 'producer' if caller is parent else 'service'
                if phase == 'before':
                    # Test observation only. No body size flows to the algorithm.
                    n = len(fixture.raw(result))
                    attempts.append(label)
                    return n, actions((old, result))
                n, measured = before
                after = actions((old, result))
                calls.append({'caller': label, 'bits': n,
                              'return_actions': {k: after[k]-measured[k] for k in after}})
                if name == 'service-stop' and label == 'service':
                    raise ValueError('deliberate stop after adopted service return')

            protocol = adapter.install(parent, installed, fixture.J.owned_tapes,
                                       (root/CALLER/'producer.py').read_bytes(), adopt_return,
                                       fixture.transfer, fixture.erase_marker,
                                       mode=mode, observe=observe)
            protocols.append(protocol)
            if name == 'service-stop':
                original_run = parent.run
                def run(payload, descriptors):
                    image = bytes(payload.cells), payload.head
                    metadata = {k: (bytes(v.tape.cells), v.tape.head) for k, v in descriptors.items()}
                    try:
                        return original_run(payload, descriptors)
                    except ValueError as error:
                        need(str(error) == 'deliberate stop after adopted service return', 'exact service failure')
                        need((bytes(payload.cells), payload.head) == image and
                             all((bytes(descriptors[k].tape.cells), descriptors[k].tape.head) == v
                                 for k, v in metadata.items()), 'controlled failure preserves borrowed state')
                        need(installed.storage.stage == installed.bundle.state == 'closed' and
                             installed.compiler.closed and installed.service.closed and installed.native_child.closed,
                             'actual discard closes service lifetimes')
                        need(all(t.read() == fixture.BLANK for t in fixture.J.owned_tapes(installed)),
                             'actual discard retires current owned inventory')
                        cleanup.append('checked before fixture finally')
                        raise
                parent.run = run
            return installed
        fixture.C.install = install
        try:
            try:
                output = fixture.run_case(mutation='output_alias' if name == 'output-alias' else None)
            except ValueError as error:
                expected = {
                    'stale-engines': 'active producer and original/service engines have distinct fixed inventories',
                    'stale-external': 'current complete external inventory',
                    'output-alias': 'exclusive physical caller/native/wrapper inventory',
                    'service-stop': 'deliberate stop after adopted service return',
                }
                need(name in expected and str(error) == expected[name], 'unexpected rejection: '+str(error))
                need(name != 'service-stop' or len(cleanup) == 1, 'service cleanup checked before fixture cleanup')
                need(name != 'stale-engines' or len(calls) == 4, 'naive adoption reaches actual original fence')
                return {'case': name, 'rejected': str(error), 'completed_returns': len(calls),
                        'attempted_callers': attempts, 'cleanup_observations': cleanup,
                        'original_fixture_cleanup_check': name == 'output-alias'}
            need(name in ('fixed', 'adopt') and len(calls) == 24 and output['completed_generations'] == 2,
                 'complete two-generation execution')
            need([r['caller'] for r in calls] == (['producer']*4+['service']*6+['producer']*2)*2,
                 'source producer-service-later-producer chronology')
            for protocol in protocols:
                protocol.check_inventory()
            return {'case': name, 'scientific': output, 'calls': calls,
                    'record_tape_actions': actions(registry), 'fresh_record_tapes': len(registry),
                    'final_inventory_exact': True}
        finally:
            fixture.Tape.__init__ = original_tape_init
            fixture.runtime.cleanup()


def compute():
    inputs = authenticate()
    rows = {}
    for name in CASE_NAMES:
        with tempfile.TemporaryDirectory(prefix='qq16-return-cache-') as cache:
            command = [sys.executable, '-I', '-B']+(['-O'] if sys.flags.optimize else [])
            command += ['-X', 'pycache_prefix='+cache, str(HERE/'verify.py'), '--case', name]
            process = subprocess.run(command, capture_output=True, text=True, timeout=90)
            need(process.returncode == 0, 'case '+name+': '+process.stdout+process.stderr)
            rows[name] = json.loads(process.stdout)
    fixed, adopted = rows['fixed'], rows['adopt']
    need(canonical(fixed['scientific']) == canonical(adopted['scientific']), 'complete matched scientific endpoint')
    need(fixed['fresh_record_tapes'] == adopted['fresh_record_tapes'], 'no added physical record tape')
    saving = {'reads': 0, 'writes': 0, 'moves': 0}
    for old, new in zip(fixed['calls'], adopted['calls'], strict=True):
        need((old['caller'], old['bits']) == (new['caller'], new['bits']), 'matched complete returned packet')
        n = old['bits']; expected = dict(reads=5*n+2, writes=2*n, moves=4*n+2)
        need({k: old['return_actions'][k]-new['return_actions'][k] for k in saving} == expected,
             'literal old-return versus adopted-return RWM delta')
        for k in saving:
            saving[k] += expected[k]
    need({k: fixed['record_tape_actions'][k]-adopted['record_tape_actions'][k] for k in saving} == saving,
         'whole reduced record-tape difference equals complete return sum')
    # The original source invoices, not the reduced fixture, supply this census.
    compilation = json.loads((ROOT/CALLER/'COMPILATION.json').read_text())
    census = compilation['producer']['root_child_census']
    original = census['baseline_whole_root']
    installed = census['installed_whole_root']
    need(original['calls'] == sum(original['rank_counts'].values()) == 510662,
         'retained whole original source census')
    prior = json.loads((ROOT/'research/qq16-nonterminal-c8-tree/RESULT.json').read_text())
    need(original['rank_counts'] == prior['rank_histogram'], 'independent prior source census agrees')
    need(census['qq16_added_lines']['calls'] == 32 and census['removed_centres']['calls'] == 16,
         'actual changed source occurrence counts')
    expected_histogram = dict(original['rank_counts'])
    expected_histogram['1'] += 32; expected_histogram['8'] -= 16
    need(installed['rank_counts'] == expected_histogram and
         installed['calls'] == sum(expected_histogram.values()) == 510678,
         'complete producer census including retained suffix')
    need(census['retained_later_source_7_481']['calls'] == 493097 and
         census['installed_entry_through_bridge']['calls'] + 493097 == installed['calls'],
         'all later root calls included')
    decoder = compilation['decoder']['physical_per_cover']
    need(decoder['rank_one_children'] == 336, 'complete decoder and continuation child census')
    # Exact source expressions which establish the service quotient is U and
    # rank reduction moves active axes into spectators without reducing b.
    machine = ast.parse((ROOT/'research/physical-complex-controller/machine.py').read_bytes())
    funcs = {n.name:n for n in ast.walk(machine) if isinstance(n,ast.FunctionDef)}
    prepare = ast.unparse(funcs['prepare_child'])
    need('after = Count.product(tail, self.c(\'spacing\'))' in prepare and
         'after.add(self.c(\'after\'))' in prepare and
         "self.c('unused') if name == 'rows'" in prepare,
         'source child width-to-spectator and row transfer')
    decoder_ast = ast.parse((ROOT/CALLER/'decoder.py').read_bytes())
    descriptors = next(n for n in decoder_ast.body if isinstance(n,ast.FunctionDef) and n.name=='service_descriptors')
    descriptor_text = ast.unparse(descriptors)
    need("result['rows'] = Count(caller.c('unused'))" in descriptor_text and
         "result['rows'].multiply_small(families * caller.binding.cover.size)" in descriptor_text,
         'source service rows restore exactly one local family-cover divisor')
    return {'status': 'PASS_QQ16_PROTECTED_RETURN_CALLER', 'live_inputs': len(inputs),
            'cases': rows, 'finite_matched_saving_RWM': saving,
            'source_protocol_census': {'producer_per_Gamma': 510678, 'service_per_Gamma': 336,
                                      'complete_per_Gamma': 511014, 'later_producer_per_Gamma': 493097},
            'whole_root_saving_RWM': ['511014*Gamma*(5*v+2)', '511014*Gamma*(2*v)', '511014*Gamma*(4*v+2)'],
            'finite_rebinding_control': 'separate signed charge; no zero-cost role-swap assumption',
            'scope': 'Installed D* versus frozen D only; no full comparison with B*, numerical supplier admission or new kappa.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=CASE_NAMES)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.case:
        need(not args.write, 'no case artifact writes')
        print(canonical(case(args.case)))
        return
    result = compute()
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(canonical(result) == canonical(json.loads((HERE/'RESULT.json').read_text())), 'typed complete result receipt')
    print(result['status'])


if __name__ == '__main__':
    main()
