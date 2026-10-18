# Attribution and license

Prepared for GitHub contributor **woklerx (@woklerx)** with substantial
**OpenAI Codex assistance** in task selection, research, implementation,
proof analysis, independent implementations, verification and documentation.
Several scoped AI workers collaborated; no independent human review is claimed.
New work is offered under the repository's **Apache-2.0 license**.

This contribution depends on and credits:

- **Gareth Davidson (@bitplane), PR952**: the complete six-wire Boolean-synthesis
  candidate is the actual input, including its earlier PR904 contributions.
  Its exact `candidate.json.gz` is consumed without modification; its `verify.py`
  supplies credited whole-word scalar/prefix checks, and its `common.py` is
  imported by that verifier. Earlier savings remain his and the named
  predecessors' work. Source PR head: `11d24706f06e95271804c9438869546724c67aab`.
- **Ross Richardson (@RossRichardson), PR936 and PR925**: the five-wire parent
  of PR952, the earlier exact positive-transfer frame267 result, and framing,
  cleanup and exported-record verification routines. `search.py` adapts PR925's
  row-subtraction recurrence with attribution. The selected PR589 frame281
  matrix is conjugate to PR925's target, so that initial lower bound is prior
  work. The distinct PR952 transfer and the paired reverse-envelope boundary
  are the new scoped objects. `verify.py` imports PR925 helper checks unchanged.
- **Jeffrey Cox, PR754**, and **mtpsl, PR691**: small-GL prefix synthesis and
  the earlier fixed-integer-transfer/reverse-domination lineage, respectively,
  as credited by the consumed PR904/925 packages.
- **Gareth Davidson, concurrent PR980**, and the **PR857/906** lineage credited
  there: complete-prefix admission despite local entrywise growth. PR980's
  broader construction is separately credited; this contribution establishes
  an exact fixed-transfer/guard boundary at frame281, which PR980 leaves at
  13 ADDs. Its changes and claimed whole-word savings are not imported here.
- **eumemic, PR543/555**, **DreamingOfClouds, PR545/589/510**, **Dylan Crow**,
  **Zhihao Chen**, **DaysSky**, and retained supplier contributors: R439 word,
  frame geometry, original H1-H5 audit, exporter, stage/cohort checks, hosting
  and pricing foundations. The selected PR589 head remains
  `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
- **Ali Romman, PR688**, and Ross Richardson: the optional native harness is
  adapted from their credited replay wrapper. The underlying C++ checkers and
  all supplier files remain untouched. No new native execution is claimed.
- **Jonathan Capalbo, PR942**, with the U8/T21/T16 owner lineage credited in the
  selected maintainer review: current conditional-frontier context only.

`independent.py` was written separately from the discovery algorithm and
imports no discovery code. It uses first-gate column subtraction and a paired
column search, while discovery uses last-gate row subtraction and shortest-path
pruning. This is algorithmic independence inside an AI-assisted contribution,
not a claim of independent authorship from every predecessor or human review.

Source file SHA-256 pins and the exact base are in `SOURCES.json`. Original
source notices and licenses remain in their existing package locations. The
selected certificate, upstream sources and predecessor packages are unchanged.
