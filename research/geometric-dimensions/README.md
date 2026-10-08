# Geometric extensions and an unsuccessful dimension search

This is a research continuation of [PR #9](https://github.com/CrocSwap/integer-mult-bounds/pull/9),
which refines Zhihao Chen's [PR #7](https://github.com/CrocSwap/integer-mult-bounds/pull/7).
**No larger multiplication exponent is claimed here.** The current submitted
conditional witness remains kappa = 3.8e-9. The lemmas below are written
arguments awaiting independent review; circuit enumeration does not formally
verify the multiplication theorem or the general transfer arguments.

After these screens finished, [PR #10](https://github.com/CrocSwap/integer-mult-bounds/pull/10)
posted a stronger conditional claim, kappa = 6149999/50000000000000,
using batched recursive networks. Its proof has not been reviewed here.
The comparisons below are specifically against PR #9, not a current-best
claim. The output-cost obstructions apply to the stated unbatched compiler
and do not rule out PR #10's different recursive cost accounting. Reviewing
that construction takes priority in subsequent numerical research.

## Bank sharing does not require a multiple of four

Let the vertices be the r-subsets of an h-point set. Connect a left copy S to
a right copy T when |S intersection T| = t. Every vertex has degree

    d = binom(r,t) binom(h-r,r-t).

If h >= 2r-t, then d > 0. For any collection A of left vertices, its d|A|
edges end in its right neighborhood, which receives at most d|N(A)| edges.
Thus |N(A)| >= |A|. Hall's theorem supplies a bijection pi with
|S intersection pi(S)| = t. This is a finite fixed permutation, independent
of the multiplication input size. Its existence is enough to choose a fixed
network wiring; this argument makes no efficiency claim for finding it.

For r=5,t=2, h>=8 suffices. In PR #7's bank join, the only property of pi
used to establish the middle-factor orthogonality is this intersection
condition. Its labels and rank accounting therefore admit every h>=8 for
which the producer and remaining interface hypotheses hold, including odd h.

There is also a small explicit construction for every even h>=8. Retain
PR #7's paired-point cases with zero or one complete pair. In the case of
two complete pairs, replace its Euler successor with a cyclic ordering of
the edges of a complete graph in which consecutive edges share one vertex.
Such an ordering exists at every order k>=3:

* Start with the triangle's three edges.
* Given consecutive edges e,f with shared vertex a, choose b in f other
  than a. When adding a vertex z, insert between e and f all new edges
  (x,z), starting with (a,z), ending with (b,z), and using every other old
  vertex once in between.

The insertion preserves cyclic adjacency and includes every edge exactly
once. Its successor is a bijection on edges. In PR #7's two-pair case this
preserves exactly one full pair, while flipping the singleton; the five-sets
therefore intersect in exactly two points. Invertibility follows separately
in each of the three preserved cases. `matching.py` checks every image at
h=8,10,24,26,28,30,32, not just a random sample.

## A prime-power family of scalar identities and rational labels

Let q=p^a for a prime p, put r=2q-1 and t=q-1, and index payloads by r-sets.
For 0<=j<=r, in characteristic p,

    binom(j,t) - [j=t] = [j=r].

Proof: write j=b+uq with 0<=b<q and u in {0,1}. Frobenius gives
(1+z)^j = (1+z)^b (1+z^q)^u in F_p[z]. Its coefficient of z^(q-1)
is one exactly when b=q-1, namely at j=t or j=r.

For each t-set C, retain the sum of payloads whose r-set contains C. The
sum of these totals over C contained in a target S has coefficient
binom(|S intersection T|,t) on source T. Subtract the side sum over exactly
intersection-t neighbors. The displayed identity gives the identity map.
For a fixed C contained in S, that side sum is a degree-q exclusion sum
on the points outside C, excluding S minus C.

Use rational address labels given by r-set indicators, with bilinear form

    H = I - (t/r^2) J.

Two labels have pairing |S intersection T|-t and each has norm q. Any
linear combination u of indicators containing a fixed C has common value
alpha on C and coordinate sum r alpha. Consequently

    u^T H u = sum_{i outside C} u_i^2.

If this is zero, the coordinate-sum relation forces (r-t)alpha=q alpha=0
over Q, hence u=0. Thus every such source span is positive definite and
nondegenerate. The full span has dimension h-t: differences of r-sets
containing C span the zero-sum vectors outside C, and any one indicator
adds the remaining dimension. Here h>=2r-t guarantees enough outside
points. The ambient form is nonsingular unless h=r^2/t; among integer
q>=2 this exceptional integral case is q=2,h=9, which must be excluded
or treated separately.

The regular-graph matching above applies with h>=3q-1. These facts provide
the scalar and geometric ingredients of a candidate family. They do not
by themselves provide a cheap producer, a complete finite-alphabet transfer,
or a new assembled multiplication theorem.

## Why larger prime powers are expensive in this architecture

Retaining the same three-stage schedule, center accounting, and c+Q role
compiler would give, with v=binom(h,r), m=h^3,

    Q = binom(h,t) (binom(h-t,q)+1),  R=c+Q,
    eta = (v - 6 binom(h,t)(h-t)) / (2 h^3 (v+R)).

There are Q designated output uses. This alone forces R>=Q, regardless
of producer optimizations. The corresponding saving is
a=-log(1-eta)/log(m). For 0<eta<1,

    a <= eta / ((1-eta) log(m)).

For q>=7, h>=3q-1>=20 and binom(2q-1,q-1)>=1716. Dropping center losses
and retained-total outputs gives eta <= 1/(2*20^3*1717). The exact rational
logarithm enclosure in `family.py` proves that even this upper bound on a
is below PR #9's certified bit saving 761/10^11. Monotonicity covers all
larger q and h, not merely a finite scan.

For q=5 a stronger elementary count applies. At h=3q-1 the deficit is
negative. For h>=3q, each side output has at least q+1 source terms.
Its source-support intersection recovers C, and its source-support union
recovers the excluded set E, so all these outputs are distinct. Retained
totals are also distinct and differ from side outputs. Every output needs
a distinct addition node in a monotone binary-addition DAG. Hence c>=Q
and R>=2Q. `family.py` checks exact upper bounds for h=15,...,29 and a
monotonically decreasing bound for all h>=30. Each is below 761/10^11.

These exclusions apply only to this retained-center architecture with its
specified output interface and c+Q compiler. They do not exclude different
compilers, center schedules, payload models, or arbitrary algorithms.

The first remaining larger prime power is q=4: binary payloads on seven-sets,
common triples, and degree-four exclusion circuits. Around h=27 the circuit
would need roughly fewer than 4.04 additions per designated output to beat
the current bit saving (the exact target depends on h). No such producer
has been constructed here. This is a research target, not a new bound.

## Dimension experiments

Complete support enumeration, dead-node pruning, and all three PR #9 star
rules were tested. The source extension uses nine 64-bit key words to hold
every pair coordinate through h=32. At odd h, the unpaired last point is
included in the ordering tail. No fingerprints replace exact key equality.

| h | Checked roles R | Estimated bit saving |
|---:|---:|---:|
| 24 | 4,728,452 | 4.8281431e-9 |
| 26 | 7,602,157 | 7.2041450e-9 |
| 27 | 9,476,476 | 7.5484524e-9 |
| 28 (PR #9) | 11,670,540 | 7.6108867e-9 |
| 29 | 14,398,188 | 7.4068726e-9 |
| 30 | 17,515,487 | 7.1356570e-9 |
| 32 | 25,224,960 | 6.4700807e-9 |

The displayed decimal estimates are not new headline witnesses. Exact
rational upper bounds separately reject all six new dimensions against
the certified 7.61e-9 bit saving. This does not assert optimality across
all dimensions or other producers.

Run from the repository root with Python 3.11 and a C++17 compiler:

```sh
c++ -std=c++17 -O3 research/geometric-dimensions/supports.cpp -o build/geometric-dimensions/check
python3.11 research/geometric-dimensions/explore.py 24 26 27 29 30 32
python3.11 research/geometric-dimensions/matching.py 8 10 24 26 28 30 32
python3.11 research/geometric-dimensions/family.py
python3.11 research/geometric-dimensions/report.py
```

Create `build/geometric-dimensions/` before compiling on a fresh checkout.
Generated producer data stays there. The h32 check can use several GB of
memory; none of the generated graphs or binaries belongs in Git.

## Provenance and next experiments

The ternary motif, source-span argument, producer, and original matching
are Zhihao Chen's PR #7 work. `supports.cpp` is that attributed checker,
extended only in its key capacity, dimension bound, and odd-dimension point
ordering. PR #9 supplies the selected star rules. Earlier contributions and
the OpenAI manuscript remain credited in the parent contribution. These
extensions and experiments were prepared with substantial OpenAI Codex
assistance at Rohan Arun's request; no worldwide priority is asserted.

Next work should focus on a shared degree-four exclusion producer for q=4,
or a compiler that reduces output-use overhead. Another small search over
ternary tie-breaking rules may improve the number, but would be a circuit
heuristic refinement rather than a new geometric mechanism.
