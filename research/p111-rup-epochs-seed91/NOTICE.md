# Attribution and scope

Prepared by **Philipp (@mightyOil)** with substantial **OpenAI Codex assistance**
in implementation, reasoning, measurement and writing. A scoped Codex subagent
wrote the independent finite semantic oracle and reviewed the epoch semantics;
a second reviewed packaging. These are AI-assisted checks, not independent human
peer review. New files are Apache-2.0 under the repository LICENSE.

`candidate.py` adapts the ordered checker in **Gareth Davidson (@bitplane),
PR1097**, reviewed head `ad0cc538d7f827461da6364c3c0e09176b10bcae`.
That contribution supplies the proof traces, formula regeneration, positive
calibration, original-encoder comparison, parser, controls and full receipt.
The frozen package and its notices remain unchanged.

The archived minimum-rank and uniqueness findings are credited to **Joel
Pulikkan (@GamingPuzzled), PR620**, with the **DreamingOfClouds / PR595** geometry
lineage. **Russell Seligmann / PR757** and **Cody Harris / PR761** established the
distinct copied-rank results and root-order caveat. PR1097 retains the full
PySAT, CaDiCaL, DRAT-trim and LRAT research attribution and source-specific MIT
notices; this package neither copies nor relicenses their source.

Related verifier engineering in PR1059, PR1092, PR1099, PR1137, PR1144 and PR1151
targets different workloads. No combined performance claim is made. The selected
construction remains credited to the authors in the repository's selected
record and review; this contribution supplies no new multiplication exponent.
