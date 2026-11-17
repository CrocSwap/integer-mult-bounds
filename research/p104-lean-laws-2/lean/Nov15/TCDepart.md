# TCDepart
Kernel-only; axioms propext/Classical.choice/Quot.sound; no sorry/native_decide. Builds on TCLemma (`held_run`, `cancel_only_by_read`, `legal`/`ND`).

## Timed model
Run `evs` from `s0` in the TokenCancel op model; `st s0 evs n` = state before event n. Hypotheses throughout: `LegalA` (ascending public moves), `ND h` (no destroying e_h), helper `h`, receiver `r != h`.
Import = `add r h _ F` at index t1; departure = event at index tau (move r c'); r sits at F on every n in (t1,tau).

## Theorems
- `dirty_departure`: r leaves F for c' carrying e_h, run ends e_h-clean => for every chart R with not c' <= R, some read of h AFTER the departure is at a chart outside R.
- `cancel_in_window`: dirty at time a, clean at b => some event in [a,b) is `add r j` with j = h or j dirty.
- `clean_departure`: dirty after import, clean at tau => some event in the window is a stay `add r h _ F` OR a read of a register j != h,r that is resident at F, carries e_h. (This is the "cover": e_h already present in the rows at F before departure.)
- `forced_stay`: if `CoverFail` (no j != h,r with e_h resident at F during the window) then the helper reads h into r at F inside the window.
- `forced_stays_count`: finite family of imports, each dirty/clean/resident/CoverFail, windows of same-receiver imports pairwise disjoint => #reads of h >= #imports.

## Reading of the paper statement (SAID AT ONCE)
"Either h stays at F, or rank(rows at F before tau_dep) covers cargo + e_h" is not literally right in two places.
1. Dirty departure does NOT force a stay AT F. `TCDepart.CE` (Lean) is a legal ascending run, no destroy, final clean, where the receiver leaves F=0 dirty, h reads at F only for the import, and the cancel is at chart 1. Correct statement: `dirty_departure` (stay outside every R not containing the departure chart; this is the cone climb).
2. The cover condition must exclude h and r. Rows of h itself (= cargo + e_h) are always at F at the import, so "rank covers cargo + e_h" is vacuous unless h's own row (and r's) is excluded. Exact form: a THIRD register j with e_h content resident at F inside the window (`CoverFail` negated). The clean branch then says: stay at F, or such a j exists.

## Not covered
- Cover is stated as e_h presence in the resident rows (a one-coordinate rank condition), not full span containment of the cargo vector; cargo separability (33/1,698) is a different, stronger requirement and is not modelled.
- Rows of registers resident at F but arriving by move are included (any resident j counts); "before tau_dep" is the window (t1,tau) only, not earlier history.
- Counting needs windows of same-receiver imports disjoint; overlapping windows can share one stay.
- `dirty after import` is a hypothesis (import's token not cancelled by a(row_h)[h] + row_r[h] = 0).
- No claim about D0 prices; this is the exact wall statement and the spec for a mod-p gate (CoverFail = no dirty third register resident at F in (t1,tau)).
