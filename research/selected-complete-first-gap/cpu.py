"""Read-only literal replay CPU: unchanged C4 run method, fixed inventory45.

The frozen optimized instruction compiler is inherited. Payload computation
is exclusively local graph transitions; packet oracles are outside this CPU.
Apache-2.0; source and assistance credit in NOTICE.md.
"""

def program_class(C):
    need, Rejected, TAPES = C.need, C.Rejected, 45
    class Program(C.Program):
        def run(self, state, *, start=None, stop=None, budget=150_000_000):
            need(len(state.tapes) == TAPES and len({id(t) for t in state.tapes}) == TAPES,
                 'all physical tape owners must be distinct')
            pc = self.start if start is None else self.labels[start]
            stop_pc = None if stop is None else self.labels[stop]
            rows, tapes, heads = self.rows, state.tapes, state.heads
            lows, highs, writes = state.lows, state.highs, state.writes
            limit = state.steps+budget
            while pc != -1 and pc != stop_pc:
                op, tape, arg = rows[pc]
                if op == 0:
                    pc = arg[tapes[tape][heads[tape]]]
                    if pc == -2:
                        raise Rejected('literal scanned-symbol rejection')
                elif op == 1:
                    value, pc = arg
                    need(heads[tape] != state.origins[tape] or value == 2,
                         'permanent origin overwrite')
                    tapes[tape][heads[tape]] = value
                    writes[tape] += 1
                elif op == 2:
                    delta, pc = arg
                    need(delta in (-1, 1), 'nonunit emitted move')
                    heads[tape] += delta
                    need(0 <= heads[tape] < len(tapes[tape]), 'finite verifier capacity')
                    lows[tape] = min(lows[tape], heads[tape])
                    highs[tape] = max(highs[tape], heads[tape])
                elif op == 3:
                    pc = tape
                else:
                    found = None
                    for rule in tape:
                        if all(tapes[t][heads[t]] == symbol for t, symbol in rule[0]):
                            need(found is None, 'nondeterministic literal rules')
                            found = rule
                    if found is None:
                        raise Rejected('literal scanned-symbol rejection')
                    for t, value in found[1]:
                        need(heads[t] != state.origins[t] or value == 2,
                             'permanent origin overwrite')
                        tapes[t][heads[t]] = value
                        writes[t] += 1
                    for t, delta in found[2]:
                        need(delta in (-1, 1), 'nonunit emitted move')
                        heads[t] += delta
                        need(0 <= heads[t] < len(tapes[t]), 'finite verifier capacity')
                        lows[t] = min(lows[t], heads[t])
                        highs[t] = max(highs[t], heads[t])
                    pc = found[3]
                state.steps += 1
                need(state.steps <= limit, 'finite execution budget')
            return state

    return Program
