"""Concrete finite degree-eight Taylor/tail certificate; analytic scope explicit."""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, hashlib, json, re

ap = argparse.ArgumentParser()
ap.add_argument('weighted_json', type=Path)
ap.add_argument('--scoped')
ap.add_argument('--published')
ap.add_argument('--source-pin')
ap.add_argument('--output', type=Path, default=Path(__file__).with_name('CurrentRecordCertificate.lean'))
ap.add_argument('--namespace', default='CurrentRecordCertificate')
ap.add_argument('--label', default='current-record finite arithmetic')
args = ap.parse_args()
assert re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', args.namespace)
d = json.loads(args.weighted_json.read_text(encoding='utf-8'))
assert d['upper_enclosure_kind'] == 'taylor8_tail'
old_scope = args.scoped or d.get('comparison', {}).get('old_formal_scoped_limit')
old_public = args.published or d.get('comparison', {}).get('old_published_kappa')
assert old_scope and old_public
assert Q(old_public) < Q(old_scope) < Q(d['kappa'])
if args.source_pin:
    assert d['source_commit'] == args.source_pin
rows = d['rows']; scale = rows[0]['rounding_scale']
assert rows and scale > 0 and all(r['rounding_scale'] == scale for r in rows)
assert len(d['named_slacks']) == 47 and all(Q(v) > 0 for v in d['named_slacks'].values())
for r in rows:
    v = Q(d['bit_saving'])*Q(r['log_upper'])
    f = r['width']*(sum((v**j/Q(factorial(j)) for j in range(9)), Q())
        + v**9/Q(factorial(9))/(1-v/10))
    assert 0 <= v < 1 and f == Q(r['F_upper'])
    assert f <= Q(r['rounded_F_upper_numerator'], scale)
assert sum(r['multiplicity']*r['rounded_F_upper_numerator'] for r in rows) == d['weighted_upper_numerator']
assert scale*d['m']*d['W'] == d['weighted_upper_denominator']
assert sum(r['width']*r['multiplicity'] for r in rows) == d['total_rank']

def rat(value):
    q = Q(value)
    return f'Rat.divInt ({q.numerator}) ({q.denominator})'

label = args.label.replace('-/', '- /').replace('\n', ' ')
polynomial = '1/40320'
for denominator in [5040, 720, 120, 24, 6, 2, 1, 1]:
    polynomial = f'1/{denominator}+x*({polynomial})'
source = f'''import FiniteRationalChecks

/-!
Concrete finite arithmetic for {label}, source {d['source_commit']}.
Weighted input SHA256 {hashlib.sha256(args.weighted_json.read_bytes()).hexdigest()}.
Source certificate SHA256 {d['source_certificate_sha256']}.
Candidate certificate SHA256 {d['refined_certificate_sha256']}.
The kernel computes the degree-eight Taylor polynomial, ninth-term rational
tail, directed upper rounding, weighted moment and all 47 positive slacks.
The logarithm enclosure and analytic exponential tail bound are inherited
explicit contracts. Source/profile binding, completeness of assembly formulas,
physical compiler/tape transfer and the global multiplication theorem remain
external contracts. This file proves no optimization or practical speedup.
-/
namespace {args.namespace}
open FrontierRationalCertificate
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def saving : Rat := {rat(d['bit_saving'])}
def newKappa : Rat := {rat(d['kappa'])}
def oldScoped : Rat := {rat(old_scope)}
def oldPublished : Rat := {rat(old_public)}

structure Row where
  width : Nat
  multiplicity : Nat
  logUpper : Rat
  roundedNumerator : Nat

def rows : List Row := [
'''
source += ',\n'.join(f'  ⟨{r["width"]},{r["multiplicity"]},{rat(r["log_upper"])},{r["rounded_F_upper_numerator"]}⟩' for r in rows)+'\n]\n\n'
source += 'def slacks : List Rat := [\n'
slacks = list(d['named_slacks'].items())
for i, (name, value) in enumerate(slacks):
    source += f'  {rat(value)}'+(',' if i+1 < len(slacks) else '')+f' -- {name}\n'
source += f''']

def data : Data where
  width := {d['m']}
  volume := {d['W']}
  weightDenominator := {scale}
  weightedRows := rows.map (fun r => (r.multiplicity,r.roundedNumerator))
  assemblySlacks := slacks
  expectedAssemblyRows := 47
  kappa := newKappa
  latestKappa := oldScoped

def v (r : Row) : Rat := saving*r.logUpper
def partial8 (x : Rat) : Rat := {polynomial}
def taylorUpper (r : Row) : Rat :=
  (r.width : Rat)*(partial8 (v r)+(v r)^9/(362880*(1-v r/10)))

theorem weighted_numerator_exact : momentNumerator data = {d['weighted_upper_numerator']} := by decide +kernel
theorem profile_rank_mass : (rows.map (fun r => r.width*r.multiplicity)).sum = {d['total_rank']} := by decide +kernel
theorem profile_row_count : rows.length = {len(rows)} := by decide +kernel
theorem assembly_row_count : slacks.length = 47 := by decide +kernel
theorem taylor_rounding_checked :
    rows.all (fun r => decide (0 ≤ v r ∧ v r < 1 ∧
      taylorUpper r ≤ Rat.divInt (r.roundedNumerator : Int) {scale})) = true := by decide +kernel
theorem finite_checks_pass : check data = true := by decide +kernel
theorem rational_moment_upper_below_one : momentUpper data < 1 :=
  (check_sound data finite_checks_pass).2.1
theorem every_assembly_slack_positive : ∀ s ∈ slacks, 0<s :=
  (check_sound data finite_checks_pass).2.2.1
theorem exceeds_old_scoped_limit : oldScoped < newKappa :=
  checked_frontier_strict data finite_checks_pass
theorem published_below_old_scope : oldPublished < oldScoped := by decide +kernel
theorem exceeds_old_published : oldPublished < newKappa := by decide +kernel

end {args.namespace}
'''
theorems = re.findall(r'^theorem\s+(\w+)', source, flags=re.M)
source += '\n'+''.join(f'#print axioms {args.namespace}.{name}\n' for name in theorems)
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(source, encoding='utf-8')
print(json.dumps(dict(output=str(args.output), namespace=args.namespace,
    theorems=len(theorems), kappa=d['kappa'], source_commit=d['source_commit'],
    output_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest()), indent=2))
