# Attribution and license

Prepared for Gareth Davidson (@bitplane), with substantial OpenAI Codex
assistance in research, implementation, mathematical checks and writing.
One AI agent performed this pass. Separate checking implementations do not
constitute independent human review. New material is Apache-2.0; see LICENSE.

The direct parent is Gareth Davidson's PR952 at
`11d24706f06e95271804c9438869546724c67aab`, integrated unchanged on main. Its
Gaussian nominee generator is reused without modification. Its pinned
literal set-valued interpreter, source checker wrapper and prefix-expression
binding are reused as a separate implementation from this pass's macro
evaluator. common.py, native.py and artifact test scaffolding are adapted
from that package. The native harness follows Sagar Thakrar's R420
decoder-sharing checks. Existing source notices retain their disclosures.

Ross Richardson's PR936 at `0679fb6e1e4c91f573ae07ab1d0ea273b13c74e3` provides
340 of the inherited savings. Gareth Davidson's PR904 at
`883a0bdf7792693e57c16be660824b57aacfbe05` provides 254 and PR952 provides 38.
Jeffrey Cox (@namredips), PR754, supplied the earlier local resynthesis and
positive-guard method credited by these predecessors. The additional 240
ADD savings in this package are accounted for separately.

zeusinsight's PR857 and Jerry Chen (@CubeJerry)'s PR906 already admit distinct
B-block constructions using full precision checks despite reverse positive
growth. They establish relevant precedent for relaxing a local guard; no
priority for that general idea is claimed here. Ross Richardson's PR925
gives a 12-ADD exact positive-transfer minimum at frame 267, shorter than
our 13-ADD nominee. Its recipe and optimum certificate are not imported.

Selected PR589 is DreamingOfClouds' tuned punctured word on eumemic's PR555
and PR543 skeleton, with retained PR545/493/510/425/370 ancestry. Exact source
checkers and native exporter/checkers are used unchanged. Preserve notices
in research/e8-bit-p111-tuned and research/e8-bit-carrier-skeleton, crediting
eumemic, Dylan Crow, DaysSky, Zhihao Chen and their predecessors.

PR915/926/941, Ross Richardson's concurrent PR965 and Sricharan Vagvala's
PR967 optimize D under a semantic interface. Cinna Davis's PR973 optimizes
B frame 509. No candidate or saving from these separate branches is composed
here. Ross Richardson's PR963 closes a frozen receiver-plan class and helped
select this pass's scope. Jonathan Capalbo's accepted PR942/U8/T37 provides
the current assembly context and is unchanged by this contribution.
