"""Source-specific representation adapter; keeps predecessor control/cleanup.

All source replacements are counted and pinned. No acceptance-result cache.
"""
import ast
import builtins
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import lanes


def authenticate():
    for row in json.loads((HERE / 'INPUTS.json').read_text()):
        data = (ROOT / row['path']).read_bytes()
        lanes.need(hashlib.sha256(data).hexdigest() == row['sha256'], 'authenticated input: ' + row['path'])


def rewrite(source, edits):
    for old, new, count in edits:
        lanes.need(source.count(old) == count, 'unique source adapter: ' + old)
        source = source.replace(old, new)
    return source


def predicate_labels(source):
    return [ast.dump(node.args[1]) for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == 'need' and len(node.args) == 2]


def functions(source, names, filename, namespace):
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    lanes.need({n.name for n in nodes} == set(names), 'complete source definitions')
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec', optimize=0), namespace)


def load(n, width, packed=True, value_width=None):
    authenticate()
    prefix = ROOT / 'research/dense-paired-collector'
    sources = types.ModuleType('sources')
    sources.__file__ = str(prefix / 'sources.py')
    exec(compile((prefix / 'sources.py').read_bytes(), sources.__file__, 'exec', optimize=0), sources.__dict__)
    source = sources.load()
    core = source['core']
    c = lanes.Context(n, width if value_width is None else value_width)
    if packed:
        with tarfile.open(prefix / 'inputs/pr3109.tar') as archive:
            core_text = archive.extractfile('model.py').read().decode()
        edits = [
            ('saved_source = tuple(source)', 'saved_source = source', 1),
            ('tuple(source) == saved_source', 'source == saved_source', 1),
            ('[(a >> g, b >> g) for a, b in source]', 'source.quotient(g)', 1),
            ('[(a % (1 << g), b % (1 << g)) for a, b in source]', 'source.residue(g)', 1),
            ('[(0, 0)]*len(source)', 'ZERO', 2),
            ('[(a+c, b+d) for (a, b), (c, d) in zip(decode(wide, width), narrow, strict=True)]', 'decode(wide, width) + narrow', 1),
            ('[(a ^ (x >> g), b ^ (y >> g)) for (a, b), (x, y) in zip(quotient, source, strict=True)]', 'quotient ^ source.quotient(g)', 1),
            ('[(a ^ (x % (1 << g)), b ^ (y % (1 << g))) for (a, b), (x, y) in zip(returned_residues, source, strict=True)]', 'returned_residues ^ source.residue(g)', 1),
        ]
        changed = rewrite(core_text, edits)
        lanes.need(predicate_labels(core_text) == predicate_labels(changed), "retained core predicates")
        core.ZERO = c.zero
        core.list = lambda v: v if isinstance(v, lanes.Vector) else builtins.list(v)
        core.lifted = lambda v, axes, inverse=False: lanes.transform(v, axes, inverse)
        core.linear_numerators = lambda v, axes, inverse=False: lanes.transform(v, axes, inverse, True)
        core.encode = lambda v, w: v.encode(w)
        core.decode = lambda v, w: v.decode(w)
        core.xor_words = lanes.xor_words
        def scaled(v, axes, inverse=False, guard=None):
            k = len(axes)
            g = k // 2 + 1 if guard is None else guard
            lanes.need(0 <= g <= k, 'finite scaled guard')
            return lanes.transform(v, axes, inverse, True).shift(g-k)
        core.scaled = scaled
        functions(changed, ['evaluate', 'inplace_block'], 'adapted_credited_core', core.__dict__)
    text = (prefix / 'model.py').read_text()
    text = rewrite(text, [('1 <= n <= 10 and width >= 8', '1 <= n <= 18 and width >= 8', 1)])
    if packed:
        text = rewrite(text, [
            ('[(0, 0)]*len(source)', 'ZERO', 2),
            ('[(0, 0)]*len(values)', 'ZERO', 1),
            ('[(0, 0)]*len(query)', 'ZERO', 2),
            ('[(a+c, b+d) for (a, b), (c, d) in zip(total, source, strict=True)]', 'total + source', 1),
            ('[(a+c, b+d) for (a, b), (c, d) in zip(promoted, sent, strict=True)]', 'promoted + sent', 1),
            ('[(a-c, b-d) for (a, b), (c, d) in zip(private, source, strict=True)]', 'private - source', 1),
        ])
    lanes.need(predicate_labels((prefix / 'model.py').read_text()) == predicate_labels(text), 'retained model predicates')
    module = types.ModuleType('packed_dense_model' if packed else 'original_dense_model')
    module.__file__ = str(prefix / 'model.py')
    previous = sys.modules.get('sources')
    sys.modules['sources'] = sources
    try:
        exec(compile(text, module.__file__, 'exec', optimize=0), module.__dict__)
    finally:
        if previous is None:
            del sys.modules['sources']
        else:
            sys.modules['sources'] = previous
    if packed:
        module.ZERO = c.zero
        module.list = core.list
        module.shift = lambda v, bits: v.shift(bits)
        module.character = lanes.character
        module.recipe_phase = lanes.recipe_phase
    return module, c
