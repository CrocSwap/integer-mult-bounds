"""Exact E8 signed defining-source admission supplement, independent of PR370.

OpenAI Codex assistance; Apache-2.0. Original PR370 E8 word: Dylan Crow,
with Anthropic Claude assistance, Apache-2.0. Frozen inputs remain unchanged.
The signed source is a witness for the parity word, not its literal Z endpoint.
"""
import gzip, hashlib, json, struct, sys, time
from collections import Counter
from functools import lru_cache
from pathlib import Path
if not __debug__:
    raise SystemExit('Assertions required')
sys.dont_write_bytecode = True
P=Path(__file__).resolve().parent
S=Path('/private/tmp/pr370-low-read-certificate-v1')
R=P/'records'
WORD_PATH=S/'candidate-word.json.gz'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rd=lambda p:json.loads(p.read_text())
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
start=time.monotonic()
inputs={str(p):sha(p)for p in [WORD_PATH,R/'249-records.bin',R/'249-states.json',R/'frames.json']}
word=json.load(gzip.open(WORD_PATH,'rt'))
st=rd(R/'249-states.json');frames={int(k):v for k,v in rd(R/'frames.json')['frames'].items()}
raw=(R/'249-records.bin').read_bytes();ev=list(struct.iter_unpack('<6i',raw))
n,v,h=st['n'],st['v'],st['h'];N=n+1
assert (n,v,h,st['R'],len(word['ret']))==(1105,120,8,865,9)
assert not any(op==1 and v<=b<2*v for op,a,b,c,f,z in ev),'targets never feed the helper network'
assert all(op!=1 or a>=v for op,a,b,c,f,z in ev),'source rows are never written'

def add(dst,src,c):
    for k,x in src.items():
        z=dst.get(k,0)+c*x
        if z:dst[k]=z
        else:dst.pop(k,None)

# Independent certificate-network replay excludes the F2-only D/C fields.
def clean_network():
    rows=[{i:1} for i in range(n)]
    def gates(gs):
        for f,a,ss in gs:
            for b in ss:add(rows[a],rows[b],1)
    gates(word['A'])
    retained=[dict(rows[a])for a in word['ret']]
    for t,ks in enumerate(word['scatter']):
        for k in ks:add(rows[v+t],retained[k],1)
    gates(word['B'])
    return rows

rows=clean_network()
M=[];K=[]
for t in range(v):
    q=dict(rows[v+t]);assert q.pop(v+t)==1
    assert not any(v<=s<2*v for s in q)
    M.append({s:c for s,c in q.items()if s<v})
    K.append({s:c for s,c in q.items()if s>=2*v})
    assert {s for s,c in M[-1].items()if c&1}=={t}
    assert sorted(s for s,c in K[-1].items()if c&1)==next(ss for f,d,ss in word['D']if d==v+t)

# Independently derive every target's input coefficients by exact transposed
# propagation of its covector, to avoid certifying the source from itself.
network=[]
for f,a,ss in word['A']:
    network.extend((a,b,1)for b in ss)
for t,ks in enumerate(word['scatter']):
    network.extend((v+t,word['ret'][k],1)for k in ks)
for f,a,ss in word['B']:
    network.extend((a,b,1)for b in ss)
for t in range(v):
    cov={v+t:1}
    for a,b,c in reversed(network):
        z=cov.get(a,0)
        if z:cov[b]=cov.get(b,0)+c*z
    assert cov==rows[v+t],('adjoint mismatch',t)

# Initial compensation lives at D0. It can contain even coefficients: those
# gates reduce to the identity over F2 and are absent from the actual word.
D=[(1,v+t,s,-c,st['ZERO'],1)for t,row in enumerate(K)for s,c in sorted(row.items())]
assert not any(op==0 for op,a,b,c,f,z in ev[:len([e for e in ev if e[0]==1 and e[5]==1])])
signed=D+[(op,a,b,-c if op==1 and z==5 else c,f,z)for op,a,b,c,f,z in ev if not(op==1 and z==1)]
parity=[(op,a,b,c%2 if op==1 else c,f,z)for op,a,b,c,f,z in signed if op!=1 or c%2]
assert parity==ev,'literal parity-filtered signed source must be exactly the exported word'
signed_bytes=b''.join(struct.pack('<6i',*e)for e in signed)
(P/'signed-records.bin').write_bytes(signed_bytes)
(P/'decoder-and-dirt.json').write_bytes(canon(dict(M=M,K=K))+b'\n')

def endpoint(direction=1):
    out=[{r:1}for r in range(n)]+[{}]
    for t,row in enumerate(M):add(out[v+t],row,direction)
    return out

def replay(records,reverse=False,negative_decoder=False,initial=None):
    val=[{i:1}for i in range(n)]+[{}]if initial is None else [dict(x)for x in initial]
    top=1;norm=[1]*n+[0];copies=0;borrowed=None
    for op,a,b,c,f,z in reversed(records)if reverse else records:
        if op==1:
            coef=-c if reverse else c
            if negative_decoder and v<=a<2*v:coef=-coef
            add(val[a],val[b],coef)
            norm[a]+=abs(coef)*norm[b];top=max(top,norm[a])
        elif op==(3 if reverse else 2):
            assert borrowed is None and b==n
            borrowed=a;val[n]=dict(val[a]);norm[n]=norm[a]
        elif op==(2 if reverse else 3):
            assert borrowed==a and val[n]==val[a]
            borrowed=None;val[n]={};norm[n]=0;copies+=1
    assert borrowed is None and copies==9 and not val[n]
    return val,dict(copies=copies,max_prefix_row_l1=top,final_max_row_l1=max(norm),formal_columns=n)

forward,forward_stats=replay(signed);assert forward==endpoint(1)
inverse,inverse_stats=replay(signed,reverse=True);assert inverse==endpoint(-1)
negative,negative_stats=replay(signed,negative_decoder=True);assert negative==endpoint(-1)
back,_=replay(signed,reverse=True,initial=forward);assert back==[{i:1}for i in range(n)]+[{}]

@lru_cache(None)
def contained(a,b,rev):
    x,y=frames[a],frames[b]
    assert (h-x['dim']if rev else x['dim']) <= (h-y['dim']if rev else y['dim'])
    assert all(sum(i*j for i,j in zip(u,w))==0 for u in (x['A']if rev else x['B'])for w in(y['B']if rev else y['A']))
    return True

def ledger(records,rev=False):
    state={int(k):x for k,x in st['final'if rev else'initial'].items()}
    target={int(k):x for k,x in st['initial'if rev else'final'].items()}
    borrowed=None;H=Counter()
    for op,a,b,c,f,z in reversed(records)if rev else records:
        if op==0:
            old,new=(c,b)if rev else(b,c)
            assert state[a]==old and contained(old,new,rev)
            assert f==(frames[old]['dim']-frames[new]['dim']if rev else frames[new]['dim']-frames[old]['dim'])>=0
            if f:H[f]+=1
            state[a]=new
        elif op==1:
            assert a!=b and a!=n and state[a]==state[b]==f
            assert b!=n or borrowed is not None
            assert a!=borrowed
        elif op==(3 if rev else 2):
            assert borrowed is None and b==n and n not in state and state[a]==c
            assert z==(0 if rev else frames[c]['dim'])
            assert f==st['ZERO']and frames[c]['dim']==h
            borrowed=a;state[n]=f;H[h]+=1
        else:
            assert op==(2 if rev else 3)and borrowed==a and b==n and state[a]==c and state[n]==f
            assert z==(frames[c]['dim']if rev else 0)
            borrowed=None;del state[n]
    assert state==target and borrowed is None
    return dict(histogram=dict(sorted(H.items())),paid_calls=sum(H.values()),rank_mass=sum(r*c for r,c in H.items()))

ledgers=[ledger(signed,rev)for rev in(False,True)]
assert ledgers[0]==ledgers[1]==ledger(ev)

def must_reject(name,bad,mode='Z'):
    value,_=replay(bad)
    if mode=='F2':
        odd=lambda row:{k for k,x in row.items()if x&1}
        assert any(odd(a)!=odd(b)for a,b in zip(value,endpoint(1)))
    else:assert value!=endpoint(1)
    return dict(name=name,mode=mode,rejected=True)

controls=[]
odd_d=next(i for i,e in enumerate(signed)if e[0]==1 and e[5]==1 and e[3]&1)
cleanup=next(i for i,e in enumerate(signed)if e[0]==1 and e[5]==5)
scatter=next(i for i,e in enumerate(signed)if e[0]==1 and e[5]==3)
for name,i,mode in [('omit_odd_dirt_compensation',odd_d,'F2'),('omit_cleanup_add',cleanup,'Z'),('omit_retained_scatter',scatter,'F2')]:
    controls.append(must_reject(name,signed[:i]+signed[i+1:],mode))
for name,i in [('flip_dirt_compensation_sign',odd_d),('flip_cleanup_sign',cleanup)]:
    bad=list(signed);op,a,b,c,f,z=bad[i];bad[i]=(op,a,b,-c,f,z)
    controls.append(must_reject(name,bad))
bad=list(signed);op,a,b,c,f,z=bad[odd_d];bad[odd_d]=(op,a,b,c-2,f,z)
controls.append(must_reject('same_parity_wrong_integer_compensation',bad))

# A forward scalar coordinate valuation cannot certify reflected rational
# charts; those are separate obligations. Check every original source-support
# operand against its actual common rational frame, excluding the copied
# complete-stream extraction whose frame change is separately paid.
source=[{i:1}for i in range(v)]+[{}for _ in range(N-v)]
checks=0
for op,a,b,c,f,z in signed:
    if op==1:
        for r in(a,b):
            if r==n or v<=r<2*v:continue
            for s in source[r]:
                assert all(sum(x*y for x,y in zip(word['lines'][s],ann))==0 for ann in frames[f]['A'])
                checks+=1
        add(source[a],source[b],c)
    elif op==2:source[n]=dict(source[a])
    elif op==3:assert source[n]==source[a];source[n]={}
assert source[:v]==[{i:1}for i in range(v)]and all(not r for r in source[2*v:])

result=dict(
    status='PASS_EXACT_SIGNED_DEFINING_DECODER_AND_LITERAL_PARITY_PROJECTION',
    source_pr320_lowread_candidate_sha256=sha(WORD_PATH),input_sha256=inputs,
    signed_record_sha256=hashlib.sha256(signed_bytes).hexdigest(),signed_records=len(signed),
    exported_F2_record_sha256=hashlib.sha256(raw).hexdigest(),literal_parity_record_equality=True,
    decoder_sha256=sha(P/'decoder-and-dirt.json'),target_decoder_exact_integer=True,
    target_decoder_mod2_identity=True,independent_adjoint_all_target_rows=True,
    arbitrary_helper_dirt_restored_exactly=True,source_rows_unchanged_exactly=True,
    forward=forward_stats,literal_signed_inverse=inverse_stats,direction_minus_source=negative_stats,
    forward_then_signed_inverse_identity=True,forward_and_reflected_ledgers=ledgers,
    compensation=dict(weighted_additions=len(D),odd_additions=sum(c&1 for row in K for c in row.values()),even_additions=sum(not(c&1)for row in K for c in row.values()),unit_additions=sum(sum(row.values())for row in K),maximum_coefficient=max(c for row in K for c in row.values())),
    decoder=dict(nonzero_coefficients=sum(len(row)for row in M),maximum_coefficient=max(c for row in M for c in row.values()),diagonal_coefficients=sorted(set(M[t][t]for t in range(v)))),
    signed_source_support_checks=checks,controls=controls,
    signed_source_majorant_is_not_emitted_word_payload_bound=True,
    scope='Exact all-column signed defining-source supplement. The actual paid bit word is its byte-identical parity reduction and keeps its own forward/inverse majorant and paid profile. The defining Z target is the explicit clean E8 network decoder, not the identity; its mod2 is identity. This is not a source527 replay or a general all-size compiler proof. E8 rational charts, global five-stage emitted addresses, selectors, finite invoice and assembly are separate obligations.',
    attribution='Original E8 construction: Dylan Crow with Anthropic Claude assistance; this independent audit and signed defining-source repair: OpenAI Codex assistance. Apache-2.0.',seconds=time.monotonic()-start)
assert inputs=={p:sha(Path(p))for p in inputs}
(P/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps(result,sort_keys=True,indent=2),flush=True)
