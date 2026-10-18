# The balanced ten-call four-SWAP residual: the J^2 layer cannot decide it

**Scoped obstruction plus scoped search failure; no new kappa.** The selected
result, the selected bit supplier and `upstream/` are unchanged.

Four coordinate-SWAP targets `T = diag([S],[S],[S],[S])`, `S = aba = bab`, at
exactly `r = 4` registers in the formal `F2[GL_2(F2)]` rank-one-idempotent
register model: can a **ten-call word with exactly five `a`-labels and five
`b`-labels** realize `T`? This is the balanced residual of the four-SWAP line
after [PR1705](https://github.com/CrocSwap/integer-mult-bounds/pull/1705)
narrowed the minimum to `q in {8,10,12}` and the concurrent label-saturation
claim
[discussion 1715](https://github.com/CrocSwap/integer-mult-bounds/discussions/1715)
put "the ten-call balanced case" outside its session. The handoff
[comment 18918391](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18918391)
proposed deriving the `J^2`-coefficient-layer bound in `F_2[G]/J^3`
(`sum E_i + sum_{i<j} E_i E_j = T - I`) to exclude `q = 10` in writing.

This package does that derivation and records the exact obstruction: **the
route is empty in this algebra.** The balanced question itself remains open.

## Model and reduction

`R = F2[GL_2(F2)]`, `a = [[1,1],[0,1]]`, `b = [[1,0],[1,1]]`,
`S = aba = bab = [[0,1],[1,0]]`. Paid calls are `I + ([g]+1) N` with
`g in {a,b}` and `N = u v^T` a binary rank-one idempotent (`v^T u = 1`);
free scalar `GL_r(F2)` mixing is granted between calls; every call is charged
and all four registers carry arbitrary dirty inputs restored exactly.

Free mixing normalizes away: absorbing the scalar factors conjugates the `N`
(which stay rank-one idempotent), and the augmentation of the boundary
`[s] I_r` forces the accumulated scalar to the identity. So a word is a pure
product `prod (1 + eps_i)`, `eps_i = ([g_i]+1) N_i`, and any word realizing
`T` satisfies `sum_i N_i = I_r` by the sign quotient (every label is odd).

## Result 1: `J^2 = J^3`, so the proposed layer bound is vacuous

Exact linear algebra on `R` (bit vectors, `verify.py`):

| subspace | `J^1` | `J^2` | `J^3` |
|---|---|---|---|
| dimension | 5 | 4 | 4 |

The augmentation powers stabilize at the second step: `J^3 = J^2`, so
`R/J^3 = R/J^2` is just the sign quotient `F2[z]/(z^2)`, in which
`red([a]+1) = red([b]+1) = red([s]+1) = z` and both pair terms
`P = ([a]+1)([b]+1)` and `Q = ([b]+1)([a]+1)` vanish. The word expansion
lemma

```
prod (1 + eps_i) = 1 + sum eps_i + sum_{i<j} eps_i eps_j    (mod J^3 M_r)
```

is exact and is checked on seeded random words (same-label pairs already
vanish identically because `([a]+1)^2 = ([b]+1)^2 = 0`). But after reduction
the whole layer equation collapses entrywise to `sum_i N_i = I_r`, nothing
more (for a target that restores a role with the identity boundary, the
right-hand side is the target's own z-coefficient matrix instead: `diag(I_4,0)`
at `r = 5` with one restored fifth role, whose target augmentation is zero).
The verifier machine-checks the equivalence
(`layer check holds  <=>  sum N_i = I_r`) on 200/200 random instances, and
the search below confirms it exhaustively on its own domain: every one of the
5,771,556 balanced labelings passed the layer check, because the sampler
conditions on `sum N_i = I_r` — a condition the sign quotient already forces
on any candidate word.

So the handoff's proposed `J^2`-coefficient-layer bound cannot exclude
`q = 10`, `q = 8`, or anything else above the two-call case: in `F2[G]` there
is no second augmentation layer to read a coefficient bound off. Any written
exclusion of the balanced profile must use word order or a different quotient
of `F2[G]` (for example the natural two-dimensional image `M_2(F2)`, as in
PR1705's census, or the commutator `[([a]+1),([b]+1)] = [ab]+[ba]`, which
survives in `J^2` but is invisible in `R/J^3`).

## Result 2: bounded exact search of the balanced profile

With `sum N_i = I_r` justified as a lossless reduction, the sampler draws
ordered ten-tuples of the 120 binary rank-one idempotents conditioned on
`sum N_i = I_4` (each valid ordered tuple uniform), and checks all 252 ways
to place the five `a`-labels, first at the `J^3` layer and then, for every
layer-feasible labeling, at **full formal level** in `M_4(F2[G])` (96-bit
states, exact bit arithmetic).

Recorded run (`--full`, seed 20261014): 6,000,000 samples, 22,903 valid
tuples, 5,771,556 labelings, **0 full-formal hits**. This is a scoped search
failure over that sampled domain, not an impossibility theorem: it does not
cover the unsampled valid tuples, `q = 8` profiles, `r = 5`, or any word with
a different label profile.

Controls: the four direct words (`aba` at `r = 1`; `aba|bab` at `r = 2`;
`aba` on three registers at `r = 3`; four disjoint `aba`/`bab` words at
`r = 4`, 6a6b balanced) hit their targets exactly in `M_r(F2[G])`; four
mutation controls (dropped call, flipped label, dropped target, perturbed
`N`) fail; the search finds known-solvable instances at `r = 1` (`q = 3`)
and `r = 2` (`q = 6` balanced, 3,254 witnesses); a strict-relaxation honesty
control exhibits a layer-feasible word that fails full equality; conjugation
of `N` by `GL_r(F2)` preserves the idempotent family; and two hand-derived
pins (`([a]+1)^2 = 0`; `([a]+1)([b]+1)([a]+1) = [aba]+[ab]+[ba]+[b]`) bind
the group algebra implementation. A restored-role regression control pins the
corrected `r = 5` sign quotient: the fifth role's target augmentation is zero,
`sum N_i = diag(I_4, 0)`, and an `I_5` total fails the endpoint layer equation
(see open question 2).

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -I -B research/four-swap-balanced-j3-layer/verify.py --full
python3 -I -B research/four-swap-balanced-j3-layer/test_verify.py
python3 scripts/research_package.py --package research/four-swap-balanced-j3-layer --check-only
```

Expected direct-replay line (`--full`, about 6 minutes):

```text
PASS_FOUR_SWAP_BALANCED_J3_LAYER balanced_5a5b_unrealized_in_search layer_hits=5771556 no_new_kappa
```

`EXPECTED.json` pins the deterministic counts for both the default and the
full budget; the verifier fails on any mismatch. `--emit` prints a receipt
without comparing.

## Task and overlap

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; card `bit-new-register-model`,
scope key `7084092dd726e7ba1f2f`, priority revision 3, chooser nonce
`cd67986ec4d736b6ed683332001aecde`, track `bit-mechanisms`. Claim:
[discussion 1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18919080).
[TASK-CARD.md](TASK-CARD.md) records the pre-computation card; [TASK.json](TASK.json)
the refined scope; [SOURCES.json](SOURCES.json) the exact pins.

Refined-object overlap searches (`find_overlap.py` with 'balanced ten-call',
'five of each label', 'ten-call balanced', 'augmentation layer', 'F2[G]/J3'
at 07:53–07:54 UTC over 410 open PRs and 358 discussions, complete
pagination) matched only
[discussion 1715](https://github.com/CrocSwap/integer-mult-bounds/discussions/1715),
which explicitly excludes this case. Coverage excludes arbitrary diffs and
nested files; no match is not a novelty certificate.

## Limitations and remaining obligations

Not checked: Lean or independent human proof review; a selected-supplier cold
replay; physical, compiler, hosting, precision or tape admission; the `q = 8`
profiles; `r = 5` with a restored dirty extra; label profiles other than
(5,5); unsampled valid tuples of the balanced domain. No claim is made that a
balanced ten-call word does or does not exist; no new supplier, recursive
profile or kappa follows; the selected frontier is unchanged.

## Open next questions

1. **Order-sensitive exclusion (or construction) for the balanced (5,5)
   profile.** It decides whether the four-SWAP minimum is 10 or 12 once
   saturation lands. First step: evaluate every balanced candidate at the
   natural image `M_2(F2)` (PR1705's homomorphic image) with a 5+5 meet, or
   derive a commutator-layer bound using `[ab]+[ba] in J^2`, which `R/J^3`
   cannot see. Blocked by: the `J^2 = J^3` collapse recorded here rules out
   any purely augmentation-layer argument.
2. **The same balanced question at `r = 5` with one restored dirty extra.**
   Smallest falsifying instance of "workspace cheapens the tariff". First
   step: rerun the conditioned sampler at `r = 5`, target
   `diag([S],[S],[S],[S],1)`, conditioning on `sum N_i = diag(I_4, 0)`:
   the restored fifth role carries the identity boundary, so its target
   augmentation is zero and the sign quotient (register-count independent)
   forces the fifth diagonal entry of `sum N_i` to be 0. The earlier
   `sum N_i = I_5` wording was wrong and would exclude every solution to that
   endpoint: the four disjoint `aba`/`bab` control word with the fifth role
   restored realizes `diag([S],[S],[S],[S],1)` exactly and has
   `sum N_i = diag(I_4, 0) != I_5`, so an `I_5`-conditioned sampler rejects
   it. `verify.py` and `test_verify.py` pin the corrected condition by exact
   check. Blocked by: nothing; it is open compute.

## Credit and license

Prepared by Aaron Wang, with help from opencode. Predecessor credit:
commdata2338 ([PR1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414),
[PR1491](https://github.com/CrocSwap/integer-mult-bounds/pull/1491) — model,
sign parity, three-SWAP finite result), Gareth Davidson
([PR1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333) —
free-scalar normalization), Cinna Davis
([PR1541](https://github.com/CrocSwap/integer-mult-bounds/pull/1541) —
arbitrary-workspace three-SWAP theorem), Aaron Wang
([PR1705](https://github.com/CrocSwap/integer-mult-bounds/pull/1705) —
four-SWAP `r = 4` bounds and the 4+4 obstruction measurement), Ross
Richardson
([discussion 1715](https://github.com/CrocSwap/integer-mult-bounds/discussions/1715) —
concurrent saturation claim, complementary). New work is Apache-2.0;
predecessor sources and notices remain unchanged. No general rank principle
or literature-priority claim is made.
