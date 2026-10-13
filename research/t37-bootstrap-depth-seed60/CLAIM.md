# Round 2: adversarial bootstrap-depth audit, seed 60

- Base: `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
- Claim: 2026-10-13 16:10 UTC; target handoff 16:30 UTC.
- Exact object: the selected PR942 assembly's affine bootstrap recurrence
  `a[j+1]=(1-s)*s+s*a[j]`, starting at `384599/10^10`, and its strict outer
  `10^-18` grid at kappa `1661960547713947/10^18`.
- Hypothesis: six completed levels suffice; five do not within the pinned
  recurrence, even after relaxing the outer reservation/backoff to zero.
- Method: exact rational closed form, independently iterated recurrence,
  explicit strict-margin signs, and replay of the pinned 47 outer constraints.
- Deliverable: one finite depth boundary certificate, source pins, exact
  reproduction and meaningful mutations; no new kappa or supplier adoption.
- Assignment seed 60 is the first OS-random draw already recorded by batch
  coordination; no reroll. Its audit track and three-way selection prioritize
  bootstrap-depth sufficiency over owner geometry or native circuit changes.

Three candidates considered: (1) this least-depth question (chosen); (2) T37
owner/payload accounting (overlaps PR962 and PR991, declined); (3) copied-temp
lifecycle audit (overlaps PR729, declined). The initial cutoff-allowance-only
idea was rejected before implementation because PR991 already checks it.
PR768's five-level obstruction concerns the historical PR387 point; this
audit instead asks whether the selected seven-level recipe needs all seven.
No coordination issue was pinned at the batch check, so this is a local claim.

Only this package is writable. All predecessor sources, selected pointers and
upstream remain unchanged. No GitHub mutations. Native/full-suite checks are
not implied by an exact finite assembly calculation.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.

## Completed result, 2026-10-13 16:20 UTC

The selected native-complex branch passes all 47 outer constraints with six
levels at unchanged kappa. Zero through five fail under the more generous
inherited next-grid endpoint `u=b+10^-24`, even with independent per-level
savings and zero reservation loss. All original seven records are reproduced,
the first six cutoff obligations pass unchanged, eleven mathematical mutants
reject, one stronger-start positive control passes, and three source/snapshot
mutants reject. Historical replay works without the mutable selected pointer.
Final overlap query found PR991/962/942; PR991's reserve-allowance audit is
credited and differs from this least-depth result. No GitHub mutation occurred.
