#!/usr/bin/env python3
"""Check the sign-metric response with integer real matrices."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
CAMPAIGN=HERE.parents[2]
PINS={
    'root/SIGN-METRIC-FREEZE-20261020.json':'33c920f59ef3e2c644ba5c798a81bda257863e5e3a9cef68fba46968332471b1',
    'root/sign-metric-normal-20261020/RESPONSE.json':'9ae1c4bf391f8ac082d2137e686f7de474005002399648bff5d443c3bc215c9c',
    'lanes/controller-followthrough-20261017/row-involution-20261020/run-normal/ROW-INVOLUTION.json':
        'a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b',
    'lanes/independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json':
        '3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585',
}


def need(condition,label):
    if not condition:
        raise ValueError(label)


def load(path):
    raw=(CAMPAIGN/path).read_bytes()
    need(sha256(raw).hexdigest()==PINS[path],'Source pin '+path)
    return json.loads(raw)


def eye(n,scale=1):
    return [{i:scale} for i in range(n)]


def scale(a,c):
    return [{j:c*v for j,v in row.items() if c*v} for row in a]


def plus(a,b):
    result=[]
    for x,y in zip(a,b):
        row=dict(x)
        for j,c in y.items():
            row[j]=row.get(j,0)+c
            if not row[j]:
                del row[j]
        result.append(row)
    return result


def times(a,b):
    out=[]
    for source in a:
        row={}
        for j,x in source.items():
            for k,y in b[j].items():
                row[k]=row.get(k,0)+x*y
        out.append({j:c for j,c in row.items() if c})
    return out


def transpose(a,width):
    out=[{} for _ in range(width)]
    for i,row in enumerate(a):
        for j,v in row.items():
            out[j][i]=v
    return out


def realify(rows,width,denominator=1):
    n=len(rows)
    out=[{} for _ in range(2*n)]
    for i,row in enumerate(rows):
        for key,value in row.items():
            j=int(key)
            a,b=[Q(v)*denominator for v in value]
            need(a.denominator==b.denominator==1,'Integer realification')
            a,b=int(a),int(b)
            if a:
                out[i][j]=a;out[n+i][width+j]=a
            if b:
                out[i][width+j]=-b;out[n+i][j]=b
    return out


def real_rows(rows):
    return [{str(j):[str(v),'0'] for j,v in row.items()} for row in rows]


def block_support(a,i,n=112):
    return {j for j in range(n) if a[i].get(j,0) or a[n+i].get(j,0)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=HERE/'run-normal')
    args=parser.parse_args()
    freeze=load('root/SIGN-METRIC-FREEZE-20261020.json')
    for name,pin in freeze['files'].items():
        need(sha256((CAMPAIGN/'root'/name).read_bytes()).hexdigest()==pin,'Frozen root file '+name)
    packet=load('root/sign-metric-normal-20261020/RESPONSE.json')
    prior=load('lanes/controller-followthrough-20261017/row-involution-20261020/run-normal/ROW-INVOLUTION.json')
    pairs=load('lanes/independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json')
    selected=set(prior['pivots'])|{2,25,13,51,11,63,42,105}
    need(sorted(selected)==packet['selected'] and len(selected)==24,'Actual24 selected ports')
    h=eye(112)
    large=set()
    closed_pairs=[]
    for pair in pairs['pair_codes']:
        p,q=pair['ports']
        need((p in selected)==(q in selected),'Every physical pair is closed')
        large.update((p,q))
        if p in selected:
            closed_pairs.append([p,q])
        for row,target in zip(pair['matrix'],(p,q)):
            h[target]={j:int(v) for j,v in zip((p,q),row) if v}
    ht=transpose(h,112)
    gram=times(ht,h)
    need(gram==[{i:2 if i in large else 1} for i in range(112)],'Actual H*H block scales')
    hi2=[{j:(1 if i in large else 2)*c for j,c in ht[i].items()} for i in range(112)]
    need(times(hi2,h)==times(h,hi2)==eye(112,2),'Actual pair inverse without division')
    H=realify(real_rows(h),112)
    R=realify(real_rows(hi2),112)
    D=realify(real_rows([{i:-1 if i in selected else 1} for i in range(112)]),112)
    need(D==realify(packet['metric'],112),'Actual sign metric')
    need(times(D,H)==times(H,D),'Metric and physical pair code commute')
    w=[{} for _ in range(112)]
    occupied=[]
    kinds=Counter()
    for k,block in enumerate(prior['blocks']):
        ports=block['ports']
        occupied.extend(ports)
        picks=sorted(selected.intersection(ports))
        need(len(picks)==(2 if len(ports)==6 else 1),'Actual block exceptions')
        values={}
        for p,d in zip(ports,block['signs']):
            values[str(p)]=[str(Q(d)),str(2*Q(d) if len(ports)==8 and p in selected else 0)]
            w[p][str(k)]=values[str(p)]
        need(packet['blocks'][k]=={'ports':ports,'selected':picks,'w':values},'Independent block reconstruction')
        kinds[len(ports)]+=1
    need(sorted(occupied)==list(range(112)) and kinds=={6:8,8:8},'Sixteen disjoint complete blocks')
    W=realify(w,16)
    V=scale(times(transpose(W,32),D),-1)
    need(times(V,W)==eye(32,-2),'Sixteen independent reflection contractions')
    S=plus(eye(224),times(W,V))
    A2=times(times(R,S),H)
    A2_saved=realify(packet['response'],112,2)
    need(A2==A2_saved,'All112 complex columns from independent integer reconstruction')
    need(S==realify(packet['mode_response'],112),'Mode response')
    need(times(A2,A2)==eye(224,4),'Physical involution')
    need(transpose(A2,224)==times(times(D,A2),D),'Physical adjoint and sign metric')
    need(times(times(transpose(A2,224),D),A2)==scale(D,4),'Metric preservation')
    need(transpose(A2,224)==realify(packet['response_adjoint'],112,2),'Serialized physical adjoint')
    U2=times(R,W)
    VP=times(V,H)
    need(U2==realify(packet['correction_U'],16,2),'Serialized physical correction U')
    need(VP==realify(packet['correction_V'],112),'Serialized physical correction V')
    need(times(VP,U2)==eye(32,-4),'Exact correction rank16')
    need(A2==plus(eye(224,2),times(U2,VP)),'Physical displacement factorization')
    diagonal={i:A2[i].get(i,0)//2 for i in range(112) if A2[i].get(i,0)}
    need(set(diagonal)==selected and Counter(diagonal.values())=={2:16,6:8},'Exact physical diagonal exceptions')
    need(sum(diagonal.values())==80,'Trace80')
    old2=realify([{j:[c,'0'] for j,c in row.items()} for row in prior['original_response']],112,2)
    ordinary=set(range(112))-selected
    for i in ordinary:
        need(block_support(A2,i)==block_support(old2,i),'Ordinary physical row support')
        for j in ordinary:
            need(A2[i].get(j,0)==old2[i].get(j,0) and A2[112+i].get(j,0)==old2[112+i].get(j,0),
                 'Ordinary physical principal block')
    changed_columns=[]
    for j in selected:
        if any(A2[i].get(j,0)!=old2[i].get(j,0) or A2[112+i].get(j,0)!=old2[112+i].get(j,0) for i in ordinary):
            changed_columns.append(j)
    need(set(changed_columns)==selected,'Every selected column changes in ordinary rows')
    # Use a noncommuting diagonal unitary to check the exact mixed-phase order.
    zrows=[{i:['0','1'] if i==1 else ['1','0']} for i in range(112)]
    Z=realify(zrows,112);Zi=transpose(Z,224)
    E2=times(Z,A2)
    Einv2=times(A2,Zi)
    need(times(E2,Einv2)==times(Einv2,E2)==eye(224,4),'Mixed-phase inverse')
    need(times(times(D,transpose(E2,224)),D)==Einv2,'Mixed-phase adjoint conversion')
    need(times(A2,Z)!=times(Z,A2),'Noncommuting phase witness')
    complex_conjugation=[{i:1 if i<112 else -1} for i in range(224)]
    bilinear=times(times(complex_conjugation,transpose(A2,224)),complex_conjugation)
    need(bilinear!=transpose(A2,224) and times(times(D,bilinear),D)!=A2,'Transpose mutation rejected')
    need(transpose(A2,224)!=A2,'Omitting metric signs fails')
    # Moving only one member of a pair breaks the physical diagonal metric.
    wrongD=[dict(row) for row in D]
    p=closed_pairs[0][0]
    wrongD[p][p]*=-1;wrongD[112+p][112+p]*=-1
    need(times(wrongD,H)!=times(H,wrongD),'Pair-closure mutation rejected')
    need(times(times(wrongD,A2),wrongD)!=transpose(A2,224),'Wrong physical metric rejected')
    # A size-six rank-one sign reflection with one exception has norm4, not2.
    bad=[{j:(1 if i==j else 0)-(1 if j<5 else -1) for j in range(6)} for i in range(6)]
    bad=[{j:v for j,v in row.items() if v} for row in bad]
    need(times(bad,bad)!=eye(6),'One-exception real-sign mutation rejected')
    need([(a,b) for a in range(3) for b in range(3) if (a*a+b*b)%3==0]==[(0,0)],'Norm3 rational descent residue')
    swaps=[{i^1:1} for i in range(6)]
    need(times(swaps,swaps)==eye(6) and all(i not in row for i,row in enumerate(swaps)),
         'Higher-rank zero-exception counterexample')
    uneven=[{j:(1 if i==j else 0)-(1 if j<5 else -3) for j in range(6)} for i in range(6)]
    uneven=[{j:v for j,v in row.items() if v} for row in uneven]
    need(times(uneven,uneven)==eye(6) and [row.get(i,0) for i,row in enumerate(uneven)]==[0,0,0,0,0,4],
         'Unequal-metric one-exception counterexample')
    for mask in range(64):
        signs=[{i:-1 if (mask>>i)&1 else 1} for i in range(6)]
        need(times(times(signs,uneven),signs)!=transpose(uneven,6),'No diagonal sign metric for counterexample')
    receipt={
        'status':'PASS_INDEPENDENT_SIGN_METRIC_REVIEW',
        'source_pins':PINS,
        'engine':'Integer realification; no producer code or Gaussian pair arithmetic imported',
        'complex_ports':112,'real_integer_matrix_rows':224,
        'correction_rank_over_Gaussian_rationals':16,
        'selected_ports':sorted(selected),'closed_selected_pairs':closed_pairs,
        'diagonal_values':diagonal,'trace':80,'determinant':1,
        'determinant_reason':'Sixteen disjoint rank-one reflections each have determinant minus one',
        'ordinary_physical_support_preserved':True,
        'ordinary_physical_principal_block_preserved':True,
        'selected_columns_changed_in_ordinary_rows':sorted(changed_columns),
        'mutation_checks':['bilinear transpose','missing sign metric','broken physical pair closure','one-exception real signs'],
        'mixed_phase_noncommutation_witness':True,
        'outside_scope_counterexamples':['rank3 zero-exception involution','rank1 one-exception involution with unequal metric magnitudes'],
        'one_exception_bound_scope':'Rank-one reflection with a diagonal sign metric over Gaussian rationals; independent six/eight coordinate blocks',
        'native_word_or_invoice_reviewed':False,
        'producer_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'CHECKS.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_pins','diagonal_values')},sort_keys=True))


if __name__=='__main__':
    main()
