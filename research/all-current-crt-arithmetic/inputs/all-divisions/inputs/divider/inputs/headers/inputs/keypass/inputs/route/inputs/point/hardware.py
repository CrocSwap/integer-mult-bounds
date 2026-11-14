"""A literal fixed-table interpreter over the existing caller's physical Tapes.

Observers count instructions; no observation feeds a program operand.
Apache-2.0; substantial OpenAI assistance.
"""


class Program:
    def __init__(self, code, labels):
        self.code, self.labels = code, labels
        self.tape_count = 1+max(instruction[1] for instruction in code
                               if instruction[0] in ('R', 'W', 'M'))
        self.calls = self.instructions = self.core_instructions = self.symbol_actions = 0
        self.writes = [0]*self.tape_count
        self.last = None

    def run(self, tapes, limit=10000000):
        if len(tapes) != self.tape_count or len({id(t.cells) for t in tapes}) != self.tape_count:
            raise ValueError('distinct physical tape owners are required for the fixed graph')
        pc, steps, core_steps, symbol_actions = 0, 0, 0, 0
        writes = [0]*self.tape_count
        while True:
            instruction = self.code[pc]
            op, *args = instruction
            steps += 1
            if self.labels['CORE_ENTRY'] <= pc < self.labels['CORE_DONE']:
                core_steps += 1
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
                self.calls += 1
                self.instructions += steps
                self.core_instructions += core_steps
                self.symbol_actions += symbol_actions
                self.writes = [x+y for x, y in zip(self.writes, writes)]
                self.last = {'status': args[0], 'instructions': steps,
                             'core_instructions': core_steps, 'symbol_actions': symbol_actions,
                             'writes': writes}
                return self.last
            else:
                raise ValueError('unknown literal instruction')
