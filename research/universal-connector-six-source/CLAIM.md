# Task card (local; no public discussion claim posted)

- Task ID / scope key: `connector-alphabet-change` card, track `recursive-interfaces`
  (helper seed `3e75b34c2e4efaf833ba00d8c0753b86`, scope key `ff4f5113ed2256ab19ed`).
  Refined scope: PR943's *unchanged* alphabet, next source count. The changed
  premise is the source count, n=6. No new operation is added.
- Base commit: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`; predecessor PR943
  (merged, `research/universal-connector-boundary`, blobs pinned in SOURCES.json).
- Object and question: minimum length `f(6)` of a restored source word whose
  paired-readout differences `D(w)` cover `F2^6`; exact unit-cost optimum of the
  all-63-row batch; general-n bounds.
- Method and domain: two independent exhaustive censuses at lengths 12 and 14
  (all even multiplicity patterns); explicit Gray-cycle construction; parity
  counting bound; dense F2 replay with mutation controls. n=7 was explored only
  heuristically (annealing, lengths 18/20/22), and is reported as bounds.
- Overlap check (2026-10-13 ~19:45 UTC): searched all PR titles and bodies for
  universal-path, six-source, D(w) and PR943 follow-ups, plus `research/`
  directories. Open #1083 formalizes PR943's 945 five-source pairings in Lean.
  #938 and #1103 count fanout or rectangular words. #934, #944 and #1088 cover
  the 3x3 cases. None treats six sources or general-n universal paths.
  Discussions #1163, #1166 and #1167 were read; there was no related claim.
- Optimistic budget / required observable: none for kappa. This is an
  interface-boundary result. Success means an exact `f(6)` with independent
  confirmation; falsification would be a full-coverage word of length <= 14.
- Cap: one session. Final quarter reserved for verification and packaging.
- Predecessor authors: Ross Richardson (PR943, PR934), with the lineage credited
  in references/PR943-NOTICE.md.
- Artifact / reproduction: `python3 -I -B research/universal-connector-six-source/verify.py`.
