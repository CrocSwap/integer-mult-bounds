# OwnedSkeleton.lean: E1-E3 as a decidable check, run on the real skeleton
Kernel-only (`decide +kernel`; no sorry, no native_decide); 13 `#print axioms` all within [propext, Classical.choice, Quot.sound] (most: propext only). 11 s, peak 3.3 GB (data elaboration; under the 3.5 GB guard). Imports Nov15.ClearCert (+ generated OwnedSkeletonData.lean). Build order: ClearCert, OwnedSkeletonData, OwnedSkeleton (oleans in .lake/build/lib/lean/Nov15).

## What is defined
Skeleton = time-ordered list of owned `Ev` (`init f c | move f dest | clear f c`; MOVE source = the field's tracked current chart), the same event type ClearCert's `ownedEvents` filters, so it plugs into `ErasureOK`. Clauses as in the CLEARFORM note, section 0 (FINITE-PRECOMPILATION.md:34-35, :250-268; check.py `replay` :98-117):
- E1 (explicit INIT, erased, no overlapping reuse of a name): INIT only of a dead field, MOVE/CLEAR only of a live one, nothing live at the end (`e1run`).
- E2 (one bank per live unit retained to its CLEAR; reuse needs a lifetime proof): every field is one of the 68 labels (1501..1568) and peak live <= 68, so 17 calls x 68 labels = 1,156 banks hold every lifetime.
- E3 (field identity / chronology): MOVE starts at the current chart and is properly nested (GF(2) span of the frame, check.py:104), CLEAR is at the current chart (`e3run`).
`Sk := E1 /\ E2 /\ E3`, a `Decidable` Prop.

## What is proved (all by kernel `decide`)
Data: the #7630 word file (208,738 events, sha prefix in the data file header), extracted by a script that is not shipped (fidelity of extraction by reading; the extractor only filters INIT/CLEAR and owned MOVEs, p >= 1501). Counts agree with VERIFY.json/check.py `core`: 407 events = 180 INIT + 180 CLEAR + 47 owned MOVE; 68 labels; peak 50.
- `sk_skel : Sk skel` (E1, E2, E3 separately too). `Sk` is now a kernel-checked FACT for our word.
- `erasure_ok_on_skel`: for any endpoint-exact, birth-free word whose owned events equal `skel`, `ErasureOK Sk owned s es` holds (Sk from the check, lossless content from ClearCert `every_clear_lossless`).
- Counts: `n_lifetimes` 180, `n_clears` 180, `n_moves` 47, `n_labels` 68, `peak_skel` 50, `peak_le` 50 <= 68, `bank_count` 17*68 = 1156, `lifetimes_exceed_labels` (180 > 68, so labels ARE reused), `total_lifetimes` 17*180 = 3060 lifetimes on 1,156 banks.
- 9 negative controls rejected (double INIT, leak, CLEAR of dead, CLEAR at wrong chart, label out of range, non-nested MOVE 115->117, 69 simultaneous banks, truncated real skeleton).

## Paper statements
No false statement found. Two precision points: (1) The premise scope note's "the 180 lifetimes fit the allocation" is true only with reuse: 180 lifetimes per call on 68 labels (peak 50); E2's "a smaller reuse allocation requires its own lifetime proof" is what E1 disjointness + peak <= 68 supplies, so the reading "one bank per label" rests on this proof, not on one bank per lifetime. (2) The flat word's lifetimes interleave arbitrarily (2,165 crossing interval pairs; 251 CLEARs happen while a field on a strictly smaller chart is live), so E3's "parent erases only after the whole child unit completed / clear never acts on a descendant's live storage" cannot be read off the flat word. It needs the unit tree.

## What stays assumed
- E3 parent/child half (unit tree, compiler recursion structure), not expressible on the flat word.
- E4 (copy/read/erase linear in volume), E5 (paid non-reversible erase permitted), E6 (dirty residuals via ADD errors): cost/permission, not in the row model.
- Compiler admission of the retained allocation, of owned ascent (OwnedAscent), `native_all_columns`, `compiler`, `precision_tape`, `analytic_recovery`.
- Extraction fidelity of skel/chartGens from word.json.gz (script; the 180 certificates and the full 208,738-event replay are still not in the kernel).
## How far narrowed
owned_erasure: content half (ClearCert) AND the checkable skeleton half E1, E2, E3-identity are now kernel facts for #7630's word; the residue is E3-tree, E4-E6 and compiler admission. Allocation (premise 4): 17x68 = 1156, peak 50 <= 68, label-range and disjoint reuse proved; what remains is only the convention that banks are fixed per label per call.
