"""Check the actual reciprocal family with exact matrix arithmetic."""

from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from math import lcm
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES/"controller-followthrough-20261017/reciprocal-centres-20261018"
FREEZE_PIN = "8dbeea6d6ed538592b7f20cb651dd1ad257a1fbaa60c9b0d3c04a2a51e98c99e"
DATA_PIN = "0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee"
SELF_PIN = sha256(Path(__file__).read_bytes()).hexdigest()


def need(test, message):
    if not test:
        raise ValueError(message)


def identity(n):
    return [[F(i==j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def mul(a,b):
    columns = transpose(b)
    return [[sum((x*y for x,y in zip(row,col) if x and y), F(0)) for col in columns] for row in a]


def add(a,b,c=F(1)):
    return [[x+c*y for x,y in zip(row,other)] for row,other in zip(a,b)]


def scale(a,c):
    return [[c*x for x in row] for row in a]


def submatrix(a,rows,columns=None):
    columns = rows if columns is None else columns
    return [[a[i][j] for j in columns] for i in rows]


def diagonal(values):
    return [[F(v) if i==j else F(0) for j in range(len(values))] for i,v in enumerate(values)]


def determinant(a):
    """Clear each row denominator, then use integer Bareiss elimination."""
    n = len(a)
    rows, denominator = [], 1
    for row in a:
        d = lcm(*(v.denominator for v in row))
        rows.append([int(v*d) for v in row])
        denominator *= d
    sign, previous = 1, 1
    for j in range(n-1):
        pivot = next((k for k in range(j,n) if rows[k][j]),None)
        if pivot is None:
            return F(0)
        if pivot != j:
            rows[j],rows[pivot] = rows[pivot],rows[j]
            sign = -sign
        value = rows[j][j]
        for r in range(j+1,n):
            for c in range(j+1,n):
                numerator = value*rows[r][c]-rows[r][j]*rows[j][c]
                need(numerator%previous == 0, "Exact Bareiss division")
                rows[r][c] = numerator//previous
            rows[r][j] = 0
        previous = value
    return F(sign*rows[-1][-1],denominator)


def inverse(a):
    n = len(a)
    rows = [list(row)+unit for row,unit in zip(a,identity(n))]
    for j in range(n):
        pivot = next(k for k in range(j,n) if rows[k][j])
        rows[j],rows[pivot] = rows[pivot],rows[j]
        value = rows[j][j]
        rows[j] = [x/value for x in rows[j]]
        for r in range(n):
            if r != j and rows[r][j]:
                value = rows[r][j]
                rows[r] = [x-value*y for x,y in zip(rows[r],rows[j])]
    return [row[n:] for row in rows]


def dyadic_unit(value):
    a,b = abs(value.numerator),value.denominator
    return bool(a) and a&(a-1)==0 and b&(b-1)==0


def product(values):
    result = F(1)
    for value in values:
        result *= value
    return result


def factor_h(kt,kr,gr,coefficients,reverse=False):
    rows = identity(40)
    if not reverse:
        rows[:8] = mul(kt,rows[:8])
        rows[:8] = add(rows[:8],mul(kr,rows[8:]))
        rows[:8] = mul(diagonal([-v for v in coefficients]),rows[:8])
        rows[8:] = mul(gr,rows[8:])
        rows[8:] = add(rows[8:],mul(transpose(kr),rows[:8]))
        rows[:8] = mul(transpose(kt),rows[:8])
    else:
        rows[:8] = mul(inverse(transpose(kt)),rows[:8])
        rows[8:] = add(rows[8:],mul(transpose(kr),rows[:8]),F(-1))
        rows[8:] = mul(gr,rows[8:])
        rows[:8] = mul(diagonal([-1/v for v in coefficients]),rows[:8])
        rows[:8] = add(rows[:8],mul(kr,rows[8:]),F(-1))
        rows[:8] = mul(inverse(kt),rows[:8])
    return rows


def block(a,b,c,d):
    return [x+y for x,y in zip(a,b)]+[x+y for x,y in zip(c,d)]


def main():
    raw = (SOURCE/"FREEZE.json").read_bytes()
    need(sha256(raw).hexdigest()==FREEZE_PIN,"Producer freeze pin")
    for name,digest in json.loads(raw)["files"].items():
        need(sha256((SOURCE/name).read_bytes()).hexdigest()==digest,"Frozen producer file: "+name)
    raw = gzip.decompress((SOURCE.parent/"bipartite-eight-20261018/BIPARTITE-EIGHT-PROGRAM.json.gz").read_bytes())
    need(sha256(raw).hexdigest()==DATA_PIN,"Actual signed source")
    data = json.loads(raw)
    sparse = lambda rows:[{int(p):F(v) for p,v in row.items()} for row in rows]
    full_g,full_k,full_response = map(sparse,(data["signed_monomial"],data["centre_rows"],data["response"]))
    large,small = data["large_ports"],data["small_ports"]
    need(set(large).isdisjoint(small) and set(large)|set(small)==set(range(112)) and
         all(set(row)<=set(large) for row in full_k) and
         all(not full_g[p] for p in small) and
         all(set(full_response[p])<=set(small) for p in small),
         "No hidden centre or small-complement cross block")
    index = {p:i for i,p in enumerate(large)}
    selected = [index[p] for p in data["selected_ports"]]
    partners = [index[p] for p in data["partner_ports"]]
    residual = [index[p] for p in data["residual_ports"]]
    ordinary = partners+residual
    need(len(large)==48 and len(small)==64 and len(set(ordinary))==40 and
         set(selected).isdisjoint(ordinary),"Actual port partition")
    g = [[full_g[p].get(r,F(0)) for r in large] for p in large]
    k = [[row.get(p,F(0)) for p in large] for row in full_k]
    alpha = list(map(F,data["component_signs"]))
    need(alpha==[1,-1,1,-1,1,-1,1,-1],"Actual alternating signs")
    kt = transpose(k)
    need(mul(k,kt)==scale(identity(8),F(12)),"Exact independent centre rows")
    need(g==transpose(g) and mul(g,g)==identity(48) and determinant(g)==1,"Actual signed involution")
    need(mul(g,kt)==mul(kt,diagonal(alpha)),"Actual signed centre action")
    base = [[full_response[p].get(r,F(0)) for r in large] for p in large]
    need(base==add(g,scale(mul(mul(kt,diagonal(alpha)),k),F(1,2)),F(-1)),
         "The family contains the actual frozen beta=1/2 response")
    ks = submatrix(k,list(range(8)),selected)
    kpartner = submatrix(k,list(range(8)),partners)
    kr = submatrix(k,list(range(8)),residual)
    gr = submatrix(g,residual)
    need(determinant(ks)==-4 and abs(determinant(kpartner))==4,"Both selected centre bases")
    need(not any(any(row) for row in submatrix(g,selected)),"Selected G is zero")
    need(all({j for j,v in enumerate(g[i]) if v} <= set(partners) for i in selected) and
         all({j for j,v in enumerate(g[i]) if v} <= set(selected) for i in partners) and
         mul(gr,gr)==identity(32),"Partner permutation and residual closure")
    small_response = [[full_response[p].get(r,F(0)) for r in small] for p in small]
    need(mul(small_response,small_response)==scale(identity(64),F(4)) and
         determinant(small_response)==2**64,"Exact full64 complement")
    allowed = [F(1,4),F(1,8),F(-1,4),F(1,16)]
    cases = [(f"uniform_{v}",[v]*8) for v in allowed]
    cases += [
        ("mixed_independent",[allowed[i] for i in (3,3,0,1,2,0,2,1)]),
        ("old_principal_units_only",[F(1,2)]*8),
        ("full_unit_nonprincipal",[F(3,4)]*8),
        ("zero_selected_minor",[F(0)]+[F(1,4)]*7),
        ("mixed_unbounded_exponents",[(1-F(-2)**n)/12 for n in (-9,-4,-3,-1,1,3,5,8)]),
    ]
    reports = []
    for name,beta in cases:
        spectral = [1-12*b for b in beta]
        need(all(spectral),"All dyadic choices have nonzero centre eigenvalues")
        e = add(g,mul(mul(kt,diagonal([a*b for a,b in zip(alpha,beta)])),k),F(-1))
        ei = add(g,mul(mul(kt,diagonal([a*b/s for a,b,s in zip(alpha,beta,spectral)])),k))
        need(mul(e,ei)==mul(ei,e)==identity(48),"Both exact response inverse orders")
        l,h = submatrix(e,selected),submatrix(e,ordinary)
        dl,dh = determinant(l),determinant(h)
        expected = 16*product(beta)
        need(dl==dh==expected and determinant(e)==product(spectral),"Direct Bareiss determinants")
        result = {"case":name,"beta":[str(v) for v in beta],"det48":str(product(spectral)),
                  "det_selected":str(dl),"det_ordinary40":str(dh),
                  "full_dyadic_unit":all(dyadic_unit(s) for s in spectral),
                  "both_principal_dyadic_units":dyadic_unit(dl)}
        if all(beta):
            coefficients = [a*b for a,b in zip(alpha,beta)]
            literal = factor_h(kpartner,kr,gr,coefficients)
            literal_inverse = factor_h(kpartner,kr,gr,coefficients,True)
            reference = inverse(h)
            need(literal==h and literal_inverse==reference and
                 mul(literal,literal_inverse)==mul(literal_inverse,literal)==identity(40),
                 "All40 arbitrary input columns of the six-step gauge and its reverse")
            b,d = submatrix(e,selected,ordinary),submatrix(e,ordinary,selected)
            li = inverse(l)
            a = block(add(scale(l,F(-1)),mul(mul(b,reference),d)),scale(mul(b,reference),F(-1)),
                      scale(mul(reference,d),F(-1)),reference)
            ai = block(scale(li,F(-1)),scale(mul(li,b),F(-1)),
                       scale(mul(d,li),F(-1)),add(h,mul(mul(d,li),b),F(-1)))
            need(mul(a,ai)==mul(ai,a)==identity(48) and determinant(a)==1,"Both local interface inverse orders")
            result["six_step_gauge_and_interface"]=True
        reports.append(result)
    need(reports[5]["full_dyadic_unit"] is False and reports[5]["both_principal_dyadic_units"] is True,
         "Principal units alone do not imply the four-value classification")
    need(reports[6]["full_dyadic_unit"] is True and reports[6]["both_principal_dyadic_units"] is False,
         "Full units alone do not imply principal units")
    # Count determinant values by a recurrence, without enumerating the producer's parameter tuples.
    states = {(1,4):1}
    for _ in range(8):
        updated = defaultdict(int)
        for (sign,power),count in states.items():
            for dv,dp in ((1,-2),(1,-3),(-1,-2),(1,-4)):
                updated[sign*dv,power+dp] += count
        states = updated
    histogram = {str(F(sign)*F(2)**power):count for (sign,power),count in states.items()}
    producer = json.loads((SOURCE/"RECIPROCAL-CENTRES.json").read_bytes())
    need(sum(histogram.values())==65536 and histogram==producer["principal_determinant_histogram"],
         "Independent eight-component count and determinant distribution")
    exponent_checks = []
    for n in range(-128,129):
        s = F(-2)**n
        beta = (1-s)/12
        need(beta.denominator&(beta.denominator-1)==0 and
             dyadic_unit(beta)==(n in (-2,-1,1,2)),"Independent finite controls of the infinite proof")
        need(-beta/s==(1-F(-2)**(-n))/12,"Reciprocity reverses the exponent")
        if dyadic_unit(beta):
            exponent_checks.append({"n":n,"beta":str(beta),"s":str(s)})
    need(sha256(Path(__file__).read_bytes()).hexdigest()==SELF_PIN,"Checker stayed fixed")
    receipt = {
        "status":"PASS_INDEPENDENT_RECIPROCAL_CENTRE_CLASSIFICATION",
        "checker_sha256":SELF_PIN,"producer_freeze_sha256":FREEZE_PIN,
        "source_payload_decompressed_sha256":DATA_PIN,"matrix_cases":reports,
        "six_step_gauge_cases":sum("six_step_gauge_and_interface" in r for r in reports),
        "parameter_count":65536,"determinant_distribution":histogram,
        "finite_exponent_controls":[-128,128],"four_unit_parameters":exponent_checks,
        "selected_centre_determinant":str(determinant(ks)),
        "partner_centre_determinant":str(determinant(kpartner)),
        "small64_determinant":str(2**64),"centre_interface_determinant":"1",
        "full112_interface_determinant":str(F(1,2**64)),
        "scope":"Exact signed48 family and its fixed64 complement. The infinite classification is proved in REVIEW.md; the finite controls do not prove completeness. No native schedule, all-stage closure, precision, or supplier invoice is claimed.",
    }
    (HERE/"REVIEW.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
