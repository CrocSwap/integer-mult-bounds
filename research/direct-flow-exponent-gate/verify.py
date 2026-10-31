#!/usr/bin/env python3
"""Source-bound finite full-flow identities and exact limiting-coefficient gates.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
The written proof, not finite enumeration, establishes asymptotic convergence.
"""
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from certificate import inventory, numerical_certificate, coefficient
from intervals import I, need, log_integer, exp_interval, rank_power
from complement import full_certificate, series_controls


def authenticate():
    result = {}
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            raw = (ROOT/row['path']).read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            need(digest == row['sha256'], 'source hash: '+row['path'])
            blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            need(blob == row['git_blob'], 'source Git blob: '+row['path'])
            result[row['path']] = digest
    return result


def convolution(left, right):
    out = Counter()
    for x, nx in left.items():
        for y, ny in right.items():
            out[x*y] += nx*ny
    return out


def powers(law, depth):
    result = [Counter({1:1})]
    for _ in range(depth):
        result.append(convolution(result[-1],law))
    return result


def mirror_flow(targets, paid, n, fault=None):
    m, kmin = max(targets), min(targets)
    cap, depth = n//m, 0
    while kmin**(depth+1) <= cap:
        depth += 1
    need(0 <= depth <= 3, 'finite fixture depth')
    tp, pp = powers(targets,depth), powers(paid,depth)
    top, leaf, boundary, inner, units = (Counter() for _ in range(5))
    for c,nc in tp[depth].items():
        if c <= cap:
            for k,wk in targets.items():
                top[c*k] += nc*wk
    for c,nc in pp[depth].items():
        if c <= cap:
            for r,pr in paid.items():
                if fault != 'terminal-cut' or c*r <= cap:
                    leaf[c*r] += nc*pr
    for h in range(depth+1):
        for z,weight in convolution(pp[depth-h],tp[h]).items():
            if z <= cap:
                units[z] += weight
    for h in range(depth):
        if fault == 'omit-target-depth' and h > 0:
            continue
        for z,weight in convolution(pp[depth-1-h],tp[h]).items():
            for r,pr in paid.items():
                for k,wk in targets.items():
                    value = weight*(1 if fault == 'omit-multiplicity' else pr*wk)
                    if r*z <= cap < k*z:
                        inner[r*k*z] += value
                    elif k*z <= cap < r*z:
                        boundary[r*k*z] += value
    if fault == 'reverse-windows':
        inner,boundary = boundary,inner
    source = inner if fault == 'omit-top' else top+inner
    return source,leaf+boundary,boundary,leaf,units


def moment_exact(histogram, exponent):
    return sum(count*Q(rank)**exponent for rank,count in histogram.items())


def finite_checks(paid,targets):
    # Execute only the authenticated pinned implementation, in memory; no pyc reads.
    path = ROOT/'research/direct-mixed-flow/flow.py'
    namespace = {'__name__':'pinned_flow_source','__file__':str(path)}
    exec(compile(path.read_bytes(),str(path),'exec'),namespace)
    Flow = namespace['Flow']
    domains = [1,2,4,5,6,17,24,25,26,32,49,80,124,125,126,200,300,624]
    fixtures = [(targets,paid,121*cap+(cap % 3)*40) for cap in domains]
    fixtures += [({2:1,5:1},{1:2,4:1},n) for n in (5,10,20,39)]
    fixtures += [({2:4,3:1},{1:6,2:2},n) for n in (3,6,12,23)]
    digest = hashlib.sha256()
    identities = 0
    for ts,ps,n in fixtures:
        reference = Flow(ts,ps,n).merged()
        src,ext,bound,leaf,unit = mirror_flow(ts,ps,n)
        need(src == reference['sources'], 'all source histogram entries')
        need(ext == reference['exits'], 'all exit histogram entries')
        need(bound == reference['boundary_exits'], 'all boundary histogram entries')
        need(leaf+bound == ext, 'leaf boundary partition')
        for exponent in range(4):
            left = moment_exact(src,exponent)-moment_exact(ext,exponent)
            right = (moment_exact(ts,exponent)-moment_exact(ps,exponent))*moment_exact(unit,exponent)
            need(left == right,'all-potential telescoping')
            identities += 1
        serial = [n,sorted(src.items()),sorted(ext.items()),sorted(bound.items())]
        digest.update(json.dumps(serial,separators=(',',':')).encode())
    rejected = []
    for fault in ('terminal-cut','omit-target-depth','omit-multiplicity','reverse-windows','omit-top'):
        differs = False
        for ts,ps,n in fixtures:
            if mirror_flow(ts,ps,n,fault)[:3] != mirror_flow(ts,ps,n)[:3]:
                differs = True
                break
        need(differs,'undetected semantic fault '+fault)
        rejected.append(fault)
    return {'fixtures':len(fixtures),'potential_identities':identities,
            'full_histogram_sha256':digest.hexdigest(),'rejected':rejected}


def algebra_checks(paid,targets):
    checks = 0
    for alpha in (-1,0,1):
        a,b = moment_exact(paid,alpha),moment_exact(targets,alpha)
        for s in (alpha+1,alpha+2,alpha+3):
            source=boundary=Q(0)
            for r,pr in paid.items():
                for k,wk in targets.items():
                    if k > r:
                        source += pr*wk*(Q(r)**alpha*Q(k)**s-Q(k)**alpha*Q(r)**s)
                    elif r > k:
                        boundary += pr*wk*(Q(k)**alpha*Q(r)**s-Q(r)**alpha*Q(k)**s)
            need(source-boundary == a*moment_exact(targets,s)-b*moment_exact(paid,s),
                 'finite coefficient conservation')
            checks += 1
    return checks


def controls(paid,targets):
    count = 0
    for thunk in (lambda:I(2,1), lambda:I(1)/I(-1,1),
                  lambda:log_integer(0),lambda:exp_interval(I(6)),
                  lambda:coefficient(paid,targets,I(1),I(1))):
        try:
            thunk()
        except ValueError:
            count += 1
        else:
            raise ValueError('invalid interval or gap accepted')
    # Independent elementary enclosures against exact rationals.
    need(log_integer(1).contains(0),'log one')
    need(exp_interval(I(0)).contains(1),'exp zero')
    for rank in (1,2,3,5,8,48,121):
        need(rank_power(rank,I(0)).contains(1),'rank power zero')
        need(rank_power(rank,I(1)).contains(rank),'rank power one')
    return count


def main():
    sources = authenticate()
    paid,targets,m = inventory()
    need(m == 121 and len(paid)==len(targets)==9,'fixed source inventory domain')
    need(moment_exact(targets,1)-moment_exact(paid,1)==608,'raw rank-one surplus')
    result = {'status':'PASS_DIRECT_FLOW_FULL_LIMIT',
              'finite':finite_checks(paid,targets),
              'algebraic_identities':algebra_checks(paid,targets),
              'boundary_rejections':controls(paid,targets),
              'numerical':numerical_certificate(),
              'complete_complement':full_certificate(),
              'series_controls':series_controls(),'sources':sources}
    result['package_sha256'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(HERE.iterdir()) if p.is_file()}
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
