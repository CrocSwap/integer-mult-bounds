# Executed validation and scope

The first complete native/hosted run passed on 2026-10-16 UTC. Its fresh
certificate is committed as `CERTIFICATE.json`. Two complete runs were compared, followed by a final clean-output run after
normalizing timing-dependent hash links; final status is recorded below.
No recorded predecessor PASS is substituted for fresh native execution.

Environment used:

- Linux x86_64, glibc 2.39; CPython 3.12.14.
- GCC C++ 13.3.0, `-O2 -std=c++17`, with the exact macro/include flags in
  pinned PR1043 `pipeline.py`.
- Boost 1.83 headers; `boost/version.hpp` SHA256
  `a547ee7eddf1b96695027922345b471feba8bcba79a8572399d282247c02e4ab`.
  Headers were extracted locally from Debian's
  `libboost1.83-dev_1.83.0-4.2~bpo12+1_amd64.deb`; no compiler source was changed.
- NumPy 2.3.5, SciPy 1.17.0, SymPy 1.14.0, mpmath 1.3.0, in a virtual
  environment. The exact requirements are recorded beside this file.

Executed commands (paths abbreviated only for the local output directories):

```sh
BOOST_INCLUDE=/tmp/s2-boost/usr/include /tmp/s2-venv/bin/python -B \
  research/r438-native-rehost/verify.py --output /tmp/s2-native-second \
  --write-certificate /tmp/s2-native-certificate.json
BOOST_INCLUDE=/tmp/s2-boost/usr/include /tmp/s2-venv/bin/python -B \
  research/r438-native-rehost/verify.py --output /tmp/s2-native-publish
python3 -B scripts/research_package.py --package research/r438-native-rehost --check-only
python3 -B scripts/research_package.py --package research/r438-native-rehost
python3 -O -B research/r438-native-rehost/verify.py --local-only
```

The optimized command must exit nonzero with `Inherited checkers require
assertions: do not use -O`. It did. The registered command passed and explicitly
reported `native_not_run`; only the complete commands execute native and hosted stages. The catalogue's first working example,
`research/r439-bsection-stars-seed01/verify.py`, was also run and passed during
orientation; it is not evidence for this different candidate.

Fresh complete evidence includes:

- Both source words, every dirty local column, and every original H1–H5 flag.
- Six freshly compiled scalar checkers (three stage counts for each word),
  native legality and exact positive Gram checks; 96 rejected omitted bridges.
- Both parent constructions and all 34 parent mutations; both hosted
  constructions and all 32 hosted mutations.
- Both exact endpoint engines, with the full inherited surcharge, precision,
  child-size and row checks. The historical cited PR548 outer calculation
  executes but is excluded from this package's current-frontier claims.
- PR2653's entire exact geometric receipt and its ten controls/witnesses;
  all 126,144 actual emitted owner/projector matches and every remainder.
- Nine new semantic rejection controls, including equal-width owner errors and
  an understated rank-34 remainder. See the certificate for exact messages.

During adapter development, the first partial run stopped because the new
adapter compared zero-rank remainders against a predecessor table that records
only positive ranks. The comparison was corrected to use the declared
positive-rank convention. A pre-native comparison also exposed JSON integer
versus string histogram-key ordering; normalization now precedes sorting.
These were adapter implementation failures, not counterexamples to the word
or weakened inherited checks. The final emitted remainder check still retains
all per-child histograms, including zero entries where present.

The first clean certificate comparison then caught a real reproducibility
issue: `GEOMETRY.json` contains elapsed seconds, and its raw digest is included
in both templates. The two complete runs agreed on every mathematical value
and every emitted instruction/owner digest. The final adapter authenticates
each run's original raw geometry/template links, removes only geometry
elapsed time, and records explicit `semantic_*` digests for comparisons.
Re-summarizing both complete output directories produced identical normalized
certificates. The final clean-output command exercises this corrected path
from compilation through complete certificate comparison.

Before the clean comparison run, canonical main advanced from research base
`389fa10d714f5b40afe624908e487eb5e424498d` to publication base
`318ba71b8927f81141f41a89c1af74323586f253`. The isolated branch was updated.
All 188 live source files, the task guidance, catalogue and selected record
were unchanged. The three predecessor ledger scopes were checked again.
No `upstream/`, selected certificate, frozen input or shared checker is edited.

This is local execution evidence. Hosted CI, a full selected-frontier cold
replay, the full repository suite, Lean and independent human review are not
claimed. Publication commit/tree identity is recorded in the PR handoff; it
is not embedded in this file, which would make the commit self-referential.

Final stable replay: **PASS**, 2026-10-16T14:36Z. After replacing the large
generated geometry copy by its full semantic digest, the publication replay
repeats the complete command and certificate comparison; see final status below.

Final verifier source SHA256:
`f80d03a25d3742822cc8da8435b3b0fe51dd63f53ea744a8e781294eae06cd27`.
Normalized certificate SHA256:
`6da8c593257c8440f0fe35488d941715d953d715e2e464ffdfffff7ed31eee9c`.

Publication refresh: canonical main advanced again to
`0614abaef427f123d9b844f85a759e64ee3ab29c`. All 188 live inputs and the
entry guidance/selected record remained byte-identical. The branch was
advanced to that parent after the native run; package/source-pin checks and
committed-byte preflight were repeated on the publication tree.

The compact publication certificate binds the full generated geometry by its
semantic digest and records its dimensions/control counts. It does not
vendor the 5.8 MB regenerated geometry a second time. All original integrity
checks and complete mathematical coverage remain in the reproduction command.

Publication replay: **PASS**, 2026-10-16T14:44Z, on the compact final
verifier/certificate. All native/hosted stages and the complete normalized
certificate comparison passed in a fresh output directory.
