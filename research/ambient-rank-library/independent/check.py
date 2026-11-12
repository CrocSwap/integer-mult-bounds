"""Independent positive-source/brute-replication review of ambient rank libraries.

Expected answers use no author verifier, oracle, compressed products, or
signed subtraction census. Source absence is tested on lattice points and
paid paths; least replication is found by literal positive-integer search.
"""
from collections import Counter
from hashlib import sha1, sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from math import factorial, prod
from pathlib import Path
import json
import sys
import types

CODE_SHA = '4c709f98239782ba938aa70ee22c0cdf7204fbdac8a5c444e71adb568e06bbfe'
PROOF_SHA = 'a7d75efc8f4c38ca231324f99ce92b0d45df91cbd5ef89c93224700bf740b0c7'
DOMAINS = (
    (3, ((2,1),(3,1)), ((1,1),), 24),
    (6, ((2,1),(3,1)), ((1,1),), 35),
    (4, ((3,2),), ((2,2),), 18),
    (9, ((3,1),(4,1)), ((2,1),), 48),
    (7, ((3,1),(5,1)), ((2,1),), 40),
    (8, ((2,2),(4,1)), ((1,3),), 24),
    (5, ((2,3),), ((1,1),), 32),
    (8, ((3,1),(4,1)), ((1,1),(2,1)), 48),
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def points(total, dimension):
    if dimension == 1:
        yield (total,)
    else:
        for first in range(total+1):
            for tail in points(total-first, dimension-1):
                yield (first,)+tail


def fresh_census(A, target, paid, n):
    kmin = target[0][0]
    g = 0
    while A*kmin**(g+1) <= n:
        g += 1
    sites = tuple(r for r, count in paid for _ in range(count))
    source, units, checked_slots = Counter(), 0, 0
    for h in range(g+1):
        for indices in product(range(len(sites)), repeat=h):
            rho = prod(sites[j] for j in indices)
            for alpha in points(g-h, len(target)):
                column = prod(k**a for (k,_), a in zip(target, alpha))
                if A*rho*column > n:
                    continue
                u = factorial(g-h)//prod(factorial(a) for a in alpha)
                u *= prod(w**a for (_,w), a in zip(target, alpha))
                units += u
                for k, w in target:
                    checked_slots += u*w
                    if not h or A*(rho//sites[indices[-1]])*column*k > n:
                        source[rho*column*k] += u*w
    cuts = tuple(prod(sites[j] for j in path)
                 for path in product(range(len(sites)), repeat=g+1))
    need(source and all(n < A*s <= target[-1][0]*n for s in source), 'fresh source band')
    need(all(0 < A*e <= (A-1)*n for e in cuts), 'exit contraction')
    return g, units, source, cuts, checked_slots


def direct_rows(A, target, paid, maximum):
    rows, flows = [None], {}
    trial_count = 0
    for n in range(1, maximum+1):
        if n < A:
            rows.append((1,1,n,0))
            continue
        flow = fresh_census(A,target,paid,n)
        g, unit_count, source, cuts, _ = flow
        constraints = [(n-s,count) for s,count in source.items() if s<n]
        constraints += [(e,1) for e in cuts]
        for a in range(1,50001):
            trial_count += 1
            if all(a*count % rows[e][1] == 0 for e,count in constraints):
                break
        else:
            raise ValueError('declared independent replication-search cap exceeded')
        leaves, units = 0, a*unit_count
        for e,count in constraints:
            copies, remainder = divmod(a*count,rows[e][1])
            need(remainder == 0,'exact independent copies')
            leaves += copies*rows[e][2]
            units += copies*rows[e][3]
        rows.append((a,a*sum(source.values()),leaves,units))
        flows[n] = flow
    return rows, flows, trial_count


def members(A,target,paid,maximum):
    C=maximum//A
    generators=sorted({r for alphabet in (target,paid) for r,_ in alphabet if r>=2})
    # Test each bounded integer by division into previously settled membership.
    yes=[False]*(C+1)
    if C:yes[1]=True
    for n in range(2,C+1):
        yes[n]=any(n%r==0 and yes[n//r] for r in generators)
    return tuple(n for n in range(1,C+1) if yes[n])


def check_domain(module, domain):
    A,target,paid,maximum=domain
    expected, flows, trials=direct_rows(A,target,paid,maximum)
    rule=module.Rule(A,target,paid)
    actual=module.compile_library(rule,maximum)
    got=[None]+[(r.replication,r.width,r.leaves,r.units) for r in actual.rows[1:]]
    need(got==expected,'positive-source/brute-replication row mismatch')
    limits=module.Limits();work=module.Work();gmax=module.height(rule,maximum)
    tt=module.product_tables(target,gmax,limits,work)
    pp=module.product_tables(paid,gmax+1,limits,work)
    for n,(g,u,source,cuts,_) in flows.items():
        census=module.census(rule,n,tt,pp,limits,work)
        need(census.height==g and census.units==u,'direct height/unit census')
        need(census.sources==tuple(sorted(source.items())),'positive fresh-source census')
        need(census.exits==tuple(sorted(Counter(cuts).items())),'distinct-cut census')
    env=module.envelope(rule,maximum)
    exponent=0
    while 2**exponent < target[0][0]:exponent+=1
    tau=A*exponent
    need(env['plateau_visit_bound']==tau,'honest ambient plateau constant')
    need((A-1)**tau*target[0][0]<A**tau,'exact plateau contraction')
    need((A-1)**env['D']*maximum < A**(env['D']+1),'exact depth contraction')
    gammas=members(A,target,paid,maximum)
    divisor=1
    for gamma in gammas:
        source=fresh_census(A,target,paid,A*gamma)[2]
        divisor*=sum(source.values())**tau
    need(all(divisor%row[1]==0 for row in expected[1:]),'all-prime plateau divisor')
    depth=[0]*(maximum+1)
    visit={gamma:[0]*(maximum+1) for gamma in gammas}
    for n in range(A,maximum+1):
        _,_,source,cuts,_=flows[n]
        children=[n-s for s in source if s<n]+list(cuts)
        need(children and all(0<e<n for e in children),'positive strict child descent')
        depth[n]=1+max(depth[e] for e in children)
        plateau=max(gamma for gamma in gammas if A*gamma<=n)
        for gamma in gammas:
            visit[gamma][n]=int(plateau==gamma)+max(visit[gamma][e] for e in children)
    peak=max(max(v) for v in visit.values())
    need(peak<=tau and max(depth)<=env['D'],'longest-chain plateau/depth bounds')
    need(all(row[1].bit_length()<=env['width_log_bound']+1 for row in expected[1:]),'width bound')
    need(all((row[1]+row[2]+row[3]).bit_length()<=env['combined_output_bits']
             for row in expected[1:]),'complete output-bit bound')
    max_row=max(value.bit_length() for row in expected[1:] for value in row)
    need(max_row<=env['Z'],'ordinary scalar bit budget')
    counters=vars(actual.work)
    need(sum(counters.values())<=4*env['K'],'conservative implementation work envelope')
    return {'ambient':A,'targets':target,'paid':paid,'maximum':maximum,
            'rows':maximum,'replication_trials':trials,'plateaus':len(gammas),
            'max_chain_depth':max(depth),'max_plateau_visits':peak,
            'tau':tau,'max_row_bits':max_row,'divisor_bits':divisor.bit_length(),
            'checked_slots':sum(f[-1] for f in flows.values()),
            'row_sha256':sha256(repr(expected).encode()).hexdigest()}


def load(path,name,mutation=None):
    if mutation is None:
        spec=spec_from_file_location(name,path);module=module_from_spec(spec)
        sys.modules[name]=module;spec.loader.exec_module(module);return module
    source=path.read_text();old,new=mutation
    need(source.count(old)==1,'unique mutant seam')
    module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
    exec(compile(source.replace(old,new),str(path),'exec'),module.__dict__)
    return module


def plateau_check(module):
    records=[]
    for A in (4,5,7,8,13,32,64,127):
        n=2*A-1
        rule=module.Rule(A,((2,1),(3,1)),((1,1),))
        rows=module.compile_library(rule,n).rows
        expected=[(t//2)+1 for t in range(A)]
        need(all(rows[A+t].width==2**exponent for t,exponent in enumerate(expected)),
             'separate exact plateau recurrence formula')
        written=sum(rows[A+t].width.bit_length() for t in range(A))
        need(written==(A-1)**2//4+2*A,'closed total width-output length')
        need(rows[n].width.bit_length()==(A+1)//2+1,'closed endpoint length')
        need((1<<A)%rows[n].width==0,'honest plateau divisor')
        if A>=7:need(8%rows[n].width!=0,'false default divisor exposed')
        records.append({'ambient':A,'maximum':n,'endpoint_bits':rows[n].width.bit_length(),
                        'width_bits_written':written})
    # All-prime evidence: rank semigroup uses only 2, but a width uses prime 3.
    r=module.compile_library(module.Rule(5,((2,3),),((1,1),)),16).rows[16]
    need(r.width%3==0,'source-prime support is not rank-prime support')
    return records


def run(package):
    path=package/'ambient_library.py'
    need(sha256(path.read_bytes()).hexdigest()==CODE_SHA,'science code changed')
    need(sha256((package/'PROOF.md').read_bytes()).hexdigest()==PROOF_SHA,'science proof changed')
    manifest=json.loads((package/'SOURCES.json').read_text());pins=[]
    for item in manifest['files']:
        if 'local' not in item:continue
        data=(package/item['local']).read_bytes()
        need(len(data)==item['bytes'] and sha256(data).hexdigest()==item['sha256'],'frozen local source bytes')
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['git_blob'],'frozen local Git blob')
        pins.append(item['local'])
    module=load(path,'independent_ambient_subject')
    domains=[check_domain(module,d) for d in DOMAINS]
    plateau=plateau_check(module)
    mutations=(
        ('pooled_exit',
         'factor = child(rows, flow.rank, exit_rank).width',
         'factor = child(rows, flow.rank, exit_rank).width // gcd(child(rows, flow.rank, exit_rank).width, multiplicity)',DOMAINS[2]),
        ('default_ambient_visits',
         'visits = rule.ambient * (rule.kmin - 1).bit_length()',
         'visits = rule.m * (rule.kmin - 1).bit_length()',DOMAINS[1]),
        ('missing_consumed_demands',
         'if depth < gmax:', 'if False:',DOMAINS[0]),
    )
    controls=[]
    for j,(label,old,new,domain) in enumerate(mutations):
        mutant=load(path,'independent_ambient_mutant_'+str(j),(old,new))
        try:check_domain(mutant,domain)
        except ValueError as error:controls.append({'mutant':label,'failure':str(error)})
        else:raise ValueError('undetected independent mutant '+label)
    return {'status':'PASS_INDEPENDENT_AMBIENT_LIBRARY_REVIEW','code_sha256':CODE_SHA,
            'proof_sha256':PROOF_SHA,'authenticated_local_sources':pins,'domains':domains,
            'plateau_output_fixtures':plateau,'negative_controls':controls,
            'coverage':{'rows':sum(d['rows'] for d in domains),
                        'brute_replication_trials':sum(d['replication_trials'] for d in domains),
                        'represented_target_slots':sum(d['checked_slots'] for d in domains)},
            'limits':'Finite corroboration; universal acceptance is in REVIEW.md. No native realization, selected table, literal tape simulation, or multiplier admission.'}


if __name__=='__main__':
    package=Path(sys.argv[1]).resolve()
    print(json.dumps(run(package),indent=2,sort_keys=True))
