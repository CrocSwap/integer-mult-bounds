# A reusable optimal comparison barrier

The dimension-uniform statements below are informal proofs. The verifier supplies
exact finite corroboration. Neither is a complete multiplication theorem.

## 1. Comparison and every principal restriction

Let H be an N-by-N complex matrix with nonzero diagonal. Its real comparison
matrix M has entries

    M_ii = |H_ii|,       M_ij = -|H_ij| for i != j.

Assume there is w > 0 with Mw > 0, componentwise. For example, the weighted
strict diagonal dominance in Dugongue's #3872 supplies such a w. This assumption
is essential; invertibility of H alone does not imply it.

Write M=S(I-B), where S=diag(|H_ii|) and B is nonnegative with zero diagonal.
For W=diag(w), the row sums of W^-1 B W are strictly below one, since Mw > 0.
Thus its geometric series converges in the infinity norm. Consequently

    M^-1 = (I-B)^-1 S^-1 >= 0.

Every principal restriction M_J has the same property, using w restricted to J.
In particular, if M_J v >= 0 then v >= 0. Here inequalities are componentwise.

For any complex vector e on J, the triangle inequality gives

    M_J |e| <= |H_J e|.

Therefore, for a nonnegative residual envelope r_J,

    |H_J e| <= r_J   implies   |e| <= M_J^-1 r_J.       (1)

This also proves H_J is invertible, by applying (1) with r_J=0 to its kernel.
No inverse cache or numerical experiment is a premise of this argument.

## 2. One source barrier covers all ordered windows

Fix a full-source envelope r >= 0 and set h=M^-1 r. Then h >= 0. For every
principal index set J,

    M_J h_J = r_J + sum_(k outside J) |H_ik| h_k >= r_J. (2)

Multiplication by M_J^-1 proves

    M_J^-1 r_J <= h_J.

Combining with (1), the restriction of one precomputed source barrier certifies
the physical error after every principal-window solve. Simultaneous row/column
permutations simply reorder (1) and (2), so any legal ordered slide sequence is
covered, independently of its length. This is a residual certificate at each
current solve; it does not sum or cancel errors across a product of solves.

If y approximates the exact solution x of H_J x=b and
`|H_J y-b| <= r_J`, then `|y-x| <= h_J`. In particular, if x is independently
known to be integral, `max_i h_i < 1/2` guarantees unique nearest-integer
recovery. Integral output remains an explicit premise.

## 3. Optimality in the declared comparison method

The barrier h is the componentwise least full-source supersolution: if Md >= r,
then `d-h=M^-1(Md-r) >= 0`. It is attained, with Mh=r. When r>0, h>0, since the
diagonal term S^-1 in the nonnegative inverse series is strictly positive.

For the uniform envelope r=1, a positive test vector d with Md>0 gives the
scalar maximum-principle certificate

    ||H_J^-1||_infinity <= max_i d_i / min_i (Md)_i       (3)

for every J. To see this, divide d by t=min_i(Md)_i and apply section 2's
supersolution reasoning. Its restriction satisfies M_J(d_J/t)>=1.

Conversely d/t is a supersolution for the full source, so d/t>=h. Hence

    min_(d>0, Md>0) max_i d_i / min_i(Md)_i
      = ||M^-1 1||_infinity,

and d=h attains the minimum. When the unweighted choice d=1 is feasible, it
recovers the familiar inverse minimum-row-gap bound. Optimizing this certificate
cannot do worse than that feasible choice.

This does not say that ||H^-1||_infinity equals ||M^-1||_infinity. Comparison
discards signs and phases. It is sharp over the class with the same diagonal
magnitudes and off-diagonal magnitudes: take H=M and residual vector 1. Then
the error is exactly h. This identifies the sharpness model without asserting
optimality of a physical decoder, precision scheme or paid implementation.

## 4. The retained setup fixture

Jose Manuel's exact setup fixture, retained unchanged in #3872, is

    H = [ 4    -1     0   ]
        [ 1/3   5    -1/2 ]
        [ 0     1/4   3   ].

It is a rational setup fixture, not a production Gaussian window. Its minimum
unweighted row gap is 11/4, giving the previous certificate 4/11. Direct rational
multiplication gives

    h = (49/156, 10/39, 83/234),       Mh = (1,1,1).

All coordinates are positive, so this equation alone also supplies the required
positive dominance witness. The improved all-window error constant is

    C = 83/234 = 4/11 - 23/2574.

For `||H_J y-b||_infinity <= t`, the new componentwise bound is `|y-x|<=t h_J`.
Known-integer recovery follows whenever

    t < 1/(2C) = 117/83,

instead of the old sufficient `t < 11/8`. At t=7/5 the new error bound is
581/1170<1/2, whereas the old one is 28/55>1/2 and gives no conclusion.
There is no claim that the old method produces an incorrect answer there.

For the comparison matrix itself, residual `(117/83)1` has an error coordinate
exactly 1/2. Thus the new threshold must remain strict for the same-magnitude
comparison class. This boundary witness is not a failure claim about H itself.

## 5. Cost and scope

When M and r are rational, as in the retained fixture, preparing h uses one
rational solve in M, O(N^3) field operations with ordinary dense elimination
and its O(N^2) workspace, plus O(N) retained barrier rationals. Testing a
proposed rational barrier uses O(N^2) field operations. The general complex
theorem is an exact mathematical statement; it makes no rational-arithmetic
claim for irrational magnitudes. A window can reuse the restricted h without another
solve. Residual formation, comparison, coefficient creation, protected-page
emission, ownership, scaling and clearing remain paid work. No fixed-tape or
bit-cost improvement follows just from this arithmetic preparation component.

The exact M-matrix comparison and maximum-principle arguments are classical.
The contribution is the least reusable residual-barrier contract for this
sliding-window boundary and its new exact fixture constant and recovery margin.
The predecessor's inverse-update algorithms and replay counts are cited, not
re-audited. No selected frontier, supplier, kappa or full Gaussian guard changes.

## 6. Verifier constraints

The verifier has no recursion or dynamic code execution. Rational matrix inputs
are bounded to dimension eight and 128-bit source coefficients; the actual
enumeration is the fixed three-coordinate fixture. Its separate determinant
oracle is bounded to dimension four. The largest enumeration has 16 sign
variants, 15 ordered windows and eight residual vertices per window. Source
bytes are authenticated before AST-only literal extraction; source modules are
never imported. All mathematical gates use explicit exceptions, including under
`-O`. Functions remain below 60 physical lines. Normal runs are read-only;
receipt output is optional, exclusive-create and outside the checkout.

Power-of-Ten rule 3 has a managed-runtime deviation in verify.py: CPython and
Fraction allocate during arithmetic, so fixed post-initialization allocation
is unavailable. This is confined to a terminating finite verifier with the
explicit dimension, coefficient, source-size and enumeration bounds above.
Live matrix storage is quadratic and case comparisons stream into one digest.
The normal/optimized replay exercises these bounds and rejection controls.
Any change to larger fixture dimensions must revisit the resource bound.
Rule 10 uses warning-as-error normal/optimized execution and AST inspection;
no new repository-wide static-analysis configuration or native build is added.
