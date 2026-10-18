# Two-coordinate GL3 mixing: the three-product branch cannot improve COPY cost

**Structural decoder research / scoped negative result; no new kappa.** In the
fixed P112 model, mix coordinate terms 4 and 6 with one nonzero free odd
rectangle through an arbitrary GL(3,C) factor change. If all three replacement
terms have nonzero original-coordinate projections on both sides, each costs
at least **six COPY ranks**, and the whole decoder costs at least **66** versus
the original **64**. Fully dense original-coordinate coefficients give at
least eight per replacement and a whole-decoder floor of **72**.

This addresses a larger coupled branch than Arham Tahir's pending
[PR1331](https://github.com/CrocSwap/integer-mult-bounds/pull/1331), which mixes
one original term through GL(2,C). It does **not** settle all two-coordinate
GL3 mixing. The exactly-two-product boundary remains open here. No new
physical supplier or selected-frontier change is proposed.

Concurrent work discovered in the final refresh is acknowledged explicitly:
commdata2338's [GL3 singleton claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1316#discussioncomment-18911259)
aims to settle all branches and all 28 coordinate pairs for singleton corrections;
Arham Tahir's [rank-nine singleton claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1360)
allows all nine factor terms to change. This result covers arbitrary free
rectangles rather than singleton corrections, but only one pair and the
three-product branch. Their claims are not assumed proved or used as theorem
dependencies. The additional rectangle coverage and 6/7/8 survivor table are
the independently reproducible contribution here.

## Exact mechanism and optimistic price

Let x and y be columns 4 and 6 of the pinned 112-by-8 coordinate matrix X.
Choose nonzero complex vectors u,v with binary pairing matrix
`B[supp(u),supp(v)]=0`. The rectangle `uv^T` is therefore free on the constrained
even entries. For arbitrary nonsingular M, set

```text
D = [x,y,u] M,       S = [x,y,v] M^(-T).
D S^T = xx^T + yy^T + uv^T.
```

Transpose is ordinary, without conjugation. Write q_j,p_j for the first two
coordinates of columns j of M and M^(-T). The investigated branch requires
`q_j != 0` and `p_j != 0` for all three j. Coefficients may be complex and
u,v may have arbitrary supports satisfying the free-rectangle condition.

The other six original coordinate terms each retain cost eight. Before
implementing gathering, frame changes, source access, mixing, restoration,
hosting or recursive children, grant **all those expenses zero**. The two
original COPY terms cost `2*(8/m)^q`; their three replacements still cost at
least `3*(6/m)^q`, where `0<q=1-a<=1` and m/normalization are unchanged.
The replacement ratio is at least **9/8**, and the whole decoder's COPY power
bill is at least **33/32** of the original. Nonnegative additional charges
cannot rescue this branch. This is a favorable cost screen, not a completed
physical invoice or a universal limit on other stages or architectures.

## Finite premise and quantified proof

A nonzero complex normal on the two original coordinates has exactly one of
five support classes: either axis, equal coefficients, opposite coefficients,
or the remaining nonzero ratios. Representatives are
`(1,0),(0,1),(1,1),(1,-1),(1,2)`; their support sizes are 56,56,76,76,88.

For each ordered live-port pair `(i,j)` with `B_ij=0`, price the pairing between
`support(q) intersect even-neighbors(j)` and
`support(p) intersect even-neighbors(i)`. There are **5,824** such port pairs
and **145,600** class-and-pair records. Complete exact enumeration gives:

| Original coordinates present on left | Present on right | Minimum survivor pairing rank |
| ---: | ---: | ---: |
| 1 | 1 | 6 |
| 1 | 2 | 7 |
| 2 | 1 | 7 |
| 2 | 2 | 8 |

These are exact minima for the finite survivor premise, not asserted sharp
minima for the full GL3 decoder. An independent implementation uses the
nine-bit labels/duals and a different elimination direction; the primary
checker reconstructs the Euclidean roots and uses 112-column binary matrices.
Their entire transcripts, 25 histograms, witnesses and slice dimensions agree.

The [written proof](PROOF.md) uses one port in each nonempty rectangle support.
Every pairing-one survivor against that port lies outside the opposite support,
so it survives every possible cancellation in a mixed factor. Rank monotonicity
then extends the finite premise to all complex M,u,v in the stated branch.
`sum q_j p_j^T=I_2` forces at least two nonzero projected products. Therefore any
improving candidate with a nonzero rectangle must lie in the **exactly-two**
branch; a blind search of fully dense mixing cannot help.

## Reproduce

Python 3.12, Git with the pinned base object, and the standard library:

```sh
python3 -I -B research/p112-gl3-survivors-seed46/verify.py
```

Expected final line:

```text
PASS_P112_GL3_S46 records=145600 floor=66 power_ratio_floor=9/8 controls=10 no_new_kappa
```

The command checks exact source hashes/Git blobs, the geometry and label
factorization, both complete rank censuses, four Q(i) factor identities over
all 12,544 entries each, ten controls, and the committed certificate.
`--check FILE` checks an alternate receipt; `--write-certificate` explicitly
regenerates only this package's receipt. Checks use explicit exceptions and
remain active under optimization. Registered replay is
`python3 -B scripts/research_package.py --package research/p112-gl3-survivors-seed46`.

Two concrete boundary controls explain essential hypotheses. With M=I and a
nonzero free rectangle the costs are `(8,8,0)`: the third projected product
vanishes. A different nonsingular M has three nonzero projected products but
u=0 and v=x; its costs are again `(8,8,0)`. Neither satisfies this theorem's
full hypotheses. Further controls cover a nonfree diagonal, singular M,
conjugation, a false rank-seven floor, missing coverage, the wrong generic
support, an out-of-range power and a corrupt source pin.

## Provenance, coverage and scope

OS assignment seed **46**, structural decoder track; it selects pair `(4,6)`.
Exact base: **bce54fb3f895cbe5cd4c0eb477c3afeed100190f**. Its selected conditional
kappa is 0.001672660197076918, PR1094 with PR589/555 on the bit side. The actual
model input is Mihir Srivastava's retained PR845 geometry, derived from
DreamingOfClouds' PR717 at 4150829a2cb66b823f4282da98985959ee448a90.
`SOURCES.json` pins input bytes and Git blobs; `PREDECESSORS.json` records exact
pending-source heads read for overlap and credit. No pending checker is imported.

The completed domain is the fixed pair, all 25 support-class combinations and
all 5,824 ordered zero-pairing port pairs. Exhaustion is the stopping rule;
there is no random or heuristic search. The complex reduction and containment
argument carry the unbounded coefficients/supports, not extrapolation from
fixtures. Finite census and fixtures are not formal theorem verification.

Inherited separate-total gathering and COPY-tree interpretation, compiler,
frames, hosting, precision, analytic and full-supplier obligations remain.
Neither a full supplier replay nor physical admission is claimed. Other
coordinate pairs, zero rectangles, exactly-two projected products, changed
normalization, correlated gathering and arbitrary masked decoders are outside
this result. The whole-decoder floors are lower bounds, not global optima.

## Open next questions

Resolve the exactly-two projected-product branch for this same pair and free
rectangle. It is the only remaining branch with a nonzero correction that can
improve the unchanged COPY bill. Start by using `sum q_j p_j^T=I_2` to classify
the vanishing column projection, derive its complete support/cost identity,
and test that identity on arbitrary dirty inputs before searching. The current
survivor proof does not price a term with a zero original-coordinate projection;
no such replacement construction or complete invoice is supplied.

## Attribution

Cinna Davis (@1337isnot1337), with substantial OpenAI Codex assistance in task
selection, proof, implementation, checking and documentation; Apache-2.0.
Credit Arham Tahir/PR1331 for the one-rectangle GL2 predecessor and survivor
containment method; Mihir Srivastava/PR845 for exact P112 geometry and the
single-lift floor; DreamingOfClouds/PR717/446 for the masked model and accounting;
Joel Pulikkan/GamingPuzzled/PR620 for the coordinate cost 64; and the retained
pairing-cost lineage. PR1327's two-sided parity-lift family and PR1325's fixed
single-lift normal are distinct. No independent human or proof-assistant review
is claimed, and prior results are not claimed anew.
