# T16 owner-packing improvement from an OR-Tools evacuation neighbourhood

This package records a **conditional packing gain**, not a new word, supplier,
mechanism, or multiplication theorem. On the same selected PR1094 T16 word and
both unchanged suppliers, a finite OR-Tools CP-SAT large-neighbourhood search
found an owner map with exact **κ = 0.001673618490895016**. The immediately
preceding map had κ = 0.001673614205725695, so the increase is
**4.285169321 × 10⁻⁹** (0.0002560428% relative). The map changes 163 rows of its
predecessor: 142 helper relocations and 21 offset-only edits.

The exact selected-word ceiling from `complex-local-word-ceiling/ceiling.py` is
`a_hi = 0.001690054109089`, giving `κ < a_hi/(1+a_hi) =
0.001687202645325402…`. This candidate realizes **99.194871%** of that κ
ceiling. The gain closes 6.589632% of the κ gap from the selected PR1094 map to
this ceiling. These are ceilings for the fixed word, template,
coverage law, and halving guard. They do not bound other words or changed
mechanisms.

The inherited exact packing certificate still proves at most 4,887 empty
capacity-48 bins and `Σ f ln(f) ≤ 908,139.013`; this candidate has 4,880 such
bins and `Σ f ln(f) = 907,279.723`. That surrogate certificate is not a κ
optimality proof. The CP-SAT run ended `FEASIBLE` with objective 10,463,952 and
solver bound 10,540,812. Exact κ and legality came from independent replay and
pricing, not from the solver objective. Later evacuation, relocation-cost,
single-call, and time-window neighbourhood rounds did not improve the exact κ.
The finite search does not establish an optimum.

## Verification

The verifier reconstructs the candidate from the predecessor's compressed
owner rows plus `DIFF-vs-predecessor.json`, regenerates `OWNERS`, `PLAN`, and
`SPEC` through the existing builder, then runs the unchanged strict T16 replay.
It also runs the independent seed67 owner audit, prices both suppliers with the
pinned engines and PR1069 sweep, calls the exact word-ceiling routine, and runs
the exact-integer packing-ceiling checker. The strict replay recomputes the
73-column chart count as 10,008.

From the repository root, run:

```sh
python3.12 scripts/research_package.py --package research/complex-t16-evacuation-increment --check-only
python3.12 scripts/research_package.py --package research/complex-t16-evacuation-increment
```

The search used OR-Tools 9.11.4210 with Python 3.10.12. Reproducing the search
itself requires the pinned research environment described in `SEARCH.json`;
the registered verifier deliberately replays and audits the candidate without
running an optimizer.

## Search overlap

The live overlap refresh on 2026-10-17 at 21:23 UTC returned 350 open PRs and
321 discussion records. It found no matching open T16 owner-packing PR. The
nearest scoped results are a census of single whole-helper relocations
(Discussion #1332 / closed PR #1343), which explicitly excluded multi-row
repacking, and a rank-48 idle-only repartition ceiling (Discussion #1265 /
closed PR #1276) below this candidate's κ. An idle-axis overlay (Discussion
#1339 / PR #1387) did not pass actual stream composition. These checks support
the stated scoped distinction, not a claim of global novelty. The returned
inventory and details are recorded in `evidence/OVERLAP.json` and `SEARCH.json`.

## Open next questions

The structured questions are in `TASK.json`. Three bounded probes of a rounded
exact-moment objective did not improve the candidate, so that
objective/neighbourhood combination is not the next search to repeat. A more
promising question is whether exact supplier prices can drive a decomposed
master problem with pricing cuts instead of a single rounded surrogate. This
candidate improved exact κ even though its `Σ f ln(f)` surrogate is higher than
its predecessor's, so the surrogate can mis-rank nearby maps. A proof-quality
bound on the remaining κ gap is also open.

## Credit

The predecessor packing, builder, exact checkers, strict replay, and proof
retain their original authorship and notices. This incremental map and search
record were prepared by OpenAI Codex at the user's direction with substantial
AI assistance. No independent human review is claimed. New package material is
Apache-2.0.
