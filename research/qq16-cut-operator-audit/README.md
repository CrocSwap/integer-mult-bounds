# QQ16 retained-cut decoder: independent exact operator audit

**The ordered recovery in PR2443 passes an independent symbolic audit.** The
checker verifies both inverse orders on all 224 formal input arrays and all
224 independently specified observation arrays, using actual 73-dimensional
owner maps. No producer executable is imported. No new supplier or kappa is
claimed.

The additional failure control separates logical and physical charts: replacing
the logical owner-only map `D=(rho,0)` in the decoder with the native alignment
`A=(rho,delta)` produces a nonzero exact arbitrary-payload residual. The same
fault passes after every payload shift is forgotten. Thus payload-constant
fixtures alone cannot distinguish this incorrect implementation. This is a
deliberately injected fault, **not a defect found in PR2443**, which correctly
uses the logical maps.

## Audited contract and evidence

The audited predecessor is [PR2443](https://github.com/CrocSwap/integer-mult-bounds/pull/2443)
at `545c05e17243c962b112b91e7f84b4c1a41de7b8`. Read source hashes are in
[PREDECESSORS.json](PREDECESSORS.json). Its unread ports are
`J=[1,2,3,4,5,6,8,12]`; the other 88 ordinary ports are read. With
`(x1,y1)=F0(x,y)` and `(x2,y2)=B_1_2(x1,y1)`, exactly these observations are
granted, without intervening changes:

- `x1_A/T` and `y1_A/T`: 32 complete arrays at the F0 cut;
- `y2_A` and `C=x2_U`: 104 complete arrays at the B1 cut;
- `x1_(U\J)`: 88 complete arrays at the F0 cut.

This is 224 arrays in total, not 88 total records. Each array includes arbitrary
owner and payload contents. The retained first two events operate on pair zero;
the other three pairs are not decoded.

The [proof and audit interpretation](PROOF.md) explain the factorization into
F0 and the cut observation map. The checker reconstructs R from the immutable
predecessor's scalar prefix, rebuilds stage-1/stage-2 routes and translations
from its phase geometry, and compares all 224 entry/inverse pairs with the
emitted QQ16 packet. It checks the selected Grams, K, unread minor and both
minor inverse orders. Formal expressions retain independent array identifiers
and exact affine owner/payload operators, with rational coefficients.

[RESULT.json](RESULT.json) records four complete inverse identities and seven
rejected faults, including a concrete point-supported input for each residual.
The six other controls omit the old A baseline, omit the future T term, reverse
the C sign, apply port inverses before the scalar inverse, discard the B1 A
cut, or discard initial Y dirt. Source-file corruption controls and optimized
replay are registered separately. No floating-point acceptance is used.

## Reproduce

Python 3.10+ and the standard library suffice for the direct checker. The
repository's registered environment is Python 3.12:

```sh
python3 -I -B research/qq16-cut-operator-audit/verify.py
python3.12 -I -B scripts/research_package.py --package research/qq16-cut-operator-audit
```

Expected direct status: `PASS_QQ16_CUT_OPERATOR_AUDIT`. Replay is read-only and
compares the entire recomputed receipt with the committed file. Receipt creation
is explicit via `--write-result` and refuses to overwrite an existing file.
The source archive and frozen packages remain unchanged. Sources and Git
provenance are in [SOURCES.json](SOURCES.json); scope is in [TASK.json](TASK.json).

## Limits

This checks the mathematical decoder from PR2443's displayed formulas, not the
execution of its Python implementation. It imports no implementation from that
PR. The inherited QQ16 logical local contract, physical/logical conjugation,
and legal native kernels are not re-proved. The extra native-alignment mutation
is a diagnostic on the logical decoder; it does not execute a physical decoder.

Neither the remaining 17 schedule events nor final endpoint availability is
checked. Retaining the two cuts, native read permissions, storage, cleanup,
hosting, addresses, precision, all-size transfer, and the complete invoice
remain open. Four operator identities are not a formal verification of the
full multiplication theorem. No full selected cold replay was needed or run.

## Open next questions

1. Can a physical implementation realize the decoder with the correct
   input/output gauges? First trace each read in the pinned formula through
   the bridge relation `A T = T_common D`. The missing work is the mixed
   endpoint types and retention, not the scalar inverse.
2. Can the two retained cuts be reconstructed at final controller endpoints?
   First propagate the 224 observation arrays through the complete remaining
   schedule. A favorable scalar identity alone supplies no legal record.

Both questions and their blockers are recorded in [TASK.json](TASK.json).

## Credit

`starship-s` / PR2443 supplies the audited arbitrary-input cut decoder and its
observation contract; Gareth Davidson / PR2432 supplies its unread basis and
coordinate-read lineage. commdata2338 / PR2174 supplies the earlier two-query
cut recovery. Ali Romman / PR1969 supplies the QQ16 local maps and native
contract; Adam Gall / PR2093, kyzer1023 / PR2354, PR2389 and PR2419 supply
the hidden-family and read-set work. The retained Rohan Arun, Jeremy Kothe,
DreamingOfClouds and other source contributors keep their attribution in
[the source notice](../joint-query/NOTICE.md).

The independent reviewer code, exact operator audit, and diagnostic control
were prepared by ywz65 with substantial OpenAI Codex assistance. No independent
human or proof-assistant review is claimed. New work is Apache-2.0.
