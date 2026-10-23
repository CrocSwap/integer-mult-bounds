# Exact-search tooling for noncommuting words, and the KB2 six-distinct-value screen

**Scoped negative plus reusable tooling; no new kappa.** This package has two
parts. (1) `exact_search.py` is reusable, dependency-free exact-search tooling
for noncommuting word/tuple enumeration over group rings `F2[G]` and matrix
rings `M_r(F2[G])` (instantiated for `GL_2(F2)` and `Q8`), with prefix closure
bounds, memoized layer-ball digests, a signature DP, `GL_r` conjugation
reduction and SHA256-receipted parallel-safe batch splitting. (2) It is
demonstrated on the strictly alternating thirteen-call five-SWAP candidate of
open problem KB2: the complete **six-distinct-value** family is exhaustively
searched and **excluded** (zero survivors over 323,963,640 placements and
700,496 exact `M_5(F2[G])` product evaluations). Seven or more distinct
projector values are **not** covered. The selected result, the selected bit
supplier and `upstream/` are unchanged.

## Collision note (read first)

KB2 is open question 1 of
[`research/fiveswap-alt13-commuting-screen`](https://github.com/CrocSwap/integer-mult-bounds/pull/2317):
find or exclude the strictly alternating thirteen-call word at five fully
occupied coordinate-SWAP roles in the formal `F2[GL_2(F2)]`
rank-one-idempotent register model. While this session ran, Ross Richardson
posted
[discussion 1317 comment 18944151](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18944151)
(2026-10-15 08:01 UTC) establishing the exclusion analytically: the PR 1989
symmetric-adjacent-cut theorem, bridged to `F2[GL_2(F2)]` by the
product-preserving isomorphism `GL_2(F2) -> S_3`, gives exact cost `3t` for
every finite `R >= t`, all binary rank-one idempotents and arbitrary restored
dirty spectators — hence minimum 15 at `t = 5`
([PR 2415](https://github.com/CrocSwap/integer-mult-bounds/pull/2415),
package `research/gl2-swap-cut-corollary`). Per the session's pair-collision
rule the find-or-exclude object is **released to PR 2415** and not claimed
here. What this package adds is the solver tooling the predecessor named as
its blocker, and an explicitly independent, search-level audit of the
exclusion on the largest noncommuting family our tooling closes exactly. The
two lines agree; the search is not a proof of PR 2415's theorem and PR 2415's
theorem is not a replay of this search.

## Model (unchanged coordinate-CNOT line)

Let `a=[[1,1],[0,1]]`, `b=[[1,0],[1,1]]`, `s=aba=bab` in `G=GL_2(F2)`,
`R=F2[G]`. A paid call is `D_N(g)=I+([g]+1)N` with `g in {a,b}` and
`N=uv^T` a binary rank-one idempotent (`v^T u=1` over `F2`); there are
`(2^5-1)*2^4 = 496` such projectors in `M_5(F2)`. Free scalar `GL_5(F2)`
mixing is normalized by augmentation. The target is `T=[s] I_5` at exactly
`t=r=5` fully occupied roles with arbitrary dirty inputs restored exactly;
acceptance is equality of all formal group-algebra coefficients in
`M_5(F2[G])`. Word direction is irrelevant on the palindromic alternating
label word `(ab)^6a`.

## Tooling (`exact_search.py`, Python stdlib only)

- `Group`/`GroupAlgebra`: `F2[G]` from any multiplication table
  (`gl2f2()`, `q8()`), exact bit-mask convolution.
- `M_r(F2)` and `M_r(F2[G])` arithmetic, rank-one idempotent alphabets,
  call matrices, word products, targets.
- Quotient projections: the sign quotient `F2[epsilon]/(epsilon^2)` and the
  natural 2-dimensional quotient. The combined map is checked to be an
  algebra isomorphism `F2[S_3] = F2[epsilon]/(epsilon^2) x M_2(F2)`, so the
  sign equation plus the four natural-quotient block equations are
  **equivalent** to the full endpoint (machine-checked on random and
  structured tuples).
- The `C`-matrix invariant `C_ij = v_i^T u_j`: `C^2 = C`, `rank C = 5`, and
  the four projected block equations `C D^{p,q} C = C` (the predecessor's
  handoff equations) are equivalent to the full endpoint.
- Search engine: BFS layer-ball digests (calibrated against the recorded
  `Q8` balls `[1, 12, 110, 936]`), meet-in-the-middle join helper, the sign
  prefix closure bound `rank(I - S_k) <= 13-k`, `GL_r` conjugation
  reduction, SHA256-receipted `shard_split` batches for parallel workers,
  and the signature DP + exact evaluator used below.
- Note on arithmetic: `F2[G]` is noncommutative, and the call scalars
  `[g]+1` do **not** commute with group-ring entries of other calls. The
  evaluator keeps every scalar at its own word position; a control compares
  it against the generic product engine on random frame-plus-extra tuples
  and on mutations.

## Classification of low-distinct-value tuples

Written proofs with exhaustive small-instance controls (over `F2^3`, 28
projectors):

1. **Parity and rank.** The sign equation `sum N_i = I_5` forces the number
   `k` of odd-multiplicity projector values to satisfy `k >= 5` (rank) and
   `k = 1 (mod 2)` (trace).
2. **Dual-frame lemma.** `t` rank-one idempotents summing to `I_t` are
   automatically a dual frame: `C = V^T U` is a `t x t` idempotent which is
   invertible because `UV^T = I`, hence `C = I`, i.e. `v_i^T u_j =
   delta_ij`. Exhaustive over `F2^3` at `k = t = 3` (28 frames); at
   `k = t+2` noncommuting summand sets exist (336 of them), so the collapse
   is exactly `k = t`.
3. Hence any KB2 solution uses **at least 6 distinct projector values**;
   `<= 5` distinct values are pairwise commuting, the family already
   excluded by
   [`research/fiveswap-alt13-commuting-screen`](https://github.com/CrocSwap/integer-mult-bounds/pull/2317)
   (every frame class needs at least three positions, so 13 cannot fill 5
   classes).
4. **At exactly 6 distinct values** the 5 odd-multiplicity values form a dual
   frame (free `GL_5` conjugation puts them at the coordinate projectors
   `e_c e_c^T`) and the sixth value `W` has even multiplicity
   `m_W in {2,4,6,8}` (`5 + m_W = 13` with all class multiplicities odd and
   `m_W <= 8`). `W` is automatically noncommuting with the frame unless it
   equals a frame projector, which is excluded by distinctness. This family
   is what the search exhausts.

## Search method and receipts

For each `m = m_W`, one signature DP runs over **all** placements at once: a
state is the `S_5`-canonical tuple of (class segment products, parity) rows
plus the label word at the extra positions. The extra projector `uv^T` is
kept symbolic; every one of the 491 non-frame rank-one idempotents `W` is
tested against every signature by the exact `M_5(F2[G])` evaluator (the
predecessor's four block equations are recovered as an equivalent form). The
`S_5` canonicalization is complete because conjugation by any
`P in GL_5(F2)` preserves the target and every `W` is tested. A sound
diagonal pre-filter drops candidates early: the empty-subset term fixes entry
`(c,c)` to the class-`c` segment product, and every other term carries the
factor `u_c v_c`, so a mismatch with the target diagonal forces `u_c v_c=1`.

Complete run (CPython 3.12, one core, 321 s):

```text
m2: assignments=233719200 signatures=53055  peak_dp=850772   evals=255078 survivors=0
    sig_sha256=67e78c9d772d8a0d0296a290108874a3ff65b86563709e4b0a4137148e5fa693
m4: assignments=82882800  signatures=183711 peak_dp=6728684  evals=403608 survivors=0
    sig_sha256=597a936da3fe9cf619aeb2fc104a6b4f8bbeaa7e52dcd68156577dabababde60
m6: assignments=7207200   signatures=40523  peak_dp=9878765  evals=40523  survivors=0
    sig_sha256=84eb289160a6eecae3398b300a1314de49c60919107aceb5b5bc0cc7a97d4fd3
m8: assignments=154440    signatures=1287   peak_dp=10218769 evals=1287   survivors=0
    sig_sha256=b247c3baf5e3ba07d51165f669306a30c598a9a2f012534c2baaa4bb9d015980
PASS_KB2_ALT13_NONCOMMUTING_TOOLING assignments=323963640 evaluations=700496
survivors=0 frontier=d6_complete_d_ge_7_open no_new_kappa elapsed=321.4s
```

`assignments` counts (extra-position pattern, class assignment) pairs with
all class multiplicities odd — i.e. the complete six-distinct-value placement
space at `t = 5`, `n = 13`. **Zero survivors**: no six-distinct-value tuple
realizes `[s] I_5` in thirteen strictly alternating calls. Together with the
predecessor's commuting exclusion this leaves only tuples with **seven or
more distinct projector values** as possible KB2 escapes; PR 2415's theorem
excludes those as well, analytically.

## Controls (`verify.py`, all passing)

- Direct words for `t = 1, 3, 5` (3/9/15 calls) reach `[s] I_t`; a mutated
  word fails.
- The sign x natural image is an algebra isomorphism (bijective,
  multiplicative), and sign + natural equations agree with the full endpoint
  on 300 random tuples; the `C`-invariant agrees on the same tuples.
- `GL_5` conjugation invariance of the endpoint.
- Classification controls over `F2^3`: 28 dual frames at `k = t`;
  336 noncommuting 5-summand sets at `k = t+2`; no 4-summand identity.
- Fast evaluator equals the generic product engine on random frame-plus-extra
  tuples; corrupting one segment product changes the result (mutation).
- `Q8` layer balls `[1, 12, 110, 936]` reproduce the recorded
  [`q8-central-commutator-pair`](https://github.com/CrocSwap/integer-mult-bounds/pull/1822)
  calibration (cross-algebra reuse).
- Shard manifests partition `0..999` and their SHA256 receipts are stable.
- Sign prefix closure bound accepted and rejected cases.
- **Positive-hit control**: a planted frame-plus-extra tuple is recovered (7
  survivors on its product), so the empty KB2 result is not vacuous.
- **Tiny completeness cross-check** at `t = 2`, `n = 6`: the signature search
  returns exactly the direct enumeration of the same family (non-vacuous,
  target = a planted family tuple).
- `tests/test_research_exact_word_search.py` re-runs 17 failure-sensitive
  unit controls (including the two caught during development: a wrong
  Gauss-Jordan pivot order and the noncommutative scalar placement).

## Coverage and what is not checked

This is a finite exact screen of a declared family plus written lemmas. It
does **not** cover tuples with seven or more distinct projector values, does
not reprove PR 2415 or PR 1989, and makes no partial-occupancy (`r > t`),
changed-tariff (asymmetric label prices, rank-two unit prices),
changed-endpoint or physical/compilation claim. No Lean formalization,
independent human review, precision/tape or analytic transfer is claimed. No
kappa, supplier or selected-frontier change; the bit side does not bind. The
result is author-checked only.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -I -B research/kb2-alt13-noncommuting-tooling/verify.py
python3 -B -m unittest tests.test_research_exact_word_search -v
python3 scripts/research_package.py --package research/kb2-alt13-noncommuting-tooling --check-only
```

Expected marker: `PASS_KB2_ALT13_NONCOMMUTING_TOOLING assignments=323963640
evaluations=700496 survivors=0 frontier=d6_complete_d_ge_7_open no_new_kappa`.
`make` is not required and is unavailable on the recording host.

## Task, overlap and credit

Base main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4,
card `bit-new-register-model` (chooser OS nonce `56cf67ad450f0a4b6c78411360a6654f`),
scope **changed** by the orchestrator's tooling mandate (an authorized
explicit open request); [TASK.json](TASK.json) records the reason. The claim
and its scope update are in
[discussion 1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18944685).

Predecessors and credit: Ross Richardson for
[PR 2415](https://github.com/CrocSwap/integer-mult-bounds/pull/2415)
(`research/gl2-swap-cut-corollary`, the concurrent analytic exclusion of the
same object, released to him) and
[PR 1989](https://github.com/CrocSwap/integer-mult-bounds/pull/1989)
(the `S_n` cut theorem); Ross Richardson
[`research/four-swap-full-occupancy`](https://github.com/CrocSwap/integer-mult-bounds/tree/main/research/four-swap-full-occupancy)
(rotation step, uniform cut consequence, open question 2);
Aaron Wang [PR 2317](https://github.com/CrocSwap/integer-mult-bounds/pull/2317)
(the commuting screen and the block-equation handoff this search consumes);
commdata2338
[PR 1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414) /
[PR 1491](https://github.com/CrocSwap/integer-mult-bounds/pull/1491)
(formal model, sign quotient); Gareth Davidson
[PR 1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333)
(free scalar normalization); Cinna Davis
[PR 1541](https://github.com/CrocSwap/integer-mult-bounds/pull/1541)
(workspace reasoning); the `Q8` calibration source
[PR 1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822).

Overlap refreshes at 2026-10-15 07:54Z and 08:34-08:36Z (620 open PRs, 1153
discussion records, complete pagination) found no other work on the
noncommuting thirteen-call tuple search or on exact-search tooling for this
line; the only KB2-object records are the predecessor and PR 2415. No
matches is not a novelty certificate.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance
in reasoning, implementation, verification and writing; no independent human
review). New work is Apache-2.0; predecessor sources and notices are
unchanged.

## Open next questions

1. **Do seven-or-more-distinct-value tuples need new machinery, or does the
   `C`-matrix DPLL close them?** Why it matters: it would give a search-level
   exclusion of all of KB2 independent of the PR 1989 bridge. First step:
   branch on the gap-layer bits `c_{ij}` with the quadratic idempotence
   equations `C^2 = C` as watched constraints and the four `C D^{p,q} C = C`
   equations as the leaf test. Blocker: the high-degree `Z` polynomials need
   propagators; the 78 free bits are not enumerable directly.
2. **Changed-charge variants of the five-SWAP word problem.** Why it matters:
   PR 2415's handoff lists changed operation/charge/endpoints as the
   remaining premises; asymmetric label prices (e.g. `price(a)=1`,
   `price(b)=2`) make longer `a`-heavy words competitive and the crossing
   rank no longer prices the minimum. First step: complete weighted minima
   for `t = 2` and `t = 3` by BFS with a weighted layer digest. Blocker: the
   weighted search needs length 9+ layers at `t = 3`; the current layer-ball
   engine is exponential in word length without the frame-family structure.
3. **Reusable tooling gaps.** Why it matters: the tooling is deliberately
   small. First step: a bit-sliced evaluator over candidate sets (the
   `u_c v_c` masks already exist) would make `m_W >= 6` searches cheap
   enough for wider algebras. Blocker: none scientific; it is engineering.
