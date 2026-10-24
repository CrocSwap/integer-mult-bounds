#!/usr/bin/env python3
"""Independent whole632+9 parametric promoted local check; root executes.
Whole-job aliases are first signature-bound and collapsed using accepted phase
identities; their generic chirps are NEVER assumed to commute with R. Only the
old Kp/Km generators use the already audited R intertwining. No author evaluator.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict,Counter
from hashlib import sha256
import argparse,copy,importlib.util,json
HERE=Path(__file__).resolve().parent;CALLER=HERE.parent/'caller'
spec=importlib.util.spec_from_file_location('our_old_signed_words',HERE/'check_literal_local.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)


def need(ok,s):
    if not ok:raise ValueError(s)


def norm(w):
    stack=[]
    for a in w:
        if abs(a)==1:
            p=(1 if a>0 else-1)
            if stack and stack[-1][0]=='D':p+=stack.pop()[1]
            if p%4:stack.append(('D',p%4))
        else:
            if abs(a)in old.INVO:a=abs(a)
            if stack and stack[-1][0]=='K'and(stack[-1][1]==-a or(abs(a)in old.INVO and stack[-1][1]==a)):stack.pop()
            else:stack.append(('K',a))
    return tuple(a for k,v in stack for a in([1]*v if k=='D'else[v]))


def app(row,r=0,w=()):
    out=defaultdict(F)
    for(col,p,word),v in row.items():out[col,(p+r)%4,norm(w+word)]+=v
    return {k:v for k,v in out.items()if v}


def add(a,b,q=F(1)):
    out=defaultdict(F,a)
    for k,v in b.items():out[k]+=q*v
    return {k:v for k,v in out.items()if v}


def H(v,m,inverse=False):
    # v is112p+8aux. Exact H=[[C,-W],[Z,I]] orH^-1=[[I,W],[-Z,-13I]].
    out=[]
    for i in range(112):
        row=v[i]
        for k in range(8):
            if not m[k][i]:continue
            if not inverse:
                for j in range(112):
                    if m[k][j]:row=add(row,app(v[j],w=(-(i+2),j+2)),F(-m[k][i]*m[k][j],4))
            row=add(row,app(v[112+k],w=(-(i+2),114+k)),F(m[k][i]if inverse else-m[k][i],2))
        out.append(row)
    for k in range(8):
        row={key:(-13 if inverse else 1)*v for key,v in v[112+k].items()}
        for j in range(112):
            if m[k][j]:row=add(row,app(v[j],w=(-(114+k),j+2)),F(-m[k][j]if inverse else m[k][j],2))
        out.append(row)
    return out


def signatures_match(a,b,cache):
    def sig(word):
        key=json.dumps(word,separators=(',',':'))
        if key not in cache:cache[key]=old.map_signature(word)
        return cache[key]
    return sig(a)==sig(b)


def collapse_aliases(ops,aliases,promoted,cache):
    positions=[i for i,e in enumerate(ops)if e['op'].startswith('PROVIDER_')];need(len(positions)==1,'one exact source provider macro');pos=positions[0];inverse=ops[pos]['op']=='PROVIDER_5411_INVERSE'
    need(pos>=400 and len(ops)>pos+400,'complete wholejob alias blocks')
    for side,block in [('pre',ops[pos-400:pos]),('post',ops[pos+1:pos+401])]:
        targets={}
        key='remaining392_'+('inverse'if inverse else'forward')+('_pre_input_maps'if side=='pre'else'_post_output_maps')
        for e in aliases[key]:targets[f"owner{e['owner']}"]=e['word']
        for k,owner in enumerate(promoted):
            src='promoted8_post_output_maps'if(inverse and side=='pre')else'promoted8_pre_input_maps'if(inverse and side=='post')else'promoted8_pre_input_maps'if side=='pre'else'promoted8_post_output_maps'
            word=next(e['word']for e in aliases[src]if e['owner']==owner)
            if inverse:
                # Compare using full signed inverse, no candidate inverse-word code.
                expected=old.inverse_signature(old.map_signature(word));actual=old.map_signature(next(e['word']for e in block if e.get('field')==f'k{k}'))
                need(actual==expected,'actual promoted inverse D8 boundary word')
                targets[f'k{k}']=None
            else:targets[f'k{k}']=word
        need(len(block)==400 and {e.get('field')for e in block}==set(targets),'all392+8 exact owner aliases once')
        for e in block:
            need(e['op']=='MONOMIAL','wholejob alias contains onlymonomial')
            if targets[e['field']]is not None:need(signatures_match(e['word'],targets[e['field']],cache),'wholejob literal signed phase alias changed')
    return ops[:pos-400]+[ops[pos]]+ops[pos+401:],inverse


def run_local(data,direction,p,m,signs,aliases,proof,cache):
    promoted=[449,451,453,455,482,483,492,502];mode=p['mode_owners'];remaining=sorted(set(range(224,632))-set(mode)-set(promoted))
    mapping={**{f'x{i}':i for i in range(112)},**{f'y{i}':112+i for i in range(112)},**{f'h{k}':r for k,r in enumerate(mode)},**{f'k{k}':r for k,r in enumerate(promoted)},**{f'owner{r}':r for r in remaining},**{f'c{k}':632+k for k in range(9)}}
    need(len(mapping)==641 and len(set(mapping.values()))==641,'all632persistent+9owned independent IDs')
    rows={name:{(j,0,()):F(1)}for name,j in mapping.items()};orig=copy.deepcopy(rows)
    ops,inverse=collapse_aliases(data['operations'],aliases,promoted,cache);counts=Counter();paid=Counter();ground={};nmacro=0
    for e in ops:
        op=e['op'];counts[op]+=1
        if op=='MONOMIAL':
            f=e['field'];need(f in rows and not f.startswith('owner'),'no unbound helper alias remains');word=e['word']
            if word in([['X',1]],[['X',510]]):
                rows[f]=app(rows[f],r=2,w=(-1,-1))if word==[['X',1]]else app(rows[f],w=(1,1))
            else:
                b=f[0];i=int(f[1:]);idx=i if b in('x','y')else 112+i-1 if b=='c'else 112+i
                need(b in('x','y','h','c')and 0<=idx<120,'old K sourcefield')
                sig=old.map_signature(word)
                if sig==signs[idx]:letter=idx+2
                elif sig==old.inverse_signature(signs[idx]):letter=-(idx+2)
                else:raise ValueError('ordinary old K signed map differs')
                rows[f]=app(rows[f],w=(letter,))
        elif op=='ADD':need(e['dst']in rows and e['src']in rows and e['dst']!=e['src'],'distinct typed ADD');rows[e['dst']]=add(rows[e['dst']],rows[e['src']],F(e['coefficient']))
        elif op=='CLEAR':need(e['field'].startswith('c')and e.get('owned')is True,'CLEAR only9owned');rows[e['field']]={};ground[e['field']]=False
        elif op=='COPY':
            need(e['dst'].startswith('c')and not rows[e['dst']]and e['src']in rows and ground.get(e['dst'])is True,'COPY complete zero owned ground-chart destination');rows[e['dst']]=dict(rows[e['src']])
        elif op=='ZERO_RETAG':need(e['field'].startswith('c')and not rows[e['field']]and e['new_chart']=='ground','actual complete zero ground retag');ground[e['field']]=True
        elif op=='GAUSSIAN':
            need(e.get('paid')is True and e['rank']==1 and e['operator']=='Q_h','only8actual paid observationQh');rows[e['field']]=app(rows[e['field']],r=1,w=(-1,));paid[1]+=1
        elif op=='SWAP':
            need(e.get('includes_chart')is True,'wholefield chart SWAP');a,b=e['fields'];rows[a],rows[b]=rows[b],rows[a]
        elif op.startswith('PROVIDER_'):
            nmacro+=1;need(e['owned_fields']==[f'c{k}'for k in range(9)],'same9ownedsourcebank')
            if inverse:
                need(proof['status']=='PASS_REVERSE_ONLY_NATIVE_INVERSE_DELTA'and e['source_head']=='123ffa6aa7c1866ac60c67739841f71d95b3edf7'and e['inverse_of_provider_head']=='3348fccea855082786d5f0fc5558b73d4974e745','independent641inverseaccepted exact source')
                need({int(k):v for k,v in e['paid'].items()}=={int(k):v for k,v in proof['paid'].items()},'source inverse paid binding')
                for name,digest in e['source_hashes'].items():need(sha256((HERE.parent/'source/pr5411'/name).read_bytes()).hexdigest()==digest,'exact inverse proof/source record')
            else:need(e['provider_sha256']==sha256(old.PROVIDER.read_bytes()).hexdigest(),'exactforwardprovidermacro')
            oldrows=copy.deepcopy(rows)
            for k in range(9):rows[f'c{k}']={};ground[f'c{k}']=False
            for i in range(112):
                if not inverse:
                    row=add(app(oldrows[f'x{i}'],w=(1,)),app(oldrows[f'y{i}'],r=1),-1)
                    for k in range(8):
                        if m[k][i]:row=add(row,app(oldrows[f'h{k}'],r=1,w=(-(i+2),114+k)),F(m[k][i],2))
                else:
                    row=add(app(oldrows[f'x{i}'],w=(-1,)),app(oldrows[f'y{i}'],r=1,w=(-1,-1)))
                    for k in range(8):
                        if m[k][i]:
                            row=add(row,app(oldrows[f'h{k}'],r=1,w=(-1,-(i+2),114+k,-1)),F(-m[k][i],2))
                            for j in range(112):
                                if m[k][j]:row=add(row,app(oldrows[f'y{j}'],r=1,w=(-1,-(i+2),j+2,-1)),F(-m[k][i]*m[k][j],4))
                rows[f'x{i}']=row;rows[f'y{i}']=app(oldrows[f'y{i}'],w=(-1,)if inverse else(1,))
            for k in range(8):
                row=app(oldrows[f'h{k}'],w=(-1,))if inverse else oldrows[f'h{k}']
                for j in range(112):
                    if m[k][j]:row=add(row,app(oldrows[f'y{j}'],w=(-(114+k),j+2,-1)if inverse else(-(114+k),j+2)),F(m[k][j]if inverse else-m[k][j],2))
                rows[f'h{k}']=row if inverse else app(row,w=(1,));rows[f'k{k}']=app(oldrows[f'k{k}'],w=(-1,)if inverse else(1,))
            for owner in remaining:rows[f'owner{owner}']={(owner,0,(10000+owner,)):F(1)} # independently proved positive wholejob alias
        else:raise ValueError('unsupported literal instruction '+op)
    U=[orig[f'x{i}']for i in range(112)]+[orig[f'k{k}']for k in range(8)];V=[orig[f'y{i}']for i in range(112)]+[orig[f'h{k}']for k in range(8)]
    if direction=='B':uu=[add(app(u,w=(1,)),app(z,r=1),-1)for u,z in zip(U,H(V,m))];vv=[app(v,w=(1,))for v in V]
    elif direction=='inverse':uu=[add(app(u,w=(-1,)),app(z,w=(-1,)))for u,z in zip(U,H([app(v,r=1,w=(-1,))for v in V],m))];vv=[app(v,w=(-1,))for v in V]
    else:uu=[app(u,w=(1,))for u in U];vv=[add(app(v,w=(1,)),app(z,w=(1,)))for v,z in zip(V,H([app(u,r=3,w=(1,))for u in U],m))]
    expected={**{f'x{i}':uu[i]for i in range(112)},**{f'k{k}':uu[112+k]for k in range(8)},**{f'y{i}':vv[i]for i in range(112)},**{f'h{k}':vv[112+k]for k in range(8)},**{f'c{k}':{}for k in range(9)},**{f'owner{r}':{(r,0,(10000+r,)):F(1)}for r in remaining}}
    need(rows==expected,'full632+9 endpoint differs from exact ordered '+direction)
    need(nmacro==1 and paid==Counter({1:8}),'one source macro+8paidH1; helpersnotduplicated')
    need(data['helper_profile']=={'4':28,'7':7,'8':39,'9':318},'actual392targetdebit')
    return {'status':'PASS_'+direction,'original_columns':632,'arbitrary_owned_columns':9,'positive_autonomous_helpers':392,'paid_extra_H1':8,'raw_macro_counts':dict(counts),'alias_maps':800,'native_direction':'inverse'if inverse else'forward','main_rows':240,'inverse_scope':'maininverseplus392positivejobs;notinverseofalreadypositivehelperABI'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();p,m,signs=old.initialize();aliases= json.loads((HERE/'CURRENT-HELPER-ALIASES-v2.json').read_text());proof=json.loads((HERE/'INVERSE-DELTA-RESULT-v2.json').read_text());cache={}
    acceptance=json.loads((HERE/'HELPER-ALIAS-RESULT-v2.json').read_text());need(acceptance['aliases_sha256']==sha256((HERE/'CURRENT-HELPER-ALIASES-v2.json').read_bytes()).hexdigest(),'authenticated executed helper alias bytes');need(proof['checker_sha256']==sha256((HERE/'check_inverse_delta_v2.py').read_bytes()).hexdigest(),'authenticated independent inverse checker bytes')
    names={'B':'PARAMETRIC-BACKWARD-v14.json','inverse':'PARAMETRIC-INVERSE-v14.json','F':'PARAMETRIC-FORWARD-v14.json'};documents={d:json.loads((CALLER/n).read_text())for d,n in names.items()};results={d:run_local(a,d,p,m,signs,aliases,proof,cache)for d,a in documents.items()};controls=[]
    def reject(label,d,mutate):
        a=copy.deepcopy(documents[d]);mutate(a)
        try:run_local(a,d,p,m,signs,aliases,proof,cache)
        except(ValueError,KeyError,IndexError)as ex:controls.append({'name':label,'rejected':True,'reason':str(ex)});return
        raise ValueError('acceptedactualv14mutant '+label)
    reject('wrong observation sign','B',lambda a:next(e for e in a['operations']if e['op']=='ADD'and e['dst'].startswith('k')).__setitem__('coefficient','1'))
    reject('missing owned initialization','B',lambda a:a['operations'].pop(next(i for i,e in enumerate(a['operations'])if e['op']=='CLEAR')))
    reject('nonzero cache retag','B',lambda a:a['operations'].pop(next(i for i,e in enumerate(a['operations'])if e['op']=='CLEAR'and i>0 and a['operations'][i-1].get('op')=='ADD'and a['operations'][i-1].get('dst','').startswith('k'))))
    reject('missing owned ground retag','B',lambda a:a['operations'].pop(next(i for i,e in enumerate(a['operations'])if e['op']=='ZERO_RETAG')))
    reject('omitted paid observation','inverse',lambda a:a['operations'].pop(next(i for i,e in enumerate(a['operations'])if e['op']=='GAUSSIAN')))
    reject('wrongforwardnativeq²mask','F',lambda a:a['operations'][0].__setitem__('word',[['X',511]]))
    reject('SWAPwithoutchart','F',lambda a:next(e for e in a['operations']if e['op']=='SWAP').__setitem__('includes_chart',False))
    out={'schema':'independent-parametric632plus9-local-v14','status':'PASS_B_MAIN_INVERSE_AND_PROPER_F_COMPONENTS','results':results,'controls':controls,'alias_boundaries':'Allactual400pre+400postwordsliteralphaseboundbeforecollapse; noRcommutationwithnewaliaschirps assumed','source_macro':'Frozen5402forwardplusindependentlyverified5411reverse-only641columnplan; noauthororacle/providerphasereplay','checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'source_hashes':{str(x.relative_to(old.BASE)):sha256(x.read_bytes()).hexdigest()for x in[HERE/'check_literal_local.py',HERE/'CURRENT-HELPER-ALIASES-v2.json',HERE/'INVERSE-DELTA-RESULT-v2.json']+[CALLER/n for n in names.values()]},'complete_caller':False,'new_kappa':None,'remaining':'Actualglobalcaller/terminalGaussiancontracts/allordinaryrecursionprecisionstoragecompilerandouterfunding.'}
    need(not args.output.exists(),'immutable result exists');args.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()
