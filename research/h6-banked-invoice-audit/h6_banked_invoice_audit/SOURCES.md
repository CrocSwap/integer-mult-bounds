# Source register and authentication boundary

All references are public source data. No external write was performed.
The frozen arithmetic inputs are those in the task, not a moving frontier.

## Imported closure: authenticated before import

Retained revision: `81e81af67714bdc8d1693b0bf5c29468b92f62ff`.
Merged PR606 head supplied by the task:
`048f884ea9c222faad43e8bb01e2a6863f6925d4`.
The task reports the four files are byte-identical at both commits; the
executed closure is authenticated against the retained-revision full-file
hashes below. This audit does not claim an additional independent binary
comparison of both Git commits.

The full pinned files were viewed at their public URLs and transferred into
the local package as text. Direct container downloads were unavailable. All
four resulting byte strings matched their supplied full-file SHA-256 values
**before any upstream import**. Thus this is not an import of unchecked
excerpt concatenations. Source bytes were checked again after execution.

| File relative to repository | Bytes | SHA-256 |
|---|---:|---|
| research/niemeier-lattices/workbench/paid-controller/banked.py | 4796 | 8fb244f0f8dd007b29bc033c709bc04acd39fb562fb9c5382e7b4573233fb079 |
| research/niemeier-lattices/workbench/paid-controller/portable.py | 2800 | 95d245eb15ff930847b6872eb10e9d1feb382ce135013e18ab5737ae626efde8 |
| research/niemeier-lattices/code/costs.py | 16210 | 885303fde89db6153b9cf74e229e5ababe511f971c2f928f93355ac4740631e8 |
| research/leech-lattice/code/screen.py | 12756 | 6118abd81e8860bdb551526029d8b36958835de52adb8f50c1a43bb247005385 |

Each exact URL is also recorded in `EVIDENCE.json` under `source_files`.
The URL prefix is:

https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/81e81af67714bdc8d1693b0bf5c29468b92f62ff/

Only `base`, `helper`, `threshold`, `invoice`, their required pressure/interval
functions, and module initialization were used from this closure. We did not
call `run()`, `source_check()`, geometric verification, a native compiler, or
any of the historical controller scans. The code's historical PR592 default
is authenticated as a constant, expressly excluded as a scientific target.

## Model, attribution, and target references

[S1] Dominik Scholz, PR606 and retained banked accounting:
https://github.com/CrocSwap/integer-mult-bounds/pull/606
https://github.com/CrocSwap/integer-mult-bounds/blob/81e81af67714bdc8d1693b0bf5c29468b92f62ff/research/niemeier-lattices/workbench/paid-controller/PAID-CONTROLLER.txt

[S2] Moment screens and construction caveats:
https://github.com/CrocSwap/integer-mult-bounds/blob/81e81af67714bdc8d1693b0bf5c29468b92f62ff/research/niemeier-lattices/COSTS.txt

[S3] Upstream attribution notices:
https://github.com/CrocSwap/integer-mult-bounds/blob/81e81af67714bdc8d1693b0bf5c29468b92f62ff/research/niemeier-lattices/NOTICE
https://github.com/CrocSwap/integer-mult-bounds/blob/81e81af67714bdc8d1693b0bf5c29468b92f62ff/research/leech-lattice/NOTICE

[S4] DreamingOfClouds's original H6 response, supplied creation time
2026-10-14T04:10:46Z:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18914612
The task's response-body SHA-256 is
`596422e39ead6c6f629412c052d8ef83a70611dfe4d56ad284cf208837f48cb7`.
This is a **supplied body hash**, not a newly authenticated raw-comment hash.
The visible public text was read and matched substantively to the supplied
response. It is not part of the imported code closure.

[S5] Retained PR890 checkpoint, exact target read from its `kappa` field:
https://github.com/CrocSwap/integer-mult-bounds/blob/81e81af67714bdc8d1693b0bf5c29468b92f62ff/certificates/checkpoints/frontier890.json
`1661957774647029/1000000000000000000`.
The associated construction/certificate chain was not replayed here.

[S6] Selected record at the task's pinned main revision, exact target read
from its `kappa` field:
https://github.com/CrocSwap/integer-mult-bounds/blob/0a201997097b8a89b638f3a2afcb35db4184c8b2/certificates/selected-result.json
`836330098538459/500000000000000000`.
The task supplies Git blob `ae6a99f28aa468649eb66a361e764d769363bf11`.
The target field was verified in the pinned public text; the complete blob
hash and selected construction were not independently replayed by this audit.
“Selected” below always means this pinned selection, not an assertion about
whatever a moving main branch might select later.

[S7] H6 proposal provenance:
https://github.com/CrocSwap/integer-mult-bounds/pull/1590
Task-observed head `08e134b4a0c7f04869dae703f2a2e688e53c44f0`;
H6 table reported unchanged from `8423efd138226d2d760a01b91573db186c3ca76c`.
The task's quoted PR1424 comparison is `0.001676855229071321`.
PR1424 comparison head supplied by the task:
`bfe423c24555baf35dab991a8d6fe723a038945c`.
https://github.com/CrocSwap/integer-mult-bounds/pull/1424
No longer endpoint was substituted into that frozen comparison.

## Later author supplement: read, not executed

[S8] A later reply in the same discussion publicly linked an exact commit:
https://github.com/DreamingOfClouds/integer-mult-bounds/tree/b496aed769dd724cd1ff6b921cade626562be27b/research/h6-banked-breakeven
https://raw.githubusercontent.com/DreamingOfClouds/integer-mult-bounds/b496aed769dd724cd1ff6b921cade626562be27b/research/h6-banked-breakeven/price_h6.py
https://raw.githubusercontent.com/DreamingOfClouds/integer-mult-bounds/b496aed769dd724cd1ff6b921cade626562be27b/research/h6-banked-breakeven/README.md

This was observed during the audit on 2026-10-14. It supersedes the initial
“not supplied at preparation time” status; it does not retrospectively add
scripts or a ceiling definition to the original response itself. The request
for those sources remains at:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18914809

The newly visible price script specifies float versus Fraction comparisons,
a [0, 2,000,000) search range, a longer PR1424 title target, and the ceiling
ratio. Its main loop would perform a different target/mode set. It was read
as clarification, not executed, imported, hash-authenticated, or represented
as the author's original previously unpublished implementation. Its
structure/Walsh programs and saved runs were not independently verified.

## Coordination and scope

https://github.com/CrocSwap/integer-mult-bounds/discussions/1635
The claim and advisory expiry are coordination metadata, not proof premises.
The user/root retains all posting and coordination authority. No posting,
claim update, PR, installation, source-package edit, or frontier change was
performed by this audit.
