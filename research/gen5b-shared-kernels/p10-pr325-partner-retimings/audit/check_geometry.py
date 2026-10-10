from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_source()
"""Independent exact retiming geometry for the newly pinned PR325 word.
No source programs or other verifiers are imported or executed.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from math import lcm
import gzip,hashlib,json
import numpy as np
if not __debug__:raise RuntimeError('Assertions must be enabled')
HERE=contract.AUDIT
SOURCE=contract.SOURCE
I=SOURCE/'inputs'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(name):
    p=I/name;b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
source=json.loads((SOURCE/'SOURCES.json').read_text())
assert source['head']=='0eca9340a3df6141b8e71a41638c3937b3522888'
for row in source['files']:
    raw=(I/row['local']).read_bytes()
    assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
    if row['path'].endswith('.py'):assert row['local'].endswith('.py.txt')
w=read('bitword__selected__bit__word_p10.json.gz')
g=read('bitword__selected__bit__graph_p10.json')
f=read('bitword__selected__bit__frames_p10.json.gz')['frames']
k=read('bitword__selected__bit__kchron_p10.json')['entries']
assert len(k)==480 and g['h']==20 and g['v']==960
Id=np.eye(20,dtype=object)
G=9*Id-np.ones((20,20),dtype=object)
Gi=np.asarray([[Q(int(i==j),9)-Q(1,99) for j in range(20)]for i in range(20)],dtype=object)
assert np.array_equal(G@Gi,Id)
def inverse2(a):
    if a.shape==(1,1):
        assert a[0,0]
        return np.asarray([[1/a[0,0]]],dtype=object)
    assert a.shape==(2,2)
    det=a[0,0]*a[1,1]-a[0,1]*a[1,0]
    assert det
    return np.asarray([[a[1,1]/det,-a[0,1]/det],[-a[1,0]/det,a[0,0]/det]],dtype=object)
cache={}
def proj(fid):
    if fid in cache:return cache[fid]
    z=f[str(fid)];rank=z['dim']
    if rank==20:p=np.asarray(Id,dtype=object)
    elif 'b' in z:
        B=np.asarray([[Q(x)for x in r]for r in z['b']],dtype=object)
        p=B.T@inverse2(B@G@B.T)@B@G
    else:
        A=np.asarray([[Q(x)for x in r]for r in z['a']],dtype=object)
        p=Id-Gi@A.T@inverse2(A@Gi@A.T)@A
    den=lcm(*(Q(x).denominator for x in p.flat))
    num=np.asarray([[int(Q(x)*den)for x in row]for row in p],dtype=object)
    assert np.array_equal(num@num,den*num)
    assert sum(num[i,i]for i in range(20))==rank*den
    cache[fid]=(num,den)
    return num,den
def sub(a,b):
    A,da=proj(a);B,db=proj(b)
    assert np.array_equal(A@B,db*A)and np.array_equal(B@A,db*A)
def difference(a,b):
    A,da=proj(a);B,db=proj(b);d=da*db;n=da*B-db*A
    assert np.array_equal(n@n,d*n)
    return n,d
def D(num,den):
    # Exact 40-column companion swap, scaled by den.
    C=Id[:,::-1]
    return np.block([[den*Id-num,num@C],[C@num,den*Id-C@num@C]])
receipts=[];hist_old=Counter();hist_new=Counter();members=Counter()
for pair,e in enumerate(k):
    a,b=e['carrier'],e['passive'];mix,cap=e['mix_frame'],e['deliver_frame']
    sa,sb=w['source_frame'][a],w['source_frame'][b];full=w['full_frame']
    assert e['carrier_chain']==[sa,mix,cap,full]and e['passive_chain']==[sb,mix,full]
    assert [f[str(x)]['dim']for x in [sa,sb,mix,cap,full]]==[1,1,2,18,20]
    root=g['roots'][e['deliver_after_root']]
    assert root['kind']=='side'and sorted(root['targets'])==sorted(e['receivers'])
    assert len(set(g['labels'][a])&set(g['labels'][b]))==1
    sub(sa,mix);sub(sb,mix);sub(mix,cap);sub(cap,full)
    extra,de=difference(mix,cap)
    assert sum(extra[j,j]for j in range(20))==16*de
    # Both actual integer source lines lie in the delivery cap. The moved
    # rank-16 component cannot act on either source contribution.
    for s in [a,b]:
        chi=np.asarray([int(j in g['labels'][s])for j in range(20)],dtype=object)
        assert all(x==0 for x in extra@chi)
        cp,dc=proj(cap);assert np.array_equal(cp@chi,dc*chi)
    # Actual target covectors annihilate this cap; no target frame grows.
    cp,dc=proj(cap)
    for t in e['receivers']:
        cov=np.asarray([3*int(j in g['labels'][t])-1 for j in range(20)],dtype=object)
        assert all(x==0 for x in cov@cp)
    endpoints=[]
    for s,old in [(a,e['carrier_chain']),(b,e['passive_chain'])]:
        new=[w['source_frame'][s],cap,full]
        products=[]
        for chain,H in [(old,hist_old),(new,hist_new)]:
            total=np.eye(40,dtype=object);scale=1
            for x,y in zip(chain,chain[1:]):
                sub(x,y);gap=f[str(y)]['dim']-f[str(x)]['dim']
                if gap:H[gap]+=1
                q,dq=difference(x,y);total=D(q,dq)@total;scale*=dq
            products.append((total,scale))
        assert np.array_equal(products[0][0]*products[1][1],products[1][0]*products[0][1])
        # Omitting the nonzero extra component fails on some dirty columns.
        dq=D(extra,de)
        assert not np.array_equal(dq,de*np.eye(40,dtype=object))
        endpoints.append({'source':s,'old_chain':old,'new_chain':new,'all40column_endpoint_equal':True})
        members[s]+=1
    receipts.append({'pair':pair,'carrier':a,'passive':b,'mix_frame':mix,'delivery_frame':cap,
                     'extra_rank':16,'extra_denominator':de,'source_lines_annihilated':True,
                     'target_cap_unchanged':True,'endpoints':endpoints})
assert members==Counter({s:1 for s in range(960)})
assert hist_old==Counter({1:960,2:480,16:480,18:480})
assert hist_new==Counter({2:960,17:960})
delta=Counter(hist_new);delta.subtract(hist_old)
assert {r:v for r,v in delta.items()if v}=={1:-960,2:480,16:-480,17:960,18:-480}
out={'status':'PASS_NEW_PR325_EXACT_480_RETIMING_GEOMETRY',
     'source_head':source['head'],'source_manifest_sha256':sha(SOURCE/'SOURCES.json'),
     'word_sha256':sha(I/'bitword__selected__bit__word_p10.json.gz'),
     'checker_sha256':sha(__file__),'pairs':480,'sources':960,'rational_projectors_checked':len(cache),
     'old_source_histogram':dict(sorted(hist_old.items())),'new_source_histogram':dict(sorted(hist_new.items())),
     'source_delta':{r:v for r,v in sorted(delta.items())if v},
     'all480_extra_rank16_projectors_idempotent':True,'all960_actual_source_lines_annihilated':True,
     'all960_exact40column_endpoint_chains_equal':True,'all960_omitted_extra_controls_rejected':True,
     'all_actual_receiver_caps_checked':True,
     'scope':'Exact local projector, source-line, target-cap and arbitrary-dirty endpoint chain identities. Full retimed frame admission additionally requires the actual event source-incidence invariant, scalar endpoint and COPY/chronology checks; this receipt alone does not establish equality of interleaved gate matrices or global lowering.',
     'receipts':receipts}
(HERE/'GEOMETRY-RESULT.json').write_text(json.dumps(contract.portable(out),indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k!='receipts'},indent=2))
