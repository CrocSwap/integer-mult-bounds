# Volume III self-review

Status: complete informal draft, independently proof-read by root; minor boundary clarifications incorporated. No Lean edit, compilation, model request, Jev request, service change or live-DAG mutation was performed.

- Exactly C001–C100 occur once and in order:90 entries have a full English proof;10 are explicitly labelled conjectures, each with evidence, a proved special case and a proposed use/approach.
- The ten targets are C010,C020,C030,C040,C050,C060,C070,C080,C090,C100. None is used as a proved dependency. Text checks reject their IDs inside the90 proof bodies.
- The ten sections cover submodularity, matroids, matching, flows, trees, extremal graphs, set families, polynomial grids, designs/Fourier tools and additive combinatorics. Claims are distinct certificates, constructions or existence results, not parameter renamings.
- Forward dependencies C018→C022, C019→C041 and C038→C041 are acyclic: the later arguments are independent elementary proofs. C019 also supplies the forest-count argument it needs directly.
- Audited delicate steps: symmetric exchange uses closure idempotence; lower-bounded circulation has the correct incoming-lower/outgoing-upper cut sign; EKR circle pairs are disjoint; coefficient interpolation permits individual degrees exceeding the target because another exponent must then be smaller; Chevalley–Warning includes the exponent-zero power sum; Petridis deletes old translate contributions; Bogolyubov uses normalized convolution and counts four-term support.
- Root's boundary corrections incorporated: C034 deletes arcs into s/out of t before path decomposition; C038 distinguishes a zero-distance quotient; C055 states n≥1 for the radical bound; C056 states N>0; C057 states positive r,s.
- Freshness exclusions: the unrestricted real sum-product conjecture has a2026 counterexample; ordinary cycle-double-cover has2026 proof announcements; the Chvatal downset theorem has September2026 proofs. None is presented as a currently open target. C040 is the stronger bounded-five-even-subgraph assertion, and C070 is the new explicit inertia-matrix conjecture from §4 of Ellis–Filmus–Friedgut.
- Frankl/Rota/Ryser/graceful/Tuza/Alon–Tarsi/Hadamard/Erdos–Turan status evidence comes from primary papers and current targeted retrieval. Partial, approximate and integer-versus-natural-number variants are distinguished. This is not an exhaustive current-preprint census or an independent validation of recent major proof announcements.
- All proved entries are classical mathematics with attribution hooks and our supplied derivations. No mathematical novelty is asserted. No unsupported sourceGoal or conditional project declaration is used as an established theorem.
- Eleven exact local files are SHA-256 bound with declaration/near-proof excerpts in03-sources.json;23 primary web sources are attributed. DAG discovery used bounded indexed FTS queries in the authoritative registered catalog. Rows marked source-catalog with axioms=null are source-only evidence, not kernel or axiom audits; zero search hits are not absence proofs.
- All owned writes used exclusive per-target locks and preimage SHA guards where files existed. Handles were closed before lock deletion. Final draft uses LF only; no repeated CR translation remains.

Limitations: English mathematical review does not supply a formal kernel certificate. Entry proofs use elementary background algebra, probability and linear algebra explicitly where needed. A conjecture's special case is not a proof of its general statement. Publication should retain these distinctions and the primary-source credits.

Draft SHA-256: b313fc596333de77cfa6caa05b402db646ca8849967d65861630a2f7cae625cd
Ledger SHA-256: ab282920968de07215e32ff60ab0cd54064bfe47fec10945019f0dd432113fcf
Word count: 12354

Cross-volume duplicate review: replaced C081–83 design identities/Fisher/finite-plane constructions, overlapping B011/B013/B001–02, with Möbius inversion, Cauchy–Frobenius orbit counting and the full weighted Pólya cycle-index formula. Counts remain90 proofs+10 conjectures; the replacement proof chain is C082→C083 only. Root independently reviews the three new entries.
