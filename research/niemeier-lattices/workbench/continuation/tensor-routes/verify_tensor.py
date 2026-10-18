"""Exact embedding checks for punctured E8 native-word tensor controls.

The inherited native word itself is an input interface, not replayed here.
This verifies its field-independent common-frame lift and all scalar kernels.
"""
from pathlib import Path
import json,sys,hashlib
import numpy as np
PACKAGE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PACKAGE / 'code'))
import e8_cubed as e
HERE=Path(__file__).resolve().parent

def binary_basis(rows):
    basis={}
    for row in rows:e.insert_binary(basis,int(row))
    return tuple(basis[p]for p in sorted(basis))

def pack(rows):
    return rows.astype(np.uint32)@(1<<np.arange(rows.shape[1],dtype=np.uint32))

def bits(rows,n):
    return np.array([[(int(row)>>j)&1 for j in range(n)]for row in rows],dtype=np.uint8)

roots,fourth=e.e8_shells()
G=(roots@roots.T)//4
cover=json.loads((HERE/'ORTHOGONAL-CLIQUE-COVER.json').read_text())
cliques=json.loads((HERE/'orthogonal-cliques.json').read_text())
selected=[cliques[i]for i in cover['selected_indices']]
inc=np.zeros((120,120),dtype=np.int16)
for c in selected:
    e.require(len(c)==8 and len(set(c))==8,'Eight distinct roots per selected frame')
    e.require(np.array_equal(G[np.ix_(c,c)],2*np.eye(8,dtype=np.int16)),'Real orthogonal root frame')
    inc[np.ix_(c,c)]+=1
expected=(G==0).astype(np.int16)+9*np.eye(120,dtype=np.int16)
e.require(np.array_equal(inc,expected),'Exact edge partition by135 cliques')
e.require(np.array_equal(G*G-1,12*np.eye(120,dtype=np.int16)-inc),'Dyadic H decomposition')
# Puncture one root frame. Each surviving root is odd-adjacent to exactly4 frame roots.
omitted=selected[0]
keep=[i for i in range(120)if i not in omitted]
r=roots[keep]
native_labels,native_packed,_=e.binary_labels(roots,r)
native_centers=(r@roots[omitted].T)//4
center_spans=[]
for j in range(8):
    support=native_packed[native_centers[:,j]!=0]
    span=binary_basis(support)
    e.require(len(span)==8 and len(support)==56,'Punctured E8 center rank8')
    center_spans.append(list(span))
e.require(np.array_equal(2*(r@r.T)//4,native_centers@native_centers.T),'E8 eight-center scalar factor')
e.require(np.all((native_centers!=0).sum(axis=1)==4),'Four nonzero coordinates per punctured root')
# Match the inherited Hamming-coordinate prototype, including signed line orientation.
prototype_relative=Path('research/frame-sa504/inputs/hamming/PROTOTYPE.json')
prototype_path=PACKAGE.parents[1]/prototype_relative
prototype=json.loads(prototype_path.read_text())
prototype_rows=[tuple(row)for row in prototype['root_lines'][8:]]
port_map=[];port_sign=[]
for row in native_centers:
    sign=1 if next(int(x)for x in row if x)>0 else -1
    port_map.append(prototype_rows.index(tuple(map(int,sign*row))))
    port_sign.append(sign)
e.require(len(set(port_map))==112,'Signed bijection to inherited Hamming root lines')
prototype_packed=[prototype['binary_ports'][8+i]for i in port_map]
prototype_bits=bits(prototype_packed,9)
proto_chosen=[];proto_basis={}
for i,p in enumerate(prototype_packed):
    if e.insert_binary(proto_basis,p):proto_chosen.append(i)
prototype_isometry=(e.inverse_binary(prototype_bits[proto_chosen])@native_labels[proto_chosen])&1
e.require(np.array_equal((prototype_isometry@prototype_isometry.T)&1,np.eye(9,dtype=np.uint8)),'Inherited prototype label isometry')
e.require(np.array_equal((prototype_bits@prototype_isometry)&1,native_labels),'All inherited prototype port labels transported')
# Same-label +/- pairs, represented explicitly in canonical root ordering.
ports=[]
for a in r:
    for b in r:
        ports.extend([np.concatenate((a,b)),np.concatenate((a,-b))])
ports=np.array(ports,dtype=np.int16)
labels,packed,_=e.binary_labels(roots,ports)
e.require(np.array_equal(labels[::2],labels[1::2]),'Free relative-sign Walsh pairs have identical labels')
# Choose nine independent native labels once. Every fixed-root group is their isometric image.
chosen=[];b={}
for i,p in enumerate(native_packed):
    if e.insert_binary(b,p):chosen.append(i)
e.require(len(chosen)==9,'Native labels span9')
inv=e.inverse_binary(native_labels[chosen])
embeddings=[]
for orientation in range(2):
    for fixed in range(112):
        ids=np.array([2*(varying*112+fixed)+orientation if orientation==0 else 2*(fixed*112+varying)+orientation for varying in range(112)])
        image=(inv@labels[ids[chosen]])&1
        e.require(np.array_equal((image@image.T)&1,np.eye(9,dtype=np.uint8)),'Fixed-root embedding is an isometry')
        e.require(np.array_equal((native_labels@image)&1,labels[ids]),'Every fixed-root port is embedded correctly')
        complement=(np.eye(17,dtype=np.uint8)^(image.T@image&1))
        epacked=binary_basis(pack(complement))
        E=bits(epacked,17)
        e.require(len(epacked)==8 and not((E@image.T)&1).any(),'Eight-dimensional spectator complement')
        e.require(len(binary_basis(list(pack(image))+list(epacked)))==17,'Native full plus spectator equalsFULL17')
        e.require(not((labels[ids]@E.T)&1).any(),'Spectator lies in every target cap in its fixed-root block')
        for center_span in center_spans:
            lifted=(bits(center_span,9)@image)&1
            e.require(len(binary_basis(list(pack(lifted))+list(epacked)))==16,'Native center lift dimension16')
        embeddings.append(dict(orientation=orientation,fixed_root_index=keep[fixed],native_image=list(map(int,pack(image))),spectator=list(map(int,epacked))))
# The two Walsh sectors use different fixed-coordinate kernels. Neither requires cross-B regrouping.
e.require(len(embeddings)==224 and len(ports)==25088,'Symmetric punctured mixed-port counts')
receipt=dict(status='PASS_EXACT_NATIVE_TENSOR_LIFT_INTERFACE',
    scope='A complete common-frame lift of any inherited punctured E8 native scalar word, conditional on that word and its paid endpoint-normalization interface. This file does not replay the inherited native word or certify a moment gain.',
    omitted_root_indices=omitted,retained_root_indices=keep,
    inherited_prototype=dict(path=prototype_relative.as_posix(),sha256=hashlib.sha256(prototype_path.read_bytes()).hexdigest(),root_map=port_map,root_signs=port_sign,isometry_to_native=list(map(int,pack(prototype_isometry))),scope='The112 punctured roots are an exact signed reindexing of the inherited Hamming-coordinate prototype. Signed data conjugation transports its Gram factor and entire native scalar identity.'),
    native=dict(ports=112,dimension=9,real_centers=8,center_widths=[8]*8,center_bill=64,center_support_spans=center_spans),
    lifted=dict(ports=25088,dimension=17,native_blocks=224,center_copies={8:1792},center_bill=14336,extra_data_climbs={8:50176},native_histogram_multiplier=224,prefix_coalescence='Optional exact improvement: defer each extra8D data climb until its first scalar incidence, combining it with an immediately preceding native initial edge if there is one. This receipt conservatively keeps the8D climbs separate.'),
    scalar_kernel='After an invertible H2 relative-sign change on each pair of identical binary labels: E_A tensor I_B on the odd-A sector and I_A tensor E_B on the odd-B sector, where E=root_Gram/2.',
    data_chronology='Within each fixed-root block, grow source line p to E+<p> by rank8 and target0 to E by rank8. Run the inherited9D word using every frame U replaced by E+image(U). Finish atFULL17 for sources and p-perp for targets. Reverse the same-label Walsh change at the endpoints. Blocks are disjoint within each sector.',
    helper_chronology='Native helper entrance U and final V lift to E+image(U) and E+image(V); ranks both increase by8, so residual width dim(V)-dim(U) and every native edge rank are unchanged. A hyperplane-ended helper remains hyperplane-ended after lifting. Arbitrary dirt cancellation and cleanup follow from the identical scalar word and the isometric common-frame embedding; endpoint wrappers and spectator ownership must remain paid.',
    center_chronology='Each native rank8 center lives in a16D lifted frame E+image(U). Its private copy descends to E, costing8; targets have already grown to E. Different fixed-root blocks have different E, but never share data roles or require regrouping.',
    embeddings=embeddings,
    clique_cover=dict(selected=selected,number=135,root_multiplicity=9,orthogonal_edges=3780,identity='H=(G_entrywise_square-J)/4 =3I-(1/4)sum_C 1_C1_C^T',scope='Exact dyadic matrix decomposition only. Independent clique lifts need repeated source incidences and do not constitute a free common-frame circuit.'))
print(json.dumps(receipt,indent=2,sort_keys=True))
