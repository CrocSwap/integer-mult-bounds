#!/usr/bin/env python3
"""Adapted sparse execution of authenticated full natural-root preparation."""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

PINS = {
    'CONTRACT.json': 'fb9f1b971bd9c2e7aabc963d299177a2cac84d3ba9106e55cbcb827e1da32ea1',
    'CASES.json': '04a4a6d479e1650b718dc5e6eab0c1ad254bafd070a12ede34dfecbf136397e0',
    'SOURCE-PINS.json': '5f344aab83d23b178c369186b6d51ca33d7b9cf64067ccc522a4339aba21e380',
}
BL, LEFT, BASE, Z, O, SEP, END = range(7)
CAP = 8388608


class Failure(Exception):
    pass


class Semantic(Failure):
    pass


def need(ok, message):
    if not ok:
        raise Failure(message)


def semantic(ok, message):
    if not ok:
        raise Semantic(message)


def integer(value):
    need(type(value) is int, 'Boolean/noninteger proof value')
    return value


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True) + '\n').encode('ascii')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def no_real(token):
    raise Failure('float/nonfinite JSON token: ' + token)


def parse(data):
    need(len(data) <= CAP, 'JSON byte limit')
    try:
        return json.loads(data, object_pairs_hook=unique,
                          parse_float=no_real, parse_constant=no_real)
    except (ValueError, UnicodeError) as exc:
        raise Failure('invalid JSON: ' + str(exc)) from exc


def read_raw(path, cap=CAP):
    with path.open('rb') as stream:
        raw = stream.read(cap + 1)
    need(len(raw) <= cap, 'raw input byte cap: ' + str(path))
    return raw


def authenticate(base):
    meta = {}
    for name, expected in PINS.items():
        raw = read_raw(base / name)
        need(hashlib.sha256(raw).hexdigest() == expected, 'metadata hash: ' + name)
        meta[name] = parse(raw)
    manifest = meta['SOURCE-PINS.json']
    need(type(manifest['sources']) is list and len(manifest['sources']) == 20,
         'twenty source objects')
    raw_sources, hashes = {}, {}
    for row in manifest['sources']:
        name = row['local_path']
        need(type(name) is str and not Path(name).is_absolute()
             and '..' not in Path(name).parts and name not in raw_sources,
             'safe unique source path')
        raw = read_raw(base / name, integer(row['bytes']))
        need(len(raw) == integer(row['bytes']), 'source length: ' + name)
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA: ' + name)
        blob = b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob: ' + name)
        raw_sources[name], hashes[name] = raw, row['sha256']
    return meta, raw_sources, hashes


def validate_program(program, count=31821, tapes=27):
    need(type(program) is dict and set(program) == {'entry', 'tapes', 'instructions'},
         'program keys')
    rows = program['instructions']
    need(type(rows) is list and len(rows) == count, 'actual instruction count')
    need(integer(program['tapes']) == tapes and integer(program['entry']) == 0,
         'actual tape/entry contract')
    for pc, row in enumerate(rows):
        need(type(row) is list and row and type(row[0]) is str, 'instruction row')
        op = row[0]
        need(op in ('branch', 'write', 'move', 'goto', 'halt', 'reject'), 'opcode')
        arity = {'branch': 4, 'write': 3, 'move': 3, 'goto': 2, 'halt': 1, 'reject': 2}
        need(len(row) == arity[op], 'instruction arity')
        if op in ('branch', 'write', 'move'):
            need(0 <= integer(row[1]) < tapes, 'instruction tape')
        if op == 'branch':
            need(type(row[2]) is list, 'branch pairs')
            symbols = []
            for pair in row[2]:
                need(type(pair) is list and len(pair) == 2, 'branch pair')
                need(0 <= integer(pair[0]) <= 6, 'branch symbol')
                need(0 <= integer(pair[1]) < len(rows), 'branch target')
                symbols.append(pair[0])
            need(len(set(symbols)) == len(symbols), 'repeated branch symbol')
            need(0 <= integer(row[3]) < len(rows), 'default target')
        elif op == 'write':
            need(0 <= integer(row[2]) <= 6 and pc + 1 < len(rows), 'write')
        elif op == 'move':
            need(integer(row[2]) in (-1, 1) and pc + 1 < len(rows), 'unit move')
        elif op == 'goto':
            need(0 <= integer(row[1]) < len(rows), 'goto target')
        elif op == 'reject':
            need(type(row[1]) is str, 'reject reason')


def expand_table(raw):
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(CAP + 1)
    table = parse(expanded)
    need(type(table) is dict and set(table) == {'schema', 'program', 'metadata'},
         'source table root')
    return table


def candidate(base, raw):
    table = expand_table(raw['inputs/TABLE.json.gz'])
    old = expand_table(raw['source/inputs/core/TABLE.json.gz'])
    validate_program(table['program'])
    validate_program(old['program'], 20897, 25)
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('independent_root_candidate',
                                                 base / 'source/root_prefix.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    program, metadata = module.build(4, 3, 1)
    built = parse(canonical({'program': {'entry': program.entry, 'tapes': program.tapes,
                                       'instructions': program.instructions},
                             'metadata': metadata}))
    need(built == {'program': table['program'], 'metadata': table['metadata']},
         'complete source/constructed table mismatch')
    validate_old_links(old, built)
    return table['program'], table['metadata'], digest(built)


def validate_old_links(old, built):
    rows = built['program']['instructions']
    old_rows = old['program']['instructions']
    changes = built['metadata']['core_link_changes']
    need(type(changes) is list and len(changes) == 2, 'two core link changes')
    actual = [index for index, row in enumerate(old_rows) if rows[index] != row]
    need(actual == [change['pc'] for change in changes], 'complete unchanged old prefix')
    for change in changes:
        pc = integer(change['pc'])
        need(old_rows[pc] == change['old'] and rows[pc] == change['linked'],
             'actual old/new link rows')
    need(changes[0]['old'] == ['goto', old['metadata']['events']['node_entry']]
         and changes[1]['old'] == ['halt'], 'entry/final-halt link identities')
    for key, value in old['metadata'].items():
        if key != 'tapes':
            need(built['metadata'][key] == value, 'unchanged old metadata: ' + key)


def encode(symbols):
    return [O if symbol & (1 << shift) else Z
            for symbol in symbols for shift in (2, 1, 0)]


def header(value):
    need(type(value) is int and value > 0, 'positive header fixture')
    return [LEFT] + [O if value & (1 << i) else Z
                     for i in range(value.bit_length())] + [BASE]


def split_banks(bits, A, L, R):
    return [[bit for a in range(A)
             for bit in bits[(a * L + low) * R:(a * L + low + 1) * R]]
            for low in range(L)]


def expected(bits, A, R, H, L, remaining):
    banks = split_banks(bits, A, L, R)
    if remaining == 0:
        banks[0] = [1 - bit for bit in banks[0]]
    else:
        for low in (0, 1):
            banks[low] = expected(banks[low], A // (L * H), H * R,
                                  H, L, remaining - 1)
    return [bit for a in range(A) for low in range(L)
            for bit in banks[low][a * R:(a + 1) * R]]


def tape_object(cells, head):
    return {'head': head, 'cells': [[key, cells[key]] for key in sorted(cells)]}


class Sparse:
    def __init__(self, case, metadata, contract):
        self.case, self.meta, self.contract = case, metadata, contract
        self.prefix = case['prefix']
        self.origin = self.prefix + 1
        self.heads = [self.origin] * 27
        self.cells = []
        for role in range(27):
            cells = {-2: O, -1: Z, 50000: Z, 50001: O}
            cells.update({i: O if i % 2 == 0 else Z for i in range(self.prefix)})
            cells[self.prefix] = LEFT if role < metadata['payloads'] else BASE
            self.cells.append(cells)
        self.H = case['q'] ** (case['N'] * case['N'] * (case['w'] - 1))
        self.A = case['T'] * (case['L'] * self.H) ** case['d']
        self.R = self.H * case['R_body']
        self.V = case['L'] * self.A * self.R
        self.bits = [int((i * i + 5 * i + 3) % 11 < 5) for i in range(self.V)]
        ports = metadata['ports']
        self.put(ports['source'], [LEFT] + [O if b else Z for b in self.bits] + [BASE])
        for role, value in ((metadata['T_input'], case['T']),
                            (metadata['R_body_input'], case['R_body']),
                            (metadata['width'], case['w'])):
            self.put(role, header(value))
        self.cells[metadata['depth']].update({self.origin + i: O for i in range(case['d'])})
        self.initial_cells = copy.deepcopy(self.cells)
        self.initial_heads = self.heads[:]
        self.visits = [set() for _ in range(27)]
        borrowed = (ports['source'], metadata['T_input'], metadata['R_body_input'])
        self.protected = {t: set(range(self.origin, max(
            key for key in self.cells[t] if key < 50000) + 1)) for t in borrowed}
        self.frames, self.outputs = [], []
        self.nodes, self.grants, self.returns = [], [], []
        self.root = {}
        self.high_readonly = self.ar_readonly = False
        self.ar_protected = {}
        for role, value in ((ports['repeats_input'], self.A), (ports['block_input'], self.R)):
            self.ar_protected[role] = set(range(self.origin, self.origin + len(encode(header(value)))))
        self.steps = 0

    def put(self, role, symbols):
        for offset, symbol in enumerate(encode(symbols)):
            self.cells[role][self.origin + offset] = symbol
        self.heads[role] = self.origin + 3

    def visit(self, role, position):
        limits = self.contract['limits']
        need(limits['visited_address_min'] <= position <= limits['visited_address_max'],
             'visited address cap')
        self.visits[role].add(position)

    def write(self, role, symbol):
        position = self.heads[role]
        self.visit(role, position)
        forbidden = (position <= self.prefix or position in (50000, 50001)
                     or role in (self.meta['width'], self.meta['depth'], self.meta['T_input'],
                                 self.meta['R_body_input'])
                     or position in self.protected.get(role, ())
                     or (self.high_readonly and role == self.meta['high'])
                     or (self.ar_readonly and position in self.ar_protected.get(role, ())))
        semantic(not forbidden, 'write protection')
        if symbol == BL:
            self.cells[role].pop(position, None)
        else:
            self.cells[role][position] = symbol

    def packet(self, role):
        marker = LEFT if role < self.meta['payloads'] else BASE
        start = self.heads[role] - 1
        while self.cells[role].get(start, BL) != marker:
            semantic(start > -8, 'packet origin delimiter')
            start -= 1
        position, symbols = start + 1, []
        while True:
            semantic(position < 40000, 'packet scan cap')
            triple = [self.cells[role].get(position + j, BL) for j in range(3)]
            semantic(all(value in (Z, O) for value in triple), 'incomplete encoded packet')
            value = sum((value == O) << (2 - j) for j, value in enumerate(triple))
            semantic(0 <= value <= 6, 'invalid encoded symbol')
            symbols.append(value)
            position += 3
            if value == BASE:
                break
        semantic(symbols[0] == LEFT and all(s in (Z, O) for s in symbols[1:-1]),
                 'marked bit packet')
        return [int(s == O) for s in symbols[1:-1]]

    def number(self, role):
        bits = self.packet(role)
        semantic(bits and bits[-1] == 1, 'positive canonical observed header')
        return sum(bit << index for index, bit in enumerate(bits))

    def snapshot(self):
        meta = self.meta
        return {'payload': [tape_object(self.cells[t], self.heads[t])
                            for t in range(meta['payloads'])],
                'control': tape_object(self.cells[meta['control']], self.heads[meta['control']]),
                'phase': tape_object(self.cells[meta['phase']], self.heads[meta['phase']])}

    def full_state(self):
        return {'heads': self.heads[:],
                'cells': [tape_object(cells, head)['cells']
                          for cells, head in zip(self.cells, self.heads)]}

    def phase_state(self, fields, output=False):
        cells, heads = copy.deepcopy(self.initial_cells), self.initial_heads[:]
        for role, value in fields:
            for i, symbol in enumerate(encode(header(value))):
                cells[role][self.origin + i] = symbol
            heads[role] = self.origin + 3
        if output:
            bits = expected(self.bits, self.A, self.R, self.H, self.case['L'], self.case['d'])
            role = self.meta['ports']['output']
            for i, symbol in enumerate(encode([LEFT] + [O if bit else Z for bit in bits] + [BASE])):
                cells[role][self.origin + i] = symbol
            heads[role] = self.origin + 3
        return {'heads': heads, 'cells': [tape_object(cells[t], heads[t])['cells']
                                         for t in range(27)]}

    def root_record(self, name, value):
        semantic(name not in self.root, 'duplicate root observation: ' + name)
        self.root[name] = value

    def root_phase(self, name):
        p, meta = self.meta['ports'], self.meta
        fields = [(p['repeats_input'], self.A), (p['block_input'], self.R)]
        if name == 'prefix_start':
            actual = self.full_state()
            semantic(actual == self.phase_state([(meta['high'], self.H)]), 'full prefix-start state')
            self.root_record(name, {'H': self.number(meta['high']), 'state_sha256': digest(actual)})
            self.high_readonly = True
        elif name == 'handoff':
            actual = self.full_state()
            semantic(actual == self.phase_state(fields + [(meta['high'], self.H)]),
                     'full root handoff state')
            A, R, H = self.actual_shape()
            self.root_record(name, {'A': A, 'R': R, 'H': H, 'state_sha256': digest(actual)})
            self.ar_readonly = True
        elif name == 'precleanup':
            actual = self.full_state()
            semantic(actual == self.phase_state(fields, output=True), 'full precleanup state')
            self.root_record(name, {'A': self.number(p['repeats_input']),
                                    'R': self.number(p['block_input']), 'state_sha256': digest(actual)})
            self.ar_readonly = False

    def root_observe(self, pc):
        meta, root_events = self.meta, self.meta['root_events']
        if pc == meta['core_link_changes'][0]['linked'][1]:
            self.root_phase('prefix_start')
        elif pc == root_events['root_depth_restore']:
            head = self.heads[meta['depth']]
            semantic(head == self.origin + self.case['d'], 'root depth before rewind')
            self.root_record('depth_before_rewind', head)
        elif pc == root_events['root_depth_restored']:
            head = self.heads[meta['depth']]
            semantic(head == self.origin, 'root depth after rewind')
            self.root_record('depth_after_rewind', head)
        elif pc == root_events['root_descriptor_handoff']:
            self.root_phase('handoff')
        elif pc == meta['core_link_changes'][1]['linked'][1]:
            self.root_phase('precleanup')
        if pc == meta['events']['root_done']:
            self.high_readonly = False

    def depth(self):
        value = self.heads[self.meta['depth']] - self.origin
        semantic(0 <= value <= self.case['d'], 'observed depth range')
        return value

    def actual_shape(self):
        p = self.meta['ports']
        return (self.number(p['repeats_input']), self.number(p['block_input']),
                self.number(self.meta['high']))

    def node(self):
        A, R, H = self.actual_shape()
        depth = self.depth()
        semantic((A, R, H) == (self.A // ((self.case['L'] * self.H) ** depth),
                               self.R * self.H ** depth, self.H), 'live node shape')
        bits = self.packet(self.meta['ports']['source'])
        semantic(len(bits) == self.case['L'] * A * R, 'complete node source')
        self.nodes.append({'depth': depth, 'A': A, 'R': R, 'H': H,
                           'source_bits': bits})

    def grant(self, site):
        A, R, H = self.actual_shape()
        child_A, child_R = self.number(self.meta['grant_A']), self.number(self.meta['grant_R'])
        bank = self.packet(site)
        semantic(A % (self.case['L'] * H) == 0 and child_A == A // (self.case['L'] * H)
                 and child_R == H * R and len(bank) == A * R, 'actual live grant')
        self.grants.append({'depth': self.depth(), 'site': site, 'A': A, 'R': R,
                            'H': H, 'child_A': child_A, 'child_R': child_R,
                            'bank_bits': bank})

    def push(self):
        phase = self.cells[self.meta['phase']].get(self.origin, BL)
        semantic(phase in (Z, O), 'call phase')
        self.frames.append({'snapshot': self.snapshot(), 'depth': self.depth(),
                            'site': int(phase == O)})

    def save_output(self):
        semantic(self.frames, 'nonroot protected output')
        self.outputs.append(self.packet(self.meta['ports']['output']))

    def protected_output(self):
        semantic(self.outputs, 'missing output protection observation')
        actual = self.packet(self.meta['output_relay'])
        semantic(actual == self.outputs[-1], 'protected child output mismatch')

    def pop(self):
        semantic(self.frames and self.outputs, 'return without frame/output')
        frame, output = self.frames.pop(), self.outputs.pop()
        after = self.snapshot()
        semantic(after == frame['snapshot'], 'full parent restoration')
        semantic(self.depth() == frame['depth'] + 1, 'return depth before decrement')
        self.returns.append({'depth': frame['depth'], 'site': frame['site'],
                             'before_sha256': digest(frame['snapshot']),
                             'after_sha256': digest(after), 'output_bits': output})

    def observe(self, pc):
        events = self.meta['events']
        if pc == events['node_entry']:
            self.node()
        elif pc == events['grant_ready_0']:
            self.grant(0)
        elif pc == events['grant_ready_1']:
            self.grant(1)
        elif pc == events['push_begin']:
            self.push()
        elif pc == events['save_child_output']:
            self.save_output()
        elif pc == events['retire_child']:
            self.protected_output()
        elif pc == events['pop_end']:
            self.pop()

    def dispatch(self, row, pc, branches):
        op = row[0]
        if op == 'branch':
            role = row[1]
            self.visit(role, self.heads[role])
            symbol = self.cells[role].get(self.heads[role], BL)
            return branches[pc].get(symbol, row[3]), False
        if op == 'write':
            self.write(row[1], row[2])
        elif op == 'move':
            role = row[1]
            self.visit(role, self.heads[role])
            self.heads[role] += row[2]
            self.visit(role, self.heads[role])
        elif op == 'goto':
            return row[1], False
        elif op == 'halt':
            return pc, True
        elif op == 'reject':
            raise Semantic('literal reject: ' + row[1])
        else:
            raise Failure('unknown dispatch opcode')
        return pc + 1, False

    def execute(self, program):
        rows = program['instructions']
        branches = {pc: dict(row[2]) for pc, row in enumerate(rows) if row[0] == 'branch'}
        pc, halted = program['entry'], False
        events = set(self.meta['events'].values()) | set(self.meta['root_events'].values())
        events.update(change['linked'][1] for change in self.meta['core_link_changes'])
        while not halted:
            need(self.steps < self.contract['limits']['steps_per_case_cap'], 'step cap')
            need(0 <= pc < len(rows), 'runtime PC')
            if pc in events:
                self.root_observe(pc)
                self.observe(pc)
            self.steps += 1
            pc, halted = self.dispatch(rows[pc], pc, branches)
        return self.finish()

    def finish(self):
        meta, p = self.meta, self.meta['ports']
        wanted_bits = expected(self.bits, self.A, self.R, self.H, self.case['L'], self.case['d'])
        semantic(self.packet(p['output']) == wanted_bits, 'complete root output')
        semantic(not self.frames and not self.outputs, 'unreturned frames/output')
        wanted_cells = copy.deepcopy(self.initial_cells)
        wanted_heads = self.initial_heads[:]
        for i, symbol in enumerate(encode([LEFT] + [O if b else Z for b in wanted_bits] + [BASE])):
            wanted_cells[p['output']][self.origin + i] = symbol
        wanted_heads[p['output']] = self.origin + 3
        semantic(self.cells == wanted_cells, 'complete final ownership/cells')
        semantic(self.heads == wanted_heads, 'complete final heads')
        semantic(set(self.root) == set(self.contract['packet']['root_fields']),
                 'all unique root observations')
        visits = [sorted(positions) for positions in self.visits]
        backing = sum(len(set(before) | seen)
                      for before, seen in zip(self.initial_cells, self.visits))
        return {'id': self.case['id'], 'H': self.H, 'A': self.A, 'R': self.R,
                'volume': self.V, 'steps': self.steps, 'node_entries': self.nodes,
                'grants': self.grants, 'returns': self.returns, 'root': self.root,
                'final': {'heads': self.heads[:],
                          'cells': [tape_object(cells, head)['cells']
                                    for cells, head in zip(self.cells, self.heads)],
                          'visits': visits, 'retained_backing': backing}}


def mutated(program, metadata, name):
    result = copy.deepcopy(program)
    rows, events = result['instructions'], metadata['root_events']
    if name in ('skip_root_prefix', 'skip_final_cleanup'):
        change = metadata['core_link_changes'][0 if name == 'skip_root_prefix' else 1]
        need(rows[change['pc']] == change['linked'], 'actual root link mutation')
        if name == 'skip_final_cleanup':
            need(change['old'] == ['halt'], 'final HALT mutation')
        rows[change['pc']] = change['old'][:]
    elif name == 'skip_depth_rewind':
        at = events['root_depth_restore']
        need(rows[at] == ['move', metadata['depth'], -1], 'depth rewind mutation predicate')
        rows[at] = ['goto', events['root_depth_restored']]
    elif name == 'skip_dummy_retire':
        at = events['root_depth_restored']
        need(rows[at] == ['move', metadata['return'], -1], 'dummy retirement mutation predicate')
        rows[at] = ['goto', events['root_descriptor_handoff']]
    elif name == 'wire_T_to_Rbody':
        first = metadata['core_link_changes'][0]['linked'][1]
        edits = 0
        for row in rows[first:events['root_descriptor_handoff']]:
            if row[0] in ('branch', 'write', 'move') and row[1] == metadata['T_input']:
                row[1] = metadata['R_body_input']
                edits += 1
        need(edits > 0, 'T/body wire mutation nonempty')
    else:
        raise Failure('unknown mutation')
    validate_program(result)
    return result


def control_rows(program, metadata, contract, cases):
    lookup = {case['id']: case for case in cases['healthy']}
    results = []
    for item in cases['controls']:
        changed = mutated(program, metadata, item['id'])
        try:
            Sparse(lookup[item['case']], metadata, contract).execute(changed)
        except Semantic:
            accepted, failure = False, 'semantic_rejected'
        else:
            accepted, failure = True, 'none'
        need(type(item['accepted']) is bool and accepted is item['accepted'],
             'control unexpected acceptance: ' + item['id'])
        results.append({'id': item['id'], 'accepted': accepted, 'failure_gate': failure})
    return results


def produce(base):
    metadata, raw_sources, source_hashes = authenticate(base)
    contract, cases = metadata['CONTRACT.json'], metadata['CASES.json']
    program, meta, table_hash = candidate(base, raw_sources)
    records = [Sparse(case, meta, contract).execute(program) for case in cases['healthy']]
    controls = control_rows(program, meta, contract, cases)
    return {'schema': contract['packet']['schema'], 'sources': source_hashes,
            'table': {'tapes': program['tapes'], 'instructions': len(program['instructions']),
                      'entry': program['entry'], 'sha256': table_hash},
            'cases': records, 'controls': controls}


def validate_receipt(actual, expected):
    need(type(actual) is type(expected), 'receipt strict type')
    if type(expected) is dict:
        need(set(actual) == set(expected), 'receipt exact keys')
        for key in expected:
            validate_receipt(actual[key], expected[key])
    elif type(expected) is list:
        need(len(actual) == len(expected), 'receipt exact list length')
        for left, right in zip(actual, expected):
            validate_receipt(left, right)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--certificate-out', type=Path)
    selection.add_argument('--check', type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    base = args.inputs or (here if (here / 'CONTRACT.json').is_file() else here.parent)
    value = produce(base)
    data = canonical(value)
    need(len(data) <= CAP, 'certificate byte cap')
    if args.certificate_out:
        args.certificate_out.write_bytes(data)
    else:
        raw = read_raw(args.check or (base / 'CERTIFICATE.json'))
        validate_receipt(parse(raw), value)
        need(raw == data, 'whole recomputed certificate bytes mismatch')
    print('PASS natural-root sparse complete generation/handoff/cleanup/execution')


if __name__ == '__main__':
    try:
        main()
    except (Failure, OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        sys.exit(1)
