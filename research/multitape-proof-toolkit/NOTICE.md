Fixed-tape proof toolkit, 2026-10-13. New work is Apache-2.0.

New theorem implementations, the finite compiler and scheduler, dirty-frame
proofs, examples and replay infrastructure were prepared with substantial
OpenAI Codex assistance, including three parallel Codex agents. No submitting
user's name, email or private machine paths are included.

Mathlib supplies its Turing tape/TM2 and asymptotic vocabulary and retains its
own upstream licensing and attribution. No Mathlib source tree is vendored.
The toolkit's finite absolute-coordinate convention was compared against
platypii/integer-mult-bounds-lean, Machine.lean at
4f270864a297374cae8e443c520c6225b625c0d5. Lean PR1 and PR2 supplied inspected
statement, adapter and heterogeneous-host context; their proof implementations
are not imported or copied into this package.

CrocSwap/integer-mult-bounds PR1379 by commdata2338 supplied the motivating
recursive parking boundary and named open Lean frame/composition work, building
on rfu08's PR64 transfer lineage. Its stream implementation is not vendored or
claimed proved here. PR1608 and the earlier PR893 audit lineage motivated exact
declaration/report coverage; their audit implementations are not imported.
Original selected construction and upstream contributors retain their credit.

The package proves its displayed universal sufficient machine/transfer results.
It changes no supplier, selected record or kappa and does not represent a
formal verification of the full fast multiplication theorem. Local kernel
checks, hosted CI, public submission and external human review are distinct.

## Parking and binary-proof reuse

ParkStack modifies the Apache-2.0 PR64 TapeStack.lean/TapeStackPush.lean primitives
by rfu08, pinned at bce54fb3f895cbe5cd4c0eb477c3afeed100190f: actual optional
halting, generic physical tape selection, absolute cells/heads and arbitrary past.
The root LICENSE retains the upstream Apache-2.0 text. PR1379 by commdata2338
(head3a45bd089ad56c38b55da8d80d7b056f2d90e5fa) supplies the written caller/table
lineage; the tagged assembly and trace proof are supplied here.

BinaryCanonicalOutput narrows fixed-width binary lemmas from our independently
formalized Problem1.8 output adapter. The portable module contains the pure
proofs and their Mathlib imports; that initial pure module needs no personal RAM/TM import. This release also
bundles the complete arithmetic dependency closure under public module names,
including reusable Problem1.8 RAM/TM sublemmas; no external personal library is
required.
PORTING.json records canonical and portable source hashes and exact import rewrites.

Platypii is reference-only: no platypii implementation or proof source is copied.
Its existing normalize_exists/carryOut_exec overlap is acknowledged in FRONTIER.md.
No upstream normalization novelty or complete fast multiplication result is claimed.


## Anchored compiler and arithmetic ABI extension

Seven new modules implement finite tape-bank embedding, a generic physical
caller, clean unmarked lifecycle, compiler stack anchors, a literal five-state
serializer and a closed six-tape quadratic output example. Existing schoolbook
arithmetic and its checked Problem1.8 support proofs are reused, with systematic
public import/namespace renaming only. PORTING.json binds every source pair;
the complete public closure receives fresh kernel and defining-module axiom checks.
New routine/table/control proofs are credited to this Codex-assisted contribution,
with three parallel agents. No new kappa or complete fast multiplier is claimed.

Current platypii reference69839dbc892690d972faed2207674c1b6e73a792 already contains
RecoverOutputSerialize and RecoverPublicOutput. Their existing serialization and
cleanup theorems retain credit and are reference-only, not copied source here.
The new serializer bridges our actual moving-head compiler stack to origin output.
