# Rational splittings of 2I are not length-6 words

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, fix the old call `B` and the frozen frames `A`, `P`, and `Q`. Let `X` and `2I-X` be any rational rank-one splitting of `2I`. The six labels

```
A, B, P, Q, X, 2I-X
```

sum to `4I` and meet all four targets as subset sums. Both the `P`-coefficient and the `AB`-coefficient extend to the lattice they generate. Each extension detects two calls and four targets. The inherited inequality therefore admits no word on this multiset.

The displayed point is the chart value `t=2`, with frames `(-2/5, 4/5, 8/5)` and `(12/5, 6/5, -8/5)`. For that one lattice every integer lift of either character, not only the exhibited odd multiple, gives the same count. Inside the lattice, no word that uses all six labels has fewer than ten calls. A single extra label is impossible at any ambient group, so length 7 is impossible as well.

Selected κ stays `363005817/100000000000`. Nothing here changes the selected frontier, exhibits a word, or moves the eight-call minimum. The length-6 support census of PR #7067 is not replayed.

The inequality "detected calls ≥ detected targets" is inherited from `research/bit-two-signed-frame-floor/PROOF.md`, Section 1, and is not reproved. The address group is a subgroup of `Q^3`, so it is torsion-free: the determinant monomial of a word is `[4I]` only when the paid labels sum to `4I`. That reading of the determinant identity is the same section and is not reproved.

## 1. Setup

Addresses are rational symmetric 2-by-2 matrices. Write

```
A = diag(1,0),  B = diag(0,1),
P = [[1,1],[1,1]]/2,  Q = [[1,-1],[-1,1]]/2.
```

A coefficient vector `(a,b,c)` means `aA + bB + cP`. The matrix is

```
[[a + c/2, c/2], [c/2, b + c/2]].
```

Its trace is `a+b+c` and its determinant is `ab + c(a+b)/2`. The matrix is nonzero and rank one exactly when the vector is nonzero and `2ab + c(a+b) = 0`. The old projectors and the identity are

```
A = (1,0,0),  B = (0,1,0),  P = (0,0,1),  Q = (1,1,-1),
I = (1,1,0),  2I = (2,2,0),  4I = (4,4,0).
```

The four targets are `A+P`, `A+Q`, `B+P`, and `B+Q`. Each has trace 2 and determinant `1/2`.

For a primitive integer vector `u = (u1,u2)`, write `n = u1^2 + u2^2` and

```
uu^T = u1(u1-u2) A + u2(u2-u1) B + 2 u1 u2 P.
```

The partner direction `w = (-u2, u1)` is primitive and has the same squared length. The matrices satisfy `uu^T + ww^T = n I`, so

```
X(u) = (2/n) uu^T,  2I - X(u) = (2/n) ww^T
```

are nonzero, symmetric, rank one, and sum to `2I`. Conversely every rational rank-one splitting of `2I` arises this way. A rank-one symmetric matrix has a rational image line. Its trace equals its nonzero eigenvalue, so a summand of trace 2 is the positive multiple `(2/n) uu^T` of the primitive generator of that line. Squares modulo 4 are `0` and `1`. A primitive vector is not divisible by 2, so `n` is `1` or `2` modulo 4, never `0`.

The four pair sums `{A,P}`, `{A,Q}`, `{B,P}`, and `{B,Q}` are the four targets, and they do not use `X`. The six labels therefore sum to

```
A + B + P + Q + 2I = 4I,
```

and the five labels other than the old call `B` sum to `4I-B`. This is the support solution in the construction of PR #7067. The choice of which projector is called old does not change the multiset: the same six labels appear for each of the four choices. The argument below is written for old call `B`.

## 2. The odd multiplier

Let `m = n / gcd(n,4)`. Then `m = n` when `n` is odd, and `m = n/2` when `n ≡ 2 (mod 4)`. In both cases `m` is odd.

The two forms

```
f_PQ(a,b,c) = m c,  f_AB(a,b,c) = m(a+b)
```

are `Z`-linear. On the old lattice `Z^3` they reduce to `c` and `a+b` modulo 2, because `m` is odd. Thus `f_PQ` is a `P`-coefficient and `f_AB` is an `AB`-coefficient.

Let `Λ = Z^3 + Z X(u)`. For every `Y` in `Λ`, both `m` times each coefficient of `Y` is an integer. It is enough to check generators. On `Z^3` the coefficients are already integers. On `X`,

```
a = 2 u1(u1-u2)/n,  b = 2 u2(u2-u1)/n,  c = 4 u1 u2 / n,
```

so

```
m a = 2 u1(u1-u2)  or  u1(u1-u2),
m b = 2 u2(u2-u1)  or  u2(u2-u1),
m c = 4 u1 u2      or  2 u1 u2,
```

in the odd and even cases respectively. Each value is an integer. Hence both forms are integer-valued on `Λ`. They are even on `2Λ` because they are `Z`-linear and integer-valued, so each descends to a character `Λ → F2`.

## 3. Both characters detect two calls and four targets

**Theorem 1.** For every primitive `u`, both characters detect exactly the calls `{P,Q}` or `{A,B}` respectively, and both detect all four targets. The six labels are therefore not a word.

The values on the splitting are

```
f_PQ(X) = 4 u1 u2     if n is odd,    and  2 u1 u2  if n ≡ 2 (mod 4),
f_AB(X) = 2(n - 2 u1 u2)  if n is odd, and  n - 2 u1 u2  if n ≡ 2 (mod 4).
```

Both are even integers. The partner is `2I-X`, and

```
f_PQ(2I) = 0,  f_AB(2I) = 2m,
```

so the partner receives the negative of an even integer under `f_PQ` and the difference of two even integers under `f_AB`.

Among the projectors, `f_PQ` is odd exactly on `P` and `Q`, and `f_AB` is odd exactly on `A` and `B`. The four targets each have odd `c` and odd `a+b`:

| Target | `(a,b,c)` | `a+b` | `c` |
|---|---|---|---|
| `A+P` | `(1,0,1)` | 1 | 1 |
| `A+Q` | `(2,1,-1)` | 3 | -1 |
| `B+P` | `(0,1,1)` | 1 | 1 |
| `B+Q` | `(1,2,-1)` | 3 | -1 |

Multiplication by the odd integer `m` preserves both parities. Each character therefore detects two of the six calls and all four targets. The inherited inequality forbids a word.

The same count holds for every other integer form that reduces to the same character on `Z^3` and is integer-valued on `Λ`. A general `P`-coefficient has the shape `2α a + 2β b + (1+2τ) c`. On `X` its value is `4M/n` for an integer `M`. If `n` is odd, an integer value is `4` times an integer. If `n = 2m` with `m` odd, the relation `4M = N n` becomes `2M = N m`, so `m` divides `M` and `N` is twice an integer. A general `AB`-coefficient has the shape `(1+2p)a + (1+2s)b + 2t c`. On `X` its value is `2K/n` for

```
K = (1+2p) u1(u1-u2) + (1+2s) u2(u2-u1) + 4 t u1 u2.
```

When `n` is odd, an integer value is twice an integer. When both coordinates of `u` are odd, `K ≡ 0 (mod 4)`: the `4t` term vanishes modulo 4, and with `d = u1-u2` the other two terms are `(1+2p) u1 d` and `-(1+2s) u2 d`. If `d ≡ 0 (mod 4)` both vanish. If `d ≡ 2 (mod 4)`, each product of two odd factors with `d` is `2` modulo 4, and those two contributions sum to `0` modulo 4. An integer value `N = 2K/n = K/m` then satisfies `K = N m` with `K` divisible by 4 and `m` odd, so `N` is divisible by 4. In every case an integral value on `X` is even, and the induced character on `Λ` is independent of the lift.

## 4. The displayed frames at t = 2

Take `u = (1,2)`. Then `n = 5`, `m = 5`, and

```
X = (-2/5, 4/5, 8/5),  2I-X = (12/5, 6/5, -8/5).
```

These are the chart frames at `t = 2`, on directions `(1,2)` and `(2,-1)`, each at scale `2/5`. The exhibited forms are `f_PQ = 5c` and `f_AB = 5(a+b)`. Their values on the six labels are

| Label | `5c` | `5(a+b)` |
|---|---:|---:|
| `A` | 0 | 5 |
| `B` | 0 | 5 |
| `P` | 5 | 0 |
| `Q` | -5 | 10 |
| `X` | 8 | 2 |
| `2I-X` | -8 | 18 |

Each column has exactly two odd calls. All four targets are odd in both columns.

Every integer `P`-coefficient is `2α a + 2β b + (1+2τ) c`. On `X` the numerator of the value is `-4α + 8β + 8 + 16τ`, and the value is that numerator divided by 5. The numerator is `0` modulo 5 exactly when `τ ≡ 2 - α - 3β (mod 5)`. Substituting `τ = 2 - α - 3β + 5k` produces the even integer `-4α - 8β + 8 + 16k`. The partner receives `4α + 4β` minus that integer, which is even. Raising `α`, `β`, or `τ` by 5 changes the value by `-4`, `8`, or `16`, all even, so the `5^3 = 125` residue classes exhaust the parities of all integer lifts. The coefficient of `τ` is invertible modulo 5, so exactly 25 of those classes are integral, and each of those 25 values is even. The same period check for a general `AB`-coefficient, whose numerator on `X` is `-4p + 8s + 2 + 16t`, has an invertible coefficient of `t` and gives another 25 integral classes, all even. This residue count is an exhaustive finite census of the parities. It is not a sample of directions.

One further boundary belongs to this lattice only as a negative control. The matrix `P/2 = (0,0,1/2)` is rank one and does not lie in `Λ`, because every `c`-coordinate in `Λ` has denominator dividing 5. Every `P`-coefficient shape `(1+2τ)c` takes the value `τ + 1/2` on `P/2`, so the `P`-coefficient does not extend. The `AB` lift `a + 3b`, from `(p,s,t) = (0,1,0)`, is integral on the six labels and on `P/2`. It is odd on `A` and `B` only. Thus the eight labels given by the six plus `P/2` and `-P/2` are still not a word: the same inequality reads two calls against four targets.

## 5. Ten calls inside the lattice

**Lemma 2.** No nonzero rank-one matrix in `Λ` has character `(1,1)`.

Clear denominators by the odd integer `m`. For `Y` in `Λ`, the integers `A' = m a`, `B' = m b`, and `C' = m c` satisfy

```
2 A' B' + C' (A' + B') = m^2 (2ab + c(a+b)).
```

Character `(1,1)` means `A'+B'` and `C'` are both odd, so the left side is odd and cannot vanish. A vanishing quadric with a nonzero vector is therefore impossible.

**Corollary 3.** Let every paid label of a word lie in `Λ`, and suppose each of `A`, `B`, `P`, `Q`, `X`, and `2I-X` occurs at least once. The word has at least ten paid calls.

The six labels sum to `4I`. Any further paid labels, including extra copies of these six, sum to `0`. Lemma 2 says a rank-one label in `Λ` has character in `{(0,0),(1,0),(0,1)}`. Paid labels in this model are nonzero symmetric rank-one matrices. The original six contribute two `AB` detections and two `P`-detections. The extras must contribute at least two more of each, and the sum of their characters is `0` in `F2^2`. No multiset of size 1, 2, or 3 drawn from those three characters meets both quotas and sums to `0`. Four extras are enough for the character arithmetic: `A`, `-A`, `P`, and `-P` have types `(1,0)`, `(1,0)`, `(0,1)`, and `(0,1)`. That multiset is not claimed to be a word. The counting lower bound is therefore ten calls, and it is not a construction of a ten-call word.

Length 6 is the empty extra multiset, already forbidden by Theorem 1. Length 7 would be a single extra label equal to `0`, which is not a paid address. That length is impossible whether or not the extra label is chosen inside `Λ`. The ordinary eight-call word uses only the four projectors, so it does not contain `X` and is not affected. Corollary 3 does not raise the eight-call minimum.

## 6. What this proof does not say

The support classification of PR #7067 is a separate exhaustive census of subset tuples. This file uses only the direct construction, which is addition of the four projector pairs. It does not replay that census and does not prove that no other length-6 support solution exists.

A word that omits one of the six labels, or that uses a label outside `Λ`, is outside Corollary 3. Section 4 records one outside length-8 pair, with `P/2`, that is still forbidden. The open question below is the next such pair.

The result is a scoped impossibility under the inherited inequality and the torsion-free determinant identity. It is not an unrestricted multiplication theorem and not a change of selected κ.

## Open next questions

Is there a rank-one matrix `Y` outside the `t=2` lattice for which every `AB` lift and every `P`-coefficient lift that is integral on the displayed frames detects `Y`? The cancelling pair `Y, -Y` would then meet both inequalities at length 8. The half projector `P/2` does not: the lift `a+3b` misses it. The smallest next matrix is `(0,0,1/3)`.
