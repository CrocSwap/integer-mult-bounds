# Zero-circuit clearing relations above the PR71/73 frontier

New conditional `kappa=257077122735047/5000000000000000000=5.14154245470094e-5`, above PR71's `5.1414646104039e-5`
by `0.0015140490%`. Pinned construction: PR71 at
`1bef94fd40a746452548c84a4a8f8834670a3113`.

We extend our profile-aware clearing method to pending live controls. A zero
fresh-signal provider circuit can be toggled into a clearing expression for
the same retired target, excluding the target itself. The alternative relation
preserves fresh clearing and is synthesized through charged literal XORs;
pending providers retain current-frame <= clearing-frame <= next-use-frame.
Bounded search prices alternatives by complete nonlinear transition-profile
cost, rather than first-order entropy alone. This changes actual words/profiles.

Fresh complete input/target/dirty bases in both orientations, independent frame
reconstruction, exact fixed-I+J profiles/CRT, the Taylor8 characteristic enclosure,
all47 strict assembly inequalities and seven margins pass. The complete old71
profile is rejected at the new bit saving. The37-theorem standalone Lean packet
includes4 new circuit-toggle proofs and11 concrete arithmetic endpoints, plus22
reused dirty-word/rational helpers. Standard axioms only; no omitted proofs.

## Reproduce

Use an external checkout of the exact upstream71 commit above. Compile its
`scripts/experiments/binary_frame_profiles.cpp` with C++17 and include directory
`references/frame-compiler/pr48/scripts/partial_swap`, then run:

```
python verification/verify_words.py --upstream UPSTREAM --profiler PROFILER --word23 words/word-23.json.gz --word25 words/word-25.json.gz --output work/recheck
cd math
lake build CurrentRecordMath
```

Source/adapter byte hashes are checked before import; assertion-disabled Python
is rejected. The supplied words are authoritative replay inputs. Discovery source
snapshots show the new heuristic and contain original workspace paths; those
paths are not needed for the accepted-word replay with explicit UPSTREAM.

The PR71 scalar graph and data geometry/recovery are unchanged and inherited.
All-size analytic enclosures, frame/compiler transfer, routing, prime selection,
finite-alphabet tape layout and eventual setup remain conditional. Full upstream
repository verification was pending at PR71's draft announcement; no fresh whole
repository run or practical speedup is asserted here. This is a new finite
word/profile certificate, not a full formalization of multiplication or an optimum.

Alejandro Zarzuelo Urdiales is the human author/developer; earlier Archivara and
personal matrix/parity work and substantial OpenAI Codex assistance retain their
provenance. This extends our PR70 profile-aware tools. Credit Chafik Boukhalfa's
PR71 anchored split/next-use composition, Dominik Scholz's live controls, Rohan
Arun's profile-cost work, Rohan Garg's split operation, eumemic's compiler and
Avi Eisenberg's interval/core-aware graph; all inherited notices remain.
The paper is provided as LaTeX source; no new compiled PDF is claimed.
