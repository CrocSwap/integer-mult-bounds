# Full local residual transfer for the inverse-coded pair

This enabling proof extends the inverse-only result in
[PR #5322](https://github.com/CrocSwap/integer-mult-bounds/pull/5322).
It allows errors at every stated operation in the local pair. It does not
prove provider accuracy or admit a complete caller. The complete paid
Gaussian profile and kappa are unchanged.

Use the physical operators and order from JoyboyBrian's
[PR #5069](https://github.com/CrocSwap/integer-mult-bounds/pull/5069),
as retained at canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf.
D and Q commute, and C commutes with DQ. In general C does not commute
with D or Q separately. All operators act on 112 independent owners.
Errors use the maximum absolute real or imaginary component.

## The chronological residual identity

Each residual is the returned output minus the exact operator on its actual
computed input. Thus a residual can be nonlinear and depend on all earlier
errors. Define e0 after the entrance inverse, bX and bY after FULL, e1 after
the thin inverse, et after its Q^-1 and destination update, eQ after the exit
Q, eC after the exit C, and eL after the final Q^-1. Exact copies and monomial
wrappers are assumed. A defect in an update can be included in et, at the
same output site. The executed values satisfy these definitions:

```text
y1 = C^-1 y + e0
x2 = D(x-Q C y1) + bX
y2 = D y1 + bY
y3 = y2 + Q^-1(C^-1 x2+e1) + et
outY = Q^-1[C(Q y3+eQ)+eC] + eL.
```

Set S=Q^-1 C Q. Relative to the exact standard-pair outputs
`D(x-Qy)` and `DQ^-1 x`, the errors are exactly

```text
Delta X = -DQ C e0 + bX
Delta Y = Q^-1 bX + S bY + Q^-1 C e1 + S et
          + Q^-1 C eQ + Q^-1 eC + eL.
```

To prove this, substitute x2 in y3. The two terms involving the original y
cancel by `C^-1 DQ C=DQ`; the two terms involving e0 cancel by the same
identity. The exact part left in y3 is `Q^-1 C^-1 D x`. Its perturbation is
`Q^-1 C^-1 bX+bY+Q^-1 e1+et`. Apply the last line of the schedule and collect
terms. This proves the formula on every input and every residual vector.
There is no residual product and no assumption that a rounded map is linear.

## Exact terminal norm

Dillon's [PR #4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933)
gives the actual normalizers `K_i=Z_(z_i) P_(G_i)` and the four-point expansion
in its retained TERMINAL.md. For a nonzero code entry, put M=K_i^-1 K_j.
The source ports are distinct, so `G_i^-1 G_j e` is neither zero nor e.
In one digit column, each row of `Q^-1 M Q` therefore has four entries,
each equal to one of `+1/2,-1/2,+i/2,-i/2`.

At positive fiber width f, the block is its f-fold tensor power. Each row has
4^f entries of magnitude 2^-f, and each entry is real or purely imaginary.
Thus each realified row has absolute sum 2^f. The owner coefficient A_ij is
applied once. Distinct input owners occupy disjoint columns, so there is no
cancellation between their row sums. Every row of A has absolute sum 26.
Consequently

```text
||Q_f^-1 C_f Q_f||_(infinity,real) = 26 * 2^f.
```

This is an exact induced norm for arbitrary residuals. It improves the
product bound `26*2^(2 ceil(f/2))` by a factor two when f is odd.
It does not reduce the paid cost of the terminal operation.

For comparison, let B1=2^ceil(f/2) and B9=2^ceil(9f/2).
The canonical Gaussian row formula gives `||Q^-1||=B1` and `||DQ||=B9`.
A real signed monomial preserves row absolute sums. Each block of Q^-1 C
is a Gaussian followed by a signed monomial, with total owner weight 26.
Hence `||Q^-1 C||=26 B1`; likewise `||DQ C||=26 B9`.

## Budget with the actual inverse kernel

The source finite kernel in [PR #5035](https://github.com/CrocSwap/integer-mult-bounds/pull/5035)
computes `x-M round(M^T x/52)` in integer grid units. Since
`A=I-MM^T/4` and `M^T M=56I`, its residual from A^-1 is `-M delta`,
where each mode rounding error delta has magnitude at most half a grid unit.
Each owner has four mode entries, so its error is at most two grid units.
Also `A M=-13 M`. Exact signed monomial wrappers therefore give `C e=-13 e`
for each of the two inverse residuals, even on perturbed valid inputs.
This is the error-shape premise already isolated by PR #5322.

Let the eight residual bounds be epsilon0, epsilonX, epsilonY, epsilon1,
epsilont, epsilonQ, epsilonC and epsilonL in the order defined above. Then

```text
||Delta X|| <= 13 B9 epsilon0 + epsilonX
||Delta Y|| <= B1 epsilonX + 26*2^f (epsilonY+epsilont)
               + 13 B1 epsilon1 + 26 B1 epsilonQ
               + B1 epsilonC + epsilonL.
```

These unequal allowances let a caller assign accuracy at each actual output
site. A useful common sufficient contract is, for u=2^-P,

```text
epsilon0, epsilon1 <= 2u
all six other residual bounds <= u.
```

Under that contract, X error is at most `(26B9+1)u`, and Y error is at most
`(54B1+52*2^f+1)u`. For f>=1, B1<=2^f and B9>=16*2^f. Thus X is below
27B9 u and Y is at most 107*2^f u, below 7B9 u. It follows that

```text
P = p + ceil(9f/2) + 5  =>  both output errors are strictly below 2^-p.
```

The inverse-only guard now funds the additional returned residuals under
explicit call contracts. It is not a proof that each physical provider meets
those contracts. If the inverse implementation does not preserve the error
subspace, replace the coefficients 13 by 26 in the two displayed bounds.

## Evidence and limits

The checker authenticates all six declared inputs. It checks all code entries,
the mode Gram identity, all 112 normalizers and all 5,824 terminal-block
independence premises. Three actual blocks have all 512 rows and columns
expanded with exact signed coefficients. A diagonal control loses four-point
support. Sixty-three exact rational chronological cases cover seven actual
Walsh fibers at widths 1, 2, 3 and 5, with each residual injected alone and
all injected together. Controls detect a missing FULL-Y residual, a missing
exit-Q residual, and reversed thin order. Twelve actual kernel calls verify
the inverse error subspace and paid scratch return. Five hundred widths check
the integer guard. The written operator, row and inequality proofs cover all
positive widths; the finite checks corroborate them.

The second inverse range must include the perturbed x2. Provider input-domain
gates and their internal precision costs remain necessary. All Gaussian calls,
ordinary arithmetic, movement, workspace, copying and cleanup must retain
paid physical contracts. The error bound does not remove the unshared
boundary-call obstruction or supply a cheaper complete caller. It is a local
analytic result, not a full native, compiler, Lean or selected replay.

## Credit and next question

PR #5069 supplies the exact pair and its charged schedule. PR #4933 supplies
the real signed normalizers, mode code and four-point terminal formula.
PR #5035 supplies the finite rounded kernel. PR #5322 supplies the inverse-only
residual cancellation and error-shape guard. Those predecessors are not new
claims here. New result: all returned residual sites, the exact component
terminal norm and the resulting complete local accuracy contract.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

The next question is whether a changed or shared-boundary caller can meet
these local provider bounds within its complete price and range budget.
Start by binding each epsilon above to a named provider contract. No
independent human or proof-kernel acceptance is claimed.
