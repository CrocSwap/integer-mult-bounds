# Charged common-A broadcast readout for five-source masks

**Scoped recursive-interface construction. No new kappa or selected-supplier admission is claimed.**

## Result

Specialize the universal dirty-connector task to one common exact F2-linear output map A and five arbitrary exact source maps B0,...,B4. Add one operation:

    R_S(z): for each target mask m in S, y_m += A z.

Each target row and the connector may start with arbitrary dirty contents. R_S leaves z and unselected targets unchanged. Its price is one complete A evaluation, every selected full-row update, and the actual target-list, routing, dispatch, scratch, and restoration costs.

On the fixed ten-toggle source word

    B0 B1 B2 B0 B3 B1 B4 B2 B3 B4

the prefix masks are

    0, 1, 3, 7, 6, 14, 12, 28, 24, 16, 0.

The first ten prefixes are distinct. The predecessor certificate assigns two readout boundaries to each nonzero mask except mask 21, which uses four; the selected prefix masks xor to the corresponding target mask in every row. Grouping those 64 readouts by the ten distinct prefix values gives ten R_S calls and still exactly 64 target-row additions. A unicast implementation on the same B word makes 64 ordinary A calls; the broadcast version evaluates A ten times, saving 54 full A evaluations while adding no row writes.

The broadcast target sets, indexed by the prefix mask q, are:

| q | Targets updated by R_S |
|---:|---|
| 0 | 1, 3, 6, 7, 12, 14, 16, 21, 24, 28 |
| 1 | 1, 2, 13, 15, 17, 21, 25, 29 |
| 3 | 2, 3, 4, 5, 19, 27, 31 |
| 6 | 5, 6, 8, 10, 22, 26, 30 |
| 7 | 4, 7, 9, 11, 23 |
| 12 | 10, 11, 12, 13, 20, 21 |
| 14 | 8, 9, 14, 15, 18 |
| 16 | 16, 17, 19, 22, 23 |
| 24 | 20, 21, 24, 25, 27, 30 |
| 28 | 18, 26, 28, 29, 31 |

The sets contain 64 target incidences in total. Mask 21 appears four times; every other mask appears twice. Events are issued on the first visit to each q. The terminal q=0 is the repeated initial state and requires no additional A evaluation.

The two-source fixture is smaller: B0 B1 B0 B1 has prefix masks 0,1,3,2,0. Three broadcast events at masks 0,1,3 serve the three nonzero target masks with six row updates.

## Exact dirty-state identity

For a boundary with prefix mask q, the dirty connector is

    z_q = z_initial + sum_j q_j B_j x_j.

If R_S updates target m at the selected boundaries q_1,...,q_t, its total increment is

    (t mod 2) A z_initial + A sum_j ((q_1 xor ... xor q_t)_j) B_j x_j.

The certificate has even t and xor q_l = m. Thus the dirty connector contribution cancels and target m receives exactly

    y_m += A sum_{j: m_j=1} B_j x_j.

Every B_j appears twice in the ten-toggle word, so z returns to its original dirty value. The proof uses linearity over F2 only; no map is assumed invertible and no A/B commutation is used.

The new alphabet premise is specifically that all output maps are the same A and one call may add the same computed A z to an explicit set of targets. If the A_i differ, this sharing is unavailable. The operation never overwrites a target or assumes clean data.

## Complete cost accounting

Let b_j be the cost of one B_j child, including source and coefficient access, arithmetic, the connector update, recursive children, private scratch, precision, frames, and return-to-entry state, but excluding its root instruction descriptor and dispatch. Let a be the corresponding complete evaluation of A z before adding its output to target rows, again excluding root dispatch and target updates. Let w be the cost of reading and updating one target row. Let P cover common input storage, one-time coefficient preparation, startup, and final interface transitions. Let D_u be all ordinary-call dispatch, routing, and instruction costs for the 10-source/64-unicast schedule. Let D_b include every broadcast dispatch, target-list routing, and additional instruction cost.

For the same fixed source word:

    C_unicast   = P + 2 sum_j b_j + 64(a + w) + D_u
    C_broadcast = P + 2 sum_j b_j + 10 a + 64 w + D_b

Therefore the exact saving in this model is

    C_unicast - C_broadcast = 54 a + D_u - D_b.

All 64 target writes are paid in both invoices. No saving is credited to source calls, copies, or free targets. The mechanism improves the invoice exactly when D_b - D_u < 54 a. At a=w=1/2 and equal D, the displayed unit normalization gives 27 units saved; this is an example price point, not a measured runtime or an admitted supplier cost.

The certificate gives a fixed-width program description. Source IDs use three bits, a boundary/state ID four bits, target IDs five bits, an opcode one bit, and broadcast target counts four bits. The ordinary encoding costs 680 bits:

    10(1+3) + 64(1+4+5) = 680.

The broadcast encoding costs 450 bits:

    10(1+3) + 10(1+4+4) + 64(5) = 450.

This accounts for every source instruction, broadcast state, target-list length and target ID. The encoded program storage and reads are included in D_u and D_b. It saves 230 descriptor bits under this stated encoding.

For a dense F2 matrix-vector reference implementation, initialize one scalar accumulator to zero for each output coordinate of A z, xor in all L products, and immediately xor the result into the selected target coordinates. No full-length temporary is used. With L coordinates, one A evaluation uses L^2 coefficient reads, L^2 connector reads, L^2 binary products, L^2 accumulator xors and L scalar zeroes. Each selected target adds L target reads and L target writes; all 64L pairs are charged. The candidate uses ten A evaluations; the unicast comparator uses 64. Both use the same ten B evaluations, each with its full coefficient/source reads, binary products, accumulator xors, scalar zeroes and connector updates recorded in CERTIFICATE.json. Persistent storage is 6L^2 coefficient bits and 37L data bits (five sources, connector and 31 targets); extra full-length rows: zero; scalar accumulators: one. Program generation and role IDs are fixed by the certificate. This dense row model has exact F2 arithmetic, so it has no rounding, phase, frame, hosting or tape-head expense. For a recursive A, all recursive-child, precision and interface costs belong in a; the new operation is not admitted until its real D_b is measured.

## Verification

From the repository root:

~~~sh
python3 -B research/universal-connector-boundary/verify.py
python3 -B research/common-a-broadcast-readout-seed4a52/verify.py
python3 scripts/research_package.py --package research/common-a-broadcast-readout-seed4a52 --check-only
python3.12 scripts/research_package.py --package research/common-a-broadcast-readout-seed4a52
~~~

The scoped verifier checks every output mask and dirty parity from the prefix identity, dense exact matrix replay over all 111 five-source basis columns and 64 additional dirty cases, and the two-source fixture over all 18 basis columns and 32 additional dirty cases. Three controls reject an omitted source restoration, a wrong output prefix difference, and a missing target update.

## Pins, overlap and limits

This cycle accepted seed 4a52e71a301f7115ab632ed556f62fad on the recursive-interfaces track, task connector-alphabet-change, catalogue priority revision 3. Its exact base is 0b1cccf86e2f5132ed286a26ef0a681a495740ea and the selected-record SHA-256 is 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32.

At that base the selected result is Rohan Arun's #1094, conditional kappa 0.001672660197076918. Its review is docs/research/community-batch1099-review.md; source manifest is research/community-frontier1094-audit/SELECTED-SOURCE.json; assembly certificate is research/community-frontier1094-audit/ASSEMBLY.json (SHA-256 1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045); selected reproduction is make frontier1094-verify. This package does not edit or replay the selected construction.

Predecessors are Ross Richardson's [PR943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) at head cf360b4b09b7d0419decdd6ac85421fefed55bdd, which supplies the universal source-prefix witness and dirty-connector contract, and CubeJerry's [PR889](https://github.com/CrocSwap/integer-mult-bounds/pull/889) at head e2021d1c9e06948528cbc0a8fd7079b671da981d, which batches outputs sharing a common right factor. This contribution shares the output-side A across changing source-prefix states; it does not claim priority over the related common-factor sharing lineage. The current source-side DUO [PR1531](https://github.com/CrocSwap/integer-mult-bounds/pull/1531), head 892b28a3358b16c9083036f71e1ef505ccf5d20a, and triple-sum [PR1518](https://github.com/CrocSwap/integer-mult-bounds/pull/1518), head 0c6a58aaf22e0fc1b34497f8f6f80db6212b4621, use different added calls. A fresh overlap refresh at claim time covered 385 open PRs and 337 Discussion records and found no matching common-A broadcast claim; this is not a proof of novelty.

The result is a finite interface construction with a priced break-even condition. It does not show that the selected multiplication supplier exposes a common A, does not discharge the all-size/compiler, native routing, precision, or outer analytic assumptions, and does not change the selected kappa.

## Open next questions

- **Question:** Can a selected recursive supplier expose the same exact A evaluation as a streamed result to multiple dirty output rows while keeping D_b - D_u below 54a?
- **Why it matters:** Only a positive fully priced realization in the selected supplier can turn this interface construction into a conditional kappa improvement.
- **First step:** Find two output roles in the selected source manifest with a byte-identical A map, then write the exact recursive child and target-update contract for those roles.
- **Blocked by:** The selected #1094 construction does not currently identify a common-A broadcast provider or an admitted per-target write tariff.

## Credit

Prepared by OpenAI Codex with GPT-6, with substantial AI assistance disclosed in TASK.json. Ross Richardson's PR943 supplies the prefix-path witness and dirty-connector boundary; CubeJerry's PR889 supplies related common-right-factor multi-output batching. The current contribution uses neither as an admitted supplier and claims no new kappa. New package material is under Apache-2.0.
