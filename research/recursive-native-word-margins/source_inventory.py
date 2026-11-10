"""Pinned source/proof boundary, not a general range analyzer or kernel.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import ast
from copy import deepcopy
from hashlib import sha256
import json
import tarfile
from margin_sources import ROOT, need

ARCHIVE = 'research/physical-ordinary-interchange/inputs/pr2809.tar'
VENDOR = 'inputs/pr2753/predecessor/vendor/'
MODULE_SECTIONS = {
    'macro_machine.py': '4,5,7', 'macro_binding.py': '4,6,7',
    'residual_blocks.py': '5', 'role_parking.py': '7',
    'inputs/pr2769/codec.py': '7',
    'inputs/pr2753/layout.py': '5', 'inputs/pr2753/trace.py': '4,5',
    'inputs/pr2753/peel.py': '5', 'inputs/pr2753/packet_engine.py': '7',
    'inputs/pr2753/recursive_call.py': '7',
    'inputs/pr2753/stream_runner.py': '5,6',
    'inputs/pr2753/linear_sign.py': '6',
    **{VENDOR+name+'.py': section for name, section in (
        ('words', '3,6'), ('controller', '4,6'), ('children', '4'),
        ('numeric', '4,5,6'), ('records', '4,7'), ('directory', '4,6'),
        ('cardinality', '6'), ('routes', '6'), ('matrices', '6'),
        ('forms', '6'), ('stream', '6'), ('bitstream', '6'),
        ('packet', '4,7'),
        ('selection', 'separate unbounded cardinalities'),
        ('episode', 'separate unbounded cardinalities'),
    )},
}
PHYSICAL = ('physical_words.py', 'ordinary.py', 'session.py', 'encoded.py')
OPERATIONS = {'divmod', 'times_small', 'shift_add_bit', 'increment_in_place',
              'subtract_exact', 'add', 'plus', 'literal', 'load', 'prepare',
              'read_word', 'append_word', 'copy_word'}


def functions(tree):
    result = {}
    def walk(node, prefix=''):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    need(name not in result, 'unique lexical function')
                    result[name] = child
                walk(child, name + '.')
            else:
                walk(child, prefix)
    walk(tree)
    return result


def describe(raw):
    result = {}
    for name, node in functions(ast.parse(raw)).items():
        calls = []
        for item in ast.walk(node):
            if not isinstance(item, ast.Call):
                continue
            stem = item.func.attr if isinstance(item.func, ast.Attribute) else (
                   item.func.id if isinstance(item.func, ast.Name) else '')
            if stem in OPERATIONS:
                calls.append(dict(line=item.lineno, operation=stem, expression=ast.unparse(item)))
        result[name] = dict(ast_sha256=sha256(ast.dump(node, include_attributes=False).encode()).hexdigest(),
                            numerical_calls=sorted(calls, key=lambda x:(x['line'], x['expression'])))
    return dict(sha256=sha256(raw).hexdigest(), functions=result)


def bindings(sources):
    """Exact critical producer geometry; all other named functions are pinned."""
    facts = {}
    layout = functions(ast.parse(sources['inputs/pr2753/layout.py']))
    assignments = {ast.unparse(n.targets[0]): ast.unparse(n.value)
                   for n in ast.walk(layout['Layout.__init__'])
                   if isinstance(n, ast.Assign) and len(n.targets)==1}
    expected = {'self.core': 'geometry.raw.times_small(geometry.columns, geometry.plan.dimension)',
                'remaining': 'geometry.raw.subtract_exact(parent_size, self.core)',
                'self.extra': 'geometry.raw.times_small(remaining, 2)',
                'self.total': 'geometry.raw.times_small(parent_size, 2)'}
    need(all(assignments.get(k)==v for k,v in expected.items()), 'actual compact/core/extra/total expressions')
    facts['core_and_gap'] = expected
    physical = [ast.unparse(n.value) for n in ast.walk(layout['Layout.physical'])
                if isinstance(n, ast.Return)]
    need(set(physical) == {'self.geometry.index.copy(position)', 'self.geometry.plus(position, self.extra)'},
         'actual piecewise original-gap embedding')
    facts['physical_returns'] = physical
    ordinary = functions(ast.parse(sources['physical/ordinary.py']))
    calls = [ast.unparse(n) for n in ast.walk(ordinary['Ordinary.fitted']) if isinstance(n, ast.Call)]
    for expression in ('Count(plan[\'body\'])', 'indices.prepare(index_maximum)',
                       'indices.load(plan[\'body\'])', 'indices.zero()',
                       'self.runtime.arena.prepare(modulus)',
                       'self.runtime.indices.prepare(index_maximum)'):
        need(expression in calls, 'actual root template producer: ' + expression)
    facts['root_template_calls'] = [x for x in calls if '.prepare(' in x or x=='indices.load(plan[\'body\'])']
    copies = [n for n in ast.walk(ordinary['unit_program']) if isinstance(n, ast.For)]
    need(len(copies)==1 and ast.unparse(copies[0].iter)=='(size, ring.one, depth)',
         'unit ROOT encoded fields')
    facts['unit_root_fields'] = ast.unparse(copies[0].iter)
    machine = functions(ast.parse(sources['macro_machine.py']))
    returns = [ast.unparse(n.value) for n in ast.walk(machine['Machine.prepare_child'])
               if isinstance(n, ast.Return)]
    need(returns == ['(self.arena.copy(self.context.ring.modulus), self.indices.copy(event.width), self.indices.copy(event.depth))'],
         'actual unchanged-template child grants')
    facts['child_grants'] = returns[0]
    return facts


def sources():
    with tarfile.open(ROOT/ARCHIVE, 'r:') as archive:
        result = {name: archive.extractfile(name).read() for name in MODULE_SECTIONS}
    for name in PHYSICAL:
        result['physical/'+name] = (ROOT/'research/physical-ordinary-interchange'/name).read_bytes()
    return result


def build():
    raw = sources()
    modules = {name: dict(section=MODULE_SECTIONS.get(name, '3,7; encoded setup separate'),
                          **describe(body)) for name, body in raw.items()}
    divisors = []
    for module, record in modules.items():
        for function, info in record['functions'].items():
            for call in info['numerical_calls']:
                if call['operation']=='divmod':
                    divisors.append(dict(module=module, function=function, **call))
    return dict(schema_version=1,
                methodology='Pinned functions and named-module numerical calls bind the written proof; no generic program analysis',
                structural_facts=bindings(raw), divisors=divisors, modules=modules,
                excluded_execution=['ToyBinding', 'fixture constructors', 'host fixed-source compilation',
                                    'unbounded Count/cardinality operations', 'unrelated native variants'])


def canonical(record):
    return json.dumps(record, sort_keys=True, separators=(',', ':'), allow_nan=False)


def verify(record, actual):
    need(canonical(record)==canonical(actual), 'complete typed source-range inventory')


def controls(record):
    labels = []
    for label, mutate in (
        ('omit_module', lambda r:r['modules'].pop('inputs/pr2753/layout.py')),
        ('omit_divisor', lambda r:r['divisors'].pop()),
        ('alter_grant_extent', lambda r:r['structural_facts'].__setitem__('child_grants', 'shortened child template')),
    ):
        changed = deepcopy(record)
        mutate(changed)
        try:
            verify(changed, record)
        except ValueError:
            labels.append(label)
        else:
            raise ValueError('inventory mutation accepted')
    raw = sources()
    for label, name, before, after in (
        ('third_gap_copy', 'inputs/pr2753/layout.py', b'geometry.raw.times_small(remaining,2)', b'geometry.raw.times_small(remaining,3)'),
        ('wrong_root_bank_maximum', 'physical/ordinary.py', b'self.runtime.indices.prepare(index_maximum)', b'self.runtime.indices.prepare(modulus)'),
    ):
        need(before in raw[name], 'exact mutation anchor')
        changed = dict(raw)
        changed[name] = raw[name].replace(before, after, 1)
        try:
            bindings(changed)
        except ValueError:
            labels.append(label)
        else:
            raise ValueError('critical producer mutation accepted')
    return labels
