# No sum of letters hosts the frame-0 indicator

No new κ. The selected record stays `781451/250000000`. This note answers the
sum question left open by PR #7031. It does not redo that product census, it
does not host another frame, and it does not name monomials on the selected
invoice.

## 1. Hypotheses

Ports, the odd graph, and the simple-root chart are those of PR #7031. Frame 0
of the #7014 witness is the ordered 8-tuple

```text
11, 21, 38, 56, 140, 146, 161, 191.
```

A **letter** `λ_i` is the root-line functional `j ↦ (<r_i, r_j> + 1) mod 2`.
In the chart every label has ninth coordinate 1, and the accepted identity
`S9(u_i, u_j) = (<r_i, r_j> + 1) mod 2` makes each letter an affine function

```text
λ_i = 1 + (linear form in x0, ..., x7).
```

A **sum of letters** is an `F_2` linear combination of these 120 functions.
Repetitions cancel in pairs, so every sum is the sum of a set of distinct
letters. The sum **hosts** the row when its value is 1 on the eight frame
lines and 0 on the other 112 root lines. Agreement on the 104 P104 lines is
the weaker condition used below; it is already impossible.

The charge of a word is the set of square-free monomials in its algebraic
normal form, in this fixed chart, with `x_i^2 = x_i`. As in #7031, a
**new** monomial is one of degree at least 2. The constant and the eight
variables are not new.

Sums in `Z`, thresholds, and sums of products are outside these hypotheses.

## 2. The explicit sum

**Proposition.** The sum of four frame letters cancels:

```text
λ_11 + λ_21 + λ_38 + λ_56 = 0.
```

The chart polynomials, recomputed from the labels, are

```text
λ_11 = 1 + x1 + x2 + x4 + x5,
λ_21 = 1 + x0 + x1 + x2 + x4 + x5,
λ_38 = 1 + x0 + x1 + x2 + x4,
λ_56 = 1 + x1 + x2 + x4.
```

Each of `1, x0, x1, x2, x4, x5` occurs an even number of times (`4, 2, 4, 4,
4, 2`), and `x3, x6, x7` do not occur. The sum is the zero polynomial. Its
monomial list is empty, so it has **zero** new monomials. On every root line
the value is 0, including the eight frame lines, so the sum does not host
the row.

The same direct count gives thirteen further cancelling fours inside the
frame, and the sum of all eight frame letters is zero as well. No nonempty
subset of the eight of size other than 4 or 8 cancels. Deleting any one
letter from `λ_11 + λ_21 + λ_38 + λ_56` leaves a nonzero affine function.
None of the 255 nonempty subset-sums of the eight frame letters hosts the
row. That 255-count is an exhaustive census of a finite domain. It is not a
census of sums that use a letter from outside the frame.

One single letter has the same new-monomial count and also fails. For
example `λ_11` expands to `1, x1, x2, x4, x5` (zero new monomials). It equals
1 on all eight frame lines and also equals 1 on a line outside the frame.

## 3. Every sum is affine, and none hosts

**Theorem.** Under the hypotheses in §1, every sum of letters has algebraic
normal form of degree at most 1, hence has zero new monomials. No such sum
agrees with the frame-0 indicator on the 104 P104 lines. In particular, no
sum hosts the #7031 row on all 120 root lines, and no sum hosts that row
with fewer than 40 new monomials.

The degree bound is the sum of affine functions. It does not use a search.
The zero new-monomial count is the same degree cut #7031 uses for the
product charge. Every sum would be strictly below 40 on that cut. The
obstruction is that none of them hosts.

**Four-line parity.** Let `v(j) ∈ F_2^9` be the eight chart coordinates of
root line `j`, followed by a constant coordinate 1. For an affine function
`f(x) = c + Σ a_i x_i`, the sum of `f` over a set of lines equals the
`F_2` dot product of `(a, c)` with the sum of their vectors `v(j)`. The four
P104 ports `478, 11, 14, 475` have chart coordinates

```text
478: (0, 0, 1, 1, 0, 0, 0, 0),
11:  (0, 1, 0, 1, 1, 0, 0, 0),
14:  (1, 1, 1, 1, 0, 1, 0, 1),
475: (1, 0, 0, 1, 1, 1, 0, 1).
```

Each coordinate appears an even number of times, and the four constant
coordinates sum to 0. Therefore `v(478) + v(11) + v(14) + v(475) = 0`, and
every affine function has value-sum 0 on these four lines. Any three of the
four vectors already sum to something nonzero, so the dependence has size
exactly 4.

Port 11 is in the frame. Ports 478, 14 and 475 are in P104 and are not in
the frame. The indicator therefore takes values `0, 1, 0, 0` and has
value-sum 1. No affine function can match it on these four lines, hence
none matches it on all 104 P104 lines, hence none matches it on all 120
root lines.

A second four, also inside P104, gives the same contradiction. Ports
`21, 13, 493, 501` have coordinates

```text
21:  (0, 0, 1, 1, 1, 0, 0, 0),
13:  (0, 1, 0, 1, 1, 1, 0, 0),
493: (0, 1, 1, 1, 1, 0, 0, 0),
501: (0, 0, 0, 1, 1, 1, 0, 0),
```

which sum to 0, while the indicator is 1 only at port 21.

The cancelling frame sum of §2 is a dependence of the other kind. The
evaluation labels of ports `11, 21, 38, 56` also sum to 0, but all four
ports are in the frame, so the indicator sum is 0 as well. That relation
does not separate the indicator from the affine functions. Clearing the
frame membership of port 11 in the first four would likewise make the
indicator sum even, and that altered row would not be obstructed by this
particular four.

## 4. Finite censuses

These domains are finite, every element is visited, and the counts are
checked by `verify.py`. They are not samples.

1. **Chart identity.** All `120 × 120` pairings match
   `(<r_i, r_j> + 1) mod 2`. Every letter has constant term 1, and the 120
   letter vectors in `F_2^9` are distinct and have rank 9. Subset sums of
   the letters are therefore exactly the 512 affine functions. The census
   of affine functions is the census of sums.

2. **Distances.** Evaluated on the 120 root lines, the 512 affine functions
   have Hamming distances

   ```text
   8, 48, 56, 64, 72, 112
   with multiplicities
   1,  7, 248, 248, 7,  1.
   ```

   The unique function at distance 8 is the zero polynomial, which is the
   explicit sum of §2. It matches the 112 non-frame lines and misses the
   eight frame lines. Every other sum misses at least 48 lines. On the 104
   P104 lines the distances are

   ```text
   8, 36, 44, 48, 52, 56, 60, 68, 96
   with multiplicities
   1,  3, 12, 199, 82, 199, 12, 3,  1.
   ```

   Again the minimum is 8 and is achieved only by zero. No affine function
   hosts on either domain.

3. **Short obstructions.** No subset of 1, 2, or 3 of the 120 root lines has
   augmented-label sum 0. Exactly 7168 subsets of size 4 have augmented-label
   sum 0 and indicator sum 1. Each of those 7168 meets the frame in exactly
   one line. Exactly 4384 of them lie entirely in the 104 P104 lines. The
   two fours of §3 are in that list. This is why a one-line, two-line, or
   three-line witness cannot exist, and why size 4 is the minimum.

4. **Short syzygies.** No set of 1, 2, or 3 distinct letters sums to the
   zero function. Exactly 32130 sets of four letters do. The explicit sum
   of §2 is one of them. The zero function is therefore achieved by a
   nonempty sum, not only by the empty combination.

5. **Frame-letter sums.** Of the 255 nonempty subset-sums of the eight
   frame letters, 15 are the zero polynomial (14 fours and the full eight)
   and none hosts the row.

## 5. What this does not say

The product in #7031 is not a sum. Its 40 new monomials remain a
product-hosting charge. This note does not prove that 40 is minimal for
sums of products, for a different chart, or for a circuit that is not an
`F_2` sum of letters. It does not prove that the indicator is non-affine
as a function on all of `F_2^8`; the obstruction is only on root lines. A
failed search outside this alphabet would not be a minimality proof. No
selected-invoice histogram is computed, and κ is unchanged.
