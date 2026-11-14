# Global funding under arbitrary helper dependencies

## Finding

I independently confirm the helper-only funding obstruction for the unchanged #7481 native word, under the retained original helper-coordinate interface. Every subset of the 468 main-free MOVE rows is funded by the minimum target-rank price of a helper-column basis, for Gaussian tariffs `r^(1-kappa)` throughout `0 <= kappa <= 1/4`. The full row set has rank 463 and five dependencies; after decomposing its row matroid, every dependent subset in the four nontrivial row blocks passes the exact integer envelope. Thus charging the lost helper targets costs at least the saved MOVE price, even with preparation, frame conversion, storage, zeroing, and cleanup granted for free.

This result excludes a positive net saving obtained by zeroing any set of these 468 MOVE occurrences through dependencies among the original helper inputs while preserving arbitrary retained original helper coordinates. It does not cover changed scalar contacts, the 5,811 MOVE rows with main coefficients, changed native words, additional productive credit for rotated coordinates, or an emitted physical implementation/admission.

## Source reconstruction and exact checks

- Native word SHA-256: `acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9`.
- Replayed the full 76,475-instruction program over all 1,501 independent public input coordinates using exact rational arithmetic. Reconstructed 400 main coordinates and 1,101 helpers from the word, verified every listed frame is an independent GF(2) basis, validated all owner lifetimes and final charts, checked every helper endpoint is its original unit row, and checked main endpoints remain helper-independent.
- Independently extracted 468 nonzero main-free MOVE rows over 806 used helper columns. Each of the other 5,811 MOVE rows has a nonzero main coefficient. The fresh 468 row records and every helper target-rank weight match the frozen B inventory byte-semantically after replay.
- The paid rank of a MOVE is the absolute source/destination frame-rank difference; helper target rank is the original helper's final-frame rank minus its initial-frame rank. All are in 1..9. For every one of the 468 rows, the paid rank is no larger than the target rank of every helper in that row's support; the minimum target-to-paid linear-rank ratio is exactly 1.

The independently computed exact-Q rank of the 468-by-806 matrix is 463. My exact echelon basis has 463 rows; a separate elimination modulo prime 1,000,003 gives 463 pivots and a nonzero maximal minor (determinant up to row/column permutation is 865,310 modulo the prime). The five remaining source rows each have a separately stored rational relation on the basis; direct exact summation verifies every relation is zero. These relations span the full five-dimensional dependency space.

Support connectivity gives 94 components. The largest has 347 rows and 669 helper columns, exact rank 342 and nullity 5; the remaining 121 rows are independent. The five exact fundamental relations partition the dependent elements into four row-matroid blocks of sizes 11, 5, 5, 5, with ranks 9, 4, 4, 4. The giant has 321 coloops in addition to those 26 dependent elements. Several of the dependent blocks share helper columns with rows in other matroid components; observed external support-overlap counts are 8/9, 6/6, 6/7 and 42/51. This is why the composition argument below uses a determinant expansion rather than assuming disjoint column supports.

## Local subset funding

All 2,140 nonempty subsets of the four dependent blocks were ranked independently over Q: 2,109 are independent and 31 are dependent. Independent subsets are funded by the pointwise support condition. For any independent row set `S`, every nonzero full-rank minor has a nonzero determinant permutation pairing each row to a distinct helper column in that row's support. Each paired helper target rank is at least that row's paid rank, so every column basis has at least the paid price for any increasing tariff.

For each of the 31 dependent subsets `S`, I computed the exact minimum *linear target-rank sum* of a column basis from prefix ranks, without using the author's greedy column selection. If `rho = rank_Q(M_S)` and `C_k = {h : R_h <= k}`, then

\[
\beta(S)=\min_{J\text{ column basis}}\sum_{h\in J}R_h
 = 9\rho-\sum_{k=1}^{8}\operatorname{rank}_{\mathbb Q}(M_S[:,C_k]).
\]

For any basis `J`, its sum equals `9*rho - sum_{k=1}^8 |J intersect C_k|`. The count |J∩C_k| is at most the rank of the restricted columns; the increasing-weight matroid greedy basis attains all eight prefix ranks, proving the formula. The independent implementation records all eight ranks per dependent subset in its returned subset document.

All 31 satisfy the exact integer inequality

\[
6\beta(S)\;\ge\;11\sum_{e\in S} r_e.
\]

The minimum ratio is exactly 11/6, attained by events `32944, 32945, 32947, 32951, 33081, 33089, 33091, 33100` with basis target-rank sum 44 and paid-rank sum 24. The minimum integer margin `6*beta - 11*P` over the 31 checks is zero.

For `R in [1,9]` and `0 <= kappa <= 1/4`,

\[
R^{1-\kappa}\ge R\,9^{-1/4}>\frac{6}{11}R,
\qquad r^{1-\kappa}\le r,
\]

where the strict rational envelope is `9*6^4 = 11664 < 14641 = 11^4`. Thus the minimum target-basis price for every dependent `S` is at least its paid MOVE price throughout `0 <= kappa <= 1/4`. The independent-set argument gives the same conclusion. No floating-point comparison is used.

## Combining row-matroid components with shared columns

The exact row-dependency space has dimension five and is spanned by the five checked relations. Their supports yield four disjoint dependent blocks; all other rows have coefficient zero in every dependency and are coloops. Hence for any selected MOVE set `S`, its row space is the direct sum of the selected row spaces `S_C` from these components, and its rank is the sum of their ranks.

Let `J` be any global column basis for `M_S`. Choose an independent row basis inside each selected component; their concatenation is a row basis for the global row space. The square minor on these rows and columns (J) is nonzero. Laplace expansion along the row-component blocks has at least one nonzero term. That term partitions `J` into disjoint column sets `J_C`, with each block minor nonzero; therefore `J_C` is a column basis for `M_{S_C}`. Consequently

\[
\sum_{h\in J}R_h=\sum_C\sum_{h\in J_C}R_h\ge\sum_C\beta(S_C).
\]

The same expansion with each column weighted by any nonnegative price f(R_h) gives the identical inequality with local minimum f-prices. Taking the minimum over global `J` proves that shared helper-column support cannot reduce the funding lower bound below the sum of local bounds. The proof needs no disjointness of supports. The executed overlapping-support control gives two independent rows on the same two helper columns: each one-row minimum basis price is 1, while the global minimum is 3, so the global lower bound still dominates the sum 2. A parallel-row control rejects a false direct-sum split (component-rank sum 2 versus true global rank 1).

## Arbitrary helper relations with retained coordinates still surjective

For a zeroed row set `S`, write its helper coefficient matrix as `M_S = [M_{S,I} | M_{S,H}]`, where `I` are original coordinates that remain independently productive and `H` are original helper coordinates demoted by the proposed restriction. Suppose the allowed helper assignments form any relation over `Q^I x Q^H`, not necessarily a linear graph, whose projection onto `I` is surjective and whose rule is independent of arbitrary main inputs. If every row in `S` must vanish for every allowed assignment, then for each `u` in `Q^I` there is an `h` in `Q^H` with

\[
M_{S,I}u+M_{S,H}h=0.
\]

Therefore `im(M_{S,I})` is contained in `im(M_{S,H})`, and so

\[
\operatorname{rank}(M_S[:,H])=\operatorname{rank}(M_S).
\]

This necessity uses only surjectivity and row cancellation; it does not assume the helper assignment is linear or single-valued. For a fixed linear graph `h = B*u`, the same rank equality is also sufficient to solve for `B`, but I make no such sufficiency claim for arbitrary nonlinear relations.

The rank condition means that `H` must contain a column basis for `M_S`. Since target prices are nonnegative, its lost f-price is at least the minimum f-price of a column basis. The linear basis sum beta(S) supplies the (6/11) power-price lower bound used above; it is not itself the lost power price. The verified funding inequalities therefore rule out positive net savings for this class of helper restrictions even when preparation itself is granted free. Restrictions that reduce the allowed retained `I` assignments, depend on main inputs, use new carrier coordinates, or change original productive target directions are outside this statement.

## Controls and evidence

- Executed a wrong-source-hash guard; it rejects a changed hash. The exact native and B-row artifact pins are checked before comparison.
- Executed an overlapping-column direct-sum control, a false-direct-sum rejection control, and an underpriced-target mutant. The last has target basis sum 2 against paid sum 4, so its margin `6*beta - 11*P = -32` and is rejected.
- `graph/rebuild_engine.py`, `graph/structure_engine.py`, and `graph/subset_engine.py` all pass normally and under `python -O`; each normal/optimized output JSON is byte-identical. Each stage is below 60 seconds; full native row replay takes about 10 seconds.
- No native word was changed, and no supplier or physical word was emitted.

## Files

- `graph/rebuild_engine.py` and its in-memory rebuilt document: independent pinned full-source row extraction.
- `graph/structure_engine.py` and its in-memory structure document: exact/modular global rank, five relations, support graph, matroid blocks, target-rank domination.
- `graph/subset_engine.py` and its in-memory subset document: all local exact subset ranks, prefix-rank basis prices and controls.
- `SOURCES.json`: source and output hashes, including normal/optimized reproducibility pins.


## Whole-array relations and complete caller

The necessary rank condition also applies to helper preparations that use
operators on complete arrays. Choose any nonzero complete array z and let the
retained inputs range over arbitrary scalar multiples a_i z. Apply a linear
functional taking z to 1 to each equation of the proposed zero-MOVE system.
This gives a scalar solution in the demoted coordinates for every tuple a_i.
Thus the same scalar image inclusion and rank equality are necessary. Rational
matrices have the same rank over Q and C. The functional is a proof device, not
an additional physical input read or an implementation instruction. Arbitrary
joint retained inputs, independence from mains, and exact source row identities
remain essential; a restricted retained-input domain may not satisfy the premise.

Every non-main-free original MOVE has a nonzero main coefficient. It cannot
vanish for every independent main assignment under a main-independent helper
restriction. Hence the extracted 468 rows exhaust all possible zero-MOVE
credits in this scope. Native paid ranks, scalar contacts, charts and all other
instructions are fixed; any new preparation or retirement costs are granted
free. The result does not include deleting a nonzero MOVE through a cache.

The enclosing verifier independently reconstructs the full retained signed
caller: 17 native calls, 22,461 productive fields, 110,519 paid positions and
linear-rank surplus 1,424. Lost original helper targets and zero-MOVE savings
both occur once per selected invocation. Each invocation may select its own
helper relation; its nonpositive gain sums to a nonpositive full caller gain.
The base source is unselected #7481; no admission or new kappa follows.

## Portable replay and attribution

`graph_verify.py` explicitly loads the bundled standard-library engines by
absolute local paths, including under isolated Python. It uses the existing
exact native input and the three pinned author certificates in `graph/inputs`.
The independent native replay reconstructs every row before comparing with the
author inventory. Structure, exact relations, the independent prime minor and
prefix-rank basis sums are freshly recomputed, not trusted from stored results.
The author used greedy weighted bases; the independent price calculation uses
all eight prefix ranks. Input hashes bind provenance and are additional to the
mathematical checks, not substitutes for them. Runtime writes no package files.

The preceding coordinate and matching-boundary subspace theorems remain valid
in their stated scopes. This extension permits correlations across different
boundary groups while retaining the original-coordinate productive interface.
It excludes assigning old prices to new decoded target types or using main-
dependent helper preparation. All five foundational assumptions remain retained.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance in
author derivation, a separate exact source/price implementation, adversarial
review and packaging. Retain Clear1nsight #7481, Rohan Arun #7113, ToikY #7307
and the complete original NOTICE lineage. The matroid exchange, determinant
matching and Laplace identities are standard mathematics; their source-bound
certificate and interface composition are this contribution. Algorithmic
independence does not mean independent human or formal-kernel acceptance.
