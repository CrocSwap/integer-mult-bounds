"""Cancel exact updates after scalar and native-map normalization.

This constructor extends the source compressor for the fixed PR4610 word.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Credit Cao Yifan, Cinna Davis, ahrazzle, Chrisbryan17, and retained authors.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rid(r):
    return r[1] if r[0] == 'L' else 632 + r[1]


def product(a, b):
    out = list(a)
    for x in b:
        if out and out[-1] == -x:
            out.pop()
        else:
            out.append(x)
    return tuple(out)


def inverse(w):
    return tuple(-x for x in reversed(w))


def simplify(program):
    gauges = [()] * 633
    scales = [Q(1)] * 633
    gates = []
    changes = {}
    pairs = []
    for i, e in enumerate(program):
        if e[0] == 'warp':
            r = rid(e[1])
            gauges[r] = product((e[2],), gauges[r])
        elif e[0] == 'scalar':
            g = e[1]
            r = rid(g[1])
            if g[0] == 'scale':
                scales[r] *= Q(*g[2:4])
            elif g[0] == 'add':
                s = rid(g[2])
                w = product(inverse(gauges[r]), gauges[s])
                factor = scales[s] / scales[r]
                c = Q(*g[3:5]) * factor
                for j in range(len(gates) - 1, -1, -1):
                    old = gates[j]
                    if old is None:
                        continue
                    if old[0] == 'barrier':
                        if r in old[1] or s in old[1]:
                            break
                        continue
                    _, old_i, a, b, old_w, old_c = old
                    if a == s or b == r:
                        break
                    if (a, b, old_w) == (r, s, w):
                        c += old_c
                        changes[old_i] = None
                        gates[j] = None
                        pairs.append([old_i, i])
                        break
                if c:
                    v = c / factor
                    if v != Q(*g[3:5]):
                        changes[i] = ['scalar', [*g[:3], v.numerator, v.denominator], e[2]]
                    gates.append(('add', i, r, s, w, c))
                else:
                    changes[i] = None
            elif g[0] in ('clear', 'copy'):
                touched = {r}
                if g[0] == 'copy':
                    touched.add(rid(g[2]))
                gates.append(('barrier', touched))
            else:
                raise ValueError(g)
    kept = [(i, changes.get(i, e)) for i, e in enumerate(program) if changes.get(i, e) is not None]
    # A warp and its inverse can be removed if no remaining scalar contact
    # reads or writes that field between them. Scales commute with warps.
    stack = [[] for _ in range(633)]
    remove = set()
    for i, e in kept:
        if e[0] == 'warp':
            r = rid(e[1])
            if stack[r] and stack[r][-1][1] == -e[2]:
                old, _ = stack[r].pop()
                remove.update((old, i))
            else:
                stack[r].append((i, e[2]))
        elif e[0] == 'scalar' and e[1][0] != 'scale':
            for a in e[1][1:]:
                if isinstance(a, list):
                    stack[rid(a)] = []
    return [(i, e) for i, e in kept if i not in remove], pairs, sorted(remove)


def construct():
    predecessor = load(ROOT / 'research/cao-trace-retiming-20261023/construct.py', 'gauge_source_compressor')
    original, prior, _ = predecessor.construct()
    programs, patches = {}, {}
    for direction, program in prior['programs'].items():
        indexed, pairs, warps = simplify(program)
        programs[direction] = [event for _, event in indexed]
        patches[direction] = {'combined_event_pairs': pairs, 'removed_warp_events': warps}
    return original, prior, {'canonical': prior['canonical'], 'programs': programs}, patches
