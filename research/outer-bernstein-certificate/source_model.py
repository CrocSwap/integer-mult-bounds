"""Interpret only the pinned outer engine's arithmetic expression syntax.

This never imports or executes predecessor Python. Source assertions are replaced
by coefficient identities/positivity obligations. Exact source hashes are checked
by verify.py before this parser is used.
Gareth Davidson / OpenAI Codex, Apache-2.0.
"""
import ast
from fractions import Fraction as F

from algebra import RationalPoly, require


class Model:
    def __init__(self, source, inputs):
        self.env = dict(inputs)
        self.symbolic = isinstance(inputs['bit_saving'], RationalPoly)
        self.branches = {}
        self.identities = {}
        self.margin_gaps = {}
        tree = ast.parse(source)
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        require(len(functions) == 1 and functions[0].name == 'assembly', 'source function')
        function = functions[0]
        require([a.arg for a in function.args.args] ==
                ['bit_saving', 'complex_saving', 'bridge', 'kappa', 'eta', 'beta'],
                'source signature')
        assertions = 0
        updates = 0
        returns = 0
        for node in function.body:
            if isinstance(node, ast.Assign):
                value = self.expression(node.value)
                for target in node.targets:
                    self.assign(target, value)
            elif isinstance(node, ast.Expr):
                call = node.value
                require(isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                        and isinstance(call.func.value, ast.Name)
                        and call.func.value.id == 'slacks' and call.func.attr == 'update'
                        and len(call.args) == 1 and not call.keywords, 'unexpected source update')
                new = self.expression(call.args[0])
                require(not set(new).intersection(self.env['slacks']), 'duplicate slack')
                self.env['slacks'].update(new)
                updates += 1
            elif isinstance(node, ast.Assert):
                # First two assertions are cardinality and positivity, discharged
                # explicitly by the complete certificate inventory in verify.py.
                if assertions >= 2:
                    terms = node.test.values if isinstance(node.test, ast.BoolOp) else [node.test]
                    if isinstance(node.test, ast.BoolOp):
                        require(isinstance(node.test.op, ast.And), 'unexpected assertion connective')
                    for term in terms:
                        require(isinstance(term, ast.Compare) and len(term.ops) == 1 and
                                isinstance(term.ops[0], ast.Eq), 'unexpected source identity')
                        gap = self.expression(term.left) - self.expression(term.comparators[0])
                        self.identities[ast.unparse(term)] = gap
                assertions += 1
            elif isinstance(node, ast.Return):
                returns += 1  # Returned formatting does not add arithmetic obligations.
            else:
                raise ValueError('unsupported source statement: ' + type(node).__name__)
        require(assertions == 5 and updates == 1 and returns == 1, 'source statement inventory')
        require(len(self.env['slacks']) == 47 and len(self.env['margins']) == 7,
                'source row inventory')
        require(len(self.branches) == 2 and len(self.identities) == 4 and
                len(self.margin_gaps) == 7, 'source proof inventory')

    def assign(self, target, value):
        if isinstance(target, ast.Name):
            require(target.id not in self.env, 'reassigned source name')
            self.env[target.id] = value
        elif isinstance(target, ast.Tuple):
            require(isinstance(value, tuple) and len(value) == len(target.elts), 'tuple binding')
            for name, item in zip(target.elts, value):
                self.assign(name, item)
        else:
            raise ValueError('unsupported assignment')

    def expression(self, node):
        if isinstance(node, ast.Constant):
            require(type(node.value) in (int, str), 'nonexact source literal')
            return F(node.value) if type(node.value) is int else node.value
        if isinstance(node, ast.Name):
            require(node.id in self.env, 'unknown source name')
            return self.env[node.id]
        if isinstance(node, ast.Tuple):
            return tuple(self.expression(n) for n in node.elts)
        if isinstance(node, ast.Subscript):
            return self.expression(node.value)[self.expression(node.slice)]
        if isinstance(node, ast.BinOp):
            x, y = self.expression(node.left), self.expression(node.right)
            if isinstance(node.op, ast.Add):
                return x + y
            if isinstance(node.op, ast.Sub):
                return x - y
            if isinstance(node.op, ast.Mult):
                return x * y
            if isinstance(node.op, ast.Div):
                return x / y
        if isinstance(node, ast.DictComp):
            require(len(node.generators) == 1, 'comprehension arity')
            gen = node.generators[0]
            require(not gen.ifs and not gen.is_async and isinstance(gen.target, ast.Tuple)
                    and len(gen.target.elts) == 2, 'comprehension shape')
            names = [x.id for x in gen.target.elts]
            require(not any(n in self.env for n in names), 'comprehension shadows source name')
            result = {}
            for pair in self.expression(gen.iter):
                self.env.update(zip(names, pair))
                key, value = self.expression(node.key), self.expression(node.value)
                require(key not in result, 'duplicate generated row')
                result[key] = value
            for name in names:
                del self.env[name]
            return result
        if isinstance(node, ast.Call):
            return self.call(node)
        raise ValueError('unsupported source expression: ' + type(node).__name__)

    def call(self, node):
        if isinstance(node.func, ast.Attribute):
            obj = self.expression(node.func.value)
            require(type(obj) is dict and not node.args and not node.keywords,
                    'unexpected attribute call')
            require(node.func.attr in ('items', 'values'), 'unexpected dictionary method')
            return list(obj.items()) if node.func.attr == 'items' else list(obj.values())
        require(isinstance(node.func, ast.Name), 'unexpected callable')
        name = node.func.id
        if name == 'dict':
            require(not node.args and all(k.arg is not None for k in node.keywords),
                    'unexpected dictionary syntax')
            result = {k.arg: self.expression(k.value) for k in node.keywords}
            require(len(result) == len(node.keywords), 'duplicate dictionary key')
            return result
        require(not node.keywords, 'unexpected call keywords')
        args = [self.expression(n) for n in node.args]
        if name == 'Q':
            require(len(args) in (1, 2), 'fraction arity')
            return args[0] if len(args) == 1 else args[0] / args[1]
        if name in ('min', 'max') and len(args) == 2:
            x, y = args
            # The certified ordering chooses the second branch in both source
            # calls. Numeric witness execution also verifies that actual order.
            gap = y - x if name == 'max' else x - y
            self.branches[ast.unparse(node)] = gap
            if not self.symbolic:
                require(gap > 0, 'branch ordering fails')
            return y
        if name == 'min' and len(args) == 1:
            require(args[0] == list(self.env['margins'].values()), 'unexpected minimum list')
            minimum = self.env['minimum']
            self.margin_gaps = {key: value - minimum for key, value in self.env['margins'].items()}
            if not self.symbolic:
                require(min(args[0]) == minimum, 'minimum margin mismatch')
            return minimum
        raise ValueError('unsupported source call: ' + name)
