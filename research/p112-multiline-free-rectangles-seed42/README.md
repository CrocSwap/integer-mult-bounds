# Free rectangles with multiple rows and columns retain COPY64

**Scoped negative result, with a written proof and exact finite premises.**
On the fixed P112 coordinate decoder, add any nonzero free rank-one correction
whose support contains at least two rows and two columns. Mix that correction
with any two original coordinate terms by an arbitrary complex invertible
3-by-3 factor change. Keep the other six coordinate terms unchanged.
At least two replacement terms still have binary pairing rank eight or more.
The sharp whole-decoder separate COPY cost is therefore **64**, and its COPY
power bill cannot improve for `0 < q <= 1`.

The contribution is the **two-anchor span-preservation lemma** below and its
explicit extension to all 28 coordinate pairs. Concurrent PR1460 already gives
a COPY64 theorem for arbitrary nonzero rectangles at pair (4,6), using a
compensation-size argument. This package supplies a different, stronger
per-active-term rank-eight statement when both supports have at least two
indices, together with a complete independent two-anchor census. PR1375's
small rectangles and PR1373's three-active-product case are also credited.
Singleton-sided rectangles and zero factors are excluded; PR1468 independently
addresses the one-column class. None of those pending theorems is assumed.

No physical supplier, complete child histogram, improved kappa, full
multiplication theorem, or proof-assistant verification is claimed.

## Reproduce

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p112-multiline-free-rectangles-seed42
```

Expected final marker:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/p112-multiline-free-rectangles-seed42 outcome=negative-result
```

The explicit replay runs both checkers after validating metadata and source
pins. Their default modes only read files. `--write PATH` regenerates the
respective receipt, and `--check PATH` checks an alternative receipt.

- `verify.py`: all 512 binary characters and five support strata, producing
  2,553 nonempty cuts; 28 explicit coordinate symmetries; seven exact
  Gaussian-rational decoder fixtures, 87,808 matrix entries; 12 controls.
- `independent_check.py`: constructs Euclidean E8 roots without importing the
  primary checker or predecessor code. Set-based elimination checks all 6,216
  two-anchor erasures and 31,080 span identities. It independently validates
  the 28 proposed symmetries, including 351,232 pairing entries, and a literal
  integer compensation identity on 12,544 entries; six controls.

Both implementations are by the same AI-assisted contributor. Separate code
and exact finite checks are not independent human review or formalization of
the quantified theorem. Execution details are in `VALIDATION.md`.

## Model and statement

Use the PR845/PR717 P112 geometry pinned in `SOURCES.json`. Enumerate doubled
E8 roots, choose the lexicographically larger sign of each root line, remove
the eight frame roots `2e_(2j) +/- 2e_(2j+1)`, and sort the remaining 112 lines.
The frame order is increasing j, plus before minus. Define

```
G_ij = (r_i dot r_j) / 4
X_ik = (r_i dot f_k) / 4
B_ij = (1 + G_ij) mod 2.
```

Then `XX^T = 2G`, `X_ik in {0,1,-1}`, and the symmetric binary matrix B has
rank nine. For index sets A,C, let `rho(A,C) = rank_F2 B[A,C]`. The inherited
separate-total model charges a scalar rank-one term d t^T by
`rho(supp(d),supp(t))`. Complex coefficients are not reduced modulo two.
Entries with `B_ij=1` are constrained; a correction on a rectangle U x V is
free precisely when `B[U,V]=0`.

Choose any distinct coordinate modes p,r, and put x=X[:,p], y=X[:,r]. Let
u,v be arbitrary complex vectors with actual supports U,V satisfying

```
|U| >= 2, |V| >= 2, B[U,V] = 0.
```

For every `M in GL(3,C)`, set

```
D = [x,y,u] M,      T = [x,y,v] M^(-T).
```

Ordinary transpose gives `DT^T = xx^T + yy^T + uv^T`. Thus these three terms,
together with the other six unchanged coordinate terms, form a masked decoder.
Zeros within the chosen support containers are allowed as long as the actual
supports still satisfy the displayed conditions.

**Theorem.** Write `r_j=rho(supp(D[:,j]),supp(T[:,j]))`. At least two r_j are
at least eight. Consequently

```
6*8 + sum_j r_j >= 64,
6*8^q + sum_j r_j^q >= 8*8^q       (0 < q <= 1).
```

Identity mixing M=I attains equality for every allowed u,v: the replacement
ranks are `(8,8,0)`. This is a sharp statement for this family and objective.

## Finite lemma: two common odd neighbors prevent span loss

For the seed-selected representative coordinate pair `(2,4)`, every nonzero
complex combination of x,y has one of five supports. Representatives are
`x, y, x+y, x-y, x+2y`; call the supports S_0,...,S_4. This classification is
exhaustive over C: when both coordinates at a row are nonzero, cancellation
can occur only at ratio +1 or -1. The generic ratio 2 represents all other
nonzero ratios. Their support sizes are `56,56,76,76,88` and their binary row
span dimensions are `8,8,9,9,9`.

The unmodified pairing-rank matrix is

```
8 8 8 8 8
8 8 8 8 8
8 8 9 9 9
8 8 9 9 9
8 8 9 9 9.
```

The primary certificate enumerates the entire 512-element row space of B.
For every character c and every S_i, form E=S_i intersect supp(c). Whenever
E is nonempty, it has **at most one common odd neighbor**: at most one index b
satisfies `B[e,b]=0` for every e in E. The receipt lists all 2,553 nonempty
cuts, their exact masks and their complete common-neighbor sets; seven cuts
are empty. No random coefficient search enters this claim.

Why these characters suffice: a linear functional on the row space of B
extends to a dot product with a vector in F2^112. Its evaluations on the rows
of B lie in the column space of B, which equals its row space by symmetry.
Thus all possible binary separating functionals occur in the census.

Suppose a set U has at least two common odd neighbors. If deleting U from
S_i decreased the span of the corresponding full rows of B, some binary
functional would vanish on all surviving rows but not on all original rows.
Its nonempty cut E would be contained in U, and would inherit those two
common odd neighbors. This contradicts the finite certificate. Hence

```
span_F2 B[S_i minus U, :] = span_F2 B[S_i, :].             (1)
```

The second checker verifies (1) by a different finite reduction. Any such U
is contained in `N(beta) intersect N(gamma)` for two distinct common odd
neighbors. It checks the largest possible deletion for **every** unordered
pair beta,gamma, then uses rank monotonicity for every smaller U. The maximal
deletion sizes and counts are

| Deleted rows | Anchor pairs |
|---:|---:|
| 20 | 168 |
| 22 | 2,688 |
| 24 | 672 |
| 26 | 2,688 |

All five span dimensions remain unchanged in all 6,216 cases. In particular,
this includes free-compatible deletions beyond the earlier 23-row cap.

The certificate also gives 28 explicit permutations of the eight coordinates,
with signed bijections of the 112 root lines, carrying `(2,4)` to every
unordered coordinate pair. Both checkers verify their complete binary pairing
matrices and root-coordinate equations. Row signs do not alter supports or
binary pairings. Reversing the two chosen coordinates merely exchanges the
first two factor coordinates. Thus (1) and the five-stratum pairing table hold
for every pair, without assuming an unverified symmetry group classification.

## Proof of the COPY floor over all complex factors

Write the j-th columns of M and N=M^(-T) as `(a_j,c_j)` and `(b_j,d_j)`, with
`a_j,b_j in C^2`. The top-left block of `MN^T=I_3` gives

```
sum_j a_j b_j^T = I_2.
```

A sum of fewer than two nonzero rank-one matrices has rank at most one.
Therefore at least two terms have both a_j and b_j nonzero. For each such
term, its left support contains `S_i minus U` for some support stratum S_i,
and its right support contains `S_l minus V` for some S_l. Corrections cannot
cancel entries outside their actual supports.

Since V has at least two elements and `B[U,V]=0`, equation (1) applies to U.
Similarly it applies to V, using two elements of U and symmetry of B.
Deleting U preserves the full row span of S_i; deleting V preserves the full
column span of S_l. Restricting a spanning set of rows to any fixed columns
still spans their restrictions, and the analogous statement holds for
columns. Consequently

```
rho(S_i minus U, S_l minus V) = rho(S_i,S_l) >= 8.
```

Enlarging supports cannot lower matrix rank. Each of the two active terms
therefore costs at least eight. This proves the two displayed bounds and
covers exactly two or three active projected products alike. Pure correction
terms remain in the bill; their rank is nonnegative. If all three products
are active, the whole separate COPY rank is at least 72.

The arbitrary-complex quantifiers are supplied by this argument. The finite
Gaussian-rational fixtures check implementation and conventions, not a sample
from which those quantifiers are inferred.

## Controls, budget, and boundary

The identity fixture has a nonzero 24-by-2 correction and attains `(8,8,0)`.
A literal compensated cancellation fixture has ranks `(8,8,6)`, hence whole
cost 70. Omitting its third term changes constrained entry `(8,8)` by -1 in
the independent integer fixture. Other fixtures include nonreal coefficients,
a 4-by-8 rectangle, a maximal 26-by-2 rectangle, transposition, and dense and
triangular factor changes.
Wrong inverse-transpose, Hermitian substitution, singular mixing and nonfree
support mutations are rejected.

A singleton-sided control shows why the two-anchor premise matters. For
coordinate x=X[:,2] and singleton column 42, deleting
`{i : x_i != 0 and B_i42=0}` lowers the row span from eight to seven. This is a
counterexample to extending **the span lemma** to one anchor, not to a COPY64
theorem for singleton corrections. Those cases require a different argument.
Missing source pins, altered source digests, incomplete character/orbit
inventories, altered geometry and corrupted receipts also fail closed.

The optimistic COPY screen retains the width, normalization, multiplicity and
separate-call convention of the original decoder. Its complete replacement
bill includes all three terms and the other six unchanged terms. Grant zero
additional preparation, source-access, frame-change, helper, restoration,
hosting and recursive-management expenses. Even this relaxation cannot reduce
this COPY bill. A physical implementation still must account for all those
operations; none is constructed here. No complete supplier moment or kappa is
inferred, and savings elsewhere in a supplier or a changed sharing convention
are outside the obstruction.

## Provenance and overlap

Exact base: `410026dc5513b87db92ae98571d1d5984c69a983`. The selected certificate
at that base is PR1094's conditional
`kappa=836330098538459/500000000000000000=0.001672660197076918`.
Its construction/source manifest and maintainer review were consulted; the
baseline source-binding check passed. This is not its full cold replay.
Selected, frozen, and upstream files are unchanged.

OS assignment seed 42 selected structural decoder research. `TASK.json`
records three candidates, the stopping rule and exact predecessor heads.
The initial one-column scope was released when the complete overlap scan
found Gareth Davidson / bitplane's earlier
[Discussion1434](https://github.com/CrocSwap/integer-mult-bounds/discussions/1434).
The one allowed pivot tested two-column erasures. The same finite lemma then
proved the larger multiple-row, multiple-column statement above; this was a
logical consequence, not another search or pivot. The
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1316#discussioncomment-18912476)
records that change. `OVERLAP.json` records the final search coverage and scope
comparison. No absence of search hits is presented as proof of novelty.

Credit and distinctions:

- commdata2338 / PR1375: small-rectangle floor and the free-compatible erasure
  boundary. The new result removes the size cap when both supports have at
  least two elements.
- Cinna Davis / PR1373: arbitrary rectangles with three active products at
  pair (4,6), and identification of the exactly-two-product branch. The present
  proof handles that branch and all pairs under its explicit support premise.
- Arham Tahir / PR1331: one-coordinate arbitrary-rectangle predecessor and
  the two-coordinate handoff; Discussion1360 considers all nine factors of a
  single-entry completion and is distinct.
- Hanson Sun / PR1432: fixed 24-by-one boundary and coupled-factor accounting.
- Hanson Sun / concurrent PR1460, head
  `8d53667d9bb09d9b1ffb0f865b5c8dc230eb02f6`: earlier arbitrary nonzero
  rectangle COPY64 proof at (4,6), including the two-product branch. This
  package adds the stronger span-preservation lemma, explicit all-pair
  transport and an independent maximal-erasure method, not first priority for
  that COPY64 subcase.
- Gareth Davidson / bitplane / PR1468, head
  `5e2d8ec8ebff17c85e813ef1bd6f06312c1fe16a`: independent all-pair one-column
  theorem after Discussion1434. Its singleton-sided class is outside this
  proof's two-anchor premise; the coverage is complementary.
- Mihir Srivastava / PR845: pinned geometry implementation, imported only by
  the primary checker. DreamingOfClouds / PR717 and PR446/595: masked decoder
  and separate-copy framework. themilkman216 / PR968: pairing-cost model.
  Joel Pulikkan / GamingPuzzled / PR620: coordinate COPY64 construction.
  woklerx / PR1077: complex-coefficient orientation check.

Pending predecessor theorems are contextual credit, not assumed proof steps.
The finite geometry and every premise used here are recomputed. All-size
compilation, common-label/mutable-source realization, legal frames/owners,
physical gathering, restoration/hosting/precision, analytic transfer and bit
H1-H5 obligations remain outside this result.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex**
assistance in mathematics, both implementations, checking and writing.
Apache-2.0.

## Open next questions

- **Three original modes.** Fix (2,4,6), classify their exact complex support
  strata, and test character cuts with two common odd neighbors before trying
  a GL(4,C) synthesis. The five-stratum argument here does not extend without
  a new classification and four-term cost proof.
- **Shared COPY calls.** An explicit shared endpoint contract could change
  the separate-term objective. First produce a small legal two-term sharing
  construction and price gathering, frames and restoration. No such contract
  or complete physical invoice is supplied here.

`TASK.json` records why these questions matter and their blockers.
