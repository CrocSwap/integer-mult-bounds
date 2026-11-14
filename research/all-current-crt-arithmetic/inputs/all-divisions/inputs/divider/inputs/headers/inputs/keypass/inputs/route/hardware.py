"""Fixed-table execution on retained physical Tapes; observations never choose work.

Apache-2.0. Prepared for @CubeJerry with substantial OpenAI assistance.
"""


class Program:
    def __init__(self, code, labels, metadata):
        self.code, self.labels, self.metadata = code, labels, metadata
        self.calls = self.instructions = self.core_instructions = self.symbol_actions = 0
        self.routes = self.point_calls = self.point_instructions = 0
        self.last = None
        self.writes = [0]*metadata['tapes']

    def run(self, tapes, direction='FORWARD', limit=20000000):
        if len(tapes) != self.metadata['tapes'] or len({id(t.cells) for t in tapes}) != len(tapes):
            raise ValueError('fixed distinct physical owners')
        if direction not in self.metadata['entries']:
            raise ValueError('one fixed direction entry port')
        pc = self.metadata['entries'][direction]
        points = self.metadata['point_copies']
        entries = {value['start']: key for key, value in points.items()}
        first_point = min(entries)
        inner = self.metadata['point_labels']
        core_ranges = [(value['start']+inner['CORE_ENTRY'], value['start']+inner['CORE_DONE'])
                       for value in points.values()]
        core_at = tuple(any(start <= index < end for start, end in core_ranges)
                        for index in range(len(self.code)))
        steps = core_steps = symbol_actions = point_steps = point_calls = 0
        writes = [0]*len(tapes)
        visits = []
        while True:
            if pc in entries:
                point_calls += 1
                # Diagnostic snapshots only: neither these values nor their length
                # is an operand, a branch source, or a run-time graph callback.
                visits.append({'mode': entries[pc], 'row': ''.join(tapes[17].cells),
                               'address': ''.join(tapes[18].cells), 'target_head': tapes[19].head,
                               'private_heads': [t.head for t in tapes[:14]],
                               'private_extents': [len(t.cells) for t in tapes[:14]]})
            instruction = self.code[pc]
            op, *args = instruction
            steps += 1
            point_steps += pc >= first_point
            core_steps += core_at[pc]
            if steps > limit:
                raise ValueError('literal verifier watchdog')
            if op in ('R', 'W', 'M'):
                symbol_actions += 1
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
                self.calls += point_calls
                self.routes += 1
                self.instructions += steps
                self.core_instructions += core_steps
                self.symbol_actions += symbol_actions
                self.point_calls += point_calls
                self.point_instructions += point_steps
                self.writes = [a+b for a, b in zip(self.writes, writes)]
                self.last = {'status': args[0], 'instructions': steps,
                             'point_instructions': point_steps, 'core_instructions': core_steps,
                             'controller_instructions': steps-point_steps,
                             'point_calls': point_calls, 'symbol_actions': symbol_actions,
                             'writes': writes, 'visits': visits}
                return self.last
            else:
                raise ValueError('unknown literal instruction')
