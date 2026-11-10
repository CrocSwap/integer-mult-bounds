# SPDX-License-Identifier: Apache-2.0
"""Source-bound numerical stream order and unbounded-loop proof outlines.

The local bodies are interpreted symbolically. The unbounded repetitions are
certified by explicit source-derived recurrence descriptors and written
induction, not by materializing an FFT at a sampled length.
"""
import ast
from copy import deepcopy
from dataclasses import dataclass, field

from algebra import Poly, need, power_two, variable
from ast_machine import Broke, Object
from source_certificate import CertificateMachine, Count, Value, ZeroPredicate
from twiddle_certificate import named_return, synthetic


def methods(source):
    class_ = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef) and node.name == 'RingProduct')
    return {node.name: node for node in class_.body if isinstance(node, ast.FunctionDef)}


def code(node):
    return ast.unparse(node)


def same_statements(nodes, expected, message):
    need([code(node) for node in nodes] == expected, message)


def guard(node, expression, message):
    need(isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
         and code(node.value.func) == 'need' and len(node.value.args) == 2
         and not node.value.keywords and code(node.value.args[0]) == expression
         and isinstance(node.value.args[1], ast.Constant)
         and type(node.value.args[1].value) is str, message)


def loop_bounds(function):
    return [code(node.iter) for node in ast.walk(function) if isinstance(node, ast.For)]


def require_bounds(function, expected):
    loops = [node for node in ast.walk(function) if isinstance(node, ast.For)]
    need(all(not node.orelse for node in loops), 'no unaccounted source for-loop normal-completion clauses')
    actual = loop_bounds(function)
    need(sorted(actual) == sorted(expected), 'all source loop bounds for '+function.name)
    targets = {
        'stage': [('_', 'indices(plan.records)'), ('_', 'indices(groups)'), ('_', 'indices(half)'),
                  ('value', 'results'), ('buffer', '(left, top, bottom)'), ('buffer', '(left, top, bottom)')],
        'fft': [('_', 'indices(plan.m)')],
        'pointwise': [('_', 'indices(plan.fft_gaussians)'), ('value', 'result')],
        'recover': [('_', 'indices(plan.records)'), ('_', 'indices(plan.r)'), ('index', 'indices(plan.r)'),
                    ('_', 'range(2)'), ('_', 'range(2)')],
        'lift_and_pad': [('_', 'indices(plan.records)'), ('_', 'indices(plan.r)'), ('_', 'range(2)'),
                        ('_', 'indices(plan.lift)'), ('_', 'indices(zeros)')],
    }
    need(function.name in targets
         and sorted((code(node.target), code(node.iter)) for node in loops) == sorted(targets[function.name]),
         'exact source loop targets cannot rebind a numerical owner or parameter')
    return actual


@dataclass
class Words:
    name: str
    incoming: tuple = ()
    outgoing: list = field(default_factory=list)
    position: int = 0


class StreamMachine(CertificateMachine):
    def __init__(self, words, arithmetic):
        super().__init__(words, arithmetic, dag=True)
        self.services.update(read_signed=self.read_signed, write_signed=self.write_signed)

    def read_signed(self, tape, width):
        need(isinstance(tape, Words) and width.value == variable('Q')+2, 'complete Gaussian read width Q+2')
        need(tape.position < len(tape.incoming), 'source consumes the declared stream exactly once')
        value = tape.incoming[tape.position]
        tape.position += 1
        return Value(value)

    def write_signed(self, value, tape, width):
        need(isinstance(value, Value) and isinstance(tape, Words) and width.value == variable('Q')+2,
             'complete Gaussian write width Q+2')
        tape.outgoing.append(value.value)


def stage_body_certificate(words, arithmetic, engine):
    functions = methods(engine)
    stage = functions['stage']
    need(len(stage.body) == 6 and isinstance(stage.body[-1], ast.Try),
         'complete stage allocation, parameter, rewind and try outline')
    same_statements(stage.body[:1], ['output, left, top, bottom = (self.pool.acquire() for _ in range(4))'],
                    'four distinct source stage buffers')
    same_statements(stage.body[4:5], ['source.rewind()'], 'stage starts at the complete input origin')
    region = stage.body[-1]
    need(len(region.body) == 5 and not region.orelse, 'complete stage successful return region')
    same_statements(region.body[1:], ['source.clear()', 'output.rewind()',
                                     "self.calls['stages'] += 1", 'return output'],
                    'stage consumes only its source and returns the complete output')
    same_statements(region.finalbody,
                    ['for buffer in (left, top, bottom):\n    buffer.clear()',
                     'half.close()', 'groups.close()', 'table.rewind()'],
                    'stage cleanup preserves its returned output')
    loops = require_bounds(stage, ['indices(plan.records)', 'indices(groups)', 'indices(half)',
                                   'results', '(left, top, bottom)', '(left, top, bottom)'])
    inner = next(node for node in ast.walk(stage) if isinstance(node, ast.For) and code(node.iter) == 'indices(half)')
    need(len(inner.body) == 1 and isinstance(inner.body[0], ast.With), 'one complete source butterfly body')
    body = synthetic('source_stage_body', ('self', 'left', 'source', 'table', 'top', 'bottom', 'plan', 'opposite'),
                     deepcopy(inner.body))
    machine = StreamMachine(words, arithmetic)
    machine.functions[body.name] = body
    machine.validate(body)
    receipts = []
    Q = variable('Q')
    plan = Object(machine, 'Parameters', Q=Count(Q), wide=Count(Q+2), half_shift=Count(Q+1), word_width=Count(Q+3))
    arithmetic_ = Object(machine, 'Arithmetic')
    owner = Object(machine, 'StageOwner', arithmetic=arithmetic_)
    a, b, c, d, u, v = (variable(name) for name in ('a', 'b', 'c', 'd', 'u', 'v'))
    for opposite in (False, True):
        left, source, table = Words('left', (a, b)), Words('source', (c, d)), Words('table', (u, v))
        top, bottom = Words('top'), Words('bottom')
        machine.scalar_calls = []
        machine.function(body.name, (owner, left, source, table, top, bottom, plan, opposite))
        expected = machine.method(arithmetic_, 'dit' if opposite else 'dif',
                                  (Value(a), Value(b), Value(c), Value(d), Value(u), Value(v), plan))
        need(left.position == source.position == table.position == 2
             and top.outgoing == [x.value for x in expected[:2]]
             and bottom.outgoing == [x.value for x in expected[2:]],
             'actual source butterfly stream read/write order')
        receipts.append(dict(opposite=opposite, top=[x.data() for x in top.outgoing], bottom=[x.data() for x in bottom.outgoing]))

    # Bind concatenation to the complete group loop, not only one butterfly.
    group = next(node for node in ast.walk(stage) if isinstance(node, ast.For) and code(node.iter) == 'indices(groups)')
    need([code(node) for node in group.body[:3]] == [
        'copy_bits(source, left, half_bits)', 'left.rewind()', 'table.rewind()'],
        'actual complete first-half staging and table restart')
    need(group.body[3] is inner and len(group.body) == 8, 'complete group operation sequence')
    need([code(node) for node in group.body[5:7]] == ['append_bits(top, output)', 'append_bits(bottom, output)'],
        'natural top then bottom source group output')
    outer = next(node for node in ast.walk(stage) if isinstance(node, ast.For) and code(node.iter) == 'indices(plan.records)')
    need(outer.body == [group], 'each complete record consists of exactly all groups')
    guard(group.body[4], 'left.read() == table.read() == BLANK',
          'both complete source half and twiddle table are exhausted')
    same_statements(group.body[7:],
                    ['for buffer in (left, top, bottom):\n    borrowed_tape(buffer).clear()'],
                    'only staged scratch is reset between complete groups')
    # The bit count is an actual encoded product; source comparison is an
    # outline obligation whose integer interpretation is proved in PROOF.md.
    enclosing = next(node for node in ast.walk(stage) if isinstance(node, ast.With)
                     and any('Count.product(half, plan.wide)' in code(item.context_expr) for item in node.items))
    need(region.body[0] is enclosing and len(enclosing.items) == 1
         and code(enclosing.items[0]) == 'owned(Count.product(half, plan.wide)) as (half_bits,)'
         and len(enclosing.body) == 3 and enclosing.body[1] is outer
         and code(enclosing.body[0]) == 'half_bits.multiply_small(2)', 'two complete words per staged Gaussian')
    guard(enclosing.body[2], 'source.read() == BLANK', 'all complete stage records exhaust source')
    division = stage_division_certificate(words, arithmetic, stage)
    return dict(loop_bounds=loops, arbitrary_group_body=receipts, group_division=division,
                staged_bits='2 * (length/2) * (Q+2)', concatenation=['top', 'bottom'],
                written_invariant='groups=N/length; after j butterflies, both halves and the table have consumed j complete Gaussian records')


@dataclass
class Stream:
    expression: object
    live: bool = True

    def source_attribute(self, name):
        if name in ('clear', 'close'):
            return lambda: setattr(self, 'live', False)
        raise ValueError('unknown stream numerical operation '+name)


class FFTMachine(CertificateMachine):
    extra_methods = {'table', 'stage'}

    def __init__(self, words, arithmetic):
        super().__init__(words, arithmetic, dag=True)
        self.methods['FFT'] = {'table': None, 'stage': None}
        self.events = []

    def method(self, object_, name, arguments):
        if object_.kind == 'FFT':
            if name == 'table':
                plan, length, opposite = arguments
                self.events.append(['table', length.value.data(), opposite])
                return Stream(['twiddles', length.value.data(), opposite])
            if name == 'stage':
                current, table, plan, length, opposite = arguments
                need(current.live and table.live
                     and table.expression == ['twiddles', length.value.data(), opposite],
                     'stage uses a live current packet and its own exact table and sign')
                self.events.append(['stage', length.value.data(), opposite])
                current.live = False
                return Stream(['stage', current.expression, length.value.data(), opposite])
            raise ValueError('unknown FFT source numerical call')
        return super().method(object_, name, arguments)


def fft_loop_certificate(words, arithmetic, engine):
    table = methods(engine)['table']
    need(len(table.body) == 4 and isinstance(table.body[1], ast.With)
         and isinstance(table.body[3], ast.Try), 'complete successful twiddle-table copy outline')
    same_statements(table.body[:3], ['self.idle()',
                    'with self.scope.suspended():\n    returned = self.twiddles.run(borrowed_count(plan.Q), borrowed_count(length), opposite)',
                    'result = self.pool.acquire()'],
                    'actual table request binds precision, current stage length and direction')
    same_statements(table.body[3].body, ['append_bits(returned, result)', 'result.rewind()',
                                       "self.calls['tables'] += 1", 'return result'],
                    'complete table copy returns the owned source buffer')
    need(not table.body[3].orelse, 'no omitted successful table-copy exit')
    same_statements(table.body[3].finalbody, ['returned.clear()', 'erase_marker(returned)'],
                    'only the consumed child table is retired')
    function = methods(engine)['fft']
    require_bounds(function, ['indices(plan.m)'])
    need(len(function.body) == 3 and isinstance(function.body[2], ast.Try), 'whole FFT driver outline')
    region = function.body[2]
    need(len(region.body) == 2 and isinstance(region.body[0], ast.For)
         and code(region.body[1]) == 'return current', 'all FFT stages precede the returned current packet')
    need(not region.orelse, 'no unaccounted FFT successful-exit statements')
    same_statements(region.finalbody, ['length.close()'], 'FFT cleanup preserves returned current')
    loop = region.body[0]
    need(code(loop.iter) == 'indices(plan.m)' and not loop.orelse, 'exact m complete FFT stages')
    initialize = synthetic('source_fft_initialize', ('source', 'plan', 'opposite'),
                           [*deepcopy(function.body[:2]), named_return(('current', 'length'))])
    step = synthetic('source_fft_step', ('self', 'current', 'plan', 'length', 'opposite'),
                     [*deepcopy(loop.body), named_return(('current', 'length'))])
    machine = FFTMachine(words, arithmetic)
    for node in (initialize, step):
        machine.functions[node.name] = node
        machine.validate(node)
    plan = Object(machine, 'Parameters', N=Count(variable('N')), m=Count(variable('m')))
    owner = Object(machine, 'FFT')
    L = variable('half_length')
    receipts = []
    for opposite in (False, True):
        initial, length = machine.function(initialize.name, (Stream('input'), plan, opposite))
        need(initial.live and initial.expression == 'input'
             and length.value == (Poly.number(2) if opposite else variable('N')),
             'actual ascending/descending FFT first stage')
        machine.events = []
        current, following = machine.function(step.name, (owner, Stream('current'), plan, Count(2*L), opposite))
        need(machine.events == [['table', (2*L).data(), opposite], ['stage', (2*L).data(), opposite]],
             'exactly one correctly directed table and stage per source iteration')
        need(current.live and current.expression == ['stage', 'current', (2*L).data(), opposite]
             and following.value == (4*L if opposite else L), 'actual source stage transition and dyadic length update')
        receipts.append(dict(opposite=opposite, first_length=length.value.data(),
                             next_length=following.value.data(), events=machine.events))
    return dict(stage_count='m=ell+1=log2(N)', directions=receipts,
                written_invariant='Forward lengths N,N/2,...,2; opposite lengths 2,4,...,N; DIF bit reversal matches DIT input order')


def stage_division_certificate(words, arithmetic, function):
    need(len(function.body) >= 5 and isinstance(function.body[3], ast.With),
         'source stage group-count initialization outline')
    context = function.body[3]
    need(len(context.items) == 1 and code(context.items[0]) == 'owned(Count(length)) as (divisor,)'
         and len(context.body) == 1 and isinstance(context.body[0], ast.While),
         'source dyadic group divisor is a copy of the stage length')
    loop = context.body[0]
    need(code(loop.test) == 'not divisor.zero()' and not loop.orelse, 'complete dyadic group division loop')
    machine = CertificateMachine(words, arithmetic)
    machine.positive_names.update(('x_positive', 'y_positive'))
    initialize = synthetic('group_initialize', ('length', 'plan'),
                           [*deepcopy(function.body[1:3]), named_return(('half', 'groups'))])
    step = synthetic('group_divide_step', ('divisor', 'groups'), deepcopy(loop.body))
    for node in (initialize, step):
        machine.functions[node.name] = node
        machine.validate(node)
    x, y = variable('x_positive'), variable('y_positive')
    plan = Object(machine, 'Parameters', N=Count(variable('N')))
    half, groups = machine.function(initialize.name, (Count(2*x), plan))
    need(half.value == x and groups.value == variable('N'), 'actual source half and group initialization')
    receipts = []
    for final in (False, True):
        environment = dict(divisor=Count(1 if final else 2*x), groups=Count(y if final else 2*y))
        broke = False
        try:
            machine.statements(step.body, environment)
        except Broke:
            broke = True
        need(broke == final and environment['divisor'].value == (Poly.number(0) if final else x)
             and environment['groups'].value == y, 'actual dyadic division step and terminal break')
        receipts.append(dict(final=final, divisor=environment['divisor'].value.data(),
                             groups=environment['groups'].value.data(), break_taken=broke))
    return dict(transfers=receipts, written_invariant='After j nonterminal steps: divisor=L/2^j and groups=N/2^j; final divisor1 returns groups=N/L')


class RecoveryMachine(StreamMachine):
    def __init__(self, words, arithmetic):
        super().__init__(words, arithmetic)
        self.widths = {}
        self.last = False
        self.zero_guards = []
        self.services.update(nearest=lambda value, amount: Value(Poly.atom('nearest_half_away', value.value, amount.value)),
                             need=self.need_condition)

    def read_signed(self, tape, width):
        need(width.value == self.widths[tape.name], 'source recovery read width')
        need(tape.position < len(tape.incoming), 'complete scalar recovery input')
        value = tape.incoming[tape.position]
        tape.position += 1
        return Value(value)

    def write_signed(self, value, tape, width):
        need(width.value == self.widths[tape.name], 'source recovery output width')
        tape.outgoing.append(value.value)

    def compare(self, left, right):
        need(left.value == variable('index') and right.value == variable('last'), 'actual final ordinary coefficient guard')
        return 0 if self.last else -1

    def need_condition(self, condition, message):
        if isinstance(condition, ZeroPredicate):
            expected = Poly.atom('nearest_half_away', variable('upper_grid'), variable('s'))
            need(self.last and condition.value == expected, 'only the proved final ordinary-coefficient zero premise')
            self.zero_guards.append(condition.value.data())
            return
        super().need_condition(condition, message)


def recovery_certificate(words, arithmetic, engine):
    function = methods(engine)['recover']
    need(len(function.body) == 3 and isinstance(function.body[-1], ast.Try), 'whole recovery source outline')
    same_statements(function.body[:2], ['output, low = (self.pool.acquire(), self.pool.acquire())', 'source.rewind()'],
                    'distinct output and lower-half buffers at the source origin')
    region = function.body[-1]
    need(len(region.body) == 6 and not region.orelse, 'complete recovery successful path')
    guard(region.body[1], 'source.read() == BLANK', 'recovery exhausts all complete source records')
    same_statements(region.body[2:], ['source.clear()', 'output.rewind()',
                                     "self.calls['recoveries'] += 1", 'return output'],
                    'recovery retains the returned output while consuming its source')
    same_statements(region.finalbody, ['low.clear()'], 'recovery cleanup erases only lower-half scratch')
    one = region.body[0]
    need(isinstance(one, ast.With) and len(one.items) == len(one.body) == 1
         and code(one.items[0]) == 'owned(Count.literal(1)) as (one,)', 'last-index unit is exactly one')
    last_context = one.body[0]
    need(isinstance(last_context, ast.With) and len(last_context.items) == len(last_context.body) == 1
         and code(last_context.items[0]) == 'owned(subtract(plan.r, one)) as (last,)',
         'last upper-half index is exactly r-1')
    loops = require_bounds(function, ['indices(plan.records)', 'indices(plan.r)', 'range(2)',
                                      'indices(plan.r)', 'range(2)'])
    record = next(node for node in ast.walk(function) if isinstance(node, ast.For) and code(node.iter) == 'indices(plan.records)')
    need(last_context.body[0] is record and len(record.body) == 5 and isinstance(record.body[0], ast.For)
         and isinstance(record.body[2], ast.For), 'complete two-half recovery and retirement outline')
    lower_loop, upper_loop = record.body[0], record.body[2]
    need(code(lower_loop.iter) == code(upper_loop.iter) == 'indices(plan.r)'
         and code(lower_loop.target) == '_' and code(upper_loop.target) == 'index',
         'lower and upper passes have their actual bounds and index role')
    need(code(record.body[1]) == 'low.rewind()' and code(record.body[4]) == 'borrowed_tape(low).clear()',
         'recover all lower coefficients before the upper half; clear only after the full record')
    guard(record.body[3], 'low.read() == BLANK', 'the complete lower buffer is checked before retirement')
    need(len(lower_loop.body) == len(upper_loop.body) == 1
         and isinstance(lower_loop.body[0], ast.For) and isinstance(upper_loop.body[0], ast.For),
         'two explicit scalar components per recovered Gaussian')
    lower = synthetic('recover_lower_component', ('source', 'low', 'plan'), deepcopy(lower_loop.body[0].body))
    upper = synthetic('recover_upper_component', ('source', 'low', 'output', 'plan', 'index', 'last'),
                      deepcopy(upper_loop.body[0].body))
    machine = RecoveryMachine(words, arithmetic)
    for node in (lower, upper):
        machine.functions[node.name] = node
        machine.validate(node)
    Q, p, ell, s = (variable(name) for name in ('Q', 'p', 'ell', 's'))
    plan = Object(machine, 'Parameters', wide=Count(Q+2), small=Count(p+2),
                  integer_width=Count(2*p+ell+3), recovery_shift=Count(s), product_shift=Count(p+ell))
    machine.widths = dict(source=Q+2, low=2*p+ell+3, output=p+2)
    lower_grid, upper_grid = variable('lower_grid'), variable('upper_grid')
    source, low = Words('source', (lower_grid,)), Words('low')
    machine.function(lower.name, (source, low, plan))
    expected_lower = Poly.atom('nearest_half_away', lower_grid, s)
    need(source.position == 1 and low.outgoing == [expected_lower], 'actual lower-half integer recovery and storage')
    receipts = []
    from algebra import truncation
    for last in (False, True):
        source = Words('source', (upper_grid,))
        low = Words('low', (expected_lower,))
        output = Words('output')
        machine.last, machine.zero_guards = last, []
        machine.function(upper.name, (source, low, output, plan, Count(variable('index')), Count(variable('last'))))
        expected = truncation(expected_lower-Poly.atom('nearest_half_away', upper_grid, s), p+ell)
        need(source.position == low.position == 1 and output.outgoing == [expected]
             and len(machine.zero_guards) == int(last), 'nearest integer, negacyclic subtraction and only-final p+ell truncation')
        receipts.append(dict(last=last, output=expected.data(), zero_guard=machine.zero_guards))
    return dict(loop_bounds=loops, lower_integer=expected_lower.data(), upper_pass=receipts,
                written_premise='The last ordinary coefficient has degree2r-1 and is zero; the scaled error is <1/8 so nearest returns exactly zero')


@dataclass
class PacketFlow:
    expression: object


class RunMachine(CertificateMachine):
    extra_methods = {'compile', 'lift_and_pad', 'fft', 'pointwise', 'recover', 'idle'}

    def __init__(self, words, arithmetic, plan_source):
        super().__init__(words, arithmetic, plan_source, dag=True)
        self.methods['RingProduct'] = {name: None for name in ('lift_and_pad', 'fft', 'pointwise', 'recover', 'idle')}
        self.events = []
        self.services.update(ProductPlan=self.new_plan, append_bits=self.append_bits)

    def new_plan(self, *parameters):
        result = Object(self, 'ProductPlan')
        self.method(result, '__init__', parameters)
        return result

    def append_bits(self, source, destination):
        need(isinstance(source, PacketFlow) and isinstance(destination, PacketFlow)
             and destination.expression == 'empty_output', 'one complete returned normalized-product packet')
        destination.expression = source.expression
        self.events.append('install_output')

    def method(self, object_, name, arguments):
        if object_.kind != 'RingProduct':
            return super().method(object_, name, arguments)
        if name == 'idle':
            self.events.append('children_returned')
            return
        plan = arguments[-1] if name != 'fft' else arguments[1]
        need(isinstance(plan, Object) and plan.kind == 'ProductPlan', 'one source-generated numerical plan')
        if name == 'lift_and_pad':
            self.events.append(['lift_and_pad', arguments[0].expression])
            return PacketFlow(['lift_and_pad', arguments[0].expression])
        if name == 'fft':
            source, _, opposite = arguments
            need(type(opposite) is bool, 'finite Fourier direction')
            self.events.append(['fft', opposite])
            return PacketFlow(['fft', opposite, source.expression])
        if name == 'pointwise':
            first, second, _ = arguments
            self.events.append('pointwise')
            return PacketFlow(['pointwise', first.expression, second.expression])
        if name == 'recover':
            self.events.append('recover')
            return PacketFlow(['recover', arguments[0].expression])
        raise ValueError('unknown normalized-product numerical stage')


def whole_run_certificate(words, arithmetic, plan_source, engine):
    function = methods(engine)['run']
    need(len(function.body) == 7 and isinstance(function.body[5], ast.Try),
         'whole source run entry, successful path and returned owner')
    same_statements(function.body[:1], ['first, second = (borrowed_tape(first), borrowed_tape(second))'],
                    'both numerical inputs use the retained borrowed-tape ABI')
    guard(function.body[1], 'first is not second and first is not self.output and (second is not self.output)',
          'the source disallows input/output aliasing')
    same_statements(function.body[2:5], ['self.rearm()', 'plan = None', 'succeeded = False'],
                    'one fresh source run and explicit success state')
    same_statements(function.body[6:], ['return self.output'], 'returns the actual installed output owner')
    outer = function.body[5]
    need(len(outer.body) == 1 and not outer.handlers and not outer.orelse
         and isinstance(outer.body[0], ast.With), 'one complete source caller scope')
    scope = outer.body[0]
    need([code(item) for item in scope.items] == ['sealed_constructors()', 'self.scope.installed()']
         and len(scope.body) == 1 and isinstance(scope.body[0], ast.Try),
         'all numerical source calls share the actual installed owner scope')
    region = scope.body[0]
    need(not region.handlers and not region.orelse, 'no alternate successful numerical run path')
    need(len(region.body) == 13, 'no omitted or unaccounted source numerical operation')
    need(code(region.body[-1]) == 'succeeded = True',
         'actual successful numerical return enables the preserving finalization path')
    same_statements(region.finalbody, ['first.rewind()', 'second.rewind()',
                    'for value in (dimension, precision, ell, rows):\n    value.rewind()',
                    'for value in (self.a, self.b, self.current):\n    if value is not None:\n        value.clear()',
                    'self.a = self.b = self.current = None',
                    'if plan is not None:\n    plan.close()', 'self.pool.empty()'],
                    'source numerical cleanup cannot erase the distinct installed output')
    same_statements(outer.finalbody, ['for item in self.pool.tapes:\n    erase_marker(item)',
                    'self.output.rewind()',
                    'if not succeeded:\n    self.output.clear()\n    erase_marker(self.output)',
                    'self.closed = True'], 'successful source return preserves the installed complete packet')
    numerical = synthetic('source_complete_run', ('self', 'first', 'second', 'dimension', 'precision', 'ell', 'rows'),
                          deepcopy(region.body))
    machine = RunMachine(words, arithmetic, plan_source)
    machine.functions[numerical.name] = numerical
    machine.validate(numerical)
    owner = Object(machine, 'RingProduct', a=None, b=None, current=None, output=PacketFlow('empty_output'))
    parameters = tuple(Count(variable(name)) for name in ('A', 'p', 'ell', 'C'))
    machine.function(numerical.name, (owner, PacketFlow('first'), PacketFlow('second'), *parameters))
    expected = ['recover', ['fft', True, ['pointwise',
                 ['fft', False, ['lift_and_pad', 'first']], ['fft', False, ['lift_and_pad', 'second']]]]]
    need(owner.fields['output'].expression == expected, 'actual complete forward/product/opposite/recovery composition')
    expected_events = [['lift_and_pad', 'first'], ['lift_and_pad', 'second'], ['fft', False], ['fft', False],
                       'pointwise', ['fft', True], 'recover', 'children_returned', 'install_output']
    need(machine.events == expected_events and owner.fields['a'] is owner.fields['b'] is None,
         'all three transforms and exact final recovery precede output installation')
    return dict(composition=expected, events=machine.events,
                source_numerical_statements=len(region.body),
                written_boundary='The retained successful-entry ownership/Count/scalar contracts supply each numerical region; failure cleanup is not a new theorem')


def pointwise_stream_certificate(words, arithmetic, engine):
    function = methods(engine)['pointwise']
    need(len(function.body) == 4 and isinstance(function.body[-1], ast.Try), 'whole pointwise source outline')
    same_statements(function.body[:3], ['output = self.pool.acquire()', 'first.rewind()', 'second.rewind()'],
                    'fresh pointwise output and complete matching input origins')
    region = function.body[-1]
    need(len(region.body) == 7 and not region.orelse and not region.finalbody,
         'complete pointwise successful path')
    guard(region.body[1], 'first.read() == second.read() == BLANK', 'both frequency packets are exhausted')
    same_statements(region.body[2:], ['first.clear()', 'second.clear()', 'output.rewind()',
                                     "self.calls['pointwise'] += 1", 'return output'],
                    'pointwise consumes both inputs and returns only the complete product')
    loops = require_bounds(function, ['indices(plan.fft_gaussians)', 'result'])
    loop = next(node for node in ast.walk(function) if isinstance(node, ast.For)
                and code(node.iter) == 'indices(plan.fft_gaussians)')
    need(region.body[0] is loop and len(loop.body) == 1, 'one complete live pointwise Gaussian body')
    body = synthetic('source_pointwise_body', ('self', 'first', 'second', 'output', 'plan'), deepcopy(loop.body))
    machine = StreamMachine(words, arithmetic)
    machine.functions[body.name] = body
    machine.validate(body)
    Q = variable('Q')
    plan = Object(machine, 'Parameters', Q=Count(Q), wide=Count(Q+2), word_width=Count(Q+3))
    arithmetic_ = Object(machine, 'Arithmetic')
    owner = Object(machine, 'PointwiseOwner', arithmetic=arithmetic_)
    a, b, c, d = (variable(name) for name in ('a', 'b', 'c', 'd'))
    first, second, output = Words('first', (a, b)), Words('second', (c, d)), Words('output')
    machine.function(body.name, (owner, first, second, output, plan))
    expected = machine.method(arithmetic_, 'pointwise', (Value(a), Value(b), Value(c), Value(d), plan))
    need(first.position == second.position == 2 and output.outgoing == [x.value for x in expected],
         'complete source frequency record pairing and output order')
    return dict(loop_bounds=loops, outputs=[x.data() for x in output.outgoing],
                total_gaussians='C*2^A*N from the actual ProductPlan')


def lift_layout_certificate(engine):
    function = methods(engine)['lift_and_pad']
    need(len(function.body) == 3 and isinstance(function.body[-1], ast.Try), 'whole lift source outline')
    same_statements(function.body[:2], ['output = self.pool.acquire()', 'source.rewind()'],
                    'fresh lifted output and complete input origin')
    region = function.body[-1]
    need(len(region.body) == 4 and not region.orelse, 'complete lift successful path')
    guard(region.body[1], 'source.read() == BLANK', 'lift exhausts all supplied complete records')
    same_statements(region.body[2:], ['output.rewind()', 'return output'], 'lift returns the completed output')
    same_statements(region.finalbody, ['source.rewind()'], 'lift cleanup preserves input and output contents')
    loops = require_bounds(function, ['indices(plan.records)', 'indices(plan.r)', 'range(2)',
                                      'indices(plan.lift)', 'indices(zeros)'])
    source = next(node for node in ast.walk(function) if isinstance(node, ast.For) and code(node.iter) == 'range(2)')
    need(len(source.body) == 2 and isinstance(source.body[0], ast.For)
         and code(source.body[0].iter) == 'indices(plan.lift)'
         and [code(x) for x in source.body[0].body] == ['output.append(0)']
         and code(source.body[1]) == 'copy_bits(source, output, plan.small)',
         'exact signed two-complement lift: low zeros then original complete word')
    padding = next(node for node in ast.walk(function) if isinstance(node, ast.With)
                   and any('Count.product(plan.r, plan.wide)' in code(item.context_expr) for item in node.items))
    need(len(padding.items) == 1
         and code(padding.items[0]) == 'owned(Count.product(plan.r, plan.wide)) as (zeros,)'
         and len(padding.body) == 2 and code(padding.body[0]) == 'zeros.multiply_small(2)'
         and isinstance(padding.body[1], ast.For) and code(padding.body[1].iter) == 'indices(zeros)'
         and [code(x) for x in padding.body[1].body] == ['output.append(0)'],
         'exactly r complete zero Gaussian coefficients after each lifted record')
    record = region.body[0]
    need(isinstance(record, ast.For) and len(record.body) == 2
         and code(record.iter) == 'indices(plan.records)'
         and isinstance(record.body[0], ast.For) and code(record.body[0].iter) == 'indices(plan.r)'
         and record.body[1] is padding
         and record.body[0].body == [source], 'each full input record precedes exactly its own zero padding')
    return dict(loop_bounds=loops, source_words='p+2', lift_bits='Q-p', padded_gaussians='r',
                written_identity='Signed LSB-first shift gives exact Q-grid input; input degree<r and N=2r prevent cyclic wrap')
