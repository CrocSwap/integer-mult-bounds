# Six-source path with one atomic TRIO

**Scoped exact negative result.** A six-source closed connector path containing
thirteen singleton source calls and one atomic three-source call cannot cover
all 63 nonzero output masks using paired readouts when the total of 16 source
map applications is restored at minimum multiplicity. The best coverage in
that exact domain is 61/63. One maximum path repairs its two missing masks with
four readouts apiece, for a completed total of 144 root calls. The incumbent
singleton construction uses 142. At equal unit call prices, this TRIO path
loses by two calls before any TRIO-specific overhead. This is not a result
about paths with two or more TRIO calls, other operation alphabets, or changes
to the readout/restoration model, and it gives no new kappa.

## Exact domain and census

The path has six source labels, thirteen singleton steps, and one TRIO step
`TRIO_{j,k,l}: z += B_j x_j + B_k x_k + B_l x_l`, with three distinct labels.
The sources are read-only and the connector may start dirty. Source updates
commute, so moving the TRIO to the end preserves all pairwise differences
between boundary states. The final TRIO must toggle exactly the three labels
whose singleton counts are odd.

There are 16 source-map applications altogether. Restoring every source
requires an even count of at least two, so the only possible sorted total
source-map profiles are `(2,2,2,2,4,4)` and `(2,2,2,2,2,6)`. Subtracting the
three final TRIO applications yields the two enumerated sorted singleton
profiles `(1,2,2,2,3,3)` and `(1,1,2,2,2,5)`.

`search.py` exhausts every restricted-growth string (RGS) of length 13 using
all six labels. RGS canonicalization quotients coordinate relabeling, which
preserves XOR coverage. Repeated prefix states are allowed. For each word the
search incrementally accumulates all pairwise XORs of `p0..p13`; `p14=p0`
after the closing TRIO. It counts 9,321,312 complete six-label RGS words and
2,342,340 words in the two charged profiles. None covers 62 or 63 nonzero
masks; 88 paths attain 61. The complete coverage histogram and a fixed-width
SHA-256 digest of every eligible word/coverage record are in
[CERTIFICATE.json](CERTIFICATE.json).

The maximum witness is singleton labels
`0,1,0,2,3,0,4,5,4,1,3,4,5`, followed by `TRIO_{0,2,4}`. Its source-map counts
are `(4,2,2,2,4,2)`. Prefixes are
`0,1,3,2,6,14,15,31,63,47,45,37,53,21`. Its paired-readout set misses masks
11 and 40. Boundary indices `(0,1,7,13)` XOR to 11; `(0,1,4,9)` XOR to 40,
so each can be emitted with four readouts while restoring the output.

## Completed cost

Let `f` be the complete per-source-call frame and dispatch tariff, `g` the
price of one output readout, and `rho` all incremental TRIO expenses. The
source-map application multiset matches the incumbent and can be assigned to
the same source tariffs. Its 16 singleton calls emit 63 rows twice each:
142 root calls total. The best one-TRIO path uses 14 source calls. Since it
misses two rows under paired readout, completing those rows with four
readouts each adds four output calls, giving 130 output readouts and 144 root
calls. Thus

```text
candidate - incumbent = -2*f + 4*g + rho.
```

Here `rho` includes any extra TRIO arithmetic, source access, descriptors,
precision, copied information, hosting, restoration, and interface-routing
cost beyond the same 16 source-map applications and common work. At unit call
prices `f=g=1`, the candidate costs `2+rho` more. A different tariff model can
be assessed from the displayed equation; no unpriced TRIO operation or
supplier improvement is assumed.

## Reproduction

From the repository root, the registered replay recomputes the full Python
census and checks the certificate, witness, positive control, negative
controls, and bill:

```sh
python3 -B research/six-source-trio-path-seed87a169/verify.py
```

Expected final line:
`PASS_SINGLE_TRIO_CENSUS eligible=2342340 max=61/63 at_max=88 completed_queries=144 incumbent=142`.

An independent C++ implementation recomputes the pairwise differences directly
at each eligible leaf (rather than incrementally maintaining coverage):

```sh
g++ -O3 -std=c++17 research/six-source-trio-path-seed87a169/independent.cpp -o /tmp/six-trio-independent
/tmp/six-trio-independent
```

It reports the same node count, profile count, maximum, and complete histogram.
The repository positive control is the known 16-singleton six-source word,
which covers all 63 nonzero masks. Negative controls reject an invalid source
profile and an out-of-alphabet label.

The original boundary-model control is also reproduced by
`python3 -B research/universal-connector-boundary/verify.py`.

## Provenance and limits

The source manifest pins the selected record, task catalogue, and model
predecessors to base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The six-source
singleton result is in `research/universal-connector-six-source/`; the
unchanged boundary model is in `research/universal-connector-boundary/`.
PR #1518's reviewed scope is a ten-call, one-TRIO, twelve-source-map census;
this package instead covers fourteen source calls and sixteen map applications.
The nearest active connector claim in the fresh snapshot concerned six-source
DUO paths, a different operation.

This result is restricted to one TRIO, thirteen singleton calls, six sources,
16 source-map applications, the restored even-count profiles above, and the
paired-readout model with four-readout repairs. It does not rule out another
alphabet, a longer source path, multiple TRIO calls, a changed restoration
contract, or a different weighting of frames and readouts.

## Open next questions

Can two or more atomic TRIO calls reduce the completed six-source bill? This
changes the call-count frontier and the attainable prefix-difference set. A
bounded first step is to derive the optimistic source-map profiles for twelve
singleton calls plus two TRIO calls and test whether all 63 rows can be paired
with fewer than 126 readouts. It is outside this cycle's one-TRIO census and
has no known blocker.

## Credit

Prepared by OpenAI Codex with substantial AI assistance in the mathematical
search design, implementation, cost accounting, and write-up. No predecessor
code is imported; model and incumbent claims are attributed to the pinned
repository sources above.
