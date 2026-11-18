# Sharp rank cost for a fixed binary stage factor

Let `A` be an `n × n` matrix over `F₂`. Seek `B,C` with prescribed
determinant valuations `b,c` such that

```text
(I+xA)(I+xB)(I+xC) = (1+x)I.
```

The valuation of `M` is the multiplicity of `1+x` in `det(I+xM)`.
A completion exists exactly when `A³=A²` and `b,c` are nonnegative
integers with `b+c=n-rank(A²)`. Write `r=rank(A+A²)`. For each such
split the exact minimum rank sum is

```text
n + r + max(0,r-b) + max(0,r-c).
```

The construction attains `rank(B)=max(b,r)` and `rank(C)=max(c,r)`
simultaneously. In particular both companions can be idempotent exactly
when `b,c ≥ r`. This is a scoped proof for the formal stage identity over
`F₂` in every positive dimension.

## Proof

Write `F_M=I+xM`. Comparing coefficients in `F_A(F_BF_C)=(1+x)I`
gives `B+C=I+A`, `BC=A(B+C)=A+A²`, and `ABC=0`. The last two equations
give `A³=A²`. Each factor is invertible over `F₂(x)` because its
determinant has constant term one. Since the target is scalar, cyclic
rotation preserves it. The same cubic condition therefore holds for
`B` and for `C`.

For each successful factor `M`, `P=M²` is idempotent and commutes with
`M`. On `im P`, `M` acts as the identity because `MP=P`. On `ker P`,
its restriction squares to zero. Choose a basis of its image there, lift
each basis vector to a preimage, and complete the image basis to a basis
of the kernel of that restriction. This gives one block of the following
form for each unit of `rank(M+M²)`, along with zero and identity
singletons.

```text
N = [0 1]
    [0 0]
```

Each `N` contributes one to the ordinary rank and zero to the valuation.
Each identity singleton contributes one to both. Thus the valuation of
`M` is `rank(M²)` and its rank is
`rank(M²)+rank(M+M²)`. Multiplying determinants gives
`rank(A²)+b+c=n`.

The identity `BC=A+A²` gives `rank(B),rank(C) ≥ r`. Their valuations
also lower-bound their ranks. With `p=rank(A²)`, this gives the lower
bound `p+r+max(b,r)+max(c,r)`, which equals the claimed sum.

### Attainment

In the split basis for `A`, use `B=C=0` on every identity singleton.
On each zero singleton of `A`, use `(B,C)=(1,0)` or `(0,1)`.
On an `N` block choose one of the following ordered companions. Here
`Eᵢⱼ` has its one in row `i`, column `j`, with indices starting at one.

| `B` | `C` | Valuations `(b,c)` on the block | Ranks `(rank B,rank C)` |
|---|---|---|---|
| `E₁₁` | `E₂₂+N` | `(1,1)` | `(1,1)` |
| `N` | `I₂` | `(0,2)` | `(1,2)` |
| `I₂` | `N` | `(2,0)` | `(2,1)` |

The first row has `B+C=I₂+N` and `BC=N`, so
`F_BF_C=(1+x)F_N`. The other two rows give the same product directly.
In all three rows `F_N²=I₂`.

There are `r` such blocks and `l=n-p-2r` zero singletons. Start with the
first row on every block. If `b<r`, change `r-b` blocks to the second
row and assign all zero singletons to `C`. If `c<r`, change `r-c`
blocks to the third row and assign all zero singletons to `B`. The two
cases cannot coincide because `b+c=2r+l`. Otherwise assign
`b-r` zero singletons to `B` and the rest to `C`. The resulting ranks
are the stated minima. Conjugating all three factors by the same basis
change returns a completion for the original `A`.

## Evidence and reproduction

Use CPython 3.12.15 and the standard library, from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/paired-star-factor-rank
python3.12 -B scripts/check_research_commit.py --package research/paired-star-factor-rank --check-source-history
python3.12 -I -B -W error -X dev research/paired-star-factor-rank/verify.py
python3.12 -I -O -B -W error -X dev research/paired-star-factor-rank/verify.py
```

Both registered modes report:

```text
PASS_PAIRED_STAR_FACTOR_RANK pairs=232576 fibers=345 witnesses=930 controls=1
```

The enumeration tries every middle matrix for every non-idempotent leading
matrix through dimension three. It forces `C=I+A+B`, multiplies the
polynomial in order, and compares the observed minimum in every valuation
fiber with the formula. It checks 930 block witnesses across every
admissible signature and valuation split through
dimension ten. Reversing the companion order on the shared two-dimensional
block must fail. The proof gives the unrestricted dimension claim.

The `joint-query-controller` card changes scope to an algebraic rank
requirement for the paired-star stage. The complete physical price also
depends on preparation, storage, restoration, native alignment and how the
recursive caller uses each rank. Those obligations and the full selected
replay remain open for this construction. The selected conditional saving
remains `363005817/100000000000`.

## Open next questions

- Which attaining companion pairs can be realized in a paired-star caller
  without a separate paid change of basis? Start with one two-dimensional
  shared block on a named stage. Identify its physical frames and check
  restoration before pricing the complete caller.
- Which even valuation splits remain attainable when all three factors must
  commute with the stage operator `T`? Begin by imposing the commutant equations on
  the two-dimensional block lifted to one paired-star stage. That constraint
  can forbid block choices used here.

## Credit

This result was produced by Nick Petalas. Unpaidmoon's example contains
the shared two-dimensional block used in the attainment proof. The example
and the paired-star setting are in [PR #7027](https://github.com/CrocSwap/integer-mult-bounds/pull/7027)
at `1ba2ac5adfe58fbe9dba34d50d4e5d30633ce3d0` and its
[pinned proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/1ba2ac5adfe58fbe9dba34d50d4e5d30633ce3d0/research/paired-star-valuation-one-factor/PROOF.md).
Ali Romman's related idempotent-leading classification is in
[PR #7706](https://github.com/CrocSwap/integer-mult-bounds/pull/7706)
at `79ff656972d66915977e816b23ffdcef42fb0e12`. Credit Ali Romman for the
paired-star model in [PR #5747](https://github.com/CrocSwap/integer-mult-bounds/pull/5747)
and its credited predecessors.
