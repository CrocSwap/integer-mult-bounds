# Actual canonical phases and the whole backward cut grid

This note corrects the physical-kernel argument in the first reset
review, receipt `f86a6122d2f883730206b37f8d21273a8b7f20d59738cf48f277423ef7fe17b5`.
That review expanded a product of intrinsic C_v gates for each listed
frame basis. The actual canonical frame includes a quadratic phase
conjugation. Its listed basis does not specify that plain product.
The earlier phase claim is withdrawn. The centre lattice and norm
conclusions remain valid, for the corrected reason proved here.
The exact cut response, rounding formula, and error-cone census in
the first review are unchanged. Its files are preserved.

## Source and actual centre operators

The selected source archive is
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.
Its exact native recipes are pinned at
`d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731`.
The canonical operator definition is read from `clifford_exact.py`,
SHA-256 `2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962`.
The checker imports none of that code.

Let G be the exact canonical basis extension. Put

    Q=I+(G^-1)^T G^-1 over F2,
    K=D_Q P_G.

The rank-r canonical frame is `K F_r K*`. The phase of D_Q is

    q(x)=sum_i Q_ii x_i + 2 sum_(i<j) Q_ij x_i x_j mod4.

For r=8, its coefficient from x to `y=G(G^-1 x+t)`, with t supported
on the first eight coordinates, is

    i^(-weight(t)+q(y)-q(x))/16.

The independent checker reconstructs G and Q from the pinned canonical
basis. It also evaluates the pinned `left * F_8 * right` native recipe
directly, with its actual address maps, translations, linear phases,
upper-triangular quadratic phases, and global phase. The two operators
agree on all 512 columns for every one of the eight centre frames.
This checks 4,096 complete columns and 1,048,576 nonzero coefficients.
The omitted quadratic conjugation produces a recorded phase failure
in every centre frame.

Every physical column and row has 256 Gaussian-unit coefficients
divided by 16. The real-block infinity norm is 16. Tensor width f
therefore gives grid denominator `2^(4f)` and norm `2^(4f)`. Gaussian
monomial conjugation preserves both conclusions. Exterior directions
are spectators and commute with the full local canonical operator,
including its monomial factors. No cancellation of listed frame
vectors is used.

## A uniform grid for all 704 fields at the backward cut

The raw backward prefix stops before event 12995. Its pin is
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
The checker replays every prefix scalar and native frame condition.
At the cut it records all 5,476 nonzero scalar coefficients of the
704 input rows. Their maximum denominator is four. Their maximum
row one-norm is 26. The maximum data-only row one-norm is 14.

Let c_ij be a scalar prefix coefficient. Let r_i be the current frame
rank and s_j the input frame rank. Up to Gaussian monomial endpoint
views, its physical operator is

    c_ij H_i H_j*.

All endpoint monomials preserve the coefficient grid and its maximum
real-component norm. Write the dyadic denominator of c_ij as `2^d`.
The exact non-dominated pairs `(d,r_i+s_j)` are

    (0,10), (2,8).

This statement is only about the denominator bound. It does not claim
that frames with shared listed basis vectors cancel as operators.

To prove the physical bound, set `a=(1+i)/2`. Every nonzero rank-n
native coefficient belongs to `a^n Z[i]`, including its monomial
conjugates and adjoints. Products of such coefficient sets lie in
`a^(n+m) Z[i]`, and sums stay in that set. Thus the operator term
above has dyadic grid denominator at most

    2^(d+ceil((r_i+s_j)f/2)).

Assume every real and imaginary coefficient of all 704 finite inputs
lies in `2^-b Z`. Then every untagged physical cut value lies in

    Delta Z[i],
    Delta=2^(-b-beta(f)), beta(f)=max(5f,4f+2).            (1)

This is a sufficient common grid. No claim of minimal denominator
is made. At f=1, an actual centre coefficient has magnitude 1/64
from a grid-one Y input. Thus replacing beta(1)=6 by 5 fails.

Each native product has at most `2^((r_i+s_j)f)` paths per row.
Each path has coefficient real-component one-norm
`2^(-floor((r_i+s_j)f/2))`. The triangle inequality gives physical
row norm at most `2^(ceil((r_i+s_j)f/2))`. Consequently the complete
untagged cut map has norm at most `26*2^(5f)` in the maximum of the
absolute real and imaginary coefficients.

For data input columns only, the maximum frame-rank sum is eight.
Hence replacing both input data banks by `(1+delta)` times their
values adds at most

    14*2^(4f)*delta*M                                      (2)

to every physical cut field, where M bounds the original data
coefficients. This bound applies to all 704 fields, not only centres.
It does not assume that helper inputs have frame zero.

If the actual physical error at each field is at most eta, equations
(1) and (2) give the sufficient whole-cut coarse-snap margin

    14*2^(4f)*delta*M + eta < Delta/2.                    (3)

The result of each snap is then its exact untagged prefix value.
For a centre alone, the sharper coarse grid of `H_k(u_k+R_kY/4)` is
`2^(-b-4f-2) Z[i]`. The helper-only component `H_k u_k` lies in
`2^(-b-4f) Z[i]`.

## Remaining obligations

This note supplies actual phase checks and sufficient physical grid
and norm bounds. It does not choose a recursive accuracy or assert
that an approximate caller has the required finite input grid. It
does not implement the separate tagged-input reset word or price its
storage, scans, arithmetic, rounding, and recursive children.

The centre-only exact recovery lemma from the earlier review remains
valid when its plain-product justification is replaced by this actual
canonical-frame proof. Its margin is

    14*2^(4f)*delta*M + eta < 2^(-b-4f-1).

The earlier all-extra-reset mass 1,040 still applies only to its
literal delta-scaled reset policy. Its nonmonotonicity qualification
also remains unchanged. Neither statement is a bound on the separate
tagged word.

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/paired-package-review/centre-reset-review/check_physical_grid_v2.py
```

The command passed with status
`PASS_ACTUAL_CANONICAL_PHASES_AND_WHOLE_CUT_GRID`. All source files and
the first review were preserved. The actual native recipe and canonical
phase construction are credited to the pinned source authors. OpenAI
Codex assisted this independent check under the user's direction.
No PR, commit, or push was made.
