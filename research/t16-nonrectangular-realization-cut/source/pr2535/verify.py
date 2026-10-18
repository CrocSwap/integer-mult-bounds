"""Source-bound necessary class cuts for PR2169. Apache-2.0."""
import argparse
from collections import Counter,defaultdict
import gzip,hashlib,importlib.util,json
from itertools import combinations,product
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
W=(4,5,7,8,9)
PLAN='research/complex-t16-rare-pattern-exchanges/data/PLAN.json'
SELECTED='research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz'
TEMPLATE='research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz'
PHASES='research/community-k492-audit/pr622/replay/baseline558/complex-global/base/work/complex-nine-native/DATA-PHASES.json'

def need(ok,message):
    if not ok: raise ValueError(message)

def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)

def authenticate():
    # No predecessor code is imported or executed.
    for row in read(HERE/'SOURCES.json')['files']:
        if row.get('usage')=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'main input hash: '+row['path'])
    for row in read(HERE/'SNAPSHOTS.json')['files']:
        raw=(HERE/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'snapshot hash: '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'snapshot blob')

def load_cuts():
    spec=importlib.util.spec_from_file_location('t16cuts',HERE/'cuts.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def geometry():
    """Rebuild windows and active-pair exclusions from retained events/phase ranks.
    Structural reconstruction only; this does not rerun the full native audit.
    """
    plan,template,phases=read(ROOT/PLAN),read(ROOT/TEMPLATE),read(ROOT/PHASES)
    blocks=defaultdict(list);stage=None;place={};events=template['execution_schedule']
    need([e['kind'] for e in events[30:]]==['bank_padding_cover_sweep','translate_every_live_family'],'tail')
    for e in events[:30]:
        if e['kind']=='local_cover_sweep':stage=e['stage']
        need(stage is not None,'event prefix');blocks[stage].append(e)
        if e['kind']=='idle_cover_sweep':
            for side,c in enumerate(e['child_indices']):place[c]=(e['pair'],side)
    stagepair={e['stage']:e['pair'] for e in template['recipe'] if e['kind']=='local'}
    ranks={}
    for recipe in phases['recipes']:
        entries=recipe['idle_children']
        for c,item in (enumerate(entries) if isinstance(entries,list) else ((int(c),v) for c,v in entries.items())):
            r=len(item['orthogonal_axes']);need(ranks.setdefault(c,r)==r,'nonuniform rank')
    rank={c:r for c,r in ranks.items() if r}
    order=[tuple(z) for z in plan['order']];pos=0;last={};span={};callpos={}
    for stage,replica in order:
        for e in blocks[stage]:
            kind=e['kind']
            if kind=='local_cover_sweep':callpos[stage,replica]=pos;last[replica,stagepair[stage]]=pos
            elif kind=='bridge':last[replica,e['src']]=last[replica,e['dst']]=pos
            elif kind=='idle_cover_sweep':
                for c in e['child_indices']:
                    if c in rank:span[replica,c]=(last.get((replica,e['pair']),-1),pos)
            pos+=1
    rebuilt={f'{o},{c}':[rank[c],[t for t,key in enumerate(order) if lo<callpos[key]<hi]] for (o,c),(lo,hi) in span.items()}
    need(rebuilt==plan['windows'],'source window reconstruction')
    classes={};binclass={}
    # mindiff_cls1 enumerates sorted physical bins; glob.py uses another order.
    for owner,c in sorted(span):
        lo,hi=span[owner,c]
        allowed=tuple(t for t,key in enumerate(order) if lo<callpos[key]<hi and (owner,place[c][0])!=(key[1],stagepair[key[0]]))
        key=(rank[c],allowed)
        if key not in classes:classes[key]=[]
        for port in range(112):classes[key].append((owner,c,port))
    result=[]
    for ci,((capacity,calls),bins) in enumerate(classes.items()):
        result.append({'capacity':capacity,'calls':calls,'bins':bins})
        for b in bins:binclass[b]=ci
    need(len(binclass)==32256 and len(order)==144,'selected dimensions')
    return result,binclass

def aggregate(roles,classes,binclass):
    slots=defaultdict(Counter);flows=[{t:[0]*len(W) for t in c['calls']} for c in classes];occupied=set()
    for z in roles:
        b=(z['owner_replica'],z['child'],z['port']);ci=binclass[b];t=z['time'];w=z['width']
        need(t in flows[ci] and w in W,'illegal class flow')
        need((b,t) not in occupied,'two helpers per bin/call');occupied.add((b,t))
        slots[b][w]+=1;flows[ci][t][W.index(w)]+=1
    patterns=[Counter(tuple(slots[b][w] for w in W) for b in c['bins']) for c in classes]
    return patterns,flows

def decode_stage1(data,classes,cuts):
    need(type(data) is dict and {'x','y'}<=set(data)<= {'x','y','changed','bound'},'stage1 x/y schema')
    # mindiff_cls1's changed/bound are solver metadata, not certified by this tool.
    patterns=[Counter() for _ in classes];flows=[{t:[0]*len(W) for t in c['calls']} for c in classes];seen=set()
    for row in data['x']:
        need(type(row) is list and len(row)==3,'x row');ci,p,v=row
        need(type(ci) is int and 0<=ci<len(classes) and type(p) is list,'x class/pattern')
        need(all(type(a) is int and a>=0 for a in p) and type(v) is int and v>=0,'x integer')
        key=(ci,tuple(p));need(key not in seen,'duplicate x');seen.add(key);patterns[ci][tuple(p)]=v
    seen=set()
    for row in data['y']:
        need(type(row) is list and len(row)==4,'y row');ci,t,w,v=row
        need(all(type(a) is int for a in row) and 0<=ci<len(classes) and t in flows[ci] and w in W and v>=0,'y coordinate')
        key=(ci,t,w);need(key not in seen,'duplicate y');seen.add(key);flows[ci][t][W.index(w)]=v
    for ci,c in enumerate(classes):cuts.validate(patterns[ci],flows[ci],W,c['capacity'],len(c['bins']))
    return patterns,flows

def export_stage1(patterns,flows):
    return {'x':[[ci,list(p),n] for ci,ps in enumerate(patterns) for p,n in sorted(ps.items()) if n],
            'y':[[ci,t,W[i],v] for ci,fs in enumerate(flows) for t,row in sorted(fs.items()) for i,v in enumerate(row) if v]}

def controls(cuts,patterns,flows):
    rejected=[]
    trials=[('bool multiplicity',{(0,):True},{0:[0]},(4,)),
            ('negative count',{(1,):-1},{0:[0]},(4,)),
            ('unbalanced',{(1,):1},{0:[0]},(4,)),
            ('too many calls per bin',{(2,):1},{0:[2]},(4,)),
            ('duplicate widths',{(1,0):1},{0:[1,0]},(4,4))]
    for name,p,f,w in trials:
        try:cuts.validate(p,f,w)
        except ValueError:rejected.append(name)
        else:raise ValueError('control survived: '+name)
    # Dropping the per-bin min would incorrectly accept the strictness fixture.
    need(sum(flows[t][i] for t in (0,1) for i in (0,3))
         ==sum(n*(p[0]+p[3]) for p,n in patterns.items()),'uncapped mutant control')
    return {'invalid_inputs_rejected':rejected,'uncapped_rhs_accepts_impossible_fixture':True}

def all_cuts(patterns,flows,cuts):
    return [{'class':ci,**cut} for ci,(ps,fs) in enumerate(zip(patterns,flows)) for cut in cuts.separate(ps,fs,W)]

def micro_oracle(cuts):
    feasible=set()
    for cells in product(range(3),repeat=9):
        pats=Counter((cells[3*b:3*b+3].count(1),cells[3*b:3*b+3].count(2)) for b in range(3))
        flow=tuple((sum(cells[3*b+t]==1 for b in range(3)),sum(cells[3*b+t]==2 for b in range(3))) for t in range(3))
        feasible.add((tuple(sorted(pats.items())),flow))
    compared=violating=0
    for pp,rows in sorted(feasible):
        pats=dict(pp);fs=dict(enumerate(rows))
        need(not cuts.separate(pats,fs,(4,8)),'false rejection of concrete schedule')
        variants=[fs]
        for t in range(3):
            for i in range(2):
                if rows[t][i]:
                    changed=[list(r) for r in rows];changed[t][i]-=1;changed[(t+1)%3][i]+=1
                    variants.append(dict(enumerate(changed)))
        for flow in variants:
            fast=max([z['deficit'] for z in cuts.separate(pats,flow,(4,8))]+[0]);brute=0
            for mask in (1,2,3):
                ix=[i for i in range(2) if mask>>i&1]
                for k in range(1,4):
                    for ts in combinations(range(3),k):
                        lhs=sum(flow[t][i] for t in ts for i in ix)
                        rhs=sum(n*min(k,sum(p[i] for i in ix)) for p,n in pats.items())
                        brute=max(brute,lhs-rhs)
            need(fast==brute,'sorted separator differs from literal subset oracle')
            compared+=1;violating+=bool(brute)
    return {'concrete_schedules':3**9,'distinct_aggregate_schedules':len(feasible),
            'direct_subset_comparisons':compared,'violating_perturbations':violating}

def run():
    authenticate();cuts=load_cuts();classes,binclass=geometry();c=classes[9]
    need(c['capacity']==16 and c['calls']==tuple(range(9)),'predecessor class9')
    patterns=Counter({(2,0,0,1,0):1,(0,0,0,1,0):1,(0,)*5:len(c['bins'])-2})
    bad={t:[0]*5 for t in c['calls']};bad[0]=[1,0,0,1,0];bad[1]=[1,0,0,1,0]
    cuts.validate(patterns,bad,W,16,len(c['bins']))
    need(cuts.source_hall_and_gr(patterns,bad,W),'witness must pass source Hall/GR')
    witness=next(z for z in cuts.separate(patterns,bad,W) if z['widths']==[4,8] and z['calls']==[0,1])
    need((witness['lhs'],witness['rhs'],witness['deficit'])==(4,3,1),'mixed width cut')
    good={t:list(row) for t,row in bad.items()};good[1][3]-=1;good[2][3]+=1
    placements=[(0,0,4),(0,1,4),(0,2,8),(1,0,8)];rows={t:[0]*5 for t in c['calls']};pp=Counter();pairs=set()
    for b,t,w in placements:
        need((b,t) not in pairs,'placement collision');pairs.add((b,t));rows[t][W.index(w)]+=1
    for b in range(len(c['bins'])):pp[tuple(sum(bb==b and ww==w for bb,_,ww in placements) for w in W)]+=1
    need(rows==good and pp==patterns and not cuts.separate(patterns,good,W),'retimed same-pattern positive')
    actual=[]
    for name,path in [('selected',ROOT/SELECTED),('pr2169',HERE/'inputs/pr2169/data/OWNERS.json.gz')]:
        roles=read(path);ps,fs=aggregate(roles,classes,binclass)
        for ci,cl in enumerate(classes):cuts.validate(ps[ci],fs[ci],W,cl['capacity'],len(cl['bins']))
        need(not all_cuts(ps,fs,cuts),'concrete map violates cut')
        need(decode_stage1(export_stage1(ps,fs),classes,cuts)==(ps,fs),'source schema roundtrip')
        actual.append({'name':name,'rows':len(roles),'classes':len(classes),'bins':len(binclass),
                       'prefix_checks':31*sum(len(cl['calls']) for cl in classes),'violations':0})
    return {'status':'PASS_T16_JOINT_WIDTH_CUTS','source_head':'01b15aee27947d3319c8574464bdab80a00d2839',
            'strictness':{'class':9,'capacity':16,'bin_count':len(c['bins']),'source_hall_and_gr':True,
                          'violating_cut':witness,'same_patterns_legal_placements':[list(z) for z in placements]},
            'reported_predecessor_failure':{'quad_bins':11,'inside_calls':[5,6,8],'reported_outside_width4':4,
                'required_outside_width4':11,'deficit':7,'scope':'Conditional on producer-reported aggregates; c1 artifact unavailable.'},
            'concrete_maps':actual,'micro_oracle':micro_oracle(cuts),'controls':controls(cuts,patterns,bad),
            'scope':'Necessary inequalities only; no sufficient realization claim, solver rerun, optimum or new kappa.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-result',action='store_true')
    parser.add_argument('--stage1',type=Path);parser.add_argument('--output',type=Path);args=parser.parse_args()
    if args.stage1:
        need(args.output is not None and not args.write_result,'stage1 requires exclusive output')
        authenticate();cuts=load_cuts();classes,_=geometry();ps,fs=decode_stage1(read(args.stage1),classes,cuts)
        result={'status':'NECESSARY_CUT_SEPARATION_ONLY','cuts':all_cuts(ps,fs,cuts),
                'limits':'Passing is not realization; global demands and idle targets still need the source model.'}
        with args.output.open('x',encoding='utf-8',newline='\n') as out:json.dump(result,out,indent=2);out.write('\n')
        print(json.dumps({'violations':len(result['cuts'])}));return
    need(args.output is None,'output only for stage1');result=run()
    if args.write_result:
        with (HERE/'RESULT.json').open('x',encoding='utf-8',newline='\n') as out:json.dump(result,out,indent=2);out.write('\n')
    else:need(json.dumps(read(HERE/'RESULT.json'),sort_keys=True)==json.dumps(result,sort_keys=True),'typed result receipt mismatch')
    print(json.dumps(result))

if __name__=='__main__':main()
