#!/usr/bin/env python3
"""One-site phase absorption, exact Gaussian-rational caller matrices.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
The retained source interpreter is authenticated reuse, not an independent oracle.
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


def span_two_minor(a, b):
    av, bv = flat(a), flat(b)
    pivot = next((i for i, v in enumerate(av) if v != Z), None)
    if pivot is None:
        return None
    for j in range(len(av)):
        d = sub(mul(av[pivot], bv[j]), mul(av[j], bv[pivot]))
        if d != Z:
            return {'flat_positions': [pivot, j], 'determinant': d}
    return None


def obstruction(samples):
    """Exact necessary/sufficient fixed-projector criterion on supplied samples."""
    first = None
    for x, a in samples:
        d = defect(a)
        minor = rank_two_minor(d)
        if minor:
            return {'kind': 'rank-at-least-two', 'characters': [x], **minor}
        if all(v == Z for v in flat(d)):
            continue
        t = trace(d)
        if t == Z:
            return {'kind': 'nonzero-rank-one-nilpotent', 'characters': [x]}
        if add(O, t) == Z:
            return {'kind': 'zero-phase-eigenvalue', 'characters': [x]}
        # A rank-one matrix obeys D^2=tr(D)D; nonzero trace scales it to an idempotent.
        require(product(d, d) == [[mul(t, v) for v in row] for row in d], 'rank-one identity')
        if first is None:
            first = x, d
        else:
            witness = span_two_minor(first[1], d)
            if witness:
                return {'kind': 'inconsistent-projector', 'characters': [first[0], x], **witness}
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
    p = [[Z for _ in range(8)] for _ in range(8)]
    p[0][0] = p[1][0] = O
    require(product(p,p) == p, 'non-coordinate projector positive')
    def phase(p, f):
        return [[add(O if i == j else Z, mul(f,v)) for j,v in enumerate(row)] for i,row in enumerate(p)]
    good = [(0,identity()),(1,phase(p,(F(-1),F(1)))),(2,phase(p,(F(-2),F(0))))]
    require(obstruction(good) is None, 'valid oblique projector rejected')
    other = [[Z for _ in range(8)] for _ in range(8)]
    other[2][2] = O
    bad = [good[0],good[1],(2,phase(other,(F(-2),F(0))))]
    require(all(obstruction([sample]) is None for sample in bad), 'per-character rank-one positive controls')
    require(obstruction(bad)['kind'] == 'inconsistent-projector', 'cross-character defect missed')
    nil = identity()
    nil[0][1] = O
    require(obstruction([(1,nil)])['kind'] == 'nonzero-rank-one-nilpotent', 'nilpotent cannot be phase projector')
    two = identity()
    two[0][0] = two[1][1] = (F(0),F(1))
    require(obstruction([(1,two)])['kind'] == 'rank-at-least-two', 'rank-two defect missed')
    return ['oblique-projector-accepted','per-character-rank-one-is-insufficient','nilpotent-rejected','rank-two-rejected']


def run():
    authenticate()
    old, ctx = source_context()
    original = {j:list(v) for j,v in ctx['residual'].items()}
    moved = {j:list(v) for j,v in original.items()}
    moved[10].remove(16)
    moved[12].append(16)
    require(old.orthonormal(moved[10]) and old.orthonormal(moved[12]), 'candidate axis orthonormality')
    samples = {j:[] for j in range(20)}
    witnesses = {}
    tested = []
    baseline_controls = 0
    for x in [0,16]+[1<<k for k in range(73) if k != 4]:
        ops, sites = operations(old,ctx,moved,x)
        target = [[(F(a),F(b)) for a,b in row] for row in old.baseline_target(x)]
        needed, overlay = requirements(ops,sites,target)
        require(overlay == old.replay(ctx,moved,x,old.stage_blocks(ctx['template'])), 'retained interpreter overlay agreement')
        require(old.replay(ctx,original,x,old.stage_blocks(ctx['template'])) == old.baseline_target(x), 'pinned baseline equality')
        tested.append(x)
        # An unchanged literal child always satisfies the common-projector criterion.
        base_ops, base_sites = operations(old,ctx,original,x)
        baseline_needed, baseline = requirements(base_ops,base_sites,target)
        require(baseline == target, 'baseline chronological matrix equality')
        for j in range(20):
            if x == 0:
                require(needed[j] == identity(), 'zero-character normalization')
            samples[j].append((x,needed[j]))
            if j not in witnesses:
                reason = obstruction(samples[j])
                if reason:
                    reason['required_matrices'] = [m for c,m in samples[j] if c in reason['characters']]
                    witnesses[j] = reason
            require(obstruction([(x,baseline_needed[j])]) is None, 'baseline single-child positive control')
            baseline_controls += 1
        if len(witnesses) == 20:
            break
    require(len(witnesses) == 20, 'one-site obligation unresolved')
    full_baseline = {}
    for j in range(20):
        full_baseline[j] = []
    # Cross-character baseline controls are distinct from per-character rank tests.
    for x in tested:
        ops, sites = operations(old,ctx,original,x)
        target = [[(F(a),F(b)) for a,b in row] for row in old.baseline_target(x)]
        needed,_ = requirements(ops,sites,target)
        for j in range(20):
            full_baseline[j].append((x,needed[j]))
    require(all(obstruction(v) is None for v in full_baseline.values()), 'unchanged child simultaneous positive controls')
    kinds = {}
    for w in witnesses.values():
        kinds[w['kind']] = kinds.get(w['kind'],0)+1
    return encode({'status':'PASS_IDLE_SINGLE_CHILD_ABSORPTION','base':BASE,'owner_replica':0,'port':0,'transfer':{'axis':16,'donor':10,'receiver':12,'old_ranks':[48,48],'candidate_ranks':[47,49]},'t740_rows_authenticated':old.TOTAL_ROWS,'sites':20,'characters_tested':tested,'witness_kinds':kinds,'witnesses':witnesses,'baseline_single_character_controls':baseline_controls,'baseline_simultaneous_controls':20,'synthetic_controls':controls(),'contract':'One completed Fourier-diagonal phase on one stream, with fixed scalar stream-only encoder/decoder (tensor address identity); arbitrary nonzero scalar eigenvalue function; all other gates fixed.','new_kappa':None})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        require(not args.output.exists(), 'exclusive new output')
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        require(result == json.loads((PACKAGE/'RESULT.json').read_text()), 'committed result mismatch')
    print('PASS_IDLE_SINGLE_CHILD_ABSORPTION sites=20 characters='+str(len(result['characters_tested']))+' no_new_kappa')


if __name__ == '__main__':
    main()
