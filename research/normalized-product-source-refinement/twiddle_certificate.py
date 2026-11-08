# SPDX-License-Identifier: Apache-2.0
"""Independent all-input certificates for the source interval primitives."""
import ast
from copy import deepcopy
from itertools import product

from algebra import Poly, ceiling_log, need, power_two, variable
from ast_machine import Context, Object
from source_certificate import (CertificateMachine, Count, Order, Sign, Value,
                                numerical_value)


class IntervalMachine(CertificateMachine):
    def __init__(self, words, arithmetic, twiddles, dag=False):
        super().__init__(words, arithmetic, dag=dag)
        self.division_relation = None
        self.positive_names = {'x_positive', 'y_positive', 'quotient_positive'}
        self.services['divide'] = self.divide
        self.register(twiddles, functions=('quotient', 'interval_sum', 'padded', 'inward'))
        if dag:
            self.services['add'] = lambda a, b: Value(self.value(a)+self.value(b))

    def value(self, object_):
        return object_.value if isinstance(object_, Value) else numerical_value(object_)

    def divide(self, numerator, denominator):
        need(self.division_relation is not None, 'declared exact Euclidean division relation')
        quotient, divisor, remainder = self.division_relation
        need(numerator.value == quotient*divisor+remainder and denominator.value == divisor,
             'source division uses exact declared numerator and denominator')
        return Count(quotient), Count(remainder)

    def control_bool(self, value):
        if isinstance(value, Sign):
            # These particular magnitudes are parameterized by strictly
            # positive variables. Arbitrary butterfly atoms are never admitted.
            import json
            for monomial, _ in value.value.terms:
                for atom in monomial:
                    data = json.loads(atom)
                    need(data[0] == 'integer' and data[1] in self.positive_names,
                         'unproved interval sign atom')
            return value.value.positive_variable_order() < 0
        return super().control_bool(value)


def interval_helpers(words, arithmetic, twiddles):
    machine = IntervalMachine(words, arithmetic, twiddles)
    x, y = variable('x_positive'), variable('y_positive')
    q = variable('quotient_positive')
    quotient_cases = []
    for zero_quotient, exact, upward in product((False, True), repeat=3):
        quotient = Poly.number(0) if zero_quotient else q
        divisor, remainder = (x, Poly.number(0)) if exact else (x+y, x)
        machine.division_relation = quotient, divisor, remainder
        result = machine.function('quotient', (Count(quotient*divisor+remainder), Count(divisor), upward))
        expected = quotient+(1 if upward and not exact else 0)
        need(result.value == expected, 'arbitrary Euclidean quotient floor/ceiling semantics')
        quotient_cases.append(dict(zero_quotient=zero_quotient, exact=exact, upward=upward))

    dag = IntervalMachine(words, arithmetic, twiddles, dag=True)
    lower, upper, lo, hi, padding = (variable(name) for name in ('L', 'U', 'term_lo', 'term_hi', 'padding'))
    sum_receipts = []
    for negative in (False, True):
        result = dag.function('interval_sum', (Value(lower), Value(upper), Count(lo), Count(hi), negative))
        expected = (lower-hi, upper-lo) if negative else (lower+lo, upper+hi)
        need(tuple(x.value for x in result) == expected, 'signed interval accumulation endpoints')
        sum_receipts.append(dict(negative=negative, outputs=[x.value.data() for x in result]))
    result = dag.function('padded', (Value(lower), Value(upper), Count(padding)))
    need(tuple(x.value for x in result) == (lower-padding, upper+padding), 'both interval padding endpoints')

    # Full partition of all ordered integer intervals. x,y are positive;
    # lower/upper signs and zero endpoints are represented explicitly.
    zero = Poly.number(0)
    domains = ((x, x, x, False), (x, x+y, x, False),
               (-x, -x, x, True), (-x-y, -x, x, True),
               (zero, zero, zero, False), (-x, zero, zero, False),
               (zero, y, zero, False), (-x, y, zero, False))
    shift = variable('shift')
    inward_receipts = []
    def numeric_signed(poly):
        sign = poly.positive_variable_order() < 0
        return machine.signed(Count(-poly if sign else poly), sign)
    for index, (left, right, chosen, negative) in enumerate(domains):
        result = dag.function('inward', (numeric_signed(left), numeric_signed(right), Count(shift)))
        expected = zero if chosen == zero else Poly.atom('unsigned_right_shift', chosen, shift)
        if negative:
            expected = -expected
        need(result.value == expected, 'all ordered interval inward branch values')
        inward_receipts.append(dict(domain=index, lower=left.data(), upper=right.data(), output=result.value.data()))
    return dict(euclidean_division_cases=quotient_cases, signed_interval_sums=sum_receipts,
                padding_outputs=[(lower-padding).data(), (upper+padding).data()],
                complete_ordered_interval_domains=inward_receipts)


class Counter:
    def __init__(self, count):
        self.value = count.value

    def source_attribute(self, name):
        if name == 'finished':
            return self.value.integer() == 0
        if name == 'decrement':
            def decrement():
                need(self.value.integer() > 0, 'positive loop variant before decrement')
                self.value = self.value-1
            return decrement
        if name == 'close': return lambda: None
        raise ValueError('unknown exact Counter operation')


class TaylorMachine(IntervalMachine):
    def __init__(self, words, arithmetic, twiddles):
        super().__init__(words, arithmetic, twiddles, dag=True)
        self.services.update(Counter=Counter, range=self.fixed_range,
                             quotient=self.quotient_contract)
        self.expected_spread = None
        self.checked_guards = []

    def fixed_range(self, length):
        need(type(length) is int and 0 <= length <= 4, 'at most four fixed Taylor accumulator roles')
        return tuple(range(length))

    def quotient_contract(self, numerator, denominator, upward=False):
        need(type(upward) is bool, 'finite directed-division orientation')
        return Count(Poly.atom('ceil_ratio' if upward else 'floor_ratio', numerator.value, denominator.value))

    def subtract(self, left, right):
        if self.expected_spread is not None and left.value-right.value == self.expected_spread:
            return Count(self.expected_spread)
        return super().subtract(left, right)

    def compare(self, left, right):
        if self.expected_spread is not None and left.value == self.expected_spread and right.value == Poly.number(16):
            self.checked_guards.append(self.expected_spread.data())
            return Order((-1, 0))
        return super().compare(left, right)


def synthetic(name, arguments, body):
    node = ast.FunctionDef(name=name,
                          args=ast.arguments(posonlyargs=[], args=[ast.arg(arg=x) for x in arguments],
                                             kwonlyargs=[], kw_defaults=[], defaults=[]),
                          body=body, decorator_list=[])
    return ast.fix_missing_locations(node)


def named_return(names):
    return ast.Return(value=ast.Tuple(elts=[ast.Name(id=x, ctx=ast.Load()) for x in names], ctx=ast.Load()))


def taylor_transfer_certificate(words, arithmetic, twiddles):
    """Outline exactly one source loop; prove its finite phases symbolically.

    The outline gate accounts for every successful-path statement. Initial,
    loop-body and final blocks are interpreted from the original AST. Only
    the unbounded repetition is replaced by the written induction invariant.
    """
    function = next(n for n in ast.parse(twiddles).body if isinstance(n, ast.FunctionDef) and n.name == 'taylor_intervals')
    tries = [n for n in function.body if isinstance(n, ast.Try)]
    need(len(tries) == 1 and function.body[-1] is tries[0], 'one whole Taylor try/finally region')
    region = tries[0]
    need(not region.handlers and not region.orelse and len(region.body) == 4,
         'complete Taylor successful path outline')
    outer = region.body[0]
    need(isinstance(outer, ast.With) and len(outer.items) == 1 and len(outer.body) == 2,
         'exact Taylor total/context outline')
    inner = outer.body[1]
    need(isinstance(inner, ast.With) and len(inner.items) == 1 and len(inner.body) == 1,
         'exact Taylor counter/context outline')
    loop = inner.body[0]
    need(isinstance(loop, ast.While) and not loop.orelse,
         'one source Taylor loop without omitted exit code')
    condition = ast.dump(loop.test, include_attributes=False)
    expected_condition = ast.dump(ast.parse('not remaining.finished', mode='eval').body, include_attributes=False)
    need(condition == expected_condition, 'Taylor loop continues exactly while its Counter is nonzero')

    initial = deepcopy(function.body[:-1])
    outer_initial, inner_initial = deepcopy(outer), deepcopy(inner)
    inner_initial.body = [named_return(('lo', 'hi', 'accumulators', 'degree', 'phase', 'total', 'remaining'))]
    outer_initial.body[1] = inner_initial
    initial.append(outer_initial)
    initialize = synthetic('initialize_taylor', ('angle', 'plan'), initial)
    step = synthetic('one_taylor_step',
                     ('angle', 'plan', 'lo', 'hi', 'accumulators', 'degree', 'phase', 'remaining'),
                     [*deepcopy(loop.body), named_return(('lo', 'hi', 'accumulators', 'degree', 'phase', 'remaining'))])
    finalize = synthetic('finish_taylor', ('accumulators', 'plan'), deepcopy(region.body[1:]))
    cleanup = synthetic('cleanup_taylor', ('lo', 'hi', 'degree', 'accumulators'),
                        [*deepcopy(region.finalbody), ast.Return(value=ast.Constant(value=None))])

    machine = TaylorMachine(words, arithmetic, twiddles)
    for node in (initialize, step, finalize, cleanup):
        machine.functions[node.name] = node
        machine.validate(node)
    R, T, angle, degree = (variable(name) for name in ('R', 'T', 'angle', 'degree'))
    unit = power_two(R)
    plan = Object(machine, 'TaylorParameters', R=Count(R), T=Count(T), unit=Count(unit), padding=Count(24*T))
    state = machine.function('initialize_taylor', (Count(angle), plan))
    lo, hi, accumulators, first_degree, phase, total, remaining = state
    need(lo.value == hi.value == unit and all(value.value == Poly.number(0) for value in accumulators)
         and len(accumulators) == 4 and first_degree.value == Poly.number(1) and phase == 0
         and total.value == remaining.value == 2*T,
         'actual Taylor initialization, total term count and first degree')
    lower, upper = variable('term_lower'), variable('term_upper')
    accumulator_names = [variable(name) for name in ('cos_lower', 'cos_upper', 'sin_lower', 'sin_upper')]
    expected_lo = Poly.atom('floor_ratio', lower*angle, degree*unit)
    expected_hi = Poly.atom('ceil_ratio', upper*angle, degree*unit)
    machine.expected_spread = expected_hi-expected_lo
    transfers = []
    for phase, last in product(range(4), (False, True)):
        machine.checked_guards = []
        result = machine.function('one_taylor_step', (
            Count(angle), plan, Count(lower), Count(upper), [Value(x) for x in accumulator_names],
            Count(degree), phase, Counter(Count(1 if last else 2))))
        got_lo, got_hi, got_accumulators, got_degree, got_phase, got_remaining = result
        expected_accumulators = list(accumulator_names)
        offset = 0 if phase % 2 == 0 else 2
        if phase < 2:
            expected_accumulators[offset] += lower
            expected_accumulators[offset+1] += upper
        else:
            expected_accumulators[offset] -= upper
            expected_accumulators[offset+1] -= lower
        need([x.value for x in got_accumulators] == expected_accumulators,
             'all-input Taylor signed accumulator phase')
        need(got_lo.value == (lower if last else expected_lo)
             and got_hi.value == (upper if last else expected_hi)
             and got_degree.value == (degree if last else degree+1)
             and got_phase == (phase+1) % 4 and got_remaining.value.integer() == (0 if last else 1),
             'all-input Taylor directed term step and loop variant')
        need(len(machine.checked_guards) == (0 if last else 1), 'every interior Taylor width guard certified')
        transfers.append(dict(phase=phase, last=last, lower=got_lo.value.data(), upper=got_hi.value.data(),
                              accumulators=[x.value.data() for x in got_accumulators], degree=got_degree.value.data(),
                              next_phase=got_phase, guard=machine.checked_guards))
    final = machine.function('finish_taylor', ([Value(x) for x in accumulator_names], plan))
    expected_final = [value+(-24*T if index % 2 == 0 else 24*T) for index, value in enumerate(accumulator_names)]
    need([x.value for x in final] == expected_final, 'actual final cosine/sine interval ordering and padding')
    need(machine.function('cleanup_taylor', (Count(lower), Count(upper), Count(degree),
                                            [Value(x) for x in accumulator_names])) is None,
         'Taylor cleanup cannot override the numerical return')
    return dict(initial_unit=unit.data(), initial_degree=1, terms=(2*T).data(),
                complete_phase_transfers=transfers, final_endpoints=[x.value.data() for x in final],
                conditional_guard='0 <= ceil(hi*angle/(2^R*degree))-floor(lo*angle/(2^R*degree)) <= 16',
                guard_proof='Written invariant with 0<=angle/2^R<4 and the reachable term-width recurrence')


def twiddle_plan_certificate(words, arithmetic, twiddles):
    """Check the actual straight-line fields used by the proved interval loop.

    The source's dyadic admission loop and optional Machin interval/guards are
    separate written obligations; their blocks are retained intact in the
    source binding, not silently represented as constant-cost arithmetic.
    """
    tree = ast.parse(twiddles)
    class_ = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'TwiddlePlan')
    compile_ = next(n for n in class_.body if isinstance(n, ast.FunctionDef) and n.name == 'compile')
    need(isinstance(compile_.body[0], ast.With) and isinstance(compile_.body[-1], ast.With),
         'twiddle admission/optional-Machin blocks remain explicit')
    machine = TaylorMachine(words, arithmetic, twiddles)
    machine.register(twiddles, classes={'TwiddlePlan': ('__init__', 'keep')})
    fields = synthetic('compile_twiddle_fields', ('self',), deepcopy(compile_.body[1:-1]))
    machine.functions[fields.name] = fields
    machine.validate(fields)
    Q, half = variable('Q'), variable('stage_half')
    machine.positive_names.add('Q')
    # The theorem admits Q>=16, so Q+64>1 and this exact ceiling logarithm
    # is strictly positive. No arbitrary logarithm atom gets a sign oracle.
    machine.positive_atoms.add(ceiling_log(Q+64).terms[0][0][0])
    object_ = Object(machine, 'TwiddlePlan')
    machine.method(object_, '__init__', (Count(Q), Count(2*half)))
    machine.function(fields.name, (object_,))
    T, J = Q+64, Q+8
    R = Q+ceiling_log(T)+12
    expected = dict(half=half, T=T, J=J, width=Q+2, R=R, shift=R-Q,
                    unit=power_two(R), grid=power_two(Q), padding=24*T)
    observed = {name: value.value for name, value in object_.fields['fields'].items()}
    need(observed == expected, 'all actual twiddle precision, term-count and padding fields')
    return dict(fields={name: value.data() for name, value in sorted(observed.items())},
                written_blocks=['TwiddlePlan.compile dyadic admission',
                                'TwiddlePlan.compile optional Machin construction and (3,4) guard'])


def twiddle_direction_certificate(words, arithmetic, twiddles):
    tree = ast.parse(twiddles)
    class_ = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Twiddles')
    run = next(n for n in class_.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    need(len(run.body) == 8 and isinstance(run.body[6], ast.Try), 'complete successful twiddle owner outline')
    entry = ast.parse('''need(type(opposite) is bool, "finite twiddle direction")
need(self.closed and not self.pool.live and self.output.read() == BLANK, "consume prior twiddle output")
for item in (*self.pool.tapes, self.output):
    initialize_marker(item)
self.closed = False
plan = None
succeeded = False
''').body
    need([ast.dump(node, include_attributes=False) for node in run.body[:6]] ==
         [ast.dump(node, include_attributes=False) for node in entry],
         'actual twiddle entry preserves the supplied Fourier direction and initializes only declared owners')
    outer = run.body[6]
    need(len(outer.body) == 1 and not outer.handlers and not outer.orelse
         and isinstance(outer.body[0], ast.With), 'one live successful twiddle scope')
    scope = outer.body[0]
    need([ast.unparse(item) for item in scope.items] == ['sealed_constructors()', 'self.scope.installed()']
         and len(scope.body) == 1 and isinstance(scope.body[0], ast.Try),
         'twiddle arithmetic is directly inside the installed source scope')
    region = scope.body[0]
    need(len(region.body) == 4 and not region.handlers and not region.orelse,
         'complete plan, compilation, emission and success sequence')
    loop = region.body[2]
    need(isinstance(loop, ast.For) and not loop.orelse and ast.unparse(loop.target) == 'index'
         and ast.unparse(loop.iter) == 'indices(plan.half)', 'one complete live half-length twiddle table')
    need(len(loop.body) == 2 and ast.unparse(loop.body[0]) == 'real, imaginary = plan.value(index)'
         and isinstance(loop.body[1], ast.Try), 'every actual twiddle index emits one complete returned value')
    emitted = loop.body[1]
    need(len(emitted.body) == 4 and not emitted.handlers and not emitted.orelse,
         'complete twiddle direction, disk guard and component emission')
    need([ast.unparse(node) for node in emitted.body[2:]] ==
         ['write_signed(real, self.output, plan.width)', 'write_signed(imaginary, self.output, plan.width)']
         and [ast.unparse(node) for node in emitted.finalbody] == ['real.close()', 'imaginary.close()'],
         'both components emit in actual real/imaginary order before value retirement')
    disk = emitted.body[1]
    need(isinstance(disk, ast.With) and len(disk.items) == 1
         and ast.unparse(disk.items[0]) ==
         'owned(Count.product(real.magnitude, real.magnitude), Count.product(imaginary.magnitude, imaginary.magnitude), power_two(precision)) as (norm, other, bound)'
         and len(disk.body) == 2 and ast.unparse(disk.body[0]) == 'norm.add(other)',
         'actual disk guard computes the sum of squared component magnitudes')
    squared = disk.body[1]
    need(isinstance(squared, ast.With) and len(squared.items) == len(squared.body) == 1
         and ast.unparse(squared.items[0]) == 'owned(Count.product(bound, bound)) as (squared,)'
         and isinstance(squared.body[0], ast.Expr)
         and isinstance(squared.body[0].value, ast.Call)
         and ast.unparse(squared.body[0].value.func) == 'need'
         and ast.unparse(squared.body[0].value.args[0]) == 'compare(norm, squared) <= 0',
         'actual disk guard is exactly the squared Q-grid unit bound')
    need([ast.unparse(node) for node in region.body[:2]] ==
         ['plan = TwiddlePlan(precision, length)', 'plan.compile()']
         and ast.unparse(region.body[3]) == 'succeeded = True',
         'one actual plan precedes every twiddle and success follows the complete table')
    need([ast.unparse(node) for node in region.finalbody] ==
         ['if plan is not None:\n    plan.close()', 'precision.rewind()', 'length.rewind()', 'self.pool.empty()'],
         'twiddle arithmetic cleanup preserves the emitted packet')
    need(ast.unparse(run.body[-1]) == 'return self.output' and isinstance(run.body[-2], ast.Try)
         and [ast.unparse(node) for node in run.body[-2].finalbody] ==
         ['for item in self.pool.tapes:\n    erase_marker(item)', 'self.output.rewind()',
          'if not succeeded:\n    self.output.clear()\n    erase_marker(self.output)', 'self.closed = True'],
         'successful twiddle producer returns its complete preserved output packet')
    branch = emitted.body[0]
    need(isinstance(branch, ast.If) and ast.unparse(branch.test) == 'not opposite' and not branch.orelse,
         'one live actual Fourier direction conjugation')
    function = synthetic('source_twiddle_direction', ('imaginary', 'opposite'), [deepcopy(branch)])
    machine = IntervalMachine(words, arithmetic, twiddles)
    machine.functions[function.name] = function
    machine.validate(function)
    receipts = []
    for zero, negative, opposite in product((False, True), repeat=3):
        magnitude = Poly.number(0) if zero else variable('x_positive')
        value = machine.signed(Count(magnitude), negative)
        before = numerical_value(value)
        machine.function(function.name, (value, opposite))
        need(numerical_value(value) == (before if opposite else -before), 'all signed and zero twiddle conjugation cases')
        receipts.append(dict(zero=zero, negative=negative, opposite=opposite))
    return dict(table_length='L/2', component_order=['real', 'imaginary'], complete_sign_cases=receipts,
                result='opposite=False emits exp(-2*pi*i*k/L); opposite=True emits its conjugate')


class TwiddleValueMachine(TaylorMachine):
    """Compose the already checked interval contracts at the real call site."""
    def __init__(self, words, arithmetic, twiddles):
        super().__init__(words, arithmetic, twiddles)
        self.services.update(taylor_intervals=self.taylor_contract, inward=self.inward_contract)
        self.register(twiddles, classes={'TwiddlePlan': ('value',)})
        self.positive_names.update(('index_positive', 'half_positive'))
        self.generic = False
        self.endpoint_spreads = set()
        self.interval_guards = []
        self.events = []
        self.plan = None

    def taylor_contract(self, angle, plan):
        need(plan is self.plan, 'Taylor source call uses the same compiled plan')
        self.events.append(['Taylor', angle.value.data()])
        endpoints = tuple(Poly.atom('Taylor_endpoint', angle.value, index) for index in range(4))
        self.endpoint_spreads = {endpoints[1]-endpoints[0], endpoints[3]-endpoints[2]}
        return tuple(Value(value) for value in endpoints)

    def inward_contract(self, lower, upper, shift):
        need(upper.value-lower.value in self.endpoint_spreads,
             'inward source call uses a complete ordered Taylor endpoint pair')
        self.events.append(['inward', lower.value.data(), upper.value.data(), shift.value.data()])
        return Value(Poly.atom('inward_interval', lower.value, upper.value, shift.value))

    def control_bool(self, value):
        if isinstance(value, Sign) and value.value in self.endpoint_spreads:
            # This exact nonnegative spread follows from the Taylor/interval
            # theorem, not from a generic sign oracle for symbolic objects.
            return False
        return super().control_bool(value)

    def compare(self, left, right):
        if self.generic and (left.value, right.value) == (2*variable('index_positive'), variable('half_positive')):
            return Order((-1, 1))  # Complete non-quarter-turn branch.
        if left.value in self.endpoint_spreads and right.value == 64*variable('T'):
            self.interval_guards.append(left.value.data())
            return Order((-1, 0))  # The written reachable 64T interval bound.
        return super().compare(left, right)


def twiddle_value_certificate(words, arithmetic, twiddles):
    machine = TwiddleValueMachine(words, arithmetic, twiddles)
    Q, R, T = (variable(name) for name in ('Q', 'R', 'T'))
    k, H, pi_lo = (variable(name) for name in ('index_positive', 'half_positive', 'pi_lower'))
    B = power_two(Q)
    cases = []
    for kind in ('zero', 'quarter', 'generic'):
        index = Poly.number(0) if kind == 'zero' else k
        half = 2*k if kind == 'quarter' else H
        machine.plan = Object(machine, 'TwiddlePlan', grid=Count(B), half=Count(half),
                              T=Count(T), shift=Count(R-Q), pi_lower=Value(pi_lo))
        machine.generic = kind == 'generic'
        machine.events, machine.interval_guards, machine.endpoint_spreads = [], [], set()
        result = machine.method(machine.plan, 'value', (Count(index),))
        if kind != 'generic':
            expected = (B, Poly.number(0)) if kind == 'zero' else (Poly.number(0), B)
            need(tuple(value.value for value in result) == expected
                 and not machine.events and not machine.interval_guards,
                 'actual exact zero/quarter twiddle branches bypass generic setup')
        else:
            angle = Poly.atom('floor_ratio', pi_lo*k, H)
            endpoints = tuple(Poly.atom('Taylor_endpoint', angle, j) for j in range(4))
            expected = tuple(Poly.atom('inward_interval', endpoints[j], endpoints[j+1], R-Q) for j in (0, 2))
            expected_events = [['Taylor', angle.data()],
                               *[['inward', endpoints[j].data(), endpoints[j+1].data(), (R-Q).data()]
                                 for j in (0, 2)]]
            need(tuple(value.value for value in result) == expected and machine.events == expected_events
                 and len(machine.interval_guards) == 2,
                 'actual lower-pi angle, cosine/sine endpoint order, guards and inward shift')
        cases.append(dict(branch=kind, outputs=[value.value.data() for value in result],
                          events=machine.events, interval_guards=machine.interval_guards))
    return dict(complete_index_branches=cases,
                inherited_contracts=['Directed quotient', 'All Taylor phase transfers plus written enclosure',
                                     'All ordered inward interval branches'],
                written_premises=['Generic index 0<k<L/2 and 2k!=L/2',
                                  'Initialized pi_lower for L>4',
                                  'Both Taylor interval spreads lie in [0,64T]'])
