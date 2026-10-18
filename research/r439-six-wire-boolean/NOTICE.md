# Attribution and license

Prepared for Gareth Davidson (@bitplane), with substantial OpenAI Codex
assistance in the search, implementation, checks and writing. One AI agent
performed this pass. The independent interpreter is a separate implementation,
not independent human review. New work is Apache-2.0; see LICENSE.

Ross Richardson's PR936 (`0679fb6e1e4c91f573ae07ab1d0ea273b13c74e3`) supplies
the frozen input circuit and 340 of the inherited ADD savings. Its candidate,
certificate, README, NOTICE and LICENSE are retained unchanged. Gareth
Davidson's PR904 (`883a0bdf7792693e57c16be660824b57aacfbe05`) supplies the earlier
254 ADD savings, the adapted common.py helpers and native.py harness. That
harness follows Sagar Thakrar's R420 decoder-sharing native checks. Jeffrey
Cox (@namredips), PR754, is credited for the predecessor local-resynthesis and
positive-guard method cited by PR904 and PR936.

Ross Richardson's PR925 (`eb85d40a1ba80c2f776481fbeed1bae8cf04cfde`) motivates
the comparison with exact positive-transfer synthesis on one six-wire block.
Its search, candidate and 12-ADD minimum are not imported or recomputed here.
Frame 267 is unchanged in this contribution. The finite Gaussian elimination
search and independent truth-table checker are new code for this pass.

Selected PR589 is DreamingOfClouds' tuned punctured word on eumemic's PR555
and PR543 skeleton, with the retained PR545/493/510/425/370 ancestry. The exact
source checker and native exporter/checkers are used unchanged. Retain the
existing notices under `research/e8-bit-p111-tuned` and
`research/e8-bit-carrier-skeleton`, crediting eumemic, Dylan Crow, DaysSky,
Zhihao Chen and their predecessors. Source-specific AI disclosures remain.

PR848's restored-sharing barrier and PR933's paid-profile relocation and
reframing results informed scope selection. PR891 and the other B-block
constructions concern separate operators. PR915/926/941 optimize D under a
different interface contract; their candidates and savings are not composed
here. Accepted PR890/U8/T21 and its credited complex contributors supply
current context, not a changed source in this package.
