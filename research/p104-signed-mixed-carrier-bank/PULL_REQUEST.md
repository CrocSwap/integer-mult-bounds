# Research construction: signed pair mixtures for P104 (schematic frame model, no new κ)

**Classification: finite research construction, not a supplier or bound improvement.**

This package investigates a specific escape from PR #1125's *fixed-term* carrier restriction: redundant, reversible-in-sign **mixed scalar values** `x_i ± x_j` on new pair-label lines `span(u_i+u_j)` (not a reversible full native circuit). Every target picks disjoint pair sums independently of the others. The source values are unchanged and restored to their home frames after mixer construction and reads. **New auxiliaries are not restored/erased at the end**; this is a key open cost obligation.

- Verified target frame inclusion for **one genuine signed E8 decoder** and every required pair/target relation in it. General 7168-decoder support uniformity is inherited from merged PR #1125.
- Exact per-gate symbolic integer trace, F₂ subspace inclusion and all charged frame transitions in the explicitly relaxed model.
- Exhaustive **2,288 target/sign configurations**, all **105** perfect matchings and all **4,096** cube-edge mixture banks.
- Two independent optimization algorithms: edge-conflict DP and vertex recursion. Unique minimum frame-rank bank uses all 12 cube edges, adding 24 auxiliaries (2 signed variants per edge).
- Against a **specified, non-optimal** unmixed home-return schedule, modeled ADDs decrease 416 to 288; frame-rank moves decrease 2,224 to 1,312. These are finite schematic counts, **not** a κ/runtime gain.
- Separate restricted exact obstruction: fixed *nonredundant* eight-channel global recoding over Q with home-line-only reads cannot use 247 non-coordinate line labels for the unsigned support family (F₃ full-rank minor witnesses and independent rational verification).

Validation of the committed subset: `python -I -B research/p104-signed-mixed-carrier-bank/RUN_SUBMITTED.py`; standard library only. The larger local laboratory also ran optional independent scripts, but those are not included in this PR. The added `root_line_gate.py` confirms no mixed two-root label is an ordinary E8 root line.

Open gates: physical lowering of composite label lines, actual signed decoder word, new helper ownership/cleanup, paid source access, recursive child ranks, phase frames, full optimized unmixed comparator, full strict moment/outer recheck. This branch changes **no upstream/** file, no selected source and no κ. Upstream PR #1125 and #968 receive credit; PR #2820 supplies parallel projection context. Substantial GPT-6 assistance disclosed. Apache-2.0.