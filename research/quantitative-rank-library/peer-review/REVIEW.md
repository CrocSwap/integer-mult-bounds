# Independent review: all-rank library metadata

**Proof, implementation-seam and complete-cost review PASS.** No author
files were changed. The author verifier was not imported or rerun.

Base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Reviewed `work/quantitative_rank_closure/package/PROOF.md`, SHA256
`d6b882eff0703835416e26fb13a88b27409aaa09fa118171e6f9a1e8bb2ef830`.
Reviewed `library.py`, SHA256
`06e3b44704048461de0ff0ab55fe158b95df412688324b88fd3d81b929ef0d92`.
Focus: complete costs, exact chronological exit denominators and inherited
source contracts. Root independently reviews the general literal library.

## Proof and complete cost review

For fixed m=max k and strict separation r_max<k_min, the source histogram
equals all target slots minus all nondeepest paid demands. The retained
Pascal bijection consumes every such demand at equal true rank. Aggregating
counts is valid even though equal products remain distinct physical fields.

Every deepest class fits and has one degree-zero unit. Each actual paid
position there is one separate one-job cut. Hence E_e counts repeated cuts;
the denominator is B_e, not B_e/gcd(B_e,E_e). E_e may multiply additive
cost after each cut's divisibility is enforced. Source complements may be
grouped upfront and correctly use the gcd factor. The s=n case uses no B_0.

The source lower bound and exit upper bound give contraction by (m-1)/m.
For Y_n=(B_n+P_n+O_n)/B_n, U<=Ubar, S<=W*Ubar, S>=1 and total exit
multiplicity P^(G+1) give the stated F bound. Base Y_n=n+1<=m and
alpha^m<1/2 imply the m*bit_length(N) depth envelope. No surplus is assumed.

I independently retrieved the canonical #4638 width theorem: blob
`7548fd2060e41cf5b58485126d14b4dec936406a`, SHA256
`0a255788cd9b462c4cbef39721ce42d129878bf564fc08be33752ca84530e38d`.
Its plateau-product divisor applies even without gcd savings. The proposed
fixed-generator box safely weakens it without factoring source counts.
Together these arguments give polylogarithmic lengths for fully evaluated
B,a,P,O for a fixed rule; no unevaluated expression DAG is substituted.

The M_T/M_R/V/E counts check by weak compositions and Vandermonde. They
include rejected fits and coincident-product contributions. Z includes
rule/product/count lengths, evaluated widths and counts, arithmetic
numerators and indices. Factor eight covers fixed additions of operand
lengths. Total signed source partials are bounded by target plus incoming
mass. The indexed model explicitly charges record access, sorting and gcd.

The sequential companion's O(NZ) lookup is valid for its narrow primary
library spine: scan, copy and return are paid. Local full scans, insertion,
shifts, resets, arithmetic and append/return costs fit the stated
O(K*(NZ+L_local^2+Z^3)) bound. Optional source/exit censuses must occupy
separate output streams (or enlarge lookup scans); their O(KZ) output and
retained history are explicitly additional. Cleanup never subtracts history.
Python list access is not being admitted as a tape operation. The reference
uses deterministic sorted product/contribution tables and a constant-field
Row spine, with no optional census archive retained by default.

Code inspection confirms exact height comparisons, capacity equality,
signed aggregation, no B_0 lookup, chronological LCM factors and expanded
leaf/unit bills. Exit copies divide scale by child width before multiplying
by exit multiplicity. Product-table temporaries fit the local record
envelope up to fixed factors. Configured limits are refusal gates, not
asymptotic proofs.

## Independent exit-pooling failure control

`exit_cut_control.py` imports no author code. It literally enumerates role
words and paid-site words, uses the missing-parent source predicate, retains
each one-job exit, and builds previous least widths chronologically.

For targets (3,3,5), paid sites (2,2), m=5, n=135, G=3:

    sources = {60:16, 81:16, 90:8, 100:4, 135:8}
    sixteen separate rank-16 cuts; B_16 = 24
    correct a = 12,509,640; pooled a = 1,563,705
    pooled a mod 24 = 9; correct B_135 = 650,501,280

The pooled aggregate is divisible by 24 while each actual cut is not.
Strict separation holds, so the witness lies within the exact new domain.

Reproduce with `python3 -B reviews/compiler_library_peer_review/exit_cut_control.py`
or the same command with `-O`. Outputs are identical; the saved result
records 131 ranks, 1,686 literal unit occurrences and 876 distinct cuts.
This is bounded independent failure evidence, not the universal proof.

`reference_seam_result.json` pins direct reference-code execution against
this independent case: B_16, a_135 and B_135 agree, and the pooled scale
raises the ordinary finish-row integrality error. Root's separate parent-
edge oracle covers the broader library recurrence; it is not duplicated here.

`SOURCE-PIN-REVIEW.json` authenticates five core canonical texts: finite
precompilation, symbolic/chronological batching, the plateau width bound,
and the earlier chronological growth report. Author sources were unchanged.

## Remaining scope

O_n counts expanded mixed-unit occurrences. h*O_n allocates h supplied
banks per such occurrence only; adapter/control/auxiliary inventories and
physical extents remain separate. An evaluated width is not a constructed
native program. No payload runtime, selected assumption or kappa is improved
by this review. Later changes to the pinned scientific files need a delta
review. Packaging and publication remain the orchestrator's gate.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Retained batching/width theorems keep their original author and PR credit.

## Final frozen proof delta

The final proof SHA256 is `05a04e5ba1db71b9e40397e3220f047411906a5e8a70609c7a879499e6325e88`. Reconstructing the old header over its section 1 onward reproduces the exact previously reviewed proof hash. Only the opening provenance/review links changed; library.py is unchanged. `FINAL-DELTA.json` records this check. The earlier seam receipt correctly retains the exact proof hash under which it executed.
