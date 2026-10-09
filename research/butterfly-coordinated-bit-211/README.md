# Butterfly reassociation with coordinated frames

Conditional saving: κ = 684696826673891/1000000000000000000
= 6.84696826673891e-4. This combines 440 local XOR butterflies, PR211's
6,191 cascade-optimized operation-frame entries, the PR200/202 bit construction,
PR197 residual packing and the retained PR193 complex supplier. The three
PR211 entries at butterfly pair operations 15154, 16230 and 16881 are
explicitly replaced by the corresponding admitted butterfly pair frames.

The all-size interfaces stated in PROOF.md remain conditions. This package
is a finite supplier certificate and composition, not an unconditional
integer-multiplication theorem or a benchmark of an implemented multiplier.

## Reproduce from public sources

Use Python 3.11 or newer with assertions enabled, on Linux or macOS. From
the repository containing this package, obtain the exact public dependencies:

```sh
git clone https://github.com/ikeboy/integer-mult-bounds complex193
git -C complex193 fetch --depth=1 origin 187e1010ac8b259af8e9b5166f68b64bc27b4b47
git -C complex193 checkout --detach 187e1010ac8b259af8e9b5166f68b64bc27b4b47
git clone https://github.com/CrocSwap/integer-mult-bounds bit202
git -C bit202 fetch --depth=1 origin 8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d
git -C bit202 checkout --detach 8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d
python3 -m venv .venv-butterfly
. .venv-butterfly/bin/activate
python3 -m pip install -r research/butterfly-coordinated-bit-211/requirements.txt
python3 -B research/butterfly-coordinated-bit-211/verify.py \
  --complex-root "$PWD/complex193" --bit-root "$PWD/bit202" \
  --output "$PWD/build/butterfly-run-1"
```

SOURCES.json lists every consumed source hash. The exact PR211 frame witness is included as a pinned gzip/base64 payload,
alongside the frozen butterfly overlay. No execution receipt or
pre-existing cache is an input.
The verifier itself does not fetch sources. Output must be new, outside the
package and source checkouts. Failed outputs are preserved; use a new output
path when rerunning. Original source files are never changed.

For cheap controls and source admission without a supplier proof:

```sh
python3 -B research/butterfly-coordinated-bit-211/test_public.py
python3 -B research/butterfly-coordinated-bit-211/verify.py \
  --complex-root "$PWD/complex193" --bit-root "$PWD/bit202" \
  --output "$PWD/build/butterfly-preflight-1" --check-inputs-only
```

Preflight checks only exact package/source admission. It is not a proof run.

## What a successful full run establishes

- Six fresh stages of the pinned PR193 complex proof, the strict portability
  comparator, and four accepting/22 rejecting comparator controls.
- Canonical emission of the changed graph, word and complete frames; fresh
  abstract and physical admission, including source/gauge/alias chronology.
- Baseline F2 and defining-integer columns, then all 20,634 terminal columns
  in the three required F2/+1, Z/+1 and Z/−1 outcomes. Sources and arbitrary
  dirty contents are restored, with literal reverse cleanup and original
  partner delivery anchors. Only the F2 decoder is identity.
- Exact prime witnesses for 25,723 used frame IDs in 24,611 distinct bases,
  with separate coverage and missing-record rejection.
- Actual effective-word packing: 220 rational charts, 154,026 incidences,
  45,842 full banks, all nine invocation costs and separate selector tolls.
- Two paid rational-moment enclosures, three finite ordinary levels, the
  complex finite bridge, 47 strict assembly constraints, seven margins and
  exact equality with certificate.json.

The original completed PR200/202 ordinary seed is reused as a public proof
dependency in base-bit-certificate.json. Its paid moment and strict atom
wrapper are rederived. The full original seed word is not freshly replayed
by this command; its source-bound proof is unchanged. The new changed bit
word is fully replayed. The coarse limiting saving is never used directly
as an ordinary leaf.

Under the selected output directory, `effective-bit/` holds the complete
emitted graph/word/frame archives, abstract profile, all-used prime witness
archive and bit receipt. The top-level output contains the mathematical
certificate, packing/scalar recount and execution receipt. Logs, timings,
platform metadata and actual compressed-file hashes remain output data;
the committed certificate contains exact deterministic mathematics.

The complex portability wrapper permits only the two designated numerical
discovery-root diagnostics at the inherited display precision and explicitly
rebound downstream hashes or gzip representation differences. Exact flow,
scalar-program and proof payload identities remain required. A successful
wrapper run is not described as an unmodified upstream default-aggregate
pass.

## Review status and costs

The complete development finite proof and actual profile/price binding
passed. The public command is designed to reproduce its required stages
and persist their outputs. Its own successful execution establishes that
clean-package result; focused checks or prior receipts do not establish a
repository-wide aggregate pass. The PR description records execution status.

The normalized paid profile has m=72, W=56,402, rank mass 4,055,136 and
deficit 5,808. Its bill includes 7,093,890 literal XORs and 5,701,209,426
ordinary-selector calls across nine complete cores. No earlier stock132
rewrite or separately reported improvement is added to this construction.

See PROOF.md for the argument and NOTICE.md for named credits. Historical
UPSTREAM_PROOF_PR197.md and UPSTREAM_SOURCE_PR197.json retain the predecessor
packing dependency; their older supplier counts are not current gains.

Assisted with ChatGPT.
