# Integer-shift cubic repair at odd S, and twenty general-frame arities

Prepared by ahrazzle with substantial AI assistance. Apache-2.0. The reader,
defect and rational comparison are Nick Petalas's (PR6200). The node lemma,
the integer-shift alphabet and the substitution `v_j = 6c_j - (2r-1)` are
from Nick Petalas's PR6653. The dyadic lower bound of three queries and the
general-frame contract are apoursh's (PR6212). No new kappa is claimed.

## Setting

Retain all `r >= 3` children `y += a^3; a += b`, starting from arbitrary
incoming `(Y, A, B)`. The eager endpoint is `(Y + r A^3, A, B)`. The deferred
endpoint is `(Y + sum_{i<r} (A+iB)^3, A + rB, B)`. A repair appends
input-independent events that reach the eager endpoint exactly for every
input. Write

```
S = r(r-1)/2,   n = 2r-1,   M = 2r^2 - 2r - 1 = 4S - 1,   K = 3M,
D_r = sum_{i<r} (A+iB)^3 - r A^3 = 3S A^2 B + S n A B^2 + S^2 B^3.
```

Two event alphabets are used.

- **Integer shift (`I`).** `a += k*b` with `k` in Z, and `y += q*a^3` with `q`
  in Z[1/2]. This is the alphabet of every PR6653 certificate. `b` is never
  written or queried.
- **General frame (`G`).** Determinant-one shears `a += k*b`, `b += k*a` with
  `k` in Z[1/2], and `y += q*a^3`, `y += q*b^3` with `q` in Z[1/2]. This is the
  PR6212/PR7475 contract. The programs below use integer `k` only.

`I` is a strict sub-alphabet of `G`. In particular it excludes PR6212's
`b^3` query and PR6215's original-b family.

## Lemma 0: programs in `I` are node identities

In `I`, `b = B` throughout. Every shear adds an integer multiple of `B` to
`a`, so `a = A + cB` with `c` in Z at every query. A program with queries
`y += w_j a^3` at shifts `c_j` ends with

```
y = Y + sum_{i<r} (A+iB)^3 + sum_j w_j (A + c_j B)^3.
```

It repairs exactly when the final shift is zero and
`D_r = sum_j (-w_j)(A + c_j B)^3` as polynomials. A polynomial identity is
required because the equality must hold for every input. Conversely, such an
identity with integer `c_j` and dyadic weights gives the PR6653 schedule:
shift to each node, query, then shift back to `c = 0`.

Merge equal nodes and drop zero weights. PR6212 proves that over Z[1/2]
two queries suffice only for `r = 2`. One query never suffices, because a
single cube with zero `A^3` coefficient has zero `A^2 B` coefficient. Hence
for `r >= 3`, a repair with at most three queries in `I` is the same thing
as three **distinct** integer nodes with **nonzero** dyadic weights. The
verifier also checks the two-node case directly for `r <= 200`: two distinct
integer nodes need `(c - c')^2 = M/3` and weight `S/(c - c')`, and no odd-S
arity in range passes.

## Lemma 1 (PR6653 node lemma)

For distinct rationals `c_0, c_1, c_2`, rational weights with
`D_r = sum_j q_j (A + c_j B)^3` exist if and only if

```
3 e2(c) = n e1(c) - 3S.
```

The weights are then unique:
`q_j = S (n - 3(c_k + c_l)) / (3 (c_j - c_k)(c_j - c_l))`, where `{j,k,l} = {0,1,2}`.
The proof is in the pinned PR6653 README. `verify.py` independently
recomputes the weights by Gaussian elimination.

## Lemma 2: shifted coordinates

Put `w_j = 6 c_j - n`, as PR6653's first open question suggests. Then

```
node equation  <=>  e2(w) = -K,
q_j = -6S (w_k + w_l) / ((w_j - w_k)(w_j - w_l)).
```

*Proof.* `36 e2(c) = e2(w) + 2n e1(w) + 3n^2` and `6 e1(c) = e1(w) + 3n`.
Substituting into `36 e2(c) = 12 n e1(c) - 36 S` gives
`e2(w) = 3n^2 - 36S = -3(2r^2 - 2r - 1)`.

For the weights, `n - 3(c_k + c_l) = -(w_k + w_l)/2`, and
`3(c_j - c_k)(c_j - c_l) = (w_j - w_k)(w_j - w_l)/12`. ∎

## Lemma 3: a parity obstruction

Let `S` be odd, and let integers `c_j` satisfy the node equation. Then the
`c_j` are not all congruent modulo 2.

*Proof.* Each `w_j = 6c_j - n` is odd. If all `c_j` had one parity, then
all `6c_j` would agree mod 4, so `w_j = e + 4t_j` with a common odd `e`.
Then `w_j w_k = e^2 + 4e(t_j + t_k) + 16 t_j t_k ≡ 1 + 4(t_j + t_k) (mod 8)`.
Summing the three pairs gives `e2(w) ≡ 3 + 8(t_0 + t_1 + t_2) ≡ 3 (mod 8)`.
On the other hand, `-K = 3 - 12S ≡ 7 (mod 8)` when `S` is odd. ∎

So exactly one node, call it `c_0`, has the other parity. The gaps
`x = c_1 - c_0` and `y = c_2 - c_0` are odd, and `y - x` is even.

## Lemma 4: one weight is a nonzero integer

In that labelling, `w_1 = w_0 + 6x` and `w_2 = w_0 + 6y`, so Lemma 2 gives

```
q_0 = -S (w_0 + 3x + 3y) / (3xy).
```

The denominator `3xy` is odd. A dyadic `q_0` is therefore an integer, and
`q_0 != 0` by Lemma 0. ∎

## Lemma 5: a bound and finite fibres

The node equation becomes `3w_0^2 + 12(x+y) w_0 + 36xy = -3M`, that is

```
(E)   w_0^2 + 4(x+y) w_0 + 12xy + M = 0
      <=>  (w_0 + 3x)(w_0 + x + 4y) = 3x^2 - M.
```

**Bound.** Put `s = w_0 + 2(x+y)`. Then (E) gives
`s^2 = 4(x^2 - xy + y^2) - M < 4(|x| + |y|)^2`, because `M > 0`. Hence
`|w_0 + 3(x+y)| = |s + x + y| < 3(|x| + |y|)`. Lemma 4 gives
`3|x||y| <= S |w_0 + 3(x+y)|`, so `|x||y| < S(|x| + |y|)`. With
`m = min(|x|, |y|)` and `L = max(|x|, |y|)`, this says `mL < S(m+L) <= 2SL`.
Therefore `m < 2S`.

**Fibres.** Swap the names of `c_1` and `c_2` if needed, so that `|x| = m`.
Then `x` is odd and `0 < |x| < 2S`. Let `N = 3x^2 - M`.

- If `N != 0`, then `d = w_0 + 3x` is a nonzero divisor of `N`. It
  determines `w_0 = d - 3x` and `4y = N/d - d + 2x`. Both `d` and
  `N/d = w_0 + x + 4y` are even, since `w_0` and `x` are odd.
- If `N = 0`, then either `w_0 = -3x` or `w_0 = -x - 4y`.
  - In the first case `q_0 = -S/x`, which needs `x | S`. For `r <= 200` this
    case occurs only at `r = 14` (`x = ±11`, `S = 91`) and at `r = 134`
    (`x = ±109`, `S = 8911`). In neither case does `x` divide `S`, and the
    verifier fails if it ever would.
  - In the second case `q_0 = -S(2x - y)/(3xy)`, and integrality forces
    `y | Sx`.

Every case is finite, so for odd `S` the integer-shift three-query question
is decided by a finite computation. ∎

**Remark (the independent route).** Lemma 2 also gives
`q_2 = -S(w_0 + 3x)/(3y(y - x))`. Since `y` is odd, a dyadic `q_2` needs
`y | S(w_0 + 3x)`. When `N != 0`, `w_0 + 3x` divides `N`, so `y` divides the odd
part of `S N`. `independent_check.py` therefore enumerates the larger gap
`y` instead, and solves (E) for `w_0`. When `N = 0`, a zero `w_0 + 3x` would
make `q_2 = 0`, so the second branch above is the only one. The search's
`d`-route (`verify.py`) and `y`-route (`independent_check.py`) share no code
and agree on every node set.

## Theorem A

For every `r >= 3` with `S` odd, Lemmas 3–5 decide whether three queries
suffice in `I`. Among the 99 arities `3 <= r <= 200` with `S` odd:

1. Exactly 17 admit three queries in `I`:
   `3, 6, 7, 11, 19, 26, 27, 42, 50, 51, 62, 90, 91, 98, 114, 155, 162`.
   These have 34 node sets in total, all listed in `CERTIFICATES.json`.
   Each of the 17 lies in PR6653's table of earlier classes or among its
   certificates, so `I` adds no new odd-S arity.
2. At the other 82, which include `15, 22, 30, 31, 34, 39, 43, 58`, three
   queries are impossible in `I`. A four-query integer-shift certificate is
   recorded for each. The minimum query count in `I` is therefore exactly
   four at these 82 arities.

PR6653's bounded search covered nodes in a window of width 160. Theorem A
shows that its failures at 15, 22, 30 and 31 were not artifacts of that
window: no integer-shift certificate exists at any size. The statement
concerns `I` only:

- 44 of the 82 arities have three-query repairs in `G`. Examples are
  `r ≡ 2 (mod 3)`, through PR6212's `b^3` query, and `r mod 9` in `{0,1}`,
  through PR6215's original-b family.
- The remaining 38 have no known three-query repair in any alphabet.
  Theorem A says that any such repair must leave `I`: it needs a query on
  `b`, a write to `b`, or a non-integer shift.

This is consistent with apoursh's PR7479, which shows that finite odd-modulus
tests cannot give a four-query bound in the unrestricted contract. The
obstruction here uses the 2-adic Lemma 3 together with the size bound of
Lemma 5, and it holds only in the restricted alphabet, which PR7479 leaves open.

## Theorem B: twenty general-frame arities

At each of

```
48, 49, 57, 60, 69, 84, 88, 96, 105, 112, 120, 121, 124, 132, 133, 148,
169, 177, 184, 192
```

`CERTIFICATES.json` records primitive integer rows `(u_j, v_j)`, dyadic weights
with `D_r = sum_j q_j (u_j A + v_j B)^3`, and a literal program in `G`. The
programs use integer determinant-one shears and three queries, retain all
children and restore both arbitrary sources. With PR6212's lower bound, three
is the exact query minimum at these arities.

None of the twenty lies in:

- PR6653's table of earlier classes (`r ≡ 2 mod 3`, `r` in `{3,4}`,
  `r mod 9` in `{0,1}`, `2^s`, `2^s+1`);
- PR6653's 17 certificates;
- PR7475 (`r = 24`);
- PR7478's Pell family (`r^2 - 3m^2 = 1`).

All twenty have even `S`. For the four integer-shift ones, Theorem A
forces this. The certificates fall into three kinds:

- At `124, 169, 177, 184` the rows are monic, so these are integer-shift
  certificates whose nodes lie outside PR6653's search window.
- At `84, 105, 121, 132, 148` two rows are non-monic.
- The remaining eleven use one non-monic row, as PR7475 did at `r = 24`.

The shear counts are explicit upper bounds from a small compiler search in
`build.py`. They are not minimality claims.

## What is not claimed

- No physical price or caller invoice is given.
- No shear-count optimality is claimed.
- No claim is made about the alphabet `G` at the 38 open odd-S arities, or
  at the even-S arities `40, 61, 141, 165, 168, 193, 196`.
- The twenty rows and weights came from an external search that is not part
  of acceptance. Each certificate is accepted only by exact checks.
- Lean or other proof-kernel review is not claimed. The two checkers are
  separate AI-assisted implementations, not independent human review.
