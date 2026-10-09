#!/usr/bin/env python3
"""Emit a Lean arithmetic supplement from frozen data, not executable source."""
import argparse
import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--refresh-from-workspace', action='store_true')
args = parser.parse_args()
if (HERE/'input.json').exists() and not args.refresh_from_workspace:
    data = json.loads((HERE/'input.json').read_text())
else:
    freeze_path = ROOT / 'work/aligned-final-selection.json'
    portfolio_path = ROOT / 'work/spark-results/aligned-final-portfolio.json'
    freeze = json.loads(freeze_path.read_text())
    data = {'frozen_selection_sha256': sha256(freeze_path.read_bytes()).hexdigest(),
            'portfolio_sha256': sha256(portfolio_path.read_bytes()).hexdigest(),
            'axes': freeze['axes'], 'best': json.loads(portfolio_path.read_text())['best']}
freeze = {'axes': data['axes']}
best = data['best']
(HERE/'input.json').write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')
out = []
def emit(s=''): out.append(s)
def q(x):
    f = Fraction(x)
    return str(f.numerator) if f.denominator == 1 else f'({f.numerator} / {f.denominator})'
def proof(name, claim, defs=''):
    emit(f'theorem {name} : {claim} := by\n  norm_num [{defs}]\n')
emit('''import Mathlib.Tactic.NormNum
import Mathlib.Data.Nat.Choose.Basic

/-!
Exact arithmetic supplement for the frozen final frame composition.
Prepared with OpenAI assistance; inherited formulas retain their upstream credits.

This file proves rational arithmetic only. The supplied physical profile arrays,
the analytic validity of the logarithm and Taylor enclosures, and the all-size
tape/prime/recovery hypotheses are outside this module. It does not assert an
unconditional multiplication theorem. No sorry, native_decide, or new axioms.
The theorem statements recompute counts and parameter formulas rather than
merely asserting positivity of externally supplied fractions.
-/
namespace KappaCheck.AlignedFrameComposition
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000
''')
emit(f'-- Frozen selection SHA256: {data["frozen_selection_sha256"]}')
emit(f'-- Complete portfolio SHA256: {data["portfolio_sha256"]}')
emit('def m : ℕ := 23 * 25\ndef n : ℕ := Nat.choose 23 3 * Nat.choose 25 3')
for h in (23,25):
    p = freeze['axes'][str(h)]['paid_profile']
    emit(f'def roles{h} : ℕ := {p["R"]}')
    emit(f'def blocks{h} : List ℕ := {p["blocks"]}')
emit('''def width : ℕ := 2*n + Nat.choose 25 3 * roles23 + Nat.choose 23 3 * roles25
def counts : List (ℕ × ℕ) :=
  [(1, 23*n), (21, 4*n), (17, 2*n), (481, 2*n), (23, 2*n),
   (23, Nat.choose 25 3 * roles23), (529, Nat.choose 25 3 * roles23),
   (25, Nat.choose 23 3 * roles25), (525, Nat.choose 23 3 * roles25)] ++
  (blocks23.zipIdx.map fun (c,t) => (t, Nat.choose 25 3 * c)) ++
  (blocks25.zipIdx.map fun (c,t) => (t, Nat.choose 23 3 * c))
def count (t : ℕ) : ℕ :=
  (counts.map fun p => if p.1 = t then p.2 else 0).sum
def mass : ℕ := (counts.map fun p => p.1*p.2).sum
''')
proof('network_counts', 'm = 575 ∧ n = 4073300 ∧ width = 130417912',
      'm, n, width, roles23, roles25, Nat.choose')
proof('rank_mass', 'mass = 74988452500 ∧ m*width-mass = 1846900',
      'mass, counts, blocks23, blocks25, n, m, width, roles23, roles25, Nat.choose')
for t,c in sorted(best['bit']['child_multiplicities'].items(), key=lambda x:int(x[0])):
    proof(f'count_{t}', f'count {t} = {c}', 'count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose')
sizes = sorted(map(int,best['bit']['child_multiplicities']))
emit(f'def childSizes : List ℕ := {sizes}')
proof('complete_child_support','∀ p ∈ counts, p.2 ≠ 0 → p.1 ∈ childSizes','counts, blocks23, blocks25, n, roles23, roles25, Nat.choose, childSizes')
proof('strict_child_contraction','∀ t ∈ childSizes, 0 < t ∧ t < m','childSizes, m')
emit('''def a : ℚ := 52792403826155 / 1000000000000000000
def b : ℚ := 717 / 10000000
def kappa : ℚ := 52789616935221 / 1000000000000000000
def eta : ℚ := 1 / 1000000000000
def beta : ℚ := 1 / 20
def tau : ℚ := 1-a
def sigma : ℚ := 1-b
def qParam : ℚ := a*(1-2*eta)
def lp : ℚ := 1-qParam
def c : ℚ := qParam+eta/4
def epsilon : ℚ := (1-eta)/(1+qParam)
def lam : ℚ := (tau+lp)/2
def g : ℚ := epsilon*qParam
def r : ℚ := (g+1-epsilon)/2
def delta : ℚ := eta/8
def internal : ℚ := tau+(1-beta)*max (sigma-tau) 0
def leaf : ℚ := sigma+beta*(1-sigma)
def complexWidth : ℕ := 537696432
def complexRank : ℕ := 421548223824
def scalar : ℕ := 4793351472
def guardE : ℕ := 64*(complexWidth+784+scalar+1)^3
def guardB : ℕ := complexRank+guardE
def literal : ℕ := 2*scalar*complexWidth^2+8*complexRank+4*complexWidth+4+32*784
def guardC : ℕ := 32*784*guardB^2
def literalGap : ℚ := (guardE : ℚ)-literal
def rowGap : ℚ := 2000-(51/25)*(9*27+20*30)
def margins : List ℚ := [1-epsilon,a,g,a,min (1-epsilon-delta) (r-delta),1-epsilon-delta,epsilon]
''')
defs='a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar'
slacks = {
 'a_positive':'a','a_below_b':'b-a','b_below_one_over32':'1/32-b',
 'beta_positive':'beta','beta_below_one':'1-beta','phase_leaf_above_bit':'(1-beta)*b-a',
 'q_positive':'qParam','q_below_internal':'1-internal-qParam','q_below_leaf':'1-leaf-qParam',
 'c_positive':'c','c_below_one':'1-c','q_below_reservations':'c-qParam',
 'lambda_above_tau':'lam-tau','lambda_above_sigma':'lam-sigma','lambda_above_internal':'lam-internal',
 'lambda_prime_above_lambda':'lp-lam','compact_leaf':'lp-leaf','compact_reservations':'lp-(1-c)',
 'lambda_prime_below_one':'qParam','epsilon_positive':'epsilon','epsilon_below_one':'1-epsilon',
 'guard_width':'1-epsilon','K_geometry':'1-epsilon*(1+c)','K_dominates_log':'epsilon*c',
 'record_suffix':'1-epsilon','phase_local':'1-epsilon-delta','phase_boundary':'r-delta',
 'gamma_sublinear':'1-epsilon-r','cell_above_band':'epsilon-(1-r)/2','prime_interval_packing':'1-epsilon',
 'alpha_positive':'r','alpha_below_one':'1-r','alpha_below_one_fourth':'1/4-r','delta_positive':'delta',
 'delta_below_one_eighth':'1/8-delta','short_record_fallback':'epsilon-a','small_field_exposure':'1-epsilon-g',
 'artificial_boundary':'8-epsilon+r-delta-g','literal_scalar_guard':'literalGap','row_product_gap':'rowGap'}
margin_expr = ['1-epsilon','a','g','a','min (1-epsilon-delta) (r-delta)','1-epsilon-delta','epsilon']
for i,x in enumerate(margin_expr,1): slacks[f'g{i}_above_kappa']=f'({x})-kappa'
assert set(slacks)==set(best['assembly']['assembly']['constraints'])
for name,expr in slacks.items():
    value=best['assembly']['assembly']['constraints'][name]
    proof('slack_'+name, f'({expr}) = ({q(value)} : ℚ) ∧ (0 : ℚ) < ({expr})', defs)
proof('margins_strict', '∀ x ∈ margins, kappa < x', 'margins, '+defs)
proof('balanced_identities', '1-epsilon-g = eta ∧ 1-epsilon-r = eta/2 ∧ 1-epsilon*(1+c) = eta-epsilon*eta/4',defs)
proof('controlling_margin', 'g < kappa+1/1000000000000000000 ∧ kappa < g',defs)
proof('gain_over_original', 'kappa > (384569/10000000000 : ℚ) ∧ kappa > (409953/10000000000 : ℚ) ∧ (1/2^15 : ℚ) < kappa ∧ kappa < (1/2^14 : ℚ)',defs)
proof('finite_bridge', '575^9 > (2:ℕ)*529^9 ∧ 575^8 ≤ (2:ℕ)*529^8 ∧ 784^20 > (2:ℕ)*756^20 ∧ 784^19 ≤ (2:ℕ)*756^19 ∧ (2:ℕ)^26 ≤ width ∧ width < (2:ℕ)^27 ∧ (2:ℕ)^29 ≤ complexWidth ∧ complexWidth < (2:ℕ)^30 ∧ guardE > literal ∧ 2*guardB*(784-756) ≥ complexRank+guardE ∧ guardC > 2*guardB+18','width, n, roles23, roles25, Nat.choose, '+defs)
emit('''-- Rounded exponential bounds are supplied here. Their weighted sums and
-- their domination of the degree-eight Taylor arithmetic are checked below.
-- Analytic connections to real log/exp remain external to this supplement.
def taylor8 (x : ℚ) : ℚ := 1+x+x^2/2+x^3/6+x^4/24+x^5/120+x^6/720+x^7/5040+x^8/40320
def expUpper (x : ℚ) : ℚ := taylor8 x+x^9/362880/(1-x/10)
''')
moment_names=[]
for typ, side, saving in [('accepted','upper','a'),('rejected','lower','(a+1/1000000000000000000)')]:
    terms=best[typ+'_moment']['terms']
    moment=[]
    recomputed=[]
    for t,item in sorted(terms.items(),key=lambda z:int(z[0])):
        lo,hi=q(item['log_lower']),q(item['log_upper'])
        val=q(item['exp_'+side]); cnt=best['bit']['child_multiplicities'][t]
        emit(f'def {typ}_{t} : ℚ := {val}')
        proof(f'{typ}_interval_{t}',f'(0 : ℚ) ≤ {saving}*{lo} ∧ {saving}*{lo} ≤ {saving}*{hi} ∧ {saving}*{hi} < 1','a')
        expr=f'expUpper ({saving}*{hi}) ≤ {typ}_{t}' if side=='upper' else f'{typ}_{t} ≤ taylor8 ({saving}*{lo})'
        proof(f'{typ}_taylor_{t}',expr,'expUpper, taylor8, a, '+f'{typ}_{t}')
        moment.append(f'(({t}*{cnt} : ℚ)/(575*130417912))*{typ}_{t}')
        recomputed.append(f'(({t}*(count {t} : ℚ))/(m*width))*{typ}_{t}')
    emit(f'def {typ}Moment : ℚ :=\n  '+ ' +\n  '.join(moment))
    emit(f'def {typ}FromCounts : ℚ :=\n  '+ ' +\n  '.join(recomputed))
    proof(typ+'_profile_link',f'{typ}FromCounts = {typ}Moment',typ+'FromCounts, '+typ+'Moment, m, width, n, roles23, roles25, Nat.choose, '+', '.join(f'count_{t}' for t in terms))
    comparison=f'{typ}Moment < 1' if typ=='accepted' else f'1 < {typ}Moment'
    proof(typ+'_moment', f'{comparison} ∧ {typ}Moment = {q(best[typ+"_moment"][side])}',typ+'Moment, '+', '.join(f'{typ}_{t}' for t in terms))
    claim=f'{typ}FromCounts < 1' if typ=='accepted' else f'1 < {typ}FromCounts'
    emit(f'theorem {typ}_paid_moment : {claim} := by\n  rw [{typ}_profile_link]\n  exact {typ}_moment.1\n')
emit('end KappaCheck.AlignedFrameComposition')
theorems = [line.split()[1] for line in '\n'.join(out).splitlines() if line.startswith('theorem ')]
for name in theorems:
    emit(f'#print axioms KappaCheck.AlignedFrameComposition.{name}')
(HERE/'AlignedFrameComposition.lean').write_text('\n'.join(out)+'\n')
print(json.dumps({'lines':len(('\n'.join(out)).splitlines()),'lean_sha256':sha256((HERE/'AlignedFrameComposition.lean').read_bytes()).hexdigest()}))
