"""Verify all character certificates and emit the physical translation kernels."""

from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
CAMPAIGN = LANES.parent
SELF_PIN = sha256(Path(__file__).read_bytes()).hexdigest()
SOURCES = {
    "response": (
        LANES/"new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json",
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c", False),
    "directions": (
        LANES/"history-encoding/independent-skeleton-20261018/fresh-three-child/FRESH-THREE-CHILD-PROGRAMS.json.gz",
        "b08cb4146f1aec241e027cd62c942f6eca4ddab3e97f000a9c0017575d36deb5", True),
    "inverse_certificate": (
        CAMPAIGN/"root/RANK30-PHASE-SECTION-BLOCKS-20261020.json.gz",
        "91b546da328fbf4a58b9fbf92c5851ec7a66402d3c2bcf7a52ce3e1533052bc8", True),
    "root_receipt": (
        CAMPAIGN/"root/RANK30-PHASE-SECTION-CHECKS-20261020.json",
        "04121bb27884df692fd13e042f9f7b8ab005982535a07f7c95e3b1de5dfcaee7", False),
    "actual_data_views": (
        LANES/"bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473", False),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def matrix_product(a,b):
    columns = list(zip(*b))
    return [[sum(x*y for x,y in zip(row,col)) for col in columns] for row in a]


def fwht(values):
    out = list(values)
    step = 1
    while step < len(out):
        for base in range(0,len(out),2*step):
            for j in range(base,base+step):
                a,b = out[j],out[j+step]
                out[j],out[j+step] = a+b,a-b
        step *= 2
    return out


def dyadic_add_price(coefficient):
    n,d = abs(coefficient.numerator),coefficient.denominator
    need(n > 0 and d&(d-1)==0,"Nonzero dyadic ADD")
    return 2*(1+n.bit_length()+n.bit_count()+d.bit_length())


def kernel_summary(rows):
    common, witnesses = 1, {}
    norms = []
    for i,row in enumerate(rows):
        norms.append(sum((abs(F(n,30720)) for n in row.values()),F(0)))
        for (j,g),n in row.items():
            c = F(n,30720)
            common = lcm(common,c.denominator)
            for prime in (2,3,5):
                if c.denominator%prime == 0 and prime not in witnesses:
                    witnesses[prime] = {"output":i,"input":j,"translation":g,"coefficient":str(c)}
    return {"nonzero_coefficients":sum(map(len,rows)),
            "coefficients_per_row":list(map(len,rows)),
            "common_denominator":common,
            "exact_physical_infinity_norm":str(max(norms)),
            "norm_maximizing_rows":[i for i,n in enumerate(norms) if n==max(norms)],
            "denominator_witnesses":witnesses}


def formal_product(a,b):
    result = defaultdict(F)
    for x,c in a.items():
        for y,d in b.items():
            word = x+y
            while "DJ" in word:
                word = word.replace("DJ","")
            result[word] += c*d
    return {w:c for w,c in result.items() if c}


def formal_sum(a,b):
    out = defaultdict(F,a)
    for key,value in b.items():
        out[key] += value
    return {key:value for key,value in out.items() if value}


def swap_certificate():
    one,minus = {"":F(1)},{"":F(-1)}
    j,d = {"J":F(1)},{"D":F(1)}
    a = [one,{}]
    z = [{},one]
    a = [formal_sum(x,formal_product(j,y)) for x,y in zip(a,z)]
    z = [formal_sum(x,formal_product(minus,formal_product(d,y))) for x,y in zip(z,a)]
    a = [formal_sum(x,formal_product(j,y)) for x,y in zip(a,z)]
    z = [formal_product(minus,x) for x in z]
    wanted = [[{"":F(1),"JD":F(-1)},j],[d,{}]]
    need([a,z]==wanted,"Complete arbitrary-input swap from DJ=I only")
    square = [[{} for _ in range(2)] for _ in range(2)]
    for r in range(2):
        for c in range(2):
            for k in range(2):
                square[r][c]=formal_sum(square[r][c],formal_product(wanted[r][k],wanted[k][c]))
    need(square==[[one,{}],[{},one]],"The exact swap restores every borrowed input on its second application")
    return {"endpoint":["(I-JD)a+Jz","Da"],"square_is_identity":True,
            "single_application_restores_z":False,"physical_input_query":"T^-1 V Q x"}


def main():
    data = {}
    for name,(path,pin,compressed) in SOURCES.items():
        raw = path.read_bytes()
        if compressed:
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest()==pin,"Pinned source: "+name)
        data[name]=json.loads(raw)
    q = [r["q"] for r in data["directions"]["transfers"]]
    actual_q = {r["port"]:r["q"] for r in data["actual_data_views"]["entries"] if r["stage"]==0}
    need(len(q)==112 and q==[actual_q[p] for p in range(112)] and
         len(set(q))==112 and all(0<x<512 and x.bit_count()%2 for x in q),"The actual112 intrinsic lines")
    u = [{int(j):F(c) for j,c in row.items()} for row in data["response"]["correction_U"]]
    v = [{int(p):int(c) for p,c in row.items()} for row in data["response"]["correction_V"]]
    need(len(u)==112 and len(v)==30,"Actual factor dimensions")
    u2 = [{j:int(2*c) for j,c in row.items()} for row in u]
    need(all(2*u[p][j]==c for p,row in enumerate(u2) for j,c in row.items()),"Twice U is integral")
    cliques = data["response"]["small_cliques"]
    need(len(cliques)==14 and all(len(c) in (3,5) for c in cliques),"The14 odd cliques")
    for i,clique in enumerate(cliques,16):
        need(set(v[i])==set(clique) and all(v[i][p]==1 and u[p]=={i:F(-1)} for p in clique),
             "Each scalar block is the negative odd sum of actual translation characters")
    records = data["inverse_certificate"]["characters"]
    need([r["chi"] for r in records]==list(range(512)),"All character certificates, with no duplicate")
    b_char = []
    common, max_char_norm = 1,F(0)
    character_witnesses = {}
    for chi,record in enumerate(records):
        m = [[0]*30 for _ in range(30)]
        for i,row in enumerate(v):
            for p,c in row.items():
                sign = 1-2*((chi&q[p]).bit_count()%2)
                for j,d0 in u2[p].items():
                    m[i][j] += c*sign*d0
        need(all(m[i][j]==0 for i in range(30) for j in range(30)
                 if (i>=16 or j>=16) and i!=j),"Exact block decomposition")
        ti = [[F(x) for x in row] for row in record["large_inverse"]]
        need(len(ti)==16 and all(len(row)==16 for row in ti),"Inverse certificate size")
        b = [[int(60*x) for x in row] for row in ti]
        need(all(b[i][j]==60*ti[i][j] for i in range(16) for j in range(16)),"Integral60 inverse certificate")
        large = [row[:16] for row in m[:16]]
        expected = [[120*int(i==j) for j in range(16)] for i in range(16)]
        need(matrix_product(large,b)==matrix_product(b,large)==expected,
             "Two independent integer certificate products")
        full_b = [[0]*30 for _ in range(30)]
        for i in range(16):
            full_b[i][:16]=b[i]
        for i in range(16,30):
            s=F(m[i][i],2)
            need(s==F(record["small_diagonal"][i-16]) and s.denominator==1 and int(s)%2,
                 "Every odd scalar block is nonzero")
            need((60/s).denominator==1,"The scalar inverse divides60")
            full_b[i][i]=int(60/s)
        b_char.append(full_b)
        for i,row in enumerate(full_b):
            max_char_norm=max(max_char_norm,sum(abs(F(x,60)) for x in row))
            for j,x in enumerate(row):
                c=F(x,60)
                common=lcm(common,c.denominator)
                for prime in (3,5):
                    if c.denominator%prime==0 and prime not in character_witnesses:
                        character_witnesses[prime]={"chi":chi,"row":i,"column":j,"coefficient":str(c)}
    need(common==60 and max_char_norm==F(53,5),"Exact character denominator and row norm")
    inverse_rows = [dict() for _ in range(30)]
    d_rows = [defaultdict(int) for _ in range(30)]
    for i in range(30):
        for j in (range(16) if i<16 else [i]):
            spectrum=[b[i][j] for b in b_char]
            numerators=fwht(spectrum)
            need(fwht(numerators)==[512*x for x in spectrum],"Exact inverse Walsh transform")
            for g,n in enumerate(numerators):
                if n:
                    need(g.bit_count()%2==1,"Inverse support has the required odd translation parity")
                    inverse_rows[i][j,g]=n
                    for p,c in v[j].items():
                        d_rows[i][p,g]+=n*c
    d_rows=[{key:n for key,n in row.items() if n} for row in d_rows]
    inverse_summary,d_summary=kernel_summary(inverse_rows),kernel_summary(d_rows)
    need(inverse_summary["nonzero_coefficients"]==2712 and
         inverse_summary["common_denominator"]==120 and
         inverse_summary["exact_physical_infinity_norm"]=="88/5","Exact physical inverse kernel")
    need(d_summary["nonzero_coefficients"]==15688 and
         d_summary["common_denominator"]==120 and
         d_summary["exact_physical_infinity_norm"]=="1666/15","Exact additive query kernel")
    # Evaluate the emitted query at every character, independently of the Walsh order.
    d_evaluations=0
    for i,row in enumerate(d_rows):
        by_input=defaultdict(list)
        for (p,g),n in row.items():
            by_input[p].append((g,n))
        for chi in range(512):
            for p,terms in by_input.items():
                numerator=sum((1-2*((chi&g).bit_count()%2))*n for g,n in terms)
                expected=sum(b_char[chi][i][j]*v[j].get(p,0) for j in range(30))
                need(numerator==512*expected,"Direct evaluation of D=T^-1 V")
                d_evaluations+=1
    grouped=defaultdict(list)
    for i,row in enumerate(d_rows):
        for (p,g),n in row.items():
            c=-F(15*n,30720)
            need(c.denominator&(c.denominator-1)==0,"15D needs only dyadic ADDs")
            grouped[p,g].append([i,c.numerator,c.denominator])
    service=[]
    d_price=0
    for (p,g),targets in sorted(grouped.items()):
        need(g!=0,"No identity source view is included in the map invoice")
        service.append({"source":p,"translation":g,"target_adds":sorted(targets)})
        d_price+=sum(dyadic_add_price(F(n,d0)) for _,n,d0 in targets)
    j_price=sum(dyadic_add_price(c) for row in u for c in row.values())
    j_norm=max(sum(map(abs,row.values())) for row in u)
    need(d_price==204768 and j_price==1600 and len(service)==5812,"Exact direct additive service invoice")
    kernel=lambda rows:[[[j,g,F(n,30720).numerator,F(n,30720).denominator]
                         for (j,g),n in sorted(row.items())] for row in rows]
    program={
        "schema":"rank30-uniform-translation-section-v1",
        "T_inverse_kernel":kernel(inverse_rows),
        "D_kernel":kernel(d_rows),
        "J_rows":[{"target":p,"translation":q[p],
                   "adds":[[j,c.numerator,c.denominator] for j,c in sorted(row.items())]} for p,row in enumerate(u)],
        "additive_D_lowering":{
            "start":"Multiply each of30 target fields by15 with a coefficient scan.",
            "groups":service,
            "group_action":"Translate the named source; apply all target ADDs; translate that source back.",
            "finish":"Divide each of30 target fields exactly by15 under the declared rational-grid contract.",
            "effect":"z <- z-Da; a is unchanged",
            "owned_array_count":0,"complex_multiply15_scans":30,"complex_divide15_scans":30,
            "dyadic_real_primitives":d_price,"uniform_translation_map_calls":2*len(service),
        },
        "swap_chronology":["a += Jz","z -= Da","a += Jz","z = -z"],
        "scope":"A physical array service on disjoint a and z banks. Caller owner availability, finite coefficient-grid admission, and bit/tape costs remain separate.",
    }
    raw=(json.dumps(program,sort_keys=True,separators=(",",":"))+"\n").encode()
    (HERE/"PHASE-SECTION-PROGRAM.json.gz").write_bytes(gzip.compress(raw,mtime=0))
    need(sha256(Path(__file__).read_bytes()).hexdigest()==SELF_PIN,"Checker stayed fixed")
    receipt={
        "status":"PASS_INDEPENDENT_RANK30_PHASE_SECTION",
        "checker_sha256":SELF_PIN,
        "source_pins":{name:{"path":str(path),"sha256":pin,"decompressed":compressed}
                       for name,(path,pin,compressed) in SOURCES.items()},
        "character_count":512,"large_block_dimension":16,"scalar_blocks":14,
        "inverse_character_common_denominator":common,"inverse_character_row_norm":str(max_char_norm),
        "odd_denominator_character_witnesses":character_witnesses,
        "inverse_kernel":inverse_summary,"D_kernel":d_summary,"D_character_entry_checks":d_evaluations,
        "J_scalar_primitives":j_price,"J_physical_row_norm":str(j_norm),
        "additive_D_dyadic_primitives":d_price,"additive_D_translation_maps":2*len(service),
        "additive_D_odd_scans":{"complex_multiply15":30,"complex_divide15":30},
        "complete_swap_dyadic_primitives":d_price+2*j_price+60,
        "complete_swap_translation_maps":2*len(service)+448,
        "complete_swap_odd_scans":{"complex_multiply15":30,"complex_divide15":30},
        "swap":swap_certificate(),
        "program_decompressed_sha256":sha256(raw).hexdigest(),
        "all_width_statement":"Uniform translations form F2^9 at every positive width; Fourier blocks depend only on the XOR of the column characters. The emitted inverse is the same group-algebra element at every width.",
        "scope":"All-width algebra and a true additive physical query lowering with explicit odd-scan obligations. No complete recursive finite invoice or caller cohort is assumed.",
    }
    (HERE/"CHECKS.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(receipt["status"])
    print(json.dumps({k:receipt[k] for k in ("inverse_kernel","D_kernel","complete_swap_dyadic_primitives","complete_swap_translation_maps")},sort_keys=True))


if __name__=="__main__":
    main()
