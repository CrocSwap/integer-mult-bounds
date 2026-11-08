# SPDX-License-Identifier: Apache-2.0
"""Fail-closed interpretation of the retained straight-line numerical code.

This is not Python eval/exec. It has a finite syntax and service vocabulary;
unbounded tape loops are outside this interpreter and have written proofs.
"""
import ast
from dataclasses import dataclass

from algebra import Poly, as_poly, need


class Returned(Exception):
    def __init__(self, value):
        self.value = value


class Broke(Exception):
    pass


@dataclass
class Context:
    values: object


class Object:
    def __init__(self, machine, kind, **fields):
        self.machine, self.kind, self.fields = machine, kind, fields

    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        if name in self.machine.methods.get(self.kind, {}):
            return lambda *args: self.machine.method(self, name, args)
        if name in self.fields.get('fields', {}):
            return self.fields['fields'][name]
        raise ValueError('unrecognized object field '+self.kind+'.'+name)


class Machine:
    allowed_nodes = {
        ast.FunctionDef, ast.arguments, ast.arg, ast.Name, ast.Load, ast.Store,
        ast.Constant, ast.Expr, ast.Assign, ast.AugAssign, ast.Return, ast.If,
        ast.With, ast.withitem, ast.Try, ast.ExceptHandler, ast.Raise,
        ast.Call, ast.Attribute, ast.Tuple, ast.List, ast.Dict, ast.Subscript,
        ast.UnaryOp, ast.Not, ast.USub, ast.BinOp, ast.Add, ast.Sub, ast.Mult,
        ast.Mod, ast.BoolOp, ast.And, ast.Or, ast.Compare, ast.Eq, ast.NotEq,
        ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn,
        ast.Starred, ast.GeneratorExp, ast.ListComp, ast.comprehension,
        ast.Slice, ast.IfExp, ast.For, ast.Break,
    }

    def __init__(self, services):
        self.services = dict(services)
        self.functions, self.methods = {}, {}
        self.executed = set()

    def register(self, text, functions=(), classes=None):
        tree = ast.parse(text)
        for top in tree.body:
            need(isinstance(top, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef))
                 or isinstance(top, ast.Expr)
                 and (isinstance(top.value, ast.Constant) and type(top.value.value) is str
                      or ast.unparse(top.value) == 'active()'),
                 'module bindings cannot silently replace a proved numerical service')
        found = {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
        for name in functions:
            node = found[name]
            need(isinstance(node, ast.FunctionDef), 'source function '+name)
            self.functions[name] = node
        for name in functions:
            self.validate(self.functions[name])
        for name, selected in (classes or {}).items():
            node = found[name]
            need(isinstance(node, ast.ClassDef), 'source class '+name)
            need(not node.bases and not node.keywords and not node.decorator_list,
                 'plain retained source numerical class')
            members = {n.name: n for n in node.body if isinstance(n, ast.FunctionDef)}
            if name in ('ProductPlan', 'TwiddlePlan'):
                getter = members.get('__getattr__')
                need(getter is not None and [arg.arg for arg in getter.args.args] == ['self', 'name']
                     and not getter.decorator_list and not getter.args.defaults
                     and [ast.unparse(item) for item in getter.body] == ['return self.fields[name]'],
                     'the actual plan field accessor is the declared finite role map')
            self.methods[name] = {}
            for method in selected:
                self.validate(members[method])
                self.methods[name][method] = members[method]

    def validate(self, node):
        local_names = {x.arg for x in node.args.args}
        for part in ast.walk(node):
            if isinstance(part, ast.Name) and isinstance(part.ctx, ast.Store):
                local_names.add(part.id)
        permitted_names = local_names | set(self.services) | set(self.functions) | {'BaseException'}
        methods = {'zero', 'close', 'copy', 'negated', 'multiply', 'complex_product',
                   'suspended', 'run', 'read', 'clear', 'multiply_small', 'add',
                   'increment', 'decrement', 'divide_small', 'keep', 'literal', 'product',
                   'dif', 'dit', 'pointwise'} | getattr(self, 'extra_methods', set())
        for part in ast.walk(node):
            need(type(part) in self.allowed_nodes, 'unsupported numerical AST syntax: '+type(part).__name__)
            if isinstance(part, ast.Call):
                need(not part.keywords, 'keyword calls are outside numerical vocabulary')
                if isinstance(part.func, ast.Name):
                    need(part.func.id in set(self.services) | set(self.functions),
                         'unknown numerical service even on an unexecuted path')
                elif isinstance(part.func, ast.Attribute):
                    need(part.func.attr in methods, 'unknown numerical method vocabulary')
                else:
                    raise ValueError('indirect numerical callable is outside vocabulary')
            if isinstance(part, ast.Name):
                need(part.id in permitted_names, 'unknown numerical name in source '+part.id)
            if isinstance(part, (ast.GeneratorExp, ast.ListComp)):
                need(len(part.generators) == 1 and not part.generators[0].ifs
                     and not part.generators[0].is_async, 'one finite tuple generator')
            if isinstance(part, ast.ExceptHandler):
                need(isinstance(part.type, ast.Name) and part.type.id == 'BaseException'
                     and part.name is None, 'cleanup-only exception vocabulary')
            if isinstance(part, ast.Raise):
                need(part.exc is None and part.cause is None, 'bare cleanup rethrow')
        args = node.args
        need(not args.posonlyargs and not args.kwonlyargs and args.vararg is None
             and args.kwarg is None and not node.decorator_list, 'fixed numerical function interface')

    def invoke(self, node, arguments):
        names = [x.arg for x in node.args.args]
        need(len(arguments) <= len(names), 'numerical call arity')
        if len(arguments) < len(names):
            missing = len(names)-len(arguments)
            need(missing <= len(node.args.defaults), 'numerical default arity')
            arguments = (*arguments, *(self.expression(n, {}) for n in node.args.defaults[-missing:]))
        environment = dict(zip(names, arguments))
        self.executed.add(node.name)
        try:
            self.statements(node.body, environment)
        except Returned as result:
            return result.value
        return None

    def function(self, name, arguments):
        need(name in self.functions, 'unregistered source numerical function '+name)
        return self.invoke(self.functions[name], arguments)

    def method(self, object_, name, arguments):
        return self.invoke(self.methods[object_.kind][name], (object_, *arguments))

    def expression(self, node, environment):
        if isinstance(node, ast.Constant):
            need(node.value is None or type(node.value) in (str, int, bool), 'literal numerical type')
            return node.value
        if isinstance(node, ast.Name):
            if node.id in environment:
                return environment[node.id]
            if node.id in self.services:
                return self.services[node.id]
            if node.id in self.functions:
                return lambda *args: self.function(node.id, args)
            raise ValueError('unknown numerical name '+node.id)
        if isinstance(node, ast.Attribute):
            value = self.expression(node.value, environment)
            if isinstance(value, Object):
                return value.get(node.attr)
            need(hasattr(value, 'source_attribute'), 'untyped numerical attribute')
            return value.source_attribute(node.attr)
        if isinstance(node, (ast.Tuple, ast.List)):
            values = []
            for n in node.elts:
                if isinstance(n, ast.Starred):
                    extra = self.expression(n.value, environment)
                    need(type(extra) in (tuple, list), 'finite tuple-role expansion')
                    values.extend(extra)
                else:
                    values.append(self.expression(n, environment))
            return tuple(values) if isinstance(node, ast.Tuple) else values
        if isinstance(node, ast.Dict):
            result = {}
            for key, value in zip(node.keys, node.values):
                key = self.expression(key, environment)
                self.container_index(result, key)
                result[key] = self.expression(value, environment)
            return result
        if isinstance(node, ast.Subscript):
            collection, index = self.expression(node.value, environment), self.expression(node.slice, environment)
            self.container_index(collection, index)
            return collection[index]
        if isinstance(node, ast.Slice):
            values = [self.expression(value, environment) if value is not None else None
                      for value in (node.lower, node.upper, node.step)]
            need(all(value is None or type(value) is int for value in values), 'finite control-role slice')
            return slice(*values)
        if isinstance(node, ast.IfExp):
            return self.expression(node.body if self.control_bool(self.expression(node.test, environment)) else node.orelse,
                                   environment)
        if isinstance(node, ast.Call):
            function = self.expression(node.func, environment)
            arguments = []
            for argument in node.args:
                if isinstance(argument, ast.Starred):
                    arguments.extend(self.expression(argument.value, environment))
                else:
                    arguments.append(self.expression(argument, environment))
            need(callable(function), 'callable numerical service')
            if function is bool:
                need(len(arguments) == 1, 'one explicit finite boolean argument')
                return self.control_bool(arguments[0])
            return function(*arguments)
        if isinstance(node, ast.UnaryOp):
            value = self.expression(node.operand, environment)
            if isinstance(node.op, ast.Not):
                return not self.control_bool(value)
            if isinstance(node.op, ast.USub):
                return -value
        if isinstance(node, ast.BinOp):
            left, right = self.expression(node.left, environment), self.expression(node.right, environment)
            if isinstance(node.op, ast.Add):
                return left+right
            if isinstance(node.op, ast.Sub):
                return left-right
            if isinstance(node.op, ast.Mult):
                return left*right
            if isinstance(node.op, ast.Mod):
                need(type(left) is int and type(right) is int and right > 0, 'finite control residue')
                return left % right
        if isinstance(node, ast.BoolOp):
            result = isinstance(node.op, ast.And)
            for n in node.values:
                value = self.expression(n, environment)
                value = self.control_bool(value)
                result = result and value if isinstance(node.op, ast.And) else result or value
                if isinstance(node.op, ast.And) and not result or isinstance(node.op, ast.Or) and result:
                    break
            return result
        if isinstance(node, ast.Compare):
            values = [self.expression(n, environment) for n in (node.left, *node.comparators)]
            result = True
            for left, op, right in zip(values, node.ops, values[1:]):
                test = self.control_compare(left, op, right)
                need(type(test) is bool, 'concrete finite comparison')
                result = result and test
            return result
        if isinstance(node, (ast.GeneratorExp, ast.ListComp)):
            loop = node.generators[0]
            values = self.expression(loop.iter, environment)
            need(type(values) in (tuple, list), 'finite numerical tuple iteration')
            result = []
            for value in values:
                local = dict(environment)
                self.assign(loop.target, value, local)
                result.append(self.expression(node.elt, local))
            return tuple(result) if isinstance(node, ast.GeneratorExp) else result
        raise ValueError('unhandled numerical AST expression '+type(node).__name__)

    def assign(self, target, value, environment):
        if isinstance(target, ast.Name):
            environment[target.id] = value
        elif isinstance(target, (ast.Tuple, ast.List)):
            need(len(target.elts) == len(value), 'exact numerical destructuring')
            for name, item in zip(target.elts, value):
                self.assign(name, item, environment)
        elif isinstance(target, ast.Attribute):
            object_ = self.expression(target.value, environment)
            need(isinstance(object_, Object), 'owned object field assignment')
            object_.fields[target.attr] = value
        elif isinstance(target, ast.Subscript):
            collection = self.expression(target.value, environment)
            need(type(collection) in (dict, list), 'finite numerical role container')
            index = self.expression(target.slice, environment)
            self.container_index(collection, index)
            collection[index] = value
        else:
            raise ValueError('unsupported numerical assignment')

    def container_index(self, collection, index):
        if type(collection) is dict:
            need(type(index) in (str, int, bool, type(None)),
                 'dictionary keys require concrete finite roles, never symbolic numerical equality')
        else:
            need(type(collection) in (tuple, list) and type(index) in (int, slice),
                 'sequence indices require concrete finite roles')

    def control_bool(self, value):
        need(type(value) is bool, 'concrete finite sign/control branch')
        return value

    def control_compare(self, left, operator, right):
        """Never infer unequal numerical values from unequal formal objects.

        Source equality is a runtime predicate, unlike certificate equality
        of two polynomial DAGs. Symbolic refinements must prove a predicate
        in a subclass or reject it; Python dataclass equality is not a proof.
        """
        literals = (bool, int, str, type(None))
        if isinstance(operator, (ast.Is, ast.IsNot)):
            # The source uses singleton None for an optional owner and bool
            # for the finite sign type. Other object identity is not modeled.
            admissible = (left is None or right is None
                          or type(left) is bool and type(right) is bool
                          or left is bool and right is bool)
            need(admissible, 'unproved symbolic source identity predicate')
            same = left is right
            return same if isinstance(operator, ast.Is) else not same
        if isinstance(operator, (ast.In, ast.NotIn)):
            need(type(left) in literals and type(right) in (tuple, list, dict)
                 and all(type(value) in literals for value in right),
                 'finite literal membership predicate')
            member = left in right
            return member if isinstance(operator, ast.In) else not member
        need(type(left) in literals and type(right) in literals,
             'unproved symbolic source comparison')
        if isinstance(operator, ast.Eq): return left == right
        if isinstance(operator, ast.NotEq): return left != right
        need(type(left) is type(right) is int, 'integer finite control order')
        if isinstance(operator, ast.Lt): return left < right
        if isinstance(operator, ast.LtE): return left <= right
        if isinstance(operator, ast.Gt): return left > right
        if isinstance(operator, ast.GtE): return left >= right
        raise ValueError('unknown comparison')

    def statements(self, nodes, environment):
        for node in nodes:
            if isinstance(node, ast.Assign):
                value = self.expression(node.value, environment)
                for target in node.targets:
                    self.assign(target, value, environment)
            elif isinstance(node, ast.AugAssign):
                need(isinstance(node.op, ast.Add), 'finite diagnostic increment only')
                self.assign(node.target, self.expression(node.target, environment)+self.expression(node.value, environment), environment)
            elif isinstance(node, ast.Expr):
                self.expression(node.value, environment)
            elif isinstance(node, ast.Return):
                raise Returned(self.expression(node.value, environment) if node.value else None)
            elif isinstance(node, ast.If):
                condition = self.expression(node.test, environment)
                condition = self.control_bool(condition)
                self.statements(node.body if condition else node.orelse, environment)
            elif isinstance(node, ast.With):
                contexts = []
                for item in node.items:
                    context = self.expression(item.context_expr, environment)
                    need(isinstance(context, Context), 'known numerical context')
                    contexts.append(context)
                    if item.optional_vars:
                        self.assign(item.optional_vars, context.values, environment)
                self.statements(node.body, environment)
            elif isinstance(node, ast.Try):
                # Successful-path refinement. Exceptional cleanup is separately
                # source-pinned and is not claimed as a numerical return.
                try:
                    self.statements(node.body, environment)
                    self.statements(node.orelse, environment)
                finally:
                    self.statements(node.finalbody, environment)
            elif isinstance(node, ast.For):
                values = self.expression(node.iter, environment)
                need(type(values) in (tuple, list) and len(values) <= 32 and not node.orelse,
                     'bounded fixed-role numerical loop')
                for value in values:
                    self.assign(node.target, value, environment)
                    self.statements(node.body, environment)
            elif isinstance(node, ast.Break):
                raise Broke()
            else:
                raise ValueError('unhandled numerical AST statement '+type(node).__name__)
