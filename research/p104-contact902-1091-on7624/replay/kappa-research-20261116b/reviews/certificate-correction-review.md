# Certificate census correction: independent static review

**HOLD for one pre-existing source-verifier contract gap**, described below. The census correction itself is consistent with the source's nonzero snapshot. Review is read-only; no scientific imports, execution or tests. The frozen failed gate and its evidence were not changed.

## Source snapshot and corrected census

Source `verify_certificates.py:68–73` constructs the snapshot from live rows except the erased owner **only if the row is nonzero**. `compose7624_completion/certificates.py:64–68` now compares the stored `other_live` with exactly this nonzero count, while separately recording total other-live and nonzero-other-live counts (`79–83`). The original frozen checker compared to `len(live)-1`; the data-only diagnosis records 137 structural discrepancies among 204 records and explicitly did not replay scalars. The source verifier does not itself compare the certificate's `other_live` field to that count (`141–162`), so mapping stored metadata to the snapshot count is an evidence-supported hypothesis to verify on actual full replay, not an already verified 204/204 outcome. The corrected check retains a strict per-record equality rather than dropping the metadata predicate.

The correction retains the full closed-trace argument: zero fresh INIT; only active operands, linear operations, COPY prezero then assignment, valid CLEAR relation, no external births; independent final public rank `n`; and no opened owned lifetimes at completion. Zero rows do not affect rank, so the distinction in census does not weaken the derived rank of **all other live rows** after each valid CLEAR. Reported per-record rank is derived only when whole replay ultimately passes final rank; it is not an independent elimination at each cut or a public-only rank claim. The exact 204 records, source/candidate binding, seven zero count, clocks, ownership, public domain, target, certificate relation and final endpoints remain as in the frozen version.

`168–174` correctly changes the rank-two counterexample's first other-live snapshot count from three to two: its other live rows are zero, `y`, and `x`. The synthetic control `188–197` checks a positive nonzero census and demands the appropriate reason for both including a zero and omitting a nonzero. These are code paths, not observed passing controls. The literal diff is confined to the census, reported counts and rank, the corrected fixture, and those controls.

## Blocker: zero-row providers

The source verifier's `verify_comb` at `113–117` rejects a certificate provider absent from `snap`; `snap` excludes zero rows. The new `check_record` at `71–77` only requires a provider be live and not the target. A live public zero-row provider with a nonzero coefficient is therefore admitted by this predicate if the rest of the terms reconstruct the target, whereas the original source verifier rejects it. This gap predates this particular census correction, but it is material to the requested strict preservation of the source certificate relation contract.

Minimal fix: additionally require that each referenced provider row is nonzero, with a specific diagnostic, and add a production-`check_record` control in which adding a nonzero coefficient for a live zero provider leaves the algebraic target unchanged and must reject specifically at that provider check. Keep the positive relation fixture and all existing controls. If this additional check encounters actual source data, stop and report the evidence rather than altering source certificates or weakening the original condition.

## Identities

- Corrected copy `compose7624_completion/certificates.py`: `b1ff7ad11c09d33d6c31de2e94ad8fceb9b24941aa327af206eca94123fcb242`.
- Frozen original `compose7624/certificates.py`: `96a058596462bf38ffae27bbd7c5cf16dc33d0b6fbf4151d783997e4eb2d4dba`.
- `CERTIFICATE-METADATA-DIAGNOSIS.json`: `b84861769615fcb2519ea20f174b2e52fd350df546f088977a56fb84bfdad5ea`.
- Source `verify_certificates.py`: `6be256ca0de88ed99398f8d170e26f71e700c14398f4dbe97f6c6ab693cffbce`.

A follow-up review must bind the revised file hash. This review does not authorize a stage-only continuation or full qualification and does not assert the eventual result.

## Successor correction review

**PASS for the scoped static correction**, superseding the provider hold above, for corrected copy SHA-256 `10714b5e758ce2bd23432c7824dbcb719b9f81ae2444a32a2eb25d8d284d1411`. `check_record:71–74` now requires each already public, live, non-target provider to have a nonzero row, matching source snapshot membership. The positive fixture remains, and `188–202` adds a live zero public provider with a nonzero coefficient that leaves the target algebraically unchanged; its control requires the specific `zero_provider` rejection. The two earlier nonzero-census mutation controls are unchanged. The diff from the frozen checker is limited to these corrections, counts and fixtures; no other scientific logic changes were found. The correction preserves the other-live rank argument and all previously reviewed 204-record, identity, COPY, relation and endpoint predicates.

This is inspection, not execution: the 24 expected synthetic controls under normal and optimized interpreters, and actual 204 source/candidate certificate replays, remain to be observed if the user separately authorizes the proposed stage-only completion. The source `other_live` interpretation remains a hypothesis tested by that replay, and no complete first gate or full qualification is claimed. The prior failed attempt and original frozen files remain the controlling historical record.
