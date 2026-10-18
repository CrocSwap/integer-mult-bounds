The frozen PR1048 pricer returns two false root brackets at its unchanged
default34-term/24-digit settings. For explicit rank-one profiles with m=9 and
W=10^64, both the surcharged and unsurcharged functions return
`[1/20-10^-24,1/20]`, although an exact tenth-power integer inequality proves
the root is strictly greater than1/20. Neighboring profiles with one additional
call have roots on the opposite side and receive the same original bracket.

This turns the maintainer's already recorded undecided-sign finding into
reproducible false certificates. The package retains the unchanged original
code/notice at07730cd, proves that float nomination already encloses these roots,
and supplies a bounded tri-state bisection that certifies both endpoint signs
or explicitly returns unresolved. An independent integer-only checker proves
the root intervals without importing the pricer or repair.

Validation: both original defaults, four paired fixtures, one ordinary-profile
control, capped/equality/initial-unknown cases, ten rejection controls, source
inventory checks, optimized and assertion-enabled replay. Reproduction and
actual outputs are recorded in README.md and VALIDATION.json.

These are abstract arithmetic profiles; no realizable supplier or selected
PR589/PR1094 failure is claimed. PR1048's search, ordering and neighborhood
claims remain deferred. Credit to flemhhh's pricer and Douglas Colkitt's prior
finding; retained source lineage and notices included. @woklerx with substantial
OpenAI Codex assistance, Apache-2.0.
