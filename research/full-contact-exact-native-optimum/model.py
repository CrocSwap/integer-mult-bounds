"""Execute the pinned original model builder, without importing a solver.
JoyboyBrian, with OpenAI Codex assistance. Apache-2.0.
"""
import ast
import collections
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/carried-warp-frame-intervals'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Changed source: ' + row['path'])


def module(name):
    # Compile authenticated source bytes directly: no stale .pyc reads.
    import types
    result = types.ModuleType(name)
    result.__file__ = str(SOURCE / (name + '.py'))
    sys.modules[name] = result
    exec(compile(Path(result.__file__).read_bytes(), result.__file__, 'exec'), result.__dict__)
    return result


def load():
    authenticate()
    frame = module('frame_dag')
    replay = module('replay')
    verifier = module('verify')
    return frame, replay, verifier.source()


def build(direction, frame, replay, retained):
    need(direction in ('forward', 'backward'), 'Unknown orientation')
    path = SOURCE / 'discovery/search.py'
    tree = ast.parse(path.read_text())
    def target(node, name):
        return isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
    start = [i for i,n in enumerate(tree.body) if target(n, 'retained')]
    end = [i for i,n in enumerate(tree.body) if target(n, 'starts')]
    need(len(start) == len(end) == 1 and start[0] < end[0], 'Unique complete builder boundaries')
    statements = tree.body[start[0]:end[0]]
    # Only bind the requested source word to the original builder's forward slot.
    # The backward replay adapter preserves the original replay direction contract.
    source = {'canonical': retained['canonical'], 'programs': {'forward': retained['programs'][direction]}}
    ns = dict(vars(frame))
    ns.update(collections=collections, Decimal=Decimal, localcontext=localcontext,
              verify=SimpleNamespace(source=lambda: source),
              replay=lambda c,p: replay.replay(c,p,direction == 'backward'),
              highspy=SimpleNamespace(kHighsInf=math.inf, HighsLp=SimpleNamespace,
                  ObjSense=SimpleNamespace(kMaximize='maximize'),
                  HighsVarType=SimpleNamespace(kInteger='integer')))
    exec(compile(ast.Module(body=statements, type_ignores=[]), str(path), 'exec'), ns)
    lp = ns['lp']
    need(lp.num_col_ == len(ns['initial']) and lp.num_row_ == len(ns['rows']), 'Full model dimensions')
    need(lp.col_lower_ == [0.0]*lp.num_col_ and lp.col_upper_ == [1.0]*lp.num_col_, 'Original unit bounds')
    need(lp.integrality_ == ['integer']*lp.num_col_, 'Original MIP is integral')
    ns['builder_lines'] = [statements[0].lineno, statements[-1].end_lineno]
    return ns
