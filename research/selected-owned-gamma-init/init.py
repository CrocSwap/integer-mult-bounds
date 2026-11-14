"""Uniform six-Gamma typed zero and full-capacity raw retirement.

Apache-2.0. Prepared with OpenAI Codex assistance. Python only constructs
finite transition tables; execution uses local tape tests/writes/unit moves.
"""
from pathlib import Path
import hashlib
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.pycache_prefix = str(HERE / '_unwritten_cache')
if Path(sys.pycache_prefix).exists():
    raise ValueError('bytecode isolation path exists')

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def pinned(path, digest):
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('frozen dependency drift: ' + str(path))

pinned(HERE/'inputs/tape_graph.py', '7d3cee3e79ba5fe410e1a6b5f4cf6a2fbe5e274f838b798cd8860344ff258b54')
pinned(HERE/'inputs/machine.py', 'ffe2677bb5b82932873cb08b05f890a1218070215ebe670a0b05079518e8baee')
D = load('typed_init_dispatch', HERE/'inputs/tape_graph.py')
DONOR, TARGET, GUIDE = 1, 2, 3
TAPES = 4

def primitive(g, name, arity, after, stages=None):
    stages = {} if stages is None else stages
    if name == 'CLEAR':
        if arity != 1:
            raise ValueError('CLEAR has exactly one owned operand')
        done = g.rewind(1, after)
        loop = g.state('raw-clear-all-capacity')
        g.add(loop, done, tests=((1, '|'),))
        for bit in '01':
            g.add(loop, loop, tests=((1, bit),), writes=((1, '0'),), moves=((1, 1),))
        entry = g.jump(loop, ((1, 1),))
        stages['entry'] = entry
        stages['return'] = after
        return entry
    if name != 'INIT' or arity != 2:
        raise ValueError('INIT requires distinct donor and inactive owned target')
    done = g.rewind(DONOR, g.rewind(TARGET, g.rewind(GUIDE, after)))
    data = g.state('init-full-zero-data')
    g.add(data, done, tests=((DONOR, '|'), (TARGET, '|')))
    for bit in '01':
        for old in '01':
            g.add(data, data, tests=((DONOR, bit), (TARGET, old)),
                  writes=((TARGET, '0'),), moves=((DONOR, 1), (TARGET, 1)))
    nxt = data
    for field in range(5, -1, -1):
        prefix = g.state('init-Gamma-prefix')
        pop = g.state('init-Gamma-pop')
        suffix = g.state('init-Gamma-suffix')
        for old in '01':
            g.add(prefix, prefix, tests=((DONOR, '0'), (TARGET, old)),
                  writes=((TARGET, '0'), (GUIDE, '1')),
                  moves=((DONOR, 1), (TARGET, 1), (GUIDE, 1)))
            g.add(prefix, pop, tests=((DONOR, '1'), (TARGET, old)),
                  writes=((TARGET, '1'),),
                  moves=((DONOR, 1), (TARGET, 1), (GUIDE, -1)))
        g.add(pop, nxt, tests=((GUIDE, '^'),), moves=((GUIDE, 1),))
        g.add(pop, suffix, tests=((GUIDE, '1'),),
              writes=((GUIDE, '_'),), moves=((GUIDE, -1),))
        for bit in '01':
            for old in '01':
                g.add(suffix, pop, tests=((DONOR, bit), (TARGET, old)),
                      writes=((TARGET, bit),), moves=((DONOR, 1), (TARGET, 1)))
        nxt = prefix
    entry = g.jump(nxt, ((DONOR, 1), (TARGET, 1), (GUIDE, 1)))
    stages['entry'] = entry
    stages['data'] = data
    stages['return'] = after
    return entry

def compile_home(events, owners, productive_count):
    return D.compile_graph(events, owners, primitive=primitive,
                           productive_count=productive_count)
