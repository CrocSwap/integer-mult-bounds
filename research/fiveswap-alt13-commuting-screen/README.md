# Five fully occupied SWAP targets: no thirteen-call word with commuting projectors

**Scoped negative screen; no new kappa.** In the formal `F2[GL_2(F2)]`
coordinate-CNOT register model, this package screens the strictly alternating
thirteen-call candidate for five fully occupied coordinate-SWAP targets inside
the **pairwise-commuting projector subfamily**. The screen is complete and
excludes that family: every frame class needs at least three word positions, so
no partition of thirteen positions into five classes exists. In fact the same
argument shows `q >= 3t` for commuting projectors at any fully occupied target
count `t`, so the direct `3t` tariff is exact inside this family. Any
thirteen-call escape for five targets must use noncommuting scalar projectors.
The selected result, the selected bit supplier and `upstream/` are unchanged;
the bit side does not bind.

## Model (unchanged coordinate-CNOT line)

Let `a=[[1,1],[0,1]]`, `b=[[1,0],[1,1]]`, and `s=aba=bab` in `G=GL_2(F2)`,
`R=F2[G]`. A paid call is `D_N(g)=I+([g]+1)N` with `g in {a,b}` and `N=uv^T`
a binary rank-one idempotent (`v^T u=1`). Every call, including an undo, costs
one. Free scalar `GL_t(F2)` mixing is normalized by augmentation (credit:
PR1333). The target is `T=[s] I_t` at exactly `r=t` fully occupied roles with
arbitrary dirty inputs restored exactly. Equality is equality of all formal
group-algebra coefficients.

## Why thirteen calls, why alternating

`research/four-swap-full-occupancy` proves that any fully occupied `t`-target
word saving over `3t` has `q >= 2t+3` (every rotated cut carries both label
counts at least `t+1`), and that at equality the labels strictly alternate
(credit: Ross Richardson's rotation step and the PR1722 saturation lemma).
For `t=5` the sign trace `q = t mod 2` then leaves exactly one candidate below
the direct fifteen: `q=13`, strictly alternating. That package's open question
2 asks whether rank-one idempotent unknowns can realize it and names
noncommuting scalar-projector interactions as the blocker. This package closes
the commuting part of that question.

## Necessary conditions and the commuting reduction

Work in the natural quotient `R -> M_2(F2)` (`[g] -> g`). A call maps to
`I + (g+I) tensor N`; expanding the product, a subsequence of calls survives
exactly when consecutive picked labels differ, and contributes
`(N-product) tensor E(row of last label, col of first label)`. Comparing with
the target `I_t tensor (E12+E21)` gives, for every frame class position set
`S`, four mod-2 conditions on the label-alternating nonempty subsequences of
`S`: each of the four `(first label, last label)` counts `(a,a)`, `(a,b)`,
`(b,a)`, `(b,b)` must be **odd** (the empty subsequence cancels the `E11` and
`E22` identity terms).

**Commuting reduction.** The sign quotient (`[g] -> 1+epsilon` over
`F2[epsilon]/(epsilon^2)`) gives `sum N_i = I_t`. Pairwise-commuting distinct
rank-one idempotents are equal or mutually orthogonal (`phi_i v_j = 0`), and an
orthogonal distinct sum equal to `I_t` uses exactly `t` projectors forming a
frame with odd multiplicities (any extra even-multiplicity projector would
need `v=0`). Up to `GL_t` conjugation the word is therefore a coordinate-frame
word, and each of the `t` classes must satisfy the four conditions above.

**Size floor.** A class of size one or two fails the conditions for every
label word: one subsequence contributes to exactly one category; two positions
contribute to at most three. Hence every class has at least three positions and
`q >= 3t` in the commuting family. The direct word `aba` on each coordinate
attains `3t`, so the tariff is exact there. For `t=5`, thirteen positions
cannot fill five classes of size at least three.

## Checked results (`verify.py`, exact, stdlib only)

```text
PASS_FIVESWAP_ALT13_COMMUTING_SCREEN min_class=3 admissible_sets=1365 size_hist=3:91,5:455,7:546,9:247,11:26 partitions5=0 direct15_partitions=608 small_pairs=2046 commuting_pairs=196 frames3=28 no_new_kappa
```

- Formal product controls: the direct words for `t=1` (3 calls), `t=3` (9
  calls) and `t=5` (15 calls) reach `[s] I_t` exactly in `M_t(R)`.
- Complete screen of all 8,191 nonempty position sets of the strictly
  alternating thirteen-label word: 1,365 sets are admissible, the minimum
  admissible size is 3, and an exact-cover DP finds **zero** partitions of the
  thirteen positions into five admissible classes. All admissible sizes are
  odd, matching the sign equation's odd-multiplicity deduction.
- Positive structural control: the direct fifteen-call partition passes the
  conditions (608 five-class partitions pass in total).
- Failure controls: a mutated direct word fails the formal product; a
  size-one class is rejected; the universal size floor is checked
  exhaustively for every label word through length six (2,046 cases); an
  explicit noncommuting idempotent pair witnesses that the excluded family is
  strict.
- Reduction-lemma support: exhaustive over `F2^3` (28 rank-one idempotents):
  every commuting pair is equal or orthogonal (196 commuting pairs), and 28
  orthogonal triples sum to `I_3`.

## Scope and what is not checked

This is a finite exact screen of a declared subfamily plus a written reduction,
not a general exclusion of thirteen-call words. No noncommuting tuple search is
attempted; the general block equations above are recorded as the handoff for
that search. No partial-occupancy (restored dirty extras, `r > t`) claim is
made: at partial targets the rotation and the block comparison change shape
(see the workspace boundary in `research/four-swap-full-occupancy`). No Lean
formalization, independent human review, physical compilation, hosting,
precision/tape, analytic transfer or selected-supplier cold replay is claimed.
The result is author-checked only.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -I -B research/fiveswap-alt13-commuting-screen/verify.py
python3 scripts/research_package.py --package research/fiveswap-alt13-commuting-screen --check-only
```

Expected marker: `PASS_FIVESWAP_ALT13_COMMUTING_SCREEN ... partitions5=0 ...
no_new_kappa`. `make` is not required and is unavailable on the recording
host.

## Task, overlap and credit

Base main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4,
card `bit-new-register-model`, chooser OS nonce `c91910338314e7e3bba60391fdf5bb54`
(track `bit-mechanisms`). [TASK.json](TASK.json) records the refined scope.
The claim is in
[discussion 1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18940800).

Predecessors and credit: commdata2338 (PR1414/PR1491) for the formal model,
sign invariant and swap results; Gareth Davidson (PR1333) for scalar
normalization; Cinna Davis (PR1541) for workspace reasoning; Ross Richardson
(PR1722) for the saturation lemma and `research/four-swap-full-occupancy` for
the rotation step and uniform cut consequence whose open question 2 this
package narrows. `research/three-swap-cnot-census` and
`research/three-swap-compression-seed6` closed `t=3` at any workspace;
`research/four-swap-r4-cnot` records the `t=4` residual search. Overlap search
refreshed 2026-10-15 04:42 UTC with complete pagination (526 open PRs, 994
discussion records); no claim on the `t=5` object was found. No matches is not
a novelty certificate.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance;
no independent human review). New work is Apache-2.0; predecessor sources and
notices are unchanged.

## Open next questions

1. **Can noncommuting rank-one idempotents realize the strictly alternating
   thirteen-call word for five fully occupied targets?** Why it matters: it is
   the only remaining potential saving below the direct fifteen-call tariff at
   five roles in this alphabet. First step: feed the four block equations and
   the sign equation to a quadratic/backtracking search over noncommuting
   tuples, smallest falsifying instance first (one class near-commuting).
   Blocker: no SAT/SMT tooling on this host; the noncommuting
   scalar-projector interactions are exactly where the reduction stops.
2. **Does the commuting obstruction survive one restored dirty extra
   register?** Why it matters: it would extend the `q >= 3t` commuting tariff
   toward the `t=4, r=5` workspace question of `research/four-swap-r4-cnot`.
   First step: re-derive the block comparison for `P = diag(I_t, 0)` and test
   the four conditions on the smallest coupled projector example. Blocker: at
   partial targets conjugation leaves the paid alphabet (the recorded workspace
   boundary), so the reduction needs a replacement for the frame argument.
