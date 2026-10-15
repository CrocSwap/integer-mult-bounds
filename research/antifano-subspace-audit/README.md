# Independent subspace audit of the anti-Fano decoder bound

The minimum raw pairing cost of the pinned 12-line configuration is **12**.
This independently corroborates DreamingOfClouds' PR2111, Theorem T, and PR2162,
Theorem T'. It does not supply a new decoder, supplier or multiplication bound.

The new check replaces PR2111's SAT-based uniqueness step with two complete
binary-subspace censuses. It imports no predecessor code and uses no external solver,
finite-field extension, floating point or jet certificate. The exchange argument
below is credited to PR2111, not claimed as new.

## Model and result

For the twelve point/line pairs `(p(t), q(t))` in
[CONFIGURATION.json](CONFIGURATION.json), an admissible binary matrix `B` has
unit diagonal. An off-diagonal entry can be one only if `p(t) dot q(s) = 0`.
There are 72 independently optional entries, hence `2^72` admissible matrices.
All points have full coordinate support. Let `C_j` contain the four columns
whose `q` has coordinate `j` equal to zero, and let `A_j` be its eight-column
complement. The raw cost is

`rank_F2 B[:, A_0] + rank_F2 B[:, A_1] + rank_F2 B[:, A_2]`.

For each block the audit establishes:

| Missing coordinate | Universal triangular minor | Column-basis assignments | Row-basis assignments | Rank-3 completions |
| --- | --- | ---: | ---: | ---: |
| 0 | 1, 4, 2 | 262,144 | 4,096 | 1 |
| 1 | 0, 9, 1 | 262,144 | 4,096 | 1 |
| 2 | 0, 9, 2 | 262,144 | 4,096 | 1 |

Indices start at zero and retain the predecessor's ordering. Both orientations
recover exactly the same unique completion. Its two constituent class column
spaces each have dimension three, their union has dimension three, and every
row in `C_j` vanishes. [EXPECTED.json](EXPECTED.json) records each completion
as twelve-bit column vectors, together with the minors and the upper witness.

**The bound is a minimum over B, not equality for every B.** The full incidence
matrix has block ranks `(8,8,8)` and cost 24. A recorded admissible matrix has
ranks `(4,4,4)` and attains 12.

## Why the census is complete

Each displayed principal minor is unit upper triangular for every admissible
matrix. The verifier checks that all entries below its diagonal are forbidden.
Its three columns and three rows are therefore independent, so every block has
rank at least three.

Fix one block. Each column has six optional bits and its mandatory diagonal
bit. There are exactly `64^3` assignments to the three displayed basis columns.
For a block of rank at most three, every other column must lie in their
eight-element span. The column census intersects that span with each remaining
column's allowed affine set. The product of the intersection sizes counts all
completions. Different basis assignments give different matrices, and the
remaining columns have independent entry constraints. Thus no rank-three
completion is omitted or counted twice.

The separate transpose implementation reconstructs the entry constraints directly
from the rational configuration, without calling the column-option builder.
Each selected row has four optional bits, giving `16^3` basis assignments.
It constructs row spans by set doubling and intersects them with independently
enumerated eight-bit row alphabets. It again counts all completions and agrees
entrywise with the column result.

## The credited exchange argument

Write `S_k` for the span of the columns in `C_k`. If no block has rank three,
all three have rank at least four and the cost is at least twelve.

Otherwise, suppose block `j` has rank three. The unique completion gives
`S_k = S_l = U` of dimension three for the other two classes, and `U` vanishes
on the four rows `C_j`. The projection of `S_j` onto those rows has dimension
at least two. The verifier supplies a universal two-by-two principal identity
minor in `B[C_j,C_j]`, respectively `(0,9)`, `(2,7)` and `(1,4)`.

Because projection kills `U`,
`dim(S_j + U) >= dim U + dim projection(S_j) >= 3 + 2 = 5`.
Both other blocks have column space `S_j + U`. Their ranks are at least five,
so this case costs at least `3 + 5 + 5 = 13`. In either case the cost is at
least twelve. The explicit cost-twelve matrix proves sharpness.

This is a finite computer-assisted proof of the pinned configuration's minimum.
It replaces one computational step of an existing proof, not its mathematical
claim or its broader open three-total conjecture.

## Reproduce

Standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/antifano-subspace-audit
python3.12 -I -O -B research/antifano-subspace-audit/verify.py
python3.12 -O -B -m unittest discover -s research/antifano-subspace-audit -p 'test_*.py'
```

Expected verifier line:

```text
PASS_ANTIFANO_SUBSPACE_AUDIT minimum=12 blocks=3 column_trials=786432 row_trials=12288 unique_rank3=1,1,1 no_new_kappa
```

The ten test groups include all 4,096 three-by-four binary matrices against a
separate dense elimination oracle, a 64-completion census fixture, an impossible
completion fixture, and controls for a missing diagonal, forbidden entry,
incorrect cost witness, wrong source bytes, dependent basis, false uniqueness,
truncated census count, corrupted completion, false lower bound and capacity
exhaustion. Checks remain active under `-O`.

The direct verifier also works from a source export without Git or network.
The registered metadata checker uses Git for historical provenance. Exact heads,
source hashes, scope change, overlap coverage and environment are in
[TASK.json](TASK.json) and [SOURCES.json](SOURCES.json).

Ruff 0.17.0 also passes with all diagnostics enabled under the package's scoped
configuration. Its exclusions retain standard-library unittest, standalone
scripts, literal mathematical dimensions and the documented CLI output:

```sh
ruff check --config research/antifano-subspace-audit/ruff.toml research/antifano-subspace-audit/
```

## Implementation bounds

All mathematical loops have fixed finite bounds. The largest is `64^3` basis
assignments per block, each testing at most five columns against eight vectors.
The transpose uses `16^3` assignments, each testing at most twelve rows.
No search state accumulates across assignments. Configuration and receipt reads
are capped at 4,096 and 16,384 bytes. Every function is shorter than 40 lines.

Python necessarily allocates integers and collections during the census. This
is a managed-runtime deviation from allocation-free steady operation, confined
to this fixed instance. Column alphabets contain at most `8*64` integers; row
alphabets at most `12*16`; each span contains eight. CPython 3.12 tracemalloc
measured a 240,520-byte peak during one audit after configuration parsing. This
is an observation, not a universal process-memory bound. Any variable-size
extension must derive new input, loop and memory caps before reuse.

The unittest runner uses framework dispatch to ten named test methods. This is
the only test-framework indirect-call deviation; no user-supplied code or solver
is loaded. Discovery is confined to this package. A future plugin or broader
discovery mechanism would need a new review. The single `FBT001` suppression
marks an assertion predicate, not a mode-selection flag; all acceptance checks
remain ordinary exceptions under `-O`.

## Limits

This does not enumerate the 217 optimal matrices, prove the general `T=3`
conjecture, reproduce either predecessor's entire suite, or formalize the
exchange argument in Lean. No physical decoder, hosting, precision, all-size
compiler, outer assembly or selected cold replay is checked. The selected
conditional exponent remains unchanged.

## Open next questions

- Can the unique rank-three completion be derived without enumeration? Start
  with the displayed triangular minors and the eight-element spans, then
  eliminate the remaining affine constraints by hand. This would remove the
  computational step, but a short symbolic argument is not established here.
- Can the projection/exchange certificate extend to other three-total
  configurations? First inspect the rank-three blocks of a second explicit
  configuration. The present zero-row and equal-class-space properties are
  verified only for this anti-Fano object and must not be assumed generally.

The structured questions and their blockers are in TASK.json.

## Credit and scope selection

DreamingOfClouds supplied the configuration, the exchange proof and the SAT
uniqueness result in [PR2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111),
and the separate jet proof in
[PR2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162).
This responds to item 1 of the
[independent-check handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18934590).
The model and prior rank arguments retain the PR446/595/1590 lineage.
CONFIGURATION.json is an unchanged copy of PR2162's `data/tied_min.json`, also
byte-identical in PR2111. LICENSE and UPSTREAM-NOTICE.md retain its Apache-2.0
terms and source notice. No predecessor implementation is imported.

The original draw was `bit-helper-contract`, priority revision 4. Its basic
H2/K replacement was already covered by PR1194/1782/1805 and related packages;
the proposed full-profile recount was already covered by PR1421. This is an
explicitly changed scope to an independent decoder-floor audit, not progress on
the helper contract. The binary pairing-cost check addresses a live verification
request on the binding complex side. Nick Petalas prepared this audit.
