# Attribution and assistance disclosure

Prepared for **@woklerx** with substantial **OpenAI Codex assistance** in research, mathematics, implementation, verification and writing. New files are Apache-2.0; LICENSE is copied unchanged from the repository. No independent human review is claimed.

**ToikY**, with disclosed OpenAI Codex assistance, supplied the retained `research/complex-swap-runs-seed37` compiler, arbitrary-dirt boundary construction, exact dense checker and complete historical scalar receipts. This package imports those pinned compiler/checker files read-only to identify and replay the actual boundaries. The new finite forward and backward quotient searches, their proof and matrix witness checks are separately written. The prior d+c+1 construction is not claimed as new.

**Ross Richardson (@RossRichardson), PR919**, supplied the sign-normalization compiler with substantial OpenAI Codex assistance. Its pinned optimize_run is used for the comparison. The joint pilot combines inherited location/sign invariants and uses standard three-ADD rotations; it is not a priority claim for those mechanisms. An explicit in-memory one-condition adaptation of ToikY's checker permits signed prefix containment; all original endpoint checks remain intact.

**Sagar Thakrar, PR696**, supplied the pinned paid dyadic primitive lowering, with OpenAI Codex assistance. Its primitive vocabulary and original Horner circuit credit **icekylinx's PR425/433/531 lineage**. The known-zero CLEAR principle belongs to **PR839**, as credited in the predecessor package; this contribution does not claim those savings.

The historical source programs come from **Chafik Boukhalfa's PR626** on **Jeremy Kothe's PR622** CK construction and retained JP8 lineage. Their original notices, AI disclosures and source licenses remain in the repository, along with the supplier work of **DreamingOfClouds**, **eumemic**, **Rohan Arun** and the wider compiler/hosting lineage. The detailed inherited credits remain in `../complex-swap-runs-seed37/NOTICE.md`, `../ck-sign-normalization-seed22/NOTICE.md`, `../complex-dyadic-lowering/NOTICE.md` and the historical provider packages. No predecessor source or notice is modified.

Concurrent PR1064 (Ali Romman's factory fusion), PR1060 (Ali Romman's P111 COPY construction), PR1032 (@woklerx's earlier cache census), and PR1033 (bbMisk's factory-window minima) are overlap references only. No unpublished source or reported gain from those contributions is imported.
