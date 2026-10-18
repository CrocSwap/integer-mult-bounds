# NOTICE

`research/bit-profile-pair-audit/` is a research note and exact audit contributed under the
repository's Apache-2.0 license (see `LICENSE`).

## Predecessor work

* **PR #555 (eumemic)** — the punctured R439 bit word, its generator, checkers, pricing pipelines and
  package structure. The base word `research/e8-bit-p111/data/bitE8mut-p111.json.gz` is read unchanged.
* **PR #543 (eumemic)** — the R420 L3 skeleton (keepers read by targets, then rewritten in phase B)
  that #555 stacks on, and the interleaved scalar-interface lemma.
* **PR #545 (DreamingOfClouds)** — the punctured star unit (nine lines neither sources nor targets),
  the decoder constant 63 at v = 111, and the deficit identity `m W - rank_mass = T(2Kv - L cst)`.
* **PR #510** — the nine-stage pricing chain (#463 template, 32 replicas, #442 hosting).
* **PR #589 (DreamingOfClouds)** — the two A-section transports audited here, and the tuner
  (`tune/tune.py`, `tune/wlib.py`) whose move class this audit prices exactly.
* **PR #620 (GamingPuzzled) and PR #631 (vectorsss)** — the decoder-side bounds (`63/111` optimal for
  star label decoders under puncturing), which are orthogonal to the reframing class audited here.

`code/replay.py` and `code/bitprof.py` were written for this note and share no code with the pinned
dependencies; `code/stateprof.py` and `code/search.py` drive the pinned tuner's move enumeration and
price everything on the exact paid-profile objective.

## AI disclosure

Substantial AI assistance was used in preparing this contribution (DeepSeek Harness, deepseek-flash
model). Every claim in `verify.py` is a deterministic exact-arithmetic check against files pinned by
sha256 on the stated base commit, and the numbers in `README.md` are the values those checks assert.
