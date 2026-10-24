#!/usr/bin/env python3
"""Independent literal augmented LOCAL checker. Root executes only.

Fresh signed-permutation interpreter; no submitted evaluator import. The frozen
provider is a previously audited macro, NOT freshly replayed native physics.
Group ring normal form R^r * free(D,K0,...,K119) retains [D,Q]=0, DQ=R,
and [R,K]=0 but does not introduce [D,K] or [Q,K].
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from functools import lru_cache
from hashlib import sha256
import argparse, copy, json
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[2]
PROVIDER=BASE/'swarm-provider-audit-sol-high-20261024/repository/research/native-rank8-helper-provider/PROVIDER.json'
INVO=set()
NORMAL=BASE/'swarm-next-gain-sol-high-20261024/repository/research/coded-native-caller/NORMALIZERS.json'


def need(ok,s):
    if not ok:raise ValueError(s)


def wordred(word):
    out=[]
    for a in word:
        if abs(a) in INVO:a=abs(a)
        if out and (out[-1]==-a or (abs(a) in INVO and out[-1]==a)):out.pop()
        else:out.append(a)
    return tuple(out)


def plus(a,b,q=F(1)):
    out=dict(a)
    for k,v in b.items():
        out[k]=out.get(k,F(0))+q*v
        if not out[k]:del out[k]
    return out


def apply(a,r=0,w=()):
    out={}
    for (col,rr,ww),v in a.items():
        key=(col,rr+r,wordred(w+ww))
        out[key]=out.get(key,F(0))+v
        if not out[key]:del out[key]
    return out


def map_signature(word):
    # Each monomial maps |address> to i^phase |address'>. All 512 addresses
    # are compared, including absolute scalar phase.
    out=[]
    for original in range(512):
        addr=original;phase=0
        for g in word:
            if g[0]=='P':
                need(len(g[1])==9,'nine-axis P')
                addr=sum(((row&addr).bit_count()%2)<<j for j,row in enumerate(g[1]))
            elif g[0]=='X':addr^=g[1]
            elif g[0]=='phase':phase+=g[1]
            elif g[0]=='D':
                quad,lin=g[1:]
                phase+=sum(lin[j] for j in range(9) if addr>>j&1)
                phase+=2*sum((quad[j]&addr&~((1<<(j+1))-1)).bit_count()%2 for j in range(9) if addr>>j&1)
            else:raise ValueError('unsupported monomial gate')
        out.append((addr,phase%4))
    need(len({x for x,p in out})==512,'monomial address map invertible')
    return tuple(out)


def inverse_signature(sig):
    out=[None]*512
    for i,(j,p) in enumerate(sig):out[j]=(i,(-p)%4)
    return tuple(out)


def initialize():
    p=json.loads(PROVIDER.read_text());n=json.loads(NORMAL.read_text())
    need(sha256(PROVIDER.read_bytes()).hexdigest()=='676de7551d3364598f4a7e29ae97cae0e4364348786bbe70435b84294ba7dd65','provider pin')
    need(sha256(NORMAL.read_bytes()).hexdigest()=='ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da','normalizer pin')
    matrix=n['mode_columns'];need(len(matrix)==8 and all(len(x)==112 for x in matrix),'mode dimensions')
    need(all(sum(matrix[i][k]*matrix[j][k] for k in range(112))==56*(i==j) for i in range(8) for j in range(8)),'source Gram')
    words=[x['K_word'] for x in n['ports']]+[x['input_K']['literal_word'] for x in p['mode_boundaries']]
    signs=[map_signature(w) for w in words]
    INVO.update(k+2 for k,sig in enumerate(signs) if sig==inverse_signature(sig))
    return p,matrix,signs


def candidate_check(cand,provider,m,signs,cache=True):
    fields=[f'{b}{i}' for b,nn in [('x',112),('y',112),('h',8),('g',8)] for i in range(nn)]
    rows={s:{(j,0,()):F(1)} for j,s in enumerate(fields)}
    orig=copy.deepcopy(rows)
    paid=Counter();provider_calls=0;counts=Counter();sign_cache={}
    for op in cand['operations']:
        name=op['op'];counts[name]+=1
        if name=='MONOMIAL':
            f=op['field'];need(f in rows,'monomial field ownership')
            b=f[0];i=int(f[1:]);need(b in 'xyh','unexpected moved bank')
            k=(i if b in 'xy' else 112+i)
            need((0<=i<(112 if b in 'xy' else 8)),'monomial owner range')
            raw=json.dumps(op['word'],separators=(',',':'))
            sig=sign_cache.get(raw)
            if sig is None:sig=map_signature(op['word']);sign_cache[raw]=sig
            forward=signs[k];backward=inverse_signature(forward)
            if sig==forward:letter=k+2
            elif sig==backward:letter=-(k+2)
            else:raise ValueError('monomial differs from source K or its full signed inverse')
            # If K is involutive the direction is mathematically immaterial.
            rows[f]=apply(rows[f],w=(letter,))
        elif name=='ADD':
            dst,src=op['dst'],op['src'];need(dst in rows and src in rows and dst!=src,'ADD typed fields')
            rows[dst]=plus(rows[dst],rows[src],F(op['coefficient']))
        elif name=='GAUSSIAN':
            f=op['field'];need(f in rows and op.get('paid') is True,'paid Gaussian ownership')
            if op['operator']=='R_h':need(f.startswith('g') and op['rank']==9,'R_h rank9 g');rows[f]=apply(rows[f],r=1)
            elif op['operator']=='Q_h':need(f.startswith('h') and op['rank']==1,'Q_h rank1 h');rows[f]=apply(rows[f],r=1,w=(-1,))
            else:raise ValueError('unknown Gaussian operator')
            paid[op['rank']]+=1
        elif name=='PROVIDER_5402':
            provider_calls+=1
            need(op['provider_sha256']==sha256(PROVIDER.read_bytes()).hexdigest(),'provider macro exact bytes')
            need(op['source_word_payload_sha256']==provider['word_payload_sha256'],'provider literal payload')
            need(op['owned_entry']=='arbitrary' and op['owned_exit']=='zero' and op['owned_fields']==[f'c{i}' for i in range(9)],'provider arbitrary owned bank')
            need(op['input_banks']==['x','y','h','autonomous400'],'provider full original input banks')
            old=copy.deepcopy(rows)
            # W_ik=(M_ki/2)Kp_i^-1 Kh_k; Z_ki=(M_ki/2)Kh_k^-1 Kp_i.
            for i in range(112):
                row=plus(apply(old[f'x{i}'],w=(1,)),apply(old[f'y{i}'],r=1),-1)
                for k in range(8):
                    if m[k][i]:row=plus(row,apply(old[f'h{k}'],r=1,w=(-(i+2),114+k)),F(m[k][i],2))
                rows[f'x{i}']=row;rows[f'y{i}']=apply(old[f'y{i}'],w=(1,))
            for k in range(8):
                row=old[f'h{k}']
                for i in range(112):
                    if m[k][i]:row=plus(row,apply(old[f'y{i}'],w=(-(114+k),i+2)),F(-m[k][i],2))
                rows[f'h{k}']=apply(row,w=(1,))
        else:raise ValueError('unsupported op/borrowed erase')
    need(provider_calls==1,'exactly one source-bound provider')
    need(paid==Counter({1:8,9:8}),'complete supplementary paid profile')
    # Expectation is derived from the full frozen provider identity and source M,
    # not from CANDIDATE.output_equations or declared counts.
    expected={}
    for i in range(112):
        row=plus(apply(orig[f'x{i}'],w=(1,)),apply(orig[f'y{i}'],r=1),-1)
        # -R C y = -R y + R W Z y.
        for k in range(8):
            if not m[k][i]:continue
            for j in range(112):
                if m[k][j]:row=plus(row,apply(orig[f'y{j}'],r=1,w=(-(i+2),j+2)),F(m[k][i]*m[k][j],4))
            row=plus(row,apply(orig[f'g{k}'],r=1,w=(-(i+2),114+k)),F(-m[k][i],2))
        expected[f'x{i}']=row;expected[f'y{i}']=apply(orig[f'y{i}'],w=(1,))
    for k in range(8):
        row=plus(apply(orig[f'h{k}'],r=1),apply(orig[f'g{k}'],r=1),-13)
        for j in range(112):
            if m[k][j]:row=plus(row,apply(orig[f'y{j}'],r=1,w=(-(114+k),j+2)),F(6*m[k][j]))
        expected[f'h{k}']=row;expected[f'g{k}']=apply(orig[f'g{k}'],r=1)
    need(rows==expected,'full unrestricted 240-main endpoint mismatch')
    need(cand['autonomous_helper_targets']=={'4':28,'7':7,'8':47,'9':318},'retained 400 helper contract; h/g earn no autonomous credit')
    need(cand['input_banks']=={'x':112,'y':112,'h':8,'g':8,'autonomous400':400},'all 640 persistent directions')
    return {'operations':dict(counts),'paid':dict(paid),'independent_main_columns':240,'retained_autonomous_helpers':400,'owned_macro_contract':9,'monomial_occurrences':counts['MONOMIAL'],'distinct_literal_monomial_words':len(sign_cache),'address_phase_checks':512*len(sign_cache),'provider_macro_replayed':False}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    provider,m,signs=initialize();cand=json.loads(args.candidate.read_text())
    result=candidate_check(cand,provider,m,signs)
    controls=[]
    def reject(label,mutate):
        bad=copy.deepcopy(cand);mutate(bad)
        try:candidate_check(bad,provider,m,signs)
        except ValueError as e:controls.append({'name':label,'rejected':True,'reason':str(e)});return
        raise ValueError('negative control accepted '+label)
    def change_add(c):
        e=next(e for e in c['operations'] if e['op']=='ADD');e['coefficient']=str(F(e['coefficient'])+1)
    reject('actual prefeed coefficient changed',change_add)
    def phase(c):next(e for e in c['operations'] if e['op']=='MONOMIAL')['word'].append(['phase',2])
    reject('absolute phase changed on actual monomial',phase)
    reject('unearned h autonomous helper credit',lambda c:c['autonomous_helper_targets'].__setitem__('8',55))
    reject('Gaussian Q_h charge omitted',lambda c:c['operations'].pop(next(i for i,e in enumerate(c['operations']) if e['op']=='GAUSSIAN' and e['operator']=='Q_h')))
    reject('borrowed main CLEAR',lambda c:c['operations'].append({'op':'CLEAR','field':'x0'}))
    def wrong_order(c):
        ops=c['operations'];last=[e for e in ops if e['op']=='ADD' and e.get('coefficient')=='-14'];need(len(last)==8,'eight final corrections');ops[:]=[e for e in ops if not any(e is x for x in last)];i=next(i for i,e in enumerate(ops) if e['op']=='MONOMIAL' and e['field']=='x0');ops[i:i]=last
    reject('J correction moved before X reads J',wrong_order)
    result.update({'schema':'independent-augmented-local-review-v1','status':'PASS_LOCAL_MACRO_CONTRACT_ONLY','candidate_sha256':sha256(args.candidate.read_bytes()).hexdigest(),'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'source_sha256':{str(p.relative_to(BASE)):sha256(p.read_bytes()).hexdigest() for p in [PROVIDER,NORMAL]},'controls':controls,'complete_caller':False,'new_kappa':None,'boundary':'Inherited source-bound provider macro and its 400 helpers/nine owned zero exits; fresh literal extension only. All-width free-word consequence with exterior coefficients; no complete global caller, phase lowering of inherited Gaussian/provider macros, compiler or funding.'})
    need(not args.output.exists(),'immutable result exists');args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
