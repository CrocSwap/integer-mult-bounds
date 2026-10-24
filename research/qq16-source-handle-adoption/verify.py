#!/usr/bin/env python3
"""Literal retained-source oracle versus a paid stable-handle transaction."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'research/qq16-finite-handle-charge'))
from kernel import need, validate
from observer import snapshot, SKIP
from frontend import Frontend, BANK, PRIVATE, PARKED, PARKING, OUTPUT, PACKETS, PARKING_ROLES


class Tape:
    """Marker-only oracle; no physical body or erasure-cost claim."""
    serial = 0
    def __init__(self):
        Tape.serial += 1
        self.handle = Tape.serial
        self.head = 0
        self.marker = '^'
    def step(self, step): self.head += step
    def read(self): return self.marker if self.head == -1 else '_'
    def clear(self): need(self.head == 0, 'oracle clear at origin')


def erase_marker(tape):
    need(tape.head == 0, 'oracle marker at origin')
    tape.marker = '_'


class Owner:
    schema = ('bank', 'private', 'roles', 'parked', 'parking', 'output', 'capsule',
              'native_child', 'binding', 'counter', 'backref', 'alias', 'closed')
    def packet(self, target):
        return (self.bank.packets + self.private)[target]


class Bank: schema = ('packets', 'output')
class Parking: schema = ('roles', 'stack', 'reverse')


def owner():
    x = Owner()
    x.bank = Bank(); x.bank.packets = (Tape(), Tape()); x.bank.output = Tape()
    x.private = (Tape(), Tape())
    x.roles = {'first': Tape(), 'second': Tape()}
    x.parked = (*x.roles.values(), *x.bank.packets, *x.private)
    x.parking = Parking(); x.parking.roles = x.parked
    x.parking.stack, x.parking.reverse = Tape(), Tape()
    x.output = Tape()
    x.capsule = {'current': Tape()}
    x.native_child = None
    x.binding = types.SimpleNamespace(slots=2)
    x.counter, x.backref, x.alias, x.closed = 1, x, None, True
    return x


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source integrity: '+row['path'])


def sources():
    raw = (ROOT/'research/qq16-caller-install/installer.py').read_bytes()
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'owned_tapes')
    records = types.ModuleType('records'); records.Tape = Tape; sys.modules['records'] = records
    env = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'retained/owned_tapes', 'exec'), env)
    with tarfile.open(ROOT/'research/qq16-complete-cost/inputs/PR4172.tar') as archive:
        raw = archive.extractfile('research/qq16-native-history/inputs/PR4167.tar').read()
    need(hashlib.sha256(raw).hexdigest() == '68ff3b4b541434cb9df15884d027838cbc80300e9d78015eb82c395c5168d166', 'nested source pin')
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        raw = archive.extractfile('research/qq16-protocol-comparison/adapter.py').read()
    need(hashlib.sha256(raw).hexdigest() == '77c01376ac43339a7c99ab377c7947cb89b44e96ff4a826becb545cccd045fef', 'adoption source pin')
    node = next(n for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.FunctionDef) and n.name == 'adopt_return')
    adoption = dict(need=need, LEFT='^', erase_marker=erase_marker)
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'retained/adopt_return', 'exec'), adoption)
    module = types.ModuleType('retained_return_protocol')
    exec(compile((ROOT/'research/qq16-protected-return-caller/adapter.py').read_bytes(), 'retained/adapter.py', 'exec'), module.__dict__)
    return env['owned_tapes'], adoption['adopt_return'], module.ReturnProtocol


def compile_fixture(roots):
    """Test-only pre-input compiler, explicit class schemas and identity table.

    This is not a source-runtime frontend and is not included in its tariff.
    """
    objects, records = [None], [(0, 0, [])]
    def visit(value):
        if not isinstance(value, (Tape, Owner, Bank, Parking, tuple, list, dict)):
            return 0
        for index, existing in enumerate(objects):
            if value is existing:
                return index
        index = len(objects); objects.append(value); records.append(None)
        if isinstance(value, Tape):
            records[index] = (value.handle, 0, [])
        elif isinstance(value, (tuple, list, dict)):
            children = value.values() if isinstance(value, dict) else value
            records[index] = (0, 0, [(visit(v), True) for v in children])
        else:
            records[index] = (0, len(value.schema), [(visit(getattr(value, key)) if key != 'binding' else 0,
                                                    key not in SKIP) for key in value.schema])
        return index
    handles = [visit(root) for root in roots]
    return records, handles, objects


def run_case(service_call, target, numeric=False, stale_alias=False):
    Tape.serial = 0
    owned_tapes, adoption, Protocol = sources()
    service, native, parent = owner(), owner(), owner()
    service.native_child = parent.native_child = native
    caller = service if service_call else parent
    if numeric:
        caller.counter = 10**100000
    if stale_alias:
        caller.alias = caller.bank.packets
    engines = (owned_tapes(service), owned_tapes(native))
    auxiliary, storage_roles = (Tape(),), (Tape(),)
    storage = types.SimpleNamespace(external_roles=(*engines[0], *engines[1], *auxiliary), roles=storage_roles, acquisition=None)
    def distinct():
        values = (*storage.roles, *storage.external_roles)
        need(len(set(values)) == len(values), 'source storage separation')
    storage._distinct = distinct
    installation = types.SimpleNamespace(service=service, native_child=native, engine_roles=engines, storage=storage)
    protocol = Protocol(parent, installation, owned_tapes, adoption, lambda *a: None, erase_marker)
    engine_holder, external_holder = [engines], [storage.external_roles]
    records, roots, objects = compile_fixture([service, native, parent, engine_holder, external_holder, auxiliary, storage_roles])
    machine = Frontend(256, records, roots)
    checks, invoices, update_deltas, scalar_deltas = 0, [], [], []
    need(machine.store.accesses <= 1024*256**2 and machine.store.scalar <= 2048*256**2,
         'constructor tariff')
    stable_tapes = {id(t): t.handle for t in objects if isinstance(t, Tape)}
    initial_dfs = [machine.dfs(root) for root in roots[:3]]
    for round_number in range(4):
        # Physical source contracts are supplied by the marker oracle, not by
        # the metadata implementation; return payloads are outside this test.
        result = native.output; result.marker = '^'; caller.packet(target).marker = '^'
        source_before = snapshot(protocol, Tape, stable_tapes)
        for root, obj in zip(roots[:3], (service, native, parent), strict=True):
            need(machine.dfs(root) == [t.handle for t in owned_tapes(obj)], 'exact pre-return DFS order')
        validate(source_before, 2048)
        validate(machine.inventory(), 2048)
        before_access = machine.store.accesses
        before_scalar = machine.store.scalar
        old, new = machine.adopt(roots[0] if service_call else roots[2], roots[1], target, 2)
        machine.caches(roots[3], roots[4], old, new, service_call, roots[5])
        update_deltas.append(machine.store.accesses-before_access)
        scalar_deltas.append(machine.store.scalar-before_scalar)
        need(update_deltas[-1] <= 256*256**2 and scalar_deltas[-1] <= 1024*256**2,
             'per-transaction tariff')
        source_failed = False
        try:
            protocol(caller, target, result)
        except ValueError as error:
            need(stale_alias and ('producer disjoint' in str(error) or 'current complete engine inventory' in str(error)), 'specific alias failure: '+str(error))
            source_failed = True
        for root, obj in zip(roots[:3], (service, native, parent), strict=True):
            need(machine.dfs(root) == [t.handle for t in owned_tapes(obj)], 'exact post-return DFS order')
        pair = machine.sequence(machine.edge(roots[3], 0))
        need([machine.dfs(x) for x in pair] == [[t.handle for t in row] for row in installation.engine_roles], 'literal ordered cache updates')
        need(machine.dfs(machine.edge(roots[4], 0)) == [t.handle for t in storage.external_roles], 'literal external update')
        caller_handle = roots[0] if service_call else roots[2]
        parked = machine.edge(caller_handle, PARKED)
        need(parked == machine.edge(machine.edge(caller_handle, PARKING), PARKING_ROLES), 'fresh tuple identity shared')
        if stale_alias:
            try:
                validate(machine.inventory(), 2048)
            except ValueError as error:
                need('producer separated' in str(error), 'finite-store alias rejection')
            else:
                raise ValueError('finite store accepted retained old tuple alias')
        else:
            validate(machine.inventory(), 2048)
        checks += 1
        gc_access, gc_scalar = machine.store.accesses, machine.store.scalar
        machine.collect()
        need(machine.store.accesses-gc_access <= 64*256**3 and
             machine.store.scalar-gc_scalar <= 256*256**3, 'collection tariff')
        if stale_alias:
            need(source_failed, 'retained old tuple alias must fail source inventory')
            break
    invoices.append(machine.finish())
    return dict(checks=checks, initial_dfs=initial_dfs, bill=invoices[0], constructor_accesses=machine.constructor_accesses, peak_update_accesses=max(update_deltas),
                peak_update_scalar=max(scalar_deltas))


def compute():
    authenticate()
    positive = [run_case(service, target) for service in (False, True) for target in (0, 2)]
    huge = run_case(False, 0, numeric=True)
    need(huge == positive[0], 'opaque numeric values absent from machine and invoice')
    alias = run_case(False, 0, stale_alias=True)
    return dict(status='PASS_QQ16_SOURCE_HANDLE_ADOPTION_PARTIAL', positive_transactions=sum(x['checks'] for x in positive),
                numeric_control_transactions=huge['checks'], stale_tuple_alias_rejections=alias['checks'],
                constructor_capacity=256, numeric_decimal_exponent=100000,
                peak_accesses=max(x['bill']['accesses'] for x in positive),
                peak_bits=max(x['bill']['bits'] for x in positive),
                peak_update_accesses=max(x['peak_update_accesses'] for x in positive),
                peak_update_scalar=max(x['peak_update_scalar'] for x in positive),
                constructor_accesses=positive[0]['constructor_accesses'],
                scope='Literal adoption and cache metadata refinement only; marker-only Tape oracle; no complete frontend F or full source fixture replay.')


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--write', action='store_true'); args=parser.parse_args()
    result=compute(); path=HERE/'RESULT.json'
    if args.write: path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else: need(result == json.loads(path.read_text()), 'deterministic complete receipt')
    print(result['status'])


if __name__ == '__main__': main()
