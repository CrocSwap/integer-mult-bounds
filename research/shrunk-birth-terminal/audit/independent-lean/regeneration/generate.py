#!/usr/bin/env python3
"""Generate a scoped Lean rational-arithmetic companion from input.json."""
import json
from fractions import Fraction
from pathlib import Path
from hashlib import sha256
HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'input.json').read_text()); cert=data['certificate']; profile=cert['profile']
out=[]
def emit(s=''):out.append(s)
def q(x):
 f=Fraction(x);return str(f.numerator) if f.denominator==1 else f'({f.numerator} / {f.denominator})'
def proof(name,claim,defs=''):
 emit(f'theorem {name} : {claim} := by\n  norm_num [{defs}]\n')
def pairs(d):return '['+', '.join(f'({k}, {v})' for k,v in sorted(d.items(),key=lambda z:int(z[0])))+']'
emit('''import Mathlib.Tactic.NormNum
import Mathlib.Data.Nat.Choose.Basic

/-!
Exact arithmetic companion for the shrunk-frame / birth-reuse / terminal-elision
composition. Prepared with OpenAI assistance. Upstream construction and analytic
credits are retained in the accompanying proof and source provenance.

Scope: supplied physical-count arrays, all 47 parameter slacks, seven margins,
three row stocks, scalar guards and independent degree-eight moment arithmetic.
The physical-array derivation, real logarithm / exponential enclosure validity,
and all-size framed-word, stopped-product, tape, prime and recovery hypotheses
remain external. This is not an unconditional integer-multiplication theorem.
No sorry, native_decide or additional axioms are introduced.
-/
namespace KappaCheck.ShrunkBirthTerminal
set_option maxRecDepth 20000
set_option maxHeartbeats 8000000
''')
for path,digest in data['pins'].items():emit(f'-- Source SHA256 {digest}: {path}')
emit('def h : ℕ := 24\ndef m : ℕ := h*h\ndef v : ℕ := Nat.choose h 3\ndef n : ℕ := v*v')
for name,val in [('virtualRoles',data['virtual_roles']),('births',data['births']),('terminals',data['terminals'])]:emit(f'def {name} : ℕ := {val}')
emit('def roles : ℕ := virtualRoles-births-terminals\ndef width : ℕ := 2*n+2*v*roles')
emit('def forwardHistogram : List (ℕ × ℕ) := '+pairs(data['forward_histogram']))
emit('def initialDimensionHistogram : List (ℕ × ℕ) := '+pairs(data['initial_frame_dimension_histogram']))
emit('''def counts : List (ℕ × ℕ) :=
  (forwardHistogram.map fun p => (p.1, 2*v*p.2)) ++
  (initialDimensionHistogram.map fun p => (m-h+p.1, 2*v*p.2)) ++
  [((h-1)^2, 2*n), (1, n)]
def count (t : ℕ) : ℕ := (counts.map fun p => if p.1=t then p.2 else 0).sum
def mass : ℕ := (counts.map fun p => p.1*p.2).sum
''')
cdefs='h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose'
allc=cdefs+', mass, count, counts, forwardHistogram, initialDimensionHistogram'
proof('network_counts',f'h = 24 ∧ m = 576 ∧ v = 2024 ∧ n = 4096576 ∧ roles = {profile["R"]} ∧ width = {profile["W"]}',cdefs)
proof('initial_dimension_count','(initialDimensionHistogram.map Prod.snd).sum = roles',allc)
proof('rank_mass',f'mass = {profile["total_rank"]} ∧ m*width-mass = {profile["deficit"]} ∧ n-2*v*h*(h-1) = {profile["deficit"]}',allc)
for t,cnt in sorted(profile['child_multiplicities'].items(),key=lambda z:int(z[0])):proof(f'count_{t}',f'count {t} = {cnt}',allc)
sizes=sorted(map(int,profile['child_multiplicities']));emit(f'def childSizes : List ℕ := {sizes}')
proof('complete_child_support','∀ p ∈ counts, p.2 ≠ 0 → p.1 ∈ childSizes',allc+', childSizes')
proof('strict_child_contraction','∀ t ∈ childSizes, 0 < t ∧ t < m','childSizes, h, m')
for name,key in [('a','assembly_bit'),('b','complex_saving'),('kappa','kappa'),('eta','eta'),('beta','beta'),('backoff','backoff'),('actualBitSaving','actual_bit_saving')]:emit(f'def {name} : ℚ := {q(cert[key])}')
emit('''def tau : ℚ := 1-a
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
''')
scalar=cert['finite_bridge']['complex']['scalar_group_upper']
emit(f'def scalar : ℕ := {scalar}')
emit('''def guardE : ℕ := 64*(width+m+scalar+1)^3
def guardB : ℕ := mass+guardE
def literal : ℕ := 2*scalar*width^2+8*mass+4*width+4+32*m
def guardC : ℕ := 32*m*guardB^2
def literalGap : ℚ := (guardE : ℚ)-literal
def rowCoefficient : ℕ := 367*27+200*27+9*28
def rowGap : ℚ := 32000-(51/25)*rowCoefficient
def margins : List ℚ := [1-epsilon,a,g,a,min (1-epsilon-delta) (r-delta),1-epsilon-delta,epsilon]
''')
defs='a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, '+allc
slacks = {'a_positive': 'a', 'a_below_b': 'b-a', 'b_below_one_over32': '1/32-b', 'beta_positive': 'beta', 'beta_below_one': '1-beta', 'phase_leaf_above_bit': '(1-beta)*b-a', 'q_positive': 'qParam', 'q_below_internal': '1-internal-qParam', 'q_below_leaf': '1-leaf-qParam', 'c_positive': 'c', 'c_below_one': '1-c', 'q_below_reservations': 'c-qParam', 'lambda_above_tau': 'lam-tau', 'lambda_above_sigma': 'lam-sigma', 'lambda_above_internal': 'lam-internal', 'lambda_prime_above_lambda': 'lp-lam', 'compact_leaf': 'lp-leaf', 'compact_reservations': 'lp-(1-c)', 'lambda_prime_below_one': 'qParam', 'epsilon_positive': 'epsilon', 'epsilon_below_one': '1-epsilon', 'guard_width': '1-epsilon', 'K_geometry': '1-epsilon*(1+c)', 'K_dominates_log': 'epsilon*c', 'record_suffix': '1-epsilon', 'phase_local': '1-epsilon-delta', 'phase_boundary': 'r-delta', 'gamma_sublinear': '1-epsilon-r', 'cell_above_band': 'epsilon-(1-r)/2', 'prime_interval_packing': '1-epsilon', 'alpha_positive': 'r', 'alpha_below_one': '1-r', 'alpha_below_one_fourth': '1/4-r', 'delta_positive': 'delta', 'delta_below_one_eighth': '1/8-delta', 'short_record_fallback': 'epsilon-a', 'small_field_exposure': '1-epsilon-g', 'artificial_boundary': '8-epsilon+r-delta-g', 'literal_scalar_guard': 'literalGap', 'row_product_gap': 'rowGap'}
margin_expr=['1-epsilon','a','g','a','min (1-epsilon-delta) (r-delta)','1-epsilon-delta','epsilon']
for i,x in enumerate(margin_expr,1):slacks[f'g{i}_above_kappa']=f'({x})-kappa'
assert set(slacks)==set(cert['assembly']['constraints'])
for name,expr in slacks.items():proof('slack_'+name,f'({expr}) = ({q(cert["assembly"]["constraints"][name])} : ℚ) ∧ (0 : ℚ) < ({expr})',defs)
proof('margins_strict','∀ x ∈ margins, kappa < x','margins, '+defs)
proof('balanced_identities','1-epsilon-g = eta ∧ 1-epsilon-r = eta/2 ∧ 1-epsilon*(1+c) = eta-epsilon*eta/4',defs)
proof('stopped_parameter_choice','a = min actualBitSaving ((1-beta)*b-backoff) ∧ 0 < eta ∧ eta < 1/2',defs)
proof('controlling_margin','kappa < g ∧ g < kappa+1/1000000000000000000',defs)
proof('fixed_profile_grid_exclusion','(b+1/1000000000000000000000000)/(1+b+1/1000000000000000000000000) < kappa+1/1000000000000000000',defs)
proof('gain_over_pinned_bounds','kappa > (384569/10000000000 : ℚ) ∧ kappa > (52789616935221/1000000000000000000 : ℚ) ∧ kappa > (111192082577/1000000000000000 : ℚ) ∧ (1/2^14 : ℚ) < kappa ∧ kappa < (1/2^13 : ℚ)',defs)
bridge=cert['assembly']['finite_bridge']
for name in ('bit_coarse','complex','ordinary_leaf'):
 x=bridge[name];arity=x['m'];child=x['maxchild'];degree=x['halving_degree'];w=x['W'];bits=x['wire_bits']
 proof('stock_'+name,f'({arity}:ℕ)^{degree} > 2*{child}^{degree} ∧ ({arity}:ℕ)^{degree-1} ≤ 2*{child}^{degree-1} ∧ (2:ℕ)^{bits-1} ≤ {w} ∧ {w} < (2:ℕ)^{bits}')
proof('row_stock','rowCoefficient = 15561 ∧ rowGap = (6389/25 : ℚ) ∧ 4*(32000:ℕ) = 128000','rowCoefficient, rowGap')
sem=cert['finite_bridge']['semantic']
proof('semantic_constants',f'guardE = {sem["E"]} ∧ guardB = {sem["B"]} ∧ guardC = {sem["C0"]} ∧ literal = {sem["literal_charge"]}',defs)
proof('finite_bridge','guardE > literal ∧ 2*guardB*(m-574) ≥ mass+guardE ∧ guardC > 2*guardB+18',defs)
emit('''-- The analytic meaning of supplied log intervals is external. These
-- statements prove exact rational Taylor inequalities and complete paid sums.
def taylor8 (x : ℚ) : ℚ := 1+x+x^2/2+x^3/6+x^4/24+x^5/120+x^6/720+x^7/5040+x^8/40320
def expUpper (x : ℚ) : ℚ := taylor8 x+x^9/362880/(1-x/10)
''')
for typ,side,saving in [('accepted','upper','b'),('rejected','lower','(b+1/1000000000000000000000000)')]:
 moment_data=cert['independent_moment'][typ];terms=moment_data['terms'];moment=[];recomputed=[]
 assert Fraction(moment_data['saving'])==Fraction(cert['complex_saving'])+(Fraction(1,10**24) if typ=='rejected' else 0)
 for t,item in sorted(terms.items(),key=lambda z:int(z[0])):
  lo,hi=q(item['log_lower']),q(item['log_upper']);val=q(item['exp_'+side]);cnt=profile['child_multiplicities'][t]
  emit(f'def {typ}_{t} : ℚ := {val}')
  proof(f'{typ}_interval_{t}',f'(0 : ℚ) ≤ {saving}*{lo} ∧ {saving}*{lo} ≤ {saving}*{hi} ∧ {saving}*{hi} < 1','b')
  expr=f'expUpper ({saving}*{hi}) ≤ {typ}_{t}' if side=='upper' else f'{typ}_{t} ≤ taylor8 ({saving}*{lo})'
  proof(f'{typ}_taylor_{t}',expr,'expUpper, taylor8, b, '+f'{typ}_{t}')
  assert Fraction(item['weight'])==Fraction(int(t)*cnt,profile['m']*profile['W'])
  moment.append(f'(({t}*{cnt} : ℚ)/({profile["m"]}*{profile["W"]}))*{typ}_{t}')
  recomputed.append(f'(({t}*(count {t} : ℚ))/(m*width))*{typ}_{t}')
 emit(f'def {typ}Moment : ℚ :=\n  '+' +\n  '.join(moment))
 emit(f'def {typ}FromCounts : ℚ :=\n  '+' +\n  '.join(recomputed))
 proof(typ+'_profile_link',f'{typ}FromCounts = {typ}Moment',typ+'FromCounts, '+typ+'Moment, '+cdefs+', '+', '.join(f'count_{t}' for t in terms))
 comparison=f'{typ}Moment < 1' if typ=='accepted' else f'1 < {typ}Moment'
 proof(typ+'_moment',f'{comparison} ∧ {typ}Moment = {q(moment_data[side])}',typ+'Moment, '+', '.join(f'{typ}_{t}' for t in terms))
 claim=f'{typ}FromCounts < 1' if typ=='accepted' else f'1 < {typ}FromCounts'
 emit(f'theorem {typ}_paid_moment : {claim} := by\n  rw [{typ}_profile_link]\n  exact {typ}_moment.1\n')
emit('end KappaCheck.ShrunkBirthTerminal')
names=[line.split()[1] for line in '\n'.join(out).splitlines() if line.startswith('theorem ')]
for name in names:emit(f'#print axioms KappaCheck.ShrunkBirthTerminal.{name}')
path=HERE/'ShrunkBirthTerminal.lean';path.write_text('\n'.join(out)+'\n')
print(json.dumps({'theorems':len(names),'sha256':sha256(path.read_bytes()).hexdigest(),'input_sha256':sha256((HERE/'input.json').read_bytes()).hexdigest()}))
