# PR6594 certifier-to-family code review

Qualified PASS, conditional on the successful original whole-word certificate and the stated same-grid/native/read-set/ownership interface. I found no defect in the reviewed implication. This is a source-aware written audit, not a fresh event scan, native replay, complete physical admission, new fiber floor, or general hostile-packet verification claim.

## Exposure and authority

I authored B13 session07 SCOUT-CALLER-FIBER.md and previously read actual PR6594 PROOF.md, verify.py and SOURCES.json, including the causal_certificate implementation. Historical source exposure is explicit. In this assignment I reread exact PROOF.md and verify.py as inert text at head 2502a6defbe0e78d7f9285c5eb1ff88146a968ab. While awaiting local inputs I fetched the same exact verify.py text through GitHub; I did not fetch the compressed word. No current peer/abstract/coordinator draft was read before sealing this note. The work is target-known and source-aware, not blind, human, proof-kernel or independently rediscovered source mathematics.

Reviewed source: research/rounded-read-caller-fiber/PROOF.md, Git blob 672bc4e88cd7b7d27690d6ae248560d43619e173; verify.py, blob d09d0950545fe1693dfa76156c157849bbc56e2d. Source-normalized operations, coefficients and actual cohort membership remain conditional on the successful original main() path. I did not fetch, decompress, scan or execute WORD.json.gz, source or new science code, constructors, NumPy, tests, census or a kernel. Only text reads, this written reasoning and metadata hashes/timestamps were performed.

## 1. Actual normalization and caller boundary

verify.py:29-47 hashes raw source bytes before gzip parsing. It then checks the declared public/owned counts, event count, allowed opcode, exact-int field ranges and bounded nonzero Fraction coefficient. Fraction supplies reduced p/D with D>0. Consequently this is a fixed authenticated-input normalizer, not a generic complete JSON/opcode-schema validator: for example it does not separately validate every opcode's exact arity or all native frame descriptors. Those omissions do not invalidate the conditional fixed-source implication.

ADD and COPY take src from event[2]; other instructions use dst as the single data field. ADD takes event[3] and SCALE event[2] as coefficient; other opcodes receive coefficient one. This makes a COPY source read nonfractional in find_cohort, so a pre-erasure COPY of the candidate as source is rejected by its source-read condition even though the earlier destination test does not catch it. Both COPY ports are then checked explicitly by causal_certificate. MOVE's other serialized operands are not interpreted as extra data fields here. Correctness therefore requires the declared one-field native/read-set contract, not an inference that every numerical-looking MOVE operand is a data port. No native matrix, tensor lift, shape transition, spectator or hidden native state is audited by these routines.

## 2. What the two scans actually establish

find_cohort (50-63) visits every public field and stops at its first SCALE. It selects only strict contractions; any earlier destination COPY/MOVE/INIT/CLEAR or nonfractional ADD/COPY source read prevents selection. ADD destination use is intentionally allowed. This local classifier alone does not establish that every selected contraction is a signed half, or that simultaneous inputs remain silent.

causal_certificate (66-90) supplies those additional conditions over the complete chronological operation sequence. Distinct public fields begin active. Every ADD with active source must be strictly fractional; an active destination is allowed. SCALE on an active field must be exactly p=+/-1,D=2 and removes that label. A MOVE may not access an active data field; a COPY may access neither active source nor active destination; INIT/CLEAR may not access an active destination. The final active set must be empty. The ADD-first branch is sound even for dst=src: the increment established below is zero, so no active bit changes. ADD from an inactive source to an active destination also adds zero by the invariant.

main (170-182) additionally requires exact COHORT equality, equality of sorted erasures to the local classifier, the cited read counts, last-erasure cut, native-call count, and silent endpoints. None of these whole-word tests was run here. Thus 60 fields, 39 reads, 17 read-bearing fields, cut10448 (last zero-based event10447), 22,803 events and 3,453 MOVE calls are credited source claims conditional on that successful original path, not new measured values.

## 3. Simultaneous all-N invariant, without basis linearity

The relevant invariant is stronger than the finite replay list: at each cut every active selected field equals its own original binary coordinates, and every other live data field is zero. It holds for all independent mixed bit assignments at once. For each reduced nonzero p/D with 0<|p|<D, the sign seed u=0 for p>0 or u=D-1 for p<0 makes floor((p*b+u)/D)=0 for both b=0 and b=1: both possible numerators lie between zero and D-1. For zero input, every legal seed gives floor(u/D)=0.

An ADD therefore adds zero whether its source is an active bit or an inactive zero; its destination is unchanged even if it is active. An active signed-half SCALE sends either bit to zero and retires the label, whereas all other SCALE operations preserve zero. COPY/INIT/CLEAR touch only zeros by the active-set checks. MOVE receives an all-zero field and returns zero under the inherited fixed-seed native contract. This argument applies before and after the final erasure and does not require the rounded map to be linear. Native operators may mix coordinates within their zero field; only their whole-field zero preservation is used. Iterating the local scalar argument proves all mixed real/imaginary assignments at each admitted width N=512^f and h>0; it does not extend the actual native ABI to unadmitted widths.

run_data (98-119) agrees with this stated arithmetic but treats ownership/shapes as an inherited valid source trace and treats MOVE as a zero-input assertion rather than a native implementation. replay_cases (122-137) consists of selected finite patterns, not a proof by linear extension from generators. Its 129 original replays, 9 rejections and 2 arithmetic boundary controls remain unreplayed source evidence. I do not use them as substitute evidence for this invariant.

## 4. Seed, records and matching family-code scope

seed (93-95) depends only on coefficient sign/denominator, not data, coordinate or previous outcome. The same scalar schedule can therefore be fixed for every member of the family; native seeds can be fixed arbitrarily subject to zero preservation. This is one legal deterministic realization. It is not an every-seed, unbiasedness, fresh randomness or probabilistic independence conclusion. The predecessor PR6547 every-seed86N statement remains separate and is not reaudited here.

The family contains independent binary real and imaginary coordinates on each of the distinct selected input fields, with all other public inputs zero and initially owned fields zero. Distinct inputs remain distinct at entry and have one identical complete data output after erasure. With fixed unchanged seed and no record feedback, exact recovery therefore needs distinct retained inverse states. A b-bit capacity permits at most 2^b states, yielding the credited120N lower bound once source cohort membership is assumed. Variable record lengths, allocation metadata, original copies and changed seed storage carrying distinctions must be counted in capacity.

The dirty-bank cancellation in PROOF:125-129 is valid on an unrestricted product domain: if its Q old states must also be recoverable and its final storage still has Q states, the recoverable input cardinality is |F|Q and the final record/bank capacity is at most 2^b Q. A promise correlating bank contents with family inputs, input-specific external advice, uncounted final storage, or a requirement to recover only the public input rather than the old dirty bank changes that hypothesis. The argument does not establish a minimum initially clean physical bank or a routing/cleanup schedule.

At an erasing signed half the ordinary residue (p*b+u) mod2 is b for p=+1 and 1-b for p=-1. Hence those residue fields bijectively identify this displayed family. verify.py does not implement or validate a general residual encoder/decoder or all-input recovery schedule; the matching family code is the written residue identity in PROOF:131-136, conditional on the literal retained residue ABI. No claim that other records are redundant for arbitrary inputs follows.

## 5. Discriminating written controls (UNEXECUTED)

1. Replace the negative fractional seed by zero. For b=1,p=-1,D=2, floor(-1/2)=-1 instead of zero. This tests the one-schedule boundary, not failure of the source theorem.
2. Replace a family bit by2. Its positive-half image is1, so the binary-family invariant cannot be asserted on all integer data.
3. Permit an integer source read before erasure. ADD into an initially zero destination from b with coefficient1 preserves that bit in the destination; a later erasure of the original source does not give the claimed zero output.
4. Allow a pre-erasure COPY to a zero field or a MOVE with access to an active field. COPY can propagate a bit and a native map need not erase it. The actual checker rejects active COPY on either port and active MOVE on its declared port; a hidden native port would violate the inherited interface rather than the written active-set logic.
5. Retire a label in the bookkeeping without a zeroing contraction. That field can remain nonzero although it is no longer called active. The actual signed-half gate prevents this shortcut; only dropping a label is insufficient.
6. Replace the mixed-pattern induction with one-bit generator checks alone. Rounded maps are nonlinear; agreement on a generating set does not establish all mixed input images. The written local invariant is the required bridge.
7. Give recovery an uncounted original-input copy, input-dependent seed or length channel. It can distinguish inputs without using the counted record. Such a construction changes the output/recovery interface and must not be used as a counterexample to the correctly counted claim.
8. Restrict the input family through an even-coordinate or correlated multiplication entrance promise, or correlate an allegedly arbitrary dirty bank with the input. The displayed product family may no longer be admissible. This proves no entrance-image, every-seed, global-maximum-fiber or physical-memory statement.

These are written hypothesis controls, not new executed tests or claims to have reproduced the original controls.

## Verdict and credit

Qualified PASS for the actual normalizer/local scan/whole-word active-set implication and the conditional simultaneous-family/capacity/matching-code reasoning above. The necessary actual-data membership and successful complete original certificate are explicitly inherited. The source uses a fixed authenticated word rather than an arbitrary hostile-operation API; shape/liveness/native-zero/one-field read sets, unchanged seed, no record feedback and the exact recovery domain remain essential premises.

Nick Petalas/PR6594 owns the displayed family,120N theorem, classifier/certifier, source counts, finite replays and matching family code. Credit Ali Romman/PR6546 for the same-grid numerical and retained-record ABI and PR6547 for the complete-caller fiber/every-seed86N predecessor; DreamingOfClouds/PR6030 and P104 lineage, zxv/PR6066 for signed-half residues. Chronological induction and pigeonhole/product counting are classical. This source-aware OpenAI Codex review establishes neither full word/native physical execution nor a new invoice, recovery implementation, all-five-assumption discharge, kappa or frontier change.
