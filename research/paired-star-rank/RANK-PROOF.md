# Uniform rank of global proper stars and the empty-star boundary

This note proves the dimension of the scalar global proper-star code and its
sharp algebraic all-target puncture threshold. It distinguishes the stipulated
nonempty-star code from the stronger code obtained by granting the empty star.
At `(p,k)=(8,4)` their dimensions are **447 and 448**, respectively; the minimum
numbers of deletions for simultaneous scalar decoding are **673 and 672**.
There is no circuit, paid supplier, or new kappa claim.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The experiment's track, seed
46, domain and stopping rule are recorded in [CLAIM.json](CLAIM.json).

## 1. Definitions and statement

Let `p >= k >= 2`. A signed port is `(A,epsilon)`, where `A` is a k-subset
of `[p]` and `epsilon: A -> {0,1}`. There are

```text
N(p,k) = 2^k binom(p,k)
```

ports. A partial signed port `(L,tau)` defines the incidence function
`m_(L,tau)(A,epsilon) = 1[L subset A and epsilon|L = tau]`.
Over F2, let `C+_(p,k)` span all such functions with `0 <= |L| < k`, and let
`C-_(p,k)` span those with `1 <= |L| < k`. Thus `C+ = C- + <1>`.

**Theorem.** Put

```text
rho(p,k) = sum_(j=0)^(k-1) binom(p,j) binom(p-j, min(k-1-j,p-k)),
delta(p,k) = 1 if k is a power of two and p >= 2k-1, and 0 otherwise.
```

Then

```text
dim C+_(p,k) = rho(p,k),
dim C-_(p,k) = rho(p,k) - delta(p,k).
```

For power-of-two k, allowing uniform target-overlap corrections of orders
`1,...,k-1` does not change either code. The exact all-target deletion
thresholds are therefore `N-rho+delta` for nonempty stars and `N-rho` when
the empty star is granted.

In the range `p >= 2k-1`, every minimum in the sum is `k-1-j`. The identity
`binom(p,j) binom(p-j,k-1-j) = binom(p,k-1) binom(k-1,j)` gives the simpler
formula

```text
rho(p,k) = 2^(k-1) binom(p,k-1).                     (0)
```

For power-of-two k in this range, the maximum number of simultaneously
decodable retained ports using nonempty stars is therefore
`2^(k-1) binom(p,k-1) - 1`.

## 2. The unsigned slice lemma, including small characteristic

For an arbitrary field K, let `U(n,q,d)` be the space spanned by the functions
`z_T(Q)=1[T subset Q]`, `|T| <= d`, on all q-subsets Q of `[n]`. Then

```text
dim_K U(n,q,d) = binom(n, min(d,q,n-q)).                 (1)
```

Here is the precise external input. A subset `B={b_1<...<b_i}` is ballot if
`b_l >= 2l` for every l; the empty set is ballot. Let `B_(t,q)` have rows
indexed by ballot subsets of sizes at most t, columns by q-subsets, and
entry `1[B subset Q]`. When `0 <= t <= min(q,n-q)`, this matrix has
`binom(n,t)` rows and a square minor of determinant `+1` or `-1`.
This is Theorem 1 of Ghorbani, Khosrovshahi, Maysoori and Mohammad-Noori,
[*Inclusion Matrices and Chains*, arXiv:0709.3144v1](https://arxiv.org/pdf/0709.3144v1),
printed pp. 8-9; their Remark 4, p. 11, credits Wilson and Bier for the
stacked-degree basis. This integral statement applies over every field.

To spell out why it gives (1), let `W_(t,q)` contain *all* t-subset incidence
rows. Counting the intermediate t-subsets gives the integer identity

```text
B_(t,t) W_(t,q) = D_(t,q) B_(t,q),
D_(t,q)[B,B] = binom(q-|B|,t-|B|).                    (2)
```

The square matrix `B_(t,t)` is unimodular. Hence every row of `W_(t,q)`
lies in the span of `B_(t,q)` over K, even if some entries of D vanish in K.
For `d <= min(q,n-q)`, stacking this conclusion for `t=0,...,d` gives the
upper bound `binom(n,d)`. The rows of `B_(d,q)` themselves occur among these
stacked rows and are independent, giving equality. No binomial coefficient
is divided out. In particular, a rank formula for one fixed-degree
inclusion matrix, which can depend on the characteristic, would not suffice.

For `d >= min(q,n-q)`, every q-subset Q can be isolated either by `z_Q`
(degree q) or by `prod_(i not in Q)(1-z_i)` (degree n-q). The evaluation
space is therefore full and has dimension `binom(n,q)`. This proves (1),
including the saturation cases needed below.

## 3. Separate the sign monomials

On a signed port define

```text
z_i = 1[i in A],
x_i = 1[i in A and epsilon_i=1].
```

The two signed-coordinate indicators are `x_i` and `z_i+x_i`. On each
fixed partial support, this invertible change of variables shows that the
star span is exactly the span of

```text
x_S z_T,   S intersect T = empty,   |S|+|T| <= k-1.    (3)
```

Deleting the empty star deletes just the constant monomial in this generating
description: all the coordinate changes preserve positive total degree.

For a fixed S of size j, the functions in its sector are

```text
1[S subset A] (prod_(i in S) epsilon_i) h(A\S),
h in U(p-j,k-j,k-1-j).
```

Different S sectors form a direct sum. Indeed, on any fixed support A, the
sign monomials `prod_(i in S) epsilon_i`, `S subset A`, are an independent
basis of functions on `{0,1}^A`. A zero linear combination thus has zero
coefficient for every S and every A containing S. Conversely, all
`(k-j)`-subsets of `[p]\S` arise as `A\S`, so this identifies each sector
faithfully with the stated unsigned space. This argument uses ordinary
Boolean monomials, not characteristic-zero Fourier characters.

By (1), the sector dimension is
`binom(p-j,min(k-1-j,p-k))`. There are `binom(p,j)` choices of S. Summing
over `j=0,...,k-1` proves the formula for `dim C+`.

## 4. Exactly when the empty star adds a dimension

Only the `S=empty` sector can produce the constant function, by the direct
sum just proved. The question is therefore whether 1 is in the span of
the *positive-degree* unsigned monomials `z_T`, `1 <= |T| <= k-1`, on the
k-slice of `[p]`.

If `p <= 2k-2`, choose a fixed B of size `p-k+1 <= k-1`. Every k-subset
meets B, so `prod_(i in B)(1-z_i)=0` on the slice. Expanding expresses 1
as a sum of nonempty monomials of permitted degree.

If k is not a power of two, there is a `t` with `1 <= t < k` and
`binom(k,t)` odd. For completeness, in F2[X] the identity
`(1+X)^k = prod_(r: binary digit r of k is 1)(1+X^(2^r))` proves this:
choose the least set bit of k. On the slice,

```text
sum_(|T|=t) z_T = binom(k,t) = 1,
```

so the empty star is again redundant.

It remains to take k a power of two and `p >= 2k-1`. Now the ballot rows
through degree `k-1` are independent by Section 2. In their basis the row
for the empty set is 1. For each `1 <= t < k`, the empty-index diagonal
entry of (2) is `binom(k,t)=0` in F2. Consequently every degree-t row
has zero coordinate in that empty-row direction: multiplication by the
invertible `B_(t,t)` cannot create it. All positive-degree rows lie in
the span of the nonempty ballot rows. They cannot span 1. Adding the empty
star therefore increases the dimension by exactly one. The three cases
prove the formula for `dim C-`.

## 5. From dimension to all-target punctures

For a fixed target T and source port V put `s=|T intersect V|`, with the
intersection taken in signed coordinates. For `1 <= l < k` the sum of
all l-stars contained in T has value `binom(s,l) mod 2`. The matrix of
these values for `s,l=1,...,k-1` is triangular with diagonal 1. At s=0
all values vanish; at s=k they also vanish when k is a power of two.
Thus each permitted correction `1[|T intersect V|=s]`, `1 <= s < k`,
belongs to **C-**, before and after any puncturing. This is the correction
absorption mechanism proved in [Luke Mansoor's PR #732](https://github.com/CrocSwap/integer-mult-bounds/blob/80431a74c31e807581f5c2258c87abe2084caacd/research/global-star-puncture/README.md#absorbing-overlap-corrections-when-k-is-a-power-of-two).

For either code C and surviving port set F, every target can be decoded
exactly when `C|F = F2^F`: its restricted span must contain all unit vectors.
Thus `|F| <= dim C`. A generator matrix of rank `dim C` has that many
independent columns, so an information set F of exactly that size exists
and attains equality. This proves the stated exact algebraic thresholds.
It does not bound the number or cost of operations implementing the decoders.

| (p,k) | Ports | Nonempty-star dimension | With empty star | Minimum deletions, nonempty / with empty |
| --- | ---: | ---: | ---: | ---: |
| (5,4) | 80 | 65 | 65 | 15 / 15 |
| (6,4) | 240 | 155 | 155 | 85 / 85 |
| (7,4) | 560 | 279 | 280 | 281 / 280 |
| (8,4) | 1120 | 447 | 448 | 673 / 672 |

For the selected `(8,4)` case, the four sign-sector contributions are
`56 + 168 + 168 + 56 = 448`. The missing empty-star direction subtracts one.
The `(6,4)` row and its all-target conclusion already appear in
[Alishan Ladhani's PR #747](https://github.com/CrocSwap/integer-mult-bounds/blob/aeaf0899179a14644b412e838ede14db967c765e/research/global-star-punctures/README.md#all-target-corollary);
they are a predecessor crosscheck, not a new result of this note.

## 6. Scope, provenance and verification obligations

The mathematical dependency is the integral ballot-basis theorem pinned above.
The remaining steps are the explicit variable change, the unsigned counting
identity, and linear algebra supplied here. No finite replay replaces that
argument, and no proof-assistant verification is claimed. The package's exact
replay independently checks the finite dimensions and literal information-set
decoders; its command and completed coverage belong in the package README.

The no-empty distinction concerns the full port family. Both codes are then
projected to the surviving family, and all available stars are recomputed on
that family. Coefficients are unrestricted F2 scalars. Source-dependent
overlap coefficients, degree-k stars, nonlinear decoders and other geometries
are outside the decoder theorem. The dimension formula itself does not need
k to be a power of two; the correction-absorption corollary does.

No costs for helper preparation, source access, frames, copies, restoration,
recursive children, or hosting are priced. The thresholds are necessary and
sufficient for scalar identities with unrestricted star use; they do not
establish a profitable complete supplier or discharge the multiplication
framework's compiler, precision, tape, recovery, or analytic assumptions.

Predecessors: Sam Sung's [PR #669](https://github.com/CrocSwap/integer-mult-bounds/pull/669)
at `308f1e6ec3bb0b6ec0584cf7bfe219addc219b1e` posed the global puncture
question, following Joel Pulikkan's #231 and the icekylinx/eumemic paired-cube
lineage. Luke Mansoor's #732 is pinned at
`80431a74c31e807581f5c2258c87abe2084caacd`; its one-target distance theorem
is not used to infer these all-target thresholds. Alishan Ladhani's #747 is
pinned at `aeaf0899179a14644b412e838ede14db967c765e`; its all-target
information-set observation is generalized here. Their implementation code
is not imported. Literature credit is to Ghorbani, Khosrovshahi, Maysoori,
Mohammad-Noori, Wilson and Bier as specified above.

This proof was developed with substantial OpenAI Codex assistance as part of
the seed-46 contribution. New prose and derivations are under the repository's
[Apache-2.0 license](../../LICENSE). Cited literature retains its own rights;
no literature proof or predecessor implementation is vendored here.
