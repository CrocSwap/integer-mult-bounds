# A sharp coefficient bound for the reserved-depth balanced word

This sharpens the free-algebra lemma in Chafik Boukhalfa's PR905, using
the unchanged PR628 dispatcher. It does not change a rounded leaf,
borrowed-array allocation, or multiplication exponent.

## Statement

Let `A_0,...,A_(n-1)` be formal noncommuting operators, `n >= 1`.
Use the balanced split `floor(n/2), ceil(n/2)`, distinct source and target,
and one distinct dirty register per recursion depth. A positive node executes
`U,V,U^-1,V^-1` chronologically, where `U: z += B x`, `V: y += A z`,
and `B,A` are the ordered left and right products. Negative calls reverse
the complete instruction word. Every prefix ends at a complete ideal leaf
`target += sign A_j source`.

Put `h = ceil(log2 n)`. Every entry of every prefix matrix and its inverse,
for either call direction, is zero or one signed monomial. Each nonempty
monomial has strictly decreasing factor indices. Therefore the coefficient
absolute row sum is at most **`h+2`**, replacing PR905's `2*3^h`.
The uniform constant is sharp, even for scalar identity factors.

The source row and target column are identity. For a call of sign `s` and
full ordered product `T`, its target/source entry is either zero or `s T`;
the corresponding entry of an inverse prefix is zero or `-s T`.
These additional assertions are part of the induction.

## Induction, including the cancellations

The leaf case is immediate: its two prefixes are identity and one elementary
shear. Suppose all assertions hold for both children. A parent prefix is
`P = R C`, where `C` comprises completed children and `R` is a prefix of
the active child; hence `P^-1 = C^-1 R^-1`. Completed children restore
every deeper register. Write `T = A B`. Their outer states are:

| Parent sign | Completed children | z after C | y after C | Active child |
|---|---:|---|---|---|
| + | 0 | z | y | left + |
| + | 1 | z+Bx | y | right + |
| + | 2 | z+Bx | y+Az+Tx | left - |
| + | 3 | z | y+Az+Tx | right - |
| - | 0 | z | y | right + |
| - | 1 | z | y+Az | left + |
| - | 2 | z+Bx | y+Az | right - |
| - | 3 | z+Bx | y-Tx | left - |

Let the active child's sign be `t` and full product be `F`. By induction,
`R[target,source] = t e F` and `R^-1[target,source] = -t f F`, for
`e,f` in `{0,1}`. No relation between `e` and `f` is needed. Multiplication
gives the following parent endpoint coefficients, in units of `T`:

| Parent sign | Completed children | P[y,x]/T | P^-1[y,x]/T |
|---|---:|---:|---:|
| + | 0 | 0 | 0 |
| + | 1 | e | 0 |
| + | 2 | 1 | -f |
| + | 3 | 1 | -1 |
| - | 0 | 0 | 0 |
| - | 1 | 0 | f |
| - | 2 | -e | 1 |
| - | 3 | -1 | 1 |

Here is why no other entry hides a sum of distinct monomials. In a left
child, the source row `x` and target column `z` are identity. Right
multiplication by `C` can therefore add `Bx` only to row `z`; an existing
entry there is zero or `-B` in precisely the phases that add `B`.
The separate row `y` is fixed by the child. In `C^-1 R^-1`, a new parent
row `y` may contain `A` times the child's row `z`. Each of its entries is
one monomial; the only possible overlap with the other outer entries is
the endpoint governed by `f`. The remaining changed row `z` has the same
endpoint cancellation.

For a right child, `x` is outside the child, its source row `z` is identity,
and its target column `y` is identity. Substitution of `z+Bx` in `R C`
adds a new column `x` by appending `B` to each occupied column-`z` entry.
This column was absent inside the child. Only row `y` can also receive
an outer contribution; the table and `e` control that collision. In
`C^-1 R^-1`, the identity source row leaves only the target/source
cancellation governed by `f`, and additions in the external column `x`.
All collisions thus give zero or a signed coefficient one, never two
different surviving monomials in one entry. Every new product prepends
the complete right product to a left monomial, or appends the complete
left product to a right monomial. The index sets are disjoint and ordered.

The source row and target column remain identity because no instruction
writes the source or reads the target. The final boundary is the product
shear and satisfies the same assertions. This closes the induction for
both directions and inverse prefixes. The abstract eight-case checker
is supporting exact algebra, not the basis for extrapolation to all n.

## Row bound and sharpness

There are `h+2` registers: source, target, and `h` reserved dirty registers.
The entry invariant proves the row bound. To attain it, set every factor
to the scalar identity. Follow the first positive execution down the
rightmost branch. At each level the completed left child adds the current
source to the next connector. The first execution of the last factor then
adds all `h` original connector values and the original source to the
original target. Its row has exactly `h+2` positive coefficients. The
rightmost branch has height `h` because it repeatedly takes `ceil(n/2)`.
The receipt retains an explicit 74-factor, nine-term witness.

If every ordered subset product of actual operators has norm at most
`G >= 1`, including the empty product, substitution gives

```
||P||, ||P^-1|| <= B = (h+2) G,
||P_j P_i^-1|| <= B^2.
```

No commutation is required for this implication. Obtaining the particular
small `G` used for cyclic inverses still requires PR905/PR862's common
immutable isometry and preparation hypotheses. The theorem concerns leaf
boundaries; internal leaf growth retains its separate inherited bound.

## Consequence for the existing sufficient precision formula

Keep PR905's definitions `a0, ell, Aerr, g, N, m, p` and all preparation
budgets. Its subset bound is `G <= 2^(a0+2r+ell)`. Replace only

```
J_old = a0+2r+ell+1+2h
J_new = a0+2r+ell+ceil(log2(h+2)).
w_new = max(w_input, Aerr, 2g+1,
            p+3+ceil(log2 N)+Aerr+m+3J_new).
```

PR877/905's unchanged perturbation estimate is
`2 N B^2 a u (B D+1)`, provided `N B^2 a u <= 1/2`.
Here `B <= 2^J_new`, `a <= 2^Aerr`, `D <= 2^m`, and `u=2^-w_new`.
Since `B D+1 <= 2^(J_new+m+1)`, the displayed choice bounds execution
error by `2^(-p-1)` and ensures the feedback condition. The unchanged
coefficient perturbation allowance completes the inherited `2^-p`
budget. Initial finer grids and stable closure remain explicitly charged.

At radix 64, `p=128`, `m=20`, and `w_input=0`, the source formula falls
from **1,162,553 to 1,162,523 fractional bits**. This is a sufficient-bound
comparison, not a measurement or an optimal-precision claim. Exact paid
leaf calls, logarithmic dirty storage, scalar/preparation/phase costs,
routing, and asymptotic cubic precision remain unchanged. No new rounded
kernel execution, compiler, physical hosting, transform, or multiplication
reduction is supplied.

Proof and audit by Hanson Sun, with substantial OpenAI Codex assistance.
Apache-2.0. Predecessor credit and exact pins are in README.md and SOURCES.json.
