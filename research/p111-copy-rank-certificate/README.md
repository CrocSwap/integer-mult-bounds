# P111 copied-rank optimum, without a SAT solver

**Scoped negative result: the generalized label-decoder copy-rank optimum is
63 for the actual #545 and #555 E8 punctures. No new kappa is claimed.**

The [proof](PROOF.md) permits asymmetric rank-one factorizations, repeated
terms and any finite number of totals. Nine totals cost at least 63; ten cost
at least 64; eleven or more cost at least 66. Literal nine-term witnesses
attain 63. This closes one precise way to reduce copied information, under
the stated per-total pairing-rank price, without pricing a new supplier.

It also resolves a source-binding discrepancy in the archived #620 decoder
experiment. Its sorted Hamming-root numbering differs from the actual word
files. Applying the same numeric deletion list selects a different puncture.
The exact permutation is in [ORDERING.json](ORDERING.json); the checker binds
all roots, live indices and deletions to the pinned supplier files. The
reported optimum is corroborated for the actual published examples, but the
archived geometry is not silently treated as their replay.

## Reproduce

From the repository root at base
`66849e1475c930fd7732b1a0067ffee7e1e95f60`, with this package applied:

```sh
python3 -B research/p111-copy-rank-certificate/verify.py --check research/p111-copy-rank-certificate/RESULTS.json
```

Python 3.9 or later, standard library only; no installation, optimizer,
network connection or source generation is needed. Expected output:

```text
PASS_P111_COPY_RANK: optimum 63 on two fixtures; exact geometry, independent minors, 18 negative controls
```

`--write /absolute/path/results.json` writes a fresh deterministic receipt.
The verifier works from another current directory as well. It is safe to
run with Python's `-O`: checks do not depend on `assert` statements.

The narrower candidate evaluator can be run separately:

```sh
python3 -B research/p111-copy-rank-certificate/evaluate.py research/p111-copy-rank-certificate/baseline-pr555.json
```

It returns a valid nine-term cost-63 decomposition. Its search interface caps
input length at 20; the written proof's all-length conclusion does not rely
on that implementation cap.

## Evidence and scope

For **each** published fixture, the checker verifies:

- all 511 nonzero functional supports with independent integer and rational
  elimination: nine hyperplanes of dimension seven, 502 full spaces;
- all 100 ordered pairs of span classes, covering all 261,121 ordered
  nonzero functional pairs by the proved span classification;
- all 12,321 live decoder matrix entries and the literal optimum witness;
- an independent rank-three target minor untouched by every cost-six term,
  excluding a ten-term solution below 63;
- nine failure controls, including the wrong-root-order regression.

In addition, all nonsingular symmetric unit-diagonal 3-by-3 binary matrices
are exercised across 672 square and 40,320 one-extra-term factorizations.
These finite controls test the projection mechanism; the dimension-nine,
arbitrary-length conclusion is the written algebraic proof, not an inference
from those smaller examples. The stronger ten-term lower bound of 64 uses
that proof; the independent minor certificates only exclude costs below 63.

The geometric premises, source pins and baseline witnesses are exact.
The interpretation as a price for physical copy trees inherits #446's
Theorem C and its model assumptions. Arbitrary non-label rectangles, changed
decoder matrices, vector-valued labels, helper work, frame scheduling,
restoration, all-size compilation and the full multiplication theorem remain
outside scope. The selected frontier and `upstream/` are unchanged.

## Provenance and prior work

[SOURCES.json](SOURCES.json) pins the base and 16 repository files, including
the original compressed word bytes. `roots.json` is a small extraction of
the R420 root table; it is compared to that source and to a freshly generated
E8 root set. No upstream implementation is imported by the arithmetic code.

DreamingOfClouds' #545 and eumemic's #555 provide the two punctured suppliers;
GamingPuzzled's #620 reports the earlier cost-63 SAT obstruction without proof
logs; DreamingOfClouds' #446 provides the drop-pricing framework. The point of
this contribution is a portable algebraic proof and precise source binding,
not priority for the number 63. Related #631 and #669 study different decoder
classes. The final overlap review also read #717's complex decoder section:
its P111 examples use eight rational terms and a binary pairing-rank price,
whereas this result uses binary label terms and a rational pairing-rank price.
#703 concerns quaternionic lines; #708 changes operand preparation, and #715
adds non-root ports. See [NOTICE.md](NOTICE.md) and [METHOD.md](METHOD.md) for attribution,
the bounded fork-and-flush run, the corrected evaluator and verification limits.

This is a research contribution for review. No human-only review or
proof-assistant verification is claimed. Local test details are in
[VALIDATION.md](VALIDATION.md).
