# The exact sector boundary of the retained five-in-fourteen claim

Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
This is a source-bound proof audit with exact counterexamples. It does not
exclude the general five-in-fourteen problem or change the selected κ.

## 1. Object and prior disposition

Pierre-Loic Doulcet / hexapode's PR4813 claimed a complete five-array,
fourteen-call block-three unit. Its retained package is
`research/complex-block3-five-in-fourteen`; this audit pins its bytes on
canonical main `bee95ce88f9f19802f0613f92838895cd0e14a1f`. The central ledger
records archival integration and incomplete scientific review, including its
retention alongside PR4841. Archive retention is not supplier admission.

The underlying arbitrary-input triangular ports are Dugongue's PR4743 work,
using Yiyang's PR4710 phase repair and lee-phys's PR4688 prefix. Those ports
are not refuted here. The issue is a later inference from their sector
completion to unqualified independent input arrays, followed by a finite
matrix recovery test without a uniform free-decoder implementation.

## 2. Keep coefficients outside tensor powers

Let C_j be the source unitary direction on bit j, K=C_0 C_1 C_2, and let
T swap bits zero and two. Put A=C_0. The actual source also defines unitary
words D,M,a,O, with `O=K a K^-1`, and repaired free words P,Q. Its two
separate base-word identities are

`D P A = M C_2`, `D Q A = K a`.                           (1)

They are verified individually over Q(i), with absolute phase. Thus they
lift at every tensor width. Write g_f for the tensor power of each base
word g, and set

`B_f=D_f(P_f+2Q_f)A_f=M_f C_2,f+2 K_f a_f`,
`H_(f)=(1/2) O_f^-1`, `E_(f)=H_(f)D_f`.

The factor 1/2 here is applied after tensorization. It is not `(1/2)^f`.
This is the source's separately tensorized-word convention, and it avoids
silently changing the normalizer at larger widths.

For arbitrary independent x,y, the actual three-call triangular port returns

`t=A_f x`, `u=B_f x+D_f y`.

For a chosen sign sigma in {+1,-1}, the proposed normalized subtraction is

`v_actual=H_(f)(u-sigma M_f T_f t)`.

The claimed observation used by the schedule is instead

`v_declared=K_f x+E_(f)y`.                                (2)

## 3. Necessary and sufficient validity condition

The difference between those two observations is exactly

`Delta_sigma(x)=H_(f) M_f (C_2,f-sigma T_f A_f)x`

`                 = H_(f) M_f T_f A_f (T_f-sigma I)x`.    (3)

The second equality follows from the actual conjugacy `C_2=T A T`,
which also lifts at every width. All factors before `T_f-sigma I` are
unitary except the scalar 1/2 in H_(f). Consequently

`||Delta_sigma(x)||² = (1/4)||(T_f-sigma I)x||²`.          (4)

This proves an exact equivalence, for every x and every y at every positive
width: the subtraction produces (2) **if and only if** `T_f x=sigma x`.
It is not an all-input identity. The helper y is arbitrary and cancels
from the difference, so the issue does not depend on assuming clean data.

Since T is an involution with four fixed addresses, `trace T_f=4^f`.
The valid plus and minus subspaces therefore have dimensions
`(8^f+4^f)/2` and `(8^f-4^f)/2`. At width one they have dimensions six
and two; neither is the full eight-dimensional array space. An input with
components in both sectors has no single admissible sign making (2) true.

## 4. Concrete source counterexamples and true positive controls

Take width one, x=e_1 and y=e_2, both nonzero. T e_1=e_4. For either
choice of sigma, equation (4) gives squared error 1/2. The independent
interpreter obtains these exact differences, in address order:

| sigma | Nonzero entries of v_actual-v_declared |
|---|---|
| +1 | 0: (-1-i)/4; 2: (1-i)/4; 4: (1-i)/4; 6: (-1-i)/4 |
| -1 | 0: (1+i)/4; 2: (1-i)/4; 4: (1-i)/4; 6: (1+i)/4 |

RESULT.json retains the full actual, declared and difference vectors. This
is a failure of the claimed unrestricted local observation, not of the
underlying triangular port. The result is independently bound to every
matrix returned by the retained `load_operators` factory: the audit constructs
the operators from their primitive coordinates and compares the complete
matrices before checking the actual versus declared port output.

As positive controls, all vectors `(I+sigma T)e_j` satisfy the sector
identity. The exact defect matrices have ranks two for sigma=+1 and six
for sigma=-1, agreeing with the complete validity spaces above. The audit
also checks the sharp norm identity on every basis vector, not just the
displayed counterexamples.

The failure persists at every width: choose x=e_1 tensor e_0 tensor ... .
It and T_f x are orthogonal basis vectors, so both signs again give
squared error 1/2. This extension follows from (3)–(4); the finite checker
does not substitute sampling for that all-width proof.

## 5. What the retained schedule verifier actually checks

The primary `verify_schedule.py` projects its fixtures into specified swap
sectors. It tests three sign patterns. Those are genuine inputs on which
the local formula can hold; they are not arbitrary independent arrays.
In its `v_obs` construction, it then computes `K x + E y` directly rather
than executing the raw three-call port and the proposed subtraction.
Thus a failed unrestricted local observation never reaches that test.

The script constructs an 80-by-40 observation matrix. Its last forty rows
are `diag(A,A,A,A,A)`, representing the retained t_i=A x_i. A is invertible,
so these rows alone already have rank forty. The audit checks that rank
independently. The full observation matrix being injective cannot by itself
show that any additional paid port has made a useful target available.

Finally the script solves for the inputs using arbitrary Gaussian elimination
and applies K to the reconstructed arrays in its expected-target arithmetic.
It does not emit or price a uniform allowed free word for that reconstruction.
At a single finite width, arbitrary dense recovery is different from the
engine's fixed finite scalar/monomial word acting at every width.

These observations do not prove that a suitable complete decoder is impossible.
They show why this particular receipt is insufficient evidence of the claimed
fourteen-call uniform construction. Neither the finite geometry orbit count
nor a condition number supplies the missing implementation.

## 6. The missing local correction is not automatically free

Here is a separate all-width fact about the named local read interface.
Suppose only x and A_f x are available, with any number of copies and zero
scratch arrays. Grant as free every invertible monomial base matrix, arbitrary
fixed complex register mixing and any finite compositions of them, each base
matrix applied identically to all tensor columns. Then no uniform free word
can produce C_2,f x from those observations for all positive widths.

Let H be the group of all invertible eight-by-eight monomial matrices. A
free output from the stated observations is a finite sum

`sum_h alpha_h h_f x + sum_h beta_h (h A)_f x`,            (5)

where scalar coefficients are fixed across f. C_2 is nonmonomial, and
`C_2 A^-1` has four nonzero entries per row, so is also nonmonomial.
Thus C_2 lies neither in H nor in its left coset H A.

For completeness, distinct actual nonzero matrices g_1,...,g_n are linearly
independent as the families `(g_j^(tensor f))_(f>=1)`. Choose a linear
functional ell with nonzero, pairwise distinct values ell(g_j); the forbidden
choices form finitely many proper hyperplanes. A uniform linear relation,
evaluated by ell^(tensor f) for f=1,...,n, gives a Vandermonde system with
nonzero determinant. Every coefficient is zero. Actual global phases are
retained in this argument, rather than identified projectively.

Applying this separation to the finite matrices in (5) proves the assertion.
It is a local read-interface obstruction, not a statement about a global
decoder using other paid observations or a different chronology.

A finite-width control makes the distinction tangible. At width one,

`C_2 C_0^-1 = (1/2)I+(i/2)X_0-(i/2)X_2+(1/2)X_0 X_2`.

Tensorizing each of the four free words but keeping these four coefficients
does not yield `(C_2 C_0^-1)^(tensor 2)`. On e_0 tensor e_0, the squared
error is 3/2, checked exactly. A width-one matrix inverse therefore does
not automatically provide a uniform free correction. The tensor-family
separation method is standard and is also used in the credited retained
staggered-prefix obstruction; its new use here binds the actual correction
that the schedule's local formula needs.

## 7. Transport evidence and limits

On the pinned main, the retained package wrapper stops at its own manifest
guard on NOTICE.md. The complete manifest comparison also finds a
finite_geometry.py mismatch. Those byte-transport facts are recorded separately
from the mathematical counterexample; they do not prove or disprove the unit.
Running the unchanged primary `verify_schedule.py` directly emits its finite
PASS receipt. This audit authenticates its exact bytes and independently
checks the intended port matrices instead of treating that PASS as admission.

No frozen source file, notice, manifest, central scientific disposition,
selected frontier or other contributor's PR is changed. A repair needs an
actual unrestricted caller or explicit sector-processing implementation,
plus a permitted all-width decoder and a complete paid invoice. This audit
does not count missing operations as zero or assert a global lower bound
against all five-in-fourteen constructions.
