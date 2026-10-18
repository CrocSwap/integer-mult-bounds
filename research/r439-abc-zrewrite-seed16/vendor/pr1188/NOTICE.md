# Attribution and license

New GL5 application, distance checker, bounded interval certificate and package:
**Gareth Davidson (@bitplane)** with substantial **OpenAI Codex assistance** in
mathematics, implementation, checks and writing. Apache-2.0. No subagents or
independent human review were used.

- **Ross Richardson, PR936**, supplies the previous five-wire window method,
  with PR904 and **Jeffrey Cox, PR754**, among its small-circuit predecessors.
- **Davidson PR1122**, on PR980/952/904, is the complete frozen input. Its exact
  candidate, proof, certificate, README, notice and license are preserved under
  `vendor/pr1122/`. Literal replay, strict I/O and native harness code adapt
  PR1122/980 with their attribution retained.
- **Sagar Thakrar, PR1062**, supplies the inherited B/star-D composition;
  **Aaron Wang, PR1015**, **Ross Richardson, PR923**, **Sricharan Vagvala,
  PR967**, and **Davidson PR915/926** retain credit. The unchanged parent notice
  records earlier helper-star and interface contributors in detail.
- The selected bit supplier is **DreamingOfClouds PR589**, on **eumemic
  PR555/543**. Original checker and Apache-2.0/AI notices remain unchanged.
- The native exporter/checker lineage credits **Dylan Crow**, **DaysSky**,
  **Zhihao Chen**, **Sagar Thakrar**, and PR249/266/315/496/527 contributors.
  Pinned native notices retain full attribution. Gzip payload comparison follows
  the repository guidance credited to **Maxime Fleury** and **Antoine Olivier**.
- Optimal CNOT synthesis by GL(n,2) Cayley-graph search predates this work.
  See **Jens Emil Christensen, Søren Fuglede Jørgensen, Andreas Pavlogiannis and
  Jaco van de Pol**, *On Exact Sizes of Minimal CNOT Circuits*, RC2025,
  https://cs.au.dk/~pavlogiannis/publications/papers/rc25.pdf and their CNOTter
  repository. The two C++ programs here are fresh implementations; no external
  source code or data is copied, and no algorithmic priority is claimed.

The selected context is **Rohan Arun PR1094** and its credited complex/owner
chain. It is not changed by this contribution. PR1127's commuting Steinberg
rewrites and the local guard work in PR936 remain distinct mechanisms.
