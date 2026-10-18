#!/usr/bin/env python3
"""One-site absorption with reciprocal character-controlled stream charts.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
Gaussian arithmetic/context/cut extraction adapted from Ross Richardson's PR3254,
head897bfb42; authenticated physical interpreter is Gonzalo-Mier/PR3199 lineage.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import itertools
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

def flat(a):
    return [v for row in a for v in row]

def trace(a):
    total = Z
    for i in range(len(a)):
        total = add(total, a[i][i])
    return total

def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    return value

def rank_two_minor(a):
    for rows in itertools.combinations(range(len(a)), 2):
        for cols in itertools.combinations(range(len(a[0])), 2):
            i, j = rows
            k, l = cols
            d = sub(mul(a[i][k], a[j][l]), mul(a[i][l], a[j][k]))
            if d != Z:
                return {'rows': list(rows), 'columns': list(cols), 'determinant': d}
    return None

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

def controls():
    # Valid character-controlled conjugate charts may select different streams.
    a = identity(); a[0][0] = (F(0), F(1))
    b = identity(); b[6][6] = (F(0), F(1))
    require(rank_two_minor(defect(a)) is None and rank_two_minor(defect(b)) is None,
            'character-dependent valid charts must be accepted separately')
    p = identity(); p[0][0] = (F(0),F(1)); p[1][0] = (F(-1),F(1))
    require(rank_two_minor(defect(p)) is None, 'oblique projector rank control')
    two = product(a,b)
    require(rank_two_minor(defect(two)) is not None, 'two-stream defect rejection')
    require(product(a,inverse(a)) == identity(), 'exact inverse control')
    # These noncommuting matrices detect a reversed chronological inverse.
    u=identity(); u[1][0]=O
    v=identity(); v[0][1]=O
    require(product(inverse(u),inverse(v)) != inverse(product(u,v)), 'inverse-order sensitivity')
    return ['distinct-character-projectors-accepted','oblique-projector-accepted',
            'two-stream-defect-rejected','inverse-completion','noncommuting-inverse-order']


def run():
    authenticate()
    old,ctx=source_context()
    original={j:list(v) for j,v in ctx['residual'].items()}
    moved={j:list(v) for j,v in original.items()}
    moved[10].remove(16); moved[12].append(16)
    require(old.orthonormal(moved[10]) and old.orthonormal(moved[12]), 'candidate orthonormality')
    characters=[0,16,33554432,33554448]
    witnesses={};receiver={};baseline_controls=0
    for x in characters:
        target=[[(F(a),F(b)) for a,b in row] for row in old.baseline_target(x)]
        ops,sites=operations(old,ctx,moved,x)
        needed,overlay=requirements(ops,sites,target)
        require(overlay == old.replay(ctx,moved,x,old.stage_blocks(ctx['template'])), 'source overlay agreement')
        base_ops,base_sites=operations(old,ctx,original,x)
        unchanged,baseline=requirements(base_ops,base_sites,target)
        require(baseline==target, 'full baseline exact-phase equality')
        for j in range(20):
            require(rank_two_minor(defect(unchanged[j])) is None, 'unchanged single-child control')
            baseline_controls+=1
            if x==33554448:
                minor=rank_two_minor(defect(needed[j]))
                require(minor is not None, 'character-controlled one-site question unresolved at site '+str(j))
                witnesses[j]={'character':x,'required_matrix':needed[j],**minor}
        receiver[x]=needed[12]
    # Bind the displayed receiver proof to complete literal matrices.
    for x in characters:
        expected=identity()
        if x & 16:
            expected[6][4]=(F(-1),F(1));expected[6][6]=(F(0),F(1))
        if x & 33554432:
            expected[0][0]=(F(0),F(1))
        require(receiver[x]==expected, 'displayed receiver formula '+str(x))
    require(witnesses[12]['rows']==[0,6] and witnesses[12]['columns']==[0,4]
            and witnesses[12]['determinant']==(F(0),F(-2)), 'displayed receiver minor')
    return encode({'status':'PASS_IDLE_CHARACTER_CONTROLLED_ABSORPTION',
        'base':BASE,'owner_replica':0,'port':0,
        'transfer':{'axis':16,'donor':10,'receiver':12,'old_ranks':[48,48],'candidate_ranks':[47,49]},
        't740_rows_authenticated':old.TOTAL_ROWS,'sites':20,'characters_tested':characters,
        'rank_two_witnesses':witnesses,'receiver_samples':receiver,
        'baseline_controls':baseline_controls,'synthetic_controls':controls(),
        'contract':'R(x)=L(x) diag(z(x),1,...,1) L(x)^-1; arbitrary invertible Fourier-character-dependent stream charts and nonzero eigenvalues; every other event fixed.',
        'coverage':'Four exact characters, all twenty literal cuts, all eight arbitrary input columns; witnesses refute full-domain necessary condition.',
        'new_kappa':None})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args();result=run()
    if a.output:
        require(not a.output.exists(), 'exclusive new output');a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:require(result==json.loads((PACKAGE/'RESULT.json').read_text()), 'committed result mismatch')
    print('PASS_IDLE_CHARACTER_CONTROLLED_ABSORPTION sites=20 characters=4 no_new_kappa')

if __name__=='__main__':main()
