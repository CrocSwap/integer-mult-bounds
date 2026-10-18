# Exact raw agreement set for compact dirty-control selected-bit updates

**Adversarial mathematical audit with an independent finite checker. No new
kappa; the selected record, production predicates and `upstream/` are
unchanged.** For the compact dirty-control selected-bit operation of
[`notes/compact-control-movement.tex`](../../notes/compact-control-movement.tex)
("Guards and deterministic repair"), this package computes the exact set `AG`
of states where the complete routine already equals the ideal selected-bit XOR
map and restores every dirty temporary, on complete bounded domains, and
compares it with the three published sufficient guards:

| Guard | Source |
| --- | --- |
| `G0` original temporary+target guard (plus `u` nonsaturation for the later source) | the source note, "Guards and deterministic repair" |
| `G1` expanded source-control predicate (last `u` digit keeps its complete range) | [`research/compact-carry-repair-audit`](../compact-carry-repair-audit/README.md) |
| `H` two-pass guard (1), source dependent | [`research/compact-late-guard-audit-seed73`](../compact-late-guard-audit-seed73/README.md) |

This is an **independent check of the two cited guard claims**, explicitly
identified as such, plus a new exact census those packages left open: the
seed73 README states its guard "is not the global exact agreement set" and
leaves that set uncharacterized.

## Result

1. **Sufficiency of all three guards is independently confirmed on complete
   domains.** No state admitted by `G0`, `G1` or `H` fails the ideal map or
   restoration in any of the 47 enumerated cells. Both published failure
   fixtures reproduce exactly under the independent interpreter: the
   carry-repair fixture `(x,y,t,u,b)=(16,4224,0,1,2)` returns `y=4752` against
   ideal `y=4240` with every temporary restored, and the late-guard fixture
   `(2,124,1,0,7)` returns the correct `y=126` while corrupting the temporary
   `1 -> 5`.
2. **The raw agreement set is strictly larger than every guard, everywhere.**
   Overall `|AG| / total = 11880712 / 24074240 = 49.35%`, against guard
   densities of at most 14.06% (`G0`, early `K=6,G=1`), 7.03% (`G1`) and
   44.83% (`H`). Example cells (later source):

   | Cell | AG | `G0` | `G1` | `H` |
   | --- | ---: | ---: | ---: | ---: |
   | `n=2, K=5, G=1` | 39.55% | 1.562% | 3.125% | 18.750% |
   | `n=2, K=4, G=2` | 58.42% | empty | empty | 44.824% |
   | `n=3, K=3, G=1` | 19.83% | empty | empty | 7.031% |

   Smallest agreement states every guard rejects are recorded per cell in
   [RESULT.json](RESULT.json) (`ag_outside_all`, `ag_outside_all_active`), for
   example `[y,t,u,c]=[0,1,0,0]` and the nonzero-source `[0,1,0,1]` at
   `n=2,K=3,G=1`: the saturated temporary digit is never loaded (`a_i = 0`),
   so the feared carry cannot fire and the map is exactly correct as written.
   The guards are safe repair envelopes, not the agreement set. This witness
   class is exactly the class the open
   [PR1603](https://github.com/CrocSwap/integer-mult-bounds/pull/1603) guard
   (inactive saturated digits) is designed to admit; the census also contains
   agreement states with internal `u`-load carries and cancellations between
   individually inexact subcalls, which that PR's discussion says remain
   outside its guard.
3. **The seed73 closed form (2) is independently verified.** `H`'s exact
   good-address fraction matches the enumerated count at every one of the 21
   later-source cells (the checker requires exact integer agreement).
4. **Inclusions hold as claimed**: `G0 => G1 => H` on every cell (no witness),
   and the original guard's target condition `2B <= g < 2^(K-1) - 2B` is
   *empty* for `K <= G+3`; `G0`/`G1` only engage at `K >= G+4`, which is why
   several small cells report empty guards.

## Domain and method

`verify.py` transcribes the note's four packed updates directly (whole-slot
modular rotations for the target, whole-field rotations for the compact
temporaries) and both source orders; no predecessor interpreter is imported.
For each geometry `(n,K,G)` and each selected offset `rho`, it enumerates the
complete invariant fiber: selected source bits `c`, full target `y` (its low
`rho` bits are spectators), compact temporaries `t`, compact controls `u`;
the dirty back field `b` and `x`'s unselected bits are spectators by
construction and are checked on samples. 47 cells, 24,074,240 states:
`n in {2,3}`, `K in {3,4,5,6}`, `G in {1,2}`, every `rho` for `n=2,K<=5` and
the boundary offsets for `K=6` and `n=3,K=5`, both source orders except the
one later-source-infeasible cell.

Controls: both published fixtures above (fidelity); a sign-flipped unloading
must be caught by the restoration check inside the guarded domain (witness
`[y,t,c,t_bad]=[4240,0,0,1]`); low target bits and arbitrary dirty back-field
values must not change any result (256 states times 4 dirty values).

## Reproduce

From the repository root, Python 3.10+, standard library only:

```sh
python3 -B research/compact-agreement-set-seed29/verify.py
```

Expected:

```text
PASS_COMPACT_AGREEMENT_SET: 24074240 states; 11880712 raw agreements; 47 cells; 2 fixtures; 2 controls
```

The checker verifies the pinned hashes in [SOURCES.json](SOURCES.json) before
running, compares its receipt with [RESULT.json](RESULT.json), and writes no
artifacts. `--write /new/path.json` regenerates a receipt and refuses to
overwrite an existing file. Checks use explicit exceptions and also run with
`python3 -O`; no mathematical check relies on Python `assert`. The default
replay takes a few minutes; the manifest timeout is 600 s.

## What is not checked

- The exceptional repair itself (scan, radix sort under `TS^-1`, record keys),
  its cost charges, and the complete-range invariant after row splitting
  (`docs/audit.md` lines 114-116) remain open; this audit covers the *raw*
  map before any repair.
- The production predicate and its callers are untouched; no adoption of a
  larger agreement envelope is proposed.
- `n <= 3`, `K <= 6`, `G <= 2` only. Larger geometries, the highest-bit
  completion beyond the elementary XOR, and a proof-assistant formalization
  are outside this package. Transcription fidelity rests on the source note,
  the two reproduced fixtures, and the pinned-source hashes, not on a formal
  semantics.
- The stronger sufficient guard of the concurrent open
  [PR1603](https://github.com/CrocSwap/integer-mult-bounds/pull/1603)
  (`research/compact-late-carry-guard`, not present in this base commit) is
  **not** transcribed or tested here; only the three guards whose definitions
  are in this base are checked.
- No kappa, packing-cap or a < D/E claim: this is a source-bound audit of one
  named condition, so whole-construction budgets do not apply.

## Open next questions

- **Characterize `AG` structurally.** The census shows the exact agreement set
  exceeds every digit-local guard; the seed73 proof characterizes agreement
  only inside the nonsaturated-`t` domain, and open
  [PR1603](https://github.com/CrocSwap/integer-mult-bounds/pull/1603) proves a
  maximal invariant agreement core only for `n=1`, with a handoff asking for
  the `n>1` enumeration. This package supplies that enumeration layer at
  `n=2,3`; a carry-state description of the enumerated set is still missing.
  *Why it matters:* a repair envelope priced on `AG` rather than on a
  sufficient guard would shrink the exceptional-repair workload. *First step:*
  classify the `AG \ H` states at `n=2,K=4,G=1` by which guard clause fails
  (never-loaded saturation vs internal `u`-load carry vs subcall
  cancellation), then test any proposed digit-local formula on the next
  geometry. *Blocked by:* nothing computational; a plausible predicate form is
  the missing ingredient.
- **Price the repair envelope change.** *Why it matters:* `docs/audit.md`
  asks independent verification to preserve the scan and radix-sort charges
  including full record payload and destination keys; those charges scale with
  the number of repaired records. *First step:* implement the `TS^-1` sort
  repair at `n=2,K=5,G=1` and count repaired records under `G0`/`G1`/`H`
  versus a hypothetical `AG`-based predicate. *Blocked by:* the note does not
  fully specify the tape cost model of the repair.
- **Larger-geometry falsification first.** *Why it matters:* all three guard
  sufficiency proofs are parameter-generic, but the finite checks stop at
  `n=3`. *First step:* seed-randomized falsification search for sufficiency
  counterexamples at `n=4..6`, `K=6`, `G=2` (the seed73 geometry family),
  starting at boundary guards. *Blocked by:* complete enumeration is
  infeasible there, so only bounded search, not a complete domain.

## Credit

Aaron Wang, with help from opencode. Apache-2.0; same repository licenses.
Source semantics: `notes/compact-control-movement.tex`. Guards, fixtures and
the density formula are prior work: the two-pass guard `H` and its density are
[Hanson Sun's PR1247](https://github.com/CrocSwap/integer-mult-bounds/pull/1247),
independently re-derived in `research/compact-late-guard-audit-seed73` (which
also supplied fixture 2); `G1` and fixture 1 are
`research/compact-carry-repair-audit`, following
[Sagar Thakrar's PR1475](https://github.com/CrocSwap/integer-mult-bounds/pull/1475)
and the one-pass fact of PR1219. The concurrent open
[PR1603](https://github.com/CrocSwap/integer-mult-bounds/pull/1603) (inactive
saturated digits, `research/compact-late-carry-guard`, with its claim and
handoff in
[discussion 1588](https://github.com/CrocSwap/integer-mult-bounds/discussions/1588))
is independent concurrent work on the same family: its stronger sufficient
guard and `n=1` maximality result are not reproduced here, and this census is
an answer to the `n>1` enumeration its handoff requests.
`scripts/audit_compact_controls.py` is pinned as the source-bound checker of
record; this package shares no code with it. The live overlap search and its
coverage are recorded in [TASK.json](TASK.json).
