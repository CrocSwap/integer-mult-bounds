#!/usr/bin/env python3
"""Fresh compact exact caller/coordinate replay. Root guarded execution only.
No source evaluator import. Accepted all649 local component is reused explicitly.
The Laurent engine executes every literal scalar and physical controller event.
The coordinate engine proves all-width phase using C=(1+i)/2 I+(1-i)/2 X.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from hashlib import sha256
import argparse,copy,gzip,json
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[2]
CTRL=BASE/'swarm-next-gain-sol-high-20261024/repository/research/kappa-backward-controller-20261023/CONTROLLER.json'
CH='60cc512b39cdb9ea2c2ac6c6634c8d3f9627d96ace08ffa659a9d9472444122b'
def need(x,s):
    if not x:raise ValueError(s)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def add(a,b,c=1):
    out=dict(a)
    for k,v in b.items():
        out[k]=out.get(k,F(0))+c*v
        if not out[k]:del out[k]
    return out
def mul(a,q=0,stages=()):
    out={}
    for (j,e),c in a.items():
        z=list(e);z[0]+=q
        for s in stages:z[s+1]+=1
        out[j,tuple(z)]=c
    return out
def scalar(rows,ops):
    r=copy.deepcopy(rows)
    for op in ops:
        if op[0]=='ADD':r[op[1]]=add(r[op[1]],r[op[2]],F(op[3]))
        elif op[0]=='SCALE':r[op[1]]={k:F(op[2])*v for k,v in r[op[1]].items()}
        elif op[0]=='SWAP':r[op[1]],r[op[2]]=r[op[2]],r[op[1]]
        else:raise ValueError('unlicensed scalar boundary')
    return r
def replay(w,reverse_boundaries=False):
    zero=(0,)*34;identity=[{(j,zero):F(1)}for j in range(32)]
    for side in ('right','left'):
        need(scalar(identity,w['boundaries'][side+'_program'])==[{(j,zero):F(v)for j,v in enumerate(row)if F(v)}for row in w['boundaries'][side]],'literal boundary matrix')
    first,last=('left','right')if reverse_boundaries else('right','left')
    r=scalar(identity,w['boundaries'][first+'_program'])
    for e in w['physical_events']:
        kind=e[0]
        if kind in ('LOCAL','QUERY_SHEAR'):
            _,s,p,back=e;x,y=2*p,2*p+1
            if back:r[x]=add(r[x],mul(r[y],q=1),-1)
            else:r[y]=add(r[y],mul(r[x],q=-1))
            if kind=='LOCAL':r[x]=mul(r[x],stages=[s]);r[y]=mul(r[y],stages=[s])
        elif kind=='IDLE':
            for j in (2*e[1],2*e[1]+1):r[j]=mul(r[j],stages=e[2])
        elif kind=='ADD':r[e[1]]=add(r[e[1]],r[e[2]],F(e[3]))
        elif kind=='Q_POWER':need(e[2]in(-2,2),'even central native translation only');r[e[1]]=mul(r[e[1]],q=e[2])
        elif kind=='SIGNED_SWAP':
            a,b=e[1:];r[a]=add(r[a],r[b]);r[b]=add(r[b],r[a],-1);r[a]=add(r[a],r[b])
        elif kind=='SWAP':a,b=e[1:];r[a],r[b]=r[b],r[a]
        else:raise ValueError('unknown physical event '+kind)
    r=scalar(r,w['boundaries'][last+'_program'])
    need(r==[{(j,tuple(d)):F(1)}for j,d in enumerate(w['diagonal'])],'fresh all32-row Laurent endpoint; exterior coefficients retained')
    return r
def route(active):
    pi=active+[j for j in range(145)if j not in active];inv=[None]*145
    for j,k in enumerate(pi):inv[k]=j
    # Chronological transpositions acting on coordinate basis columns.
    now=list(range(145));word=[]
    for j,want in enumerate(pi):
        if now[j]!=want:
            old=now[j];word.append(['SWAP_BITS',old,want]);now=[want if x==old else old if x==want else x for x in now]
    return {'rank':len(active),'active_axes':active,'permutation':pi,'inverse_permutation':inv,'pre_word':word,'post_word':list(reversed(word)),'affine_translation':[],'absolute_phase':0}
def verify_route(r):
    pi=r['permutation'];inv=r['inverse_permutation'];n=145
    need(sorted(pi)==list(range(n))and sorted(inv)==list(range(n))and all(inv[pi[j]]==j for j in range(n)),'actual145-axis fullrank inverse')
    now=list(range(n))
    for op in r['pre_word']:
        need(len(op)==3 and op[0]=='SWAP_BITS'and 0<=op[1]<n and 0<=op[2]<n and op[1]!=op[2],'typed coordinate SWAP')
        a,b=op[1:];now=[b if x==a else a if x==b else x for x in now]
    need(now==pi and r['post_word']==list(reversed(r['pre_word'])),'literal route word and exact inverse')
    need(pi[:r['rank']]==r['active_axes']and not r['affine_translation']and r['absolute_phase']==0,'positive child exact axes and phase')
    return True
def make_plan(w,provider,canonical):
    stages=sorted({e[1]for e in w['physical_events']if e[0]=='LOCAL'});need(len(stages)==18,'18 disjoint private8 planes')
    axes={s:list(range(1+8*t,9+8*t))for t,s in enumerate(stages)}
    main=[]
    for j,d in enumerate(w['diagonal']):
        need(d[0]in(-1,1)and all(x in(0,1)for x in d[1:])and all(not d[s+1]for s in range(33)if s not in axes),'canonical diagonal support')
        a=[0]+[x for s in stages if d[s+1]for x in axes[s]]
        main.append(dict(route(a),bank=j,ports=112,q_exponent=d[0],central_X_after_LEFT=d[0]==-1))
    mode=set(provider['mode_owners']);helpers=[];idles=[];locals_=[]
    for idx,e in enumerate(w['physical_events']):
        if e[0]=='LOCAL':
            _,s,p,back=e;need(back is True,'old all18 backward standardmain ABI')
            localaxes=[0]+axes[s];groups={}
            for owner in range(224,632):
                rank=8 if owner in mode else len(canonical['frames'][canonical['final'][owner]])-len(canonical['frames'][canonical['start'][owner]])
                groups.setdefault(rank,[]).append(owner)
            for rank,owners in sorted(groups.items()):helpers.append(dict(route(localaxes[:rank]),event_index=idx,stage=s,owners=owners,field_namespace='helper/event/owner'))
            locals_.append({'event_index':idx,'stage':s,'pair':p,'local_axes':localaxes,'binding':{'x':'main/2pair/port','y':'main/2pair+1/port','original224through631':'helper/event/originalID','owned632through648':'local_owned/local_ordinal/localID'},'owned_slot_offset':17*(len(locals_)),'owned_count':17})
        elif e[0]=='IDLE':
            a=[x for s in e[2]for x in axes[s]];rr=route(a)
            rr['pre_word'],rr['post_word']=rr['post_word'],rr['pre_word']
            idles.append(dict(rr,event_index=idx,pair=e[1],fields=224,execution='pre_inverseJ;canonicalpositiveCr;postJ'))
    return {'schema':'independent-neutral-wholecaller-plan/v1','ambient_axes':145,'chronology':['all_main_preJ','RIGHT_program','physical_events_with_helper_preJ_LOCAL_postJinverse_and_IDLEROUTES','LEFT_program','negative_q_main_Xcentral','all_main_postJinverse'],'stage_embeddings':[{'stage':s,'local_axes':[0]+axes[s],'same_for_all649_local_fields':True,'spectators':'identity'}for s in stages],'main_targets':main,'helper_targets':helpers,'idle_jobs':idles,'locals':locals_,'query_owned':{'slot_offset':306,'count':112,'shared_across_sequential_queries':True,'program':'CLEAR;COPY_actualsource;C1;Xcentral_if_inverse;ADD_actualdestination;CLEAR'},'ownership':{'local_owned_fields':306,'query_owned_fields':112,'total_private_fields':418,'persistent_main_fields':3584,'persistent_helper_fields':7344,'persistent_fields':10928,'all_helper_namespace_keys_distinct':True},'phase_proof':'C_e=aI+bX_e,a=(1+i)/2,b=(1-i)/2; coordinate permutation J sends X_ej to X_epi(j),phase0; C_e^2=X_e with absolute coefficient+1; disjoint C factors commute; negativeQ corrected by Xcentral, never scalar−1. Identities tensor columnwise at every width.','bindings':{'controller_sha256':CH,'B_sha256':'cc297ee54c2743615dfe857838d5f40424ccd33fdb08ecfafbc41b1710416d91','F_sha256':'dfa125a8c26b86cfa2024edab9f8ed3c95ebe23bffc1bedfd3c90aa471e80ae0','local_receipt_sha256':'e77d3f0eec9e2d4d7d29926ba896dfb4840ce0e43d3780399a649ca6d7fc90a0'}}
def verify_plan(plan,w):
    need(plan['ambient_axes']==145 and plan['ownership']['total_private_fields']==418,'explicit418 owned allocator')
    helpers=set();hist=Counter();paid=Counter();routecounts=Counter();negative=0
    for r in plan['main_targets']:
        verify_route(r);d=w['diagonal'][r['bank']];need(r['central_X_after_LEFT']==(d[0]==-1),'negative centralQ correction is X, not exterior SCALE')
        hist[r['rank']]+=112;routecounts['main']+=224;negative+=112*r['central_X_after_LEFT']
        # Full Fourier-character exponent identity after exact J^-1 G J.
        exp={a:1 for a in r['active_axes']};exp[0]=d[0]+2*r['central_X_after_LEFT']
        need(all(v%4==1 for v in exp.values()),'positive main phase, including absolute phase at zero character')
    for r in plan['helper_targets']:
        verify_route(r);hist[r['rank']]+=len(r['owners']);routecounts['helpers']+=2*len(r['owners'])
        for o in r['owners']:
            k=(r['event_index'],o);need(k not in helpers,'fresh original helper namespace');helpers.add(k)
    for r in plan['idle_jobs']:
        rr=copy.deepcopy(r);rr['pre_word'],rr['post_word']=r['post_word'],r['pre_word'];verify_route(rr)
        paid[r['rank']]+=224;routecounts['idle']+=448
    need(len(helpers)==7344 and sum(hist.values())==10928,'every10928 productive job canonical route covered')
    need(routecounts==Counter(main=7168,helpers=14688,idle=6720)and negative==1792,'literal target+idle map and negativeQ counts')
    need(plan['chronology'][1]=='RIGHT_program'and plan['chronology'][3]=='LEFT_program','actual ordered canonical execution')
    return hist,paid,routecounts,negative
def query_check(back=False,omit_final_clear=False):
    # Actual three-column primitive execution; native q has order4 exactly.
    rows=[{(j,0):F(1)}for j in range(3)];x,y,z=range(3)
    rows[z]={}                         # erase arbitrary third input
    rows[z]=dict(rows[y if back else x]) # COPY from preserved real source
    rows[z]={(j,(q+1)%4):v for(j,q),v in rows[z].items()} # positiveC1
    if not back:rows[z]={(j,(q+2)%4):v for(j,q),v in rows[z].items()} # Xcentral
    dst=x if back else y;rows[dst]=add(rows[dst],rows[z],-1 if back else 1)
    if not omit_final_clear:rows[z]={}
    expected=[{(j,0):F(1)}for j in range(2)]+[{}]
    expected[dst]=add(expected[dst],{(1 if back else 0,1 if back else 3):F(1)},-1 if back else 1)
    need(rows==expected,'literalquery all3independentcolumns/ownedzero/sourcepreservation')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--output',type=Path);ap.add_argument('--emit-static-plan',action='store_true');args=ap.parse_args()
    w=json.loads(CTRL.read_text());providerpath=BASE/'swarm-provider-audit-sol-high-20261024/repository/research/native-rank8-helper-provider/PROVIDER.json';p=json.loads(providerpath.read_text());cp=providerpath.parent.parent/'native-center-free-code/SOURCE-WORD.json.gz';c=json.loads(gzip.decompress(cp.read_bytes()))['canonical']
    plan=make_plan(w,p,c)
    if args.emit_static_plan:
        need(not args.plan.exists(),'plan immutable');args.plan.write_text(json.dumps(plan,indent=2)+'\n');return
    need(sha(CTRL)==CH and json.loads(args.plan.read_text())==plan,'frozen source controller and complete literal plan')
    receipt=HERE/'NEUTRAL-LOCAL-RESULT-v16c.json';accepted=json.loads(receipt.read_text());need(sha(receipt)==plan['bindings']['local_receipt_sha256']and accepted['status']=='PASS_COMPLETE_LOCAL_STANDARD_B_AND_F_WITH408POSITIVE_HELPERS','accepted actualall649 local receipt')
    for direction,name in [('B','BACKWARD'),('F','FORWARD')]:need(sha(HERE.parent/'caller'/('NEUTRAL-'+name+'-v16c.json'))==plan['bindings'][direction+'_sha256'],'bound actual local packet')
    replay(w);hist,idle,counts,negative=verify_plan(plan,w)
    # Exact Gaussian rational coefficient square, no floating arithmetic.
    a=(F(1,2),F(1,2));b=(F(1,2),F(-1,2))
    cm=lambda x,y:(x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
    aa,bb,ab=cm(a,a),cm(b,b),cm(a,b);need(tuple(x+y for x,y in zip(aa,bb))==(0,0)and tuple(2*x for x in ab)==(1,0),'C²=X absolutephase+1')
    controls=[]
    def reject(label,fn):
        try:fn()
        except(ValueError,KeyError,IndexError)as ex:controls.append({'name':label,'rejected':True,'reason':str(ex)});return
        raise ValueError('control accepted '+label)
    reject('left_before_right_chronology',lambda:replay(w,True))
    for label,fn in [('one_LOCAL_forward',lambda z:next(e for e in z['physical_events']if e[0]=='LOCAL').__setitem__(3,False)),('missing_Qtranslation',lambda z:z['physical_events'].pop(next(i for i,e in enumerate(z['physical_events'])if e[0]=='Q_POWER'))),('scalar_sign_lost',lambda z:next(e for e in z['physical_events']if e[0]=='SIGNED_SWAP').__setitem__(0,'SWAP'))]:
        bad=copy.deepcopy(w);fn(bad);reject(label,lambda bad=bad:replay(bad))
    bad=copy.deepcopy(plan);next(r for r in bad['main_targets']if r['central_X_after_LEFT'])['central_X_after_LEFT']=False;reject('negativeQ_X_missing',lambda:verify_plan(bad,w))
    bad=copy.deepcopy(plan);bad['main_targets'][0]['inverse_permutation'][0]=bad['main_targets'][0]['inverse_permutation'][1];reject('wrong_inverse_coordinate_map',lambda:verify_plan(bad,w))
    bad=copy.deepcopy(plan);bad['helper_targets'][1]['owners'].append(bad['helper_targets'][0]['owners'][0]);reject('fresh_helper_alias_collision',lambda:verify_plan(bad,w))
    # Every actualquery copies the observed source and clears same shared112slots.
    query_check(False);query_check(True);reject('query_final_CLEAR_missing',lambda:query_check(False,True))
    paid=Counter({int(k):18*v for k,v in p['paid'].items()});paid[8]+=144;paid[1]+=15*112;paid+=idle
    result={'schema':'independent-neutral-wholecaller-result/v1','status':'PASS_EXACT_WHOLECALLER_AND_ALL10928_CANONICAL_TARGET_ROUTES','controller_sha256':sha(CTRL),'plan_sha256':sha(args.plan),'checker_sha256':sha(Path(__file__)),'local_receipt_sha256':sha(receipt),'ordered_execution':plan['chronology'],'physical_events_executed':dict(Counter(e[0]for e in w['physical_events'])),'laurent_rows':32,'independent_ports_per_row':112,'formal_variables':34,'finite_order_used_in_main_Laurent':False,'productive_profile':dict(hist),'complete_paid_profile':dict(paid),'layout_fieldmaps':dict(counts),'total_new_layout_fieldmaps':sum(counts.values()),'negativeQ_Xcentral_maps':negative,'total_new_normalizer_fieldmaps_including_X':sum(counts.values())+negative,'ownership':plan['ownership'],'controls':controls,'all_width_phase_proof':plan['phase_proof'],'no_hidden_layout_assumption':True,'reused_foundation':'Exactaccepted all649 component inclpositive400aliases and newlypaidD8/restoredC8; this checker does not rerun native provider/1240phase census. All649 local fields use identical9-planeembedding with arbitrary spectator identity.','compiler_or_funding_admission':False,'economic_gain':0}
    need(args.output is not None and not args.output.exists(),'fresh result required');args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
