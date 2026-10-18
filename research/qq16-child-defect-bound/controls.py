"""Literal scalar executions on the invariant constant-owner/payload subspace.

No forward/reverse sensitivity function is imported here. Native unitaries and
cover permutations fix the constant vector; these are actual admissible inputs.
"""
from fractions import Fraction as Q
from sources import need

def literal(word,V,inputs,defects,stop=None):
    values={f'X{p}':inputs('i:E'+str(p)) for p in V};injections={}
    for i,e in enumerate(word):
        op=e['op']; olddst=oldsrc=Q(0)
        if op=='add':
            dst,src=e['dst'],e['src'];olddst,oldsrc=values[dst],values[src]
            values[dst]+=Q(e['coefficient'])*values[src]
        elif op in ('line','stage','current_map'):
            dst=e['field'];olddst=values[dst]
        elif op=='clear':values[e['field']]=Q(0)
        elif op=='history_boundary':
            for side in ('X','Y'):
                for p in range(112):values[f'{side}{p}']=inputs(f'i:{side}{p}')
        elif op=='private_end':
            for name in e['fields']:
                need(values[name]==0,'literal private clear');del values[name]
        else:need(op in ('private_begin','checkpoint'),'literal opcode')
        if op in ('add','line','stage','current_map'):
            d=defects(i,e,olddst,oldsrc);injections[f'd{i}']=d;values[dst]+=d
        if i==stop:break
    return values,injections

def evaluate(row,inputs,defects):
    return sum(c*(inputs(v) if v.startswith('i:') else defects.get(v,Q(0))) for (v,g),c in row.items())

def run(old,word,records,result,peakrows,final):
    def inputs(v):return Q((sum(map(ord,v))%11)-5,5)
    def zero(v):return Q(0)
    checked=0;controls={}
    families=['all','native','cover','capture']
    history=next(i for i,e in enumerate(word) if e['op']=='history_boundary')
    for family in families:
        def defect(i,e,a,b):
            enabled=(family=='all' or family=='native' and e['op'] in ('line','stage')
                     or family=='cover' and e['op']=='current_map' or family=='capture' and i<history)
            return Q((i%5+1)*(1 if i%2 else -1),7) if enabled else Q(0)
        values,ds=literal(word,old.V,inputs,defect)
        for name,row in final.items():
            need(values[name]==evaluate(row,inputs,ds),'literal final '+family+' '+name);checked+=1
        controls[family+'_nonzero_injections']=sum(x!=0 for x in ds.values())
        peak=result['peaks']['A']
        values,ds=literal(word,old.V,inputs,defect,peak['event'])
        need(values[peak['field']]==evaluate(peakrows['A'],inputs,ds),'literal peak '+family);checked+=1
        controls[family+'_injections_through_peak']=sum(x!=0 for x in ds.values())
    # A state-relative execution uses the actual preceding values, not ideal ones.
    u=Q(1,1<<result['state_relative_guard_bits'])
    def relative(i,e,a,b):
        weight=abs(a)+(abs(Q(e['coefficient']))*abs(b) if e['op']=='add' else 0)
        return (1 if i%2 else -1)*u*weight
    values,ds=literal(word,old.V,inputs,relative)
    for name,row in final.items():
        need(values[name]==evaluate(row,inputs,ds),'state-relative endpoint oracle');checked+=1
        exact=evaluate(row,inputs,{})
        need(abs(values[name]-exact)<=1,'sufficient b=0 error bound')
    controls['state_relative_nonzero_injections']=sum(x!=0 for x in ds.values())
    # An error in owned C is copied into outputs before C is cleared.
    site=next(i for i,e in enumerate(word) if e['op']=='add' and e['dst']=='C')
    values,ds=literal(word,old.V,zero,lambda i,e,a,b:Q(i==site))
    escaped={name:str(value) for name,value in values.items() if value and name.startswith(('Z','W'))}
    need(escaped and 'C' not in values,'private discard cannot erase escaped errors')
    controls['private_escape']={'site':site,'nonzero_outputs':len(escaped),'first':sorted(escaped.items())[0]}
    site=next(i for i,e in enumerate(word) if e['op']=='line')
    values,_=literal(word,old.V,zero,lambda i,e,a,b:Q(i==site))
    field=word[site]['field'];need(values[field]==1,'inexact native pair does not exactly restore borrowed field')
    controls['borrowed_restoration_failure']={'site':site,'field':field,'residual':'1'}
    peak=result['peaks']['A'];collapsed={}
    for (v,g),c in peakrows['A'].items():
        if v.startswith('d'):collapsed[v]=collapsed.get(v,Q(0))+c
    witness={v:Q(1 if c>0 else -1) for v,c in collapsed.items() if c}
    values,_=literal(word,old.V,zero,lambda i,e,a,b:witness.get(f'd{i}',Q(0)),peak['event'])
    attained=sum(abs(c) for c in collapsed.values())
    need(values[peak['field']]==attained,'constant-subspace signed witness')
    endpoint=max(Q(x['A']) for x in result['final'].values())
    need(attained>endpoint,'actual interior witness exceeds endpoint-only envelope')
    controls['interior_witness']={'event':peak['event'],'field':peak['field'],'attained':str(attained),'endpoint_envelope':str(endpoint)}
    # Sanity failures of replacing the operator word by its constant slice.
    nonidentity=[g for v,g in peakrows['A'] if g!=tuple(1<<j for j in range(73))]
    need(nonidentity,'peak has nontrivial ordered owner actions')
    controls['nontrivial_peak_owner_terms']=len(nonidentity)
    return {'literal_equalities':checked,'controls':controls}
