# No integral four-odd-c solution meets length-6 support

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, fix two distinct old projectors
`E, F ∈ {A, B, P, Q}`. The length-6 equation is

```
R + S + T + U = 4I - E - F,
```

with each added frame a nonzero symmetric rank-one matrix, repeats of old
projectors allowed. An **integral** label is a coefficient vector
`(a, b, c) ∈ Z^3` for `aA + bB + cP`. Its `c` coordinate is odd or even in
the usual sense. This is the odd-`c` test used for the six-label witness in
PR #7100.

**Theorem.** No six nonzero integral rank-one labels sum to `4I`, meet
target support, and include at least four labels of odd `c`. In particular,
the length-6 equation has no integral solution that meets support and has
at least four odd-`c` labels.

The #7100 witness `A, B, P, Q, 2A, 2B` meets support and the same equation,
with odd-`c` count exactly two. The count four is the next even value above
that witness. This note does not classify the solutions of count two.

Selected κ stays `363005817/100000000000`. Nothing here is a word, a κ
change, or a lowering of the eight-call minimum. The argument is for
integral labels only. A rational label with a non-integral coordinate is not
given an odd-`c` value by the test above, and this note does not treat it.

The identity "sum of the paid addresses = `4I`" and the necessary condition
"each target is a subset sum" are inherited from
`research/bit-two-signed-frame-floor/PROOF.md`, Section 1. They are not
reproved. The call-versus-target inequality is not reproved either. It is
only the reason the odd-`c` count matters: all four targets have odd `c`, so
a word needs at least four detected calls. The new fact is that no integral
support solution reaches that count.

## 1. Setup

Addresses are rational symmetric 2-by-2 matrices. Write

```
A = diag(1,0),  B = diag(0,1),
P = [[1,1],[1,1]]/2,  Q = [[1,-1],[-1,1]]/2.
```

The vector `(a, b, c)` means `aA + bB + cP`. Its determinant numerator is

```
2ab + c(a + b).
```

The matrix is nonzero and rank one exactly when the vector is nonzero and
that numerator is zero. The four targets are

```
A+P = (1,0,1),  A+Q = (2,1,-1),
B+P = (0,1,1),  B+Q = (1,2,-1).
```

Each has trace 2 and determinant numerator 1, so determinant `1/2`. Their
sum is `4I = (4,4,0)`. For each target `H`, the complement `4I-H` has
determinant numerator 17. Thus neither `H` nor `4I-H` is rank one. Every
target has odd `a+b` and odd `c`.

## 2. Carrier sizes

**Lemma 1.** If six nonzero integral rank-one labels sum to `4I`, every
subset summing to a target has size 2 or 3. A size-2 subset is one of the
projector pairs `{A,P}`, `{A,Q}`, `{B,P}`, `{B,Q}`, matching the target.
No two nonzero integral rank-one labels sum to `4I-H`.

The empty sum is 0 and the full sum is `4I`. A singleton has determinant
numerator 0, while a target has numerator 1. A five-element subset sums to
a target only if the omitted label equals `4I-H`, which is not rank one.
A four-element subset sums to a target only if the complementary pair sums
to `4I-H`. Lemma 2, proved in the next section for every integer `b`, says
no such pair exists. The same census shows that the only integral rank-one
splitting of a target is its projector pair.

## 3. The integer pair census

Let the goal be an integral vector `(p, q, r)` with `p+q ≠ 0`, and let
`X = (a, b, c)` and `Y = (p-a, q-b, r-c)` both have determinant numerator
zero. Write

```
f = 2ab + c(a+b),
g = 2(p-a)(q-b) + (r-c)(p+q-a-b),
D = p+q,  U = 2q+r,  V = 2p+r,  K = 2pq + rD.
```

As polynomials, `g - f + (cD - K + Ua + Vb) = 0`. Therefore `f = g = 0`
forces `cD = K - Ua - Vb`. For every goal in this section, `D ≠ 0` and
`U ≠ 0`. Substituting into `D f = 0` produces the quadratic

```
U a^2 + (coefB · b - K) a + b(Vb - K) = 0,
coefB = U + V - 2D.
```

Its discriminant is `Delta(b) = A2 b^2 + A1 b + A0` with `A2 < 0`. Since
`A2` is negative,

```
Delta(b) ≤ -f(|b|),
f(n) = |A2| n^2 - |A1| n - |A0|.
```

Expanding gives `f(n+1) - f(n) = |A2|(2n+1) - |A1|`. For `n ≥ 5` the
difference is at least `11|A2| - |A1|`. The checker recomputes `A2, A1, A0`
from `(p, q, r)` and records `f(5) > 0` and `11|A2| - |A1| > 0` for each
goal below, so `f(n) > 0` for every integer `n ≥ 5`. Hence `Delta(b) < 0`
whenever `|b| ≥ 5`. Every integer solution has `|b| ≤ 4`.

The nine goals and their discriminants are

| goal | `Delta(b)` |
|---|---|
| `A+P` | `-8b^2 + 1` |
| `A+Q` | `-8b^2 + 8b + 1` |
| `B+P` | `-8b^2 + 8b + 1` |
| `B+Q` | `-8b^2 + 16b + 1` |
| `4I-(A+P)` | `-136b^2 + 544b + 289` |
| `4I-(A+Q)` | `-136b^2 + 408b + 289` |
| `4I-(B+P)` | `-136b^2 + 408b + 289` |
| `4I-(B+Q)` | `-136b^2 + 272b + 289` |
| `2I = (2,2,0)` | `-64b^2 + 128b + 64` |

**Lemma 2.** On this finite range the only unordered pairs of nonzero
integral rank-one frames are

```
A+P,  A+Q,  B+P,  B+Q,
2A+2B = 2I,  2P+2Q = 2I.
```

No pair sums to a complement `4I-H`. Both frames in either splitting of
`2I` have even `c`. Some discriminants are squares, including `289 = 17^2`
for several complements; in every such complement case the reconstructed
third coordinate is not an integer. The checker tests both signs of every
square root on `b ∈ {-4,...,4}` and keeps a pair only when both frames are
integral, nonzero, and rank one.

This is an exhaustive census of a finite set of integers `b`. The bound
`|b| ≥ 5` is the completeness argument. It is not a search over directions
outside that range, because the quadratic forbids those `b`.

## 4. Parity types

**Lemma 3.** An integral rank-one frame with odd `c` has even `a+b`.

The numerator `2ab + c(a+b)` is zero, so `c(a+b)` is even. The product of
two odd integers is odd, hence `a+b` is even. The eight residue classes
mod 2 are exactly this implication: the two classes with odd `c` and odd
`a+b` have odd numerator and are not rank one.

Call the surviving classes

```
EO: c odd and a+b even,
OE: c even and a+b odd,
EE: c even and a+b even.
```

There is no integral rank-one frame with odd `c` and odd `a+b`. Negation
preserves both parities, so it preserves type. The projectors sit in these
classes as `A, B` of type OE and `P, Q` of type EO. The doubles `2A` and
`2B` are EE.

**Lemma 4.** A subset summing to a target contains exactly one OE frame.
A size-2 subset is one EO frame plus one OE frame. A size-3 subset is one
EE frame, one EO frame, and one OE frame.

Each target has parity `(a+b, c) ≡ (1, 1) (mod 2)`. Frames of type EO, OE,
and EE contribute `(0,1)`, `(1,0)`, and `(0,0)`. The checker enumerates the
27 ordered triples and the 9 ordered pairs of these three classes. The only
pairs with sum `(1,1)` are EO with OE. The only triples with sum `(1,1)`
are one class of each kind. A size-2 or size-3 subset therefore contains
exactly one OE frame.

## 5. Four or six odd labels

Let the six labels be nonzero, integral, and rank one, with sum `4I`, and
suppose at least four have odd `c`. The sum of the six `c` coordinates is
the `c` coordinate of `4I`, which is 0, so the number of odd-`c` labels is
even. It is 4 or 6.

**Six odd labels.** There is then no even label, hence no OE frame. Lemma 4
says every carrier needs an OE frame. Support fails.

**Four odd labels.** There are exactly two even labels. Write `n_OE` and
`n_EE` for how many of them have those types.

If `n_OE = 0`, there is again no OE frame, so no carrier. The six labels
`P, P, Q, Q, 2A, 2B` are an explicit sum to `4I` with odd-`c` count 4 and
with every `a+b` even. Every subset keeps `a+b` even and misses every
target.

If `n_OE = 2`, then `n_EE = 0`, so Lemma 4 leaves only size-2 carriers.
Lemma 2 says each target's size-2 carrier is its projector pair, so the
multiset contains `A`, `B`, `P`, and `Q`. Those four labels already include
both even slots. The other two labels are odd-`c` and sum to
`4I - (A+B+P+Q) = 2I`. Lemma 2 says every integral rank-one splitting of
`2I` has even `c` on both frames. Support fails.

If `n_OE = 1`, then `n_EE = 1`. Call the OE label `W` and the EE label `G`.
Every size-3 carrier is `{W, G, O}` for a single odd label `O`, so
`O = H - W - G` for the target `H` it carries. Every size-2 carrier is a
projector pair, so its OE endpoint is `A` or `B`. If `W` is neither `A`
nor `B`, there is no size-2 carrier, and all four targets are triples.

For a set `S` of projector labels and a set `T` of `k` triple targets, the
exact multiset `S ∪ {W, G} ∪ {H - W - G : H ∈ T}` sums to

```
sum(S) + sum(T) + (1-k) W + (1-k) G.
```

Support and the sum `4I` force this multiset, once overlaps are removed
below. The images `H - W - G` are distinct for distinct targets, and each
has odd `c`, so none equals `W` or `G`.

**Four triples.** Here `k = 4`, `S` is empty, and `sum(T) = 4I`. The
display collapses to `4I - 3W - 3G`, hence `G = -W`. Negation preserves
type, so `G` is OE rather than EE. This uses no special property of `W`.
The same identity is checked for `W = A`, `W = B`, and `W = 3A`, the last
of which is an OE frame other than a projector. The branch is impossible
for every integral `W`.

**The anchor is a projector.** The remaining possibility is `W ∈ {A, B}`.
The checker runs both anchors; the two calculations are the same after
swapping coordinates. Take `W = A`. Then `B` is not a label: the only OE
label is `A`, and `G` is EE while `B` is OE. Targets `B+P` and `B+Q` are
therefore triples. At least two targets are triples. The four-triple branch
is already impossible, so the number of triples is 2 or 3.

*Both `A+P` and `A+Q` are pairs.* The odd labels are `P`, `Q`, and the two
images of `B+P` and `B+Q`. If either image equals `P` or `Q`, then `G` is
one of the four integer candidates `H - A - P` or `H - A - Q`. Each
candidate fails to be a nonzero EE frame. Otherwise the four odd labels are
exactly those four vectors, and the sum solves as `G = (-3, 0, 0)`. That
vector is rank one of type OE, not EE. Substituting it back recovers `4I`,
so it is the unique solution of the sum and it has the wrong type.

*Exactly one of `A+P` and `A+Q` is a pair.* The included projector is `P`
or `Q`, and the other three targets are triples. The sum solves as
`-2G = (3, 0, 0)`. No integral vector satisfies that equation. The
half-integer value `G = (-3/2, 0, 0)` does recover `4I`, which checks the
linear algebra, and its first coordinate is not an integer. An overlap, in
which a triple image equals the included projector, again forces an integer
candidate for `G`, and each candidate fails to be EE.

The anchor `W = B` has the same three branches. Both pairs give
`G = (0, -3, 0)`, which is OE. Exactly one pair gives `-2G = (0, 3, 0)`,
which is not integral. Each overlap candidate fails to be EE.

Every distribution of the two even labels has contradicted the integral
rank-one hypotheses. Therefore no six integral rank-one labels sum to
`4I`, meet support, and have four or six odd-`c` labels.

## 6. The equation

For any distinct old projectors `E, F`, a solution of
`R+S+T+U = 4I-E-F` is six integral rank-one labels summing to `4I`, two of
which are `E` and `F`. Section 5 excludes every such six-label multiset
once four or more labels have odd `c`. The old-pair designation is not an
extra hypothesis the argument needs beyond that.

## 7. The count-two boundary

The six labels `A, B, P, Q, 2A, 2B` are nonzero and rank one, sum to `4I`,
and meet support: the targets are the pairs `A+P`, `A+Q`, `B+P`, and `B+Q`.
Exactly `P` and `Q` have odd `c`. This is the witness recorded in PR #7100.
The checker recomputes that one multiset and checks that replacing `2A` by
`2A+A` breaks the sum. It does not repeat the six old-pair verifications
from that package.

Section 5 does not apply to this witness, because the witness has two even
OE labels and two EE labels. Support at odd-`c` count 2 is not empty. The
obstruction starts at the next even count.

## 8. A bounded control, separate from the proof

`verify.py` also enumerates every integral rank-one frame of max norm 4 and
every quadruple of those frames which, together with an old pair, sums to
`4I`. More than 200 such quadruples occur. Every one that meets support has
odd-`c` count 2, and at least one does: the witness above. None with count
4 or 6 meets support.

That box is a control. A four-odd support solution inside the box would
falsify Section 5. Absence outside the box is not claimed from the scan.
Frames of larger norm are excluded by the case split, not by the norm.

## 9. What is not claimed

The theorem is the integral statement in the claim. It does not say that a
rational label with a fractional coordinate fails support, and it does not
define odd `c` for such a label. It does not classify the integral solutions
of odd-`c` count 0 or 2. It does not reprove the length-5 one-old support
obstruction, the zero-old four-call obstruction, or the inherited
call-versus-target inequality. Three old calls are a different equation.
No word is constructed, and the eight-call minimum is unchanged.

## Open next questions

Does any pair of nonzero rational rank-one frames, not both integral, sum
to `4I-H` for a target `H`? Lemma 2 is an integral census. A rational
complement pair would allow a size-4 carrier, which Section 2 excludes only
for integral labels. The first step is one rational solution of
`X+Y = 4I-(A+P)`, or a discriminant obstruction over `Q`.

Does the length-6 equation have a non-integral rational support solution
on which the inherited lattice character detects at least four calls? The
integral odd-`c` count is empty, so a length-6 word would have to leave
`Z^3`. The first step is one rational support solution with a denominator
greater than 1, then the subset scan and the character on the lattice that
solution generates.
