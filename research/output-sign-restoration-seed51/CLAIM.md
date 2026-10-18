# Output sign frames for a sign-drifting recursive reader

Claimed locally, 2026-10-13 20:10:49 UTC. No pinned coordination issue
exists. Expected finish: 2026-10-13 20:43:52 UTC.

- Track: recursive interfaces. Fresh OS-random assignment seed: 51.
- Exact base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.
- Object: fixed linear-reader children `C_i(D,W)=(D+R_i W,-W)`.
- Hypothesis: an alternating sign frame on the smaller output register can
  replace intermediate full-workspace restorations, even when every reader
  observes the changing workspace. A complete two-pass dirty echo must still
  eliminate the incoming workspace from the returned source-dependent output.
- Method: prove the all-input identity; emit only signed two-address ADD and
  NEG instructions; replay every source, output and dirty-scratch basis column
  independently; compare literal inverse words and complete scalar invoices.
- Seed-selected example: five children, workspace width eight, output width
  one. `k=3+2*(seed%2)`, `N=2+seed%9`, `d=1`.
- Deliverable: one scoped research construction, exact certificate, complete
  recursive cost/storage recurrence, independent finite replay and meaningful
  negative controls. No new kappa or supplier adoption.

## Three candidates and overlap

1. Output sign frames for fixed sign-drifting readers. Selected. The original
   readers remain unchanged, while the parent changes the output sign between
   children. Preliminary complete echo counts save 56 NEG instructions at the
   selected dimensions; this remains to be checked by an emitted word.
2. Noncommuting reader compatibility. Rejected as covered by PR1203 and PR1205,
   alongside PR1199's diagonal cut planner. Those keep or constrain reader
   observations instead of paying for a changing output frame.
3. Exact rational borrowing widths. Rejected due to active discussion1202 and
   PR1159's modular borrowing contract.

Checked 816 open PR titles/bodies and all five current discussions. A semantic
search for output/target frames and negation found supplier geometry and frame
retiming work, but no matching recursive sign-frame wrapper. PR1155's restored
batch model, PR1199's reader counterexample correction, PR1203's noncommuting
wrapper and PR1205's observer distinction are predecessors, not new claims here.
Prior compact-control boundary obstruction PR1108 concerns different primitives.

Acceptance: prove the stated identity and invoice, reproduce the predicted
finite saving, expose one failure when an output sign or workspace restoration
is omitted, and leave every existing repository file unchanged. Only this
directory will be added. Child source accesses, scratch, inverse calls and
control/preparation costs must be explicit. Physical supplier admission,
rounding, full multiplication formalization and a better exponent are outside
this contribution.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance.

## Submission overlap check

At 20:23 UTC, inspected 830 open PRs through #1221 and refreshed the
discussion inventory. No matching output-sign boundary wrapper was found.
This is bounded overlap evidence, not proof of novelty. PR1203 and PR1205
still have the pinned heads listed in SOURCE-PINS.json. PR1211 prices a
different balanced factor-tape traversal; PR1216 excludes cheap CK/JP8 dirty
donors. Neither result establishes or defeats this fixed-reader interface.

Upstream advanced to `49b3157d1d89adcef16df8be98445451672be5ba` during the
check, adding onboarding and optional package replay tools. Its selected
certificate is unchanged. The exact investigation base remains the original
commit above. The new contribution rules and package guide were inspected;
the requested open-next-question section is included. The existing offline
archive format is retained, without inventing a catalogue assignment for the
user's explicit track. Scope is a refinement of that track and is unchanged
since the local claim. No evidence-driven pivot was needed.

## Completed result, 2026-10-13 20:30 UTC

[PR1227](https://github.com/CrocSwap/integer-mult-bounds/pull/1227) submits the
completed scoped construction. The sharp uniform wrapper minimum is
`(k mod 2)N + 2 floor(k/2) min(N,d)`. The complete seed-selected dirty echo
uses 200 scalar instructions versus 256 eager, saving 56 NEG operations;
both words implement the same source-only map and restore all scratch.
The fixed-child and final-observer restrictions are explicit. No new kappa.

All 21,840 sign schedules, 384 price cases, 384 recursive cases and 3,168
small-case basis columns pass, plus selected/deeper dense words, inverses,
rational dirty probes, seven mathematical and seven input controls. Python
3.14.8 normal/optimized and 3.11.17 optimized runs pass. Relocation, four
on-disk corruptions, source identities and canonical regeneration pass.

The immediate submission refresh covered 834 open PRs through #1225.
PR784's sharp bound is for dirty-echo leaf calls, not this boundary alphabet.
No matching output-sign wrapper was found. The repository has neither the
`codex` nor `codex-automation` label. Selected cold replay, Linux, physical
supplier admission, complete formalization and independent human review were
not performed. Hosted CI is separate from the local evidence.
