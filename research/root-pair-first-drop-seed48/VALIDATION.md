# Executed validation

Executed on 2026-10-13, Windows with CPython 3.14, at base
`2921874911956718fcaaaf9396fe8267b3cfa9f0`.

| Command from repository root | Result |
| --- | --- |
| `python research/root-pair-first-drop-seed48/verify.py` | PASS; 26 threshold, 126 candidate masks, 6,720 ordered-pair orbit, cost-six witness, total completion cost 69 on 94 ports |
| `python -O research/root-pair-first-drop-seed48/verify.py` | Same PASS; acceptance checks do not depend on Python assertions |
| `python -I -O -B research/root-pair-first-drop-seed48/verify.py` | Same PASS under isolated, optimized, no-bytecode execution |
| `python research/root-pair-first-drop-seed48/check_sources.py` | PASS; all 14,400 entries agree with PR968, three pin/certificate controls rejected |
| `python -B scripts/verify_selected_result.py` | PASS selected record, exact kappa, original source inventory and proof supplement: `1661960547713947/1000000000000000000` |
| `make verify` | Unavailable: Windows reports that `make` is not recognized |
| `git diff --cached --check` | PASS for all twelve new package files |

The primary check includes five focused rejection controls: underclaiming
rank six at 25 punctures, omitting a candidate from the coverage count,
using an orthogonal pair outside the completion class, dropping the dual
scale factor in the rational decoder, and omitting the unit label in the
pairing. It also recomputes all 26 one-line restorations of the witness,
each of which raises the term cost to at least seven. The printed
`controls=6` groups these five rejections and the restoration check; it
does not mean six rejected mutations.

The separate source test checks rejection of a deleted required source
pin, a changed source digest and a modified certificate puncture. The
required source-name set is fixed in code; deleting a pin cannot disable
source verification. The primary checker never imports predecessor code.
Its two rank routines share the independently constructed exact model;
the separate source crosscheck is a compatibility check, not a wholly
independent proof of PR968.

The finite enumeration is complete for the class in PROOF.md. Witness
discovery only extends the 25-puncture candidate masks by one line until
it finds an attainment; it does not classify all 26-puncture masks or
optimize the other seven decoder terms. No floating point or random
sampling is used in the proof or accounting.

No full repository suite, native circuit replay, precision/tape admission,
all-size multiplication theorem or hosted CI is claimed. The completion
costs more per live port than the cited existing decoder. The selected
pointer, upstream sources and predecessor packages are unchanged. Root
coordination independently replayed both new checkers and reviewed the
written proof with no blocking findings.
