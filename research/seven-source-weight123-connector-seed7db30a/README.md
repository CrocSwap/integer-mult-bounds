# Seven-source weight-1/2/3 dirty connector: exact 14-toggle boundary

**Scoped construction and finite obstruction; no new κ.** For seven immutable
F2 sources and one dirty connector, consider the 63 output masks of weights one,
two, and three. Among all 135,135 canonical source words using each source toggle
exactly twice, the maximum number of these masks available as paired prefix
differences is **56**. No 14-source-call word supports all 63. The maximum is
attained by a literal word that supports every singleton and pair mask plus 28
triple masks. Its 56 arbitrary outputs attain the dirty-query call floor: 126
complete map calls.

The result is limited to the stated seven-source batch and exactly two calls per
source map. It does not exclude a 142-call schedule using additional source
calls, and it is not a supplier, recursive assembly, multiplication bound, or
new κ result.

## Exact finite result

Bit `j` denotes source `B_j`; decimal masks in [RESULT.json](RESULT.json) use that
convention. The maximum-coverage source word is

```text
0 1 2 0 3 2 4 3 5 4 6 5 1 6
```

Its boundary prefixes are

```text
0 1 3 7 6 14 10 26 18 50 34 98 66 64 0
```

The 56 supported target masks are exactly seven weight-one masks, all 21
weight-two masks, and 28 weight-three masks. The missing triple masks are

```text
22 38 41 42 73 81 84
```

The JSON receipt contains a pair of prefix-boundary indices for every supported
mask. The full census has two maximum-coverage words (both cover 56), zero
full-cover words, and the complete coverage histogram. Source-label
permutations preserve the target family, so canonical first-appearance labels
lose no cases.

## Why prefix differences implement the batch

At boundary `t`, let `q_t` be the seven-bit parity vector of the source toggles
already called. For arbitrary dirty connector `z_0` and arbitrary F2-linear
maps and inputs,

```text
z_t = z_0 + sum_j q_t[j] B_j x_j.
```

For output mask `M`, call its map `A_M` at boundaries `s` and `t`. The dirty
connector term cancels, leaving

```text
A_M z_s + A_M z_t
  = A_M sum_j (q_s[j] + q_t[j]) B_j x_j.
```

Therefore any pair with `q_s XOR q_t = M` realizes exactly that output and
restores its dirty target. Every source appears twice, so the final connector is
restored. Readouts at a boundary commute because they update distinct output
rows and do not change the connector. This argument works at every vector
dimension and requires no invertibility or commutation of the maps.

The maximum word supplies all 56 listed masks, so it constructs that arbitrary
56-output batch. Each active source map and each arbitrary-dirty output map must
be called at least twice in this connector contract. Thus `2(7+56)=126`
complete calls is attained for that support. For all 63 masks, the elementary
floor would be 140. At exactly 140 calls, dirty restoration forces every one of
the seven source maps and 63 output maps to occur exactly twice. Specializing
the arbitrary maps to scalar identities with independent source bits shows
that an output can then be correct only if its mask is a difference of two
source-prefix states. The complete census excludes that floor. Each map's
generic call count is even, so the full family needs at least 142 calls. No
142-call upper bound is claimed.

## Complete cost comparison for the attained 56-output support

Each source occurs in 19 of the 56 masks. Independent per-output stars therefore
use 38 calls to each `B_j` and two calls to each of the 56 `A_M` maps: 378
complete map calls. The shared word uses two calls per source and two per output:
126 complete map calls, saving 36 complete source-map calls per source (252 in
total).

Use an explicit straight-line event encoding with a one-bit opcode, a three-bit
`B` identifier and a six-bit `A` identifier. It contains every operation and
its map ID; boundary placement is encoded by event order, so it needs no runtime
search or uncharged address table. This encoding uses 1,848 bits for the 378-call
star program and 840 bits for the 126-call shared program. With `lambda` the
price per stored event bit, `delta` the per-event root-dispatch price, `c(B_j)`
the complete `B_j`-call price, and `c(A_M)` the complete target-call price, the
two invoices are

```text
C_shared = I + P + 2 sum_j c(B_j) + 2 sum_M c(A_M) + 840 lambda + 126 delta
C_stars  = I + P + 38 sum_j c(B_j) + 2 sum_M c(A_M) + 1848 lambda + 378 delta
C_shared - C_stars = -36 sum_j c(B_j) - 1008 lambda - 252 delta.
```

`I` is the common input admission and `P` is the common one-time coefficient
preparation. Each complete call price includes its source access, arithmetic,
target update, private scratch restoration, and head return. This is a
componentwise reduction for every nonnegative event-storage and dispatch price.
It counts the full calls; it does not assert that a physical supplier for this
interface exists.

For comparison only, the hypothetical 140-call floor for all 63 outputs would
save 294 source calls and 1,176 event bits relative to independent stars, but
the exact search proves that schedule does not exist with two uses of each
source.

## Exact domain, reproduction, and controls

The source word induces a perfect matching of the 14 call positions: the two
positions carrying each source label are paired. Relabeling pairs by their
first position gives one canonical word per perfect matching, hence
`13*11*9*7*5*3*1 = 135,135` cases. `search.py` enumerates this domain by the
least unmatched position and emits the exact receipt. `verify.py` independently
enumerates restricted-growth double-occurrence words, checks the full histogram
and maximum, and replays the dirty-state identity on deterministic arbitrary
F2-linear maps at dimensions 1, 2, and 3.

From the repository root:

```sh
python3 -I -B research/seven-source-weight123-connector-seed7db30a/search.py
python3 -I -B research/seven-source-weight123-connector-seed7db30a/verify.py
python3 scripts/research_package.py --package research/seven-source-weight123-connector-seed7db30a --check-only
```

Expected markers:

```text
SEVEN_SOURCE_WEIGHT123_SEARCH pairings=135135 targets=63 hits=0 best=56
PASS_SEVEN_SOURCE_WEIGHT123_PAIRING_BOUND pairings=135135 max=56 full_hits=0 subset_calls=126 controls=3
PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)
```

Three failure controls detect a deleted source toggle, a deleted second dirty
readout, and a readout pair whose prefix difference omits a requested mask. All
arithmetic in the proof-relevant finite search and simulation is exact integer
arithmetic over F2. The abstract prefix identity, rather than the small random
fixtures, establishes arbitrary-dimension correctness for the attained support.
Local replay used CPython 3.14.7. CPython 3.12 is unavailable in this environment,
so the registered Python 3.12 package replay was not run; the package metadata
and pin check and the verifier in normal and optimized mode were run directly.

## Assignment, overlap, and limits

Cycle 27 used seed `7db30a45a4ca218f66c410637c8459f3`, track
`recursive-interfaces`, task `connector-alphabet-change`, priority revision 4,
and exact base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The selector task asks
for a changed connector alphabet. This changed-scope result retains the
singleton alphabet and changes the matrix-support family; it answers a distinct
structural question about seven sources and low-weight outputs. The selected
record SHA-256 is
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

The refreshed overlap scan covered 463 open PRs and 918 Discussions with
complete pagination and no warnings. Closest work: PR #2128 studies six-source
universal masks with charged DUO calls; PR #2146 excludes a six-source one-TRIO
universal path; PR #2182 studies fixed-port five-source and two-root universal
boundaries. These change the operation alphabet, mask family, or root count and
do not contain this one-root seven-source weight-1/2/3 census. Ross Richardson's
PRs #934/#943 supply the connector contract and paired-prefix criterion; they
are cited for that general reduction, not as a result of this seven-source
census.

No selected record, frozen source, supplier, or frontier value changes. No
independent human review or proof-assistant formalization is claimed. Prepared
by Cinna Davis with substantial OpenAI Codex assistance in scoping, exact
enumeration, dirty-state replay, cost accounting, and writing. New work is
Apache-2.0.

## Open next questions

Can one additional even source toggle lift the seven-source weight-1/2/3 batch
from 56 to all 63 outputs at 142 total calls? This is the next even call count
above the excluded 140 floor and could retain most of the 294-call saving over
independent stars. First enumerate or construct normalized 16-event words with
one source used four times and the other six twice, then apply the same exact
prefix-difference test before evaluating any physical cost. This cycle did not
search that larger domain; the number of normalized words is much larger than
135,135, and a failed finite search would need to remain scoped.
