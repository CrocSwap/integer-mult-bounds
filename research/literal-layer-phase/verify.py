"""Bounded execution, source pins, address oracle and failure controls."""
from pathlib import Path
import hashlib
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import phase as P
import oracles as O


def need(condition, message):
    if not condition:
        raise ValueError(message)


class AuditTape(P.Tape):
    """Observers enforce current owned windows; no observer enters control."""
    def begin(self, origin, extent, public=False):
        self.origin, self.extent, self.public = origin, extent, public
        self.epoch_low = self.epoch_high = origin
        self.write_count = 0

    def check(self):
        need(self.origin-(not self.public) <= self.head <= self.origin+self.extent,
             'current-window head bound')

    def read(self):
        self.check()
        return super().read()

    def write(self, symbol):
        self.check()
        self.write_count += 1
        super().write(symbol)

    def move(self, direction):
        need(direction in (-1, 1), 'literal unit move')
        super().move(direction)
        self.check()
        self.epoch_low = min(self.epoch_low, self.head)
        self.epoch_high = max(self.epoch_high, self.head)


def extents(parameters):
    p, d, r, dimension, outer, spectator, block, select, width = parameters
    volume = 2*width*O.cardinality(parameters)
    E = len(O.header(parameters))
    result = [E, volume, volume, E, max(v.bit_length()-1 for v in parameters),
              max(parameters), p, d, r, dimension, outer, spectator, block,
              select, width, dimension*block, dimension*block, width, width, volume]
    return result


def run_case(code, parameters, values=None, *, offset=0, tapes=None,
             expected_reject=False, source_edit=None, public_reserve=0):
    width = parameters[-1]
    count = O.cardinality(parameters)
    if values is None:
        values = [(1, -1)]*count
    need(len(values) == count, 'oracle input cardinality')
    predicted = O.expected(parameters, values)
    fitting = O.fits(predicted, width)
    E = len(O.header(parameters))
    volume = 2*count*width
    capacities = extents(parameters)
    if tapes is None:
        tapes = []
        for i in range(20):
            origin = offset+11*i-71
            cells = {origin-4: '0', origin-3: '|', origin-2: '1'}
            tape = AuditTape(cells, origin)
            # Initial history includes opaque prefixes and a paid clean old tail.
            tape.low, tape.high = origin-4, origin+307
            tapes.append(tape)
    identities = tuple(map(id, tapes))
    starts = [t.head for t in tapes]
    old_history = [(t.low, t.high) for t in tapes]
    initial_private = sum(t.high-t.low+1 for t in tapes[2:])
    for i, tape in enumerate(tapes):
        tape.begin(starts[i], capacities[i], public=i<2)
    for i, word in ((P.HEADER, O.header(parameters)), (P.DATA, O.encode(values, width))):
        # Caller source acquisition/re-encoding is outside the measured table.
        tape = tapes[i]
        tape.cells = {k: v for k, v in tape.cells.items() if k < tape.origin or k >= tape.origin+900_000}
        if i == P.DATA and source_edit is not None:
            word = source_edit(word)
        tape.cells.update({tape.origin+j: bit for j, bit in enumerate(word)})
        suffix = len(word) if i == P.HEADER else max(volume, len(word), public_reserve)+1
        tape.cells.update({tape.origin+suffix: '1', tape.origin+suffix+1: '|'})
    before = [dict(t.cells) for t in tapes]
    budget = 65536*(E+parameters[0]+parameters[1]+parameters[3]*parameters[6]+count*width+1)
    machine = P.Machine(code, tapes)
    failed = False
    try:
        machine.run(budget)
    except ValueError as error:
        need(str(error) == 'invalid scanned symbol', 'unexpected failure: '+str(error))
        failed = True
    if expected_reject or not fitting:
        need(failed, 'invalid/range packet accepted')
        need(tapes[P.DATA].cells == before[P.DATA], 'rejection changed public DATA')
        need(tapes[P.DATA].write_count == 0, 'rejection wrote DATA before commit')
        return dict(parameters=parameters, count=count, steps=machine.steps, outcome='reject'), tapes
    need(not failed, 'valid fitting packet rejected')
    need(tuple(map(id, tapes)) == identities, 'changed tape ownership')
    need(all(t.head == head for t, head in zip(tapes, starts)), 'head return')
    output = ''.join(tapes[P.DATA].cells.get(starts[P.DATA]+j, P.BLANK) for j in range(volume))
    need(output == O.encode(predicted, width), 'explicit-address Gaussian result')
    need(tapes[P.HEADER].cells == before[P.HEADER], 'header preservation')
    wanted = dict(before[P.DATA])
    wanted.update({starts[P.DATA]+j: bit for j, bit in enumerate(output)})
    need(tapes[P.DATA].cells == wanted, 'public exterior preservation')
    for i in P.PRIVATE:
        need(tapes[i].cells == before[i], 'private retirement/exterior preservation')
    need(all(t.low <= lo and t.high >= hi for t, (lo, hi) in zip(tapes, old_history)), 'history reset')
    history = sum(t.high-t.low+1 for t in tapes[2:])
    bound = initial_private+4*volume+32*(E+parameters[0]+parameters[1]+parameters[3]*parameters[6]+width+1)
    need(history <= bound, 'historical backing envelope')
    need(machine.steps <= budget, 'instruction envelope')
    need(tapes[P.DATA].write_count == volume, 'whole original-owner install')
    return dict(parameters=parameters, count=count, steps=machine.steps, outcome='success',
                private_history=history, time_bound=budget, history_bound=bound), tapes


def mutant(old, new):
    source = (HERE/'phase.py').read_text()
    need(source.count(old) == 1, 'unique semantic mutation anchor')
    namespace = {'__file__': str(HERE/'phase.py'), '__name__': 'disposable_phase_mutant'}
    exec(compile(source.replace(old, new), '<disposable-phase-mutant>', 'exec'), namespace)
    return namespace['compile_phase']()[0]


def main():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for pin in pins['files']:
        data = (HERE/pin['local']).read_bytes()
        need(len(data) == pin['bytes'], 'source byte count')
        need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == pin['blob'], 'source Git blob')
    code, alphabet = P.compile_phase()
    need(len(code) == 2146, 'fixed graph size')
    for instruction in code:
        op = instruction[0]
        need(op in ('read', 'write', 'move', 'goto', 'halt'), 'literal opcode')
        if op in ('read', 'write', 'move'):
            need(type(instruction[1]) is int and 0 <= instruction[1] < 20, 'fixed tape selector')
        if op == 'move':
            need(instruction[2] in (-1, 1), 'unit displacement')
        if op == 'goto':
            need(type(instruction[1]) is int and 0 <= instruction[1] < len(code), 'fixed target')
        if op == 'read':
            need(all(symbol in alphabet and type(target) is int and 0 <= target < len(code)
                     for symbol, target in instruction[2].items()), 'local finite transition')
    rng = random.Random(0x53757350)
    runs = []
    geometry_count = 0
    for dimension in range(1, 5):
        for block in range(1, 5):
            if dimension*block > 8:
                continue
            for rho in range(block):
                for r, outer, spectator in ((1, 1, 1), (2, 2, 3)):
                    precision = 2+(dimension+block) % 2
                    width = precision+2+(rho % 2)
                    parameters = (precision, dimension+block % 2, r, dimension,
                                  outer, spectator, block, rho+1, width)
                    bound = (1 << (width-1))-1
                    values = [(rng.randint(-bound, bound), rng.randint(-bound, bound))
                              for _ in range(O.cardinality(parameters))]
                    receipt, _ = run_case(code, parameters, values, offset=geometry_count-81)
                    runs.append(receipt)
                    geometry_count += 1
    # Isolate every signed 3-bit Gaussian pair at each possible phase.
    numeric_count = 0
    numeric_parameters = (1, 3, 1, 3, 1, 1, 1, 1, 3)
    target_addresses = (0, 1, 3, 7)
    for mode, address in enumerate(target_addresses):
        for real in range(-4, 4):
            for imag in range(-4, 4):
                values = [(0, 0)]*8
                values[address] = (real, imag)
                receipt, _ = run_case(code, numeric_parameters, values, offset=17-mode)
                runs.append(receipt)
                numeric_count += 1
    for parameters in ((1, 1, 31, 1, 1, 1, 1, 1, 3),
                       (1, 1, 1, 1, 29, 1, 1, 1, 3),
                       (1, 1, 1, 1, 1, 37, 1, 1, 3),
                       (3, 1, 1, 1, 1, 1, 8, 8, 5),
                       (127, 129, 1, 1, 1, 1, 1, 1, 129),
                       (1, 1025, 1, 1, 1, 1, 1, 1, 3)):
        receipt, _ = run_case(code, parameters)
        runs.append(receipt)
    # Source re-encoding is caller work; private owner/history objects persist.
    tapes = None
    reuse = []
    for parameters in ((2, 3, 2, 3, 2, 2, 2, 2, 4),
                       (1, 1, 1, 1, 1, 1, 1, 1, 3),
                       (1, 1025, 1, 1, 1, 1, 1, 1, 3),
                       (2, 2, 3, 2, 1, 2, 3, 2, 5),
                       (1, 1, 1, 1, 1, 1, 1, 1, 3)):
        receipt, tapes = run_case(code, parameters, tapes=tapes, offset=-99)
        runs.append(receipt)
        reuse.append(receipt)
    invalid = []
    for label, parameters, edit in (
            ('D exceeds d', (1, 1, 1, 2, 1, 1, 1, 1, 3), None),
            ('rho exceeds block', (1, 1, 1, 1, 1, 1, 2, 3, 3), None),
            ('insufficient final width', (2, 1, 1, 1, 1, 1, 1, 1, 3), None),
            ('extra payload bit', (1, 1, 1, 1, 1, 1, 1, 1, 3), lambda word: word+'0'),
            ('truncated payload', (1, 1, 1, 1, 1, 1, 1, 1, 3), lambda word: word[:-1])):
        receipt, _ = run_case(code, parameters, expected_reject=True, source_edit=edit)
        invalid.append(dict(label=label, **receipt))
    cases = (
        ('inactive flips change phase',
         'nxt = (mode + (1-2*bit)*active) % 4',
         'nxt = (mode + (1-2*bit)) % 4', (1, 2, 1, 2, 1, 1, 2, 2, 3), None),
        ('carry loses subtraction',
         'nxt = (mode + (1-2*bit)*active) % 4',
         'nxt = (mode + active) % 4', (1, 2, 1, 2, 1, 1, 1, 1, 3), None),
        ('mask producer omits active bit',
         "('mask_active', ONE, 'build_after')",
         "('mask_active', '0', 'build_after')", (1, 1, 1, 1, 1, 1, 2, 2, 3), None),
        ('coefficient repetition bypassed',
         "a.op('goto', 'coefficient'+str(mode))",
         "a.op('goto', 'coefficient_end'+str(mode))", (1, 1, 2, 1, 1, 1, 1, 1, 3), None),
        ('signed minimum wraps silently',
         "{MARK: 'reject' if old_sign and new_sign else k+'done'}",
         "{MARK: k+'done'}", (1, 1, 1, 1, 1, 1, 1, 1, 3), [(0, 0), (0, -4)]),
        ('header return omitted',
         'trace_return(a, HEADER, HTRACE)',
         "a.op('goto', 'dimension_check')", (1, 1, 1, 1, 1, 1, 1, 1, 3), None),
        ('original owner return omitted',
         "a.mark('committed')\n    trace_return(a, DATA, DTRACE)",
         "a.mark('committed')", (1, 1, 1, 1, 1, 1, 1, 1, 3), None))
    detected = []
    for label, old, new, parameters, values in cases:
        broken = mutant(old, new)
        try:
            run_case(broken, parameters, values)
        except ValueError:
            detected.append(label)
        else:
            raise ValueError('undetected semantic mutation: '+label)
    # Count XOR changes independently of the producer's carry loops.
    carry_counts = []
    for length in range(1, 17):
        records = 1 << length
        actual = sum((x ^ ((x+1) % records)).bit_count() for x in range(records))
        need(actual == 2*records-2, 'exact complete-domain carry census')
        carry_counts.append(dict(length=length, records=records, bit_changes=actual))
    receipt = dict(status='PASS_LITERAL_LAYER_PHASE', base=pins['base'],
                   program_instructions=len(code), tapes=20, private_roles=18,
                   source_sha256=hashlib.sha256((HERE/'phase.py').read_bytes()).hexdigest(),
                   program_sha256=hashlib.sha256(json.dumps(code, separators=(',', ':'), sort_keys=True).encode()).hexdigest(),
                   source_pins=len(pins['files']), geometry_cases=geometry_count,
                   exhaustive_numeric_cases=numeric_count, runs=len(runs),
                   coefficients=sum(r['count'] for r in runs),
                   numerical_rejections=sum(r['outcome']=='reject' for r in runs),
                   total_transitions=sum(r['steps'] for r in runs),
                   maximum_transitions=max(r['steps'] for r in runs),
                   invalid_controls=invalid, detected_semantic_mutations=detected,
                   reuse_sequence=reuse, carry_census=carry_counts,
                   seed='0x53757350',
                   limits=['Universal correctness rests on the written proof, not finite coverage.',
                           'No recursive C, payload permutation, compiler admission or full multiplier.',
                           'No source acquisition cost or failure recovery is silently supplied.'])
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
