# No two S3 target maps share a paid call in the transposition model

**Exact two-register bound in one finite nonabelian relaxation; no new κ.**
For every ordered pair `g,h ∈ S₃`, the exact dirty-register target
`diag([g],[h])` in `F₂[S₃]` requires exactly
`|g|_{x,y} + |h|_{x,y}` paid calls when the only address labels are
`x=(12)` and `y=(23)`. Here `|·|_{x,y}` is shortest word length in those two
transpositions. Rank-one scalar mixing cannot share a paid call between the
two targets in this model. This does not establish a bound for the retained
rational-frame supplier and does not change the selected κ. The source-bound
baseline replayed for this cycle reports the complex primitive as binding.

The exact census covers all 36 ordered target pairs. Their minimum-call
histogram is `{0:1, 1:4, 2:8, 3:10, 4:8, 5:4, 6:1}`, equal to the histogram of
the separate direct bills. In particular, the inverse 3-cycle pair
`diag([xy],[yx])` costs four calls, and the pair of longest Coxeter elements
`diag([xyx],[xyx])` costs six.

## Model and complete cost

The group elements are all six permutations of three points, with products
composed right-to-left. Paid labels are only `x=(12)` and `y=(23)`. A paid
factor is `I + ([s]+[1])N`, where `N=u vᵀ` is a rank-one idempotent in
`M₂(F₂)`. There are exactly six such idempotents (`u,v` nonzero and
`vᵀu=1`), giving twelve paid generators. Each call costs one.

Both endpoint registers contain arbitrary dirty data. The target is exactly
diagonal, so both off-diagonal group-algebra entries must vanish. There is no
extra register, COPY, erasure, clean state or free address map. Free scalar
`GL₂(F₂)` mixing is included: push each free map through a paid factor by
conjugating `N`; augmentation sends every paid factor to the identity, forcing
the residual scalar map to be the identity. The twelve-generator alphabet
therefore covers all normalized words.

For each pair `(g,h)`, separate shortest transposition words give an exact
upper bound of at most six calls. Any strict saving must lie in the radius-five
ball. The exact search enumerates that complete ball, and its minimum for every
pair equals the direct bill. The radius-five ball has layer sizes
`1, 12, 80, 466, 2,345, 10,760`, for 13,664 distinct formal products. The
unique maximum-cost pair `(xyx,xyx)` is absent through length five and has its
six-call direct word, so the same search certifies its exact lower bound.

## Exact evidence and reproduction

`verify.py` enumerates the complete radius-five ball in six-coefficient
`F₂[S₃]` matrix form. It checks the group table, all twelve paid generators,
and exact direct words for all 36 targets. A separate literal matrix-product
implementation checks all 1,885 ordered words of lengths zero through three
and replays every one of the 13,664 canonical search paths. Each of 108
single-factor omissions from the direct words fails its target equality. These
formal coefficient equalities cover arbitrary dirty inputs; this is not a
finite-address representation test.

Reproduce from the repository root:

```sh
python3 -I -B research/bit-s3-two-target-census-seed36501/verify.py
python3 scripts/research_package.py --package research/bit-s3-two-target-census-seed36501 --check-only
```

Expected first line:

```text
PASS_S3_TWO_TARGET_NO_SHARING layers=[1, 12, 80, 466, 2345, 10760] pairs=36 minima={'0': 1, '1': 4, '2': 8, '3': 10, '4': 8, '5': 4, '6': 1} sha256=7923043c2764ca3ea6675d0f2ea01866f8a25401e11f10c6a928004b685a62d6
```

Local direct and optimized verifier replays pass under Python 3.14.7. Python
3.12 is not installed here, so the registered generic package replay could not
run locally; metadata and source-pin validation passed. `SOURCES.json` records
the exact base commit, selected record, task catalogue, review, selected source
manifest, assembly certificate and D8 predecessor README pins.

## Limits

This result is exact only for two registers, all 36 diagonal target pairs in
`S₃`, the two specified transposition labels, and the stated rank-one
idempotent factors. It does not cover more registers, another group or label
set, arbitrary rational address frames, physical hosting or precision, or the
recursive paid profile. No selected supplier adoption or new κ is claimed.

## Open next questions

Does a third arbitrary dirty register permit a shared-call saving for a fixed
S3 target triple, such as `diag([xyx],[xyx],1)` in the same transposition
alphabet? This would test whether the two-register no-sharing result depends on
role count. First enumerate the 56 rank-one-idempotent generators for three
registers and measure exact radius-four state growth for that target before
searching deeper. The 56-generator ball may grow quickly; the current
two-register census gives no bound for the expanded role model.

## Credit

This is an independent exact group-algebra search. The nearby D8
central-commutator result in `research/bit-dihedral-commutator/README.md`
motivated testing a different finite group and target family; no predecessor
code is imported. Prepared by Cinna Davis with substantial OpenAI Codex
assistance. Apache-2.0.
