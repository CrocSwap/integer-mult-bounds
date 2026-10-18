"""Exact source-bound colored-realization obstruction; no solver is imported."""
from pathlib import Path
from collections import Counter
from itertools import product, permutations, combinations
import argparse
import gzip
import hashlib
import json
import types

P = Path(__file__).resolve().parent
R = P.parents[1]
W = (4,5,7,8,9)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def load(name, path, raw=None):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes() if raw is None else raw,str(path),'exec'),module.__dict__)
    return module


def sources():
    manifest = read(P/'SOURCES.json')
    retained = {}
    for record in manifest['files'] + manifest['retained_sources']:
        if record.get('usage') == 'provenance':
            continue
        path = (R if record.get('usage') == 'input' else P)/record['path']
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == record['sha256'], 'source SHA256: '+record['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == record['git_blob'], 'source Git blob: '+record['path'])
        retained[record['path']] = raw
    # Compile the authenticated source bytes directly, never timestamp bytecode.
    old = load('retained_geometry',P/'source/pr2535/verify.py',retained['source/pr2535/verify.py'])
    old.ROOT = R  # Relocate only the source export's repository root.
    prior = load('retained_rectangle_cuts',P/'source/pr2535/cuts.py',retained['source/pr2535/cuts.py'])
    new = load('new_cell_cuts',P/'cuts.py')
    return old, prior, new


def witness(classes):
    c = classes[9]
    need(c['capacity'] == 16 and c['calls'] == tuple(range(9)) and len(c['bins']) == 224, 'actual class9 geometry')
    pats = Counter({(0,0,1,0,0):1,(0,2,0,0,0):1,(1,1,1,0,0):1,(0,0,0,0,0):221})
    flows = {t:[0]*5 for t in c['calls']}
    flows[0] = [0,1,0,0,0]
    flows[1] = [0,2,1,0,0]
    flows[2] = [1,0,1,0,0]
    good = {t:list(row) for t,row in flows.items()}
    good[1][2] -= 1
    good[0][2] += 1
    return pats,flows,good


def literal_rectangles(patterns, flows):
    checked = 0
    for mask in range(1,1<<len(W)):
        ix = [i for i in range(len(W)) if mask >> i & 1]
        for k in range(1,len(flows)+1):
            rhs = sum(n*min(k,sum(p[i] for i in ix)) for p,n in patterns.items())
            for ts in combinations(flows,k):
                lhs = sum(flows[t][i] for t in ts for i in ix)
                need(lhs <= rhs, 'literal rectangle cut violated')
                checked += 1
    return checked


def realizations(bad, good):
    # Every other call has zero flow, so all six helpers must use calls0,1,2.
    # Enumerate A's one7, B's two distinct-call5s, C's distinct-call4/5/7.
    total = bad_count = good_count = 0
    good_word = None
    for a in range(3):
        for bs in combinations(range(3),2):
            for cs in permutations(range(3)):
                events = [(0,a,7)] + [(1,t,5) for t in bs] + [(2,t,w) for t,w in zip(cs,(4,5,7))]
                flow = {t:[0]*5 for t in range(9)}
                for _,t,w in events:
                    flow[t][W.index(w)] += 1
                total += 1
                bad_count += flow == bad
                if flow == good:
                    good_count += 1
                    good_word = events
    need(total == 54 and bad_count == 0 and good_count > 0, 'complete54 assignment census')
    return dict(assignments=total,bad_realizations=bad_count,good_realizations=good_count,
                good_placement=[list(e) for e in good_word])


def coefficient_oracle(new):
    # Independent finite enumeration: all assignments of a three-width pattern
    # to three distinct calls, against every subset of the nine call/width cells.
    widths = (4,5,7)
    patterns = [p for p in product(range(4),repeat=3) if sum(p)<=3]
    allcells = [(t,w) for t in range(3) for w in widths]
    assignments = {p:sorted(set(permutations(tuple(w for w,n in zip(widths,p) for _ in range(n))+(0,)*(3-sum(p))))) for p in patterns}
    checks = 0
    for mask in range(1<<9):
        cells = tuple(c for i,c in enumerate(allcells) if mask >> i & 1)
        for p in patterns:
            direct = max(sum((t,w) in cells for t,w in enumerate(row) if w) for row in assignments[p])
            need(new.coefficient(p,widths,cells)[0] == direct, 'finite exact matching coefficient')
            checks += 1
    need(checks == 10240, 'coefficient oracle coverage')
    return checks


def rectangle_coefficients(new, universe):
    checks = 0
    for mask in range(1<<len(W)):
        widths = [w for i,w in enumerate(W) if mask >> i & 1]
        for k in range(10):
            cells = tuple((t,w) for t in range(k) for w in widths)
            for p in universe:
                expect = min(k,sum(p[i] for i,w in enumerate(W) if w in widths))
                need(new.coefficient(p,W,cells)[0] == expect, 'rectangle coefficient must reduce to predecessor')
                checks += 1
    return checks


def run():
    old, prior, new = sources()
    classes,_ = old.geometry()
    patterns,bad,good = witness(classes)
    c = classes[9]
    cells = read(P/'CELLS.json')
    need(cells == [[1,5],[1,7],[2,4],[2,7]], 'literal witness cells')
    prior.validate(patterns,bad,W,16,224)
    need(prior.source_hall_and_gr(patterns,bad,W), 'source Hall/GR must pass')
    need(not prior.separate(patterns,bad,W), 'all prior joint-width cuts must pass')
    rectangles = literal_rectangles(patterns,bad)
    result = new.inspect(patterns,bad,W,16,224,cells,prior.validate)
    need((result['lhs'],result['rhs'],result['deficit']) == (5,4,1), 'nonrectangular obstruction5>4')
    positive = new.inspect(patterns,good,W,16,224,cells,prior.validate)
    need((positive['lhs'],positive['rhs'],positive['violated']) == (4,4,False), 'same-pattern positive cut')
    need(not prior.separate(patterns,good,W), 'positive predecessor cuts')
    census = realizations(bad,good)
    # Check the displayed placement's complete source pattern/flow contract.
    rebuilt = Counter()
    pairs = set()
    for b,t,w in census['good_placement']:
        need((b,t) not in pairs, 'positive placement bin/call collision')
        pairs.add((b,t))
    for b in range(224):
        rebuilt[tuple(sum(bb==b and ww==w for bb,_,ww in census['good_placement']) for w in W)] += 1
    need(rebuilt == patterns, 'positive complete pattern inventory')
    # Existing per-call source demand bounds are respected. This does NOT make
    # the isolated class a globally balanced stage1 solution.
    demand = Counter((r['time'],r['width']) for r in old.read(R/old.SELECTED))
    need(all(v <= demand[t,w] for t,row in bad.items() for w,v in zip(W,row)), 'source call/width demand bounds')
    # The general cut needs coefficients for absent optimizer patterns too.
    universe = new.all_patterns(W,16,9,224)
    need(len(result['pattern_coefficients']) == len(universe) and set(patterns)<set(universe), 'complete source pattern universe')
    covered = {tuple(row['pattern']):row for row in result['pattern_coefficients']}
    need(covered[(0,0,1,0,0)]['coefficient']==1 and covered[(0,2,0,0,0)]['coefficient']==1 and covered[(1,1,1,0,0)]['coefficient']==2, 'three active pattern coefficients')
    # Semantic failure controls: replacing the cell graph by its rectangle hull
    # or dropping bin/call exclusion loses the actual separating inequality.
    hull = [[t,w] for t in (1,2) for w in (4,5,7)]
    hull_cut = new.inspect(patterns,bad,W,16,224,hull,prior.validate)
    need(not hull_cut['violated'] and hull_cut['rhs']==5, 'rectangular-hull mutant should miss obstruction')
    uncapped = sum(n*sum(p[i] for i,w in enumerate(W) if any(ww==w for _,ww in cells)) for p,n in patterns.items())
    need(uncapped==6 and result['lhs']<=uncapped, 'width-only mutant should miss obstruction')
    # A generic API must not turn an invalid graph into a favorable cut.
    rejected=[]
    for name,wrong in [('duplicate',cells+[cells[0]]),('bool',[[True,5]]),('foreign-width',[[1,6]]),('foreign-call',[[9,5]])]:
        try:new.inspect(patterns,bad,W,16,224,wrong,prior.validate)
        except ValueError:rejected.append(name)
        else:raise ValueError('malformed cell survived: '+name)
    return dict(schema_version=1,status='PASS',scope='A local source-class obstruction; no globally balanced stage1 candidate, owner map or kappa',
                class_index=9,capacity=16,bins=224,calls=list(c['calls']),widths=list(W),active_bins=[list(b) for b in c['bins'][:3]],
                patterns=[[list(p),n] for p,n in sorted(patterns.items())],bad_flows=[[t,row] for t,row in bad.items()],good_flows=[[t,row] for t,row in good.items()],
                source_hall_and_gr=True,predecessor_sorted_prefix_checks=31*9,literal_rectangle_checks=rectangles,
                bad_cut=result,good_cut=positive,realization_census=census,
                coefficient_oracle_checks=coefficient_oracle(new),rectangle_reduction_checks=rectangle_coefficients(new,universe),
                source_pattern_count=len(universe),source_demand_bounds=True,
                controls=dict(rectangular_hull_rhs=5,width_only_rhs=6,malformed_cells_rejected=rejected),no_new_kappa=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write-result',action='store_true')
    ap.add_argument('--stage1',type=Path)
    ap.add_argument('--class-index',type=int)
    ap.add_argument('--cells',type=Path)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    if args.stage1:
        need(not args.write_result and args.class_index is not None and args.cells is not None and args.output is not None,'stage1 needs class-index/cells/output')
        old,prior,new=sources();classes,_=old.geometry()
        need(0<=args.class_index<len(classes),'class index')
        ps,fs=old.decode_stage1(read(args.stage1),classes,prior)
        c=classes[args.class_index]
        result={'class':args.class_index,**new.inspect(ps[args.class_index],fs[args.class_index],W,c['capacity'],len(c['bins']),read(args.cells),prior.validate)}
        with args.output.open('x',encoding='utf-8',newline='\n') as out:out.write(json.dumps(result,indent=2)+'\n')
        print('PASS_T16_SUPPLIED_CELL_CUT deficit='+str(result['deficit']))
        return
    need(args.class_index is None and args.cells is None and args.output is None,'unexpected CLI arguments')
    result=run()
    if args.write_result:
        with (P/'RESULT.json').open('x',encoding='utf-8',newline='\n') as out:out.write(json.dumps(result,indent=2)+'\n')
    else:
        canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'))
        need(canonical(read(P/'RESULT.json')) == canonical(result),'complete typed RESULT equality')
    print('PASS_T16_NONRECTANGULAR_CUT lhs=5 rhs=4 rectangle_checks=15841 assignments=54 coefficient_checks=10240 no_new_kappa')


if __name__ == '__main__':
    main()
