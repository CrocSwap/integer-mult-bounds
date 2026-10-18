# A half-stage timing shift improves the PR2530 owner fill

The complete finite replay certifies conditional **κ ≈ 0.001713785146530231**,
exceeding PR2530 by **0.000000047224982726895549** (about 0.00276%).
The exact rational claim is in `CLAIM.json`, with complete admission in
`evidence/FULL-RESULT.json`. The complex endpoint is
`0.001713785146530231242301`; the final outer κ is slightly below it.
This package does not change the maintainer-selected frontier.

The new lever is invocation priority. Keep PR2530's two complete 422-helper
words, 74 replicas, 666 invocations, dimension 73, live width 66304 and rank
mass 4816512. Replace the predecessor order, sorted by `(4*s+r,s,r)`, with the
order sorted by `(8*s+2*r+int(s==2),s,r)` for stages `s=0..8`, replicas
`r=0..73`. This delays stage 2 by half a priority step while preserving each
replica's stage order. Recompute strict owner windows from the original event
schedule, then rehost every whole call. No local frame or operation changes.

The 42-order capacity screen found that this priority shift permits filling
all rank-8 owner bins with width-8 helpers; the predecessor leaves 114 such
bins unused. That one-width flow is only a nomination. The committed complete
allocation independently passes the original literal checker for all 281052
roles, including helper coverage, exact widths, strict windows, prefix
capacities and distinct physical families within each invocation.

The idle profiles are:

| Rank | PR2530 | Candidate |
| ---: | ---: | ---: |
| 1 | 21976 | 21720 |
| 3 | 6662 | 6513 |
| 5 | 440 | 747 |
| 8 | 114 | 0 |
| 16 | 172 | 172 |
| 32 | 3 | 4 |
| 48 | 26488 | 26489 |

The resulting full paid profile is
`{1:1599474,2:420912,3:219633,4:78588,5:18063,7:5328,16:172,32:4,48:26489}`.
At the fixed rank mass, this redistribution lowers the recursive moment.
`price.py` uses Douglas Colkitt's original rational interval engine and
certifies that the root of `sum(n_r*(r/73)^(1-a))/66304 = 1` lies between
`0.001713785146530231242301` and `0.001713785146530231242302`.
It does not apply the historical `a/(1+a)` map; the current exact outer ledger
is a separate admission gate.

## Evidence and scope

- `evidence/CANDIDATE-FILL.json.gz` is the complete literal witness;
  SHA256 `5e19643e3e6b97bc39567adca8c1d07a4aaee74b1c73ea49c35f9065f7c25770`.
- `evidence/CANDIDATE-ORDER.json` fixes the complete invocation order.
- `evidence/OWNER-RESULT.json`, `PROFILE.json` and `MOMENT.json` record direct
  exact checks; `ORDER-SCREEN.json` records the bounded capacity search.
- The direct verifier also rejects missing-role, outside-window and duplicate
  physical-family mutations, and refuses an optimized interpreter that could
  disable assertions.
- `evidence/FULL-RESULT.json` records the passing retained parent, both fresh
  native chains, reconstruction/lift, discovery, strict admission, geometry
  controls and outer replay. All 63 strict outer inequalities are positive;
  all 17 outer rejecting controls, six geometry controls and 19 outer evidence
  replays pass. `OUTER-LEDGER.json` and `FROZEN-SPEC.json` bind the final supplier.

This is a conditional finite construction, with inherited all-size,
compiler, mutable-source/common-label, precision/tape, analytic and bit
interfaces. It is not a complete multiplication theorem or independent human
review. Neither the restricted packing search nor the 42-order screen proves
global optimality or excludes other levers.

## Reproduce the committed witness

From the repository root, using a fresh workspace directory:

```powershell
py -3.12 -B research/source-partner-residual-exchanges/verify.py --work research/source-partner-residual-exchanges/_work/check
```

This direct check needs only the Python standard library. It reconstructs the
pinned parent sources, checks the witness with the unchanged original owner
checker, reprices the literal profile with exact rational intervals, and
checks three rejecting controls. `INPUTS.json` binds all proof-relevant external
source bytes and the candidate witness. It does not substitute for full native
or global admission.

Full replay, with Python 3.11, NumPy 1.26.4, SciPy 1.15.3, SymPy 1.14.0 and
mpmath 1.3.0, uses a fresh directory:

```powershell
py -3.11 -B research/source-partner-residual-exchanges/cold_replay.py --work research/source-partner-residual-exchanges/_work/full --fill research/source-partner-residual-exchanges/evidence/CANDIDATE-FILL.json.gz
```

The retained parent and both fresh native chains run in separate directories.
All must finish before candidate reconstruction, parent lifting, discovery,
strict global admission, geometry controls and the exact outer ledger run.
Logs and receipts remain in the selected workspace. The special
`--resume-in-progress-parent` option is only for continuing an already running
fresh parent process after restarting its driver; it waits for the complete
parent result and verifies both native input bindings. It skips no parent
proof obligation.

`ENVIRONMENT.json` records the exact local run, including SymPy 1.13.2 / SciPy
1.12.0 for the already running retained parent, and SymPy 1.14.0 / SciPy 1.15.3
for the new native and global/outer checks. The strict supplier receipt retains
its historical κ interface (`0.001710853111879197`); the final quoted κ is the
separately replayed outer-ledger result. Inherited `outer/OUTER-CLAIM.json`
metadata inside the recovered old package is historical; use this package's
`CLAIM.json` and fresh `evidence/OUTER-LEDGER.json`.

The registered standard-library check is:

```powershell
py -3.12 -B scripts/research_package.py --package research/source-partner-residual-exchanges
```

It checks metadata, exact source pins and the literal/moment verifier. Each
registered run uses a fresh temporary workspace and removes it on exit. Use
the explicit `--work` command above to retain receipts or failure diagnostics;
an existing path is refused without overwriting it.
[Workspace regression and evidence](../owner-replay-workspaces/README.md) cover
repeated registered checks. Full native/global/outer replay remains the
separate command above.

## Optional search reproduction

The committed witness can be checked without trusting SciPy. To repeat the
bounded nomination, use Python 3.12.2, NumPy 2.3.4 and SciPy 1.16.2:

```powershell
py -3.12 -B research/source-partner-residual-exchanges/prepare_search.py --work research/source-partner-residual-exchanges/_work/search
$env:SOURCE_PARTNER_SEARCH_WORK=(Resolve-Path research/source-partner-residual-exchanges/_work/search/packing).Path
$env:SOURCE_PARTNER_PREPARED=(Resolve-Path research/source-partner-residual-exchanges/_work/search/prepared/research/gmx-t74-borrow43-handoff).Path
py -3.12 -B research/source-partner-residual-exchanges/global_pack.py
py -3.12 -B research/source-partner-residual-exchanges/realize.py
```

The global feasibility model uses 16 predecessor-supported patterns and at
most 40 interval/flow-cut rounds, with a 30-second solve limit per round.
It found this nomination after seven rounds. Identical-demand/availability
classes realize each width, followed by explicit helper naming and prefix
packing. Floating-point solver results and class-flow nominations are never
acceptance evidence: the literal checker is mandatory. Solver tie-breaking
can change the nominated allocation.

An earlier 250-attempt fixed-order exchange search found no gain. Its temporary
execution log was lost during recovery, so that observation is local-only and
is not a retained negative certificate. The changed question and bounded
single timing pivot are recorded in `TASK.json`.

## Open next questions

- **Repack the stage-4 half-step order.** It also attains zero rank-8 capacity
  loss in the screen. First realize all five helper widths and compare the
  literal complete profile. The screen alone does not show an improvement.
- **Optimize residual concentration after fixing timing.** This witness comes
  from a restricted-pattern feasibility search, not a global optimum. First
  optimize the exact accepted pattern stock under the same literal windows;
  the remaining limitation is complete physical realization.
- **Change the local inventory for a larger gain.** PR2530's open questions
  include lender reassignment and larger recoverable subspaces. First produce
  and audit a complete changed local word. This package establishes no such
  word or universal barrier.

## Sources and credit

Canonical main was refreshed at `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
The scientific predecessor is [PR2530](https://github.com/CrocSwap/integer-mult-bounds/pull/2530),
head `b4012098048e12500b2d33d2e84be281915a27ac`, by zxv with AI assistance.
Its packages are retained byte-for-byte, including predecessor attribution.
`global_pack.py`, `realize.py` and `cold_replay.py` derive from that package's
search and replay scripts. The inherited PR2462/PR2435/PR2436/PR2322 and
native/global/outer lineage retains all original notices and credit. Douglas
Colkitt supplies the independent exact interval engine.

New work was prepared for mcorrigan with substantial OpenAI Codex assistance.
No delegated agents or independent human review. Apache-2.0.
