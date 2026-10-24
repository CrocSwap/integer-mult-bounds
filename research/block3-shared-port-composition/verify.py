#!/usr/bin/env python3
"""Actual chronological shared-port words and raw inverse transpose. Apache-2.0."""
from fractions import Fraction as Q
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok: raise ValueError(msg)

for row in json.loads((ROOT/'ORIGINS.json').read_text()):
    need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source hash '+row['path'])
d={'__name__':'retained_source'}
exec(compile((ROOT/'inputs/pr4813-verify_schedule.py').read_bytes(),'retained_pr4813','exec'),d)
Z=d['ZERO'];O=d['ONE'];add=d['add'];mul=d['mul'];neg=lambda z:(-z[0],-z[1]);conj=lambda z:(z[0],-z[1])
ops=d['load_operators']();adj=d['adjoint'];word=d['word']
base={'A':ops['A'],'C2':ops['C2'],'W':ops['W'],'V':d['monomial']([0,2,1,3,4,6,5,7]),'Z1':d['pauli'](0,2)}
S=d['s_letter'](7);U=d['monomial']([0,5,2,7,4,1,6,3]);V=base['V']
base['P']=word(S,U,S);base['Q']=word(S,V,S)
for name in ['P','Q']:base[name+'inv']=adj(base[name])
base['X0']=d['pauli'](1,0)
base['X2']=d['pauli'](4,0)
base['K']=ops['K']
base['N']=word(ops['A'],ops['D'],adj(ops['K']))
for key,a in list(base.items()):base['bar_'+key]=tuple(tuple(conj(z)for z in row)for row in a)

def port(src,dst,three=True):
    w=[('paid',src,'A'),('mono',src,'P'),('add',dst,src,1),('mono',src,'Pinv'),('mono',src,'Q'),('add',dst,src,2),('mono',src,'Qinv'),('paid',dst,'A')]
    if three:w += [('mono',dst,'W'),('paid',dst,'C2'),('mono',dst,'V'),('mono',dst,'Z1')]
    return w

def fuse(w):
    out=[];i=0
    while i<len(w):
        k=w[i][1]
        pattern=[('paid',k,'A'),('mono',k,'W'),('paid',k,'C2'),('mono',k,'V'),('mono',k,'Z1'),('paid',k,'A')]
        if w[i:i+6]==pattern:out.extend([('paid',k,'K'),('mono',k,'N')]);i+=6
        else:out.append(w[i]);i+=1
    return out

def inverse_D(k):
    return [('mono',k,'Z1'),('mono',k,'V'),('paid',k,'C2'),('mono',k,'X2'),('mono',k,'W'),('paid',k,'A'),('mono',k,'X0')]

def subtract_L(src,dst):
    return [('mono',src,'P'),('add',dst,src,-1),('mono',src,'Pinv'),('mono',src,'Q'),('add',dst,src,-2),('mono',src,'Qinv')]

def snapshot_word():
    w=[]
    for k in range(4):
        w+=port(k,k+1)+[('add',5+k,k+1,1)]+inverse_D(k+1)+subtract_L(k,k+1)
    w += [('add',9,0,1),('paid',0,'A'),('mono',0,'X0')]+port(4,0,False)
    return w

def raw_dual_word(w):
    return [('add',g[2],g[1],-g[3])if g[0]=='add'else(g[0],g[1],'bar_'+g[2])for g in w]

def invoice(w):
    return {'paid_profile':{'1':sum(g[0]=='paid'and g[2]not in ['K','bar_K']for g in w),'3':sum(g[0]=='paid'and g[2]in ['K','bar_K']for g in w)},'paid_call_records':sum(g[0]=='paid'for g in w),'monomial_passes':sum(g[0]=='mono'for g in w),'scalar_ADD_passes':sum(g[0]=='add'for g in w),'coefficient_1_ADD_passes':sum(g[0]=='add'and abs(g[3])==1 for g in w),'coefficient_2_ADD_passes':sum(g[0]=='add'and abs(g[3])==2 for g in w)}

def lift(a,f):
    rows=[[(0,O)]]
    for unused in range(f):
        rows=[[(c*8+j,mul(z,b))for c,z in prior for j,b in enumerate(row)if b!=Z]for prior in rows for row in a]
    return rows

def act(rows,v):
    return [sumq([mul(z,v[c])for c,z in row])for row in rows]

def sumq(xs):
    result=Z
    for x in xs: result=add(result,x)
    return result

def transpose_rows(rows):
    out=[[]for unused in rows]
    for r,row in enumerate(rows):
        for c,z in row:out[c].append((r,z))
    return out

def execute(w,banks,letters,dual=False,inverse=False):
    v=[list(x)for x in banks]
    gates=reversed(w)if inverse else w
    for g in gates:
        if g[0]=='add':
            _,dst,src,c=g
            if dual:dst,src,c=src,dst,-c
            if inverse:c=-c
            v[dst]=[add(x,(c*y[0],c*y[1]))for x,y in zip(v[dst],v[src])]
        else:
            _,k,name=g;a=letters[name]
            if dual:a=[[(j,conj(z))for j,z in row]for row in a]
            if inverse:a=transpose_rows([[(j,conj(z))for j,z in row]for row in a])
            v[k]=act(a,v[k])
    return v

def expected(banks,f,two=False):
    A=lift(ops['A'],f);D=lift(ops['D'],f)
    # B_f must retain separate tensorized summands, never tensorize B_1's sum!
    MC=lift(word(ops['M'],ops['C2']),f);Ka=lift(word(ops['K'],d['pauli'](1,3)),f)
    def B(v):return [add(x,(2*y[0],2*y[1]))for x,y in zip(act(MC,v),act(Ka,v))]
    def plus(x,y):return [add(a,b)for a,b in zip(x,y)]
    x=banks
    u1=plus(act(D,x[1]),B(x[0]));u2=plus(act(D,x[2]),B(u1))
    if two:return [act(A,x[0]),act(A,u1),u2,x[3],x[4]]
    u3=plus(act(D,x[3]),B(u2));u4=plus(act(D,x[4]),B(u3))
    P=lift(base['P'],f);R=lift(base['Q'],f)
    t4=act(A,u4);L=[add(a,(2*b[0],2*b[1]))for a,b in zip(act(P,t4),act(R,t4))]
    return [plus(act(A,act(A,x[0])),act(A,L)),act(A,u1),act(A,u2),act(A,u3),t4]

def main():
    need(word(ops['D'],base['P'],ops['A'])==word(ops['M'],ops['C2']),'separate DPA=MC2 tensor word')
    need(word(ops['D'],base['Q'],ops['A'])==word(ops['K'],d['pauli'](1,3)),'separate DQA=Ka tensor word')
    pair=port(0,1)+port(1,2)
    full=sum([port(k,k+1)for k in range(4)],[])+port(4,0,False)
    need(invoice(pair)['paid_call_records']==6,'two-port paid bill')
    need(invoice(full)['paid_call_records']==14,'five-port paid bill')
    # Actual transformed diagonal has a useful changed-interface rank-three form.
    AD=word(ops['A'],ops['D']);normalizer=word(AD,adj(ops['K']))
    need(all(sum(z!=Z for z in row)==1 for row in normalizer),'AD K* monomial row')
    need(all(sum(row[c]!=Z for row in normalizer)==1 for c in range(8)),'AD K* monomial column')
    need(all(z==Z or z in [O,(Q(0),Q(1)),neg(O),(Q(0),Q(-1))] for row in normalizer for z in row),'AD K* phase')
    fused_pair=fuse(pair);fused_full=fuse(full);snapshot=snapshot_word()
    need(invoice(snapshot)['paid_profile']=={'1':23,'3':0},'snapshot emitted bill')
    need(invoice(fused_full)['paid_profile']=={'1':2,'3':4},'fused paid profile')
    receipts=[];columns=[];duals=[]
    for f in [1,2]:
        n=8**f;letters={key:lift(a,f)for key,a in base.items()}
        indices=range(5*n)if f==1 else [0,1,7,8,63,64,65,127,128,191,192,255,256,319]
        tests=[]
        for idx in indices:
            v=[[Z]*n for unused in range(5)];v[idx//n][idx%n]=O;tests.append(v)
        tests.append([[(Q(((k+1)*(j+2))%7-3),Q((j+3*k)%5-2))for j in range(n)]for k in range(5)])
        for i,v in enumerate(tests):
            got=execute(pair,v,letters);need(got==expected(v,f,True),'two-port full-input endpoint')
            out=execute(full,v,letters);need(out==expected(v,f),'five-port chronological endpoint')
            need(execute(fused_full,v,letters)==out,'fused five-port endpoint')
            need(execute(fused_pair,v,letters)==got,'fused two-port endpoint')
            saved=execute(snapshot,v+[[Z]*n for unused in range(5)],letters)
            AA=lift(ops['A'],f);DD=lift(ops['D'],f);MC=lift(word(ops['M'],ops['C2']),f);Ka=lift(word(ops['K'],d['pauli'](1,3)),f)
            def bv(z):return [add(a,(2*b[0],2*b[1]))for a,b in zip(act(MC,z),act(Ka,z))]
            targets=[act(AA,z)for z in v]
            needed_saved=[[add(a,b)for a,b in zip(act(DD,v[k+1]),bv(v[k]))]for k in range(4)]+[targets[0]]
            for k in range(1,5):need(saved[k]==targets[k],'snapshot retained original input')
            need(saved[5:]==needed_saved,'snapshot outputs or owner history')
            PP=lift(base['P'],f);QQ=lift(base['Q'],f);last=act(AA,[add(a,(2*b[0],2*b[1]))for a,b in zip(act(PP,targets[4]),act(QQ,targets[4]))])
            need(saved[0]==[add(a,b)for a,b in zip(targets[0],last)],'snapshot closing endpoint')
            need(execute(full,out,letters,inverse=True)==v,'literal reverse')
            dual=execute(full,v,letters,dual=True)
            need(execute(fused_full,v,letters,dual=True)==dual,'fused raw inverse transpose')
            need(execute(raw_dual_word(fused_full),v,letters)==dual,'serialized raw inverse transpose')
            need(execute(full,dual,letters,dual=True,inverse=True)==v,'literal raw-dual reverse')
            if f==1 and i<40:columns.append(sum(out,[]));duals.append(sum(dual,[]))
        receipts.append({'width':f,'all_basis_columns':f==1,'input_vectors':len(tests),'dimension':5*n})
    # Bilinear, not Hermitian: raw inverse transpose satisfies M^T N=I.
    for i in range(40):
        for j in range(40):need(sumq([mul(x,y)for x,y in zip(columns[i],duals[j])])==(O if i==j else Z),'raw inverse transpose pairing')
    # Reject fake independent original inputs and a forward word substituted as dual.
    n=8;v=[[Z]*n for unused in range(5)];v[0][0]=O
    actual=execute(pair,v,{key:lift(a,1)for key,a in base.items()})
    need(any(z!=Z for z in actual[1]),'naive original-x1 interpretation accidentally passes')
    need(any(sumq([mul(x,y)for x,y in zip(columns[i],columns[j])])!=(O if i==j else Z)for i in range(40)for j in range(40)),'forward-for-dual mutation passes')
    # Scoped single-bank monomial/Gaussian path bound used by snapshot reset policy.
    support_Dinv=sorted(set(sum(z!=Z for z in row)for row in adj(ops['D'])))
    support_Ainv=sorted(set(sum(z!=Z for z in row)for row in adj(ops['A'])))
    need(support_Dinv==[4]and support_Ainv==[2],'reset support floor')
    result={'status':'PASS_BLOCK3_SHARED_PORT_COMPOSITION','new_kappa':False,'pair':invoice(pair),'five_port':invoice(full),'fused_pair':invoice(fused_pair),'fused_five_port':invoice(fused_full),'fused_raw_inverse_transpose':invoice(raw_dual_word(fused_full)),'optimistic_five_target_moment':'3^(1-C)-2; any additional rank1 call makes it <=0 for 0<=C<1','direct_snapshot_reset_policy':{'emitted_invoice':invoice(snapshot),'paid_calls':23,'extra_paid_over_14':9,'saved_output_fields':5,'workspace_cleanup':'unpriced; additional obligation','domain':'single-bank monomial/Gaussian resets with additive contamination removed separately; excludes split-register decoder paths'},'AD_equals_monomial_K':True,'D_inverse_column_support':support_Dinv,'A_inverse_column_support':support_Ainv,'finite_replays':receipts,'raw_dual_bilinear_entries':1600,'controls':['fake independent original input rejected','forward word as raw dual rejected']}
    if '--write' in sys.argv:
        (ROOT/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');(ROOT/'WORD.json').write_text(json.dumps({'two_ports':pair,'five_ports':full,'fused_two_ports':fused_pair,'fused_five_ports':fused_full,'snapshot_restore':snapshot,'fused_five_raw_inverse_transpose':raw_dual_word(fused_full)},indent=2)+'\n')
    else:
        need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((ROOT/'RESULT.json').read_text()),sort_keys=True),'receipt mismatch')
        need(json.dumps(json.loads((ROOT/'WORD.json').read_text()),sort_keys=True)==json.dumps({'two_ports':[list(g)for g in pair],'five_ports':[list(g)for g in full],'fused_two_ports':[list(g)for g in fused_pair],'fused_five_ports':[list(g)for g in fused_full],'snapshot_restore':[list(g)for g in snapshot],'fused_five_raw_inverse_transpose':[list(g)for g in raw_dual_word(fused_full)]},sort_keys=True),'emitted word mismatch')
    print(result['status'])

if __name__=='__main__':main()
