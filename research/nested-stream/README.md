# Nested corners on the smaller h30 producer

**Conditional κ = 1248342/10^12 = 1.248342e-6 > 2^-20.**
This is 15.9439% above PR #15's 1.076678e-6, 27.3948% above PR #16's
9.799e-7, and 37.4841% above PR #14's 9.0799e-7. These are comparisons
of exponent savings, not practical running times or global optimality.

The contribution is a compatible composition: use eumemic's smaller
13,056,812-role h30 producer (PR #15), our two data-corner profiles
(PR #14, also independently in PR #16), and Zhihao Chen's nested
controlled basis (PR #16). The nested basis turns the remaining thirty
auxiliary-exit pivots into one contiguous block. PR #15 preserves exactly
the endpoint labels required by these profiles. Its internal wire reuse
and the endpoint batching affect different parts of the construction.

The rank deficit does not change. We replace singleton calls with six
classes of contiguous recursive blocks, and decrease the role count only
through the already audited PR #15 producer. In particular, the old
auxiliary entrance block is zero after source relocation and is not
counted again. [The written argument](proof.tex) spells out the shared
basis, endpoint, multiplicity, and mixed-width interface compatibility.

- Bit saving: 2496689/10^12; exact moment gap greater than 19/10^15.
- Complex saving: conservatively 4/10^6; h28, all nonzero residuals,
  guard C1 = 3749/2500. The recomputed PR #15 complex moment is stronger.
- Epsilon: 249999687889/500000000000; beta = 1/1000; delta = 10^-10.
- All 29 constraints and seven final margins are strictly satisfied.
- Final absorption gap: 2353529497917111/2500000000000000000000000000.

## Review and reproduction

Python 3.11 or newer and a C++17 compiler are required. Run from the
repository root, using a writable build directory with several GB free:

```sh
# Full scalar producer rebuild: exact support, frame, allocation and matching audits.
python3 scripts/source_frame_stream_network.py --workdir build/nested-stream-producer
# Validate the saved, freshly reproduced producer and recompute both moments,
# assembly, 32 nested-basis profiles, and negative controls.
python3 research/nested-stream/verify.py --full
python3 -m unittest discover -s tests -p test_nested_stream.py -v
python3 research/nested-stream/make_patch.py
make verify
```

The fresh full producer rebuild reproduced the published PR #15 certificate
exactly as a JSON value. Its producer record is [producer.json](producer.json),
with source and artifact hashes. `verify.py` validates its source hashes;
it does not silently call a saved certificate a new producer rebuild.
A fresh rebuild writes `certificates/source-frame-stream-witness.json`;
compare its `producer` object with `producer.json` before reusing results.

The complete [patch](../../patches/nested-stream.patch) applies to the pinned
original `upstream/`. It retains earlier interfaces, appends the h30
composition, and rewires the active layer, transform and assembly consumers.
The [compiled manuscript](../../artifacts/nested-stream.pdf) includes the
written basis and transfer arguments inherited from PR #16.
`make_patch.py` validates unique labels, internal references and patch
applicability. For Tectonic, conditionally guard the three pdfTeX metadata
primitives in the disposable materialization before compiling `build/main.tex`.

The general rational finite-family basis argument is not proved by the
finite-field examples. The compiler, mixed-width tape transfer, precision
and original multiplication arguments remain mathematical dependencies
requiring independent review. This is a conditional research result,
not formal verification and not a claim of unrestricted optimality.

## Attribution and pinned dependencies

- eumemic: PR #15 smaller producer/all-complex batching at
  `a17cab396ce1c79c288bde9d06002cefdc0af8e6`, the base of this branch;
  PR #13 source frames at `3ef246fa4f69c87ebfed78376418afa9ffcad145`.
- Zhihao Chen (jacklightChen): PR #16 nested basis at
  `a80f5e676c84b59def9791495df0655efe89a04f`, and prior five-subset work.
  Unmodified imported files and hashes are in `references/pr16/`.
- Rohan Arun: PR #14 data corners at
  `1fa5b9a9aaccbebb3eb29ac7ea55811f46464eee`; prior dimension/matching work.
- icekylinx: PR #10 batching, mixed-width tape interfaces and Gaussian
  correction; Douglas Colkitt and OpenAI: earlier retained constructions.

Composition and checks by Rohan Arun with substantial OpenAI Codex assistance.
No exclusive priority is claimed for the data-corner or nested-basis lemmas.
