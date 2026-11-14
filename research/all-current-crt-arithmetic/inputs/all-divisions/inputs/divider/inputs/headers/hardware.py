"""Finite-graph interpreter with fixed numeric and binary symbol renamings.

Accounting and snapshots observe execution; they never choose its work.
Interpreter lineage: credited B5--B7 hardware. Apache-2.0.
"""

NUMERIC_SYMBOLS = ('0', '1', 'L', 'R', '_', 'WE', 'RE', 'ROOT',
                   'STEP', 'VALUE', 'CONSTANT', 'MULTIPLY', 'PAIR', 'RETURN')
NUMERIC_VALUES = {symbol: value for value, symbol in enumerate(NUMERIC_SYMBOLS)}


class NativePort:
    def __init__(self, tape):
        self.tape = tape

    @property
    def cells(self):
        return self.tape.cells

    @property
    def head(self):
        return self.tape.head

    def read(self):
        return NUMERIC_SYMBOLS[self.tape.read()]

    def write(self, symbol):
        self.tape.write(NUMERIC_VALUES[symbol])

    def step(self, direction):
        self.tape.step(direction)


class BitPort:
    def __init__(self, tape):
        self.tape = tape

    @property
    def cells(self):
        return self.tape.cells

    @property
    def head(self):
        return self.tape.head

    def read(self):
        return ('0', '1')[self.tape.read()]

    def write(self, symbol):
        self.tape.write({'0': 0, '1': 1}[symbol])

    def step(self, direction):
        self.tape.move(direction)


class Program:
    def __init__(self, code, labels, metadata):
        self.code, self.labels, self.metadata = code, labels, metadata
        for name in ('calls', 'instructions', 'core_instructions', 'symbol_actions',
                     'passes', 'routes', 'point_instructions', 'route_instructions',
                     'key_instructions', 'header_instructions', 'retire_instructions',
                     'payload_bit_actions', 'native_actions'):
            setattr(self, name, 0)
        self.writes, self.history = [0]*metadata['tapes'], [None]*metadata['tapes']
        self.last = None
        self.route_entries, self.route_returns, self.point_entries = {}, {}, {}
        self.route_at, self.point_at, self.core_at = ([False]*len(code) for _ in range(3))
        start = metadata['key_start']
        key = metadata['key_metadata']
        route = key['route_metadata']
        point_labels = route['point_labels']
        for direction, block in key['route_copies'].items():
            at = start+block['start']
            self.route_entries[at+route['entries'][direction]] = direction
            self.route_returns[start+block['return']] = direction
            for pc in range(at, at+block['length']):
                self.route_at[pc] = True
            for phase, point in route['point_copies'].items():
                first = at+point['start']
                self.point_entries[first] = phase
                for pc in range(first, first+point['length']):
                    self.point_at[pc] = True
                for pc in range(first+point_labels['CORE_ENTRY'], first+point_labels['CORE_DONE']):
                    self.core_at[pc] = True

    def run(self, tapes, direction='BUILD', limit=100000000):
        if len(tapes) != self.metadata['tapes'] or len({id(t.cells) for t in tapes}) != len(tapes):
            raise ValueError('fixed distinct physical owners')
        if direction not in self.metadata['entries']:
            raise ValueError('one fixed entry port')
        pc = self.metadata['entries'][direction]
        steps = key_steps = route_steps = point_steps = core_steps = 0
        marker_actions = native_actions = payload_actions = points = routes = 0
        visits, writes, actions = [], [0]*len(tapes), [0]*len(tapes)
        history = [[t.head, t.head] for t in tapes]
        outer_counts = {}
        while True:
            if pc in self.route_entries:
                routes += 1
                visits.append({'direction': self.route_entries[pc], 'index': ''.join(tapes[20].cells),
                               'address': ''.join(tapes[18].cells), 'payload_head': tapes[21].head})
            if pc in self.route_returns:
                visits[-1]['destination'] = ''.join(tapes[18].cells)
            points += pc in self.point_entries
            op, *args = self.code[pc]
            steps += 1
            in_key = pc >= self.metadata['key_start']
            key_steps += in_key
            route_steps += self.route_at[pc]
            point_steps += self.point_at[pc]
            core_steps += self.core_at[pc]
            if not in_key:
                outer_counts[pc] = outer_counts.get(pc, 0)+1
            if steps > limit:
                raise ValueError('literal verifier watchdog')
            if op in ('R', 'W', 'M'):
                role = args[0]
                marker_actions += role < 21
                payload_actions += role == 21
                native_actions += role >= 22
                actions[role] += 1
                history[role][0] = min(history[role][0], tapes[role].head)
                history[role][1] = max(history[role][1], tapes[role].head)
            if op == 'R':
                symbol = tapes[args[0]].read()
                if symbol not in args[1]:
                    raise ValueError('outside fixed symbol alphabet')
                pc = args[1][symbol]
            elif op == 'W':
                tapes[args[0]].write(args[1])
                writes[args[0]] += 1
                pc += 1
            elif op == 'M':
                tapes[args[0]].step(args[1])
                history[role][0] = min(history[role][0], tapes[role].head)
                history[role][1] = max(history[role][1], tapes[role].head)
                pc += 1
            elif op == 'J':
                pc = args[0]
            elif op == 'H':
                result = {'status': args[0], 'instructions': steps, 'key_instructions': key_steps,
                          'route_instructions': route_steps, 'point_instructions': point_steps,
                          'core_instructions': core_steps, 'routes': routes, 'point_calls': points,
                          'symbol_actions': marker_actions, 'payload_bit_actions': payload_actions,
                          'native_actions': native_actions, 'writes': writes, 'actions_by_port': actions,
                          'visits': visits, 'history': history, 'outer_counts': outer_counts,
                          'header_instructions': 0 if direction == 'RETIRE' else steps-key_steps,
                          'retire_instructions': steps if direction == 'RETIRE' else 0}
                self._record(result)
                return result
            else:
                raise ValueError('unknown literal instruction')

    def _record(self, result):
        self.last = result
        self.passes += int(result['key_instructions'] > 0)
        self.calls += result['point_calls']
        for name in ('instructions', 'key_instructions', 'route_instructions', 'point_instructions',
                     'core_instructions', 'routes', 'symbol_actions', 'payload_bit_actions',
                     'native_actions', 'header_instructions', 'retire_instructions'):
            setattr(self, name, getattr(self, name)+result[name])
        self.writes = [a+b for a, b in zip(self.writes, result['writes'])]
        for role, interval in enumerate(result['history']):
            old = self.history[role]
            self.history[role] = interval[:] if old is None else [min(old[0], interval[0]), max(old[1], interval[1])]
