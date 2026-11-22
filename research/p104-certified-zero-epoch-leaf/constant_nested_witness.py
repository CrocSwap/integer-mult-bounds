#!/usr/bin/env python3
"""Admitted constant-field witnesses for the #8041 one-call edits.

Tests the complete pinned 36-LOCAL caller.  For one selected suffix of 267
rank-127 targets, all 18,906 first-factor positions are above the 15**268
cutoff.  Other suffixes and all other first-factor inputs are zero.  Constant
binary address fields are fixed by every native address permutation, allowing
the paid recursive subcalls to be represented by identity on their completed
inputs.  This deliberately tests only this all-constant subclass.
"""
import gzip, hashlib, json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
def load(path, digest):
    b=path.read_bytes(); assert hashlib.sha256(b).hexdigest()==digest
    return json.loads(gzip.decompress(b))
g=load(ROOT/'pinned/strong-bit.json.gz','74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326')
c=load(ROOT/'pinned/EFREE-CALLER.json.gz','757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b')
p=g['program']; n=g['public']; q=c['ports']; dims={int(k):v['dim'] for k,v in g['frames'].items()}
assert (n,q,len(p),sum(e[0]=='LOCAL' for e in c['events']))==(630,111,39600,36)
assert c['events'][:6]==[['ADD',0,1],['SWAP',0,1],['ADD',19,20],['SWAP',19,20],['LOCAL',1,1,0],['LOCAL',1,20,19]]
assert c['diagonal'][0]=={'q':1,'stages':list(range(1,19))}
cut=15**268; suffix=127**267
assert min(4,8,15)*suffix>=cut
assert all(abs(dims[g['final'][h]]-dims[g['start'][h]]) in (4,8) for h in range(222,630))
assert all((1+7*len(x['stages']))*suffix>=cut for x in c['diagonal'])
# In each local call a and b are #8036/#8041's one-export branch names.
readouts={
 'a':(10037,2829,2335,[2336,2344,2416,2439,2448,2451,2482,2655,2698]),
 'b':(10034,2828,2337,[2359,2362,2372,2394,2397,2408,2416,2419,2425,2431,2434,2465,2484,2518,2530,2571,2576,2584,2600,2617,2623,2626,2778])
}
residuals={
 'a':[266,268,274,279,291,293,316,400,401,407,413,414,421,422,425,428,434,437,445,449,452,500,501,512,513,569,570,578,579],
 'b':[254,255,258,259,276,361,365,367,393,431,442,458,459,465,472,482,497,512]
}
def graph_tape(mode):
    if mode in readouts:
        start,reg,donor,others=readouts[mode]
        assert p[start:start+3]==[['INIT',reg,510],['ADD',reg,donor,510],['MOVE',reg,510,1]]
        return list(enumerate(p[:start]))+[(None,['INIT',reg,1])]+[(None,['ADD',reg,k,1]) for k in others]+list(enumerate(p[start+3:],start+3))
    if mode=='relay':
        assert p[8068:8076]==[['INIT',2326,326],['ADD',2326,1855,326],['ADD',2326,1857,326],['ADD',2326,2224,326],['MOVE',2326,326,531],['INIT',2327,326],['ADD',2327,1855,326],['MOVE',2327,326,1]]
        repl={8073:['INIT',2327,531],8074:['ADD',2327,2326,531],8075:['MOVE',2327,531,1]}
        return [(k,repl.get(k,row)) for k,row in enumerate(p) if k not in (8070,8071)]
    assert mode=='native'
    return list(enumerate(p))
tapes={name:graph_tape(name) for name in ('native','a','b','relay')}
base_hist=Counter(abs(dims[row[3]]-dims[row[2]]) for _,row in tapes['native'] if row[0]=='MOVE')
assert all(base_hist-Counter(abs(dims[row[3]]-dims[row[2]]) for _,row in tapes[x] if row[0]=='MOVE')==Counter({1:1}) for x in ('a','b'))
relay_hist=Counter(abs(dims[row[3]]-dims[row[2]]) for _,row in tapes['relay'] if row[0]=='MOVE')
assert base_hist-relay_hist==Counter({2:1}) and relay_hist-base_hist==Counter({1:1})

def inner(values, mode, probe=False):
    v=dict(enumerate(values)); charts=dict(enumerate(g['start'])); clears=0; relay_residual=None
    for clock,(op,d,*args) in tapes[mode]:
        if probe and clock==8068:
            relay_residual=v[1857]^v[2224]
        if op=='INIT':
            assert d not in charts and d>=630; charts[d]=args[0]; v[d]=0
        elif op=='ADD':
            src,site=args; assert charts[d]==site==charts[src]; v[d]^=v[src]
        elif op=='SWAP':
            src,=args; charts[d],charts[src]=charts[src],charts[d]; v[d],v[src]=v[src],v[d]
        elif op=='MOVE':
            src,dst=args; assert charts[d]==src; charts[d]=dst
            # Every physical address field is constant, so this completed
            # paid coordinate permutation acts as the identity on data.
        elif op=='CLEAR':
            assert d>=630 and charts.pop(d)==args[0]; del v[d]; clears+=1
        else: raise AssertionError(op)
    assert charts==dict(enumerate(g['final'])) and set(v)==set(range(630)) and clears==3433
    return [v[i] for i in range(630)],relay_residual

def run(mode,initial):
    roots=[[0]*q for _ in range(c['roles'])]
    helpers={k:[0]*(n-2*q) for k,e in enumerate(c['events']) if e[0]=='LOCAL'}
    if initial[0]=='helper': helpers[initial[1]][initial[2]-2*q]=1
    else: _,role,port=initial;roots[role][port]=1
    seen=0; probe={}
    for clock,(op,*args) in enumerate(c['events']):
        if op=='LOCAL':
            stage,x,y=args; inp=roots[x]+roots[y]+helpers[clock]
            if clock==4:
                probe['event_4_local_input_ones']=[i for i,v in enumerate(inp) if v]
                probe['a_residual_bit']=sum(inp[i] for i in residuals['a'])%2
                probe['b_residual_bit']=sum(inp[i] for i in residuals['b'])%2
            localmode=mode if clock==4 else 'native'
            out,relay=inner(inp,localmode,probe=(clock==4))
            if clock==4: probe['event_4_relay_residual_bit']=relay
            roots[x]=out[:q]; roots[y]=out[q:2*q];helpers[clock]=out[2*q:]
            seen+=1
        elif op in ('ADD','QUERY'):
            x,y=args;roots[x]=[a^b for a,b in zip(roots[x],roots[y],strict=True)]
        elif op=='SWAP':
            x,y=args; roots[x],roots[y]=roots[y],roots[x]
        elif op=='IDLE_ONE':
            pass
        else: raise AssertionError(op)
    assert seen==36
    result={('root',r,i):v for r,row in enumerate(roots) for i,v in enumerate(row)}
    result.update({('helper',k,i+2*q):v for k,row in helpers.items() for i,v in enumerate(row)})
    return result,probe

def main():
    results={}
    for mode,initial in [('a',('helper',4,266)),('b',('helper',4,254)),('relay',('root',0,3))]:
        native,probe0=run('native',initial); changed,probe1=run(mode,initial)
        assert [k for k,v in native.items() if v]==[initial]
        bad=[k for k in native if native[k]!=changed[k]]
        assert bad
        if mode in ('a','b'): assert probe1[mode+'_residual_bit']==1
        else: assert probe1['event_4_relay_residual_bit']==1
        results[mode]={'input':initial,'event4':probe1,'output_mismatch_count':len(bad),'output_mismatches':bad}
    print(json.dumps({'source_graph_sha256':'74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326','caller_sha256':'757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b','power':268,'floor':15,'selected_suffix':['root',0,0],'selected_suffix_rank':127,'repetitions':267,'all_first_factor_ports_retained':True,'minimum_target_rank_exceeds_floor':4*suffix>=cut,'threshold_bits':cut.bit_length(),'helper_rank_bits':(8*suffix).bit_length(),'root_rank_bits':(127*suffix).bit_length(),'results':results},indent=2))
    print('PASS_ACTUAL_RETAINED_CONSTANT_SUBDOMAIN_COUNTEREXAMPLES')

if __name__=='__main__': main()
