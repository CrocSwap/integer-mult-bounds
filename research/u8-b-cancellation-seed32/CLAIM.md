# Sprint claim — U8 B-gate cancellation audit

- Track / seed: complex supplier (20–39), OS-random assignment seed 32.
- Base commit: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`.
- Current selected record: PR942 / T37, conditional kappa `1661960547713947/10^18`; no frontier edit is proposed.
- Three narrow candidates inspected: (1) coalesce fourteen dependency-safe repeated A additions, (2) delete four dependency-safe inverse B-addition pairs, (3) re-lower large cleanup coefficients. Seed 32 selects the B region; candidate (2) has the strongest favorable complete local budget because it removes work rather than changing coefficients.
- Claimed object: four apparent inverse add pairs in the selected U8 `native/local/CANONICAL-WORD.json.gz`, B indices 176/178, 194/196, 204/206, and 278/280.
- Method: source-pin the accepted replay archive; independently replay the exact scalar word on arbitrary basis columns before and after deleting each pair; prove a local commutation/cancellation criterion; regenerate the emitted local programs; compare exact semantic, frame, profile, macro, and primitive invoices; include single-deletion and dependency-touch negative controls.
- Expected deliverable: a scoped finite complex-supplier construction or a precise obstruction if native/frame admission fails. No new kappa without a complete supplier and outer reprice.
- Expected finish: 2026-10-13 21:00 CEST.
- Coordination: no pinned sprint coordination issue was found; recent open-PR title/body searches found no U8 B-cancellation claim, so this claim is local.

## Final update

Completed a finite complex-supplier construction. Four three-shear fragments were
rewritten exactly, saving four B-stage macros and 52 real-component primitives in
each orientation while preserving the full 728-column B map and local paid profile.
The standalone verifier and nine controls pass, as do the unchanged emitter/frame
auditor, optimized and relocated replays, selected-record checker and five selected
record tests. No global supplier reprice or new kappa is claimed.
