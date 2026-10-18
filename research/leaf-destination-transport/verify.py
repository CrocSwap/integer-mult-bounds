"""Exact finite post-leaf destination perturbation envelopes. Apache-2.0."""
from functools import lru_cache
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def reverse(word):
    return tuple((x,y,j,-s) for x,y,j,s in reversed(word))


@lru_cache(None)
def emit(n,x=0,y=1,z=2,offset=0):
    if n==1:return ((x,y,offset,1),)
    left=n//2
    u=emit(left,x,z,z+1,offset)
    v=emit(n-left,z,y,z+1,offset+left)
    return u+v+reverse(u)+reverse(v)


def align(poly,n):
    # One sign variable for each scalar factor and one for the common row sign.
    pivots={}
    for monomial,coefficient in sorted(poly.items()):
        mask=1<<n
        for j in monomial:mask^=1<<j
        rhs=int(coefficient<0)
        while mask:
            k=mask.bit_length()-1
            if k not in pivots:pivots[k]=(mask,rhs);break
            old,value=pivots[k];mask^=old;rhs^=value
        if not mask and rhs:return None
    solution=0
    for k,(mask,rhs) in sorted(pivots.items()):
        if (mask&solution).bit_count()%2!=rhs:solution|=1<<k
    signs=[-1 if solution>>j&1 else 1 for j in range(n)]
    values=[]
    for monomial,coefficient in poly.items():
        value=coefficient
        for j in monomial:value*=signs[j]
        values.append(value)
    need(abs(sum(values))==sum(abs(x) for x in poly.values()),'attainment equations')
    return signs


def literal_column(word,n,factors,start,end,destination):
    need(1<=start<=end<=len(word) and destination==word[start-1][1],'actual post-leaf support')
    need(len(factors)==n and all(abs(x)<=1 for x in factors),'contractive scalar factors')
    column=[0]*((n-1).bit_length()+2);column[destination]=1
    for x,y,j,sgn in word[start:end]:column[y]+=sgn*factors[j]*column[x]
    return column


def census(n,oracle,source):
    dimension=(n-1).bit_length()+2
    peak=1;witness=None;intervals=0
    for orientation in (1,-1):
        word=emit(n) if orientation==1 else reverse(emit(n))
        need(word==tuple(oracle.source_events(source,n,orientation)),'pinned source event sequence')
        for preceding in range(len(word)):
            destination=word[preceding][1]
            column=[{} for _ in range(dimension)];column[destination]={():1}
            intervals+=1
            if witness is None and peak==1:
                witness=(orientation,preceding+1,preceding+1,destination,destination,{():1},[1]*n)
            for step in range(preceding+1,len(word)):
                x,y,j,sgn=word[step]
                for monomial,coefficient in list(column[x].items()):
                    key=(j,)+monomial
                    value=column[y].get(key,0)+sgn*coefficient
                    if value:column[y][key]=value
                    else:column[y].pop(key,None)
                mass=sum(abs(c) for c in column[y].values())
                if mass>peak:peak=mass;witness=None
                if mass==peak and witness is None:
                    signs=align(column[y],n)
                    if signs is not None:
                        witness=(orientation,preceding+1,step+1,destination,y,column[y].copy(),signs)
                intervals+=1
    need(witness is not None,'scalar attainment of envelope')
    orientation,start,end,dest,row,poly,factors=witness
    word=emit(n) if orientation==1 else reverse(emit(n))
    scalar=literal_column(word,n,factors,start,end,dest)
    independent=oracle.two_cut(n,factors,start,end,orientation)
    need(scalar==[r[dest] for r in independent],'separate recursive prefix oracle')
    need(abs(scalar[row])==peak and max(map(abs,scalar))==peak,'sharp scalar bound')
    return {'n':n,'leaf_events_each_orientation':len(word),'post_leaf_intervals':intervals,
            'sharp_envelope':peak,'witness':{'orientation':orientation,'cuts':[start,end],
            'injected_destination':dest,'attaining_row':row,'factors':factors,'column':scalar,
            'polynomial':[[list(m),c] for m,c in sorted(poly.items())]}}


def run():
    for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if row['usage']=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source '+row['path'])
    path=ROOT/'research/dirty-interval-coefficient-boundary/oracle.py'
    spec=importlib.util.spec_from_file_location('retained_prefix_oracle',path)
    oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
    source=ROOT/'research/dirty-cubic-precision/vendor/628/dirty.py'
    rows=[census(n,oracle,source) for n in range(1,33)]
    # Literal complete sign enumeration provides another independent small-domain check.
    exhaustive=0
    for n in range(1,7):
        best=1
        for bits in range(1<<n):
            factors=[-1 if bits>>j&1 else 1 for j in range(n)]
            for word in (emit(n),reverse(emit(n))):
                for cut in range(1,len(word)+1):
                    col=[0]*((n-1).bit_length()+2);col[word[cut-1][1]]=1
                    best=max(best,max(map(abs,col)));exhaustive+=1
                    for x,y,j,s in word[cut:]:
                        col[y]+=s*factors[j]*col[x]
                        best=max(best,abs(col[y]));exhaustive+=1
        need(best==rows[n-1]['sharp_envelope'],'all scalar signs independent census')
    controls=[]
    w=emit(4);fixture=rows[3]['witness'];a,b=fixture['cuts'];dest=fixture['injected_destination']
    for name,call in [('wrong_support',lambda:literal_column(w,4,[1]*4,a,b,(dest+1)%4)),
                      ('noncontractive',lambda:literal_column(w,4,[2]*4,a,b,dest)),
                      ('pre_word_injection',lambda:literal_column(w,4,[1]*4,0,b,dest))]:
        try:call()
        except ValueError:controls.append(name)
        else:raise ValueError('invalid transport domain accepted')
    need(rows[15]['sharp_envelope']==4,'n16 destination envelope')
    # The existing joint-disturbance witness is outside the single-destination claim.
    matrix=oracle.two_cut(4,[1,1,-1,1],2,6)
    joint=max(sum(map(abs,r)) for r in matrix)
    need(joint==6 and joint>rows[3]['sharp_envelope'],'joint-support boundary control')
    controls.append('joint_support_exceeds_destination_bound')
    need(abs(rows[15]['witness']['column'][rows[15]['witness']['attaining_row']])>3,'understated_bound_rejected')
    controls.append('n16_bound_three_rejected')
    return {'status':'PASS_LEAF_DESTINATION_TRANSPORT','domain':'n=1..32, both word orientations, all post-complete-leaf destinations and every later cut',
            'rows':rows,'total_post_leaf_intervals':sum(r['post_leaf_intervals'] for r in rows),
            'independent_scalar_sign_intervals':exhaustive,'controls':controls,
            'n4_joint_control':int(joint),'all_size_claim':False,'new_kappa':False}


if __name__=='__main__':
    result=run()
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:need(result==json.loads((HERE/'RESULT.json').read_text(encoding='utf-8')),'receipt')
    print(result['status'],'intervals='+str(result['total_post_leaf_intervals']),
          'maxima='+','.join(str(r['sharp_envelope']) for r in result['rows']))
