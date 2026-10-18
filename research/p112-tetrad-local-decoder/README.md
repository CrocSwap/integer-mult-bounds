# P112 tetrad-local masked decoders: exact COPY112 and rank cap four

**Scoped negative result; no new κ, supplier, or frontier change.** Any finite
masked decoder in the one-sided tetrad-local alphabet below has total copied
rank at least **112**, and each paid term has rank at most **four**. The bound
112 is attained by an explicit 56-term masked identity with COPY profile
`{2: 56}`, and also by a 112-term all-pairs identity with profile `{1: 112}`.
Neither is proposed as a physical supplier. A mixed-orientation term is allowed:
either side may be local, independently for each term.

This is the negative-result alternative of `complex-rank-shape-decoder`, not a
claim to meet its positive 5% ceiling gate. It changes both the exactly-eight-term
and all-pairs premises; it does not redo the P106/P105 rigidity handoff. The
obstruction applies to arbitrary real or complex coefficients, arbitrary
cancellations, overcomplete term counts, and arbitrary opposite-side supports.

## Alphabet and exact statement

Use norm-two representatives `r_i` of the 120 E8 lines. Fix the orthogonal frame

```
F0 = { e_(2j) + e_(2j+1), e_(2j) - e_(2j+1) : j=0,1,2,3 }.
L = P112 = P120 minus F0.
G_ij = <r_i,r_j>;  N_ij = (G_ij+1) mod 2.
```

Relative to F0, each live root has four nonzero frame coordinates, all ±1.
The fourteen possible four-element supports T partition L into eight-line
blocks B_T. Within a block, parity of the number of negative coordinates
partitions B_T into two orthogonal four-frames C_T,0 and C_T,1. Roots in
opposite classes have odd inner product. Thus

```
N[B_T,B_T] = diag(J4,J4).
```

These are the standard D4/tetrad classes of
[complex-rank8-decoder-rigidity, §2](../complex-rank8-decoder-rigidity/PROOF.md).
The new verifier reconstructs them directly, without importing that checker or
using its rigidity theorem. It also checks `rank_F2 N[B_T,L] = 4` for all 14
blocks. No hyperplane classification or SAT result is needed.

Let `K = sum_k d_k t_k^T` over R or C, using **ordinary transpose**, and require
only `K_ii=4` and `K_ij=0` on orthogonal live pairs. For each term, define its
**actual nonzero supports** X_k and Y_k and charge

```
beta_k = rank_F2 N[X_k,Y_k].
```

For each paid term require `X_k subset B_T` **or** `Y_k subset B_T` for some
T. Both the chosen block and orientation may vary by term. The other support
is unrestricted. Arbitrarily many unrestricted cost-zero terms may also be
added. A nominal support with cancelled coefficients is not used for pricing.

**Theorem.** Under precisely these hypotheses,

```
sum_k beta_k >= 112,              1 <= beta_k <= 4 for every paid term.
```

### Proof, including overcompleteness and cancellation

For a term let h_k count the 28 four-frames C for which both X_k and Y_k meet
C. Restrict the complete identity to one C. Its target is `4 I4`, rank four
over R or C. Each term contributes rank at most one and contributes zero when
one side misses C. Therefore at least four terms meet C on both sides, even
if arbitrary cancellations occur. Summing gives `sum h_k >= 28*4 = 112`.

A zero-cost term has `N[X_k,Y_k]=0`, so cannot meet both sides of any C:
otherwise its pairing submatrix contains a one. It has h_k=0 and does not
supply any of the rank demand.

Suppose X_k is contained in B_T. Only its two classes can be counted in h_k.
For every counted class choose a row in X_k and a column in Y_k belonging to
that class. The resulting h_k-by-h_k pairing minor is an identity matrix:
entries within a class are one, entries across the two classes are zero.
Consequently `beta_k >= h_k`. The same proof, transposed, handles a local
Y_k. Summing proves the floor. The checked full-block pairing rank four and
rank monotonicity give `beta_k <= 4` regardless of the unrestricted opposite
support. This proof neither assumes root-linear factors nor bounds the number
of terms. It also never assumes their rank-one contributions are independent.

### Sharpness and the small decoder identity

For one B_T write E for its eight-by-four ±1 frame-coordinate matrix. Since
F0 is a norm-two orthogonal basis,

```
E E^T = 2 G[B_T,B_T].
```

Extend each of the four columns by zero outside B_T, using the same vector for
d and t. The four actual support pairs are `(B_T,B_T)`, each costing exactly
two. Doing this on all 14 blocks gives 56 rank-two terms, total112. On different
blocks K is zero; this is correct for every required orthogonal pair, while
odd-pair entries are unconstrained. On each block the identity is exact.

For an all-pairs attainment, use one term `d=e_i`, `t=2G[i,:]` per live line.
It costs one because the pairing has one row and contains its diagonal one.
Their sum is exactly 2G and the cost is112. This separately shows the floor
is sharp even if all-pairs exactness is restored while overcompleteness remains.
These identities are coefficient identities only, not charged physical words.

## Quantitative escape condition and rank-shape consequence

For any masked decoder, including nonlocal terms, let Q be its nonlocal paid
terms and let `COST=sum beta_k`. The same four-frame rank demands imply

```
sum_(k in Q) (h_k-beta_k) >= 112-COST.
```

Indeed `112 <= sum h_k = COST + sum(h_k-beta_k)`, and every local term has
nonpositive excess. Thus COST≤64 needs nonlocal frame excess at least **48**;
COST<64 needs at least **49**, because the costs and hit counts are integers.
This is a necessary resource budget, not a sufficient construction criterion.

It is sharp at the existing coordinate decoder: its eight supports each meet
14 four-frames and have pairing rank8, so its total excess is `8*(14-8)=48`
and its total cost64. The checker reconstructs this familiar decoder as a
**negative control to locality**, not as a new construction.

In the separately charged child model, for `0<q<=1`, the local alphabet obeys

```
sum beta_k^q >= 112 * 4^(q-1).
```

This follows termwise from beta≤4 and q−1≤0. Compared with the existing eight
rank-eight copies, the lower-bound ratio is `3.5/2^q >= 7/4`. Normalization by
width `m^q` cancels. The effective child rank in this alphabet is at most four;
overcompleteness cannot turn these tetrad-local terms into rank-eight or
rank-sixteen delivery. This is a lower bound, not an exact optimum of the
power bill, nor a statement about coherent shared-copy pricing.

There is also an immediate **conditional retained-coverage screen**. If a
replacement keeps width73, roles-per-call `w=896/9`, and the selected coverage
law `paid_mass=72w+c` with centre charge `c=sum beta_k`, then even the minimum
c=112 gives

```
D = w-c = -112/9;
M(0) = (72w+112)/(73w) = 585/584 > 1.
```

For children of rank at most width and nonnegative saving a, every normalized
moment term `(r/73)^(1-a)` is at least r/73. No complete profile under that law
can pass, even before charging extra frames or restoration. Thus no synthesis
or claimed full invoice is needed to reject this route. A different coverage
law, family count, shared-copy rule, or cross-block alphabet is outside this
screen and requires its own fully charged analysis.

## Reproduce and finite coverage

From the repository root, Python3.12, standard library only:

```sh
python3.12 -I -B research/p112-tetrad-local-decoder/verify.py --json
python3.12 scripts/research_package.py --package research/p112-tetrad-local-decoder
```

`uv run --python 3.12 --no-project` can replace `python3.12`. Expected final
checker marker:

```
PASS_P112_TETRAD_LOCAL_DECODER blocks=14 classes=28 supports=917504 copy_floor=112 rank_cap=4 masked_terms=56 escape=48 moment0=585/584 controls=6
```

The verifier independently builds all120 roots, checks all14 blocks and28
classes, and exhausts **917,504** pairs of within-block actual supports
(14 times 256 squared), including empty cases. Extra opposite-side columns
cannot decrease the checked minor rank, which is the written bridge to
arbitrary opposite supports. It verifies all entries of the masked identity,
the all-pairs attainment, and the coordinate control. All arithmetic is integer
or rational; the complex-cancellation control uses separate integer real and
imaginary arrays. Six controls cover removal of locality, complex cancelling
splits, transposed locality, free terms, deletion of an essential term, and
removal of the diagonal target. Runtime evidence belongs to the replay receipt,
not to an asymptotic multiplication-speed claim. Assertions are not used.

## Open next questions

1. Which unions of two tetrads first permit positive frame excess? Enumerate
   actual support-pair witnesses on each relative pair of blocks and measure
   h−beta. This identifies the smallest locality change that can evade the
   certificate; the opposite support is unbounded, so an efficient exact
   reduction of its possible pairing patterns is needed.
2. Can a nonlocal decoder with excess at least49 realize COST<64? Start from
   the coordinate decoder's tight excess48 and alter one explicit support
   family. Rank demand alone is insufficient: coefficients must satisfy the
   masked identity and physical frame/restoration costs must be paid.

Structured versions are in TASK.json. The result is a written scoped theorem
with finite geometric checks, not a formal proof of integer multiplication.

## Sources, overlap, and credit

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
SOURCES.json pins the geometry, predecessor proof, and coverage references.

Credit DreamingOfClouds / PR717 for the B14 decoder model; the
[frame-pair decoder](../complex-frame-pair-decoders/README.md) and
[rank-eight rigidity](../complex-rank8-decoder-rigidity/README.md) authors for
geometry and prior eight-term results; Aaron Wang / Navinor, PR1226
(`8b10989e4e45f0f9ce41004d7898a21a32f87e11`), and
[masked-root-star-assembly](../masked-root-star-assembly/PROOF.md) for frame-rank
demand arguments; and PR1012 / the local-word-ceiling authors for the retained
coverage screen. No predecessor code is copied or imported.

Closest distinct live scopes inspected: [PR1633](https://github.com/CrocSwap/integer-mult-bounds/pull/1633)
(head `652264fa1f70820139b2730363a0056b7fadc689`) concerns outside-root-code ranks
of all-pairs overcomplete decoders; [PR1866](https://github.com/CrocSwap/integer-mult-bounds/pull/1866)
(head `7d22d1d51eb6c0bc040f8181b6c5f83e051fb234`) constructs a mixed rank-six
bilinear block. Neither is an input theorem here. The root-star predecessor
allows whole stars and has floor64; this package allows arbitrary one-sided
subsets of a single tetrad and proves floor112 plus an explicit nonlocal escape
budget. The two support alphabets are different, not competing universal floors.

The final cached overlap check at 2026-10-14T13:42:34Z covered543 open PRs
including drafts, completely paginated at13:23:53Z, and529 discussion records
at13:25:07Z. Targeted queries `tetrad-local`, `tetrad local`, `one-sided tetrad`,
and `frame excess` matched only this package's local README and TASK. Earlier
card-wide queries found129 possible overlaps. Targeted live PR checks confirmed
the heads cited above immediately before publication. Coverage excludes
arbitrary diffs/nested files and closed work absent from local notes; no-match
is not a novelty certificate. Parent coordination claim:
[discussion1884](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884).

Prepared for Adam Gall with substantial **OpenAI Codex assistance** in scope,
proof, implementation, and documentation. Apache-2.0. No changes to frozen
sources, selected evidence, shared indexes, or workflows.
