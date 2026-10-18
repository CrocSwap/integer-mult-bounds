#!/usr/bin/env python3
"""Operand-weighted all-cut P104 feedback. ywz65/Codex; Apache-2.0."""
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def norm(row):return sum(map(abs,row.values()),Q(0))
def encode(row):return [[j,str(q)] for j,q in sorted(row.items()) if q]


def source():
    refs=json.loads((HERE/'REFERENCES.json').read_bytes())
    need(len(refs['files'])==5,'source inventory')
    for r in refs['files']:
        raw=(HERE/r['local']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==r['sha256'],'source SHA256: '+r['local'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob'],'source blob')
    spec=importlib.util.spec_from_file_location('pinned_precision',HERE/'source/verify.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


def ideal_operands(program,roles):
    """New Fraction input-row pass; measure operands BEFORE each instruction."""
    rows=[{i:Q(1)} for i in range(roles)];weights=[];flat=[];peaks=Q(1)
    for e in program:
        if e.op=='add':
            a=norm(rows[e.dst])+abs(e.coefficient)*norm(rows[e.src]);w=1+abs(e.coefficient)
        elif e.op=='scale':a=abs(e.coefficient)*norm(rows[e.dst]);w=abs(e.coefficient)
        elif e.op=='transport':a=norm(rows[e.dst]);w=Q(1)
        else:a=w=Q(0)
        weights.append(a);flat.append(w)
        if e.op=='reset':rows[e.dst]={}
        elif e.op=='add':
            out=rows[e.dst].copy()
            for k,q in rows[e.src].items():
                out[k]=out.get(k,Q(0))+e.coefficient*q
                if not out[k]:del out[k]
            rows[e.dst]=out
        elif e.op=='scale':rows[e.dst]={k:e.coefficient*q for k,q in rows[e.dst].items()}
        if e.op!='exact':peaks=max(peaks,norm(rows[e.dst]))
    return weights,flat,rows,peaks


def forward(m,program,weights,roles):
    """Reuse authenticated source integer-row arithmetic with new site weights.

    Directly recompute each changed row's weighted sum, rather than trusting
    its incremental cache. The source implementation is credited, not called
    an independent checker.
    """
    bits=max(q.denominator.bit_length()-1 for q in weights)
    ints=tuple(int(q*(1<<bits)) for q in weights)
    rows=[m.DyadicRow(ints) for _ in range(roles)]
    peak=(Q(0),-1,0,{})
    stream=hashlib.sha256();sites=zero=0
    for j,e in enumerate(program):
        if e.op=='exact':continue
        m.update(rows,e,ints)
        if e.op in ('add','scale','transport'):
            rows[e.dst].inject(j);sites+=1;zero+=not weights[j]
        r=rows[e.dst]
        direct=sum(abs(v)*ints[k] for k,v in r.values.items())
        need(direct==r.weighted,'new weighted row cache')
        value=Q(direct,1<<(r.exponent+bits))
        stream.update(canonical([j,e.dst,str(value)]).encode()+b'\n')
        if value>peak[0]:peak=(value,j,e.dst,r.coefficients())
    return peak,rows,stream.hexdigest(),sites,zero


def reverse(program,cut,target,roles):
    """Separate sparse Fraction covector pass, without source row machinery."""
    row={target:Q(1)};defects={}
    for j in range(cut,-1,-1):
        e=program[j]
        if e.op=='exact':continue
        q=row.get(e.dst,Q(0))
        if e.op in ('add','scale','transport') and q:defects[j]=q
        if e.op=='reset':row.pop(e.dst,None)
        elif e.op=='scale':
            if q:row[e.dst]=q*e.coefficient
        elif e.op=='add' and q:
            row[e.src]=row.get(e.src,Q(0))+q*e.coefficient
            if not row[e.src]:del row[e.src]
    return row,defects


def inject(program,cut,target,defects,roles):
    state=[Q(0)]*roles
    for j,e in enumerate(program[:cut+1]):
        if e.op=='reset':state[e.dst]=Q(0)
        elif e.op=='add':state[e.dst]+=e.coefficient*state[e.src]
        elif e.op=='scale':state[e.dst]*=e.coefficient
        if j in defects:state[e.dst]+=defects[j]
    return state[target]


def guard(J,K,b):
    need(J>0 and K>=0 and type(b) is int and b>=0,'feedback domain')
    return next(g for g in range(1025) if 2**g>=J+K/Q(2**b) and 2**(b+g)>K)


def controls(m):
    I=m.Instruction
    # y+=x; y-=x: the second operation reads a large pre-operation y,
    # although its ideal endpoint is small. Endpoint weighting is unsound.
    prog=[I('add',1,0,Q(1)),I('add',1,0,Q(-1))]
    a,w,rows,_=ideal_operands(prog,2)
    need(a==[2,3] and norm(rows[1])==1,'operand chronology control')
    need(a[1]>norm(rows[1]) and a[1]>Q(1),'destination and source contributions')
    # Absolute coefficient and scaling are needed even for signed gates.
    a,_,_,_=ideal_operands([I('add',1,0,Q(-8)),I('scale',0,coefficient=Q(-4))],2)
    need(a==[9,4],'signed magnitude control')
    # A reset kills only the current row; an escaped defect must survive.
    prog=[I('add',1,0,Q(1)),I('add',2,1,Q(1)),I('reset',1)]
    _,d=reverse(prog,2,2,3);need(d=={1:Q(1),0:Q(1)},'escaped private defect')
    # Replacing a perturbed operand by its ideal value drops real feedback.
    u=Q(1,4);actual=(1+u)**2-1;linear=2*u
    need(actual>linear and actual<=linear/(1-2*u),'relative feedback cannot be discarded')
    # Large actual error can persist at an ideal-zero register. Such sites
    # remain in K even though their new ideal weight is zero.
    prog=[I('reset',1),I('add',1,0,Q(1)),I('add',1,0,Q(-1)),I('transport',1,rank=1)]
    a,w,_,_=ideal_operands(prog,2)
    need(a[-1]==0 and w[-1]==1,'zero ideal does not make native feedback free')
    return ['pre-operation rather than endpoint norms','both addition operands',
            'absolute signed coefficients and scaling','escaped defects survive reset',
            'feedback term required','zero-ideal native site remains charged']


def run():
    m=source();word=m.load_word(HERE/'source/WORD.json.gz');program=m.normalize(word)
    old=m.analyze(program);m.endpoint_check(old,word['live_ports']);m.check_peaks(program,old)
    retained=m.summarize(program,word,old)
    need(canonical(retained)==canonical(json.loads((HERE/'source/RESULT.json').read_bytes())),'complete original receipt')
    a,w,ideal,P=ideal_operands(program,844)
    need(w==old['weights'] and P==old['peaks'][0][0],'independent ideal/flat weights')
    need(all(row==old['inputs'][i].coefficients() for i,row in enumerate(ideal)),'all844 independent ideal endpoints')
    peak,errors,digest,sites,zero=forward(m,program,a,844)
    J,cut,target,witness=peak;K=old['peaks'][2][0]
    need(J==66657328 and (cut,target)==(33373,93),'new all-cut peak')
    inrow,rev=reverse(program,cut,target,844)
    need(rev==witness,'independent peak covector')
    need(sum(abs(q)*a[j] for j,q in rev.items())==J,'independent weighted peak')
    signs={j:(1 if q>0 else -1)*a[j] for j,q in rev.items()}
    need(inject(program,cut,target,signs,844)==J,'independent weighted-defect attainment')
    reverse_rows=[]
    for r in (0,93,112,205,704,843):
        ir,er=reverse(program,len(program)-1,r,844)
        need(ir==ideal[r] and er==errors[r].coefficients(),'independent endpoint covector')
        reverse_rows.append({'role':r,'input_coefficients':len(ir),'defect_coefficients':len(er),
                             'weighted_sum':str(sum(abs(q)*a[j] for j,q in er.items()))})
    need(guard(J,K,0)==27 and guard(J,K,2)==27 and guard(J,K,3)==26,'exact guard thresholds')
    need(J+K/Q(4)>2**26 and J+K/Q(8)<=2**26 and J>2**25,'all-b piecewise proof inequalities')
    return {'status':'PASS_P104_OPERAND_WEIGHTED_FEEDBACK','events':len(program),'roles':844,
            'defect_sites':sites,'zero_ideal_weight_sites':zero,'P':str(P),'K':str(K),'J':str(J),
            'uniform_guard_bits':27,'guard_b0_to_b2':27,'guard_b_at_least3':26,
            'old_uniform_guard_bits':39,'uniform_threshold':str(J+K),
            'peak':{'event':cut,'role':target,'input_row':encode(inrow),
                    'defect_row':encode(rev),'site_weights':[[j,str(a[j])] for j in sorted(rev)]},
            'all_cut_new_norms_sha256':digest,
            'ideal_operand_weights_sha256':hashlib.sha256(canonical(list(map(str,a))).encode()).hexdigest(),
            'reverse_endpoints':reverse_rows,'controls':controls(m),
            'original_receipt_reproduced':True,'native_rank_mass':retained['paid_mass'],
            'scope':'conditional completed-output feedback upper bound; no minimal physical precision, rounded child, changed invoice, supplier or kappa'}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',type=Path);args=ap.parse_args()
    result=run()
    if args.write:
        with args.write.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    else:need(canonical(result)==canonical(json.loads((HERE/'RESULT.json').read_bytes())),'typed complete receipt differs')
    print(result['status'])
