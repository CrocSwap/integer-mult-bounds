"""Kernel-checkable finite profile search instance, including old-profile rejection.

Analytic logarithm and exponential enclosures are explicit inherited contracts.
This script never changes the source graph, compiler words, or upstream files.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, hashlib, importlib.util, json, subprocess, sys

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
BASE = WORKSPACE / 'work/matrix-synthesis/bridge/pr62'
GEN = WORKSPACE / 'work/matrix-synthesis/audit/generate_frontier_case.py'
ap = argparse.ArgumentParser()
ap.add_argument('weighted_json', type=Path)
ap.add_argument('--output', type=Path, default=HERE/'ProfileSearchCertificate.lean')
ap.add_argument('--old-profile', type=Path,
    default=BASE/'research/pair-assembly/frame/frame-certificate.json')
args = ap.parse_args()
data = json.loads(args.weighted_json.read_text(encoding='utf-8'))
old = json.loads(args.old_profile.read_text(encoding='utf-8'))
old_sha = hashlib.sha256(args.old_profile.read_bytes()).hexdigest()
assert old_sha == data['source_certificate_sha256']
subprocess.run([sys.executable, str(GEN), str(args.weighted_json),
    '--scoped', '39859/781289859', '--published', '5101691/100000000000',
    '--source-pin', 'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
    '--label', 'new profile-aware compiler words on frozen PR62',
    '--output', str(args.output)], check=True)
spec = importlib.util.spec_from_file_location('frozen62_math',
    BASE/'scripts/experiments/binary_frame_math.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
a = Q(data['bit_saving']); scale = data['rows'][0]['rounding_scale']
old_bit = old['bit']; m = old_bit['m']; volume = old_bit['W']
assert m == data['m']
rows = []
exact_lower = Q()
for width, count in sorted((int(t), n) for t, n in old_bit['child_multiplicities'].items()):
    lo, _ = module.logs(Q(m, width))
    u = a*lo
    lower = width*(1+u+u*u/2+u*u*u/6)
    rounded = (lower*scale).numerator//(lower*scale).denominator
    assert 0 <= u < 1 and Q(rounded, scale) <= lower
    rows.append(dict(width=width, multiplicity=count, log_lower=str(lo),
        rounded_numerator=rounded, F_lower=str(lower)))
    exact_lower += count*lower/Q(m*volume)
assert exact_lower == Q(data['comparison']['frozen62_network_at_new_saving_lower'])
numerator = sum(r['multiplicity']*r['rounded_numerator'] for r in rows)
denominator = scale*m*volume
assert numerator > denominator
old_rank_mass = sum(r['width']*r['multiplicity'] for r in rows)

def rat(value):
    q = Q(value)
    return f'Rat.divInt ({q.numerator}) ({q.denominator})'

source = args.output.read_text(encoding='utf-8')
source += f'''
/- The unchanged frozen62 complete profile fails at the new saving. The
kernel verifies its explicit Taylor polynomial, downward rounding and weighted
sum. Logarithm lower enclosure and exp(u) >= 1+u+u^2/2+u^3/6 remain analytic
contracts. This establishes a finite conditional structural separation; it is
not a lower bound against other compiler words or multiplication algorithms.
Old source profile SHA256 {old_sha}.
-/
namespace RefinedFrontierCertificate

structure OldRow where
  width : Nat
  multiplicity : Nat
  logLower : Rat
  roundedNumerator : Nat

def oldRows : List OldRow := [
'''
source += ',\n'.join(f'  ⟨{r["width"]},{r["multiplicity"]},{rat(r["log_lower"])},{r["rounded_numerator"]}⟩' for r in rows)
source += f'''
]

def oldU (r : OldRow) : Rat := saving*r.logLower
def oldTaylor (r : OldRow) : Rat :=
  (r.width : Rat)*(1+oldU r+(oldU r*oldU r)/2+(oldU r*oldU r*oldU r)/6)
def oldNumerator : Nat :=
  (oldRows.map (fun r => r.multiplicity*r.roundedNumerator)).sum
def oldMomentLower : Rat := Rat.divInt (oldNumerator : Int) {denominator}

theorem old_profile_rank_mass :
    (oldRows.map (fun r => r.width*r.multiplicity)).sum = {old_rank_mass} := by decide +kernel

theorem old_weighted_numerator_exact : oldNumerator = {numerator} := by decide +kernel

theorem old_taylor_rounding_checked :
    oldRows.all (fun r => decide (0 <= oldU r ∧ oldU r < 1 ∧
      Rat.divInt (r.roundedNumerator : Int) {scale} <= oldTaylor r)) = true := by decide +kernel

theorem old_profile_lower_above_one : 1 < oldMomentLower := by decide +kernel

end RefinedFrontierCertificate

#print axioms RefinedFrontierCertificate.old_profile_rank_mass
#print axioms RefinedFrontierCertificate.old_weighted_numerator_exact
#print axioms RefinedFrontierCertificate.old_taylor_rounding_checked
#print axioms RefinedFrontierCertificate.old_profile_lower_above_one
'''
args.output.write_text(source, encoding='utf-8')
lower_path = args.output.with_name('old-profile-lower-data.json')
lower_path.write_text(json.dumps(dict(source_profile_sha256=old_sha,
    candidate_weighted_sha256=hashlib.sha256(args.weighted_json.read_bytes()).hexdigest(),
    bit_saving=str(a), m=m, W=volume, rows=rows,
    weighted_lower_numerator=numerator, weighted_lower_denominator=denominator,
    exact_unrounded_lower=str(exact_lower),
    lower_strict_gap=str(Q(numerator,denominator)-1)), indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(output=str(args.output), theorems=15,
    output_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
    old_rounded_lower_gap=str(Q(numerator, denominator)-1),
    old_lower_data=str(lower_path)), indent=2))
