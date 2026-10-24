# Validation record

Environment: macOS, CPython 3.12.2, standard library only. No installed solver,
network service, Lean, Docker, native compiler or historical heavy replay used.

## Executed development checks

- `python3.12 -B scripts/research_package.py --package research/auxiliary-span-six-cyclic-line`
  passed both declared science commands and source/metadata checks in under two
  seconds. An initial metadata check rejected the unrecognized outcome label
  `obstruction`; it was corrected to `negative-result` before this pass.
- Direct optimized science command also passed. Acceptance uses explicit
  exceptions, not Python assertions.
- `git diff --check` passed before publication preparation.

Science result: 120 projectors from two implementations; 12 cyclic projectors
in three groups of four; 300 pairwise symbolic projection checks; 12 ordered
eight-factor checks; final common-J two-run Laurent identities; nine-call
positive endpoint; five meaningful failure controls.

The program does not enumerate rational frame assignments, verify every
augmentation-quotient step of PR468 §5.1, or supply a physical implementation.
The proof explicitly depends on that written common-J lemma. Independent
human/proof-kernel acceptance, hosted CI and full selected cold replay are
not claimed.

Publication-source/export checks and independent review will be recorded in
the final handoff against their exact committed heads. The science program is
self-contained; its two predecessor README inputs are retained for source-bound
mathematical provenance and included by the official exporter.

## Independent mathematical review and publication evidence

A separate read-only AI-agent review inspected PROOF.md SHA256
`fcf6673d10ebb0a936fca28d6f811ab7d20e3e9438fc17f440f2b3e565e984ae`
and actual PR468 README §5.1, SHA256
`c12b33ef388deece0cbf891505a2ce2c0779a0c3a6cf1f0f7f7039bab59cbebd`.
It found no applicability blocker: the common-J lemma permits arbitrary
coordinate-diagonal targets and at most two rational relations; both tail
orientations project correctly; zero-extension preserves the subset-nullity
bound; and the singleton receives only its own coordinate calls. Root also
read the proof and confirmed its explicit inherited-premise boundary.
This is independent AI-agent review, not independent human or formal-kernel
acceptance, and not a complete fresh audit of PR468.

The first committed package, `3c7f2ec62401852823494a131761def53c0932d4`,
passed committed-byte and source-history checks on nine files; the sole source
history base is `4c0a359d88f22f05189d51f48387750b801a45d4`. Official export
and offline integrity check passed. The nine-file archive SHA256 was
`5ae743eee9507d7678e108edd22b9c324deb829cf93940fdc06bd86145875ebf`.
Actual Git-free normal and optimized science replays passed from that export.
These receipts bind that commit, not later changed bytes.

The final checker adds one exact rational rank-one eight-frame calibration:
the original nullity is two, both displayed relations meet the deleted
singleton call, and the retained core has nullity one. This directly exercises
the reason the proof must use kernel injection rather than assume disjoint
relation support. The final publication handoff records fresh checks for this
changed checker and the final committed/exported bytes.
