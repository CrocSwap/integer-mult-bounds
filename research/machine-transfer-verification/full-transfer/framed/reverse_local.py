#!/usr/bin/env python3
"""Independent physical inverse+bank-renamed local invocation, without transposing gates."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path
import struct


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def audit(word_path, manifest_path, receipt_path, binary_path):
    raw = gzip.decompress(word_path.read_bytes())
    word, manifest, receipt = json.loads(raw), json.loads(manifest_path.read_text()), json.loads(receipt_path.read_text())
    h, v, R = word['h'], word['v'], word['R']
    require(sha256(raw).hexdigest() == manifest['words'][str(h)]['word_sha256'] == receipt['word_sha256'], 'Word hash')
    triples = list(combinations(range(h), 3))
    require(len(triples) == v, 'Dimension')
    frames = [tuple(x) for x in word['frames']]
    catalog = [(0,0,0),(0,0,h)] + [(c,u,1 if c==u else u.bit_count()-c.bit_count()) for c,u in frames]
    lookup = {pair:i+2 for i,pair in enumerate(frames)}
    line = [lookup[(mask,mask)] for t in triples for mask in [sum(1<<i for i in t)]]
    require(set(word['sources']) == {str(i) for i in range(v)}, 'Source keys')
    require(len(set(word['sources'].values())) == v, 'Source aliases')
    # A stored catalog ID f denotes the actual COMPLEMENT gauge D_(I-P_f).
    # Thus original-ID 1 represents D0; original-ID 0 represents D1.
    aux = [1]*R
    X, Y = [('line',i) for i in range(v)], [1]*v
    initial = [1<<i for i in range(2*v+R)]
    xv, yv, zv = initial[:v], initial[v:2*v], initial[2*v:]
    paid, phases = Counter(), {}
    phase = ''
    side_singletons = 0
    scalar_xors = 0
    trace_hash = sha256()
    event_count = 0

    def event(*args):
        nonlocal event_count
        trace_hash.update(json.dumps(args,separators=(',',':')).encode()+b'\n')
        event_count += 1

    def begin(name):
        nonlocal phase
        phase = name
        phases[name] = Counter()
        event('phase', name)

    def same(a,b,label):
        require(a==b, 'Unequal current gauges: '+phase+': '+label)

    def gate(a,b,frame):
        nonlocal scalar_xors
        require(0<=a<R and 0<=b<R and a!=b, 'Gate roles')
        same(aux[a], frame, 'destination'); same(aux[b], frame, 'source')
        zv[a] ^= zv[b]
        phases[phase]['literal_xors'] += 1
        scalar_xors += 1
        event('xor_aux',a,b,frame)

    def move(slot,new):
        require(0<=slot<R and 0<=new<len(catalog), 'Move domain')
        old=aux[slot]
        require(type(old) is int, 'Unfinished explicit side flag')
        if old==new: return
        require(old!=0 and catalog[old][2]>catalog[new][2], 'Reverse complement movement not increasing')
        if old!=1 and new!=0:
            c,u,_=catalog[new]; cc,uu,_=catalog[old]
            require(not cc&~c and not u&~uu, 'Reverse complement non-nested frame')
        paid[new,old]+=1
        aux[slot]=new
        phases[phase]['auxiliary_transports']+=1
        event('reframe_complement',slot,old,new)

    output_slots=set(); centers=[]; sides=[[] for _ in triples]; expected=[]
    for slot,f,common,triple in word['outputs']:
        require(0<=slot<R and slot not in output_slots, 'Terminal alias')
        output_slots.add(slot)
        if len(triple)==1:
            require(triple==[common], 'Center shape')
            centers.append((slot,f+2,common,triple))
            destinations=[i for i,t in enumerate(triples) if common in t]
        else:
            require(len(triple)==3 and triple==sorted(triple) and common in triple,'Side shape')
            destinations=[triples.index(tuple(triple))]
            sides[destinations[0]].append((slot,f+2,common,triple))
        expected.extend([v+i,2*v+slot] for i in destinations)
    require(expected==word['scatter'], 'Literal scatter binding')
    require(len(centers)==h and {r[2] for r in centers}==set(range(h)), 'Centers')
    require(all(len(s)==3 for s in sides),'Sides')
    # Reconstruct exact terminal state of the forward middle path independently.
    middle_end=[0]*R
    for i,slot in word['sources'].items(): middle_end[slot]=line[int(i)]
    for a,b,f in word['ops']: middle_end[a]=middle_end[b]=f+2
    for slot,f,_,_ in word['outputs']: middle_end[slot]=f+2
    require(all(f>=2 for f in middle_end),'Unused auxiliary in word')

    begin('1_initial_inverse_V_at_D0')
    for i,slot in word['sources'].items():
        i=int(i); same(aux[slot],Y[i],'initial source injection')
        zv[slot]^=yv[i]; scalar_xors+=1; phases[phase]['literal_xors']+=1
        event('xor_aux_from_Y',slot,i,1)
    begin('2_early_L_at_D0')
    for a,b,_ in word['ops']: gate(a,b,1)

    begin('3a_inverse_J_sides_before_centers')
    early_scatter=[]; flags=[]
    for i in reversed(range(v)):
        triple=triples[i]
        same(X[i],('line',i),'side data line')
        require({r[2] for r in sides[i]}==set(triple),'Side points')
        for slot,f,common,_ in reversed(sides[i]):
            a,b=[j for j in triple if j!=common]
            require(catalog[f]==(1<<common,((1<<h)-1)^(1<<a)^(1<<b),h-3),'Actual side envelope')
            same(aux[slot],1,'side start')
            # Complement/reverse of E < E+<ea-eb> < t^perp < F:
            # 0 < t < (E+<ea-eb>)^perp < E^perp.
            aux[slot]=('line',i); phases[phase]['side_rank_one_transports']+=1
            event('side_flag',slot,0,1,i,common,a,b)
            same(aux[slot],X[i],'side read')
            xv[i]^=zv[slot]; scalar_xors+=1; phases[phase]['literal_xors']+=1
            early_scatter.append((v+i,2*v+slot)); event('xor_X_from_aux',i,slot,('line',i))
            aux[slot]=('perp_E_plus_w',slot); phases[phase]['side_rank_one_transports']+=1
            event('side_flag',slot,1,2,i,common,a,b)
            aux[slot]=f; phases[phase]['side_rank_one_transports']+=1
            event('side_flag',slot,2,3,i,common,a,b)
            side_singletons+=3; flags.append([i,slot,common,a,b])
        X[i]=0; phases[phase]['data_transports']+=1
        event('reframe_X_line_to_full',i)

    begin('3b_inverse_J_centers_with_fresh_copies')
    for slot,f,common,_ in reversed(centers):
        require(catalog[f]==(1<<common,(1<<h)-1,h-1),'Actual center frame')
        move(slot,f)  # original 0 -> U^perp, rank one
        same(aux[slot],f,'clone source frame')
        copy=zv[slot]; temp_frame=f
        phases[phase]['fresh_blank_allocations']+=1; phases[phase]['complete_stream_copies']+=1
        event('fresh_clone',slot,f)
        temp_frame=0  # U^perp -> F, exact residual projector U
        paid[0,f]+=1; phases[phase]['paid_copy_transports']+=1
        event('reframe_copy_complement',slot,f,0)
        for i in reversed(range(v)):
            if common in triples[i]:
                same(temp_frame,X[i],'center copied read')
                xv[i]^=copy; scalar_xors+=1; phases[phase]['literal_xors']+=1
                early_scatter.append((v+i,2*v+slot)); event('xor_X_from_copy',i,slot,0)
        phases[phase]['fresh_stream_erasures']+=1; event('erase_fresh_copy',slot)
    require(Counter(early_scatter)==Counter(map(tuple,word['scatter'])),'Every early scatter incidence')

    begin('4a_reverse_of_remaining_cleanup')
    for slot in range(R): move(slot,middle_end[slot])
    begin('4b_middle_inverse_L_at_complement_frames')
    for a,b,f in reversed(word['ops']):
        move(a,f+2); move(b,f+2)
        gate(a,b,f+2)  # SAME target/source orientation: inverse, NOT transpose.

    begin('5_final_inverse_V_at_triple_perpendicular')
    for i,slot in word['sources'].items():
        i=int(i); move(slot,line[i]); Y[i]=line[i]
        phases[phase]['data_transports']+=1; event('reframe_Y_zero_to_perp',i)
        same(aux[slot],Y[i],'late source cancellation')
        zv[slot]^=yv[i]; scalar_xors+=1; phases[phase]['literal_xors']+=1
        event('xor_aux_from_Y',slot,i,line[i])
    begin('6a_auxiliary_cleanup_to_D1')
    for slot in range(R): move(slot,0)
    begin('6b_late_L_at_D1')
    for a,b,_ in word['ops']: gate(a,b,0)
    begin('7_late_J_at_D1')
    for t,s in reversed(word['scatter']):
        i,slot=t-v,s-2*v
        same(aux[slot],X[i],'late scatter'); same(X[i],0,'late data endpoint')
        xv[i]^=zv[slot]; scalar_xors+=1; phases[phase]['literal_xors']+=1
        event('xor_X_from_aux',i,slot,0)
    begin('8_late_inverse_L_at_D1')
    for a,b,_ in reversed(word['ops']): gate(a,b,0)
    require(aux==[0]*R and X==[0]*v and Y==line,'Reverse local endpoint gauges')
    require(xv==[initial[i]^initial[v+i] for i in range(v)] and yv==initial[v:2*v]
            and zv==initial[2*v:], 'Complete dirty-basis inverse-renamed action')
    require(scalar_xors==4*len(word['ops'])+2*len(word['scatter'])+2*v,'Scalar XOR count')
    mass=side_singletons+sum((catalog[b][2]-catalog[a][2])*n for (a,b),n in paid.items())
    require(mass==h*R+h*(h-1)==receipt['profile']['rank_sum'],'Auxiliary mass')
    encoded=bytearray(struct.pack('<6I2Q',h,v,R,len(catalog),len(paid),side_singletons,mass,h*(h-1)))
    for c,u,r in catalog: encoded.extend(struct.pack('<2QI',c,u,r))
    for (a,b),n in sorted(paid.items()): encoded.extend(struct.pack('<2Iq',a,b,n))
    require(bytes(encoded)==binary_path.read_bytes(),'Reverse complete charge input differs from forward CRT input')
    return dict(status='PASS',h=h,v=v,R=R,word_sha256=sha256(raw).hexdigest(),
        checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        binary_profiler_input_sha256=sha256(encoded).hexdigest(),
        scalar_word='reverse chronological original wrapper, then rename X and Y; individual XOR gates are NOT transposed',
        full_input_and_dirty_basis_directions=2*v+R,scalar_wrapper_xors=scalar_xors,
        clone_xor_equivalents=h,phases={k:dict(v) for k,v in phases.items()},
        transcript_event_count=event_count,transcript_sha256=trace_hash.hexdigest(),
        complete_reverse_auxiliary_charge_byte_equality=True,local_auxiliary_rank=mass,
        side_rank_one_transports=side_singletons,side_flags_sha256=sha256(json.dumps(sorted(flags),separators=(',',':')).encode()).hexdigest(),
        endpoints={'X':'full','Y':'triple_perpendicular','auxiliary':'full'},
        side_flag_basis_obligation='The exact same E,w,t Gram identities checked by forward_local.py; complementation reverses the flag and preserves its exact residual projectors.',
        scope='Concrete local inverse+bank-renamed schedule on every original dirty/input basis vector, fresh center copies and exact unchanged auxiliary CRT input. Ambient replication and endpoint correction are checked separately.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['word','manifest','receipt','binary','output']: p.add_argument('--'+k,required=True,type=Path)
    a=p.parse_args(); r=audit(a.word,a.manifest,a.receipt,a.binary)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2)+'\n')
    print('PASS reverse inverse+bank-renamed schedule, full basis, exact charges',r['h'],flush=True)

if __name__=='__main__': main()
