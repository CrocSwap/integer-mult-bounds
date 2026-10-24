#!/usr/bin/env python3
"""Typed B extraction and all-p path obstruction. Apache-2.0, Codex assistance."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256,sha1
from pathlib import Path
import argparse,gzip,importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(v,s):
    if not v:raise ValueError(s)
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def span(b):
    s={0}
    for x in b:s|={y^x for y in list(s)}
    return s
def plus(a,b):
    c=Counter(a);c.update(b);return {k:v for k,v in c.items() if v}
def times(a,b):
    c=Counter()
    for (q,d),u in a.items():
        for (r,e),v in b.items():c[q+r,d+e]+=u*v
    return {k:v for k,v in c.items() if v}
def mm(a,b):return [[plus(times(a[i][0],b[0][j]),times(a[i][1],b[1][j])) for j in range(2)] for i in range(2)]
def mono(q=0,d=0,c=1):return {(q,d):c}
def matrices():
    z={};one=mono();minus=mono(c=-1);D=mono(d=1);QD=mono(1,1)
    forward=[[D,z],[D,QD]];left=[[one,z],[minus,one]];expected=[[D,z],[z,QD]]
    need(mm(left,forward)==expected,'Forward B output subtraction')
    backward=[[mono(d=-1),mono(-1,-1,-1)],[z,mono(-1,-1)]]
    right_orientation=[[one,one],[z,one]];dual=[[mono(d=-1),z],[z,mono(-1,-1)]]
    need(mm(right_orientation,backward)==dual,'Inverse transpose B output addition')
    need(mm([[one,z],[one,one]],forward)!=expected,'Wrong forward sign rejected')
    need(backward!=dual,'Omitted backward shear rejected')
    need(mono(-1,-1)!=mono(1,-1),'Q inverse is never identified with Q')
    return ['forward_subtraction','backward_addition','wrong_forward_sign','omitted_backward_shear','inverse_Q_not_Q']
def invoice(p,cut,mask,H,P0):
    n=mask.bit_count();T=Counter({r:n*v for r,v in H.items()});P=Counter({r:n*v for r,v in P0.items()})
    P[1]+=56*(2*p+1-n);T[1+7*n]+=112
    for length,rev in ((cut,False),(p-1-cut,True)):
        for j in range(1,length+1):
            pos=list(range(2*j+1))
            if rev:pos=[2*p-s for s in pos]
            k=sum(mask>>s&1 for s in pos);idle=sum(mask>>s&1 for s in pos[:-1]);T[1+7*k]+=112
            if idle:P[7*idle]+=112
    P[7]+=112*sum(mask>>(2*j)&1 for j in range(1,p));return +T,+P

def run():
    for row in read(HERE/'SOURCES.json')['files']:
        if row['usage']=='input':need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Source pin '+row['path'])
    for row in read(HERE/'inputs/ORIGINS.json'):
        b=(ROOT/row['path']).read_bytes();need(sha256(b).hexdigest()==row['sha256'] and sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'Exact original PR4654 Git blob')
    typed=read(HERE/'inputs/typed-interface.json');need(typed['port_types']=={'A':56,'B':56} and typed['D_rank']==7 and typed['Q_rank']==1,'Pinned typed interface')
    need(typed['forward_type_B']=='diag(D,QD) S_y(Q^-1)','Q is on physical Y')
    w=read(HERE/'inputs/native-word.json.gz');c=w['canonical'];H=Counter()
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r];need(span(c['frames'][a])<span(c['frames'][b]),'Strict original arbitrary helper')
        H[len(c['frames'][b])-len(c['frames'][a])]+=1
    need(H=={3:2,6:7,7:47,8:139,9:213},'Source helper census')
    H[7]+=56;H[8]+=56;paid={1:2177,2:424,3:389,4:147,5:50,8:8}
    for dr,events in w['programs'].items():
        P=Counter()
        for e in events:
            if e[0]=='climb':
                need(e[5]==len(c['frames'][e[4]])-len(c['frames'][e[3]]),'Actual paid climb rank');P[e[5]]+=1
            elif e[0]=='center':
                need(e[4]==abs(len(c['frames'][e[3]])-len(c['frames'][e[2]])),'Actual paid center rank');P[e[4]]+=1
        need(P==paid,'Both actual complete paid profiles')
    controls=matrices();need(sum(H.values())==520,'No lost or duplicated helper')
    massH=sum(r*v for r,v in H.items());massP=sum(r*v for r,v in paid.items())
    need((massH,massP,massP-massH-2*56*7)==(4246,5094,64),'Retained center excess')
    count=0
    for p in range(1,5):
        for cut in range(p):
            for mask in range(1<<(2*p+1)):
                T,P=invoice(p,cut,mask,H,paid);surplus=sum(r*v for r,v in T.items())-sum(r*v for r,v in P.items())
                need(surplus==-8*mask.bit_count()-56,'Every complete small rank invoice');count+=1
    path=ROOT/'research/higher-moment-strictification/verify.py';spec=importlib.util.spec_from_file_location('typed_log_bounds',path);E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
    l7,u7=E.log_bounds(7);l3,u3=E.log_bounds(3);l6,u6=E.log_bounds(6);l8,u8=E.log_bounds(8)
    need(l7>1 and u7-l3<2 and u7-l6<1 and u8-l7<1,'Elementary logarithm bounds')
    lower=Q(2177-56,7)*l7-2*(u7-l3)-7*(u7-l6)-Q(64,7)*(u8-l7)
    need(lower>Q(1980,7)>0,'All-t normalized derivative certificate')
    need(64-9<56 and 64-8==56,'Strict nine-unit threshold; equality does not suffice')
    return {'status':'PASS_TYPED_B_EXTRACTION_AND_ALL_P_PATH_OBSTRUCTION','source_PR4654_head':'dca175fed8ebde8980635fd3b4508b8cba89a1b0','active_A_pairs':56,'autonomous_helpers':dict(sorted(H.items())),'helper_fields':520,'paid':paid,'helper_rank_mass':massH,'paid_rank_mass':massP,'center_excess':64,'additional_complex_unit_ADDs_each_orientation':56,'rank_surplus_formula':'-8*n-56','uniform_all_C_upper':'-(8*n+56)*7^(-C)','quantifiers':'Every p>=1, every split, every native/thin subset; every 0<=C<1, in the unchanged minimal-cut A-path family.','strict_separator_derivative_lower':str(lower),'coarse_separator_lower':'1980/7','small_complete_invoices':count,'controls':controls,'native_admission':'Relies on the pinned typed supplier theorem; no full native/phase re-audit.','new_kappa':None}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r=run();f=HERE/'RESULT.json'
    if a.write:f.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    else:need(read(f)==json.loads(json.dumps(r)),'Stored exact receipt')
    print(json.dumps(r,indent=2,sort_keys=True))
