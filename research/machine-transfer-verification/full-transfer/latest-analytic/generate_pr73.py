"""Generate rational witnesses; Lean independently proves their analytic validity.

The positive atanh calculation only chooses witnesses. Every resulting log
bound must pass an independent lower-exponential-polynomial rational check.
"""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
from math import factorial
import argparse
import json

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("source",type=Path)
parser.add_argument("--saving",default="12854322426487/250000000000000000")
parser.add_argument("--output-dir",type=Path,required=True)
parser.add_argument("--lean-output",type=Path,required=True)
args=parser.parse_args()
source=args.source
output=args.output_dir
raw = source.read_bytes()
profile = json.loads(raw)["bit"]
a = Q(args.saving)
assert a == Q(json.loads(raw)["bit_saving"])
assert 0 < a < 1 and profile['m'] > 1 and profile['W'] > 0
LOG_SCALE = 10**24
EXP_SCALE = 10**28
LOG_TERMS = 24
EXP_TERMS = 8


def ceil_grid(q, scale):
    return Q(-((-q * scale).numerator // (-q * scale).denominator), scale)


def log_witness(q):
    z = (q - 1) / (q + 1)
    series = 2 * sum((z**(2*j+1) / (2*j+1) for j in range(32)), Q())
    upper = series + 2*z**65/(65*(1-z*z))
    result = ceil_grid(upper, LOG_SCALE) + Q(1, LOG_SCALE)
    assert q <= poly(result, LOG_TERMS)
    return result


def poly(x, n):
    return sum((x**i/factorial(i) for i in range(n)), Q())


def upper_exp(x):
    return poly(x, EXP_TERMS) + x**EXP_TERMS*(EXP_TERMS+1)/(factorial(EXP_TERMS)*EXP_TERMS)


L2 = log_witness(Q(2))
rows = []
moment = Q()
for t, multiplicity in sorted((int(t), n) for t, n in profile["child_multiplicities"].items()):
    r = Q(profile["m"], t)
    k = 0
    while r > 2:
        r /= 2
        k += 1
    assert 1 <= r <= 2
    L = log_witness(r)
    x = a*(k*L2+L)
    assert 0 <= x <= 1
    U = ceil_grid(upper_exp(x), EXP_SCALE)
    assert upper_exp(x) <= U
    moment += Q(multiplicity*t, profile["m"]*profile["W"])*U
    rows.append(dict(width=t,multiplicity=multiplicity,scale=k,logSmall=str(L),expUpper=str(U)))
assert moment < 1
certificate = dict(source_sha256=sha256(raw).hexdigest(), saving=str(a),m=profile["m"],W=profile["W"],
    log_terms=LOG_TERMS,exp_terms=EXP_TERMS,log_two_upper=str(L2), rows=rows,
    rational_moment_upper=str(moment), rational_gap=str(1-moment),
    scope="Rational witnesses; analytic validity and all witness inequalities must be checked in Lean")
output.mkdir(parents=True,exist_ok=True)
(output/"pr73-witnesses.json").write_text(json.dumps(certificate,indent=2)+'\n')
print("Rows",len(rows),"exact rational gap",1-moment)


def leanq(q):
    q=Q(q)
    return f"({q.numerator} / {q.denominator} : ℚ)"


decls = ["import AnalyticEnclosures", "", "namespace Pr73ProfileCertificate", "open AnalyticEnclosures",
    "open scoped BigOperators", "set_option maxRecDepth 100000", "set_option maxHeartbeats 0", "",
    "structure Row where", "  width : ℕ", "  multiplicity : ℕ", "  scale : ℕ", "  logSmall : ℚ", "  upper : ℚ", "",
    "def saving : ℚ := "+leanq(a), "def logTwoUpper : ℚ := "+leanq(L2),
    f"def m : ℕ := {profile['m']}", f"def W : ℕ := {profile['W']}",
    "def rows : List Row := ["]
decls.extend("  ⟨"+", ".join([str(r['width']),str(r['multiplicity']),str(r['scale']),leanq(r['logSmall']),leanq(r['expUpper'])])+"⟩"+( "," if i<len(rows)-1 else "]") for i,r in enumerate(rows))
decls.extend(["", "def ratio (r : Row) : ℚ := m / (r.width * 2 ^ r.scale : ℚ)",
    "def logBound (r : Row) : ℚ := r.scale * logTwoUpper + r.logSmall",
    "def argument (r : Row) : ℚ := saving * logBound r",
    "def weight (r : Row) : ℚ := (r.multiplicity * r.width : ℚ) / (m * W)",
    "def valid (r : Row) : Prop := 0 < r.width ∧ r.width < m ∧ 0 ≤ r.logSmall ∧",
    f"  ratio r ≤ expPoly r.logSmall {LOG_TERMS} ∧ 0 ≤ argument r ∧ argument r ≤ 1 ∧",
    f"  expUpper (argument r) {EXP_TERMS} ≤ r.upper",
    "instance rowValidDecidable (r : Row) : Decidable (valid r) := by unfold valid; infer_instance",
    "def validBool (r : Row) : Bool := decide (valid r)",
    "def rationalUpper : ℚ := (rows.map (fun r => weight r * r.upper)).sum", "",
    f"theorem logTwo_certificate : 0 ≤ logTwoUpper ∧ (2 : ℚ) ≤ expPoly logTwoUpper {LOG_TERMS} := by decide +kernel",
    "theorem rows_checked : rows.all validBool = true := by decide +kernel",
    "theorem rational_upper_lt_one : rationalUpper < 1 := by decide +kernel",
    "theorem rational_gap_exact : 1 - rationalUpper = "+leanq(1-moment)+" := by decide +kernel",
    f"theorem row_count : rows.length = {len(rows)} := by rfl",
    f"theorem rank_mass : (rows.map (fun r => r.width * r.multiplicity)).sum = {sum(r['width']*r['multiplicity'] for r in rows)} := by decide +kernel", "",
    "#print axioms logTwo_certificate", "#print axioms rows_checked", "#print axioms rational_upper_lt_one",
    "#print axioms rational_gap_exact", "#print axioms row_count", "#print axioms rank_mass",
    "", "end Pr73ProfileCertificate", ""])
args.lean_output.write_text('\n'.join(decls))
