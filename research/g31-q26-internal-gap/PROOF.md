# One internal thin gap does not meet total rank 130

This is a proof in characteristic two under the schedule hypothesis below.
It is not a search over words, not a census of projectors, and not a
heuristic. It does not say that the profile `g=31`, `q=26` is impossible
for every placement of the full calls.

No new kappa is claimed. The selected frontier stays
`781451/250000000 = 0.003125804`.

## 1. Schedule

Use the paired-star contract in `research/coupled31-chronology/PROOF.md`.
The core and each of the `g` leaves have dimension `d`. Stage `j` has two
complementary projectors on the core and leaf `j`. In those blocks

```text
P  = [[A+B, B], [B, A+B]],   R  = [[A, A], [A, A]],
P' = [[A'+B, B], [B, A'+B]], R' = [[A', A'], [A', A']],
```

with `A^2 = A`, `A' = I+A`, and `AB+BA = B`. A full call is
`(I+x P)(I+e R)` with `x = D+1` and `e^2 = 0`. A thin call is `I+e Z` for
a constant matrix `Z`. The variables `D_j` are independent. The target is
`(I+e I)` times `product_j (I+x_j E_j)`. The first-applied factor is the
rightmost factor. Matrix rows are outputs and columns are inputs.

This note uses two equal halves, so `d = 2q` and each half idempotent has
rank `q`. The block whose rank is counted is the core row and leaf column:
the block that sends leaf `j` into the core. That is the block called
core-to-leaf in open PR #7005.

**Hypothesis.** The two full calls of every stage occupy adjacent positions.
Thin maps may sit in the gaps before, between, and after those `g` stage
blocks. In addition, at most one stage has thin maps in the single gap
between its own two halves. No full call of another stage sits in that gap.
Call this one internal gap. Nested intervals, crossed intervals, and an
interleaved word are outside the hypothesis.

## 2. Eigenbasis, with the off-diagonal blocks free

Let `A` act on the `d`-dimensional coordinate space of the core and of every
leaf. Its minimal polynomial divides `y(y+1)`, and `y(y+1)` has distinct
roots in characteristic two, so `A` is diagonalizable over the base field.
In an eigenbasis, `A = diag(I_q, 0)`. Write a general block matrix in that
splitting as `B = [[H, B12], [B21, K]]`. Then

```text
AB+BA = [[0, B12], [B21, 0]],
AB+BA+B = [[H, 0], [0, K]].
```

The relation `AB+BA = B` holds if and only if `H = 0` and `K = 0`. The
off-diagonal blocks `B12` and `B21` remain arbitrary `q` by `q` matrices.
From here on, `B` has that form. The same basis splits every leaf.

In these coordinates the two halves are complementary projectors `P_+` and
`P_-` on the stage support, `P_+ + P_-` is the identity there, and
`P_+ P_- = 0`. Both orders multiply to the scalar stage factor: if `P_f` is
applied first and `P_s` second, then

```text
(I+x P_s)(I+x P_f) = I+x E,
```

where `E` is the identity on the core and on this leaf and zero on every
other leaf. Thus `I+x E = F + D E`, with `F = I+E` the identity on the
other leaves. This is the same pure factor as a completed adjacent pair.
The full-call bracket

```text
(I+x P_s) R_f + R_s (I+x P_f)
```

equals the constant matrix `T` of all four identity blocks, for either
order, with `B12` and `B21` free. The `e` coefficient of the two halves
with nothing between them is therefore `D T`, as in the consecutive
schedule. A nonzero diagonal block of `B` makes the pure product fail.
That control is part of the registered replay.

## 3. The core-to-leaf coefficient of the internal gap

Let `Z` be the sum of the thin maps in the internal gap of stage `t`.
Several maps in that one gap add, because the pure factor between them is
`I` and `e^2 = 0`. Write `P_f` and `P_s` for the first and second halves.
On the whole space

```text
U = I+x P_f = F + P_s + D_t P_f,
V = I+x P_s = F + P_f + D_t P_s.
```

The terms linear in `Z` are `V Z U`. Expanding gives

```text
VZU = B0 + D_t B1 + D_t^2 B2,
B2 = P_s Z P_f,
B1 = (F+P_f) Z P_f + P_s Z (F+P_s),
B0 = (F+P_f) Z (F+P_s).
```

Stages before `t` and after `t` contribute the same diagonal pure factors
as in the consecutive schedule, because the two halves still multiply to
`I+x E`. On the block that sends leaf `j` into the core, those outside
factors contribute the scalar monomial

```text
lambda(t,j) = (product_{k>t} D_k) * (D_j if j<t else 1).
```

`lambda` does not contain `D_t`.

For a leaf `j` other than `t`, the input lies in the complement of the
stage, so `U` acts as the identity there and `P_f`, `P_s` vanish on it.
Reading the core rows leaves

```text
pi_core VZU pi_j = pi_core P_f Z pi_j + D_t pi_core P_s Z pi_j.
```

There is no `D_t^2` term on that block. For the plus half applied first,
`P_f = P_+` and `P_s = P_-`, and the two compressions on a vector `z` are

```text
P_+:  c+ = z_c+ + B12 z_c- + B12 z_s-,    c- = B21 z_c+ + B21 z_s+,
P_-:  c+ = B12 z_c- + B12 z_s-,           c- = B21 z_c+ + z_c- + B21 z_s+.
```

Here `z` is the stage-support part of `Z` applied to the leaf-`j` input,
split into the `+` and `-` eigencomponents of the core and of leaf `t`.
The opposite order exchanges `P_+` and `P_-`.

For leaf `t` itself the input lies in the stage support, where `F = 0`, so

```text
pi_core VZU pi_t
  = pi_core (P_f + D_t P_s) Z (P_s + D_t P_f) pi_t.
```

That block is quadratic in `D_t`. Its `D_t^2` coefficient is the core-leaf
block of `P_s Z P_f`. The target's `e` coefficient is the pure product,
which is square-free, so a successful word needs `P_s Z P_f = 0`. The rank
bound below does not use that vanishing: a nonzero square already misses
the endpoint, and imposing it only constrains `Z` further.

The registered checker compares `VZU` with this closed form on the six
coordinates `(c+, c-, s+, s-, o+, o-)`, with `B12`, `B21`, and every block
of `Z` kept as noncommuting letters. It then compares a direct `g=3`,
`q=1` word, with `B12 = B21 = 1`, against the same core blocks at every
stage and both half orders.

## 4. Which required monomials the gap meets

With every stage completed adjacently, the full calls contribute exactly

```text
M_j = product_{k>=j} D_k
```

times `I_d` on the core row and leaf-`j` column. An external thin map in
the gap after `gamma` completed stages is multiplied by

```text
mu(gamma,j) = (product_{k>=gamma} D_k) * (D_j if j<gamma else 1).
```

Comparing exponents, `mu(gamma,j) = M_j` if and only if `gamma` is `j` or
`j+1`. The internal gap does not change these external monomials. Its own
contribution on leaf `j` is `lambda(t,j)` times a polynomial of degree at
most 2 in `D_t`.

The equality `lambda(t,j) D_t^a = M_j` holds for exactly these pairs, and
for no other leaf, no other power, and neither half order:

- `a = 1` and `j = t`,
- `a = 1` and `j = t-1`, when `t >= 1`,
- `a = 0` and `j = t+1`, when `t+1 <= g-1`.

Power `a = 2` produces a square of `D_t` and never equals the square-free
monomial `M_j`. Thus the internal gap can meet the required monomial of at
most the three leaves `{t-1, t, t+1}`. Every other leaf keeps the external
equation of the consecutive schedule: the core blocks in gaps `j` and
`j+1` sum to `I_d`.

The checker compares these exponent vectors for every stage, every leaf,
and every power at `g=31`, and again at `g=4`. That domain is finite and
the enumeration is complete. It is a check of this case split, not a census
of matrices.

## 5. Rank

Let `r_gamma` be the sum of the ranks of the external thin maps in gap
`gamma`, and let `r_int` be the sum of the ranks of the maps in the
internal gap. A block has rank at most the rank of its matrix, and rank is
subadditive, so each external block in gap `gamma` has rank at most
`r_gamma`. On every leaf `j` that the internal gap does not meet,

```text
r_j + r_{j+1} >= rank(I_d) = 2q.
```

There are at least `g-3` such leaves: an endpoint stage meets two, and an
interior stage meets three. Sum the inequalities. Each external gap occurs
in at most two of them, so the left side is at most `2 R_ext`, where
`R_ext` is the sum of the external ranks. Therefore

```text
R_ext >= q (g-3).
```

The internal rank is nonnegative, and the total thin rank is
`R_ext + r_int`. Every word in this schedule satisfies

```text
total thin rank >= q (g-3).
```

The same counting at every one of the `g` placements is part of the
registered replay. If the internal slot is empty, open PR #7005 gives the
stronger bound `q g`. This note does not replace that theorem. Dropping
the leaves that an internal gap might meet is what produces `g-3` rather
than `g`.

## 6. The profile

For `g=31` and `q=26`, the bound is `26 * 28 = 728`. Five thin maps of
rank 26 have total rank `130`. Since `130 < 728`, no word in this schedule
meets the endpoint at total thin rank 130. The projectors need not
commute, and `B12`, `B21` may be nonzero.

The bound 728 is not claimed to be sharp. The three leaves the gap might
meet can still cost rank, and no word of total rank 728 is constructed.
The older chronological floor `5q >= 4q+20` still passes at `q=26`. The
obstruction here is this one schedule, not that floor.

## 7. What this does not prove

- It does not prove that every `g=31`, `q=26` word needs total thin rank
  728. A second internal gap, one gap in every stage, a nested interval,
  or a crossed interval is a different schedule.
- It does not prove the consecutive bound `q g` of open PR #7005. That
  argument excludes the internal slot. The bound proved here is the weaker
  number `q(g-3)`, which already separates 130 from this schedule.
- It does not prove the map-count theorem of open PR #7010. That theorem
  requires the internal slot to be empty and concludes `ceil(g/2)` maps of
  unrestricted rank. Five maps remain possible, on other schedules, as
  far as this note goes.
- The `g=3` word in the checker is a conjugation control at `q=1`. It is
  not a census at `q=26` and it does not prove the rank bound. The bound
  is the symbolic coefficient identity together with the exponent count.
- No witness for `g=31`, `q=26` is constructed. Absence of a search is
  not nonexistence on a larger schedule.
- Native transport, frames, and the selected frontier are untouched.

## 8. Credit

The paired-star contract, the chronological rank floor, and the commuting
map-count are from PR #5747 (Ali Romman), with the predecessor statements
in PR #5673, PR #5631, and PR #5617. Cinna Davis supplied the
controller/simplex lineage those packages retain. Open PR #7005 proved the
consecutive bound `q g` and asked for the coefficient of one internal gap.
Open PR #7010 proved the adjacent-halves map count and left a call between
the halves open. This note answers the rank question for one thin gap, not
the interleaved schedule named there.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
