#!/usr/bin/env python3
"""Exact cut extraction for arbitrary-address reciprocal phase similarity.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
Gaussian arithmetic/context/cut extraction adapted from Ross Richardson's PR3254,
head897bfb42; authenticated physical interpreter is Gonzalo-Mier/PR3199 lineage.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import types
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "463113d675af7410ac91d53a4fed51ec6494eb9a"
Z = (F(0), F(0))
O = (F(1), F(0))


def require(ok, why):
    if not ok:
        raise ValueError(why)

def add(a, b):
    return a[0]+b[0], a[1]+b[1]

def neg(a):
    return -a[0], -a[1]

def sub(a, b):
    return add(a, neg(b))

def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]

def div(a, b):
    d = b[0]*b[0]+b[1]*b[1]
    require(d != 0, 'Gaussian zero divisor')
    return (a[0]*b[0]+a[1]*b[1])/d, (a[1]*b[0]-a[0]*b[1])/d

def identity(n=8):
    return [[O if i == j else Z for j in range(n)] for i in range(n)]

def product(a, b):
    out = [[Z for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, v in enumerate(row):
            if v != Z:
                for j, w in enumerate(b[k]):
                    if w != Z:
                        out[i][j] = add(out[i][j], mul(v, w))
    return out

def inverse(a):
    n = len(a)
    rows = [list(row)+unit for row, unit in zip(a, identity(n), strict=True)]
    for j in range(n):
        p = next((i for i in range(j, n) if rows[i][j] != Z), None)
        require(p is not None, 'singular matrix')
        rows[j], rows[p] = rows[p], rows[j]
        pivot = rows[j][j]
        rows[j] = [div(v, pivot) for v in rows[j]]
        for i in range(n):
            if i != j and rows[i][j] != Z:
                c = rows[i][j]
                rows[i] = [sub(v, mul(c, w)) for v, w in zip(rows[i], rows[j], strict=True)]
    require([r[:n] for r in rows] == identity(n), 'inverse elimination')
    return [r[n:] for r in rows]

def defect(a):
    return [[sub(v, O if i == j else Z) for j, v in enumerate(row)] for i, row in enumerate(a)]

def authenticate():
    sources = json.loads((PACKAGE/'SOURCES.json').read_text())
    require(sources['base_commit'] == BASE, 'base pin')
    for row in sources['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT/row['path']
        require(path.is_file() and not path.is_symlink(), 'missing/linked input '+row['path'])
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256 '+row['path'])
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw, usedforsecurity=False).hexdigest()
        require(blob == row['git_blob'], 'source Git blob '+row['path'])

def source_context():
    path = ROOT/'research/idle-star-paired-axis-census/verify.py'
    raw = path.read_bytes()
    pins = json.loads((PACKAGE/'SOURCES.json').read_text())['files']
    pin = next(r for r in pins if r['path'] == path.relative_to(ROOT).as_posix())
    require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'executed interpreter source bytes')
    module = types.ModuleType('retained_source_exact_bytes')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec', optimize=0), module.__dict__)
    module.authenticate()
    vendor = module.PACKAGE/'vendor'
    base = module.decode(module.read_bytes(vendor/'BASE-FILL.json.gz'))['rows']
    journal = module.decode(module.read_bytes(vendor/'EXCHANGE.json'))
    rows = module.project_all_ports(base, module.journal_edits(base, journal))
    allocation = ROOT/'research/rank7-joint-endframes/allocation'
    order0 = module.decode(module.read_bytes(allocation/'ORDER.json'))
    order = [[s, r+74*c] for s, r in order0 for c in range(10)]
    dispatch0 = module.decode(module.read_bytes(allocation/'DISPATCH.json'))
    dispatch = {(s,r):t for s,r,t in dispatch0}
    providers = module.decode(module.read_bytes(vendor/'PROVIDERS.json'))
    plan = module.decode(module.read_bytes(allocation/'vendor/PLAN.json.gz'))
    template = module.decode(module.read_bytes(allocation/'vendor/TEMPLATE.json.gz'))
    recipes = module.decode(module.read_bytes(ROOT/'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'))['recipes']
    ctx = module.prepare_port(0, rows[0], order, dispatch, providers, plan, template, recipes)
    require([len(ctx['residual'][j]) for j in (10,12)] == [48,48], 'concrete original ranks')
    require(16 in ctx['residual'][10], 'concrete donor axis')
    return module, ctx

def phase_matrix(stream, power):
    out = identity()
    out[stream][stream] = [(O), (F(0),F(1)), (F(-1),F(0)), (F(0),F(-1))][power % 4]
    return out

def operations(old, ctx, residual, character):
    out, sites = [], {}
    blocks = old.stage_blocks(ctx['template'])
    for time, (stage, replica) in enumerate(ctx['order']):
        for stream, axes in ctx['hosts'].get(time, ()):
            power = sum(old.parity(character, v) for v in axes)
            if power % 4:
                out.append(phase_matrix(stream, power))
        if replica != 0:
            continue
        for event in blocks[stage]:
            if event['kind'] != 'idle_cover_sweep':
                matrix = old.identity()
                old.run_data_event(matrix, event, ctx, residual, character)
                out.append([[(F(a),F(b)) for a,b in row] for row in matrix])
            else:
                for side, child in enumerate(event['child_indices']):
                    stream = 2*event['pair']+side
                    require(child not in sites, 'unique residual child site')
                    sites[child] = len(out)
                    out.append(phase_matrix(stream, sum(old.parity(character,v) for v in residual[child])))
                    out.append(phase_matrix(stream, 2*old.parity(character,ctx['recipe']['idle_children'][child]['translation_after'])))
    require(set(sites) == set(range(20)), 'complete twenty-site coverage')
    return out, sites

def requirements(ops, sites, target):
    prefixes = [identity()]
    for g in ops:
        prefixes.append(product(g, prefixes[-1]))
    suffixes = [None]*(len(ops)+1)
    suffixes[-1] = identity()
    for k in range(len(ops)-1,-1,-1):
        suffixes[k] = product(suffixes[k+1], ops[k])
    result = {}
    for child, k in sites.items():
        a, b = prefixes[k], suffixes[k+1]
        require(product(b,product(ops[k],a)) == prefixes[-1], 'literal cut reconstruction')
        r = product(inverse(b), product(target,inverse(a)))
        require(product(b,product(r,a)) == target, 'required replacement identity')
        result[child] = r
    return result, prefixes[-1]
