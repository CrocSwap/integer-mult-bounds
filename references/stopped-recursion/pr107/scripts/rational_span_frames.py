"""Exact source/target-span cut certificates for mixed-point bit circuits.

The ambient form is 9I-J, a harmless rescaling of I-J/9. Integer primitive
row reduction represents rational subspaces without floating-point decisions.
"""
from functools import lru_cache
from hashlib import sha256
from math import gcd, lcm
from types import SimpleNamespace
import json

from certify import require
from exclusion_circuit import ExclusionCircuit


def primitive(row):
    g = 0
    for x in row:
        g = gcd(g,x)
    if not g:
        return None
    if next(x for x in row if x) < 0:
        g = -g
    return tuple(x//g for x in row)


@lru_cache(maxsize=65536)
def basis(rows):
    pivots = {}
    for row in rows:
        row = primitive(row)
        if row is None:
            continue
        for p,b in sorted(pivots.items()):
            if row[p]:
                row = primitive(tuple(b[p]*x-row[p]*y for x,y in zip(row,b)))
            if row is None:
                break
        if row is None:
            continue
        p = next(i for i,x in enumerate(row) if x)
        for q,b in list(pivots.items()):
            if b[p]:
                pivots[q] = primitive(tuple(row[p]*x-b[p]*y for x,y in zip(b,row)))
        pivots[p] = row
    return tuple(pivots[p] for p in sorted(pivots))


@lru_cache(maxsize=65536)
def join(A,B):
    return basis(tuple(sorted(set(A+B))))


def dot(a,b):
    return 9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)


@lru_cache(maxsize=65536)
def nondegenerate(U):
    return len(basis(tuple(tuple(dot(a,b) for b in U) for a in U))) == len(U)


@lru_cache(maxsize=65536)
def orthogonal(U,h):
    require(h != 9, 'Degenerate ambient form')
    rows = basis(tuple(tuple(9*x-sum(row) for x in row) for row in U))
    pivots = [next(i for i,x in enumerate(row) if x) for row in rows]
    answer = []
    for free in range(h):
        if free in pivots:
            continue
        scale = 1
        for row,p in zip(rows,pivots):
            scale = lcm(scale,row[p])
        vector = [0]*h
        vector[free] = scale
        for row,p in zip(rows,pivots):
            vector[p] = -row[free]*(scale//row[p])
        answer.append(primitive(vector))
    result = basis(tuple(answer))
    require(len(result) == h-len(U), 'Complement dimension mismatch')
    require(all(dot(a,b) == 0 for a in U for b in result), 'Not an orthogonal complement')
    return result


def contained(U,V):
    return join(U,V) == V


def spans(c):
    h = c.n
    S = {}
    T = {node:() for node in c.active}
    for node in c.active:
        if c.args[node]:
            a,b = c.args[node]
            S[node] = join(S[a],S[b])
        else:
            S[node] = (tuple(int(i in c.inputs[node-1]) for i in range(h)),)
    for target,node in zip(c.targets,c.outputs):
        T[node] = join(T[node],(tuple(int(i in target) for i in range(h)),))
    for node in reversed(c.active):
        if c.args[node]:
            for child in c.args[node]:
                T[child] = join(T[child],T[node])
    require(all(dot(a,b) == 0 for node in c.active for a in S[node] for b in T[node]),
            'A forbidden source-to-target path exists')
    return S,T


def compiled_frames(c,E):
    adapter = SimpleNamespace(inputs=c.inputs,args=c.args,active=set(c.active),
                              outputs=dict(zip(c.targets,c.outputs)),additions=c.additions)
    code = ExclusionCircuit.compile(adapter)
    h = c.n
    line = lambda t:(tuple(int(i in t) for i in range(h)),)
    forward = [()]*code['roles']
    for source,slot in code['sources'].items():
        forward[slot] = line(source)
    for node,ins,outs in code['gates']:
        for slot in set(ins+outs):
            require(contained(forward[slot],E[node]), 'Decreasing forward side edge')
            forward[slot] = E[node]
    for target,slot in code['outputs'].items():
        require(contained(forward[slot],orthogonal(line(target),h)), 'Wrong forward injection frame')
    reverse = [()]*code['roles']
    for target,slot in code['outputs'].items():
        reverse[slot] = line(target)
    for node,ins,outs in reversed(code['gates']):
        label = orthogonal(E[node],h)
        for slot in set(ins+outs):
            require(contained(reverse[slot],label), 'Decreasing reverse side edge')
            reverse[slot] = label
    for source,slot in code['sources'].items():
        require(reverse[slot] == orthogonal(line(source),h), 'Wrong reverse endpoint')
    return dict(roles=code['roles'],forward_nested=True,reverse_nested=True,
                source_and_injection_frames_checked=True)


def audit(c):
    S,T = spans(c)
    singular = {node for node in c.active if not nondegenerate(S[node])}
    dual = set()
    failures = []
    for node in c.active:
        if node in singular or (c.args[node] and any(parent in dual for parent in c.args[node])):
            dual.add(node)
            if not nondegenerate(T[node]):
                failures.append(node)
    hard = [node for node in c.active if len(S[node])+len(T[node]) > len(join(S[node],T[node]))]
    result = dict(h=c.n,roles=c.additions+len(c.outputs),singular_source_spans=len(singular),
                  forced_dual_nodes=len(dual),cut_failures=failures,
                  local_nonzero_source_target_intersections=len(hard),cut_certified=not failures)
    if not failures:
        E = {node:orthogonal(T[node],c.n) if node in dual else S[node] for node in c.active}
        require(all(nondegenerate(label) for label in E.values()), 'Degenerate selected frame')
        require(all(contained(S[node],E[node]) and contained(E[node],orthogonal(T[node],c.n))
                    for node in c.active), 'Frame misses source or target obligation')
        result['compiled'] = compiled_frames(c,E)
        encoded = json.dumps([(node,E[node]) for node in c.active],separators=(',',':')).encode()
        result['frame_sha256'] = sha256(encoded).hexdigest()
    return result
