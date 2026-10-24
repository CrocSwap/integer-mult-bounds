# Exact insertion barriers around the BW16 72-line clique

This finite certificate proves a new local obstruction for the 72-line
Barnes-Wall clique published by DaysSky in [PR #895](https://github.com/CrocSwap/integer-mult-bounds/pull/895).
Adding one new line requires deleting at least **20** old lines. Adding two
compatible new lines requires deleting at least **30** old lines. Both
insertion thresholds are attained.

Consequently, any different clique with at least 72 lines must discard at
least 30 lines of the fixed clique. Every replacement that discards at most
29 old lines strictly decreases cardinality. A search that retains 43 or
more of these old lines cannot improve the 72-line witness.

Claim type: **exact finite certificate and scoped combinatorial proof**.
The maximum BW16 clique and the minimum decoder-window rank remain unknown.
The predecessor's window floor stays 72; no new kappa is claimed.

## Object and exact theorem

Use the predecessor's scaling

```text
L = RM(1,4) + 2 RM(3,4) + 4 Z^16.
```

Coordinates are indexed by the binary points 0 through 15. Let V be the
norm-eight lines of L, represented by the vector whose first nonzero
coordinate is positive. Let K be the fixed 72-element subset in
[CLIQUE72.json](CLIQUE72.json), copied byte for byte from DaysSky's source.
Two distinct lines are compatible when their integer inner product is
nonzero. A clique is a set of mutually compatible lines.

For an outside line x, define its forced deletion set

```text
S(x) = { k in K : <x,k> = 0 }.
```

The exhaustive certificate establishes

```text
min_(x in V\K) |S(x)| = 20,
min_(x,y in V\K, x != y, <x,y> != 0) |S(x) union S(y)| = 30.       (1)
```

There are 2,088 outside lines. Their deletion-set sizes have the exact
histogram `{20:378, 29:1080, 36:630}`. All 2,178,828 unordered outside pairs
are classified; 1,316,988 are compatible. Among the compatible pairs,
11,340 attain deletion size 30. The complete 18-bin pair histogram is
checked in [verify.py](verify.py) and emitted in its generated receipt.

Writing e_j for coordinate j, zero based, explicit attainments are

```text
x = 2(e_13 + e_15),
y = 2(e_11 + e_15).

|S(x)| = |S(y)| = 20,
<x,y> = 4,
|S(x) union S(y)| = 30.
```

Thus `(K\S(x)) union {x}` has 53 lines and
`(K\(S(x) union S(y))) union {x,y}` has 44 lines.
These are witnesses for the insertion thresholds, not improved cliques.

A more precise local statement follows. Require a replacement to discard
exactly d old lines and to contain at least one outside line. No such
clique exists for d < 20. For every 20 <= d <= 29 its largest possible
cardinality is exactly `73-d`.

## Proof and completeness of the finite component

The shell description is inherited from DaysSky's Construction-D argument.
Here is the finite domain used by the new certificate. The low residue of
a norm-eight vector is an affine binary function on four bits. Its weight
is 0, 8 or 16, and norm eight excludes weight 16. At weight zero, division
by two leaves an even-weight residue of norm two, giving the vectors
`2(+-e_i +-e_j)`. There are 240 canonical lines. At weight eight, every
nonzero coordinate is +-1 and the negative-sign count must be even because
RM(3,4) is the even-weight code. Each of the 30 affine hyperplanes gives
64 canonical sign patterns, hence another 1,920 lines. The two cases are
disjoint and exhaustive, giving 2,160 lines.

The verifier constructs that domain directly. A separate membership
predicate reconstructs an affine function from its values at zero and the
four coordinate points, checks all sixteen values, and checks the even
second-residue condition. The published clique is a fixed input premise;
its data hash, membership and pairwise compatibility are guarded before the
new outside-line computation. No predecessor executable or screen is run.

For each outside line the verifier computes S(x) by all 72 literal integer
inner products. It then visits every unordered outside pair, tests its
compatibility, and counts the size of the deletion union. Exact minima,
histograms and attaining lines establish (1). The registered replay repeats
the complete pair computation with ordinary integer dot products instead
of signed-support bit masks. Neither method uses floating arithmetic.

Now let C be any clique, D=K\C, and A=C\K. Compatibility forces
`S(x) subset D` for every x in A. If |D| < 20, (1) forces A to be empty.
If |D| <= 29, (1) forces |A| <= 1, since two lines in A would be compatible
and would require at least 30 deletions. Therefore, for 20 <= d <= 29,
`|C| <= 72-d+1`. This is attained by taking the 53-line one-insertion
witness and deleting any further d-20 old lines. For d < 20 the largest
clique after exactly d deletions is simply a subset of K, of size 72-d.
These statements prove the local obstruction without enumerating larger
cliques. They do not prove that 30 deletions suffice for another 72-line
clique or for an improvement.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bw16-clique-exchange-barrier
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/bw16-clique-exchange-barrier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/bw16-clique-exchange-barrier/verify.py --literal
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bw16-clique-exchange-barrier --check-source-history
```

The registered commands execute both pair representations, each in normal
and optimized Python. Expected marker:
`PASS_BW16_CLIQUE_EXCHANGE_BARRIER one=20 two=30 outside=2088 compatible_pairs=1316988`.
Each run writes a receipt to stdout with the enumerated histograms,
attainments and SHA256 hashes of every package file. No receipt is
handwritten and no output file is generated in the checkout.

The four boundary checks reject a nonaffine low residue and odd sign parity,
and distinguish a nonzero self contact and the invalid admission of an old
line as new. There are also 4,176 signed/scale encoding comparisons. All
checks use explicit exceptions and remain active under optimized Python.

## Scope, evidence and stopping decision

The initial claim sought a larger clique. Two short bounded serial
heuristics found none; this is only a search failure. The delivered result
is instead the exact local obstruction (1), which explains why small
replacement searches around this particular witness cannot succeed.
The first established new result ended the construction search.

The theorem is specific to the exact K bytes below. It covers arbitrary
simultaneous insertions under its deletion bound, but no other 72-line
clique is asserted to have the same neighborhood. It neither determines
maximum clique nor closes the decoder-window interval. Thirty is a sharp
two-line insertion threshold, not a proved sharp radius for an improving
exchange. The inherited admissible-pairing rule turns a clique into a
window floor, but this package adds no larger clique and therefore raises
no window floor. Physical decoding, helper and restoration prices,
compiler/outer admission and the multiplication theorem remain unproved.
Independent human and formal proof-kernel review are unclaimed.

Scientific base is `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`, priority
revision 7. The selected record and family guidance were read. The original
card's historical ceiling control was attempted and raises
`KeyError: 'complex_profile'` on the changed selected certificate schema.
It is not evidence for this theorem and is left unchanged. No selected
cold replay, Lean, Docker or historical suite is needed by this isolated
finite result.

Power-of-ten scope is the new verifier only. It has no recursion, dynamic
code loading, solver or imported predecessor implementation. All loops
are bounded by 16 coordinates, 72 old lines, 2,160 shell lines or
2,178,828 outside pairs. Functions stay below 60 lines. Rule 3 has a
managed-runtime deviation: Python allocates integers, tuples and generator
objects during checking. Live state is bounded by the fixed shell, 2,088
72-bit deletion masks and 18 histogram bins; pairs are streamed. There is
no retained quadratic adjacency matrix. Normal/optimized warning-strict
execution checks this fixed domain. Revisit resource bounds before adding
a configurable dimension or shell.

## Open next questions

1. Can a larger BW16 clique be found by a move discarding at least 30 lines
   of K, or by a different initial construction? This is the smallest search
   direction not excluded here. Start with one explicitly retained subset
   of at most 42 old lines; global optimality and the required replacement
   size beyond this necessary bound remain unknown.
2. Can a structural proof replace the finite deletion-set certificate, or
   establish its analogue for another inequivalent 72-line clique? Start
   by classifying the 378 minimum-deletion outside lines under K's actual
   stabilizer. No orbit or equivalence classification is supplied here.

## Provenance and credit

This contribution was produced by Nick Petalas. DaysSky supplies the
BW16 shell/screen setting and the published 72-line clique in PR #895,
head `3bf6fccaf17521ffdb9b3bec2740ba4886478556`. The copied source is
`research/bw16-unit-screen/data/clique72.json`, SHA256
`c16f23f68fd3e840216032df458dbd8f281822fbe1e829aeb06710e4372d0d99`.
Its bytes are retained unchanged in CLIQUE72.json; see [NOTICE.md](NOTICE.md).

DreamingOfClouds retains credit for the admissible-pairing framework,
#446/#595 and the #2244 line-system discussion. Joel Pulikkan retains
#620's screen credit; #598/#606 and the classical Barnes-Wall,
Reed-Muller and Construction-D lineage retain their contributions.
The new contribution is the outside-line insertion certificate and local
replacement theorem. No predecessor scientific acceptance is claimed.
New material is Apache-2.0.
