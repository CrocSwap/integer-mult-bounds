# A short-cycle P104 matching survives the helper-91 screen

**Scoped local result:** a new four-slot rematching has all 4,992 required
support paths in the relaxed interval graph and passes the exact single-helper
consistency screen for helper 91.

Starting from PR3013's source-pinned 208-slot matching, the verifier exhausts
every simple directed alternating cycle of lengths two, three and four in the
208-slot compatibility graph. The census contains 3,375 cycles: 185 of length
two, 475 of length three and 2,715 of length four. Three rematchings have all
4,992 required source-to-target paths. Two are new to this search:

| Alternating cycle | All 4,992 relaxed paths | Passing helper-91 flags |
|---|---:|---:|
| `[13, 203, 191, 63]` | yes | 33 of 9,765 |
| `[39, 134, 139, 154]` | yes | 0 of 9,765 |
| `[139, 154, 182, 179]` (PR3019) | yes | 0 of 9,765 |

Slots are zero-based departure indices. A cycle `[u0,...,uk-1]` replaces each
old assignment `M[u_i]` by `M[u_(i+1)]`, with indices read cyclically. The first
cycle is the new witness in [WITNESS.json](WITNESS.json). Its first passing
helper-91 flag has dimension-three through dimension-six bases
`[2,13,421]`, `[2,13,64,421]`, `[2,13,64,133,288]` and
`[2,13,20,64,133,288]`; [RESULT.json](RESULT.json) records the exact witness and
the complete flag census.

The key improvement over the preceding fixed-matching result is narrow but
concrete: the prior relay obstruction rejected PR3019's matching after forcing
only helper 91 to use a nested flag. This different matching retains every
required path for 33 of helper 91's 9,765 nested flags. The other 207 helpers
are still granted independent contacts in this screen, so the result does not
establish a jointly consistent frame program.

## Evidence and limits

The search binds to base commit `997e6a9ca7b4f95d50e366f61412fd640d72a88a`.
`SOURCES.json` pins both predecessor checkers, their manifests and witnesses,
and the three raw P104 inputs. The search uses the predecessor interval
checker’s contact and support definitions, updates only cycle-moved vertices,
and cross-checks the original matching, PR3019 and every support-complete
candidate against a fresh full interval replay. It then enumerates all 9,765
full flags for helper 91 for each of the three candidates.

This is a finite candidate result, not a side-correction program. It supplies
no simultaneous flags for the other helpers, chronological coefficients,
source/target access schedule, arbitrary-dirty restoration, complete cost or
supplier admission. It changes no selected record and makes no kappa claim.
See [TASK.json](TASK.json) for the scoped handoff and stopping rule.

## Reproduce

From the repository root, run the standard package replay:

```sh
python3.12 scripts/research_package.py --package research/p104-alternating-cycle-neighborhood
```

The verifier checks the exact typed receipt and prints
`PASS_P104_ALTERNATING_CYCLE_NEIGHBORHOOD`. Python 3.12 and the standard
library are sufficient. Source pins and the originating task card are recorded
in [SOURCES.json](SOURCES.json) and [TASK.json](TASK.json).

## Open next questions

Can this matching support one jointly consistent nested-frame choice for all
208 helpers? The current positive census fixes only helper 91 and relaxes the
other 207. A useful next step is to combine the recorded helper-91 witness
with exact nested-flag constraints for the four rematched slots, then widen the
joint check only if those constraints remain feasible. Even a joint flag
assignment would still need a chronological correction, dirty restoration and
a complete cost. These questions are structured in [TASK.json](TASK.json).

## Credit

The interval and correction checks reuse source-pinned routines from Nick
Petalas's PR3013/2996 lineage. The exact helper-91 flag enumeration reuses the
checker from the PR3032 fixed-matching consistency result. The predecessor
credits and Apache-2.0 terms remain with their original files; this package is
Apache-2.0. Prepared by OpenAI Codex with user-directed research; no human
mathematical review is claimed.
