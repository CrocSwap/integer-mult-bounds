# Signed scalar prefixes through unitary frames

## 1. The proposition and its hypotheses

Let H be any complex Hilbert space and let finitely many persistent registers
start at arbitrary x_j with ||x_j||₂ ≤ M. Private centres and coefficient
work start at zero. Each register has a label λ and each label denotes a
**unitary** T_λ. Assume the following execution contract at every cut:

1. A relabel A→B executes exactly T_B T_A⁻¹, with current label A.
2. ADD t,s,q has distinct registers and equal labels, and executes
   x_t ← x_t + q x_s. SCALE uses its stated rational coefficient. COPY
   inherits the source label; CLEAR writes zero with the stated label.
3. Relabels/complete recursive children are treated at their boundaries. Their
   implementations and exact physical realization are separate hypotheses.
4. Coefficient work is cleared, prepared from the unchanged source by the
   unsigned binary Horner and halving program, accumulated, then cleared.
   The completed complex scalar operation precedes the next frame operation.

The scalar shadow deletes relabels and runs the remaining scalar operations.
Let S^(k) be its matrix on the persistent input columns at cut k; zero private
input columns contribute nothing. Then

    x_r^(k) = T_(λ_r^(k)) Σ_j S^(k)_(r,j) T_(λ_j^(0))⁻¹ x_j,
    ||x_r^(k)||₂ ≤ M Σ_j |S^(k)_(r,j)|.                       (1)

The equality is the retained **Lemma G common-frame conjugation theorem**,
applied to each prefix, not a new conjugation theorem. See the pinned
[proof, Theorem 1 and row form](../e8-lemma-g-lean/PROOF.md). Its event induction
commutes ADD/SCALE through a common label, transports a relabel exactly,
and handles COPY/CLEAR. Prefixes inherit its hypotheses. The norm inequality
then follows from unitarity and the triangle inequality. This is a written
corollary; no new Lean theorem is claimed.

For a fixed nonzero row the bound is attained in this abstract model: choose
a unit vector u and x_j = T_(λ_j^(0)) sign(S_(r,j)) u, using zero for absent
columns. The output has norm M times the row's absolute sum after scaling
inputs by M. This establishes a sharp scalar-shadow/Hilbert input bound for
that cut. It is not a minimum physical fixed-point word length or rounding
error bound.

Crucially, take the absolute values **after** evaluating the signed row.
The existing recurrence e_t ← e_t + |q| e_s discards cancellations. Both are
valid sufficient bounds under the execution contract; the old estimate is
not an acceptance bug.

## 2. Coefficient work and partially written complex values

Write a nonzero reduced dyadic q as ±a/2^d, a>0. Unsigned binary Horner visits
integer multipliers k with 0≤k≤a and reaches a. Subsequent halvings decrease
the magnitude. Thus the exact largest row norm in coefficient preparation is

    a ||row(source)||₁.                                      (2)

The source is unchanged and differs from the target. The final accumulation
is the new target row; the scratch clear is zero. A power-of-two SCALE is a
monotone sequence of doublings or halvings followed, if needed, by negation;
its endpoints bound its intermediate row norms. COPY/CLEAR are immediate.
Consequently, the maximum over every stored row at scalar boundaries and
(2) covers every *completed complex scalar primitive*, including Horner
scratch. This proof does not assume that a macro endpoint bounds its work.

A physical store may update real/imaginary components or coordinates
sequentially. Between ideal consecutive values u,v, such a partial value is
P v + (I−P) u for an orthogonal coordinate projection P. Hence

    ||P v + (I−P) u||₂² ≤ ||u||₂² + ||v||₂² ≤ 2 M² L²,       (3)

where L is the largest ideal row norm. This possible factor is explicitly
charged. For the two selected programs, exact integer inequalities give

    2 · 131088²  < 2^(2·18),
    2 · 1154896² < 2^(2·21).

Thus the sufficient 18/21-bit envelopes also cover these partial stores;
no floating-point square root or implicit spare bit is used. Unit norm of
an endpoint alone would not justify this: a partial store from (3/5,4/5)
to (1,0) can have squared norm 41/25.

## 3. Why the hypotheses cannot be deleted

These are counterexamples to weakened interfaces, not accepted mutants of
the selected construction.

* **Equal labels.** Start a=1 and private b=0; COPY b←a; relabel b by −I;
  physically subtract b from a without aligning the labels. The shadow
  predicts a=0, while the actual value is 2. Add b back, relabel b by −I and
  clear b: the persistent endpoint is restored. Every relabel is unitary
  and exact, and the unlabelled shadow has maximum 1. The two intervening
  cross-label additions are inadmissible. A correct endpoint does not fix
  the wrong prefix argument.
* **Unitary labels.** With T₀=I and T₁=diag(K,1), K>1, the exact well-labelled
  relabel loop 0→1→0 has scalar shadow I and identity physical endpoint, but
  sends (1,0) through (K,0). The general Lemma G equality still holds; the
  norm conclusion without condition numbers does not. The executable
  control uses K=8, and the displayed family is unbounded in K.
* **Exact recipes.** After COPY b←a=1, declare both labels −I, but execute I
  for a's relabel and −I for b's. The declared labels now match; a−=b gives
  2 while the shadow gives zero. Unitarity of the operators actually run
  does not replace the exact-recipe condition.
* **Coefficient work.** In the actual selected forward word, persistent
  and centre rows never exceed 131072, but event 24223 prepares a numerator
  row of norm 131088. The four inputs 77,86,93,103 set to +1 (all others
  zero) attain it. An envelope that omits coefficient preparation is false.

The exact six-frame finite corpus includes noncommuting rational rotations,
216 label choices, 2,376 cuts and 57,024 matrix-entry equalities against the
physical execution. It illustrates (1); the induction above proves the
quantified statement for all finite words satisfying the hypotheses.

## 4. Selected-source application

The archived PR1094 provider has v=112, R=480, h=9, 704 arbitrary persistent
inputs and eight initially zero private centres. Both orientations contain
24,767 events and 19,693 scalar macros. The archive is pinned verbatim;
programs match the serialized selected provider and all 144 invocation
program hashes. The original local checker's retained copy has the same
SHA256 as the checker named in the selected source inventory.

The independent replay checks all 39,386 changed scalar rows twice: sparse
rational maps and dense integer rows with a single dyadic denominator.
Every ADD/COPY frame incidence, frame transition, wrapper interval and
all 960 pre/post wrapper unit rows are checked. All 704 arbitrary-input
endpoint columns are checked in each orientation; private rows vanish.
The full unchanged original local driver is also executed separately with
assertions enabled, including its containment/rank/phase checks and all
25 mutation controls. Its entire regenerated receipt equals the archived
receipt. The original positive estimates are independently recomputed.

For the physical interpretation, retain the construction's exact
frame/normalization recipes and common-label realization. The Clifford
building blocks P, X, diagonal Gaussian phases and
C_q=((1+i)I+(1−i)X_q)/2 are unitary: X_q is a self-adjoint involution, and the
two C eigenvalues are 1 and i. Products/inverses remain unitary. Normalizer
L,R are Gaussian monomials, also unitary. The extended labels
T_(pre,j)=R_(E,U) T_E and T_(done,j)=L_(E,U)⁻¹ T_U therefore satisfy the norm
hypothesis; see the pinned [hyperplane-end proof](../hyperplane-end-lean/PROOF.md).
This uses the retained recipe interpretation. We have not freshly executed
the full Clifford/native/physical provider replay, nor proved recipe
exactness for every current frame in Lean. The original local driver checks
which recipes are named and when, not all their physical matrix entries.

| Orientation | Positive envelope | Exact signed/work maximum L | Ideal and partial-store bits |
| --- | ---: | ---: | ---: |
| Forward | 2765345294379392599/1024 (52 bits) | 131088 | 18 |
| Backward | 14824960514781440791821/64 (68 bits) | 1154896 | 21 |

The forward peak occurs in coefficient preparation at zero-based event
24223, reading L103, with row
8e77 + 65536e86 + 65536e93 + 8e103. The backward peak is register L93 after
event 24342, with 176 nonzero input coefficients recorded in EXPECTED.json.
For each peak, a separate reverse functional replay recovers the entire
row. A numerical scalar run on its signed attaining input executes every
unsigned-Horner primitive in the whole orientation: 198766/198814 real
component operations, matching the archived primitive counts. It attains
the peak and never exceeds it. These scalar runs delete the unitary
relabels; their transfer to physical norms is exactly the conditional
corollary (1), not a claim to have simulated the 73-axis physical program.

## 5. Downstream arithmetic and limits

Under the retained global cover, complete-call, and precision compilation
hypotheses, substitute the checked **21-bit bound including partial stores**
for the old local 68-bit estimate in the unchanged source formula:

    68 + 37 + 144 + 144 + 4 = 397,
    21 + 37 + 144 + 144 + 4 = 350.

The extra terms retain the original input sup-to-L2 bound, all complete-call
and bridge growth allowances, and primitive arithmetic margin. We do not
use PR821's separate replica-count improvement. 350 is a conditional
sufficient estimate, not an optimal global bound. The production invoice
and 512-bit payload, row reserve, bootstrap, paid profile and selected κ
are unchanged. No current proof obligation is silently discharged: recursive
child internals, exact physical common-label/hosting realization, native
recipe admission, roundoff accumulation, tape/exact recovery and analytic
transfer remain inherited. No improved multiplication exponent or measured
runtime claim follows.
