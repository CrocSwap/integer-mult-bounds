from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,argparse,re
ap=argparse.ArgumentParser(description="Generate a concrete kernel-checkable weighted rational frontier certificate.")
ap.add_argument("weighted_json",type=Path)
ap.add_argument("--scoped",help="Stronger prior exact scoped bound; default requires JSON comparison.old_formal_scoped_limit")
ap.add_argument("--published",help="Prior exact published value; default requires JSON comparison.old_published_kappa")
ap.add_argument("--kappa",help="Optional explicit new value, must match the verified JSON")
ap.add_argument("--output",type=Path,default=Path(__file__).with_name("RefinedFrontierCertificate.lean"))
ap.add_argument("--namespace",default="RefinedFrontierCertificate")
ap.add_argument("--label",default="current source refinement")
ap.add_argument("--source-pin",help="Optional expected source commit; rejects mismatches")
args=ap.parse_args()
if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*",args.namespace):raise ValueError("Invalid namespace")
p=args.weighted_json;d=json.loads(p.read_text())
prior=d.get("comparison",{})
oldScope=args.scoped or prior.get("old_formal_scoped_limit")
oldPublished=args.published or prior.get("old_published_kappa")
if not oldScope or not oldPublished:raise ValueError("Explicit prior scoped and published fractions are required")
if args.kappa and Q(args.kappa)!=Q(d["kappa"]):raise ValueError("New kappa differs from verified input data")
if args.source_pin and d["source_commit"]!=args.source_pin:raise ValueError("Source pin mismatch")
if not Q(oldPublished)<Q(oldScope)<Q(d["kappa"]):raise ValueError("Candidate must beat the stronger prior scoped bound and publication")
label=args.label.replace("-/","- /").replace("\n"," ")
def rat(s):
 q=Q(s);return f'Rat.divInt ({q.numerator}) ({q.denominator})'
rows=d['rows'];scale=rows[0]['rounding_scale']
assert all(r['rounding_scale']==scale for r in rows) and scale>0
assert rows and len(d['named_slacks'])==47
assert all(Q(v)>0 for v in d['named_slacks'].values())
for r in rows:
 v=Q(d['bit_saving'])*Q(r['log_upper']);f=r['width']*(1+v+v*v/(2*(1-v/3)))
 assert f==Q(r['F_upper']) and f<=Q(r['rounded_F_upper_numerator'],scale)
assert sum(r['multiplicity']*r['rounded_F_upper_numerator']for r in rows)==d['weighted_upper_numerator']
source=f'''import FiniteRationalChecks

/-!
Concrete finite rational certificate for {label}, source {d['source_commit']}.
Input export SHA256 {hashlib.sha256(p.read_bytes()).hexdigest()}.
Source certificate SHA256 {d['source_certificate_sha256']}.
Refined certificate SHA256 {d['refined_certificate_sha256']}.
The kernel computes the Padé rational expressions, upward rounding, weighted
moment envelope and all 47 assembly slacks. The logarithm upper-enclosure and
exponential Padé analytic validity remain ordinary explicit inherited contracts;
this file does not claim a fully formalized global multiplication theorem.
-/
namespace Refined54Certificate
open FrontierRationalCertificate
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def saving : Rat := {rat(d['bit_saving'])}
def newKappa : Rat := {rat(d['kappa'])}
def oldScoped : Rat := {rat(oldScope)}
def oldPublished : Rat := {rat(oldPublished)}

structure Row where
  width : Nat
  multiplicity : Nat
  logUpper : Rat
  roundedNumerator : Nat

def rows : List Row := [
'''
source+=',\n'.join(f'  ⟨{r["width"]},{r["multiplicity"]},{rat(r["log_upper"])},{r["rounded_F_upper_numerator"]}⟩'for r in rows)+'\n]\n\n'
source+='def slacks : List Rat := [\n'+',\n'.join(f'  {rat(v)} -- {k}'for k,v in d['named_slacks'].items())+'\n]\n\n'
# Put commas before comments, otherwise the comma disappears into the comment.
source=source.replace(' -- ', ' -- ')
lines=[]
for line in source.splitlines():
 if ' -- ' in line and line.endswith(','):
  line=line[:-1].replace(' -- ', ', -- ',1)
 lines.append(line)
source='\n'.join(lines)+'\n'
source+=f'''def data : Data where
  width := {d['m']}
  volume := {d['W']}
  weightDenominator := {scale}
  weightedRows := rows.map (fun r => (r.multiplicity,r.roundedNumerator))
  assemblySlacks := slacks
  expectedAssemblyRows := 47
  kappa := newKappa
  latestKappa := oldScoped

def v (r : Row) : Rat := saving*r.logUpper
def padeUpper (r : Row) : Rat :=
  (r.width : Rat)*(1+v r+(v r*v r)/(2*(1-v r/3)))

theorem weighted_numerator_exact : momentNumerator data = {d['weighted_upper_numerator']} := by decide +kernel

theorem profile_rank_mass : (rows.map (fun r => r.width*r.multiplicity)).sum = {d['total_rank']} := by decide +kernel

theorem profile_row_count : rows.length = {len(rows)} := by decide +kernel

theorem assembly_row_count : slacks.length = 47 := by decide +kernel

theorem pade_rounding_checked :
    rows.all (fun r => decide (0 ≤ v r ∧ v r < 1 ∧
      padeUpper r ≤ Rat.divInt (r.roundedNumerator : Int) {scale})) = true := by decide +kernel

theorem finite_checks_pass : check data = true := by decide +kernel

theorem rational_moment_upper_below_one : momentUpper data < 1 :=
  (check_sound data finite_checks_pass).2.1

theorem every_assembly_slack_positive : ∀ s ∈ slacks, 0<s :=
  (check_sound data finite_checks_pass).2.2.1

theorem exceeds_old_scoped_limit : oldScoped < newKappa :=
  checked_frontier_strict data finite_checks_pass

theorem published_below_old_scope : oldPublished < oldScoped := by decide +kernel

theorem exceeds_old_published : oldPublished < newKappa := by decide +kernel

end Refined54Certificate

#print axioms Refined54Certificate.weighted_numerator_exact
#print axioms Refined54Certificate.pade_rounding_checked
#print axioms Refined54Certificate.finite_checks_pass
#print axioms Refined54Certificate.rational_moment_upper_below_one
#print axioms Refined54Certificate.every_assembly_slack_positive
#print axioms Refined54Certificate.exceeds_old_scoped_limit
#print axioms Refined54Certificate.exceeds_old_published
'''
source=source.replace('Refined54Certificate',args.namespace)
out=args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(source,encoding='utf-8')
print(json.dumps({'output':str(out),'namespace':args.namespace,'theorems':source.count('\ntheorem '),'source_commit':d['source_commit'],'weighted_rows':len(rows),'assembly_rows':len(d['named_slacks']),'kappa':d['kappa'],'prior_scoped':oldScope,'prior_published':oldPublished,'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
