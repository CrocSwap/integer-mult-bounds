# KB3d — the `(11,6)/(6,11)` remainder rows `(5,1),(6,0)`: impossible by an exact Fourier/Parseval identity

**Set-level finite result, no words enumerated. Both remaining rows of PR
2542's "No 17-point set covers `F2^7`" question are PROVEN impossible: for a
parity split `(|E|,|O|) = (11,6)` (and its mirror `(6,11)`) the 66 cross sums
cannot cover the 64 odd masks of `F2^7` at all. The whole `(11,6)/(6,11)`
family is excluded, so with PR 2542 (`(9,8)/(8,9)`) and PR 2773 (`(10,7)/(7,10)`
exactly; `(3,3),(4,2)` demoted by the k=11 census) the literal claim is
complete at the set level. No new kappa.**

Exact obstruction (both parity orders): the forced odd-coverage remainder
`rho` has total `2`, which squeezes the even-cardinality side's characters to
`{0, +2, -2}` off the all-ones hyperplane, while Parseval demands a remainder
of `696` over the `126` remaining character squares of at most `4` —
`696 > 504`, deficit `192`.

## Object and the recorded remainder

In the PR943 prefix-walk model
([Ross Richardson, `research/universal-connector-boundary`](https://github.com/CrocSwap/integer-mult-bounds/pull/943)),
a restored seven-source singleton word is universal exactly when its prefix
set `P` covers: `P + P = F2^7`. PR 2542
([Aaron Wang](https://github.com/CrocSwap/integer-mult-bounds/pull/2542))
excludes length 18 and asserts "No 17-point set covers `F2^7`". PR 2773
([Aaron Wang](https://github.com/CrocSwap/integer-mult-bounds/pull/2773),
package `research/f7-17point-cover-audit-seedcfa215c2`) audited that claim at
the set level: the counting-feasible 17-point splits `(|E|,|O|)` are exactly
`(9,8),(8,9),(10,7),(7,10),(11,6),(6,11)`; `(9,8)/(8,9)` die in the
pair-representation identity; `(10,7)/(7,10)` are excluded exactly against the
census floor; and `(11,6)/(6,11)` reduce to the row class
`(e_ex, b_ex, c) = (e, 6-e, 1)` with `shared = 1`, of which the completed k=11
census demotes `(3,3)` and `(4,2)`. **The whole remainder is the two rows
`(5,1)` and `(6,0)` (pair-sum excess 5 and 6 at 11 points), mattering only at
`L = 22`.** This package decides them: both impossible, by an identity rather
than an enumeration.

## The lemma (exact hypotheses)

Write `S = A u B` with `A` in the even-weight coset `E` of `F2^7` (size `s`)
and `B` in the odd-weight coset `O` (size `t`), `s + t = 17`. Sums of two
points of `S` land in `E` when the two points share a parity and in `O` when
they do not, so the **odd half of the covering condition comes from the cross
sums alone**: `S + S = F2^7` requires every odd mask to be `a + b` with
`a` in `A`, `b` in `B`.

**Lemma (odd-coverage Fourier obstruction).** Let `A` be a subset of the even
coset and `B` a subset of the odd coset of `F2^n`, with `|A| = s` and
`|B| = t` of opposite parity. Let `r = 1_A * 1_B` be the cross-sum
multiplicity on `F2^n`. If every odd mask is a cross sum (the odd half of the
covering condition), then, with `rho = r - 1_O` and `E_o = s*t - 2^(n-1)`:

1. `rho >= 0` on `O` with `sum rho = E_o`;
2. for characters `chi_u(x) = (-1)^(u.x)`, the exact identity
   `r_hat(u) = f_hat(u) * g_hat(u) = FT(1_O)(u) + rho_hat(u)` holds, and
   `FT(1_O)` is supported on `{0, 1}` (the zero vector and the all-ones
   vector);
3. hence `|f_hat(u) * g_hat(u)| = |rho_hat(u)| <= E_o` for every
   `u` not in `{0, 1}`;
4. `f_hat(u) == s (mod 2)` and `g_hat(u) == t (mod 2)` for every `u`, so the
   odd-cardinality side's character is nonzero, and the even-cardinality
   side's character `c_hat(u)` satisfies `|c_hat(u)| <= E_o` and
   `c_hat(u) == 0 (mod 2)` off `{0, 1}`;
5. Parseval on that side, using `c_hat(0) = card` and `c_hat(1) = -card`
   (all its points sit in one coset), gives
   `sum_{u not in {0,1}} c_hat(u)^2 = 2^n * card - 2 * card^2`.

If this Parseval remainder exceeds `(2^n - 2) * (largest even <= E_o)^2`, the
hypothesis is contradictory.

For `(s, t) = (11, 6)` at `n = 7`: `E_o = 66 - 64 = 2`, so `c_hat(u)` is
`0`, `+2` or `-2` off `{0, 1}`; but `128 * 6 - 2 * 36 = 696` and
`126 * 4 = 504`. **`696 > 504`: contradiction (deficit `192`).** The mirror
`(6, 11)` is identical with the roles exchanged (odd translation swaps `E`
and `O` and preserves `S + S`). Note the hypothesis used is only the odd half
of the covering condition; even coverage is not needed.

All arithmetic is exact Python integers; no floats are used anywhere.

## Machine results (exact integers)

| Split | `E_o` | Bounded side | Character values | Parseval remainder | Allowed | Verdict |
|---|---:|---|---|---:|---:|---|
| `(11,6)` | 2 | `B` (6 pts) | `-2, 0, 2` | 696 | 504 | **impossible (PROVEN)** |
| `(6,11)` | 2 | `A` (6 pts) | `-2, 0, 2` | 696 | 504 | **impossible (PROVEN)** |
| `(10,7)` | 6 | `A` (10 pts) | `-6..6` | 1080 | 4536 | no Fourier contradiction (excluded by PR 2773 census route) |
| `(7,10)` | 6 | `B` (10 pts) | `-6..6` | 1080 | 4536 | no Fourier contradiction (as above) |
| `(9,8)` | 8 | `B` (8 pts) | `-8..8` | 896 | 8064 | no Fourier contradiction (PR 2542 rows) |
| `(8,9)` | 8 | `A` (8 pts) | `-8..8` | 896 | 8064 | no Fourier contradiction (as above) |

The checker is not vacuous: it fires exactly on the `(11,6)/(6,11)` rows
among the 17-point splits, and a real 10-point cover of `F2^5`
(`S = {0,1,2,3,4,5,6,8,16,31}`, split `(4,6)`, odd excess 8) passes every
check with no false contradiction. Independent controls: the FT convolution
identity is exhaustively verified over all 65,536 set pairs of `F2^3`; the
bound `|rho_hat| <= sum rho` is exhaustively verified over all 2,080 total-2
multiplicity shapes on the 64 odd masks (worst `|rho_hat| = 2`); Parseval is
re-checked by direct pair double counting.

## Reproduce

From the repository root, standard library only, CPython 3.12:

```sh
python3 -I -B research/f7-17point-fourier-obstruction-seedb5e318fe/test_engine.py
python3 -I -B research/f7-17point-fourier-obstruction-seedb5e318fe/independent.py
python3 -I -B research/f7-17point-fourier-obstruction-seedb5e318fe/verify.py
```

Expected markers: `Ran 13 tests ... OK`, `PASS_FOURIER_INDEPENDENT {...}`,
`PASS_FOURIER_VERIFY seconds=...` (with `OBSTRUCTION (11, 6) ... deficit=192
contradiction=True`, `REPRO rows remainder (5,1),(6,0) shared=1 c=1`).

The row remainder is reproduced from the vendored PR 2773 engine:
`sharp_rows(7, 11, 6)` gives exactly the seven rows `(e, 6-e, 1)` with
`shared = 1`, `c = 1`, and the recorded k=11 census floor `e_ex >= 5` leaves
exactly `(5,1),(6,0)` — the object decided here (both orders).

Heavy anchor recomputation (completed in-session; resumable, per-sub-shard
receipts in `ANCHOR-PROGRESS.json`, the established PR 2773 raw-domain walk:
`GL(6,2)`-transitive domain through `{0,3}`, sub-shards by the smallest free
element, vendored engine byte-pinned):

```sh
python3 -I -B research/f7-17point-fourier-obstruction-seedb5e318fe/anchors.py k10b3
python3 -I -B research/f7-17point-fourier-obstruction-seedb5e318fe/anchors.py k11b4
```

Observed: `PASS_ANCHORS_K10B3 count=149990400 total_hist={'3': 149990400}
shards=62` and `PASS_ANCHORS_K11B4 count=0 total_hist={} shards=62`. Each
invocation checkpoints after every sub-shard and exits after its time budget,
so an interrupted walk resumes from `ANCHOR-PROGRESS.json`.

## Recorded anchors (reproduced before any new number)

In-session, CPython 3.12, against the predecessor packages byte-exactly
(see `ANCHOR-REPRO.json` for the commands and observed outputs):

| Anchor | Value | Status here |
|---|---|---|
| PR 2542/2634 REPRO tiers | `945/31`, `10395/49`, `945945/59` (records SHA-256 match) | recomputed |
| PR 2542 length-18 census | `15,775,992` nodes, `312,064` cycles, `0` universal | recomputed |
| PR 2773 zero shards (`k10` budgets 0/1/2, `k11` budget 2) | all `0`, match receipt | recomputed (`verify.py --full`) |
| PR 2773 row table | `(11,6)/(6,11)` remainder `(5,1),(6,0)` | recomputed |
| n=5 set controls | 0 nine-point covers (max 29/32), `99,200` ten-point covers | recomputed |
| PR 2773 `k=10 budget-3` | `149,990,400` | recomputed in full (`anchors.py k10b3`, `PASS_ANCHORS_K10B3 count=149990400`, 62/62 sub-shards) |
| PR 2773 `k=11` levels 3-4 | `0`, `0` (62/62 sub-shards) | recomputed in full (`anchors.py k11b4`, `PASS_ANCHORS_K11B4 count=0`) |

None of the last two anchors is load-bearing for the verdict here: the rows
`(5,1),(6,0)` are excluded by the identity above, which uses only exact
integer arithmetic.

## Row verdicts (labels)

- `(9,8)/(8,9)`: **PROVEN dead** in the pair-representation identity
  (PR 2542's own rows; re-derived in PR 2773).
- `(10,7)/(7,10)`: **PROVEN excluded exactly** (PR 2773, census floor
  `e_ex >= 3` kills the surviving identity rows).
- `(11,6)/(6,11)` rows `(3,3),(4,2)`: **DEMOTED** by PR 2773's completed k=11
  census (minimum 11-set excess `>= 5`).
- `(11,6)/(6,11)` rows `(5,1),(6,0)`: **PROVEN impossible** here, by the
  odd-coverage Fourier/Parseval obstruction (deficit `192`), in fact for the
  whole `(11,6)/(6,11)` family and without using the even half of the covering
  condition.
- Consequently **"No 17-point set covers `F2^7`" is complete at the set level
  (PROVEN**, jointly with PR 2542 and PR 2773**)**, and at `L = 22` every
  universal word needs at least 18 distinct prefixes.

## Scope and remaining obligations

A finite set-level result inside PR943's abstract interface. Not checked:
everything word-level (the repeated-state `L = 20` word census is Nicholas
Stone's concurrent claim,
[discussion 1166 comment 18954844](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18954844);
its remaining splits `(10,9),(10,8),(9,9)` are 18/19-point objects this
identity does not reach, since there `E_o >= 8` and the character squeeze
disappears), the 18-/19-point cover question `r((C2)^7)`, and any kappa,
supplier, tariff or selected-frontier implication. The gap
`20 <= f(7) <= 24` is unchanged.

## Open next questions

1. **Do 18-point or 19-point covers of `F2^7` exist (is `r((C2)^7) = 20`)?**
   Why it matters: with 17-point covers now fully excluded, `|P| = 18` is the
   set-level frontier for universal words at `L = 20/22`. First step: extend
   the pair-representation identity and the min-excess census to the k=18/19
   split rows. Blocked by: the joint-tree growth (~3.1e8 Sidon 6/7-sets on the
   B side; stabilizer canonical forms for the pair `(A, B)` are not
   implemented — PR 2773's recorded blocker).
2. **Does the odd-coverage Fourier obstruction extend to a general covering
   bound over `(s, t)` and `n`?** Why it matters: a table of Parseval
   remainders vs allowed character squares would prune word-census splits
   directly (PR 2773 open question 3). First step: tabulate
   `fourier17.obstruction(n, s, t)` over the counting-feasible splits of the
   `L = 20/22/24` censuses. Blocked by: nothing; cheap bookkeeping.
3. **Handoff to the concurrent `L = 20` word claim** (Nicholas Stone): the
   set-level 17-point object is closed at every split, so no `|P| = 17` word
   family survives at any length; the claim's remaining 18/19-point splits are
   untouched here. Blocked by: nothing; a handoff note, not an obligation of
   this package.

See [NOTICE.md](NOTICE.md) for attribution and licenses,
[TASK.json](TASK.json) for the task card and scope change,
[SOURCES.json](SOURCES.json) for pins and credit, [CERTIFICATE.json](CERTIFICATE.json)
for the labelled result record, and [ANCHOR-REPRO.json](ANCHOR-REPRO.json) for
the in-session anchor reproductions.
