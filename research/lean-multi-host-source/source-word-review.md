# Review of the actual normalized word

The selected invocation is PR #442 commit `4e16d001d505d4f21dd2bcfc44591f9be4c279bd`, stage 2, replica 0, pair 0, forward orientation. It has 987 original roles and a separate clean private role 987.

I independently decoded all 456,048 bytes of the replay's `249-records.bin` as 19,002 little-endian six-integer records. Its SHA256 is `99cb283793818ad03f8f16f95a8eb23d0b18769d0657d58043fb7a427471c35d`. Reconstructing the forward records by the pinned `bit_global.py` rules gives exactly both vendored templates' forward words. Their canonical forward JSON SHA256 is `4ed9ed1f7756ea6ff2c299b61ed1dc3fe0fa5bbbb91b5170133596b452c8085e`.

A separate parser compared every ordered event in `MatrixData.lean` with those reconstructed records. All 96 chunks are present in order: 95 chunks of 200 events and one of two events. There are 14,693 additions, 4,291 frame transitions, nine copies, and nine erasures. No operation is filtered out. The selected invocation appears exactly once in the hosted template's call list.

The normalization preserves opcode, source/destination indices, and coefficient parity. Frame transitions remain explicit opcode-0 events but act as the identity in this scalar model. Their complete frame metadata is preserved in the source snapshots, not in the scalar event projection. Independently replaying frame metadata checked equal-frame additions, frame ranks, centre locking, private reads only while a centre is open, the nine rank-eight copy/erase pairs, and the final frame table. That Python check is separate from the Lean matrix theorem and does not itself prove physical frame transport.

The generated checkpoints are untrusted proposed matrices. Lean checks each through definitional reduction of the literal interpreter, then composes all 96 checks. Every original role starts with its own formal input variable. The result restores all 747 helper rows, adds each source-data row to its corresponding destination-data row, and restores private role 987 to zero. The accumulated guard also checks clean copying and matching erasure as identities of symbolic rows. The generic reflection proof is what turns these symbolic identities into statements about every Boolean assignment; a few selected input tests would not suffice.

The binary tree is a checker data structure. Its 36 unused leaves are zero padding beyond roles 0–987, and the checked index bounds exclude accesses to them. They do not represent extra algorithm registers.

`SourceControls.lean` binds two controls to actual instruction indices. Omitting XOR event 218 loses exactly input variable 243 from row 126 at the end of its chunk while retaining that chunk’s clean-work guards. Applying the first actual COPY instruction to an explicitly dirty-private state fails its clean-work guard and would overwrite the dirty value. These are focused instruction/chunk controls, not complete mutated-word replays. A third control confirms that helper 3 survives the complete literal word, ruling out a false all-zero helper endpoint.

This review covers source extraction and normalized scalar semantics. The separate frame, route, ownership, and hosting proofs must supply the physical connection. It establishes no register-cost or κ bound.
