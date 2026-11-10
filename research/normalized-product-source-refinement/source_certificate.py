# SPDX-License-Identifier: Apache-2.0
"""Arbitrary-input polynomial certificates derived from authenticated ASTs.

The primitive model is exact nonnegative integer Count arithmetic. Its binary
shift/refinement and the retained scalar child contract are explicit premises
of the written proof; source helper names are not endpoint oracles.
"""
import ast
from dataclasses import dataclass
from itertools import product
import json

from algebra import Poly, as_poly, ceiling_log, need, power_two, truncation, variable
from ast_machine import Context, Machine, Object


class Count:
    def __init__(self, value):
        self.value = value.value if isinstance(value, Count) else as_poly(value)

    def source_attribute(self, name):
        operations = {
            'add': lambda value: self._set(self.value+value.value),
            'multiply_small': lambda value: self._set(self.value*value),
            'divide_small': self.divide_small,
            'increment': lambda: self._set(self.value+1),
            'zero': lambda: ZeroPredicate(self.value),
            'close': lambda: None,
        }
        need(name in operations, 'unknown exact Count operation '+name)
        return operations[name]

    def _set(self, value):
        self.value = value

    def divide_small(self, value):
        need(type(value) is int and value > 0, 'positive exact small divisor')
        if not self.value.terms or len(self.value.terms) == 1 and self.value.terms[0][0] == ():
            quotient, remainder = divmod(self.value.integer(), value)
            self.value = Poly.number(quotient)
            return remainder
        need(all(c % value == 0 for _, c in self.value.terms), 'symbolically exact small division')
        self.value = Poly(tuple((m, c//value) for m, c in self.value.terms))
        return 0


class CountFactory:
    def __call__(self, value):
        return Count(value)

    def source_attribute(self, name):
        if name == 'literal':
            def literal(value):
                need(type(value) is int and value >= 0, 'nonnegative literal Count')
                return Count(Poly.number(value))
            return literal
        if name == 'product':
            return lambda left, right: Count(left.value*right.value)
        raise ValueError('unknown exact Count class service '+name)


@dataclass(frozen=True)
class Sign:
    value: Poly


@dataclass(frozen=True)
class Magnitude:
    value: Poly
    operation: str = 'absolute'
    exponent: object = None

    def source_attribute(self, name):
        need(name == 'zero' and self.operation == 'absolute', 'only an explicit symbolic magnitude-zero predicate')
        return lambda: ZeroPredicate(self.value)


@dataclass(frozen=True)
class ZeroPredicate:
    value: Poly


@dataclass(frozen=True)
class Value:
    value: Poly

    def source_attribute(self, name):
        if name == 'magnitude': return Magnitude(self.value)
        if name == 'negative': return Sign(self.value)
        if name == 'copy': return lambda: Value(self.value)
        if name == 'negated': return lambda: Value(-self.value)
        if name == 'close': return lambda: None
        raise ValueError('unknown symbolic signed field '+name)


class Packet:
    def __init__(self, value, width):
        self.value, self.width = value, width
        self.consumed, self.cleared = False, False

    def source_attribute(self, name):
        if name == 'read':
            return lambda: 'BLANK' if self.consumed else 'DATA'
        if name == 'clear':
            return lambda: setattr(self, 'cleared', True)
        raise ValueError('unknown protected child packet operation '+name)


class ExactWord:
    def source_attribute(self, name):
        need(name == 'run', 'only exact scalar child call')
        return lambda a, b, width: Packet(a.value*b.value, 2*width.value)


class Scope:
    def source_attribute(self, name):
        need(name == 'suspended', 'only retained child scope boundary')
        return lambda: Context(None)


class Order:
    """Possible exact compare results under a quantified parameter premise."""
    def __init__(self, values):
        self.values = tuple(values)

    def test(self, other, predicate):
        need(type(other) is int, 'order compared with literal control value')
        results = {predicate(value, other) for value in self.values}
        need(len(results) == 1, 'unproved parameter-dependent numerical branch')
        return results.pop()

    def __eq__(self, other): return self.test(other, lambda x, y: x == y)
    def __ne__(self, other): return self.test(other, lambda x, y: x != y)
    def __lt__(self, other): return self.test(other, lambda x, y: x < y)
    def __le__(self, other): return self.test(other, lambda x, y: x <= y)
    def __gt__(self, other): return self.test(other, lambda x, y: x > y)
    def __ge__(self, other): return self.test(other, lambda x, y: x >= y)


def read_fixed(packet, width):
    need(isinstance(packet, Packet) and not packet.consumed and packet.width == width.value,
         'complete exact scalar result width and consumption')
    packet.consumed = True
    return Count(packet.value)


def erase_marker(packet):
    need(isinstance(packet, Packet) and packet.consumed and packet.cleared,
         'consumed scalar output retired')


class CertificateMachine(Machine):
    def __init__(self, words, arithmetic, plan=None, dag=False):
        self.count_factory = CountFactory()
        self.dag = dag
        self.scalar_calls = []
        self.parameter_assumptions = []
        self.positive_names = set()
        self.positive_atoms = set()
        services = dict(Count=self.count_factory, owned=lambda *x: Context(x),
                        need=self.need_condition, bool=bool, type=self.source_type, tuple=tuple,
                        isinstance=self.source_isinstance,
                        compare=self.compare, subtract=self.subtract,
                        borrowed_count=lambda value: value, read_fixed=read_fixed, erase_marker=erase_marker,
                        BLANK='BLANK', positive=self.positive,
                        ceiling_log=self.ceiling_log_count,
                        left_shift=self.left_shift, right_shift=self.right_shift)
        super().__init__(services)
        self.services['Signed'] = self.signed
        self.register(words, functions=('add', 'difference', 'scaled', 'truncate', 'power_two'),
                      classes={'Signed': ('__init__', 'copy', 'negated', 'close')})
        self.register(arithmetic, classes={'Arithmetic': ('multiply', 'complex_product', 'dif', 'dit', 'pointwise')})
        if plan is not None:
            self.register(plan, classes={'ProductPlan': ('__init__', 'keep', 'compile')})
        if dag:
            # This endpoint is installed only after independent source proof of
            # all signed magnitude branches below has passed.
            self.services['add'] = lambda a, b: Value(a.value+b.value)

    def source_type(self, value):
        need(type(value) in (bool, int, str, type(None)),
             'source type query requires an explicitly concrete literal')
        return type(value)

    def source_isinstance(self, value, kind):
        need(kind is self.count_factory and isinstance(value, Count),
             'only the established Count constructor type premise')
        return True

    def need_condition(self, condition, message):
        need(self.control_bool(condition), message)

    def certified_order(self, value):
        for monomial, _ in value.terms:
            for atom in monomial:
                data = json.loads(atom)
                need(atom in self.positive_atoms or data[0] == 'power_two'
                     or data[0] == 'integer' and data[1] in self.positive_names,
                     'symbolic order needs an explicit strictly-positive atom premise')
        return value.positive_variable_order()

    def control_bool(self, value):
        if isinstance(value, ZeroPredicate):
            return self.certified_order(value.value) == 0
        return super().control_bool(value)

    def control_compare(self, left, operator, right):
        if isinstance(left, Order):
            predicates = {ast.Eq: lambda x, y: x == y, ast.NotEq: lambda x, y: x != y,
                          ast.Lt: lambda x, y: x < y, ast.LtE: lambda x, y: x <= y,
                          ast.Gt: lambda x, y: x > y, ast.GtE: lambda x, y: x >= y}
            need(type(operator) in predicates, 'only ordered parameter predicates')
            return left.test(right, predicates[type(operator)])
        return super().control_compare(left, operator, right)

    def ceiling_log_count(self, value):
        need(isinstance(value, Count) and self.certified_order(value.value) > 0,
             'positive exact ceiling-log argument')
        if value.value == Poly.number(1):
            return Count(0)
        result = ceiling_log(value.value)
        if self.certified_order(value.value-1) > 0:
            self.positive_atoms.add(result.terms[0][0][0])
        return Count(result)

    def signed(self, magnitude, negative=False):
        if isinstance(magnitude, Magnitude):
            need(isinstance(negative, Sign) and negative.value == magnitude.value,
                 'signed magnitude operation preserves the original sign')
            if magnitude.operation == 'left':
                return Value(magnitude.value*power_two(magnitude.exponent))
            if magnitude.operation == 'right':
                return Value(truncation(magnitude.value, magnitude.exponent))
            raise ValueError('unsupported signed magnitude reconstruction')
        if self.dag:
            need(isinstance(magnitude, Count) and type(negative) is bool,
                 'verified signed constructor on an integer magnitude')
            return Value(-magnitude.value if negative else magnitude.value)
        object_ = Object(self, 'Signed')
        self.method(object_, '__init__', (magnitude, negative))
        return object_

    def compare(self, left, right):
        pair = left.value, right.value
        if pair == (variable('p'), Poly.number(2)):
            self.parameter_assumptions.append('p>=2')
            self.positive_names.add('p')
            return Order((0, 1))
        if pair == (variable('ell'), variable('p')):
            self.parameter_assumptions.append('ell<p')
            return -1
        return self.certified_order(left.value-right.value)

    def positive(self, count):
        need(isinstance(count, Count), 'encoded positive parameter')
        need(count.value in (variable('A'), variable('C'), variable('ell')),
             'only caller-admitted positive numerical parameters')
        self.parameter_assumptions.append(['positive', count.value.data()])
        self.positive_names.add(json.loads(count.value.terms[0][0][0])[1])

    def subtract(self, left, right):
        difference = left.value-right.value
        need(self.certified_order(difference) >= 0, 'unsigned source subtraction domain')
        return Count(difference)

    def left_shift(self, value, amount):
        if isinstance(value, Magnitude):
            need(value.operation == 'absolute', 'single source left shift')
            return Magnitude(value.value, 'left', amount.value)
        return Count(value.value*power_two(amount.value))

    def right_shift(self, value, amount):
        if isinstance(value, Count):
            return Count(Poly.atom('unsigned_right_shift', value.value, amount.value))
        need(isinstance(value, Magnitude) and value.operation == 'absolute', 'source magnitude truncation')
        return Magnitude(value.value, 'right', amount.value)

    def method(self, object_, name, arguments):
        if self.dag and object_.kind == 'Arithmetic' and name == 'multiply':
            left, right, width = arguments
            need(isinstance(left, Value) and isinstance(right, Value) and isinstance(width, Count),
                 'typed exact scalar multiplication contract')
            need(width.value == variable('Q')+3, 'complete butterfly scalar width Q+3')
            self.scalar_calls.append([left.value.data(), right.value.data(), width.value.data()])
            return Value(left.value*right.value)
        return super().method(object_, name, arguments)


def numerical_value(value):
    need(isinstance(value, Object) and value.kind == 'Signed', 'actual source Signed result')
    magnitude, sign = value.fields['magnitude'], value.fields['negative']
    need(isinstance(magnitude, Count) and type(sign) is bool, 'signed result representation')
    return -magnitude.value if sign else magnitude.value


def signed_helper_certificate(words, arithmetic):
    machine = CertificateMachine(words, arithmetic)
    machine.positive_names.update(('x_positive', 'y_positive'))
    x, y = variable('x_positive'), variable('y_positive')
    zero = Poly.number(0)
    # Complete partition of two nonnegative magnitudes, with x,y strictly
    # positive when present. This includes all zero/equality/order branches.
    domains = ((zero, zero), (x, zero), (zero, x), (x, x), (x+y, x), (x, x+y))
    cases = []
    for ordinal, (a, b) in enumerate(domains):
        for first_sign, second_sign in product((False, True), repeat=2):
            left, right = machine.signed(Count(a), first_sign), machine.signed(Count(b), second_sign)
            av, bv = numerical_value(left), numerical_value(right)
            total = machine.function('add', (left, right))
            delta = machine.function('difference', (left, right))
            copied = machine.method(left, 'copy', ())
            negated = machine.method(left, 'negated', ())
            need(numerical_value(total) == av+bv and numerical_value(delta) == av-bv
                 and numerical_value(copied) == av and numerical_value(negated) == -av,
                 'all-input signed helper identity')
            object_ = Object(machine, 'Arithmetic', word=ExactWord(), scope=Scope(), products=0)
            multiplied = machine.method(object_, 'multiply', (left, right, Count(variable('n'))))
            need(numerical_value(multiplied) == av*bv and object_.fields['products'] == 1,
                 'source signed multiplication and complete returned word')
            cases.append(dict(domain=ordinal, signs=[first_sign, second_sign]))
    return dict(complete_nonnegative_domains=6, sign_cases=len(cases),
                certified_helpers=['Signed.__init__', 'Signed.copy', 'Signed.negated',
                                   'add', 'difference', 'Arithmetic.multiply'],
                source_functions_executed=sorted(machine.executed))


def butterfly_certificate(words, arithmetic):
    machine = CertificateMachine(words, arithmetic, dag=True)
    object_ = Object(machine, 'Arithmetic')
    q = variable('Q')
    plan = Object(machine, 'Parameters', Q=Count(q), half_shift=Count(q+1), word_width=Count(q+3))
    names = {name: variable(name) for name in ('a', 'b', 'c', 'd', 'u', 'v')}
    a, b, c, d, u, v = (names[name] for name in ('a', 'b', 'c', 'd', 'u', 'v'))
    inputs = tuple(Value(x) for x in (a, b, c, d, u, v))
    B = power_two(q)
    expected = {
        'dif': (truncation(a+c, 1), truncation(b+d, 1),
                truncation(u*(a-c)-v*(b-d), q+1), truncation(v*(a-c)+u*(b-d), q+1)),
        'dit': (truncation(B*a+u*c-v*d, q+1), truncation(B*b+v*c+u*d, q+1),
                truncation(B*a-u*c+v*d, q+1), truncation(B*b-v*c-u*d, q+1)),
        'pointwise': (truncation(a*c-b*d, q), truncation(a*d+b*c, q)),
    }
    receipts = []
    for name in ('dif', 'dit', 'pointwise'):
        machine.scalar_calls = []
        arguments = (*inputs, plan) if name != 'pointwise' else (*inputs[:4], plan)
        result = machine.method(object_, name, arguments)
        need(tuple(x.value for x in result) == expected[name], 'exact arbitrary-input '+name+' rounding DAG')
        need(len(machine.scalar_calls) == 4, 'four complete scalar products per Gaussian arithmetic node')
        receipts.append(dict(operation=name, outputs=[x.value.data() for x in result], scalar_calls=machine.scalar_calls))
    return dict(arbitrary_integer_inputs=list(names), formal_precision='Q',
                source_functions_executed=sorted(machine.executed), exact_dags=receipts)


def plan_certificate(words, arithmetic, plan_source):
    machine = CertificateMachine(words, arithmetic, plan_source)
    compile_ = machine.methods['ProductPlan']['compile']
    need([ast.unparse(node) for node in compile_.body[:3]] ==
         ['positive(self.A)', 'positive(self.ell)', 'positive(self.C)'],
         'the actual positive parameter admission is retained')
    admission = compile_.body[3]
    need(isinstance(admission, ast.With) and len(admission.items) == len(admission.body) == 1
         and ast.unparse(admission.items[0]) == 'owned(Count.literal(2)) as (two,)'
         and isinstance(admission.body[0], ast.Expr)
         and isinstance(admission.body[0].value, ast.Call)
         and ast.unparse(admission.body[0].value.func) == 'need'
         and ast.unparse(admission.body[0].value.args[0]) ==
         'compare(self.p, two) >= 0 and compare(self.ell, self.p) < 0',
         'the source admits p>=2 and ell<p, never the invalid ell=p boundary')
    object_ = Object(machine, 'ProductPlan')
    A, p, ell, C = (variable(x) for x in ('A', 'p', 'ell', 'C'))
    machine.method(object_, '__init__', tuple(Count(x) for x in (A, p, ell, C)))
    # Precision differences are nonnegative under the recorded admission.
    original_subtract = machine.subtract
    def subtraction(left, right):
        difference = left.value-right.value
        if right.value == p and left.value == expected['Q']:
            return Count(difference)
        return original_subtract(left, right)
    machine.services['subtract'] = subtraction
    m = ell+1
    s = ceiling_log(12*m+2)+3
    Q = 2*p+2*m+s
    r, N = power_two(ell), 2*power_two(ell)
    records = power_two(A)*C
    expected = dict(m=m, r=r, N=N, records=records, gaussians=records*r,
                    fft_gaussians=records*N, Q=Q, recovery_shift=s, small=p+2,
                    wide=Q+2, word_width=Q+3, integer_width=2*p+ell+3,
                    lift=Q-p, half_shift=Q+1, product_shift=p+ell)
    machine.method(object_, 'compile', ())
    observed = {name: value.value for name, value in object_.fields['fields'].items()}
    need(observed == expected, 'all actual source plan expressions and normalization shifts')
    return dict(parameters=['A>=1', 'C>=1', 'p>=2', '1<=ell<p'],
                source_guard_observations=machine.parameter_assumptions,
                fields={name: value.data() for name, value in sorted(observed.items())})
