# A ceiling for every thinning of the retained paired-path moment

Prepared for Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.

## Scope and conclusion

Freeze Cao Yifan's PR4610 round-three profile at
`1eb8da6cfb35512c0cc2533413e5ca42f48e13c6`:

```
H = {4:28, 7:7, 8:47, 9:326}
P = {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}.
```

There are 112 ports, fresh block width 8, and one paid rank-one query per
port at each thin stage. Keep the predecessor's paired-path scalar word,
all its middle idle windows, a prefix of initial idle windows and the
complementary suffix of terminal idle windows. Allow **every** pair count
`p>=1`, every split `a+b=p-1`, and every binary subset of the `2p+1` full
stages. Specialize every removed stage multiplier to the identity in both
the idle words and the advertised main targets. Keep all productive helper
losses, paid native jobs, owned centres and thin queries.

Under this retained endpoint/invoice contract, no such word has positive
raw surplus at any saving `0.0030217759 <= C < 1`. The p16, a7/a8 word
has positive surplus at `C=0.0030217758`. Thus the best raw crossing is
in that interval of width `10^-10`; p16 with the existing alternating
full-stage pattern attains it. This is an infinite-family **moment theorem**,
not a new operator-admission theorem or a global barrier for other words.

The endpoint pattern is an explicit hypothesis inherited from the path
construction: one pair has all stage factors; the other pairs have the
successive prefix or suffix factors below. We do not infer a new universal
native/phase identity from finite tests. The verifier independently checks
the literal source's exact rational projectors and the complete formula
for every split and stage subset through p5. Those tests bind the stated
contract to the retained examples; the reductions and calculus below are
the infinite part of the theorem.

## 1. Arbitrary-mask formula

Fix `0<t=1-C<1`. Put `f(c)=(8c)^t`, `h(c)=(1+8c)^t`, `f(0)=0`,
and `A(t)=H(t)-P(t)`. A full stage contributes `A(t)`; a thin stage
costs 112, with no productive helper credit. The main target at the joined
end has rank `1+8k`, twice per port, where k is the total full-stage count.

On the prefix side start with `c=s_0`. For its jth window let
`o=s_(2j-1)`, `e=s_(2j)`. Its main target contributes `h(c+o+e)`,
its initial idle contributes `f(c+o)`, and its retained middle idle costs
`f(e)`. Increment c by `o+e`. On the suffix side read stages in reverse,
start with `c=s_(2p)`, and use the same formula. The remaining middle odd
stage is a separate bit. These three bits and the p-1 pairs partition all
2p+1 stages.

Thus the complete surplus is

```
F = k A(t) + 224 [h(k) + sum_windows(h(c+o+e)-f(c+o)-f(e))]
              - 112(2p+1-k).
```

At t=1 this simplifies to `48k-112`. In particular it is incorrect to
keep old helper credit after thinning or omit any thin query. The source
binding checks this rank-mass identity on every enumerated mask.

## 2. Three dominance moves eliminate all noncanonical masks

These moves compare raw surplus, not runtime or equal input counts. Each
keeps k and hence the entire local helper/paid contribution unchanged.
It produces another member of the allowed path moment family. Therefore
a positive surplus anywhere would imply a positive canonical surplus.

**Even-only to odd-only.** Replace `(o,e)=(0,1)` by `(1,0)`.
Later cumulative counts and all targets agree. The surplus gain divided
by 224 is `f(c)+f(1)-f(c+1)>=0`, by subadditivity of x^t. This includes
equality when c=0.

**Remove an empty pair.** For `(0,0)` remove that window and its two
thin stages. Its contribution is `g(c)=h(c)-f(c)<=1`, including g(0)=1.
The query saving is 224, so the surplus gain is `224(1-g(c))>=0`.
The side length and p each decrease by one; no full stage or helper is lost.

**Split a double-full pair.** Replace `(1,1)` by two successive `(1,0)`
pairs, adding one window and two stages, with k unchanged. The extra thin
query charge is 224. The surplus gain divided by 224 is

```
h(c+1) - f(c+2) + f(1) - 1
  = (8^t-1) - [(8(c+2))^t-(8(c+1)+1)^t] > 0.
```

Both differences on the right integrate the strictly decreasing derivative
`t*x^(t-1)` over an interval of length 7. The first interval starts at 1;
the second starts at `8(c+1)+1>=9`. This proves strict positivity.

Apply the first move to even-only pairs and split every double-full pair.
Then remove all empty pairs. The process terminates with only `(1,0)`
pairs. It preserves the three separate bits `l=s_0`, `r=s_(2p)`, and m
at the intervening odd stage, each in {0,1}. Splitting may increase p;
no finite pair-count cutoff is used.

## 3. Eight concave sequences replace the infinite mask search

Write `S=a+b`, `B=l+r+m`, `k=S+B`, and `g(j)=h(j)-f(j)`.
For a normalized mask,

```
F(S,a,b;l,r,m) = k A(t)
  + 224 [h(k) + sum_(j=1)^a g(l+j) + sum_(j=1)^b g(r+j)]
  - 112(2S+3-k).
```

The positive sequence g(j) is strictly decreasing for integer j>=1.
For fixed S and bits, the largest side sum is obtained by merging the
two decreasing lists `g(l+1),g(l+2),...` and `g(r+1),g(r+2),...`, taking
their S largest terms. This uses only integer argument order, not floating
comparisons. Let their sum be G(S).

For each of the eight bit triples, the resulting upper envelope has increment

```
F(S+1)-F(S) = A(t)-112
  +224 [h(S+B+1)-h(S+B) + (G(S+1)-G(S))].
```

The h increment strictly decreases and the next merged g term never increases.
Thus F is strictly discretely concave. A strict positive preceding increment
and strict negative following increment certify its unique integer maximum
over **all S>=0**. No tail search or unexplored large-p assumption remains.

At `C=0.0030217759` the exact interval certificate gives:

| l,r,m | Maximizing S | Upper bound for F |
|---|---:|---:|
| 0,0,0 | 18 | -7.78098 |
| 1,0,0 | 17 | -5.66497 |
| 0,1,0 | 17 | -5.66497 |
| 1,1,0 | 16 | -3.54895 |
| 0,0,1 | 17 | -4.23203 |
| 1,0,1 | 16 | -2.11602 |
| 0,1,1 | 16 | -2.11602 |
| 1,1,1 | 15 | -0.00000722 |

Displayed bounds are rounded upward; exact outward enclosures and adjacent
increments are in RESULT.json. All eight maxima are strictly negative.
For bits (1,1,1), S=15 means p=16, with sides 7 and 8 in either order.
Its surplus is strictly positive at the stated lower endpoint.

## 4. Exclude every larger C, rather than only one sampled exponent

Let `L(t)=P(t)-H(t)`. Its derivative divided by 9^t is

```
sum_(r=2,3,4,5) n_r (r/9)^t log r
 - 7(7/9)^t log 7 - 39(8/9)^t log 8 - 326 log 9,
n_2=412, n_3=510, n_4=99, n_5=40.
```

For `1/4<=t<=1`, upper-bound the positive terms at t=1/4 and
upper-bound each negative term at t=1. The exact resulting bound is below
`-9.53`. Hence L strictly decreases on this whole interval. Each h(k)
increases in t; so does each g(j), since `x^t log x` increases in x>=1.
Consequently every normalized F increases in t on [1/4,1]. Negativity
at `t=1-0.0030217759` excludes all smaller t down to 1/4.

For `0<t<=1/4`, P(t)>=3298 and H(t)<=2*408, since `9^(1/4)<2`.
Thus L(t)>=2482. Concavity gives `h(k)<=1+8kt` and `g(j)<=t`
for integer j>=1. Therefore every normalized surplus satisfies

```
F <= -112 + k(112+1792t-2482) + 224S(t-1) < 0.
```

This also covers k=S=0. Combining the two ranges and the dominance
reduction excludes every `0.0030217759<=C<1` in the stated family.

## 5. Even free owned centres do not reach C=0.01

As an explicitly unrealized optimistic relaxation, remove all eight paid
rank-eight owned-centre jobs, keeping every other charge and target. The
same dominance proof applies. The local derivative L' becomes still smaller,
and the small-t lower bound becomes 2474, which still exceeds 560.

Reoptimizing **all** pair counts, splits and thinning masks, rather than
keeping p16, puts the best relaxed crossing in
`(0.0080596238,0.0080596239)`, at p5 with both side lengths 2 and all three
separate flags full. The eight maximizing S values at the upper endpoint,
in the bit order used above, are `7,6,6,5,6,5,5,4`; all maxima are strictly
negative, and their adjacent differences have the required strict signs.
The p5 surplus is positive at the lower endpoint. Exact certificates are
in RESULT.json. The same monotonicity and small-t argument excludes every
larger C<1 in this relaxed family.

Thus even deleting the entire owned-centre bill cannot reach C=0.01 by
retuning this path. A C>=0.01 attack needs another changed hypothesis.
This is a planning obstruction, not an implementation of free centres.

## Implication and limits

The existing p16 allocation already attains this family's best raw crossing
with the frozen round-three inventory. More pair counts, asymmetric splits,
partial thinning, or mixtures of even and odd full stages cannot beat it.
The scope does not cover changed idle masks outside the prefix/suffix contract,
changed scalar words, nonbinary replacements, altered queries, different local
profiles, noncommuting stage actions, or a different supplier interface.

No new kappa, selected-frontier change, BIT improvement, compiler admission,
absolute-phase proof, physical implementation or multiplication theorem follows.
The remaining productive direction is to change one of those hypotheses.
Credit Cao Yifan and the source's full PR4470/native/controller lineage,
including Cinna Davis, zxv, Jacob Alan Sussman and the retained predecessors.
