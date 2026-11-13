# Uniform fixed-recipe native MOVE closure from reviewed literal components

Status: proposed compositional corollary; independent review pending.
Base e54523517d0f03e58352e647c403a5af3e525a57.
Dependency: frozen source-affine MOVE package
9645d873c995412d0ef6ab8287ae10eb63350add45263883c3cd574b4e1a1bde,
including its unchanged generic positive and arbitrary-offset engines.
This is a proposed appendix, not a separate PR or new Clifford algebra.

## Fixed recipe and supplied boundary

Fix rho in1..9 and two valid nine-coordinate monomial recipes (G,b,Q,alpha,a):
G invertible overF2, b a nine-bit output mask, Q a symmetric binary9x9 matrix,
alpha inZ4^9 with alpha_i mod2=Q_ii, and a inZ4. All recipe parameters are
construction-time constants. Let M|x> = i^(a+sum alpha_i x_i+
2sum_(i<j)Q_ij x_i x_j)|Gx XOR b>. The one-column operator is

    U = M_left (C_0 C_1 ... C_(rho-1)) M_right.

Supply the reviewed complete Gamma6/DATA entry: f,r,P,S,cutoff positive,
w>=2, V=2PSrw2^(9f), header lengthE andF=E+V; distinct owners/origins,
blank required private windows and retained old history. Require rho*f<=cutoff
and actual phase-fit and every completed C-prefix integrality/range promises.
The selected common-root corollary supplies the latter only if its actual
row/view premises hold. A valid abstract recipe is not a source frame binding.

## Flattened construction and semantics

Using existing offline emitters, concatenate one fixed-rho joint guard,
`monomial_components(right,'right_')`, the fixed-rho positive component list
with its duplicate guard omitted, and `monomial_components(left,'left_')`.
Prefix central labels distinctly and apply the unchanged `transaction` emitter.
This is the construction used for authenticated MOVE24476 with other fixed
recipe parameters. It flattens component instruction lists; it does not nest
whole31-tape transactions.

Each component's public DATA is the single outer WORK stream; private port
t>=2 maps to t+2. Highest leaf port28 maps to30, so31 tapes suffice. Fixed PC
relocation and successful-halt continuation preserve literal local operations.
The outer transaction alone writes original DATA after all factors return.
Retired private ports are reused without refunding historical backing. The
same Gamma6/HOME adapter gives35 tapes and same-owner successful return.

The generic monomial theorem supplies phase->G->X_b, scalar i^(af), and the
per-column input quadratic phase. The positive theorem supplies every rho*f
C axis with unchanged f/nine-slot geometry. Composition gives U^(tensor f)
in the canonical slot-major address convention, preserving all external,
coefficient and component spectators. This is a written universal composition
argument, not extrapolation from a dense fixture. All successful return/cleanup
contracts and explicit failure limits are inherited. No runtime recipe loader,
rank selection or source-manifest interpreter is introduced.

## Complete uniform local bill

The two monomials and rho<=9 use at most198 matrix CNOTs,40 offset-conjugator
CNOTs and48 central slot-swap CNOTs:286 total. They use at most22 fixed word
envelopes (2 matrix,4 offset,16 central),2 phase passes,2 X0 reversals,9 C
leaves,1 joint guard and1 outer transaction.

Adding the dependency proof's complete helper ceilings, including descriptor
production, arithmetic, copying, return and retirement, and using
f(V+1)<=2fV andV<=fV, gives

    9,949,215 fV +974,848 E +974,875 <=2^25(fV+E+1).

The conservative incremental history sum is

    2*256 +22*64 +9*64 +2*32 +64 +8 =2632 <4096

times(V+E+1). Thus T_core<=2^25(fV+E+1) and
K_final<=K_entry+4096(V+E+1). HOME adds128(F+1) time and64(F+1) history.
Setup/program/origin provisioning, typed entry and B1 whole-bank transport
remain separate. No E=O(V) or numeric-cutoff loop assumption is introduced.

## Exact scope

This makes a common literal template and uniform local constants explicit
for every valid fixed9-slot positive-rank recipe. For any source event whose
one-column recipe and phase are independently authenticated, the existing
tensor lift supplies this primitive's all-column semantics. Applying that
implication to every catalogue entry still requires preserving its exact
source proof and entry/view premises; a finite recipe census is not a
substitute. Only actual event24476 has the complete source and physical
checks in this new package.

No additional full physical execution for every recipe or large f is claimed.
Rank-zero/non-nested variants, variable ambient dimension, whole-job153-axis
or root adapters, actual producers, view packing, cutoff policy, full ownership
lifetime and faster nonleaf tariffs remain outside this corollary. It does not
discharge native_all_columns in its full retained scope or any other selected
assumption, and gives no new kappa. Credit all predecessor literal engines
and #6978/#7000 algebra/precision work. Prepared with substantial OpenAI
assistance; independent review is not formal acceptance.
