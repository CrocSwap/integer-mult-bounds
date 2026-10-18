"""Exact source-adapter and rank-zero phase checks with independent Pauli/state semantics."""
from hashlib import sha256
import importlib.util
import json

from source import ROOT, Q, need

MODULES={
    "clifford_compile.py":"9e1f82bdab26f3df20ca69c542657d04e170ad820196ef25bb67c519aeada832",
    "native.py":"8134106fb8a9ee8b065c51d950b41ef31ff3486a9d4da71f33c6a406ee054698",
}


def imported(name):
    path=ROOT/"research/involutive-walsh-lift"/name
    need(sha256(path.read_bytes()).hexdigest()==MODULES[name],"unchanged native semantics")
    spec=importlib.util.spec_from_file_location("covariant_"+path.stem,path)
    module=importlib.util.module_from_spec(spec)
    # Dataclass inspection resolves its declaring module through sys.modules.
    import sys
    sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module


def run(data):
    import algebra
    import circuit
    compiler,check=imported("clifford_compile.py"),imported("native.py")
    word=data["word"];sigma=data["sigma"];move=compiler.perm(9,sigma)
    endpoints={(r["role"],r["port"]):r for r in data["recipes"]["endpoint_adapters"]}
    need(len(endpoints)==224,"complete source endpoint inventory")
    normalized=[];literal=[]
    for j,port in enumerate(word["ports"]):
        record=endpoints["source",j]
        need(record["frame"]==word["start"][j] and record["rank"]==0,"source entry frame")
        entry=check.recipe(record)
        frame=check.frame(tuple(word["frames"][word["start"][j]]),9)
        expected=entry+check.adjoint(frame)
        check.equal(expected,(("C",port,-1),),"source normalized coordinate")
        literal.append(expected)
        normalized.append(compiler.Op(9,check.tableau(expected),list(expected)))
    data_records=[]
    for j,(i,sign) in enumerate(data["permutation"]):
        original=normalized[j].then(move).then(normalized[i].adjoint())
        reduced,record=compiler.monomial(original)
        actual=check.monomial(record)
        expected=literal[j]+(("P",sigma),)+check.adjoint(literal[i])
        check.equal(actual,expected,"data covariance including phase")
        check.equal(actual,(("P",sigma),),"source input action simplifies to common monomial")
        data_records.append({"source":j,"target":i,"sign":sign,"record":record})
    frames=[compiler.canonical_frame(9,word["frames"][index]) for index in word["center_frames"]]
    native_frames=[check.frame(tuple(word["frames"][index]),9) for index in word["center_frames"]]
    query=[];operators=[];wrong_ranks=[]
    inverse_move=move.adjoint()
    for i,j in enumerate(Q):
        original=frames[j].adjoint().then(move).then(frames[i])
        reduced,record=compiler.monomial(original)
        expected=check.adjoint(native_frames[j])+(("P",sigma),)+native_frames[i]
        check.equal(check.monomial(record),expected,"query covariance including phase")
        operators.append(reduced);query.append(record)
        wrong=frames[j].adjoint().then(inverse_move).then(frames[i])
        wrong_ranks.append(compiler.rank([x for x,z,p in wrong.tab[9:]]))
    need(wrong_ranks==[2]*8,"inverse orientation has positive rank")
    need([r["phase"] for r in query]==[0,2,0,2,0,2,0,2],"retained nonzero query phases")
    need([r["offset"] for r in query]==[172,427,282,303,172,467,282,343],"retained query offsets")
    wrong=dict(query[1]);wrong["phase"]=0
    try:check.equal(check.monomial(wrong),check.monomial(query[1]),"omitted query phase")
    except ValueError as error:need("global phase" in str(error),"phase-only mutation reaches exact state check")
    else:raise ValueError("lost phase control accepted")
    state=[(i,compiler.ident(9)) for i in range(8)]
    for _ in range(4):state=[(state[j][0],state[j][1].then(operators[i])) for i,j in enumerate(Q)]
    for i,(source,op) in enumerate(state):
        need(source==i,"query fourth-power role return")
        check.equal(op.circuit,(),"query fourth-power exact phase return")
    check.equal(move.then(move).then(move).then(move).circuit,(),"payload fourth power")
    field_word=circuit.permute(tuple(range(8)),Q)
    field_map=algebra.replay(field_word)
    need(field_map[:8]==[{j:algebra.ONE} for j in Q],"literal query field permutation")
    query_invoice=circuit.invoice(field_word)
    need(query_invoice["scalar_operations"]==24 and query_invoice["real_scalar_primitives"]==156,
         "query scalar permutation charge")
    query_invoice["payload_monomials"]=8
    query_invoice["events"]+=8
    canonical=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"))
    return {"data_blocks":112,"source_adapters":112,"query_blocks":8,
            "Pauli_generators_per_block":18,"state_dimension":512,
            "data_record_sha256":sha256(canonical(data_records).encode()).hexdigest(),
            "query_records":query,"inverse_orientation_ranks":wrong_ranks,
            "query_invoice":query_invoice,"query_field_word_sha256":sha256(canonical(field_word).encode()).hexdigest(),
            "phase_control":"rejected_by_exact_state","query_fourth_power":"identity",
            "positive_rank_children":0}
