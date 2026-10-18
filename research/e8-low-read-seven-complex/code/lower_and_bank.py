"""E8 specialization of source527/PR234 five-stage lowering and completed banks.

Henry Grant's PR234 layout and eumemic source527 lowering are the source of
the stage ordering, namespace, bridges, and terminal exchanges. E8 family:
Jacob Sussman; bit word: Dylan Crow with Anthropic Claude assistance.
This exact finite extension was prepared with OpenAI Codex assistance,
Apache-2.0. It does not certify the signed defining scalar decoder.
"""
import sys
if not __debug__: raise RuntimeError('Assertions must be enabled')
import hashlib, json, struct, argparse
from pathlib import Path
from collections import Counter
from fractions import Fraction

P = argparse.ArgumentParser()
P.add_argument('--records', type=Path, required=True)
P.add_argument('--charts', type=Path, required=True)
P.add_argument('--output', type=Path, required=True)
a = P.parse_args()
a.output.mkdir(exist_ok=True)
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
st=read(a.records/'249-states.json'); fs=read(a.records/'frames.json')['frames']
ev=list(struct.iter_unpack('<6i',(a.records/'249-records.bin').read_bytes()))
H,V,R=st['h'],st['v'],st['R']; M=5*H; LOCAL=2*V+R; LIVE=4*V+R; WORK=LIVE
assert (H,V,R)==(8,120,865) and LOCAL==st['n']
dim={int(k):f['dim'] for k,f in fs.items()}
ZERO=st['ZERO']; FULL=next(k for k,d in dim.items() if d==H)
assert all(st['initial'][str(r)]==ZERO and st['final'][str(r)]==FULL for r in range(2*V,LOCAL))
ACTIVE=((0,1),(1,0),(0,1),(3,2),(2,3))
MOVE,ADD,COPY,ERASE,IDLE,BRIDGE,COMPLETE,EXCHANGE=range(8)
PACK=struct.Struct('<8i')
def family(stage,local):
    assert 0<=local<=LOCAL and 0<=stage<5
    if local==LOCAL:return WORK
    if local<V:return ACTIVE[stage][0]*V+local
    if local<2*V:return ACTIVE[stage][1]*V+local-V
    return 4*V+local-2*V
for stage in range(5):
    images=[family(stage,r) for r in range(LOCAL+1)]
    assert len(set(images))==LOCAL+1 and images[-1]==WORK and WORK not in images[:-1]

def stage_rows(stage):
    reverse=stage in (1,3)
    for op,x,y,c,f,z in (reversed(ev) if reverse else ev):
        if op==MOVE:yield (MOVE,family(stage,x),c if reverse else y,y if reverse else c,f,0,stage,int(reverse))
        elif op==ADD:yield (ADD,family(stage,x),family(stage,y),-c if reverse else c,f,z,stage,int(reverse))
        elif op==(ERASE if reverse else COPY):
            yield (COPY,WORK,family(stage,x),0,c,0,stage,int(reverse))
            yield (MOVE,WORK,c,f,z if not reverse else dim[c],0,stage,int(reverse))
        else:
            assert op==(COPY if reverse else ERASE)
            yield (ERASE,WORK,-1,0,f,0,stage,int(reverse))

localH=Counter();copies=adds=0
required=set()
for op,x,y,c,f,z in ev:
    if op==MOVE and f:localH[f]+=1;required.add((y,c,f))
    elif op==ADD:adds+=1
    elif op==COPY:localH[z]+=1;copies+=1;required.add((ZERO,c,z))
charts=read(a.charts/'ALL-CHARTS.json')
assert {(c['before'],c['after'],c['rank']) for c in charts}==required
assert len(charts)==len(required)
chart_keys={(c['before'],c['after'],c['rank']) for c in charts}
chart_index={ (c['before'],c['after'],c['rank']):i for i,c in enumerate(charts) }
for c in charts:
    # Recheck the exact matrix witness consumed by the linker.  The
    # all-charts executable already proved these identities; repeating the
    # compact check here prevents a receipt-only chart substitution.
    C=[[Fraction(x) for x in r] for r in c['basis']]; I=[[Fraction(x) for x in r] for r in c['inverse']]; hmat=len(C)
    assert hmat==H and len(I)==H and all(len(r)==H for r in C+I)
    assert all(sum(C[i][k]*I[k][j] for k in range(H))==(1 if i==j else 0)
               for i in range(H) for j in range(H))
assert copies==9
idle={0:((2,2*H-2,0),(3,2*H-2,1)),1:((2,H-1,2),(3,H-1,3)),2:((0,2*H+2,4),(1,2*H+2,5),(2,4,6),(3,4,7))}
bridges={0:((0,2,1),(3,1,-1)),1:((3,1,1),(0,2,-1)),2:((1,3,-1),(2,0,1))}
counts=Counter();paid=Counter();stages=[]
program=a.output/'GLOBAL-PROGRAM.bin'
with program.open('wb') as out:
    def emit(row):
        out.write(PACK.pack(*row));counts[row[0]]+=1
    for stage in range(5):
        stageH=Counter();opened=False;cp=ad=er=0;source=None
        digest=hashlib.sha256()
        for row in stage_rows(stage):
            op,x,y,c,f,z,s,rev=row
            assert s==stage and rev==int(stage in (1,3))
            if op==MOVE:
                assert f>=0
                # Bind every emitted paid MOVE to the exact rational chart
                # admitted above. Reverse stages use the reflected pair.
                pair=(y,c,f) if not rev else (c,y,f)
                forward_pair=(y,c,f) if not rev else (c,y,f)
                if f:
                    # Reverse rows carry the reflected ledger orientation;
                    # both orientations bind to the same forward witness.
                    assert pair in chart_keys or (pair[1],pair[0],pair[2]) in chart_keys, ('unbound chart', pair)
                    idx=chart_index[forward_pair] if forward_pair in chart_index else chart_index[(pair[1],pair[0],pair[2])]
                    row=row[:5]+(idx,)+row[6:]
                if f:stageH[f]+=1
                if x==WORK:assert opened and c==ZERO and f==H
            elif op==ADD:
                assert x!=y and x!=WORK
                if y==WORK:assert opened and f==ZERO and z==3
                if opened:assert x!=source
                ad+=1
            elif op==COPY:
                assert not opened and x==WORK and y>=4*V and dim[f]==H
                opened=True;source=y;cp+=1
            else:
                assert op==ERASE and opened and x==WORK and f==ZERO
                opened=False;source=None;er+=1
            digest.update(PACK.pack(*row));emit(row)
        assert not opened and cp==er==copies and ad==adds and stageH==localH
        paid.update(stageH)
        stages.append(dict(stage=stage,complemented_reverse=stage in (1,3),sha256=digest.hexdigest(),copies=cp,erasures=er,adds=ad,paid=dict(stageH)))
        if stage in (1,2,4):
            which={1:0,2:1,4:2}[stage]
            for bank,rank,boundary in idle[which]:
                for t in range(V):emit((IDLE,bank*V+t,-1,0,rank,boundary,-1,0));paid[rank]+=1
            for dst,src,c in bridges[which]:
                for t in range(V):emit((BRIDGE,dst*V+t,src*V+t,c,0,which,-1,0))
    for x,y in ((0,1),(2,3)):
        for t in range(V):emit((EXCHANGE,x*V+t,y*V+t,-1,0,0,-1,0))
assert counts[COPY]==counts[ERASE]==5*copies and counts[BRIDGE]==6*V and counts[EXCHANGE]==2*V
assert counts[COMPLETE]==0
want=Counter({k:5*n for k,n in localH.items()})
want.update({k:2*V for k in (2*H-2,H-1,2*H+2,4)})
assert paid==want and M*LIVE-sum(k*n for k,n in paid.items())==4*V-5*copies*H==120

# Five disjoint residual windows, five width-h blocks per physical bank.
# The address route tau(stage) sends the helper's active h-window to its slot.
assert R%5==0
per_stage=R//5; banks=5*per_stage
slots=[];seen=set()
for stage in range(5):
    occupied=[set() for _ in range(per_stage)]
    for helper in range(R):
        bank=helper//5;offset=H*(helper%5)
        row=dict(stage=stage,virtual_family=4*V+helper,physical_bank=4*V+stage*per_stage+bank,offset=offset,width=H,route=['tau',stage],chart='identity')
        slots.append(row)
        for j in range(offset,offset+H):
            assert j not in occupied[bank];occupied[bank].add(j)
            key=(row['physical_bank'],j);assert key not in seen;seen.add(key)
    assert all(o==set(range(M)) for o in occupied)
assert len(seen)==banks*M==5*H*R and banks+4*V==LIVE

def bank_permutation(order):
    p=list(range(2*M))
    for block in order:
        for j in range(H*block,H*(block+1)):p[j],p[M+j]=p[M+j],p[j]
    return p
expected=[(j+M)%(2*M) for j in range(2*M)]
assert bank_permutation(range(5))==bank_permutation(reversed(range(5)))==expected
controls=[]
for block in range(5):
    for mode,seq in [('omit',[i for i in range(5) if i!=block]),('repeat',list(range(5))+[block])]:
        p=bank_permutation(seq);bad=sum(x!=y for x,y in zip(p,expected));assert bad==2*H
        controls.append(dict(mode=mode,block=block,differing_columns=bad))
slotpath=a.output/'BANK-SLOTS.json';slotpath.write_text(json.dumps(slots,separators=(',',':'))+'\n')
K=2*5*((LIVE-1)+R*M*((M-1)+M))
assert K==27347440
report=dict(status='PASS_SOURCE_BOUND_E8_FIVE_STAGE_LOWERING_AND_ACTUAL_BANK_ASSIGNMENT',
    source_hashes={n:sha(a.records/n) for n in ('249-records.bin','249-states.json','frames.json')},
    chart_hashes={n:sha(a.charts/n) for n in ('ALL-CHARTS.json','CHART-RECEIPT.json')},
    program_sha256=sha(program),stages=stages,opcode_counts=dict(counts),paid_histogram=dict(sorted(paid.items())),
    paid_calls=sum(paid.values()),rank_mass=sum(k*n for k,n in paid.items()),deficit=120,literal_stock=LIVE,
    copies_per_stage=copies,full_copy_erase_episodes=5*copies,role_stage_assignments=len(slots),bank_slots_sha256=sha(slotpath),
    banks_per_stage=per_stage,physical_banks=banks,bank_width=M,endpoint_columns_forward_and_reverse=4*M,
    bank_controls=controls,selector_charge=K,helper_chart='identity',helper_chart_factors=0,
    linked_move_charts=sum(1 for op,x,y,c,f,z in ev if op==0 and f),
    scope='Concrete renamed five-stage IR, fresh COPY lifetimes, both orientations, complete paid profile, all physical bank slots, and every paid MOVE linked to an admitted exact rational chart. Signed defining scalar decoder and all-size compiler are not established here.',
    provenance='Henry Grant PR234/source527 and completed-bank lineage; E8 family Jacob Sussman, bit word Dylan Crow with Anthropic Claude; finite extension OpenAI Codex assistance. Apache-2.0.')
(a.output/'LOWERING-BANKS.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(report['status'], 'records',sum(counts.values()),'banks',banks,'paid',sum(paid.values()),'mass',report['rank_mass'])
