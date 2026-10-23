"""A structural prototype: mutable source bases and simultaneous signed packets.

Input geometry is the pinned PR370 Hamming E8 root table. The binary realization,
packet construction, two-shear synthesis and arbitrary-dirt replay below are new
local experiments. This does NOT produce a complete improved E8 supplier.
"""
import gzip
import hashlib
import itertools as it
import json
import random
from collections import Counter,defaultdict
from fractions import Fraction as Q
from pathlib import Path

OUT=Path('work/complex-network/hamming');OUT.mkdir(parents=True,exist_ok=True)
SRC=Path('work/pr370-source/research/e8-bit/data/bit/bitE8-r865.json.gz')
word=json.load(gzip.open(SRC));roots=word['lines'];v=len(roots)
G=[[sum(x*y for x,y in zip(a,b))//2 for b in roots] for a in roots]
C=[sum((1^(G[i][j]&1))<<j for j in range(v)) for i in range(v)]

def basis(vectors):
    b={}
    for x in vectors:
        for p in sorted(b,reverse=True):
            if x>>p&1:x^=b[p]
        if x:
            p=x.bit_length()-1
            for q in b:
                if b[q]>>p&1:b[q]^=x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))

def inside(a,b):return basis(a+b)==b

indices=[]
for i,row in enumerate(C):
    if len(basis([C[j] for j in indices]+[row]))>len(indices):indices.append(i)
assert len(indices)==9
gram=[sum(((C[i]>>j)&1)<<k for k,j in enumerate(indices)) for i in indices]
def ip(a,b):
    return sum(((a>>i)&1)*((gram[i]&b).bit_count()&1) for i in range(9))&1
orth=[]
for step in range(9):
    choices=[x for x in range(1,512) if ip(x,x) and all(not ip(x,y) for y in orth)]
    chosen=next(x for x in choices if step==8 or any(y!=x and not ip(x,y) for y in choices))
    orth.append(chosen)
assert all(ip(x,y)==int(i==j) for i,x in enumerate(orth) for j,y in enumerate(orth))
ports=[]
for i in range(v):
    row=sum(((C[i]>>j)&1)<<k for k,j in enumerate(indices))
    ports.append(sum(((row&e).bit_count()&1)<<k for k,e in enumerate(orth)))
assert len(set(ports))==v and all(p.bit_count()&1 for p in ports)
assert all(((ports[i]&ports[j]).bit_count()&1)==((C[i]>>j)&1) for i in range(v) for j in range(v))

blocks=defaultdict(list);frame_lines={}
for i,r in enumerate(roots):
    support=tuple(k for k,x in enumerate(r) if x)
    if len(support)==4:blocks[support].append(i)
    else:assert len(support)==1;frame_lines[support[0]]=i
assert len(blocks)==14 and all(len(xs)==8 for xs in blocks.values())

def sparse_add(rows,t,s,q):
    for j,x in list(rows[s].items()):
        z=rows[t].get(j,Q(0))+q*x
        if z:rows[t][j]=z
        else:rows[t].pop(j,None)

def simulate(n,events):
    rows=[{r:Q(1)} for r in range(n)]
    for t,s,q in events:sparse_add(rows,t,s,q)
    return rows

def serialize(events):return [[t,s,q.numerator,q.denominator] for t,s,q in events]

packet_table={};module_receipts=[];all_programs=[]
for block,ids in sorted(blocks.items()):
    ids=sorted(ids);pos={s:i for i,s in enumerate(ids)}
    tetrads=[sorted(s for s in ids if sum(roots[s][k]<0 for k in block)%2==p) for p in (0,1)]
    assert all(len(t)==4 for t in tetrads)
    faces=[]
    for i,j in it.combinations(block,2):
        for epsilon in (-1,1):
            support=[s for s in ids if roots[s][i]*roots[s][j]==epsilon]
            content={s:Q(roots[s][i]) for s in support}
            frame=basis([ports[s] for s in support]);assert len(frame)==3
            key=(block,(i,j),epsilon);packet_table[key]=(content,frame)
            faces.append((key,content,frame))
    pair_uses=defaultdict(list)
    for f,(_,content,frame) in enumerate(faces):
        for tet in tetrads:
            pair=tuple(s for s in tet if s in content)
            assert len(pair)==2
            pair_uses[pair].append(f)
    assert len(pair_uses)==12 and all(len(fs)==2 for fs in pair_uses.values())
    bysource=defaultdict(list)
    for pair in sorted(pair_uses):
        for s in pair:bysource[s].append(pair)
    # One of the three pair branches is carried by x itself, two by helpers.
    regs={};nextreg=8;events=[];event_frames=[];cur=[basis([ports[s]]) for s in ids]
    start=list(cur);dead=[]
    def add(t,s,q,F):
        assert t!=s and inside(cur[t],F) and inside(cur[s],F)
        cur[t]=cur[s]=F;events.append((t,s,Q(q)));event_frames.append(F)
    for s in ids:
        for j,pair in enumerate(sorted(bysource[s])):
            if j==0:reg=pos[s]
            else:
                reg=nextreg;nextreg+=1;cur.append(());start.append(())
                add(reg,pos[s],1,basis([ports[s]]))
            regs[pair,s]=reg
    assert nextreg==24
    partial={}
    for pair,fs in sorted(pair_uses.items()):
        s,t=pair;a,b=regs[pair,s],regs[pair,t];f,g=fs
        alpha,beta=faces[f][1][s],faces[f][1][t]
        gamma,delta=faces[g][1][s],faces[g][1][t]
        assert alpha*delta-beta*gamma in (-2,2)
        F=basis([ports[s],ports[t]]);assert len(F)==2
        add(a,b,beta/alpha,F)
        k=gamma/(delta-gamma*beta/alpha)
        add(b,a,k,F)
        partial[f,pair]=(a,alpha)
        partial[g,pair]=(b,delta-gamma*beta/alpha)
    pre_packets=simulate(24,events)
    def clean_rank(registers):
        piv={}
        for reg in registers:
            row=[pre_packets[reg].get(i,Q(0)) for i in range(8)]
            for j in sorted(piv):
                q=row[j]
                if q:row=[a-q*b for a,b in zip(row,piv[j])]
            j=next((i for i,q in enumerate(row) if q),None)
            if j is not None:
                q=row[j];piv[j]=[a/q for a in row]
        return len(piv)
    choices=[[value for (ff,pair),value in partial.items() if ff==f] for f in range(12)]
    rng=random.Random(38639);orientation=None
    for trial in range(4096):
        bits=rng.randrange(1<<12)
        if clean_rank([pieces[1-((bits>>f)&1)][0] for f,pieces in enumerate(choices)])==8:
            orientation=bits;break
    assert orientation is not None
    outputs=[]
    for f,(key,content,F) in enumerate(faces):
        pieces=[value for (ff,pair),value in partial.items() if ff==f]
        assert len(pieces)==2
        if orientation>>f&1:pieces.reverse()
        (a,alpha),(b,beta)=pieces
        add(a,b,beta/alpha,F)
        outputs.append((a,alpha));dead.append(b)
    assert len(set(r for r,a in outputs))==12 and len(set(dead))==12
    assert not set(dead)&{r for r,a in outputs}
    core=simulate(24,events)
    for f,(reg,scale) in enumerate(outputs):
        clean={ids[j]:scale*x for j,x in core[reg].items() if j<8 and x}
        assert clean==faces[f][1]

    # Probe complete borrowing: output each packet, cancel its old dirt at label
    # zero, then undo every source/helper operation at the full frame.
    # Actual supplier consumers and their remaining chronology are NOT inferred.
    n=36;main=events.copy();dirt=[];chosen_targets=[]
    for f,(reg,scale) in enumerate(outputs):
        main.append((24+f,reg,scale))
        for j,q in core[reg].items():
            if j>=8:dirt.append((24+f,j,-scale*q))
        valid=[t for t in range(v) if all((ports[t]&x).bit_count()%2==0 for x in faces[f][2])]
        assert valid;chosen_targets.append(valid[0])
    cleanup=[(t,s,-q) for t,s,q in reversed(events)]
    actual=simulate(n,dirt+main+cleanup)
    for r in range(24):assert actual[r]=={r:Q(1)}
    for f in range(12):
        expected={24+f:Q(1)}
        expected.update({pos[s]:q for s,q in faces[f][1].items()})
        assert actual[24+f]==expected
    # A mutation of the compensator must corrupt at least one arbitrary dirt column.
    wrong=simulate(n,main+cleanup)
    assert any(wrong[r]!=actual[r] for r in range(24,36))
    # Inverse-transpose: transpose and negate each elementary shear in the SAME
    # event order. Reversing as well would generally compute the wrong map.
    dual=simulate(n,[(s,t,-q) for t,s,q in dirt+main+cleanup])
    for r in range(n):
        expected={r:Q(1)}
        if r<8:
            expected.update({24+f:-content[ids[r]] for f,(_,content,F) in enumerate(faces) if ids[r] in content})
        assert dual[r]==expected
    receipt={'block':block,'source_lines':ids,'packets':12,'pair_butterflies':12,
             'packet_additions':len(events),'live_source_registers_borrowed':8,
             'helper_registers':16,'total_source_and_helper_registers':24,
             'retired_register_clean_rank':8,
             'independent_pair_branch_comparison_helpers':48,
             'comparison_scope':'48 is a specified independent two-input-form implementation, not the helper count of the current r783 supplier.',
             'frame_rank_counts':dict(Counter(map(len,event_frames))),
             'all_dirty_columns_forward_and_inverse_transpose':n,
             'compensator_omission_rejected':True,
             'scope':'A 12-output packet factory and probe sinks. Not a complete 120-port supplier or global frame schedule.'}
    module_receipts.append(receipt)
    all_programs.append({'receipt':receipt,'start_frames':start,'events':serialize(events),
                         'event_frames':event_frames,'outputs':[[r,str(q)] for r,q in outputs],
                         'dead_registers':dead,
                         'dirt':serialize(dirt),'cleanup':serialize(cleanup),
                         'probe_target_ports':[ports[t] for t in chosen_targets]})

# Reconstruct the entire signed E8 neighbour correction from the packet family.
# This proves all 120 rational source columns of the abstract decomposition.
decomposition=[]
for target,r in enumerate(roots):
    row=defaultdict(Q);terms=[];support=[i for i,x in enumerate(r) if x]
    if len(support)==4:
        c=tuple(support)
        for d in blocks:
            inter=tuple(sorted(set(c)&set(d)))
            if len(inter)!=2:continue
            i,j=inter;epsilon=r[i]*r[j];content,F=packet_table[d,inter,epsilon]
            coefficient=-Q(r[i],2)
            assert all((ports[target]&p).bit_count()%2==0 for p in F)
            for s,a in content.items():row[s]+=coefficient*a
            terms.append({'source_block':d,'pair':inter,'epsilon':epsilon,'coefficient':str(coefficient)})
        for s in blocks[c]+list(frame_lines.values()):
            if s!=target and G[target][s]:row[s]-=Q(G[target][s],2)
    else:
        i=support[0]
        for d in blocks:
            if i in d:
                for s in blocks[d]:row[s]-=Q(roots[s][i],2)
    expected={s:-Q(G[target][s],2) for s in range(v) if s!=target and G[target][s]}
    assert {s:a for s,a in row.items() if a}==expected
    # Eight coordinate centers recover the diagonal after side corrections.
    for s in range(v):
        center=sum(Q(r[i]*roots[s][i],4) for i in range(8))
        assert center+row.get(s,Q(0))==int(s==target)
    decomposition.append({'target':target,'cross_block_packets':terms,'side_support':len(expected)})

program_path=OUT/'PACKET-PROGRAMS.json.gz'
program_path.write_bytes(gzip.compress(json.dumps(all_programs,sort_keys=True,separators=(',',':')).encode(),mtime=0))
report={'status':'PASS_STRUCTURAL_PACKET_PROTOTYPE_NOT_A_NEW_SUPPLIER',
        'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
        'binary_address_dimension':9,'binary_gram_rank':len(indices),
        'binary_ports':ports,'root_lines':roots,
        'binary_gram_identity':'p_s dot p_t = 1 + (root_s dot root_t / 2) mod 2',
        'modules':module_receipts,'signed_packets':len(packet_table),
        'full_target_decomposition_columns':120,'full_target_decomposition_entries':120*120,
        'program_sha256':hashlib.sha256(program_path.read_bytes()).hexdigest(),
        'decomposition':decomposition,
        'remaining':['Joint scheduling and charging of all packet fan-outs and target accumulations',
                     'Forming all eight centers from the available mixed source basis without an uncharged restore',
                     'Full 120-port arbitrary-dirt forward/backward program and restored work stocks',
                     'Exact complex adapters and global phases; finite invoice; two independent prices and outer assembly'],
        'no_new_coarse_b_or_kappa_claim':True}
(OUT/'PROTOTYPE.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: 14 factories, 168 signed packets; each factory uses 8 source + 16 helper registers')
print('PASS: exact dirty forward and inverse-transpose columns, omission controls, all 14400 decoder entries')
print('NOT A SUPPLIER: global scheduling, mixed-basis centers, phase and full price remain open')
