"""Execute the fixed mixed-port graph; observations never select work.

The sole binary port is a compile-time alphabet rename on the original tape.
Apache-2.0. Prepared for @CubeJerry with substantial OpenAI assistance.
"""


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
        self.calls = self.instructions = self.core_instructions = self.symbol_actions = 0
        self.passes = self.routes = self.point_instructions = self.route_instructions = 0
        self.payload_bit_actions = 0
        self.writes = [0]*metadata['tapes']
        self.last = None
        self.route_entries, self.route_returns, self.point_entries = {}, {}, {}
        self.route_at, self.point_at, self.core_at = ([False]*len(code) for _ in range(3))
        self._annotations()

    def _annotations(self):
        inner = self.metadata['route_metadata']
        point_labels = inner['point_labels']
        for mode, block in self.metadata['route_copies'].items():
            start = block['start']
            self.route_entries[start+inner['entries'][mode]] = mode
            self.route_returns[block['return']] = mode
            for pc in range(start, start+block['length']):
                self.route_at[pc] = True
            for phase, point in inner['point_copies'].items():
                at = start+point['start']
                self.point_entries[at] = phase
                for pc in range(at, at+point['length']):
                    self.point_at[pc] = True
                for pc in range(at+point_labels['CORE_ENTRY'], at+point_labels['CORE_DONE']):
                    self.core_at[pc] = True

    def run(self, tapes, direction='FORWARD', limit=100000000):
        if len(tapes) != self.metadata['tapes'] or len({id(t.cells) for t in tapes}) != len(tapes):
            raise ValueError('fixed distinct physical owners')
        if direction not in self.metadata['entries']:
            raise ValueError('one fixed direction entry port')
        pc = self.metadata['entries'][direction]
        steps = route_steps = point_steps = core_steps = marker_actions = payload_actions = 0
        points = routes = 0
        visits, writes = [], [0]*len(tapes)
        while True:
            if pc in self.route_entries:
                routes += 1
                visits.append({'direction': self.route_entries[pc], 'index': ''.join(tapes[20].cells),
                               'address': ''.join(tapes[18].cells), 'payload_head': tapes[21].head,
                               'private_extents': [len(t.cells) for t in tapes[:14]],
                               'heads': [t.head for t in tapes]})
            if pc in self.route_returns:
                visits[-1]['destination'] = ''.join(tapes[18].cells)
            points += pc in self.point_entries
            op, *args = self.code[pc]
            steps += 1
            route_steps += self.route_at[pc]
            point_steps += self.point_at[pc]
            core_steps += self.core_at[pc]
            if steps > limit:
                raise ValueError('literal verifier watchdog')
            if op in ('R', 'W', 'M'):
                marker_actions += args[0] != 21
                payload_actions += args[0] == 21
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
                pc += 1
            elif op == 'J':
                pc = args[0]
            elif op == 'H':
                result = {'status': args[0], 'instructions': steps, 'route_instructions': route_steps,
                          'point_instructions': point_steps, 'core_instructions': core_steps,
                          'pass_controller_instructions': steps-route_steps, 'routes': routes,
                          'point_calls': points, 'symbol_actions': marker_actions,
                          'payload_bit_actions': payload_actions, 'writes': writes, 'visits': visits}
                self._record(result)
                return result
            else:
                raise ValueError('unknown literal instruction')

    def _record(self, result):
        self.last = result
        self.passes += 1
        self.calls += result['point_calls']
        for name in ('instructions', 'route_instructions', 'point_instructions', 'core_instructions',
                     'routes', 'symbol_actions', 'payload_bit_actions'):
            setattr(self, name, getattr(self, name)+result[name])
        self.writes = [a+b for a, b in zip(self.writes, result['writes'])]
