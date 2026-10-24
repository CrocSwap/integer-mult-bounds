# Sharp high-weight excess at five labels and length twelve

**Scoped combinatorial proof; no new kappa.** Every simple restored universal
singleton-prefix walk of length twelve on F2^5 has separate-class pair-sum
excess at most **11** for every functional of weight four or five. The bound
is attained at each such weight. A weight-four functional cannot have an
(8,4) class split.

This closes Open next question 1 of Mihir Srivastava's
[PR #4907](https://github.com/CrocSwap/integer-mult-bounds/pull/4907).
That proof gave the sufficient cap 15 and excluded planar (8,4) minorities.
Its finite checks already measured the cap 11 and found no (8,4) walk.
Those measurements are prior work. The new result is the proof for every
minority shape, followed by the sharp support bound. The complete
multiplication exponent and selected frontier do not change.

Prepared for Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. No independent human or formal proof-kernel review is claimed.

## Definitions

Let q_0=0 and q_(i+1)=q_i+e_(w_i) in F2^5, where the twelve labels w_i
are in {0,...,4}. Restoration means q_12=0. Simplicity means that the
nonclosing states q_0,...,q_11 are distinct. Let S be this twelve-point
set. Universality means S+S=F2^5. In particular, all five labels occur.
Addition below is XOR. For a point set C, put

```text
D(C) = {x+y : x,y in C, x != y}.
X_f = choose(|A|,2) + choose(|B|,2) - |D(A)| - |D(B)|,
```

where A and B are the two classes of f in S. A difference in both
supports is counted in both. Universality gives
D(A) union D(B) = ker(f) minus {0}, a set of size 15.

## 1. Matching balance and the forced quotient cycle

Use Nick Petalas's matching-balance lemma from
[PR #4894](https://github.com/CrocSwap/integer-mult-bounds/pull/4894),
as used in PR #4907. For completeness, if f has weight four, let v be
the omitted coordinate vector. Let a and b be the numbers of cycle
edges within A and B, and c the number between them. Only v-edges stay
in a class, and these edges form a matching. With s=|A| and t=|B|,

```text
2s = 2a+c,   2t = 2b+c,   s-t = a-b,   2a <= s,   2b <= t.
```

Thus max(s,t) <= 2 min(s,t). The only unordered splits are (6,6),
(7,5), and (8,4). Weight five flips at every edge and gives (6,6).

Suppose the split is (8,4), with A the larger class. Equality forces
a=4, b=0, c=8. Every A vertex has its v-partner in A and exactly one
cycle neighbor in B. The cycle consists of four blocks

```text
B -- A --v-- A -- B.
```

Delete the v coordinate. After a translation, the projection T of A is
a four-point set in the even-parity subspace E of F2^4. Each point of T
labels exactly one block. Every block changes the v-level once. The
four B vertices therefore alternate v-levels: two at level 0, two at
level 1. The two crossing edges of a block preserve the v-level.

## 2. Universality forces an impossible neighbor count

A four-point set has either three or six nonzero differences. If T
has three, then D(A) has 1+2*3=7 elements. Four B vertices supply at
most six more, fewer than the required fifteen. Therefore |D(T)|=6.

Translate one point of T to zero. The other three are independent in
E. Let z be their sum, or equivalently the sum of all four original
points of T. Then z is the unique nonzero element of E absent from
D(T), and

```text
T and T+z are disjoint, and their union is E.
```

The lift formula is D(A) = {(0,1)} union {(d,0),(d,1): d in D(T)}.
Thus the two differences missing from D(A) are the lifts (z,0) and (z,1).
Universality requires both to occur in D(B). The first comes from two
B vertices at the same v-level. Call their projections u and w=u+z.
They use both vertices at that level. The second difference comes
from opposite levels. It cannot use two new endpoints: only the other
level is left. Thus one of its endpoints is a vertex already chosen,
and the other level contains a second lift of u or of w. Rename them
so that u occurs at both levels. Write the fourth projection as y.

Up to reversal and rotation, the alternating-level B order is

```text
u_0, u_1, w_0, y_1.
```

Here y != u, since B is a set; y=w is allowed. The four distinct block
labels t_0,t_1,t_2,t_3 in T must respectively be common cube neighbors of

```text
(u,u), (u,w), (w,y), (y,u).
```

Consequently u has at least three neighbors in T (t_0,t_1,t_3), and w
has at least two (t_1,t_2). Let N(x) be the four neighbors of x in Q4.
Since w=u+z, N(w)=N(u)+z. The partition E=T disjoint-union (T+z) gives

```text
|N(u) intersect T| + |N(w) intersect T| = |N(u)| = 4.
```

The cycle needs a sum of at least five. This is a contradiction. It
excludes every (8,4) minority, with no planarity assumption.

## 3. Small support bounds in F2^4

The remaining splits use these elementary bounds. Translation does
not change differences; affine dimension means the dimension after
one point is translated to zero.

| Size of C | If affine dimension is three | If affine dimension is four |
|---|---|---|
| 5 | 7 | 10 |
| 6 | 7 | at least 12 |
| 7 | 7 | at least 13 |

The table entries give the support size. These sets have affine dimension at least three. In dimension three,
more than half of the eight-point space is present. For each nonzero
h, one of the four pairs {x,x+h} is fully present, so all seven
nonzero differences occur.

In dimension four, choose an affine basis and send it to
{0,1,2,4,8}, using binary notation for F2^4. It has ten differences.
A sixth point has Hamming weight two, three, or four. The first two
cases give twelve differences; weight four gives fifteen. For weight
three, translate by one of its three basis vectors and choose the
translated basis. This makes the sixth point have weight two.
Coordinate permutations then put either twelve-difference case in the
form

```text
C6 = {0,1,2,3,4,8},    D(C6) = {1,...,12}.
```

Every possible seventh point gives a new difference. The following
four rows cover the complement of C6; each listed s belongs to C6.

| New point y | Choose s | New difference y+s |
|---|---|---|
| 5, 6, 7 | 8 | 13, 14, 15, respectively |
| 9, 10, 11 | 4 | 13, 14, 15, respectively |
| 12 | 1 | 13 |
| 13, 14, 15 | 0 | 13, 14, 15, respectively |

This proves the bound thirteen. If the chosen six-point set already
has fifteen differences, the claim also follows.

## 4. The sharp cap

Translate each functional class into ker(f), which is F2^4.
For (6,6), both supports have size at least seven. They cannot both
have size seven, since their union has size fifteen. Thus one has
size at least twelve, by section 3, and

```text
X_f <= 2*choose(6,2) - 12 - 7 = 11.
```

For (7,5), suppose the seven-point class lies in an affine
three-dimensional space with direction H. Its support is H minus {0}.
The five-point class would have to supply all eight differences outside
H. If it has k points in one H-coset and 5-k in the other, it supplies
at most k(5-k) <= 6 such differences. Universality rules this out.
The seven-point class therefore has affine dimension four. Section 3
gives support sizes at least thirteen and seven, so

```text
X_f <= choose(7,2) + choose(5,2) - 13 - 7 = 11.
```

Together with section 2, this proves the theorem. Sharpness follows
from the explicit universal simple restored words

```text
weight four: 012343234031, mask 10111, X_f=11;
weight five: 012343103432, mask 11111, X_f=11.
```

Coordinate permutations send the first mask to every weight-four mask
and preserve the hypotheses and excess. The first witness is retained
from PR #4907. The second was selected from its existing measured census;
we claim no new witness search result.

## Reproduction and evidence

Use Python 3.12 for the registered runner. The standalone verifier supports
Python 3.12 or later. Both use only the standard library:

```sh
python3 -I -B research/f7-five-label-sharp-cap/verify.py
python3 -I -O -W error -B research/f7-five-label-sharp-cap/verify.py
python3.12 -B scripts/research_package.py --package research/f7-five-label-sharp-cap
```

The standalone verifier imports no predecessor program. It checks all
23,816 subsets of sizes five, six and seven in F2^4. It also checks all
127,400 v-invariant (8,4) set pairs at f=01111, including all 13,664
universal sets. A second method searches the literal twelve-vertex
cube graph for a Hamiltonian cycle for each universal set. This method
does not use the quotient proof or its degree-sum contradiction.
Translation and coordinate symmetry cover the other weight-four masks.
The set counts repeat the predecessor domain; the new tests corroborate
the stronger exclusion and its proof steps.

The verifier checks both equality witnesses, invalid-input controls,
a cap-ten rejection, a low-weight boundary, and a universal set that
has no required cycle. It also checks a nonuniversal (8,4) cycle as
a positive control for the graph search. Normal replay recomputes the
complete receipt and compares it with RESULT.json. `--emit-receipt`
prints the calculated receipt for explicit authoring. It writes no files.
The receipt binds all five source files in this package. The standalone
check needs neither Git nor network access.

Local checks passed with CPython 3.12.13 and 3.14.7 on macOS. Both
registered Python 3.12 commands passed. Eight separate code mutations
failed in optimized mode with receipt comparison disabled: wrong affine
dimension, a lost difference, graph search forced false or true, omitted
universality, low-weight admission, cap ten, and merged class supports.
The controls test semantic behavior, not only source hashes.

## Scope, provenance and credit

Base: `b91956876e5b4122fd89179f1b57557ff8378f15`, priority revision 7.
The selected kappa is 60403/20000000. SOURCES.json binds predecessor
proof documents as historical provenance. They are not runtime inputs.
This is the handoff-first refinement of the census-pruning-audit card,
with its original card retained in TASK.json. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4903#discussioncomment-19138640)
records the bounded assignment and overlap limits.

Credit Mihir Srivastava (@mihir-s-05) for PR #4907's theorem, quotient
setup, prior measured cap and open question. Credit Nick Petalas for
PR #4894's matching-balance lemma and the earlier measured classifications.
Retain unpaidmoon's question and excess convention from
[PR #4148](https://github.com/CrocSwap/integer-mult-bounds/pull/4148),
Nicholas Stone's parity correction from
[PR #2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973),
James Reed's boundary audit from
[PR #3096](https://github.com/CrocSwap/integer-mult-bounds/pull/3096),
and Ross Richardson's singleton-prefix model from
[PR #943](https://github.com/CrocSwap/integer-mult-bounds/pull/943).
The new neighbor-count proof and support argument are stated in full.
No predecessor source or license notice is changed.

The result does not cover other dimensions or lengths, partial prefixes,
low-weight functionals, nonsimple walks, nonuniversal sets or arbitrary
point sets without a cycle. No engine integration, seven-label census,
supplier admission, selected cold replay, Lean or Docker run is claimed.
It gives no new multiplication exponent or practical speedup. The proof
and code are author-checked; independent review remains open.

## Open next questions

Can the sharper complete-walk bound support a useful partial-prefix prune?
First derive a completion bound from the remaining edges and prove that
it preserves every universal completion. Then measure it in a maintained
engine. No such completion contract or runtime result is supplied here.
