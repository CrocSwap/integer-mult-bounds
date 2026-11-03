# Exact conjugation tariff for separate real and imaginary frames

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. For every
positive n and real orthogonal n-by-n P,Q, the exact number of single-coordinate
conjugations required for

```text
T(x+iy) = Px+iQy
```

is **rank(P-Q)** when arbitrary invertible complex-linear frames are free.
Any finite number of exactly restored arbitrary dirty complex coordinates
leaves this minimum unchanged. For rational P,Q, an explicit attaining
compiler uses rational real frames and no square roots.

[PROOF.md](PROOF.md) proves the all-size statement, its dirty-workspace lower
bound and the rational construction. [verify.py](verify.py) implements that
construction and a separate full real-matrix interpreter. This is a changed
provider alphabet, rather than a new native supplier or a kappa improvement.

The lower bound records the rank of the antilinear part of the complete map.
Each paid conjugation increases it by at most one, while every free frame has
zero antilinear part. Classical rank-tight Householder factorization attains
the resulting bound. Those ingredients are credited below; the new scoped
contribution is their exact tariff and explicit rational interface here.

For example, P=I and Q=[[3/5,-4/5],[4/5,3/5]] need exactly two conjugations,
even with dirty workspace and arbitrary complex-linear mixing. This excludes
one-call realification of that pair. Positive real determinant alone would
not exclude it. Conversely, the free map z->iz has real displacement rank two
but needs no conjugation, so ordinary displacement rank is not this tariff.

## Reproduce

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/real-imaginary-conjugation-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/real-imaginary-conjugation-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/real-imaginary-conjugation-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/real-imaginary-conjugation-tariff --check-source-history
```

Another CPython 3.12 path may replace the absolute interpreter. The direct
commands print `PASS_REAL_IMAGINARY_CONJUGATION_TARIFF` inside generated JSON
stdout receipts bound to every package file hash. They write no files. The
registered and publication checks print `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES` respectively.

The finite corpus contains:

- All 2,372 ordered pairs of signed permutation matrices in dimensions one,
  two and three, and all 384 dimension-four targets with P=I.
- 162 parameterized rational fixtures in dimensions one through six, with
  zero, one or two arbitrary dirty complex coordinates. These fixtures may
  repeat a matrix pair; no distinct-pair count is claimed.
- Three dimension/coefficient boundary fixtures, including dimension eight
  and a reflection with 253-bit rational coefficients.
- 124,532 full real endpoint entries across those 2,921 program fixtures,
  covering 22,136 emitted instructions. Every prefix obeys its antilinear
  call bound. A separate 64-entry fixture transiently mixes active data and
  dirty coordinates using a nonreal complex-linear shear and restores them.
- All 781 words of length zero through four over two conjugations and three
  complex-linear generators. A separately evaluated 2-by-2 Gaussian
  determinant agrees with the full real antilinear-rank oracle.
- Twelve rejected cases: nine malformed or unsupported compiler inputs and
  three actual endpoint corruptions, omitting a call, flipping a real part
  instead of an imaginary part, and reversing instruction order.

The rank oracles use independent elimination implementations. Complete real
matrix identities establish arbitrary-input endpoints for each finite
fixture; they do not extrapolate the theorem. Normal and optimized receipts
must agree. The first complete local corpus ran in about five seconds on
CPython 3.12.15, macOS 27.0.1 arm64. This is a replay duration, not a speedup.

## Scope and current bottleneck

The complex-new-helper-inventory card is explicitly changed to a real-linear
interface side result. The selected source-binding positive control passed
at canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The selected record is PR6030, kappa 0.003125804; older values in priority prose
do not replace that record. [TASK.json](TASK.json) retains the complete card.

A different real/imaginary frame cannot be supplied by complex-linear frames
alone when P differs from Q. The theorem gives the exact remaining conjugation
resource in this generous relaxation. It supplies no actual P104 cut, productive
target or favorable complete recursive bill. Free frames are an accounting
assumption, not a claim that physical basis work is free. The rational compiler
can use odd denominators. A native or dyadic installation needs its own
coefficient, scalar, access, lifetime and restoration argument.

The logical identity, exact call tariff and rational frame constructor are
proved. Native conjugation delivery, physical basis costs, chronology, owned
storage, independent Gaussian targets, precision/tape, stock, uniform supplier
compilation and outer funding are unknown here. No selected cold replay,
predecessor scientific replay, Lean, Docker, native realization or rounded
multiplier was run. All five selected framework assumptions remain. Independent
human and formal proof-kernel review are unclaimed.

[The advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19376836)
preceded substantial work. Live open/account PRs, recent handoffs, active
Discussions, local reservations, general-form and distinctive main README
searches, and merged PR searches were checked. The broader cache covered 141
of 8,917 local note records, so it was supplemented by main-tree searches.
These checks do not cover unpublished work or arbitrary historical diffs.
No contributor's package or scientific checker is imported by the result.

## Open next questions

1. Can one actual complex supplier use separate real and imaginary frames at
   a favorable complete bill? First name its literal producer and consumer,
   and charge every basis, conjugation, return and target change. No native
   delivery or full signed invoice is supplied here.
2. Which rational frame pairs admit an attaining program in a required
   physical coefficient ring? Fix that ring and examine the displayed bases
   for one reached pair. Rational frames may have odd denominators.

Structured versions, first steps and blockers are in [TASK.json](TASK.json).
The first exact tariff is shipped without classifying more general real-linear
maps or expanding into physical supplier construction.

## Credit and executable bounds

Antilinear decomposition and rank subadditivity are classical. The
Cartan-Dieudonne-Scherk reflection method is classical; see
[Rodriguez-Andrade, Aragon-Gonzalez, Aragon and Verde-Star, 2010](https://arxiv.org/abs/1011.1027)
for constructive factorization context. The needed positive-definite reduction
is proved explicitly in PROOF.md. No external code or proof text is copied,
and no general literature-priority claim is made. Repository predecessors and
their credit lines are unchanged.

The public compiler accepts dimensions one through eight and integer/Fraction
entries of at most 256 bits. Matrix-product outputs are guarded at 4,096 bits;
exceeding an executable bound raises an error, not a mathematical impossibility.
The written rational construction has no such limits. [CODE-BOUNDS.md](CODE-BOUNDS.md)
records loop bounds, allocation deviations and diagnostics.
