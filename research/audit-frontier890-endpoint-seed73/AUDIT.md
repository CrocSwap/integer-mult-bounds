# Audit: endpoint certification and endpoint-to-kappa reduction of the selected frontier890 record

Assignment seed 73, track 60-74 (adversarial mathematical audit).
Prepared with help from opencode. Apache-2.0, per CONTRIBUTING.md.

## What was audited

One accounting chain: the step that turns the recorded moment endpoints of the
selected conditional witness into the headline

    kappa = 1661957774647029/10^18 = 0.001661957774647029

of `certificates/selected-result.json`, together with the surcharge-model
asymmetry that feeds it. Three statements are examined.

1. **Endpoint certification.** The claim that the two exact moment engines
   accept the recorded complex endpoint `b = 1664724476433282815289/10^24`
   and the recorded bit endpoint `c = 1733427039589844234749/10^24`, and
   reject each successor at `+10^-24`, in both the accepted and the
   conservative (surcharged) runs. This is the moment-engine obligation that
   `research/audit-kappa-floor-seed67/AUDIT.md` explicitly left unchecked.
2. **The reduction.** The claim that the recorded kappa is exactly the
   reduction of those endpoints through the seven-step bootstrap chain and the
   47 strict outer inequalities of `engines/outer.py`, floored to the 1e-18
   grid. Same method as the seed-67 audit, applied to the current record.
3. **The surcharge accounting step.** The record prices the complex side
   without the generic bad-residue surcharge and the bit side with it
   (`surcharge_model = {complex: false, bit: true}`). The claim examined: this
   asymmetry is load-bearing and its exact price is the recorded
   `native_correction_gain`.

## Base commit and pins

- Base commit: `47481c89fd30a43f8f882eb4b391e89c29273fd0` (origin/main).
- Audited record: `research/community-frontier890-audit/ASSEMBLY.json`,
  sha256 `190110b509dc87d38b72ad37c3290efcc245ce26df4cae3d7e2d6dcf0bac2c43`,
  equal to `certificate_sha256` in `certificates/selected-result.json`.
  Audited source head `4b3bd8cbe8e3e81c44161017c9b72c905a8040a8`.
- The three engines I transcribed are hash-checked against the record's own
  `input_sha256` pins and match:
  `engines/moment.py` `81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482`,
  `engines/base_two_moment.py` `aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098`,
  `engines/outer.py` `c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c`,
  read at `research/complex-k492-owner-repair/vendor/multicold/engines/`.
- The bit supplier record `research/e8-bit-p111-tuned/tune/EXPECTED.json` is
  checked by Git-blob id `e293ddc557742637f9f679f083a1a282d87b1b13`
  against the record's `bit_supplier` pin (PR589 on PR555).
- Complex stock identity: profile `H = {1:481575, 2:63882, 3:84295, 4:30618,
  5:13608, 8:1512, 48:6292}`, `m = 73`, `W = 18816`,
  `73*18816 - sum(r*n) = 6720`, and `73^2 > 2*48^2`. Bit stock identity:
  `m = 64`, `W = 28416`, deficit `T(2Kv - L*cst) = 32*(2*4*111 - 9*63) =
  10272`. Both are recomputed, not read from the record.

## Method

`audit_endpoint_reduction.py` recomputes the whole chain with exact rationals
(`fractions`), importing none of the repository engines. Every recorded value
it recomputes is compared exactly, not numerically: all six moment rows
(12 interval pairs), both decimal fields, both seven-row bootstrap tables, and
all 94 recorded outer slacks (accepted and conservative rows).

The moment sums are evaluated three ways. Two are independent interval
enclosures transcribed from the pinned engines (Mercator logarithm with
224-term alternating sums and 24-degree exponentials, outward-dyadic at
2^-224; and the base-two atanh logarithm with 12-degree exponentials,
outward-rounded at 10^-30). The third is a direct 60-digit Decimal evaluation
of the moment sum with no interval bounding and no shared rounding; it is used
only for sign agreement and interval containment.

Reproduce:

    python research/audit-frontier890-endpoint-seed73/audit_endpoint_reduction.py

Expected output (CPython 3.12, stdlib only, no `-O`):

    PASS frontier890 endpoint certification and reduction audit (seed 73)
      moment rows recomputed          = 6 (both engines + decimal signs)
      kappa                           = 1661957774647029/1000000000000000000
      margin - kappa                  = 0.315526 tick
      conservative margin - kappa_c   = 0.983742 tick
      binding endpoint                = complex
      endpoint slack c-(1-beta)b      = 6.870256e-05
      accepted - conservative kappa   = 576473/200000000000000000 (=2882365 ticks)
      endpoint gap b - b_c            = 2.891969e-12
      transfer factor                 = 0.996679077616
      guard cluster at kappa_c input  = ['Gaussian_arithmetic_above_kappa', 'balanced_prefix_above_kappa', 'compact_phase_layer_above_kappa', 'scalar_work_above_kappa']
      conservative kappa vs frontier  = above PR799 and PR870: True
      negative controls detected      = 6

## Findings

All findings are exact recomputations on the committed record. No
counterexample was found in the audited steps.

**F1 (endpoint certification confirmed).** All six recorded moment rows follow
exactly from the recorded profile and the blob-pinned bit record under both
engines' algorithms, and the accept/reject brackets are strict in both
enclosures. The tightest signs are `u-1 = -3.231659e-25` at the accepted
complex endpoint and `l-1 = +1.692003e-25` at the rejected conservative
successor; every other sign is at least `1.6e-24` from zero, so the 1e-24
endpoint grid is well resolved at this instance. The third, independently
rounded Decimal evaluation agrees in sign at all eight evaluated points
(including the two model-control points of F3) and lies inside the Mercator
intervals. This closes the moment-engine obligation left open by the seed-67
audit, for this record.

**F2 (reduction confirmed; rounding semantics at this instance).** The
recorded kappa is exactly the largest 1e-18 grid point strictly below the
reduction margin; `margin - kappa = 0.315526` of one tick, so nearest rounding
also selects kappa and upward rounding selects `kappa + 1e-18`, where exactly
the four-margin guard cluster fails (`compact_phase_layer` at the minimum,
`balanced_prefix` at `+eta`, `Gaussian_arithmetic` at `+3eta/8`,
`scalar_work` at `+7eta/8`) and every other strict slack stays positive. This
reproduces the recorded `next_grid` control from the recomputation. The
conservative row sits `0.983742` ticks below its cap. Relative to the
seed-67 audit of frontier799, the binding cluster is the same four margins;
only the sub-tick remainder differs (0.316 here, 0.076 there).

**F3 (surcharge attribution at the current record).** The accepted kappa
exceeds the conservatively admitted
`conservative_kappa = 207744721470583/125000000000000000 = 0.001661957771764664`
by exactly `2882365/10^18`, matching the recorded `native_correction_gain`.
The only input difference between the two reductions is the complex endpoint
(gap `2891969004600/10^24 = 2.8919690046e-12`), transferred through the margin
with factor `0.996679077616`. No other reduction step contributes. Both
recorded model controls are re-established by the recomputation: the
surcharged engine rejects the native endpoint `b` (Mercator lower `> 1`), and
the bit successor at `c + 1e-24` is not rejected when the bit surcharge is
omitted (Mercator upper `< 1`). The asymmetry is therefore load-bearing in
both directions: dropping the complex surcharge buys exactly the last
2,882,365 grid ticks of the headline, and the bit surcharge is required for
the bit endpoint bracket to reject its successor.

**F4 (the headline survives conservative admission).** Re-running the
reduction with the surcharged complex endpoint licenses only
`conservative_kappa = 0.001661957771764664`: at the accepted kappa the same
four guard-cluster slacks go non-positive. That conservative exponent is
still strictly above the PR799 ancestor exponent `0.001661634653669567` and
the PR870/T16 value `0.001661956299899884`. So the T21 composition's gain over
both predecessors is unconditional with respect to the surcharge question;
only the last `2.88e-12` of the headline (about `1.73e-9` relative) depends on
the PR559 license.

**F5 (scope of the surcharge-removal license at T21: inherited, not
re-proven).** The hash-pinned supplement
`research/complex-multicold/vendor/pr559/PROOF.md` licenses omitting the
complex surcharge for a complex controller with "an exact exhaustive
recursive-child profile" and "no width-dependent good/bad q-adic selector",
under the inherited exact complex-cover/compiler assumptions; its explicit
transfer section covers PR558 only. The T21 package
(`research/complex-t21-owners/PROOF.md`) calls the correction "the inherited
native-complex correction", runs the conservative admission and its surcharge
price before selecting it, and its changed structures (literal owner maps,
four-call placement delay, the nine-role trade, the dedicated-bank envelope)
are owner/schedule-level, with every bank and padding child explicitly deleted
from the emitted recursive profile. I found no document in the selected record
that re-establishes the PR559 premise for the T21 object itself. Classification:
inherited interface assumption with a documented chain of precedents, not a
missing implication in a stated proof and not a counterexample. Its exact
exposure is F3/F4.

## Negative controls

The script tampers the audited chain six ways and asserts each is caught:
kappa bumped one tick, `native_correction_gain` altered, the two complex
endpoints swapped, one outer slack replaced, one profile role count altered,
and the successor grid point treated as admissible. All six are detected on
the current record. The recomputation also fails fast if any engine or record
pin moves.

## Coverage limits and inherited assumptions

- These are finite exact recomputations of recorded identities. They are not a
  formal proof and not a re-run of the construction.
- Not checked here: the owner and invoice census that produced the profile,
  the live stock and the deficits; the prefix and row recounts
  (`491 < 512`, `16469 < 20161`); the T21 owner-bound grid ceiling; the
  analytic role of the seven bootstrap cutoffs (their arithmetic is recomputed
  and matches; their sufficiency is the inherited analytic-transfer
  hypothesis); and the PR559 exact-cover argument itself. Those remain exactly
  where the selected record places them.
- The Decimal cross-check is numerical validation with a third rounding, not
  an algorithmic proof obligation. The two interval enclosures are
  transcriptions of the pinned algorithms; a defect in the shared algorithm
  design would not be caught by any of the three evaluators.
- Inherited all-size/compiler, common-label/mutable-source, whole-call
  hosting, precision/tape, analytic and bit H1-H5 hypotheses remain
  assumptions. This note changes no selected result and claims no new kappa.
- Bootstrap cutoffs for steps 2-7 exceed 10^18; the record treats them as
  exact integers and so do I.

## Relation to predecessor audits

The seed-67 audit (`research/audit-kappa-floor-seed67/`) and navinor's PR894
reconstruction audited the frontier799 record: its reduction, its 47 margins
and its rounding prose. This audit covers the current selected record
(frontier890, U8/T21 on PR869/870 and Hao Yan's PR858 mechanism with the
PR589 bit supplier), adds the endpoint certification those works left open
(F1), and adds the quantified surcharge stakes and the T21 license scope
(F3-F5). The reduction method in F2 is the seed-67 method re-derived
independently; the exact-record comparison is extended to both rows here.

## Claim record

No pinned sprint coordination issue exists in the repository, so the claim is
recorded here: track 60-74, seed 73 (drawn from the operating system CSPRNG),
base commit `47481c89fd30a43f8f882eb4b391e89c29273fd0`, object the frontier890
endpoint-to-kappa accounting chain and its surcharge input, method exact
independent recomputation with three evaluators plus six tamper controls,
deliverable this note and its script. Checked open PRs and
`docs/research/pr-ledger.md` for overlap before submission; the closest
neighbours are the seed-67 audit and PR894, addressed above. Submitted as
[PR #957](https://github.com/CrocSwap/integer-mult-bounds/pull/957).

## Attribution

Reduction and constraint engines retained from the PR547/PR548 lineage:
`engines/outer.py` prepared by eumemic with Anthropic Claude assistance (47
constraints retained from icekylinx's PR144, adapted from Zhihao Chen's PR23;
balanced prefix from the RaD project); the assembly stage in chafreaky's
lineage with OpenAI Codex assistance. The audited record is the frontier890
maintainers' and contributors' work: T21 by Chafik Boukhalfa (PR890), U8 by
Jeremy Kothe (PR869/870), T16 by Hao Yan (PR858), the bit supplier from
eumemic/DreamingOfClouds (PR589 on PR555), the surcharge-removal review
credited to Rohan Arun (PR559). This audit is new work by sprint agent-09
with help from opencode, on base commit `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
