"""Independent source replay, all-column identities and contract mutations."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json

import algebra as a
import circuit
from source import PIVOTS, Q, add, helper_entries, need


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


def run(data):
    rows=[{i:F(1)} for i in range(704)]
    for gate in data["gates"]:
        at=gate[1][1]
        if gate[0]=="add":rows[at]=add(rows[at],rows[gate[2][1]],F(gate[3],gate[4]))
        else:rows[at]={j:v*F(gate[2],gate[3]) for j,v in rows[at].items()}
    need([rows[j] for j in data["word"]["centers"]]==data["reader"],"independent chronological full dirty reader")
    built=circuit.construct(data);identity=a.identity()
    basis=a.replay(built["basis"])
    for i,target in enumerate(PIVOTS):
        expected={j:a.constant(data["basis"][i][k]) for k,j in enumerate(PIVOTS) if data["basis"][i][k]}
        need(basis[target]==expected,"literal helper basis implements exact source section")
    forward,forward_peak=a.replay(built["word"],metrics=True)
    inverse,inverse_peak=a.replay(built["inverse"],metrics=True)
    fourth,fourth_peak=a.replay(built["word"]*4,metrics=True)
    target=a.expected_reader(data["reader"],Q)
    need(a.left(data["reader"],forward)==target,"all704 columns of the covariant reader")
    need(a.replay(built["inverse"],forward)==identity and
         a.replay(built["word"],inverse)==identity and fourth==identity,"both inverse orders and literal fourth power")
    need(a.replay(built["word"]*2)!=identity,"order four rather than two")
    phase_prefix=[]
    for phase in range(4):
        state=a.replay(built["word"]*phase)
        for orientation,step in (("word",1),("inverse",-1)):
            endpoint,peak=a.replay(built[orientation],state,metrics=True)
            need(endpoint==a.replay(built["word"]*((phase+step)%4)),"phase-indexed inverse boundary")
            need(F(peak["row_l1"])<=374 and peak["denominator"]<=2,"complete phase prefix allowance")
            phase_prefix.append({"phase":phase,"orientation":orientation,"bounds":peak})
    writable=set(range(112))|set(PIVOTS)
    need(all(e[1] in writable for e in built["word"]+built["inverse"]),"584 protected destinations at every prefix")
    need(all(forward[j]==identity[j] for j in range(704) if j not in writable),"protected dirty outputs")
    need(a.left(data["reader"],forward)!=a.reader_rows(data["reader"]),"caller must consume the changed query action")
    # On payload address zero, M_sigma is identity. This gives an actual
    # physical norm witness, not only a formal group-ring coefficient norm.
    norm=sum(sum(row.get(224,a.ZERO))**2 for row in forward)
    need(norm==6,"nonunitary source action on actual helper224")
    j=next(j for j,(i,_) in enumerate(data["permutation"]) if i!=j)
    kernel={j:F(1)}
    for k,target_field in enumerate(PIVOTS):
        value=-sum(data["inverse"][k][i]*data["reader"][i].get(j,0) for i in range(8))
        if value:kernel[target_field]=value
    image=[sum(sum(poly)*kernel.get(k,0) for k,poly in row.items()) for row in forward]
    need(all(sum(value*kernel.get(k,0) for k,value in row.items())==0 for row in data["reader"]),"actual reader kernel witness")
    need(any(image[k]!=kernel.get(k,0) for k in range(704)) and
         all(sum(value*image[k] for k,value in row.items())==0 for row in data["reader"]),"kernel invariant but not pointwise fixed")
    controls=[]
    segment=list(data["program"][7401:12550])
    segment.append(["residual_adapter","pre",PIVOTS[0],0,124])
    try:helper_entries(segment,data["helper_support"])
    except ValueError as error:need("residual input wrapper" in str(error),"helper wrapper mutation reaches boundary guard")
    else:raise ValueError("supported helper wrapper mutation accepted")
    controls.append({"kind":"supported_helper_entry_wrapper","field":PIVOTS[0]})
    omitted=next(j for j in data["helper_support"] if j not in PIVOTS and
                 tuple(data["columns"][j][i] for i in Q)!=data["columns"][j])
    bad_chart=built["basis"]+[e for e in built["load"] if e[2]!=omitted]
    bad=built["data"]+bad_chart+built["cycle"]+[("z",j,1) for j in PIVOTS]+circuit.invert(bad_chart)
    bad_map=a.replay(bad);bad_reader=a.left(data["reader"],bad_map)
    need(a.replay(bad*4)==identity and a.replay(circuit.invert(bad),bad_map)==identity,"coherent helper mutant passes group controls")
    need(all({j:p for j,p in row.items() if j<112}=={j:p for j,p in correct.items() if j<112}
             for row,correct in zip(bad_reader,target)),"coherent helper mutant passes data-only columns")
    need(bad_reader!=target,"all-dirty reader rejects omitted helper")
    controls.append({"kind":"coherent_helper_omission","field":omitted,"passes_weak_controls":True})
    sign=next(i for i,e in enumerate(built["data"]) if e[0]=="scale")
    bad=built["word"][:sign]+built["word"][sign+1:]
    need(a.left(data["reader"],a.replay(bad))!=target,"unsigned data mutation")
    controls.append({"kind":"lost_data_sign"})
    bad=[("z",e[1],-1) if e[0]=="z" else e for e in built["word"]]
    need(a.left(data["reader"],a.replay(bad))!=target,"inverse payload generator mutation")
    controls.append({"kind":"inverse_payload_generator"})
    bad=built["word"][:-1]
    need(a.replay(circuit.invert(built["word"]),a.replay(bad))!=identity,"lost inverse helper gate")
    controls.append({"kind":"lost_uncompute_gate"})
    centre=data["program"][12550:12759]
    counts=Counter(e[0] for e in centre)
    descents=[e for e in centre if e[0]=="center"]
    need(descents==[["center",i,415+i,0,8] for i in range(8)],"original eight centre descents remain")
    return {"reader_shape":[8,704],"reader_scalar_events":len(data["gates"]),
            "reader_sha256":digest([{str(j):str(v) for j,v in sorted(row.items())} for row in data["reader"]]),
            "helper_support":len(data["helper_support"]),"helper_pivots":list(PIVOTS),
            "helper_determinant":str(data["determinant"]),"binary_rows":list(data["sigma"]),
            "signed_data_counts":dict(Counter(sign for i,sign in data["permutation"])),
            "permutation_sha256":digest(data["permutation"]),
            "word_sha256":digest(built["word"]),"inverse_sha256":digest(built["inverse"]),
            "all_column_map_sha256":digest(a.encoded(forward)),
            "invoice":circuit.invoice(built["word"]),"helper_invoice":circuit.invoice(built["helper"]),
            "prefix":{"forward":forward_peak,"inverse":inverse_peak,"fourfold":fourth_peak},
            "phase_prefix":phase_prefix,
            "fixed_fields":584,"norm_squared_helper224":str(norm),"kernel_pointwise_fixed":False,
            "controls":controls,"original_centre_interval":{"event_counts":dict(counts),
                "positive_rank_children":8,"rank_mass":64,"deleted_children_claimed":0}}
