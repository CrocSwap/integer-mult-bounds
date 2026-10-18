# The first free-compatible 24-row boundary still costs COPY64

**Scoped negative result with exact finite premises; no new supplier or kappa.**
PR [#1375](https://github.com/CrocSwap/integer-mult-bounds/pull/1375) leaves a
concrete next question: its first free-compatible 24-row deletion lowers a
coordinate support's binary span from eight to seven. Can that boundary reduce
the COPY bill when the decoder factors are coupled correctly?

For that exact boundary, the answer is **no**, even with arbitrary complex
correction amplitudes, zero amplitudes, and arbitrary `GL(3,C)` mixing. The
three replacement ranks either include two ranks at least eight, or are all
at least seven. Their separate COPY power bill cannot improve for
`0 < q <= 1`. Identity mixing attains the whole-decoder cost 64.
The cancellation-aligned example lowers one term to seven but changes the
three-term bill from `(8,8,0)` to **`(7,8,7)`**, costing 70 overall.

This closes the named boundary question, not the larger-rectangle problem.
The claim was initially for cancellation-aligned amplitudes. The survivor
argument below handles every complex amplitude on the same support without
searching coefficients or changing the object. The pending PR1375 theorem is
not assumed: all finite premises used here are recomputed.

## Reproduce

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p112-boundary24-seed39
```

Expected final marker:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/p112-boundary24-seed39 outcome=negative-result
```

The replay checks metadata and exact source pins, then both implementations.
`verify.py` checks 655 support pairings, nine Gaussian-rational fixtures
(112,896 entries), and nine controls. `independent_check.py` reconstructs
Euclidean E8 geometry without importing either the primary checker or its
predecessor geometry, uses set-based binary elimination, rechecks every finite
premise, and checks 25,088 integer identities, two nonzero rank-nine minors,
and six controls. Both defaults are read-only. Explicit `--write PATH`
regenerates a receipt; `--check PATH` checks an alternate receipt.

These are finite certificates supporting the written argument below. Neither
implementation is a proof assistant, and separate code by the same contributor
is not independent human review. See [VALIDATION.md](VALIDATION.md) for executed
checks and their limits.

## Exact object and statement

Use PR845/PR717's P112 model, pinned in [SOURCES.json](SOURCES.json). Represent
E8 roots at twice their usual scale, choose the lexicographically larger sign
of each line, delete the eight roots `2e_(2j) +/- 2e_(2j+1)`, and sort the
remaining 112 lines lexicographically. Frame columns are ordered by increasing
`j`, with the plus root before the minus root. Let

`G_ij = r_i dot r_j / 4`, `X_ik = r_i dot f_k / 4`,

so `XX^T = 2G`. The binary label-pairing matrix is
`B_ij = (G_ij + 1) mod 2`. For supports `A,C`, write
`rho(A,C) = rank_F2 B[A,C]`. A scalar rank-one term costs
`rho(supp(d), supp(t))`; its complex coefficients are not reduced modulo two.
This is the inherited separate-term COPY objective.

Take `x = X[:,0]`, `y = X[:,1]`, singleton index `beta = 0`, and

`U = {i : x_i != 0 and B_i0 = 0}`.

In the specified order,

```text
U = [27,28,31,32,69,70,73,74,77,78,81,82,
     85,86,89,90,93,94,97,98,103,104,107,108].
```

This equals PR1375's `free_boundary.deleted` exactly. Its only common odd
neighbor is 0. Choose any `u in C^112` with `supp(u) subset U`, any
`lambda in C`, and any invertible complex `3 x 3` matrix `M`. Set

`D = [x,y,u] M`, `T = [x,y,lambda e_0] M^(-T)`.

Ordinary transpose gives

`D T^T = xx^T + yy^T + lambda u e_0^T`.

The correction is zero on constrained entries (`B_ij = 1`). Keep the other
six coordinate terms unchanged. All assertions include `u=0`, `lambda=0`,
and complex cancellation.

**Theorem.** For the three ranks `r_j = rho(supp(D[:,j]),supp(T[:,j]))`,
either at least two `r_j >= 8`, or all three `r_j >= 7`. Therefore

`sum_j r_j >= 16`, and `sum_j r_j^q >= 2 * 8^q` for every `0 < q <= 1`.

The whole decoder costs at least 64 and has at least the original separate
COPY power bill. `M=I` attains both bounds for every allowed `u,lambda`.
By symmetry of `B` and ordinary transpose, the transposed family has the
same conclusion. Other 24-row sets, coordinate pairs and larger rectangles
are not asserted to have these premises.

## Finite premises

A nonzero complex combination of `x,y` has one of five supports, represented
by `x`, `y`, `x+y`, `x-y`, and `x+2y`. This classification is exact over C:
nonzero coordinate entries are `+/-1`, so a row with both entries nonzero can
cancel only at ratio `+1` or `-1`; zero coefficients give the first two cases.
Write these supports as `S_0,...,S_4`, and `C_j = S_j minus {0}`.

All ordered pairings are recomputed in [CERTIFICATE.json](CERTIFICATE.json).
The original and complete-deletion matrices, respectively, are

```text
rho(S_i,C_j)                 rho(S_i minus U,C_j)
8 8 8 8 8                   7 7 7 7 7
8 8 8 8 8                   8 8 8 8 8
8 8 9 9 9                   8 8 9 9 9
8 8 9 9 9                   8 8 9 9 9
8 8 9 9 9                   8 8 9 9 9
```

Also `rho(U,C_j)=7` for every `j`. For each of the 24 possible restored
indices `k in U`, the 25 entries

`rho(S_i minus (U minus {k}), C_j)`

are at least eight. These 600 checks comprise 384 ranks eight and 216 ranks
nine. Checking maximal proper deletions suffices for **every** proper subset
of U, because enlarging either support cannot decrease pairing rank. This is
an exact monotonicity reduction, not enumeration of all `2^24` subsets.
The total is `25 + 25 + 5 + 24*25 = 655` prescribed pairing checks, plus
the eight unchanged coordinate baseline checks.

The full ambient pairing has rank nine. The binary span of `S_0` has dimension
eight and that of `S_0 minus U` has dimension seven. Thus the predecessor's
span-preservation premise really fails at this boundary; the new proof must
use the coupled factors. The independent checker computes these dimensions
using rows of B, an injective representation of the label space because B
has its full ambient rank nine.

## Proof for all complex amplitudes and factor changes

Write column `j` of `M` as `(a_j,c_j)`, with `a_j in C^2`, and column `j`
of `N=M^(-T)` as `(b_j,d_j)`. The top-left block of `M N^T = I_3` gives

`sum_j a_j b_j^T = I_2`.

At least two summands therefore have both `a_j != 0` and `b_j != 0`.
For any such term, its left support contains `S_i minus supp(u)` for some
stratum `S_i`; its right support contains `C_l` for some stratum `S_l`.
Outside the correction supports, no choice of amplitudes can cancel those
entries.

If `supp(u)` is a proper subset of U, choose a missing index `k in U`.
The maximal-proper-deletion checks and support monotonicity give rank at
least eight for each of these two terms. This proves the first alternative,
including `u=0`.

It remains to take `supp(u)=U`. Suppose some `b_j=0`. Since N is invertible,
`d_j != 0`. The off-diagonal identities in `M^T N = I_3` force
`c_k d_j = 0` for both `k != j`, hence `c_k=0`. Those two columns of M have
nonzero `a_k`, and their dual columns have nonzero `b_k` (two columns of N
cannot both be multiples of `e_3`). Their left factors are original
nonzero combinations of x,y, with no u component. The original pairing
matrix above gives rank at least eight for both. This is again the first
alternative.

Otherwise all three `b_j` are nonzero. If `a_j != 0`, the complete-deletion
matrix gives rank at least seven. If `a_j=0`, invertibility of M gives
`c_j != 0`; the left support is exactly U, and the pure-correction row
`rho(U,C_l)=7` gives the same bound. All three ranks are therefore at least
seven. This proves the second alternative.

In the first alternative, the power bill is at least `2*8^q`. In the second,

`(3*7^q)/(2*8^q) = (3/2)*(7/8)^q >= 21/16 > 1`

for `0<q<=1`. Adding the six unchanged rank-eight terms proves the stated
whole-decoder comparison. With `M=I`, the extra term has rank zero because
`B[U,{0}]=0`, proving sharpness. No sampled coefficient set is used to
quantify this argument over C.

## A concrete failed mechanism and its complete COPY bill

Set `u_i=x_i` on U and zero elsewhere, `lambda=1`, and

```text
M = [ 1 0 0 ]
    [ 0 1 0 ]
    [-1 0 1 ].
```

The factors are `(x-u,y,u)` and `(x,y,x+e_0)`. The first term drops from
eight to seven, but the third now costs seven. The replacement bill is
`7+8+7=22`, and the whole decoder costs `6*8+22=70`. Counting only the first
two terms would falsely report 63. Omitting the compensation also fails a
constrained matrix entry; the independent receipt records an exact example.

The attaining identity fixture is a genuinely rank-nine masked completion:
the independent receipt supplies nonzero `9 x 9` minors for `[X,u]` and
`[X,e_0]`. Full-rank factors imply rank nine of `XX^T+u e_0^T`. This
witness confirms the result is not restricted to rank-eight masked matrices.

For the optimistic rejection screen, retain the baseline's normalization,
width and multiplicity and grant zero additional preparation, source-access,
frame-change, restoration, hosting and recursive overhead. Even this
relaxation cannot improve the separate COPY bill. No helper network is
constructed, and no new complete child histogram, moment root or kappa is
inferred. Changed billing or savings in other parts of a supplier require
separate accounting and are outside this result.

## Provenance, coordination and limits

- Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Its selected conditional
  kappa is `836330098538459/500000000000000000`, from PR1094. Selection and
  `upstream/` are unchanged. The selected source manifest, construction and
  maintainer review were consulted; the quick baseline check is source and
  arithmetic evidence, not a selected-supplier cold replay.
- Assignment: complex-supplier track, OS-random seed **39**, generated once.
  Three candidates were this boundary, another A8 puncture orbit, and a
  two-entry masked completion. `39 mod 3 = 0` selected this boundary; the seed
  also fixes the nonreal fixture phases and the omitted boundary index.
  [TASK.json](TASK.json) records scope, stopping rule and overlap coverage.
- Claim: [Discussion1316](https://github.com/CrocSwap/integer-mult-bounds/discussions/1316#discussioncomment-18912070).
  No pinned sprint issue existed. The boundary and arbitrary-amplitude proof
  are distinct from the all-nine-factor singleton claim in Discussion1360:
  our 24-by-one correction mixes two original modes, not all eight.
- Predecessor: commdata2338's PR1375,
  `4a533aff2a7a87c9b36e077a31774b332a7f64bd`, supplies the boundary and open
  question. Arham Tahir's PR1331 supplies the earlier one-coordinate
  obstruction and two-coordinate handoff. Neither pending theorem is a
  proof dependency here. Exact contextual source digests are recorded.
- Mathematical and implementation credit: Mihir Srivastava / PR845 for
  `geometry.py`; DreamingOfClouds / PR717 and PR446/595 for the decoder and
  separate-copy framework; themilkman216 / PR968 for the pairing-cost model;
  Joel Pulikkan / GamingPuzzled / PR620 for the coordinate COPY64 construction;
  woklerx / PR1077 for the orientation check. Classical E8 geometry is retained.
- Unchecked: physical gathering, legal delivery frames and owners,
  restoration/hosting/precision invoices, all-size compilation,
  common-label/mutable-source realization, analytic transfer and the bit
  H1-H5 interfaces. No complete multiplication theorem, native/Lean proof,
  hosted-CI success or maintainer acceptance is claimed.

Prepared for **Hanson Sun / bbMisk**, with substantial **OpenAI Codex**
assistance in mathematics, implementation, verification and writing.
Both implementations are by the same AI-assisted contributor. Apache-2.0;
predecessor attribution and source files are preserved.

## Open next questions

- **Other maximal free rectangles.** Can a different 24-row boundary, or a
  rectangle with more than one column, lower the coupled bill? First compute
  its survivor pairings and pure-correction pairing ranks. The proof here
  relies on the particular U and the singleton dual-column case; it does not
  supply those premises elsewhere.
- **More mixed coordinate terms on this same U.** Can three or more original
  modes exploit it? Start with three specified modes and a `GL(4,C)` identity,
  charging all four replacement terms. The present two-mode rank identity and
  three-term power comparison do not settle that problem.

The structured questions, relevance and blockers are in [TASK.json](TASK.json).
