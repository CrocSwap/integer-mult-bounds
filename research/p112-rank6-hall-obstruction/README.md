# A COPY62 P112 cover passes frame and diagonal screens but cannot decode

**Scoped negative result and exact support certificate. No supplier, new kappa,
or selected-frontier change.**

The concrete ten-rectangle proposal in [SUPPORT.json](SUPPORT.json) has nine
COPY6 maximal star slices and one retained coordinate COPY8 rectangle. It
meets every one of the 1,260 live orthogonal eight-frames at least eight times
and covers every one of the 112 diagonals. Its frame-hit histogram is
`{8:305, 9:650, 10:305}`. Thus the diagonal failure of PR1347's COPY60 witness
is genuinely repaired at the level of these necessary conditions.

Nevertheless, the proposal is not a masked decoder. Moreover, **none of the
4,096 representative/coordinate choices in the precisely defined family
below is a masked decoder**, for any complex coefficients under ordinary
transpose, independent transposition of the nine rectangles, arbitrary
further support restrictions, or any additional cost-zero terms.

## Result and complete bounded family

Let `H_k`, for `k=0..8`, be the complete eight-frame hit set of rank-six
rectangle `k` in SUPPORT.json. Each contains 1,120 frames; the nine sets are
distinct. A permitted paid term `k`:

1. starts from **any** of the 7,616 tagged C/N root-star parent pairs of binary
   pairing rank seven on the fixed P112 model;
2. restricts both supports arbitrarily to pairing rank at most six;
3. retains every hit in `H_k`, but is allowed additional hits;
4. may transpose its two support factors.

The tenth term has arbitrary coefficients supported inside the square of
**any one of the eight punctured-frame coordinate stars**. Its full support
has pairing rank eight. The theorem does not prescribe its coefficients to
be those of the coordinate decoder. This is a generous support model, not a
physical helper program.

The complete maximal-slice census gives four tagged matches for each `H_k`,
which reduce to **two distinct support rectangles** per pattern. No strict
hit-superset appears. Each pair of choices also has different diagonal
support. Transposition does not change the screens used below.

| Exact quotient | Number |
|---|---:|
| Tagged rank-seven parents | 7,616 |
| Nonzero-codeword maximal row slices traversed | 967,232 |
| Independent representative choices | `2^9 = 512` |
| Coordinate-star choices | 8 |
| Complete representative/coordinate quotient | 4,096 |
| Rejected by an uncovered diagonal | 4,093 |
| Diagonal survivors | 3 |
| Survivors rejected by a two-root rank cut | 3 |

All three diagonal survivors use coordinate root 0. For that coordinate the
partition is 509 diagonal failures plus three rank-cut failures among 512
choices. Each of the other seven coordinates has 512 diagonal failures.
[CERTIFICATE.json](CERTIFICATE.json) gives all 18 maximal representatives,
the complete source-census digest, all three explicit survivor words, and a
compact orthogonal-pair separator for each survivor. This is a complete
bounded quotient, **not** an exhaustion of all COPY62 decoders.

The three certificates are short enough to inspect directly. Bits choose the
ordered representatives in `CERTIFICATE.json`; root and term IDs are zero-based.

| Representative bits | Orthogonal pair | Only active term on the pair |
|---|---|---|
| `110011000` | `(2,22)` | 9, the coordinate rectangle |
| `110011010` | `(4,22)` | 9, the coordinate rectangle |
| `110111000` (the supplied proposal) | `(2,23)` | 9, the coordinate rectangle |

In each row, a single rank-one contribution cannot equal `4 I_2`.

## Why these are coefficient-independent obstructions

### Proper-clique rank cuts

For any orthogonal live root set `S`, the constrained masked target is
`(2G)[S,S] = 4 I_|S|`. Each paid outer product has rank at most one on this
submatrix and vanishes unless both support factors meet `S`. Therefore at
least `|S|` paid rectangles must meet `S` on both sides. A cost-zero term
cannot contribute: the binary label pairing is one everywhere on `S x S`,
whereas a zero-cost support rectangle has identically zero pairing.

For each of the three diagonal-surviving representatives, the certificate
exhibits an orthogonal **pair** met on both sides by fewer than two terms.
No choice of coefficients can give the required rank-two matrix. This is
stronger here than checking full eight-frames and diagonals alone.

The replay also enumerates **all 262,928 nonempty orthogonal cliques**, with
counts by size
`112, 3304, 31024, 94892, 82656, 39088, 10592, 1260`.
It does not mistake subsets of live eight-frames for this full set: some
proper cliques have no live eight-frame extension. The complete scan is
supplementary; the short two-root certificates already prove rejection.

### Additional saturated-frame duality certificate

The supplied proposal also has a separate eight-frame obstruction. On a
frame `F` with exactly eight potentially active rectangles, write their
restricted factors as square matrices `D_F,T_F`. An exact decoder would give
`D_F T_F^t = 4I`. Both matrices are invertible, hence `T_F^t D_F = 4I` as well.
Consequently every active term must satisfy

`sum(i in F) d_k(i) t_k(i) = 4`.

The certificate identifies an active term whose allowed left and right
supports are disjoint on such a frame. Its left-hand side is identically
zero. This reasoning uses **ordinary transpose**, not conjugate transpose
or positivity, and is valid over the complex numbers. It does not apply to
an unsaturated frame with nine or ten potentially active terms; a negative
control enforces that boundary. We do not claim priority for square-matrix
duality itself; the contribution is its exact source-bound application.

### Why the quotient covers arbitrary joint trims

Write a binary rank-seven parent matrix as `M = A B`, with `A` of column
rank seven and `B` of row rank seven. If a joint restriction `A_L B_R` has
rank at most six, at least one of `A_L,B_R` loses rank: if both retained rank
seven, one has a left inverse and the other a right inverse, forcing their
product to retain rank seven.

A nonzero functional annihilating the deficient factor supplies a nonzero
parent codeword. Expand that side to the codeword's entire zero set and
restore the other parent support. This dominates the original rectangle.
The row-oriented case is enumerated directly, and the column-oriented case
is a transpose of an enumerated row slice. This is the domination argument
of PR1347 and its representative successors, applied to the new patterns.

Expansion preserves the required hits and only adds diagonal and clique
hits. The census includes every expanded rectangle retaining `H_k`.
Every expanded nine-tuple, even with the full coordinate rectangle, has an
uncovered diagonal or a deficient orthogonal pair. Shrinking any rectangle
cannot repair either defect. Independent transposition preserves both
screens. This proves the stated family theorem without assuming that actual
nonzero supports equal the maximal caps.

## Complete optimistic budget, not a construction

Keep every non-centre rank count of the selected local profile and replace
its eight COPY8 children by nine COPY6 and one COPY8 child:

- baseline: `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, centre charge 64;
- proposed relaxation: `{1:2412, 2:418, 3:432, 4:142, 5:82, 6:9, 8:1}`,
  centre charge 62;
- both use `m=73`, `families=896`, `stages=9`, and the inherited coverage law.

The pinned rational-interval ceiling engine gives

- baseline `a` ceiling in `[0.001690054109088, 0.001690054109089]`;
- COPY62 ceiling in `[0.001783866218920, 0.001783866218921]`.

The latter lower endpoint is strictly greater than 1.05 times the former
upper endpoint: about **5.55%** ideal headroom. This is why rejecting false
positives at COPY62 matters. New frame transitions, source access, restoration,
hosting and precision costs are **optimistically omitted for this rejection
screen only**. There is no paid physical realization, supplier admission,
scalar-operation saving, or improved multiplication exponent.

## Reproduce and verification coverage

From the repository root, standard-library CPython 3.12:

```sh
uv run --python 3.12 --no-project python -I -B research/p112-rank6-hall-obstruction/verify.py
uv run --python 3.12 --no-project python -I -O -B research/p112-rank6-hall-obstruction/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/p112-rank6-hall-obstruction
```

The verifier compares the complete deterministic certificate. `--write`
regenerates it. It independently checks the ten displayed copy ranks with
least-pivot binary elimination, traverses the complete parent/codeword
quotient, checks all three short separators, and checks the extra duality
separator. A known exact eight-coordinate decoder supplies 12,544 all-pairs
identity checks, all 10,080 saturated-frame term traces, and a positive
all-clique screen. Small rational duals and a genuinely complex ordinary-
transpose fixture supplement nine semantic negative controls.

Actual command outputs and environment are in [VALIDATION.json](VALIDATION.json).
No full selected-frontier cold replay, native compiler run, hosted CI result,
Lean proof or independent human proof review is claimed.

## Search history, limits and overlap

The independently drawn seed is `5130d276c01dfff62d214a1fd73e9011`, track
`complex-mechanisms`, emitted card `complex-rank-shape-decoder`.
[SELECTION.json](SELECTION.json) preserves the full chooser output. The exact
base is `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.

The original COPY60 search retained the full maximum-hit representative
catalogue rather than PR1347's single diagonal representative. A 180-second
MILP run and a 300-second native-cardinality attempt produced no witness;
neither is an exclusion proof. The one declared pivot introduced a retained
coordinate COPY8 term. The resulting COPY62 support witness passes the
predecessor screens but fails exact necessary rank conditions. An additional
600-second lazy proper-subframe search stopped after three incumbents; no
UNSAT or global negative claim follows. We therefore prove only the complete
source-bound representative family above, not the broader searched class.

`search.py` and `search_sat.py` retain optional proposal mechanisms; acceptance
requires neither SciPy nor PySAT. Their optional solver outcomes are never
proof inputs. Current `--all-cliques` separation enumerates the full clique
set, not merely subsets of eight-frames. Different solver runs may find
other supports or time out. The fixed certificate, not rerunning a heuristic,
is the reproducible result.

This changes PR1347's homogeneous COPY6 alphabet and its ten fixed patterns;
it is not the earlier COPY60/99-diagonal result with a larger seed. It is also
distinct from prior-round PR1909's tetrad-local COPY112 theorem. The rank-eight
all-pairs and rank-eight masked-rigidity results do not cover these ten paid
terms. [OVERLAP.json](OVERLAP.json) records exact heads and coverage limitations.

## Open next questions

Can a different mixed COPY62 support choice survive all proper-clique cuts
and saturated-frame duality? The first step is to add these cheap exact
separators to support synthesis before solving for complex coefficients.
This matters because its optimistic profile clears the five-percent screen.
The fixed nine retained-hit patterns must change to escape this theorem.
Even a surviving support proposal still needs exact coefficients and a fully
charged physical construction; neither follows from a feasible support
relaxation.

## Credit and license

Cinna Davis (@1337isnot1337), PR1347 and PR1323, supplies the rank-six support
model, census and frame-cover question; PR1402 supplies the representative
warning and union obstruction. The retained `p112-rank6-cover-representatives`
package by @woklerx with Codex supplies the sharp one-choice-per-term cap 99
and the joint-trim domination argument. We reuse their pinned geometry, not
claim independent priority for those facts. Navinor/PR1226, David Arias/PR1236,
Hanson Sun/PR1242, DreamingOfClouds/PR717 and themilkman216/PR968 retain the
underlying star, label, frame and decoder credits. Douglas Colkitt's PR1240
supplies the exact optimistic ceiling engine; the selected supplier and its
full credited lineage remain unchanged.

New work by **Adam Gall**, with substantial **OpenAI Codex GPT-6 Astra**
assistance in reasoning, experiments, implementation and documentation.
Apache-2.0. All predecessor files and their notices are unchanged.
