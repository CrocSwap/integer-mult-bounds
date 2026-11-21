# P104 tight B-linear decoder: independent reduction and certificate audit

## Status and scope

This audit concerns [PR #7852](https://github.com/CrocSwap/integer-mult-bounds/pull/7852)
at the **starting head** `41beda1d6435760dc99e38bd7e65f36798aad212`, specifically
`research/p104-lowerbound-toolkit/drat`. The original package and its 1,001
reported cube outcomes are by DreamingOfClouds, with Claude Opus 5.5 as stated
in the package. The checks and arguments below are an independent Codex audit;
they are not claims that its authors or maintainers have accepted this audit.

We independently checked the pinned reduction data, actual CNF blocks and cube
partition. A direct covering contradiction eliminates **612 of the 1,001
cubes** without a solver; `residual-cubes.tsv` lists the remaining 389, for
which this particular contradiction is absent. We also independently reran
**one cube**, `f3591` (already among those 612), with a new PicoSAT proof and
two checkers, including the small Python RUP checker in this directory. We give
a solver-free no-cover result for the subdomain where every `dim U_z <= 3`.
We have **not** independently refuted all 389 residual cubes, and the author's
1,001 historical proof files are not in the package.
This does not establish the complete budget-55 UNSAT claim, the general decoder
wall, a legal-word bound, a hosted-rise bound, or a kappa result.

## Reproduce

Run these from this directory with Python 3 and the copied pinned source data:
The full bundle includes the DIMACS cube; the compact bundle omits that file.
`prepare_cube.py` checks the pinned inputs, regenerates the cube if missing,
and verifies its full SHA-256 before the proof checker uses it.

```sh
python3 -B prepare_cube.py
python3 -B verify_artifacts.py
python3 -B verify_bridge.py
python3 -B verify_z4_cover.py
python3 -B verify_fidelity.py
python3 -B verify_symmetry.py
python3 -B verify_coverage.py
python3 -B verify_cover_eliminations.py
python3 -B verify_small_dim.py
python3 -B check_rup.py picosat/f3591.cnf picosat/f3591-core.cnf picosat/f3591-core.drat
python3 -B verify_controls.py
```

Results: 104/104 per-port orthogonal ranks are 7; all 16 price hyperplanes
check; all 65,536 Z/4 characters and 17,152 stored cover clauses check; the
only nonzero tight vectors are the 32 signed normals; all 472,977 base CNF
clauses and 121,916 variable roles match the independently reconstructed
component specifications; all 384 symmetries check; the 1,001 cube boxes
cover every admissible lex-constrained inactive set; 612 cube IDs have a
direct covering contradiction and 389 remain outside this test; and the Python checker
accepts 235 RUP additions, ending in the empty clause, on 1,680 clauses that it
finds in the 473,009-clause full cube. Flipping the first proof lemma causes
the Python checker to reject at addition 1.

The local source copy is read-only in purpose; no upstream files were changed.
The necessary original generator inputs are included in `source/drat`. They
may also be acquired from the [exact pinned upstream tree](https://github.com/CrocSwap/integer-mult-bounds/tree/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/drat);
`verify_artifacts.py` checks their SHA-256 values, regenerates `f3591`, and
compares the result with both the local CNF and the pinned historical row.
Notable Git blob pins from that exact head are:

| Source | Git blob SHA-1 |
| --- | --- |
| `drat/gen.py` | `af963b70b83f2f77edc6f18ab7a8de6396725f69` |
| `drat/cubes.txt` | `8352098e82cf4e1f8e801110adc89aca45b7d588` |
| `drat/data/e8base.json` | `7aea7de0288fa36ccd4b8b42071a594653c8ab96` |
| `drat/data/labels.txt` | `b31007d44411e1a788d5f2c8339ef2ea390c3007` |
| `drat/data/perms.json` | `21e47dcb0540b044d5133ea3a69c1111263284ca` |
| `drat/data/zclauses.json` | `7c4f5d8f196b3467ede7b826e7dd06501600c2fb` |
| `drat/hashes.tsv` | `c5abe78b578f33409d50a2ae1837f27d96c57c66` |

The source checker verifies finite facts, not a formal proof assistant theorem.
The derivations below explain the checked facts' mathematical consequences.

## Decoder to the covering relaxation

The following argument assumes exactly the tight B-linear half-integer class
described in the PR: each linear-side row is the balanced representative in
`{0,+1,-1}` of a Z/4-linear functional on the given port coordinates, and the
other side has half-integer entries. The decoder matrix has diagonal 1 and is
zero on distinct port pairs where the P104 parity matrix `Q` is 1. A row's
price is the F2-rank of `Q` restricted to the supports of the two row factors.

Let `c_t` be the first 104 integer vectors in the pinned E8-coordinate data,
`z` the final 16, and let `<x,y> = x^T G y`. The check proves that all 120
have norm 2, their distinct pairings are 0 or +/-1, `G` is nonsingular mod 2,
and the 104 coordinates have rank 8 mod 2. It also checks the claimed Q:
`Q_ts = 1 + <c_t,c_s> (mod 2)`. The nonsingularity mod 2 makes the pairing
nondegenerate over Q and over Z/4.

Every Z/4-linear functional is pairing with some vector `a in (Z/4)^8`.
The exhaustive check `verify_z4_cover.py` establishes that a nonzero such
vector has no forbidden value 2 on the 104 ports if and only if `a=+/-z` for
one of the 16 listed normals. For each such z the balanced values are exactly
the *integer* pairings `<z,c_s>`, because the norms and off-diagonal pairings
were checked. A zero row can be dropped. Rows with the same z up to sign can
be merged by adding or subtracting their other factors. Their new support is
contained in the union of the old supports, and restricted-matrix rank is
subadditive under row-set union, so merging cannot increase total price.
Consequently at most 16 indexed rows suffice.

For the merged decoder, write `M_ts = sum_z w_tz <z,c_s>` and let
`a_t = sum_z w_tz z` over Q. For each t the check finds rank 7 over F2 for
the other `c_s` with `<c_t,c_s>=0`; an odd 7-minor gives rank at least 7 over
Q, and orthogonality to nonzero `c_t` gives at most 7. Therefore they span
`c_t`'s rational orthogonal complement. The decoder zeros put `a_t` in its
orthogonal complement, so `a_t = lambda_t c_t`. The diagonal gives
`1=<a_t,c_t>=2 lambda_t`, hence

```text
M_ts = <c_t,c_s>/2,      c_t = sum_z (2 w_tz) z  in Z^8.
```

This supplies the Gram-form bridge directly for this class. Reducing the
integer relation modulo 4 proves that for every port t, `c_t` belongs to the
Z/4 span of those z whose other-side coefficient at t is nonzero. For a test
vector x, if `<x,c_t> != 0 (mod 4)`, then at least one selected z has
`<x,z> != 0 (mod 4)`. Thus the corresponding positive row-support clause is
necessary. Conversely, all such clauses characterize Z/4 span membership:
characters of the finite exponent-4 quotient separate any element outside a
subgroup, and the nonsingular pairing represents all such characters. This
last equivalence is only for the **mod-4 cover**, not for the original exact
decoder identity.

`verify_z4_cover.py` recomputes the 17,152 inclusion-minimal stored clauses by
a separate 2^16 bitset subset-closure algorithm. It verifies that every one of
65,536 characters' port obstructions has a stored subset, that every stored
port/mask pair has an exact character witness, and that no stored clause has
a smaller stored clause. This differs from the original checker's per-port
minimal-mask construction.

Let `h_t=(1,c_t mod 2)`, `n_z=(1,z mod 2)`, and `beta` be the orthogonal sum
of the first-coordinate form and `G mod 2`. Let `S_z` be the support of the
linear row, and let `U_z` be the F2 span of those `h_t` at which `w_tz != 0`.
The checks show `span{h_s:s in S_z}` has dimension 8 and beta-orthogonal
complement `<n_z>`. Thus the actual price of row z is

```text
dim U_z - 1[n_z in U_z].
```

The CNF permits arbitrary `U_z` containing the actual support labels. This
is a relaxation: enlargement can only increase the restricted Q rank. Its
cover is a necessary condition, and satisfying the cover need not reconstruct
half-integer W satisfying the exact integer relation or decoder identity.

## CNF fidelity and its two directions

Set `d_z=dim(U_z^perp)`. Ordered flags `used[z,i]` encode `i<d_z`; the other
row bits encode the unique RREF basis of `U_z^perp`. The row clauses enforce
prefix flags, exactly one increasing pivot in each active row, zero inactive
rows, and zeros in every other row's pivot column. Every subspace has such an
RREF, and every satisfying row block is such an RREF. XOR clauses exactly
encode parity. Membership flags are **one-way**: `m[z,t] -> h_t in U_z` and
`nin[z] -> n_z in U_z`; they need not be true for every actual membership.
`verify_fidelity.py` independently reconstructs every actual row, XOR,
membership, covering and totalizer clause and verifies variable freshness;
`verify_coverage.py` separately checks the exact lex blocks. Small instances
of the RREF, XOR, lex and totalizer projections are exhaustively tested.

If a model satisfies the CNF, its row blocks determine subspaces, its positive
membership flags give the stored cover, and its true `nin` flags are a subset
of the actual normal memberships. The one-sided totalizer with output 89 true
forces at least 89 true input flags. Therefore the *actual* sum of abstract
subspace prices is at most `144 - 89 = 55`. Conversely, any such abstract
subspace cover of price at most 55 extends to the row, membership, cover, and
totalizer blocks: take RREFs, set all membership flags to their correct values,
and set totalizer outputs to the true counts. After the symmetry move described
below, it also extends to the lex block. The totalizer clauses only force a lower bound on input count
when an output is true; they do not force every output to equal its true count
under every satisfying auxiliary assignment.

The added normalization clause prohibits `d_z=8` and `nin[z]=1` together.
If the true subspace has dimension 1 and contains n, it is exactly `<n_z>`;
the checks show `n_z` is not any port label, so it covers no port. Replacing
it by zero keeps its price 0 and changes `(d,nin)` from `(8,1)` to `(9,0)`,
preserving the threshold. Thus the cubes need cover normalized candidates,
not every arbitrary satisfying assignment of the unnormalized base formula.

For each permutation p, the lex block requires `d >=lex d o p`. At the first
position where dimensions differ, if its prefix-equality flag remains active,
the order-code implications rule out a smaller left dimension. At a strict
larger dimension a strict-witness flag can disable later constraints. On
equality the flags force the prefix to remain active, so no invalid lex vector
can pass. Conversely an actual lex maximum extends by the evident equality
and strict-witness flags. The 384 permutations form a group and the separate
symmetry checker constructs for each an invertible beta-isometry that maps all
16 normals and 104 ports, preserving each of the 17,152 covering clauses and
the prices. Hence every normalized abstract candidate can be moved to an
orbit-lex maximum before applying the cubes.

## Cube coverage by local witnesses

Write `I={z:d_z=9}`. The actual cube generator gives 1,001 boxes on 993
different masks: one box for each of 991 masks, six boxes for mask 0 and four
for mask 1. The checker inspects the real generated units and normalization
clauses, not merely cube labels; the two split families cover all 81 and 9
relevant `(d_0,d_1)` possibilities exactly once.

For every one of the **64,543 omitted masks**, `coverage-witnesses.txt`
stores an index of a permutation p with a direct contradiction. In position
order, each earlier j has either `p[j]=j`, or both indices lie in I and thus
both dimensions are 9. At the first other position, j is outside I and p[j]
is inside I, so `d_j <= 8 < 9=d_{p[j]}`. This forces a lexicographic loss,
independently of all other dimensions. The checker validates each witness and
the generated lex clauses. Thus all lex-constrained inactive sets are covered
without using the original DFS's negative results. A separate reviewer
independently reimplemented the mask/witness and box checks, and observed
rejection of identity-witness and split-overlap mutations. The 993 masks are
coverage cases, **not** 993 demonstrated SAT assignments.

Witness encoding: 65,536 decimal integers, one per line in mask order; value
65535 marks a covered mask and all other values index the pinned `perms.json`.
SHA-256:
`46c232791c3854b5181cc0e6f1307c6d6db8bbd737bece76cc796a7058885cd6`.

## Independently refuted subdomains

**612 cubes eliminated by inactive-row cover clauses.** For every actual cube,
`verify_cover_eliminations.py` reads the generator's units to determine its
inactive mask I. If `z in I`, then `d_z=9`, so the checked RREF block gives
`U_z=0`; no affine port label h can lie in it, and the membership implication
forces `m[z,t]=0`. If any stored nonempty cover clause at some t consists
entirely of rows z in I, that positive clause is false. This contradiction
uses no budget threshold and no solver. The checker finds and validates one
such port/clause witness for exactly 612 of the 1,001 cube IDs (612 distinct
inactive masks). It checks all stored masks to confirm that the other 389 cube
IDs have no witness of this particular form; that absence is not a SAT verdict.
For `f3591`, port 3 has clause mask 2565 contained in inactive mask 3591.

`inactive-cover-witnesses.tsv` records `(cube, I, port, clause)` for all 612;
`residual-cubes.tsv` records every other `(cube, I)` in source order. Their
SHA-256 digests are, respectively,
`88b1681613fda52eff688df9c3a67d9bc7d6b6babd4056ad24b4e32dc8e15d4b` and
`5326f358c5aee7c8849b7cdf7241580721c6f0cfa4d24c0f914357d8f03af2ae`.

**The `f3591` cube.** Its inactive set is `{0,1,2,9,10,11}` and it contains no
extra split literals. The full generated cube's SHA-256 is
`9b68e622353ea97eaa2ef982723385f05c975b092ebcf1d9da45313126370cf3`, matching
the author's historical hash table. Within a 15 s / 1 GiB cap, a fresh PicoSAT
run found UNSAT in 0.49 s and emitted a new RUP proof. A separately compiled
drat-trim accepted that proof in backward mode. It produced the retained core,
and `check_rup.py` separately verifies the multiset inclusion in the full
cube plus every proof addition by fresh unit propagation. Deletion lines are
ignored, which is sound for RUP because retaining clauses can only help unit
propagation. It explicitly requires the final empty clause. This small Python
checker, the retained input and proof, ordinary Python semantics, and the CNF
generation/hash binding are the trust base for the one-cube result; the PicoSAT
and drat-trim verdicts need not be trusted for that verification.

| Artifact | SHA-256 |
| --- | --- |
| `picosat/f3591.cnf` | `9b68e622353ea97eaa2ef982723385f05c975b092ebcf1d9da45313126370cf3` |
| `picosat/f3591.drat` | `cd58f0d0250e97bd74d065bcbadc6d0a354e7ad3a224ad4b23235ef3dab125c8` |
| `picosat/f3591-core.cnf` | `3bbf22ccd1736de06560cf427ce581c8a3e970e39a0d4a67ba414e2a763b9836` |
| `picosat/f3591-core.drat` | `7404438b3cb7c1944d7b6dfbc3548e993b66ffff917f42fba5235d6439e95221` |

PicoSAT source is Armin Biere's code retrieved from `conda/pycosat` (Git blobs
`de0d93ea5fc31c6f1c3f46998416384dd8438841` and
`db785153284764ef06b9a0d27491439102365fdc`). The checker/extractor source is
`marijnheule/drat-trim`, Git blob `cf8a676ffcc7ef5a47124bbafc9b680a2df333e0`.
Their licenses and the small local DIMACS runner are retained. Source retrieval
was by blob and these are not assertions about current upstream heads.

**All rows have `dim U_z <= 3`.** Every h has first coordinate 1. If an F2
subspace U has dimension r, its intersection with that affine hyperplane is
empty or has `2^(r-1)` points for r>0, and is empty for r=0. Therefore each
of 16 subspaces of dimension at most 3 contains at most four of the 104
distinct h labels. Every port has at least one nonempty positive covering
clause and each true membership flag forces containment, so a satisfying cover
would require at least 104 distinct contained labels; at most 64 are possible.
This proves the named subdomain impossible at **any** budget, without a SAT
solver. More generally, if every dimension is at most 4, at least 10 of the 16
must equal 4, since `64 + 4k >= 104`.
