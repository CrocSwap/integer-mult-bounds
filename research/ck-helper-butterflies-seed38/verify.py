"""Source-bound disjoint dyadic helper butterflies for fixed PR917 CK."""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
from collections import Counter
import argparse,gzip,json,hashlib,sys,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));import independent
BASE='abdc6a7002abdbcd9e21bfc5e1a795784deacfdf'
PREFIX='research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/'
INPUTS=(PREFIX+'CANONICAL-WORD.json.gz',PREFIX+'LOCAL-PROGRAMS.json.gz',
        'research/complex-ck-two-sided/RECIPE.json','research/complex-dyadic-lowering/lower.py',
        'research/complex-sw4-frame8/code/invoice_allcold.py')
def need(ok,msg):
    if not ok:raise ValueError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def load(raw):
    def pairs(items):
        d={}
        for k,v in items:need(k not in d,'duplicate JSON');d[k]=v
        return d
    def bad(x):raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)
def inputs():
    m=load((HERE/'SOURCES.json').read_bytes())
    need(set(m)=={'base_commit','files'} and m['base_commit']==BASE and set(m['files'])==set(INPUTS),'source pin inventory')
    raw=[]
    for p in INPUTS:
        b=(ROOT/p).read_bytes();need(hashlib.sha256(b).hexdigest()==m['files'][p],'source pin '+p);raw.append(b)
    spec=importlib.util.spec_from_file_location('pinned_lower',ROOT/INPUTS[3]);lower=importlib.util.module_from_spec(spec);spec.loader.exec_module(lower)
    return load(gzip.decompress(raw[0])),load(gzip.decompress(raw[1])),load(raw[2]),lower
@lru_cache(None)
def price(n,den=8):
    q=Q(n,den);a,b=abs(q.numerator),q.denominator
    if not a:return 0
    if a==b:return 2
    return a.bit_length()+a.bit_count()+b.bit_length()
def matrix(word,recipe):
    targets,helpers=recipe['targets'],recipe['sources']
    need(len(targets)==112 and len(helpers)==254 and len(set(targets+helpers))==366,'matrix register domains')
    need(all(word['start'][r]==0 for r in targets+helpers),'common entry frame')
    ri={v:i for i,v in enumerate(targets)};ci={v:i for i,v in enumerate(helpers)}
    C=[[0]*len(helpers) for _ in targets]
    for tag,t,s,a,b,f in word['compensation']:
        need(tag=='add' and f==0,'compensation shape');v=Q(a,b)*8;need(v.denominator==1,'eighth grid')
        C[ri[t]][ci[s]]+=v.numerator
    D=[row[:] for row in C]
    for i,j,s,depth in recipe['target_forest']:D[i]=[a-s*b for a,b in zip(C[i],C[j])]
    return targets,helpers,C,D
def census(D):
    columns=list(zip(*D));table={};gaps=Counter();records=[];improved=[]
    for i,A in enumerate(columns):
        for j in range(i):
            pairs=Counter(zip(A,columns[j]));ident=sum(n*(price(a)+price(b)) for (a,b),n in pairs.items())
            bf=10+sum(n*(price(a+b,16)+price(b-a,16)) for (a,b),n in pairs.items())
            choices=[(ident,'identity')]
            for mul in (-4,-2,-1,1,2,4):
                boundary=2*price(mul,2)
                choices.extend([(boundary+sum(n*(price(a)+price(2*b-mul*a,16)) for (a,b),n in pairs.items()),f'{i}<-{j}:{mul}/2'),
                                (boundary+sum(n*(price(b)+price(2*a-mul*b,16)) for (a,b),n in pairs.items()),f'{j}<-{i}:{mul}/2')])
            best=min(choices);gap=bf-best[0];gaps[gap]+=1
            record=[i,j,ident,bf,best[0],best[1]];records.append(record);table[j,i]=record
            if gap<0:improved.append(record)
    return table,{'unordered_pairs':len(records),'directed_shear_cases':12*len(records),'improving_butterflies':improved,
                  'gap_histogram':{str(k):v for k,v in sorted(gaps.items())},
                  'records_sha256':hashlib.sha256(canonical(records).encode()).hexdigest()}
def add(t,s,q):
    q=Q(q);need(t!=s and q,'bad ADD');return ['add',t,s,q.numerator,q.denominator]
def inverse(ops):
    return [add(e[1],e[2],-Q(e[3],e[4])) if e[0]=='add' else ['scale',e[1],e[3],e[2]] for e in reversed(ops)]
def build(C,D,targets,helpers,recipe,matching,table):
    need(set(matching)=={'pairs','gain','panel'} and type(matching['pairs']) is list and type(matching['gain']) is int and type(matching['panel']) is int,'matching schema')
    used=set();prepH=[];E=[[Q(x,8) for x in row] for row in D];gain=0;butterflies=[]
    for entry in matching['pairs']:
        need(set(entry)=={'pair','weight','cost','kind'} and type(entry['weight']) is int and type(entry['cost']) is int and type(entry['kind']) is str,'pair schema')
        pair=entry['pair'];need(type(pair) is list and len(pair)==2 and all(type(i) is int and 0<=i<254 for i in pair),'pair domain')
        a,b=pair;need(a<b and a not in used and b not in used,'disjoint pairs');used.update(pair)
        rec=table[a,b];i,j,ident,bf,sc,desc=rec
        kind=entry['kind'];cost=bf if kind=='butterfly' else sc
        need(kind=='butterfly' or kind==desc,'exact best same-pair shear')
        need(entry['cost']==cost and entry['weight']==ident-cost and ident>cost,'pair price')
        gain+=ident-cost
        if kind=='butterfly':
            # Census uses i=b, j=a. T acts on (h_i,h_j).
            x,y=helpers[i],helpers[j]
            prepH += [add(x,y,1),['scale',y,2,1],add(y,x,-1)]
            for row in E:A,B=row[i],row[j];row[i],row[j]=(A+B)/2,(B-A)/2
            butterflies.append([x,y])
        else:
            left,coeff=kind.split(':');dest,src=map(int,left.split('<-'));q=Q(coeff)
            prepH.append(add(helpers[dest],helpers[src],q))
            for row in E:row[src]-=q*row[dest]
    need(gain==matching['gain'],'matching gain')
    prepT=[add(targets[c],targets[p],-s) for c,p,s,_ in recipe['target_forest']]
    residual=[add(t,helpers[j],q) for t,row in zip(targets,E) for j,q in enumerate(row) if q]
    panel=prepT+prepH+residual+inverse(prepH)+inverse(prepT)
    bill=sum(price(q.numerator,q.denominator) for row in E for q in row)+4*len(prepT)
    bill+=sum(2*(price(e[3],e[4]) if e[0]=='add' else 1) for e in prepH)
    need(bill==matching['panel'],'complete panel price')
    return panel,{'panel_component_primitives':bill,'panel_macros':len(panel),'residual_additions':len(residual),'helper_pairs':len(matching['pairs']),'butterflies':butterflies}
def scalar(op,backward):
    if op[0]=='add':
        _,t,s,a,b=op
        if backward:t,s,a=s,t,-a
        return ['scalar',['add',['L',t],['L',s],a,b],0]
    _,t,a,b=op
    if backward:a,b=b,a
    return ['scalar',['scale',['L',t],a,b],0]
def programs(word,old,panel):
    begin=1+len(word['precondition']);end=begin+len(word['compensation']);result={}
    rawpanel=[e[:5] for e in word['compensation']]
    for name,events in old.items():
        need(events[0]==['phase','zero_frame_precondition'] and events[end]==['phase','entry_adapters'],'phase barriers')
        need(events[begin:end]==[scalar(e,name=='backward') for e in rawpanel],'source panel binding')
        result[name]=events[:begin]+[scalar(e,name=='backward') for e in panel]+events[end:]
        need([e for e in events if e[0]!='scalar']==[e for e in result[name] if e[0]!='scalar'],'nonscalar preservation')
    return result
def run():
    word,old,recipe,lower=inputs();targets,helpers,C,D=matrix(word,recipe);table,cens=census(D)
    witness=load((HERE/'WITNESS.json').read_bytes());need(set(witness)=={'base_commit','seed','shear_matching','butterfly_matching'} and witness['base_commit']==BASE and type(witness['seed']) is int and witness['seed']==38,'witness metadata')
    panels={};summaries={};results={};grids=set()
    for label,key in [('shear','shear_matching'),('butterfly','butterfly_matching')]:
        panel,info=build(C,D,targets,helpers,recipe,witness[key],table);panels[label]=panel;summaries[label]=info
        for backward in (False,True):independent.panel_replay(panel,targets,helpers,C,backward)
        ps=programs(word,old,panel);results[label]={}
        for name,events in ps.items():
            primitives=[];macros=0
            for e in events:
                if e[0]=='scalar':
                    macros+=1;primitives.extend(lower.lower(e[1]))
                    if e[1][0]=='add':grids.add(Q(e[1][3],e[1][4]))
            # Literal full-column endpoint check only for the new candidate;
            # both complete panels receive the separate Fraction replay above.
            replay=independent.replay(primitives,name=='backward') if label=='butterfly' else {'primitive_count':len(primitives)}
            need(replay['primitive_count']==len(primitives),'primitive tally')
            results[label][name]={**replay,'real_primitives':2*len(primitives),'scalar_macros':macros,
                                 'primitive_sha256':hashlib.sha256(canonical(primitives).encode()).hexdigest()}
    # Check the arithmetic price against the exact allowed lowerer for every coefficient used.
    for q in grids:need(price(q.numerator,q.denominator)==len(lower.lower(['add',['L',1],['L',0],q.numerator,q.denominator])),'price/lowering mismatch')
    for name in old:need(results['shear'][name]['real_primitives']-results['butterfly'][name]['real_primitives']==8,'complete scalar gain')
    need(summaries['shear']['panel_component_primitives']==8434 and summaries['butterfly']['panel_component_primitives']==8430,'panel comparison')
    # Same inherited formula; derive all changed macro terms explicitly.
    compiler=64*74**3
    K=sum(e[0] in ('climb','center') for e in old['forward'])
    need(K==3698 and K==sum(e[0] in ('climb','center') for e in old['backward']),'paid-child count')
    invoice={}
    for label in results:
        M=results[label]['forward']['scalar_macros'];need(M==results[label]['backward']['scalar_macros'],'orientation macro count')
        adapters=16*(M+K+716+8)+64*73
        invoice[label]={'macros':M,'paid_children':K,'compiler':compiler,'adapters':adapters,
                        'local_bound':max(x['real_primitives'] for x in results[label].values())+adapters*compiler}
    controls=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,TypeError):controls.append(name);return
        raise ValueError('control accepted '+name)
    p=panels['butterfly'];bf=next(k for k,e in enumerate(p) if e[0]=='scale')
    reject('omit butterfly doubling',lambda:independent.panel_replay(p[:bf]+p[bf+1:],targets,helpers,C,False))
    reject('omit final restoration',lambda:independent.panel_replay(p[:-1],targets,helpers,C,False))
    wrong=[e[:] for e in p];wrong[bf][2]=1
    reject('wrong determinant normalization',lambda:independent.panel_replay(wrong,targets,helpers,C,False))
    wrong=[e[:] for e in p];wrong[bf+1][3]*=-1
    reject('wrong butterfly sign',lambda:independent.panel_replay(wrong,targets,helpers,C,False))
    wrong=[e[:] for e in p];wrong.reverse()
    reject('wrong complete order',lambda:independent.panel_replay(wrong,targets,helpers,C,False))
    mm=load(canonical(witness['butterfly_matching']));mm['pairs'].append(mm['pairs'][0])
    reject('overlapping helpers',lambda:build(C,D,targets,helpers,recipe,mm,table))
    mm=load(canonical(witness['butterfly_matching']));mm['panel']-=10
    reject('unpaid butterfly boundary',lambda:build(C,D,targets,helpers,recipe,mm,table))
    reject('work aliases source',lambda:lower.lower(['add',['L',1],['W',0],1,2]))
    reject('duplicate JSON',lambda:load('{"x":1,"x":2}'))
    reject('nonfinite JSON',lambda:load('{"x":NaN}'))
    need(canonical({'n':1})!=canonical({'n':True}),'typed comparison')
    return {'format':'ck-helper-butterflies/1','base_commit':BASE,'seed':38,'census':cens,
            'panels':summaries,'complete_scalar_programs':results,'local_invoice':invoice,
            'coefficients_checked_against_lowerer':len(grids),'controls_rejected':controls,
            'scope':'fixed historical PR917 target forest and disjoint helper pairs; two nominated matchings; no independent global matching optimum or native/hosted supplier admission'}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-certificate',action='store_true');args=parser.parse_args()
    result=run();path=HERE/'CERTIFICATE.json'
    if args.write_certificate:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    else:need(canonical(result)==canonical(load(path.read_bytes())),'certificate mismatch')
    print('PASS_CK_HELPER_BUTTERFLIES pairs=32131 panel=8434->8430 extra_real=8/8 columns=725 controls=10 no_new_kappa')
if __name__=='__main__':main()
