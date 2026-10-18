"""Independent semantic replay; uses only frozen geometry/address construction."""
import sys, json, hashlib, time
from pathlib import Path
from collections import Counter
from fractions import Fraction
import numpy as np
sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parents[2]
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT/'research/niemeier-lattices/code'))
import e8_cubed

def check(value, message):
    if not value: raise ValueError(message)

def rank(words):
    basis = {}
    for value in words:
        value = int(value)
        while value:
            pivot = value.bit_length()-1
            if pivot in basis: value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)

def determinant(rows):
    a = [[int(x) for x in row] for row in rows]
    previous, sign = 1, 1
    for k in range(len(a)-1):
        pivot = next(i for i in range(k,len(a)) if a[i][k])
        if pivot != k: a[k],a[pivot]=a[pivot],a[k]; sign *= -1
        for i in range(k+1,len(a)):
            for j in range(k+1,len(a)):
                numerator=a[i][j]*a[k][k]-a[i][k]*a[k][j]
                check(numerator % previous == 0,'Bareiss exact division')
                a[i][j]=numerator//previous
        previous=a[k][k]
        for i in range(k+1,len(a)): a[i][k]=0
    return sign*a[-1][-1]

start=time.monotonic()
result=json.loads((BASE/'walsh/results.json').read_text())
frames=json.loads((BASE/'helper/FRAME-SUPPORT.json').read_text())
roots,_,ports,profiles=e8_cubed.construct_shell()
P=ports[(profiles&4)==0,:16].astype(np.int64)
N=len(P)
check(N==30960 and len(set(map(tuple,P)))==N,'distinct 30960 ports')
check(np.all((P*P).sum(1)==16),'norm four')
check(np.all(P[np.arange(N),np.argmax(P!=0,axis=1)]>0),'canonical orientation')
Q=roots[result['root_basis_indices']].astype(np.int64)
G=Q@Q.T//4
check(determinant(G)==1,'independent determinant one')
check(Q.tolist()==result['root_basis_doubled_vectors'],'basis vectors')
Gi=np.array(result['root_gram_inverse'],dtype=np.int64)
check(np.array_equal(G@Gi,np.eye(8,dtype=np.int64)),'integer inverse')
M=np.zeros((16,16),dtype=np.int64)
M[:8,:8]=Gi&1; M[8:,8:]=Gi&1
weights=(1<<np.arange(16,dtype=np.uint32))
L=np.concatenate([(P[:,8*b:8*b+8]@Q.T//4)&1 for b in range(2)],axis=1)
packed=L.astype(np.uint32)@weights
twisted=((L@M)&1).astype(np.uint32)@weights
check(rank(packed)==16 and rank(M.astype(np.uint32)@weights)==16,'label and form rank16')
check(not np.diag(M).any() and np.array_equal(M,M.T),'alternating form')
addresses,address_packed,_=e8_cubed.binary_labels(roots,P)
check(np.all(addresses.sum(1)%2==1),'odd addresses')
label_to_address={}; address_to_label={}
for l,a in zip(packed.tolist(),address_packed.tolist()):
    check(l not in label_to_address or label_to_address[l]==a,'label fiber maps uniquely')
    check(a not in address_to_label or address_to_label[a]==l,'address fiber maps uniquely')
    label_to_address[l]=a; address_to_label[a]=l
check(Counter(Counter(packed.tolist()).values())==Counter({2:14400,8:270}),'multiplicities')
parity=np.array([i.bit_count()%2 for i in range(1<<17)],dtype=np.uint8)
hist=Counter(); degrees=[]; checked=0
for lo in range(0,N,173):
    hi=min(N,lo+173)
    raw=P[lo:hi]@P.T
    check(not (raw%4).any(),'integral pairings')
    t=raw//4
    check(t.min()>=-3 and t.max()<=4,'Cauchy range plus orientation')
    diagonal=np.zeros(t.shape,dtype=np.int64)
    diagonal[np.arange(hi-lo),np.arange(lo,hi)]=1
    check(np.array_equal(t==4,diagonal!=0),'diagonal equality only')
    odd=t%2
    check(np.array_equal(odd,parity[np.bitwise_and(twisted[lo:hi,None],packed[None,:])]),'rank16 parity all pairs')
    check(np.array_equal(1-odd,parity[np.bitwise_and(address_packed[lo:hi,None],address_packed[None,:])]),'17bit address relation all pairs')
    left=48*diagonal+4*t-t*t*t
    right=3*t*odd-24*np.sign(t)*(np.abs(t)==3)
    check(np.array_equal(left,right),'compensation all pairs int64')
    check(np.array_equal(left!=0,odd!=0),'support')
    values,counts=np.unique(t,return_counts=True)
    hist.update({int(v):int(c) for v,c in zip(values,counts)})
    degrees.extend(odd.sum(1).tolist());checked+=t.size
check(dict(hist)=={int(k):v for k,v in result['pairing_histogram'].items()},'receipt histogram')
exception=hist[-3]+hist[3];nnz=sum(v for k,v in hist.items() if k%2)
check(result['exceptional_abs_t_3_pairs']==exception==3363840,'semantic exceptional count')
check(result['compensation_nonzeros']==nnz==480337920,'semantic support count')
check(result['exceptional_share_of_nonzeros_exact']==str(Fraction(exception,nnz)),'exact semantic fraction')
check(abs(result['exceptional_share_of_nonzeros_percent']-100*exception/nnz)<1e-12,'semantic percent')
check([min(degrees),max(degrees)]==result['compensation_row_degree']==[15488,15872],'degree extrema')
for record in frames['coordinate_supports']:
    c=record['coordinate'];support=np.flatnonzero(P[:,c])
    witness=record['witness_ports']
    check(len(support)==record['support_count'],'support count')
    check(all(P[i,c]!=0 for i in witness),'witness support')
    check(address_packed[witness].tolist()==record['witness_packed_labels'],'witness bindings')
    check(rank(address_packed[support])==rank(address_packed[witness])==17,'support and witnesses span FULL')
    check(rank(address_packed[witness[:-1]+witness[:1]])==16,'repeated witness negative control')
control=frames['restricted_label_positive_control']
bucket=np.flatnonzero(address_packed==control['label'])
check(bucket.tolist()==control['target_ports'] and rank(address_packed[bucket])==1,'bucket positive control')
receipt={'status':'PASS_INDEPENDENT_SEMANTIC_WALSH_FRAME_REPLAY','ordered_pairs_checked':checked,'histogram':dict(sorted(hist.items())),
         'exceptional_abs_t_3_pairs':exception,'compensation_nonzeros':nnz,'exceptional_fraction':str(Fraction(exception,nnz)),
         'independent_root_gram_determinant':determinant(G),'parity_label_address_fibers_bijective':len(label_to_address),
         'address_pairing_relation_checked_on_all_pairs':'p_u dot p_v = 1 + B_uv modulo 2',
         'all_coordinate_support_spans':17,'bucket_span':1,'elapsed_seconds':time.monotonic()-start,
         'walsh_receipt_sha256':hashlib.sha256((BASE/'walsh/results.json').read_bytes()).hexdigest(),
         'frame_receipt_sha256':hashlib.sha256((BASE/'helper/FRAME-SUPPORT.json').read_bytes()).hexdigest()}
(Path(__file__).with_name('RESULT.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,sort_keys=True))
