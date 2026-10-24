# A sharp uniform bound for the binary full-guard remainder spectrum

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

**Claim type: scoped mathematical proof with an exhaustive finite local lemma.**
For every zero-diagonal binary k-by-k matrix c, define the character sum
from Nick Petalas's [#4275](https://github.com/CrocSwap/integer-mult-bounds/pull/4275):

```text
Z(c) = sum_{sigma in {0,1,2}^k}
       (-1)^{sum_{i,j} c_ij [sigma_i=1] [sigma_j=2]}.
```

For every k >= 3, the spectrum has the following uniform separation:

```text
c = 0:                        Z(c) = 3^k
exactly one nonzero entry:    Z(c) = 7*3^(k-2)
at least two nonzero entries: 0 < Z(c) <= 19*3^(k-3).
```

The last bound is sharp at every k >= 3. Two arrows with a common tail,
c_12=c_13=1 and every other entry zero, attain it. At k=2 the only
two-entry character has Z=5. Thus the single-entry modes are exactly the
nontrivial maximum, and the rest are separated by a factor at most 19/21.

This answers the structural-spectrum part of Ryanson Jonathan's
[#4607](https://github.com/CrocSwap/integer-mult-bounds/pull/4607) open
question without constructing the k=6 table of 2^30 characters. That
package supplies the five-event probability theorem and its open question;
its spectrum is cited context and is not replayed here. This result does
not prove the full-guard probability inequality for arbitrary k.

## Proof

### Positivity

Fix S, the set of coordinates where sigma=1. Sum first over T, the subset
of S's complement where sigma=2. Binary character orthogonality gives

```text
Z(c) = sum_{S: sum_{i in S} c_ij = 0 (mod 2) for every j outside S} 2^(k-|S|).
```

Every term is nonnegative and S empty contributes 2^k, so Z(c)>0. For one
arrow, exactly one of the nine assignments at its two endpoints has negative
sign. Its sum is seven; isolated coordinates multiply it by three.

### The finite conditioned lemma

Fix every coordinate outside a chosen set of h vertices. The exponent on
the remaining coordinates consists of their induced directed edges, an
arbitrary binary coefficient on each indicator [sigma_i=1] and
[sigma_i=2], and one constant. The constant changes only the sign. All
possible induced fields must be allowed, even when they do not arise from
a particular outside graph.

The following exhaustive finite lemma bounds the absolute value of this
conditioned sum. The verifier evaluates every edge mask and every one of
the 2^(2h) fields by its literal 3^h signed assignments. The maxima by
number of directed edges are:

```text
h=2:  one edge 7; two edges 5.
h=3:  one edge 21; two edges 19; three edges 17;
      four edges 15; five edges 13; six edges 15.
```

The two-edge h=2 row has 16 field cases. The h=3 rows with at least two
edges have 57*64=3648 graph/field cases. All are enumerated. This finite
lemma, rather than an extrapolation of small spectra, is the
computer-assisted component of the universal proof.

### Exhaustive graph split

View the nonzero entries of c as directed arrows with no loops.

1. If a reciprocal pair occurs, condition outside its two vertices. The
   two-edge lemma and the triangle inequality give Z(c) <= 5*3^(k-2),
   which is at most 19*3^(k-3).
2. Otherwise, if two arrows share a vertex, their endpoints form a set of
   three vertices containing at least two arrows. Its induced graph may
   contain further arrows. Every corresponding row of the h=3 lemma is
   at most 19. Conditioning and summing over outside assignments gives
   Z(c) <= 19*3^(k-3).
3. If neither case occurs, the arrows form a directed matching. For r>=2
   arrows the sum factors as 7^r*3^(k-2r). Its ratio to 3^k is
   (7/9)^r <= 49/81 < 19/27.

These cases cover every matrix with at least two entries. The two-arrow
common-tail example has sum 9+9+1=19, according to whether its central
coordinate is 0, 2 or 1. Padding it with isolated coordinates proves sharpness.

## Reproduction and evidence

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/binary-character-remainder-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/binary-character-remainder-gap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/binary-character-remainder-gap --check-source-history
```

Other machines may substitute their CPython 3.12 path. The direct command
prints `PASS_BINARY_CHARACTER_REMAINDER_GAP` in a generated JSON receipt
bound to all five package files. It writes no files. Both registered
commands run the same checks, normally and with -O, with warnings as errors.

The verifier enumerates every conditioned two- and three-vertex graph,
including all unary fields. It also checks the proof's graph split and
bound on every zero-diagonal character at k=2,3,4, comparing the literal
sum with the separate positive subset formula. These are new-lemma
checks, without predecessor code or a predecessor spectrum table.
Controls reject invalid dimensions, nonzero diagonal, negative or Boolean
rows, a false bound of 18, and reciprocal-pair misclassification. Padded
sharpness examples are checked at every k=3..8.

## Scope, credit and limits

Nick Petalas's #4275 supplies the exact character formula and header
interpretation. Ryanson Jonathan's #4607 supplies the explicit structural
remainder question and five-event predecessor theorem. Nick Petalas's
#4599 supplies the earlier four-event result. Cinna Davis supplied the BIT
request context; source527, commdata2338 and Jose Manuel retain the
normalizer lineage credit. Exact retained sources are provenance-only pins
in SOURCES.json. No predecessor executable or spectrum table is imported.

The independent-moment card is explicitly changed to this original
spectral side result. It concerns shared-header densities, and does not
reprice a paid supplier. The claim is restricted to binary characters with
zero diagonal and the exact three-state weights above. An arbitrary
signed or reweighted distribution has a different spectrum. No probability
comparison at all k, general negative association, request producer,
header selection/emission, physical invoice, supplier admission, new kappa
or complete multiplication theorem is established. Lean, Docker, selected
cold replay and independent human review are unrun.

All loops have fixed finite checker domains: local dimensions at most
three, full character dimension at most four, and sharpness dimension at
most eight. There is no recursion or dynamic code execution. Functions
fit within sixty lines. CPython dynamic allocation deviates from fixed
allocation; these bounds and one-MiB package-file limits bound live work.
Warning-strict normal and optimized runs are the available diagnostics.

## Open next questions

1. Can this uniform 19/21 remainder gap prove an explicit eventual
   full-guard product inequality for every fixed k? First combine it with
   the k(k-1) negative single-entry modes and the exact finite-GL factor
   in #4275. The resulting dimension threshold may be large; dimensions
   below it remain a separate obligation.
2. Which character graphs attain 19*3^(k-3)? First classify equality in
   the conditioned local lemma and its outside-field triangle inequality.
   This package provides a sharp family but no complete equality classification.
