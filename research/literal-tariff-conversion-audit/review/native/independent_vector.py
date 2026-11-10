"""Independent static pass-count cross-review of the pinned compact ADD.

No audit.py import, table execution, timing sample, or full-word execution.
Prepared by the native-physical research agent with OpenAI assistance.
The universal path-multiplicity proof and lifecycle accounting are in REVIEW.md.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

PINS = {
    'kernel/compact_tables.py': 'fe8a28fd523ebb7ec78dce4ba0855b3070a6cbff470602cd62f8d3ff445e0f0a',
    'kernel/machine.py': 'ec597bce13275003ff30e4be481c936401826c1d4af642b55eec0c410774d1df',
    'kernel/exact_builder.py': '654e9734ef80a9394807ca508543b1bc164afb5768d23d0e5a88c790d2f13bac',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(*vectors):
    return tuple(map(sum, zip(*vectors)))


def mul(n, vector):
    return tuple(n * x for x in vector)


def physical_cost(tree, method, direction=None):
    """Count literal hardware calls on the valid nonblank method path."""
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == 'CodedPort')
    method_node = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                       and n.name == method)
    emitter = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                   and n.name == 'emit')

    def expression(node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in ('read', 'write', 'move'):
                owner = ast.unparse(node.func.value)
                need(owner in ('t', 'tape', 'self.tape'), 'unexpected hardware owner')
                return {'read': (1, 0, 0), 'write': (0, 1, 0), 'move': (0, 0, 1)}[node.func.attr]
            if isinstance(node.func, ast.Name) and node.func.id == 'emit':
                return statements(emitter.body)
        values = [expression(n) for n in ast.iter_child_nodes(node)]
        return add((0, 0, 0), *values)

    def statements(nodes):
        out = (0, 0, 0)
        for node in nodes:
            if isinstance(node, ast.If):
                test = ast.unparse(node.test)
                if test == 'direction == 1':
                    need(direction in (-1, 1), 'move direction supplied')
                    selected = node.body if direction == 1 else node.orelse
                elif test in ('t.read() == BLANK', 't.read() == LEFT'):
                    selected = node.orelse  # valid nonblank, noncrossing body
                else:
                    raise ValueError(('unexpected physical condition', test))
                item = add(expression(node.test), statements(selected))
            elif isinstance(node, ast.For):
                if isinstance(node.iter, ast.Call):
                    need(ast.unparse(node.iter.func) == 'range', 'literal loop')
                    count = ast.literal_eval(node.iter.args[0])
                else:
                    count = len(ast.literal_eval(node.iter))
                item = mul(count, statements(node.body))
            else:
                item = expression(node)
            out = add(out, item)
        return out

    return statements(method_node.body)


def literal_paths(text):
    tree = ast.parse(text)
    compile_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'compile_compact')
    helpers = {n.name: n for n in compile_node.body if isinstance(n, ast.FunctionDef)}
    loop = next(n for n in compile_node.body if isinstance(n, ast.While)
                and ast.unparse(n.test) == 'b.pending')
    node = next(n for n in loop.body if isinstance(n, ast.If))
    states = {}
    while isinstance(node, ast.If):
        need(isinstance(node.test, ast.Compare)
             and ast.unparse(node.test.left) == 'tag', 'state dispatch')
        states[ast.literal_eval(node.test.comparators[0])] = node.body
        node = node.orelse[0] if node.orelse else None

    def statements(nodes):
        # logical coordinates: branches, writes, coded moves, gotos
        out = (0, 0, 0, 0)
        for node in nodes:
            item = (0, 0, 0, 0)
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                name = ast.unparse(call.func)
                if name == 'branch':
                    item = (1, 0, 0, 0)
                elif name == 'b.emit':
                    need(ast.literal_eval(call.args[0]) == 'write', 'ordinary write')
                    item = (0, 1, 0, 0)
                elif name == 'move':
                    item = (0, 0, abs(ast.literal_eval(call.args[1])), 0)
                elif name == 'go':
                    item = (0, 0, 0, 1)
                elif name in ('publics', 'hstep'):
                    if name == 'hstep':
                        need(ast.literal_eval(call.args[7]) is None, 'ordinary hstep')
                    item = statements(helpers[name].body)
                else:
                    need(name == 'need', ('unexpected constructor call', name))
            elif isinstance(node, ast.If):
                if ast.unparse(node.test) == 'remaining is None':
                    item = statements(node.body)
                else:
                    # These conditionals only add cases to a construction-time map.
                    # Reject silently omitted row generation in either arm.
                    forbidden = {'branch', 'b.emit', 'move', 'go', 'publics', 'hstep'}
                    need(not any(isinstance(n, ast.Call) and ast.unparse(n.func) in forbidden
                                 for n in ast.walk(node)), 'conditional contains emitted rows')
            else:
                need(isinstance(node, (ast.Assign, ast.AnnAssign, ast.Nonlocal)),
                     ('unexpected ordinary statement', type(node).__name__))
            out = add(out, item)
        return out

    paths = {
        'initialization_and_rewind': ('init', 'init-y', 'init-zero', 'reset-back', 'reset-public'),
        'horner_and_rewind': ('hscan', 'hy', 'hn', 'hdigit', 'reset-back', 'reset-public'),
        'offset_and_rewind': ('offset', 'offset-digit', 'rewind'),
        'odd_residue_and_rewind': ('residue', 'res-digit', 'rewind'),
        'quotient': ('emit', 'emit-y', 'emit-n', 'emit-digit'),
        'whole_reverse': ('global-bits', 'global-public'),
        'installation': ('install', 'install-symbol'),
    }
    return {name: {'states': tags, 'logical': add((0, 0, 0, 0),
            *(statements(states[tag]) for tag in tags))} for name, tags in paths.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    files = ('kernel/compact_tables.py', 'kernel/machine.py', 'kernel/exact_builder.py')
    source = {name: (args.package / name).read_bytes() for name in files}
    need(all(hashlib.sha256(value).hexdigest() == PINS[name]
             for name, value in source.items()), 'reviewed immutable source bytes')
    machine = ast.parse(source['kernel/machine.py'])
    primitive = {name: physical_cost(machine, name) for name in ('read', 'write')}
    primitive['move'] = physical_cost(machine, 'move', 1)
    need(primitive['move'] == physical_cost(machine, 'move', -1), 'both move directions')
    paths = literal_paths(source['kernel/compact_tables.py'].decode())

    def convert(logical):
        branches, writes, moves, gotos = logical
        hardware = add(mul(branches, primitive['read']), mul(writes, primitive['write']),
                       mul(moves, primitive['move']))
        return hardware + (sum(logical),)

    for item in paths.values():
        item['physical_and_rows'] = convert(item['logical'])
    # These slopes follow from the explicit origin/retire proof in REVIEW.md.
    # The physical code width is read from the literal write loop above.
    code_bits = primitive['write'][1]
    paths['two_long_head_returns'] = {'physical_and_rows': (2*code_bits, 0, 2*code_bits, 0)}
    paths['two_private_retirements'] = {'physical_and_rows': (4*code_bits, 2*code_bits, 4*code_bits, 0)}
    horner = paths['horner_and_rewind']['physical_and_rows']
    residue = paths['odd_residue_and_rewind']['physical_and_rows']
    base = add((0, 0, 0, 0), *(v['physical_and_rows'] for k, v in paths.items()
                               if k not in ('horner_and_rewind', 'odd_residue_and_rewind')))
    source_text = source['kernel/compact_tables.py'].decode()
    old = "move(3,1);move(2,1);publics();go(('emit',kk,z,parity))"
    new = "move(3,1);publics();go(('emit',kk,z,parity))"
    need(source_text.count(old) == 1, 'unique quotient mutation')
    mutant = literal_paths(source_text.replace(old, new))['quotient']['logical']
    actual = paths['quotient']['physical_and_rows']
    short = convert(mutant)
    need(actual != short and actual[2] > short[2], 'fourth-move failure detection')
    result = {
        'status': 'PASS_STATIC_INDEPENDENT_VECTOR',
        'method': 'AST count of literal ordinary paths; universal multiplicities/lifecycle proved separately',
        'sources': {k: hashlib.sha256(v).hexdigest() for k, v in source.items()},
        'primitive_physical': primitive, 'phases': paths,
        'derived_vector': {'constant': base, 'L': horner, 'delta': residue},
        'raw_sums': {'constant': sum(base[:3]), 'L': sum(horner[:3]), 'delta': sum(residue[:3])},
        'raw_plus_rows_sums': {'constant': sum(base), 'L': sum(horner), 'delta': sum(residue)},
        'negative_control': {'missing_numerator_move': short, 'actual_quotient': actual},
        'audit_py_imported': False, 'numeric_table_execution': False, 'whole_word_execution': False,
        'credit': 'Native-physical agent; OpenAI-assisted independent pass-count review, shared immutable source',
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(payload)
    print(payload)


if __name__ == '__main__':
    main()
