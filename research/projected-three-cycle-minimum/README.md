# A projected helper three-cycle costs exactly thirteen XORs

For every finite `k >= 3`, a raw-identity word on `k` arbitrary dirty helpers
and one arbitrary dirty target needs exactly **13 unit scalar XORs** to induce
the projected cycle `z0 <- z1 <- z2 <- z0`, fixing every other register.
Projection deletes target-destination gates and replays the remaining word
chronologically; it is not a block of the raw matrix. Every ordered XOR between
distinct existing registers is allowed, and all restoration costs are counted.

[proof.md](proof.md) gives a thirteen-gate attaining word and a
**computer-assisted lower bound**. Its written rank/write-count argument
restricts a hypothetical word of length at most twelve to at most four written
helpers and one target. Coefficient restriction removes reads from unwritten
registers. A complete five-register calculation then excludes that case.
The dimension-independent argument is written mathematics, not a formal proof
checked by the program.

This is a scalar helper-contract prerequisite. It adds no paid-frame or hosting
admission, selected supplier, recursive moment improvement or new `kappa`.
The original complex-masked-decoder assignment, explicit change to the
bit-helper-contract scope and coordination links are in [TASK.json](TASK.json).
The selected frontier and predecessor packages are unchanged.

## Exact finite evidence

The self-contained [verify.py](verify.py) constructs the complete radius-six
ball of paired raw/projected states in two representations. Each engine expands
all 20 generators at every state of distance at most five, without symmetry or
endpoint pruning. Both have layers
`1, 20, 260, 2670, 22988, 174676, 1221368`: **1,421,983 states** and
**4,012,300 expanded directed edges** per engine. Every first-engine state is
converted and checked for exact membership in the second ball. Both
right-translated intersections are empty.

This is an exhaustive bounded-radius calculation, not a full paired-group
census. The two implementations were authored in the same Pro session; their
different representations provide a cross-check, not independent human review.
[certificate.json](certificate.json) is a compact receipt compared only after
full recomputation. No stored search frontier or opaque state dump is needed.

The verifier also checks the witness on all 16 dirty Boolean inputs, three
credited predecessor positive fixtures, embeddings on every basis input in
dimensions 4, 5, 6, 18 and 65, and controls for confusing raw and projected
maps, assuming a clean target, omitting target restoration, reversing the cycle
and accepting illegal gates. Essential checks use exceptions and survive `-O`.

## Reproduce

From the repository root, with standard-library Python 3.12 and roughly
**321 MiB observed peak resident memory**:

```sh
python3.12 -B scripts/research_package.py --package research/projected-three-cycle-minimum --check-only
python3.12 -B scripts/research_package.py --package research/projected-three-cycle-minimum
```

The registered hook runs the optimized verifier with a 120-second bound and
retains `-I -B`. No external files or dependencies are required. Direct commands:

```sh
python3.12 -I -B research/projected-three-cycle-minimum/verify.py
python3.12 -I -O -B research/projected-three-cycle-minimum/verify.py
```

Local CPython 3.12.14 replay on macOS 26.5.1 arm64 passed in 5.596 seconds
normally and 5.721 seconds with optimization. Peak resident memory was
337,051,648 and 332,972,032 bytes respectively. Both stdout files byte-matched
the supplied certificate. A separate optimized process changed the final gate
from `(0,1)` to `(0,2)` in memory, preserving a legal thirteen-gate word; the
endpoint guard rejected it with `thirteen-gate witness is incorrect`.
[REPLAY.json](REPLAY.json) records exact argument tails, outputs, source hashes
and the mutation command. Timings are observations, not resource guarantees.

A separate GPT-6 Pro mathematical review corroborated the universal reduction
and search interpretation, conditional on the finite nonintersection. That
review did not receive the search source or reproduce its state census. It
identified an overstatement in an identity-only translation test: identity
cannot distinguish left from right multiplication. The final checker corrects
that comment and adds the review's explicit noncommuting fixture in both packed
representations, checking `T_01 C != C T_01`. The complete registered optimized
replay passed after this addition, with the same certificate and state hash.

The complete verifier was audited before execution: standard library only,
no network, installations or subprocesses. Default execution writes nothing;
optional `--receipt PATH` writes a fresh receipt after all checks. Downloaded
sources and isolated copies remained unchanged. Local execution corroborates
the supplied program; it does not independently formalize the all-dimension
reduction, replay the selected supplier or establish external CI acceptance.

## Provenance and credit

Prepared by **Andrey Mas**, with substantial **GPT-6 Pro assistance through
ChatGPT** for mathematical research and checker authorship. Codex coordinated
the work, audited execution implications, mechanically packaged the result and
separately replayed the checker. No independent human review is claimed.

Gareth Davidson / **@bitplane**, [PR1420](https://github.com/CrocSwap/integer-mult-bounds/pull/1420)
at `d19a944897714f2ecae72720b7dafc3e256f2f8d`, supplies the prior joint-range
theorem, elementary loops, write-count observation, small paired-state censuses
and seven-gate SWAP witness. Those are credited inputs, not new results here.
**@woklerx**, [PR1105](https://github.com/CrocSwap/integer-mult-bounds/pull/1105)
at `20a960b545f4b0ade4f26922ef686bd5eaf275f4`, is earlier raw-feedback lineage.
The predecessor's remaining lineage credits are retained by reference to its
pinned README.

The [separate all-helper SWAP finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/1476#discussioncomment-18913057)
by Andrey Mas with GPT-6 Pro assistance concerns a different projected endpoint;
this lower bound does not depend on its lower bound. The present result follows
the [general-defect handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1396)
and [scoped three-cycle claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1503).

[SOURCES.json](SOURCES.json) pins historical main catalogue/selected-record
provenance at the original selector base `410026dc...`; claim-time main was
`ef5f3940...`. Its separate informational PR1420 file pins were byte-checked
against the fetched exact Git commit. They are not runtime inputs and are not
validated by the generic source-pin hook. No predecessor package is vendored.
The original local receipts refer to the preserved downloaded verifier; their
separate final-revision entry records the added translation controls and replay.
The proof's runtime and attribution paragraphs were updated for this package.
The verifier's model self-report was normalized to the observed GPT-6 Pro label.

New work is Apache-2.0; see [LICENSE](LICENSE).

## Open next questions

Can the target-write rank bound in proof section 2 be formalized for arbitrary
finite register sets and raw-identity words? It is the dimension-independent
step used here and may support future projected-defect bounds. A first step is
to formalize both prefix matrices over `F2`, prove that each difference row lies
in the span of donor rows at deleted target writes, then invoke exact target
restoration. No proof-assistant definitions are supplied, and the rank bound
alone does not determine another defect's optimum. Structured details are in
[TASK.json](TASK.json).
