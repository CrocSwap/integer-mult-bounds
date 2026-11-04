# Adversarial written review: signatures, helper order and width transfer

**Verdict: no algebraic gap found under the exact-operator, common-chart
and ownership premises identified below.** This is a conditional written
review of three implications, not acceptance of the source's actual task
census, compiler output, native implementation or complete application.

The source is the native-semantic companion in PR6716 at
`4a40713f10d47da5894d7673eb6d0ab2ebdf0687`. Its proof internally binds the
unchanged current native word/compiler to the earlier17c08 source. I read
only the pinned evidence/PROOF.md and evidence/COVERAGE.md, not source
Python or the coordinator's separate REVIEW. No numerical/checker run,
source import, emitted-recipe inspection or proof-kernel execution occurred.
Every control below is a hand-derived scope illustration, not a source
counterexample or an executed test.

| Reviewed text | SHA256 |
| --- | --- |
| evidence/PROOF.md | `1f1935b4e52726fed26ca6407ca8b1e3cc2122c6270d0ef4db48e4a97bf203a7` |
| evidence/COVERAGE.md | `b562622c483948b2786dd68d8883490095dbb040cb357b2d7ea1f449915a39c2` |

## 1. Exact signature uniqueness

Use one fixed ordered computational basis on the same nine-axis complex
space for both operators. The X_j,Z_j labels and their Z/4Z phase convention
must also be identical. Let U,V be invertible complex-linear operators
(unitary Clifford operators suffice). Equality of their exact conjugations
on all eighteen generators implies that W=V^-1 U commutes with every X_j
and Z_j.

This commutant claim can be checked directly. Commutation with all Z_j
forces W to be diagonal: distinct computational basis labels have distinct
tuples of Z eigenvalues. Commutation with all X_j then equates diagonal
entries along every bit flip. The bit-flip graph is connected, so W=cI.
Invertibility gives c!=0; unitarity additionally gives |c|=1.

Equality of the complete columns U|0> and V|0> gives
`c V|0>=V|0>`, hence c=1. Here |0> means the nonzero computational
basis vector e_(0,...,0), not the zero input array. Its column cannot be
zero for an invertible operator. Thus the source's signed-generator plus
exact-column criterion does determine the whole operator.

The column representation must preserve basis indices and every exact real
and imaginary coefficient, including absolute phase. With integer arrays
divided by2^k, k>=0, cancelling the maximal common power of two up to k
gives a unique dyadic representation. It does not quotient by a common
Gaussian unit. Norm1 is a useful consistency check but does not fix phase.

Two essential written controls are:

- **Unsigned I versus Z.** In one qubit, I and Z both give unsigned labels
  X->X,Z->Z, and both send |0> to |0>. Nevertheless ZXZ^-1=-X while
  IXI^-1=X. Even unsigned images plus the exact first column would fail
  to distinguish these operators. Signed images avoid this failure.
- **Signed I versus iI.** Their signed conjugations are identical and both
  first-column norms are1, but their complete columns are |0> and i|0>.
  Support or norm alone is insufficient. Full coefficient tuples avoid
  this failure, provided canonicalization does not discard their phase.

These examples expose weakened signature premises; they do not contradict
the complete signature criterion actually stated by the source.

The proof above does not establish that a given checker really evaluated
the actual emitted current recipe, used the correct axis convention or
matched every claimed task. Those are computational/source-binding premises.
Likewise, exact operator equality alone does not certify a recipe's paid
rank or physical cost. The source separately requires same-rank matching;
this written review does not independently recount it.

## 2. Whole-helper inverse order

With column-vector operator convention, operations act rightmost first.
For invertible normalizers L,R and a complete identity U=L G R, the
valid chronological sequence is

`pre R^-1; apply U; post L^-1`.

Its complete operator is `L^-1 U R^-1=G`. No commuting of L,R or G is
permitted. The equality is an operator identity on every arbitrary helper
input; it is not merely equality on a copied input, a measured functional,
or the all-zero array. Any input/output chart wrappers must be the actual
ones in this equation, with their exact phases.

A concrete written order control can stay inside the Gaussian-dyadic
alphabet. Put

`S=diag(1,i)`, `X=[[0,1],[1,0]]`,

`K=((1+i)/2)*[[1,1],[1,-1]]`, and `U=S K X`.

K is the phase-adjusted Hadamard, with dyadic Gaussian entries; the
unphased real Hadamard would introduce an unnecessary square-root
alphabet distinction. Correct normalization gives `S^-1 U X=K`.
Reversing the inverse placements gives instead

`X U S^-1=((1+i)/2)*[[-i,1],[1,-i]]`.

Its first column differs from K's by unequal coordinate ratios -i and1,
so it is not even a global-phase version of K. This illustrates why
inverse order must be checked on the complete helper map. It does not
assert that this particular example occurs in the source's helper census.

## 3. Arbitrary positive width: the conditional invariant

For each exact one-column frame T_c, let T_c[f]=T_c^(tensor f), f>=1.
For each arbitrary independently specified raw public array x_j in initial
frame a_j, define `z_j=T_a_j[f]^-1 x_j`. Each change is invertible, so
this reparametrization imposes no relation among public inputs. The z_j
need not be pure tensors or factor across address columns.

Assume every invoked map at width f is the corresponding factorwise
lift, in the same order, with literal native phases treated inside these
operators. Assume also that the checked scalar event word uses exact
common charts, including absolute phase, and that its INIT/COPY/CLEAR and
lifetime conditions satisfy the retained ownership contracts. Under these
premises the invariant is

`payload_r=T_current_frame_r[f] * sum_j s_rj z_j`.

An exact one-column multiplicative identity lifts because
`(AB)^(tensor f)=A^(tensor f) B^(tensor f)` and inverses lift in the
same order. Thus a frame-changing MOVE transports the invariant to its
new frame. Within a common chart, ADD and SCALE act linearly on the
exterior coefficient row s_rj, rather than on the address-column tensor
factors. INIT introduces an owned zero row; COPY and CLEAR are valid only
under the inherited ownership/erasure conditions, not as permission to
overwrite an arbitrary independent public input.

For helper normalization this same multiplicative rule gives

`(L^-1)^(tensor f) U^(tensor f) (R^-1)^(tensor f)=G^(tensor f)`.

The scalar row induction therefore holds on the full tensor address space,
not just separable basis tests. Exact equality of linear maps also persists
after appending I on a spectator space, so arrays correlated with spectators
are covered algebraically. This does not prove the physical spectator layout
or the concrete native_all_columns implementation contract.

Two different kinds of scalars must remain distinguished:

- A literal native global phase i^a in a one-column operator becomes
  i^(af) in its f-fold tensor power.
- An exterior field/register SCALE coefficient c remains c, acting once
  on the whole array and on its scalar coefficient row.

The width-transfer conclusion consequently relies on the event typing and
factorwise ABI. A finite endpoint coincidence at one column, without the
common-chart induction, would not supply this conclusion.

## 4. Written controls against invalid tensor and input transfers

**Scalar-sum cancellation.** Treat I and -I as two literal one-column
operators with exterior coefficients +1,+1. At width1 their sum is0.
At width2 their lifted sum is
`I^(tensor2)+(-I)^(tensor2)=2 I`, which is nonzero over C. Therefore
one cannot tensorize a width-one scalar-sum identity. If the minus sign
were instead an exterior coefficient, it would remain outside and the
different identity `I^(tensor f)-I^(tensor f)=0` would hold. The source
explicitly uses the latter scalar-row discipline rather than the former
invalid inference.

**Exterior coefficient2.** On a nonzero width-two array, an exterior
SCALE2 is `2 I^(tensor2)`, whereas tensoring the one-column matrix2I
would give `(2I)^(tensor2)=4 I`. These are different. Exterior coefficients
cannot silently be absorbed into the native tensor factors.

**Independent helper inputs.** A row x-y vanishes on a restricted copied
input x=y but not on arbitrary independent x,y. Consequently agreement on
correlated copies cannot prove a productive two-input or helper endpoint.
The source's claimed complete public-input scalar rows and whole helper
operator identities are the premises that exclude this shortcut. This
review does not independently inspect those actual rows or lifetime traces.

All these controls change or remove an explicit premise. They are not
counterexamples to the stated conditional argument and were not executed.

## 5. Remaining boundaries and attribution

No unresolved algebraic objection was found in signature uniqueness,
whole-helper inverse order or the factorwise common-chart implication.
The required premises must remain explicit: same ordered basis and mod4
phase convention; actual invertible linear operators; exact whole-column
values; actual delivered recipe identities; per-width factorwise realization;
common-chart exterior scalar semantics; independent public inputs and legal
owned lifetimes. Finite signatures alone do not prove any missing premise.

This review does not certify the claimed3,184-task/39-unmatched census,
current compiler/cache correctness, complete dense or scalar receipts,
source-custody claims, chronological physical contacts, actual tape allocation,
stock, numerical precision, compiler/outer or any of the five assumptions.
It does not inherit source-author CI or convert CI/publication into admission.
The selected frontier and paid profile remain unchanged.

Credit thu-nmrc with substantial OpenAI Codex assistance for the native
semantic application and its conditional presentation. Retain the source's
DreamingOfClouds/PR6030 and PR6702 lineage, Matarener's scalar/inventory
machinery, Clear1nsight's dense Gaussian-dyadic interpreter, Charles Bethin
and retained Clifford compiler/literal semantics, Ali Romman's current
prefix work, and all original notices. Commutant uniqueness, multiplicative
tensor functoriality and ordered normalization are classical; this review
claims no new general lifting theorem. It is separate AI-assisted written
scrutiny, not independent human acceptance or proof-kernel certification.
