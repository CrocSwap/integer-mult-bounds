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
S=P
R=P/'records'
WORD_PATH=S/'word.json.gz'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rd=lambda p:json.loads(p.read_text())
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
start=time.monotonic()
inputs={str(p):sha(p)for p in [WORD_PATH,R/'249-records.bin',R/'249-states.json',R/'frames.json']}
word=json.load(gzip.open(WORD_PATH,'rt'))
st=rd(R/'249-states.json');frames={int(k):v for k,v in rd(R/'frames.json')['frames'].items()}
raw=(R/'249-records.bin').read_bytes();ev=list(struct.iter_unpack('<6i',raw))
n,v,h=st['n'],st['v'],st['h'];N=n+1
assert (n,v,h,st['R'],len(word['ret']))==(980,120,8,740,9)
assert not any(op==1 and v<=b<2*v for op,a,b,c,f,z in ev),'targets never feed the helper network'
assert all(op!=1 or a>=v for op,a,b,c,f,z in ev),'source rows are never written'
# Exact native F2 reconstruction plus separately bound signed entrance witness.
from collections import defaultdict
import copy
selection=rd(P/'SELECTION.json');baseline_raw=(P/'baseline.json').read_bytes()
assert hashlib.sha256(baseline_raw).hexdigest()==selection['source_sha256']
assert hashlib.sha256(gzip.decompress(WORD_PATH.read_bytes())).hexdigest()==selection['output_sha256']
baseline=json.loads(baseline_raw);reconstructed=copy.deepcopy(baseline);by=defaultdict(list);entrance_coefficients={};positive_pivots=set();frame_ids={tuple(fr):i for i,fr in enumerate(word['frames'])}
for item in selection['entries']:
    p=item['pivot'];E=item['entrance'];fid=frame_ids[tuple(E)];assert fid!=st['ZERO'] and p not in positive_pivots
    positive_pivots.add(p);reconstructed['start'][p]=fid
    for donor,coefficient in item['donor_coefficients']:
        assert coefficient in (-1,1) and (donor,p) not in entrance_coefficients
        # This selection records K_p = sum(c_d K_d), so entrance adds -c_d.
        entrance_coefficients[donor,p]=-coefficient;by[donor,fid].append(p)
prelude=[[f,d,sorted(ps)]for(d,f),ps in sorted(by.items())]
postlude=[[baseline['final'][0],d,sorted(ps)]for(d,f),ps in sorted(by.items())]
reconstructed['A']=prelude+reconstructed['A'];reconstructed['C']+=postlude
reconstructed['D']=[[f,d,[x for x in ss if x not in positive_pivots]]for f,d,ss in reconstructed['D']]
assert reconstructed==word and len(positive_pivots)==selection['pivots']==75
assert {i for i in range(2*v,n)if st['initial'][str(i)]!=st['ZERO']}==positive_pivots
prelude_gates=len(prelude);base_cleanup_gates=len(baseline['C'])
def phase_coefficient(phase,index,d,s):
    if phase=='A' and index<prelude_gates:return entrance_coefficients[d,s]
    if phase=='C':return -entrance_coefficients[d,s]if index>=base_cleanup_gates else -1
    return 1
expected_coefficients={phase:[phase_coefficient(phase,i,d,s)for i,(f,d,ss)in enumerate(word[phase])for s in ss]for phase in('A','B','C')}


def add(dst,src,c):
    for k,x in src.items():
        z=dst.get(k,0)+c*x
        if z:dst[k]=z
        else:dst.pop(k,None)

# Independent certificate-network replay excludes the F2-only D/C fields.
def clean_network():
    rows=[{i:1} for i in range(n)]
    def gates(gs,phase):
        for index,(f,a,ss) in enumerate(gs):
            for b in ss:add(rows[a],rows[b],phase_coefficient(phase,index,a,b))
    gates(word['A'],'A')
    retained=[dict(rows[a])for a in word['ret']]
    for t,ks in enumerate(word['scatter']):
        for k in ks:add(rows[v+t],retained[k],1)
    gates(word['B'],'B')
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

assert all(not(row.keys() & positive_pivots)for row in K),'positive-entrance pivot requires exact integer cancellation, never D0 compensation'

# Independently derive every target's input coefficients by exact transposed
# propagation of its covector, to avoid certifying the source from itself.
network=[]
for index,(f,a,ss) in enumerate(word['A']):
    network.extend((a,b,phase_coefficient('A',index,a,b))for b in ss)
for t,ks in enumerate(word['scatter']):
    network.extend((v+t,word['ret'][k],1)for k in ks)
for index,(f,a,ss) in enumerate(word['B']):
    network.extend((a,b,phase_coefficient('B',index,a,b))for b in ss)
for t in range(v):
    cov={v+t:1}
    for a,b,c in reversed(network):
        z=cov.get(a,0)
        if z:cov[b]=cov.get(b,0)+c*z
    assert {k:x for k,x in cov.items()if x}==rows[v+t],('adjoint mismatch',t)

# Initial compensation lives at D0. It can contain even coefficients: those
# gates reduce to the identity over F2 and are absent from the actual word.
D=[(1,v+t,s,-c,st['ZERO'],1)for t,row in enumerate(K)for s,c in sorted(row.items())]
assert not any(op==0 for op,a,b,c,f,z in ev[:len([e for e in ev if e[0]==1 and e[5]==1])])
signed=list(D);phase_used={2:0,4:0,5:0};phase_names={2:'A',4:'B',5:'C'}
for op,a,b,c,f,z in ev:
    if op==1 and z==1:continue
    if op==1 and z in phase_names:
        i=phase_used[z];phase_used[z]+=1;c=expected_coefficients[phase_names[z]][i]
    signed.append((op,a,b,c,f,z))
assert all(phase_used[z]==len(expected_coefficients[phase])for z,phase in phase_names.items())
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
# Actual same-parity entrance/exit controls test the signed sidecar, not only F2.
first_signed_kernel=next(i for i,e in enumerate(signed)if e[0]==1 and e[5]==2 and (e[1],e[2])in entrance_coefficients)
bad=list(signed);op,a,b,c,f,z=bad[first_signed_kernel];bad[first_signed_kernel]=(op,a,b,-c,f,z)
controls.append(must_reject('flip_one_signed_entrance_coefficient_same_parity',bad,'Z'))
controls.append(must_reject('omit_actual_entrance_shear',signed[:first_signed_kernel]+signed[first_signed_kernel+1:],'Z'))
last_signed_kernel=max(i for i,e in enumerate(signed)if e[0]==1 and e[5]==5 and (e[1],e[2])in entrance_coefficients)
bad=list(signed);op,a,b,c,f,z=bad[last_signed_kernel];bad[last_signed_kernel]=(op,a,b,-c,f,z)
controls.append(must_reject('flip_one_signed_exit_coefficient_same_parity',bad,'Z'))
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
    source_R740_integer_kernel_candidate_sha256=sha(WORD_PATH),input_sha256=inputs,
    signed_record_sha256=hashlib.sha256(signed_bytes).hexdigest(),signed_records=len(signed),
    exported_F2_record_sha256=hashlib.sha256(raw).hexdigest(),literal_parity_record_equality=True,
    decoder_sha256=sha(P/'decoder-and-dirt.json'),target_decoder_exact_integer=True,
    target_decoder_mod2_identity=True,independent_adjoint_all_target_rows=True,
    arbitrary_helper_dirt_restored_exactly=True,source_rows_unchanged_exactly=True,
    integer_kernel=dict(sidecar_convention='K_p=sum(c_d K_d); entrance=-c_d, cleanup=+c_d',pivots=len(positive_pivots),donor_slots=selection['donor_count'],all_positive_start_responses_zero_over_Z=True,sidecar_sha256=sha(P/'SELECTION.json'),baseline_sha256=sha(P/'baseline.json'),coefficients={str(k):v for k,v in sorted(entrance_coefficients.items())}),
    forward=forward_stats,literal_signed_inverse=inverse_stats,direction_minus_source=negative_stats,
    forward_then_signed_inverse_identity=True,forward_and_reflected_ledgers=ledgers,
    compensation=dict(weighted_additions=len(D),odd_additions=sum(c&1 for row in K for c in row.values()),even_additions=sum(not(c&1)for row in K for c in row.values()),unit_additions=sum(sum(row.values())for row in K),maximum_coefficient=max(c for row in K for c in row.values())),
    decoder=dict(nonzero_coefficients=sum(len(row)for row in M),maximum_coefficient=max(c for row in M for c in row.values()),diagonal_coefficients=sorted(set(M[t][t]for t in range(v)))),
    signed_source_support_checks=checks,controls=controls,
    signed_source_majorant_is_not_emitted_word_payload_bound=True,
    scope='Exact all-column signed defining-source supplement. The actual paid bit word is its byte-identical parity reduction and keeps its own forward/inverse majorant and paid profile. The defining Z target is the explicit clean E8 network decoder, not the identity; its mod2 is identity. This is not a source527 replay or a general all-size compiler proof. E8 rational charts, compressed nine-stage emitted addresses, selectors, finite invoice and assembly are separate obligations.',
    attribution='Original E8 construction: Dylan Crow with Anthropic Claude assistance; PR436 producer/elimination reuse and independently rederived signed kernel; this independent signed defining-source repair: OpenAI Codex assistance. Apache-2.0.',seconds=time.monotonic()-start)
assert inputs=={p:sha(Path(p))for p in inputs}
(P/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps(result,sort_keys=True,indent=2),flush=True)
