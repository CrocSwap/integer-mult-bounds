# Maximal invariant two-digit compact-control guard

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: finite optimal-guard certificate and scoped written repair proof.

For the unchanged later-source compact word at
`n=2, K=3, G=1, rho=2`, the exact largest invariant agreement guard is

```text
H_plus = H from PR1603 OR (c=0 AND t=1 AND u=2 AND y is odd).
```

Here y is the full seven-bit target quotient, t,u are the complete two-bit
compact fields, and c contains the two processed source bits. The entire
quotient has 8,192 states. All nine physical target bits, including the two
low spectator bits and every upper bit, are accounted for.

| Same complete quotient | PR1603 carry guard H | Maximal guard H_plus |
|---|---:|---:|
| Accepted states | 2,368 | 2,432 |
| Good fraction | 37/128 | 19/64 |
| Exceptional repair records | 5,824 | 5,760 |

The 64 added states form one exact cancellation branch. An inactive
saturated low temporary digit sends a carry into the active high digit.
The old guard excludes it. With zero processed source bits, the two actual
subcalls reverse each other's displacement on this branch. The intended
map is identity there. [PROOF.md](PROOF.md) gives this calculation, the
finite maximality argument and the retained repair bill.

This answers one small multi-digit instance of Arham Tahir's PR1603 open
question. Aaron Wang's PR1823 counts raw agreement; woklerx's PR1856 reduces
that census with a full-modulus carry defect. Those results are credited
context. Their mathematical executables are neither imported nor replayed.
The general involution-core observation is also credited prior work. The
new result is the explicit maximal multi-digit guard and its strict
64-record reduction on this complete quotient.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/compact-maximal-invariant-guard/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/compact-maximal-invariant-guard/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/compact-maximal-invariant-guard
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/compact-maximal-invariant-guard --check-source-history
```

Substitute another CPython 3.12 executable elsewhere. Direct replay prints
`PASS_COMPACT_MAXIMAL_INVARIANT_GUARD` in generated JSON stdout. The receipt
binds every package file by SHA256 and includes the exact accepted-set bitmap
hash. No receipt is handwritten and normal replay writes no files.

The bounded check executes all 32,768 full-target cases and compares every
field with a separate quotient implementation. It partitions the complete
raw permutation into cycles and retains exactly those wholly in agreement.
This algorithm, which does not use the explicit guard formula, agrees with
H_plus on all 8,192 states. Every extra state is classified, both invariances
are checked and all 8,192 distinct payload tags reach their intended output
after repairing precisely the 5,760 exceptional records.

Controls reject agreement without invariance, removal of each of the three
extra-branch field conditions and incorrect current-address repair keys.
The new branch is required by a positive witness, the even-parity overlap
with H is retained, and seven invalid inputs fail in both Python modes.
The source note and PR1603 proof are authenticated live text inputs, without
executing predecessor code. The registered runner checks the remaining
historical catalogue and selected-record pins.

Local CPython 3.12.15 on macOS 27.0.1 arm64 passes both direct commands
and the registered package replay. The direct checks took 0.105 and 0.104
seconds, within their 60-second caps. These durations establish local
timeout headroom and are not a speedup claim. Normal and optimized receipts
agree byte for byte. In-memory compilation and whitespace checks pass.

## Limits and relevance

Maximality is finite and specific to the displayed geometry. The extra
branch has c=0. This does not establish an improvement on nonzero processed
source slices or on production parameter families. The wider all-n symbolic
agreement problem remains open. The card's changed scope to a written
descriptor interface result is explicit in TASK.json.

The inherited complete repair bound retains
`O(V + M L^3 + delta M L(P+L))`; only this rectangle's exact delta changes
from 91/128 to 45/64. No runtime speedup is claimed. All twelve compact
swaps, ten rotations and the separate highest-bit completion remain paid.
The payload replay is a logical permutation. Physical tape execution,
compiler, native supply, ownership/stock, precision and analytic transfer
are unproved here. No selected cold replay, Lean, Docker, new kappa or
selected-frontier change is claimed. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

Can a symbolic multi-digit carry calculation characterize an invariant
enlargement that includes nonzero processed source slices? First use the
complete-map and full-target-modulus tests on one additional geometry, then
prove a bounded carry-state description. No extrapolation from this one
finite cancellation branch is justified. The state bound, physical guard
implementation and complete caller bill remain blockers.

## Credit and provenance

Arham Tahir / Arham-Tahir64, PR1603, supplies H, its all-n invariance proof
and the explicit multi-digit open question. Aaron Wang / navinor, PR1823,
supplies the raw-agreement census context. Woklerx / PR1856 supplies the
full-target-modulus warning and integer-lift context. Douglas Colkitt
supplies the unchanged compact word and exceptional-record repair contract.
Credit Hanson Sun / bbMisk, PR1247/1219; Sagar Thakrar / thakrarsagar,
PR1475; John-Michael Smith / jp3isme, PR763; martinxxx9 / PR1108; and the
retained compact-control lineage. Their source files and credit lines are
unchanged. No general literature-priority claim is made for elementary
permutation or involution facts.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The selected source-binding baseline passed with selected PR6030 unchanged.
Live open PRs, recent account contributions, merged searches, main README
searches and Discussion claims were checked before reservation. The overlap
snapshot covered 387 open PRs, 6,322 Discussion records and all 8,917 tracked
README/TASK/ledger notes. Arbitrary diffs and unpublished work remain outside
that text coverage. Absence of a match is not a novelty certificate.

Advance claim:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362365

## Verifier bounds

All mathematical loops have fixed bounds from the 8,192-state quotient,
four low-bit lifts, two digits, four phases and a fixed control list.
Permutation traversal uses an explicit 8,192-step cap per cycle and visits
each state once. There is no recursion, subprocess, network operation,
runtime code generation or external mathematical implementation.
Functions fit within 60 physical lines. Explicit failures remain active
under optimized Python. Python dynamically allocates integer and collection
objects; fixed-size domains bound these allocations, rather than providing
a static-memory guarantee. The registered commands enable warnings as errors.
