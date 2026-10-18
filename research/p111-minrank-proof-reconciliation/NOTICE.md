# Attribution and licenses

Prepared for **bitplane**, with substantial **OpenAI Codex assistance** in
reasoning, implementation, verification and writing. No delegated agent was
used. New files are Apache-2.0 under the copied repository LICENSE. No
independent human review or formal verification of the full multiplication
theorem is claimed.

- **Joel Pulikkan / GamingPuzzled, PR620** reported the archived P111 minimum
  rank and uniqueness answers, wrote the SAT encodings and research reports,
  and disclosed Claude Opus 5.5 assistance. These findings are credited to
  that contribution. Its original source methods and notices are retained.
- **DreamingOfClouds, PR595**, with the geometry and decoder lineage credited
  in PR620, supplies the Hamming E8 enumeration, F2 labels and fitting model.
  Retained PR620 notices also credit jeremykothe2, chafreaky, eumemic and
  the PR446 contributors. This package changes no supplier attribution.
- **Russell Seligmann (@rseligm2), PR757**, and **Cody Harris (@VibeCodyH),
  PR761** supplied the distinct solver-free copied-rank floor and identified
  the archival/supplier root-order mismatch. Their conclusions and correction
  have priority here. No source from either cost proof is consumed.
- **PySAT**, by Alexey Ignatiev, António Morgado, João Marques-Silva and
  contributors, supplies the optional CaDiCaL Python interface. **CaDiCaL**,
  by Armin Biere and contributors, produced the fresh unsatisfiability traces.
  The independent cold checker does not import either tool.
- **Marijn Heule and Nathan Wetzler**, and the retained DRAT-trim contributors,
  supply the proof converter and native checker. Their exact source files
  are retained under their **MIT license**, including individual copyright
  notices and `vendor/drat-trim/LICENSE`; they are not relicensed as new
  Apache-2.0 code. Commit and Git blob pins appear in SOURCES.json.
- The LRAT format and efficient checking work are credited to **Luís
  Cruz-Filipe, Marijn Heule, Warren Hunt, Matt Kaufmann and Peter
  Schneider-Kamp**. The new Python checker implements only the RUP subset
  needed by these two certificates.
- The selected PR942 result remains credited to **Jonathan Capalbo** and
  the supplier/owner lineage retained by its maintainer review.

The archived README is preserved from base commit
`2921874911956718fcaaaf9396fe8267b3cfa9f0`. The five consumed `s2-decoder`
files also match PR620 head `8f0150e0d0a8a02370907be35cccd3ca69cdd941`
byte for byte. That head's README contains later additions and a separate
ADE erratum; those later claims are outside this package. Original relative
links refer to the original directory layout. The new scope is retained
proof evidence, exact model/source binding and independent checking.
