#!/usr/bin/env python3
"""Small independent hardware meters and exact frozen-source accounting.

Not a whole-word execution or a conversion to tariff units.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import argparse
from collections import Counter
from fractions import Fraction
import json
from types import SimpleNamespace
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from source_binding import authenticate, vendor, need
from audit import inspect_sources, lower_vector, PHASES


class Tape:
    """Independent instrumented hardware, never exposed as an arithmetic API."""
    def __init__(self, body=()):
        self.cells = {-1: 2} | dict(enumerate(body))
        self.head = 0
        self.count = Counter()

    def read(self):
        self.count['reads'] += 1
        return self.cells.get(self.head, 6)

    def write(self, value):
        need(self.head >= 0, 'protected LEFT marker')
        self.count['writes'] += 1
        self.cells[self.head] = value

    def move(self, direction):
        need(direction in (-1, 1), 'literal unit movement')
        self.count['moves'] += 1
        self.head += direction
        need(self.head >= -1, 'local hardware confinement')


class Rows:
    def __init__(self, table):
        self.table, self.count = table, 0

    def __getitem__(self, index):
        self.count += 1
        return self.table[index]


def encode_zero(widths):
    out = []
    for width in widths:
        need(width >= 1, 'positive width')
        out.extend([0] * (3 * width))
        out.extend((0, 1, 0))  # numeric delimiter 2
    return out


def counts(tapes, rows=0):
    return tuple(sum(t.count[key] for t in tapes) for key in ('reads','writes','moves')) + (rows,)


def primitive_units(machine):
    result = {}
    for name in ('read', 'write', 'move_right', 'move_left'):
        tape = Tape([0] * 6); port = machine.CodedPort(tape)
        if name == 'read': need(port.read() == 0, 'coded zero read')
        elif name == 'write': port.write(0)
        elif name == 'move_right': port.move(1)
        else: tape.head = 3; port.move(-1)
        result[name] = counts([tape])[:3]
    need(result == {'read': (4,0,6), 'write': (0,3,6),
                    'move_right': (1,0,3), 'move_left': (1,0,3)},
         'exact unchanged coded-port vector')
    return result


def literal_checks():
    machine = vendor('tariff_machine', 'kernel/machine.py')
    tables = vendor('tariff_compact_tables', 'kernel/compact_tables.py')
    units = primitive_units(machine)
    coefficients = ('1', '-1', '3/8', '-2/3', '-7/10', '1/125',
                    '-14729531/163840', '-1379/250', '1085645/393216')
    cases = []
    for q in coefficients:
        table, metadata = tables.compile_compact(q)
        for widths in ((1,1), (2,4), (17,1,3,11), (65,65)):
            body = encode_zero(widths)
            # Independent dirty contiguous bank with a displaced starting head.
            tapes = [Tape(body), Tape(body), Tape([1,0,1,1,0,1,0]), Tape([0,1,0,1])]
            tapes[2].head = 5; tapes[3].head = 2
            row_meter = Rows(table)
            host = SimpleNamespace(payloads=tapes, primitive_work=(2,3),
                                   primitive_context=(), services={'service':row_meter})
            machine.Controller.primitive(host, 'service', (0,1))
            need(all([tapes[i].cells.get(j,6) for j in range(len(body))] == body for i in (0,1)),
                 'exact zero output and complete source preservation')
            need(all(t.head == 0 for t in tapes), 'success origin restoration')
            need(all(all(v == 6 for k,v in t.cells.items() if k >= 0) for t in tapes[2:]),
                 'retirement of dirty and current private bodies')
            observed = counts(tapes, row_meter.count)
            bound = tuple(v * sum(widths) for v in lower_vector(q))
            need(all(x >= y for x,y in zip(observed,bound)), 'universal mandatory-vector lower bound')
            cases.append(dict(coefficient=q, widths=list(widths),
                              observed=list(observed), lower=list(bound), rows_in_table=len(table)))
        # With the same two components and same initial dirty bodies, the
        # width increment isolates the mandatory ordinary-bit coefficient.
        small, wide = cases[-4], cases[-1]
        need([wide['observed'][j]-small['observed'][j] for j in range(4)] ==
             [wide['lower'][j]-small['lower'][j] for j in range(4)],
             'independent width-increment coefficient check')
    return dict(cases=len(cases), primitive_units=units, observations=cases,
                exact_width_increment_controls=len(coefficients),
                scope='Small literal hardware checks supporting the symbolic all-width pass proof; no whole word replay.')


def controls(source, literal):
    # Controls target real accounting failure modes, not arithmetic mutants
    # of a predecessor already tested separately.
    detected = []
    def mismatch(name, actual, erroneous):
        need(actual != erroneous, 'negative control not discriminating: '+name)
        detected.append(name)
    mismatch('COPY_must_not_be_included_in_ADD_count', source['native_ADD_count'],
             source['native_ADD_count'] + 1)
    mismatch('one_native_call_is_not_the_complete_18_call_invoice', source['raw_action_lower'],
             source['raw_action_lower'] // 18)
    mismatch('remainder_and_reversal_cost_is_not_zero', source['raw_action_lower'],
             source['raw_action_lower'] - 18 * 28 * source['odd_ADD_count'])
    mismatch('coded_read_is_not_three_raw_reads', sum(literal['primitive_units']['read']), 3)
    # Exact rate comparison: at rho=1 the FIXED replacement ledger fails;
    # rho=3 is not disproved by this lower bound, but is not an upper certificate.
    bound = source['raw_action_lower']; room = source['replacement_headroom']
    need(bound > room and Fraction(bound,3) < room, 'conditional exchange-rate discriminators')
    detected.append('upper_cap_inference_from_lower_bound_rejected')
    # Algebraic countermodel to a stronger inference, not a claimed algorithm:
    # positive actual costs can obey every displayed lower/upper inequality
    # while fitting the cap and failing the retained replacement ledger.
    hypothetical_other, hypothetical_add = 100000000, 500000000
    need(hypothetical_other <= source['retained_other_invoice']
         and hypothetical_add >= bound
         and hypothetical_other + hypothetical_add < 10**9
         and source['retained_other_invoice'] + hypothetical_add > 10**9,
         'model upper charges cannot be used as actual lower bounds')
    detected.append('positive_abstract_countermodel_to_full_runtime_obstruction')
    need(sum(PHASES['quotient_stage'][:3]) == 55 and sum(PHASES['quotient_stage']) == 64,
         'four moves in quotient staging, not three')
    detected.append('quotient_fourth_move_counted')
    return dict(detected=detected,
        purely_algebraic_countermodel=dict(other_actual=100000000, add_actual=500000000,
            scope='Consistency witness for cost inequalities only; no physical algorithm is asserted.'),
        invalid_inferences=['An O(V) source lemma specifies rho=1.',
                            'A lower estimate under rho=3 proves an upper admission.',
                            'A failure of the retained replacement ledger proves all implementations exceed the cap.',
                            'Three installed compact source tokens constitute a full caller registry.'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suite', choices=('source','literal','all'), default='all')
    parser.add_argument('--write-receipts', action='store_true')
    args = parser.parse_args(); authenticate()
    source = inspect_sources()
    if args.suite in ('source','all'):
        if args.write_receipts:
            (ROOT/'SOURCE.json').write_text(json.dumps(source,sort_keys=True,indent=2)+'\n')
        print('PASS_LITERAL_TARIFF_SOURCE')
    if args.suite in ('literal','all'):
        literal = literal_checks(); negative = controls(source,literal)
        if args.write_receipts:
            (ROOT/'LITERAL.json').write_text(json.dumps(literal,sort_keys=True,indent=2)+'\n')
            (ROOT/'CONTROLS.json').write_text(json.dumps(negative,sort_keys=True,indent=2)+'\n')
        print('PASS_LITERAL_TARIFF_LOWER_VECTOR')
        print('PASS_LITERAL_TARIFF_CONTROLS')


if __name__ == '__main__':
    main()
