# Provenance and attribution

Alejandro Zarzuelo Urdiales is the author and human developer of this research
line. It began in an earlier Archivara exploration of parity-aware integer
multiplication. Alejandro subsequently developed it personally with multiple
AI tools, most recently GPT-6.1 as recorded by the author. This synthesis,
paper, Lean proofs, executable controls and submission preparation involved
substantial OpenAI Codex assistance.

The original exploration motivates congruence-preserving arithmetic. This
package independently proves its imported arithmetic; it does not inherit the
old draft's broader separation, carry-saving or benchmark assertions.

The exact h28,d19 scalar producer and copied-center/phase framework are
community work, retained verbatim in `references/pr46/`. This package's new
increment is the image-conditioned integer reference rewrite, complete image
guard integration, canonical arithmetic proofs/oracle, and actual-profile
precision accounting. The identity `QP=I` and mixed-center formula are already
present in the community construction and are not claimed as new discoveries.

Credit OpenAI's pinned multiplication manuscript; Douglas Colkitt/CrocSwap's
framework; icekylinx's mixed-center/fixed-basis and copied-center producers;
Zhihao Chen/jacklightChen's semantic precision, translated endpoints and
two-stage work; RaD/hipotures's semantic and changed-DAG contributions; Aurel
Prosz/Paureel's copied-stream and two-stage interfaces; James Chang/jamesyc's
reversed geometry; Dominik Scholz's fixed-basis and profile work; Rohan Arun's
corner, reversed/fixed and weighted matching work; Chafik Boukhalfa/chafreaky's
exact data recovery; Swapnil Jain's separate research and formal arithmetic;
eumemic, dleen, Bortlesboat, princezuda, and all predecessor authors and
assistance notices retained in the upstream `NOTICE`. See the complete pinned
community ledger for the individual branches and techniques.

Gaussian denominator exponents and parity reduction are established prior work
in Amy, Glaudell and Ross, Quantum 4,252 (2020), section5.4,
https://doi.org/10.22331/q-2020-04-06-252. No priority claim is made for those
arithmetic principles or the inherited network identities.

Primary community source: PR46, head
`71b6c960c89295e952522dd44111df9cfc51ae90`, which pins PR44's weighted
matching at `061414a529f1123668872db44d737e362fbe066f` and retains the
community chain documented in `LEDGER.md`. PR45's earlier Lean arithmetic is
imported unchanged from `5e219f7b3513b092d3ee919a303db0f55a3a0a0e`.
The OpenAI manuscript commit is
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`.

New material is Apache-2.0, following the destination repository. Vendored
material keeps its original `LICENSE`, `NOTICE`, author and AI disclosures.
The full multiplication theorem and physical/analytic interfaces remain
separate proof obligations. No community acceptance or new kappa is claimed.
