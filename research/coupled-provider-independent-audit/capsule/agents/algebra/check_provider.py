#!/usr/bin/env python3
"""Independent provider algebra, ownership, basis and physical phase audit."""
import argparse, copy, gzip, hashlib, json, time
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from prior_dyadic_engine import require, initial, linear, rational_row, warped
from provider_rows import interpret
import phase_exact as ph

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]/'repository'
P=ROOT/'research/native-rank8-helper-provider'
MODE=[224,225,227,229,240,241,256,257]
SOURCE='research/native-center-free-code/SOURCE-WORD.json.gz'

def add(a,b,q=F(1)):
    for j,v in b.items():
        a[j]=a.get(j,F(0))+q*v
        if not a[j]:del a[j]

def scalar(row):
    rr=rational_row(row)
    require(all(not word and role[0]=='L' for role,word in rr), 'row retains native word or owned dirt')
    return {role[1]:v for (role,word),v in rr.items()}

def basis(program,rows,c,frame):
    out=[dict(r) for r in rows]
    for e in program:
        tag,dst=e[:2]
        require(224<=dst<632 and c['start' if frame==0 else 'final'][dst]==frame,'basis physical chart')
        if tag=='add':
            src,q=e[2],F(e[3]);require(dst!=src and 224<=src<632 and c['start' if frame==0 else 'final'][src]==frame,'basis source chart')
            require(q.denominator&(q.denominator-1)==0,'basis ADD dyadic')
            add(out[dst],out[src],q)
        else:
            require(tag=='scale','basis cannot erase or borrow scratch')
            q=F(e[2]);require(q and abs(q.numerator)&(abs(q.numerator)-1)==0 and q.denominator&(q.denominator-1)==0,'basis SCALE signed power of two')
            out[dst]={j:q*v for j,v in out[dst].items() if q*v}
    return out

def decode(source,changed):
    old=source['programs']['backward'];j=0;caches={};centers={};zeros={}
    for i,e in enumerate(old):
        require(j<len(changed),'truncated native word')
        if changed[j]==e:j+=1
        elif e[0]=='center':
            a,b=changed[j:j+2];slot=tuple(b[1][2])
            require(a==['scalar',['clear',['C',0]],e[3]] and b==['scalar',['copy',['C',0],list(slot)],e[3]],'center replacement exact binding')
            require(slot in caches and caches[slot]['frame']==e[3],'cache same physical frame')
            centers[i]={'slot':slot,'frame':e[3]};j+=2
        else:
            require(e[0]=='climb' and e[5]==1,'unexplained source-word change')
            require(changed[j]==['zero_retag',e[2],e[3],e[4]],'exact removed H1 retag')
            zeros[i]={'role':('L',e[2]),'frame':e[3]};j+=1
        if j+1<len(changed) and changed[j][0]=='scalar' and changed[j][1][0]=='clear' and changed[j][1][1][0]=='C' and changed[j][1][1][1]>0:
            a,b=changed[j:j+2];slot=tuple(a[1][1]);frame=a[2]
            require(slot not in caches and b[0]=='scalar' and b[1][:2]==['copy',list(slot)] and b[2]==frame,'cache production')
            caches[slot]={'event':i,'role':tuple(b[1][2]),'frame':frame};j+=2
    require(j==len(changed),'unexpected trailing native traffic')
    require(len(caches)==len(centers)==len(zeros)==8 and set(caches)=={('C',i) for i in range(1,9)},'eight independent caches and deletions')
    require(max(r['event'] for r in caches.values())<min(centers),'all eight caches simultaneously retained')
    require(Counter(r['slot'] for r in centers.values())==Counter(caches.keys()),'each cache consumed at one deleted center')
    return caches,centers,zeros

def main(out):
    start=time.monotonic(); consumed={}
    def read(path,z=False):
        raw=path.read_bytes();consumed[str(path.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest()
        return json.loads(gzip.decompress(raw) if z else raw)
    source=read(ROOT/SOURCE,True);word=read(P/'WORD.json.gz',True);artifact=read(P/'PROVIDER.json')
    normal=read(ROOT/'research/coded-native-caller/NORMALIZERS.json')
    code=read(ROOT/'research/native-center-free-code/CODE.json')
    rawsource=gzip.decompress((ROOT/SOURCE).read_bytes())
    require(hashlib.sha256(rawsource).hexdigest()=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd','exact source payload')
    c=source['canonical'];program=word['word'];caches,centers,zeros=decode(source,program)
    sites={}
    for r in caches.values():sites.setdefault(r['event'],set()).add(r['role'])
    for i in centers:sites.setdefault(i,set()).add(('C',0))
    for i,r in zeros.items():sites.setdefault(i,set()).add(r['role'])
    original,observed,oldbill=interpret(c,source['programs']['backward'],{('C',0)},sites)
    for j in range(632):
        target=initial(('L',j))
        if j<112:target=linear(target,initial(('L',j+112)),-1)
        require(original[('L',j)]==target,'original unrestricted source endpoint')
    centerfree=[['scalar',['clear',['C',e[1]]],e[3]] if e[0]=='center' else e for e in source['programs']['backward']]
    cf,_,cfbill=interpret(c,centerfree,{('C',0)})
    cf=[scalar(cf[('L',j)]) for j in range(632)]
    M=normal['mode_columns'];require(len(M)==8 and all(len(r)==112 for r in M),'M shape')
    require(all(sum(M[k][j]*M[l][j] for j in range(112))==56*(k==l) for k in range(8) for l in range(8)),'M Gram 56')
    A=[[F(v) for v in r] for r in code['A']]
    require(all(A[i][j]==F(i==j)-sum(F(M[k][i]*M[k][j],4) for k in range(8)) for i in range(112) for j in range(112)),'actual code factorization')
    B=[[sum(-cf[224+h].get(112+j,F(0))*M[k][j] for j in range(112))/56 for h in range(408)] for k in range(8)]
    for j in range(632):
        want={j:F(1)}
        if j<112:
            for i in range(112):
                if A[i][j]:want[112+i]=-A[i][j]
        if j>=224:
            for i in range(112):
                a=-sum(B[k][j-224]*M[k][i] for k in range(8))
                if a:want[112+i]=a
        require(cf[j]==want,'source-derived full centerfree coupling')
    E=[None]*8;cache_modes={};identities=[]
    for slot,r in caches.items():
        row=scalar(observed[r['event']][r['role']]);coeff={j-224:a for j,a in row.items() if j>=224}
        projection=[sum(a*B[k][j] for j,a in coeff.items()) for k in range(8)]
        require(sum(bool(v) for v in projection)==1,'source cache selects exactly one mode')
        k=next(k for k,v in enumerate(projection) if v);f=projection[k]
        require(E[k] is None,'cache modes independent')
        E[k]={j:a/f for j,a in coeff.items()}
        want={224+j:f*a for j,a in E[k].items()}
        for j in range(112):
            if M[k][j]:want[112+j]=-f*M[k][j]
        require(row==want,'entire actual source cache identity')
        cache_modes[slot]=(k,f)
    require(all(sum(a*B[l][j] for j,a in E[k].items())==int(k==l) for k in range(8) for l in range(8)),'E B transpose identity')
    deltas={}
    for i,r in centers.items():
        cache=caches[r['slot']];delta=linear(observed[i][('C',0)],observed[cache['event']][cache['role']],-1)
        d=scalar(delta);require(d and all(j>=224 for j in d),'center delta uses scalar helpers only')
        deltas[r['frame']]=delta
        identities.append({'center_source_event':i,'cache_source_event':cache['event'],'frame':r['frame'],'scalar_relation':{str(j):str(v) for j,v in d.items()}})
    for i,r in zeros.items():require(observed[i][r['role']]==linear(({},0),deltas[r['frame']],-1),'actual later row negative center delta')
    owned={('C',i) for i in range(9)}
    raw,_,bill=interpret(c,program,owned,require_owned_return=False)
    require(not raw[('C',0)][0],'center owner already zero')
    rawrows=[scalar(raw[('L',j)]) for j in range(632)]+[scalar(raw[('C',j)]) for j in range(9)]
    require(Counter(oldbill['paid'])==Counter(bill['paid'])+Counter({1:8,8:8}),'eight H8 plus eight H1 deletions')
    require(bill['paid']=={1:2193,2:412,3:510,4:127,5:40},'complete paid histogram')
    active=sorted(set(j for r in B for j,a in enumerate(r) if a)|set(j for r in E for j in r));roles=[224+j for j in active]
    require(len(active)==122 and artifact['basis_roles']==roles and artifact['mode_owners']==MODE,'122 common-chart basis roles')
    L=[{j:F(1)} for j in range(632)]
    for j in roles:L[j]={}
    for k,owner in enumerate(MODE):
        for r in active:
            if B[k][r]:L[224+r][owner]=B[k][r]
    for owner in roles:
        if owner in MODE:continue
        for r in active:
            a=F(224+r==owner)-sum(B[k][r]*E[k].get(owner-224,F(0)) for k in range(8))
            if a:L[224+r][owner]=a
    identity=[{j:F(1)} for j in range(632)]
    entered=basis(artifact['input_basis_program'],identity,c,0);require(entered==L,'literal entrance equals derived L')
    require(basis(artifact['output_basis_program'],entered,c,1)==identity,'literal inverse basis product')
    # Square left inverse implies full inverse over Q; also test reverse product.
    inverse=basis(artifact['output_basis_program'],identity,c,1)
    require(basis(artifact['input_basis_program'],inverse,c,0)==identity,'literal reverse inverse product')
    endpoint=[]
    for row in rawrows:
        dest={}
        for j,a in row.items():add(dest,entered[j],a)
        endpoint.append(dest)
    endpoint=basis(artifact['output_basis_program'],endpoint,c,1)
    for j in range(632):
        want={} if j in MODE else {j:F(1)}
        if j<112:
            want[112+j]=F(-1)
            for k in range(8):
                if M[k][j]:want[MODE[k]]=F(M[k][j],4)
        require(endpoint[j]==want,'complete composed persistent endpoint '+str(j))
    for slot,(k,f) in cache_modes.items():
        want={MODE[k]:f}
        for j in range(112):
            if M[k][j]:want[112+j]=-f*M[k][j]
        require(endpoint[632+slot[1]]==want,'complete composed cache endpoint')
    records=artifact['mode_boundaries'];require(len(records)==8,'eight boundary records')
    K=[];NN=[];F8=[]
    frame=lambda j:ph.frame(c['frames'][j])
    back=lambda j:ph.conjugate(frame(j))
    D=tuple(('C',1<<j,1) for j in range(1,9));R=frame(1)
    counts=Counter()
    for k,r in enumerate(records):
        require(r['mode']==k and r['owner']==MODE[k],'mode boundary owner/order')
        slot=('C',r['cache_slot']-632);require(slot in cache_modes and cache_modes[slot][0]==k and r['frame']==caches[slot]['frame'],'actual saved owner/frame')
        require(F(r['cache_scalar'])==1/(2*cache_modes[slot][1]),'exterior cache scaling')
        kk=ph.freeze(r['input_K']['literal_word']);nn=ph.freeze(r['output_N']['literal_word'])
        require(all(e[0] in ('P','D','X','phase') for e in kk+nn),'only monomial boundary gates')
        for op,record in ((kk,r['input_K']),(nn,r['output_N'])):
            sig=ph.signature(op);anchor=record['zero_column_anchor'];j=anchor['index']
            require([list(t) for t in sig[0]]==record['signed_tableau'] and list(sig[1][j])==anchor['gaussian_numerator'] and sig[2]==anchor['denominator_power2'],'literal independently derived phase receipt')
        require(ph.equal(kk+R,R+kk),'K mode intertwines R with exact phase')
        K.append(kk);NN.append(nn);F8.append(back(r['frame']))
    for j,port in enumerate(normal['ports']):
        kp=ph.freeze(port['K_word']);require(ph.equal(kp+R,R+kp),'K port intertwines R')
        wrappers=port['compiled_wrappers'];BX,BY,OX,OY=[ph.freeze(wrappers[name]['word']) for name in ('backward_input_X','backward_input_Y','backward_output_X','backward_output_Y')]
        birth,final,fy=back(c['start'][j]),back(c['final'][j]),back(c['final'][j+112])
        require(ph.equal(BX+ph.adjoint(birth)+final+OX,D),'X physical diagonal')
        require(ph.equal(BY+fy+OY,D),'Y physical diagonal')
        require(ph.equal(BY+final+OX,R),'main physical shear')
        counts['main_diagonal_and_shear']+=3
        for k in range(8):
            if not M[k][j]:continue
            require(ph.equal(K[k]+final+OX,K[k]+ph.adjoint(kp)+R),'ordered helper to main coupling')
            require(ph.equal(BY+F8[k]+NN[k],kp+ph.adjoint(K[k])+D),'ordered main to helper coupling')
            counts['two_coupling_directions']+=2
    for k in range(8):require(ph.equal(K[k]+F8[k]+NN[k],D),'helper physical diagonal');counts['helper_diagonal']+=1
    require(sum(counts.values())==1240,'all 1240 actual physical blocks')
    # ZW and WZ follow by literal adjacent K inverses. Check every actual
    # normalizer is unitary; no D/K or Q/K commutation is introduced.
    for k in range(8):require(ph.equal(K[k]+ph.adjoint(K[k]),()),'mode unitary exact phase')
    require(all(sum(F(M[k][j]*M[l][j],4) for j in range(112))==14*int(k==l) for k in range(8) for l in range(8)),'ZW14 exterior scalar')
    autonomous=Counter(len(c['frames'][c['final'][j]])-len(c['frames'][c['start'][j]]) for j in range(224,632) if j not in MODE)
    require(autonomous==Counter({4:28,7:7,8:47,9:318}),'400 autonomous helper profile')
    for r in records:
        owner,cache=r['owner'],r['cache_slot'];require(not endpoint[owner],'whole field swap target zero')
        endpoint[owner],endpoint[cache]=endpoint[cache],endpoint[owner]
        require(not endpoint[cache],'owned cache after whole-field/chart swap')
    require(all(not endpoint[j] for j in range(632,641)),'all nine arbitrary-owned outputs zero')
    controls={}
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,StopIteration) as e:controls[name]=str(e)
        else:raise ValueError('negative control accepted '+name)
    mutated=copy.deepcopy(program);idx=next(i for i,e in enumerate(mutated) if e[0]=='scalar' and e[1][0]=='copy' and e[1][1][1]>0);mutated[idx][1][2][1]+=1
    reject('actual_cache_source_changed',lambda:interpret(c,mutated,owned,require_owned_return=False))
    mutated=copy.deepcopy(program);idx=next(i for i,e in enumerate(mutated) if e[0]=='scalar' and e[1][0]=='clear');mutated[idx][1][1]=['L',224]
    reject('actual_borrowed_erasure',lambda:interpret(c,mutated,owned,require_owned_return=False))
    mutated=copy.deepcopy(artifact['input_basis_program']);idx=next(i for i,e in enumerate(mutated) if e[0]=='add');mutated[idx][3]=str(F(mutated[idx][3])+1)
    reject('actual_basis_ADD_changed',lambda:require(basis(mutated,identity,c,0)==L,'derived basis matrix changed'))
    reject('same_tableau_wrong_global_phase',lambda:require(ph.equal(K[0]+F8[0]+NN[0]+(('phase',1),),D),'global phase mismatch'))
    reject('wrong_operator_order',lambda:require(ph.equal(NN[0]+F8[0]+K[0],D),'reversed noncommuting factors'))
    reject('false_autonomous_H8_credit',lambda:require(all(not any(112<=j<224 for j in endpoint[owner]) for owner in MODE),'H contains nonzero independent Y columns'))
    reject('false_zero_retag_original_input',lambda:interpret(c,[['zero_retag',224,c['start'][224],c['final'][224]]],owned,require_owned_return=False))
    # The ordinary source mutation runs through the actual same interpreter.
    mutated=copy.deepcopy(program);idx=next(i for i,e in enumerate(mutated) if e[0]=='scalar' and e[1][0]=='add');mutated[idx][1][3]+=1
    def wrong_add():
        rr,_,_=interpret(c,mutated,owned,require_owned_return=False)
        require(rr==raw,'actual source ADD changes complete endpoint')
    reject('actual_native_ADD_changed',wrong_add)
    a=initial(('L',0))
    reject('free_generators_do_not_commute',lambda:require(warped(warped(a,1),2)==warped(warped(a,2),1),'distinct native generators retain order'))
    result={'status':'PASS_INDEPENDENT_COUPLED_PROVIDER_COMPONENT','candidate_head':'3348fccea855082786d5f0fc5558b73d4974e745','all_original_inputs':632,'arbitrary_owned_inputs':9,'owned_outputs_zero':9,'autonomous_helpers':400,'coupled_helpers_without_target_credit':8,'paid':bill['paid'],'source_16_identities':identities,'native_replay':bill,'physical_phase_bindings':dict(counts),'source_derived_E':[{str(j+224):str(a) for j,a in row.items()} for row in E],'basis_roles':roles,'ordinary_basis_counts':{'input':dict(Counter(e[0] for e in artifact['input_basis_program'])),'output':dict(Counter(e[0] for e in artifact['output_basis_program']))},'controls':controls,'consumed_sha256':consumed,'checker_files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')},'runtime_seconds':round(time.monotonic()-start,6),'claims':['X=D x-R y+R W h','Y=D y','H=D(h-Z y)','ZW=14 I8','WZ=I-C'],'limitations':['No autonomous target credit for coupled H.','No caller, kappa, inverse/transpose schedule or outer budget.','Native realization and unchanged helper physical implementations inherited from pinned source.','Phase proof is exact Pauli action plus full zero-column anchor, not flattened all-column physical tape.']}
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'phase_bindings':1240,'controls':list(controls),'seconds':result['runtime_seconds']}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE/'RESULT.json');main(ap.parse_args().out)
