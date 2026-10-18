# P104 two-target sharing: exactly 78 helper lifetimes

Correcting **Y0 and Y1 together** in PR2393's fixed-path, X-only monotone
relay model requires exactly **78 new helper lifetimes**. The two 48-source
correction supports share 18 sources. A single acquisition of each shared
source can serve both targets through an invertible two-total basis in their
seven-dimensional common frame. The literal word restores every independent
dirty input and completes `Y0 <- y0+x0`, `Y1 <- y1+x1`; the other 102 target
rows retain the original `G/2` channel.

This answers the two-target sharing handoff in
[PR2393](https://github.com/CrocSwap/integer-mult-bounds/pull/2393), pinned at
`8b3e3a22c9e957990863ef60a561072dfcf08271`. Its one-target source-acquisition
argument is credited and applied to the union of these two supports. The new
result is the matching shared construction and the exact two-target minimum.
It is a **scoped written proof with exhaustive finite premises and a full
logical circuit certificate**, not a complete supplier or new kappa.

## Model and proof

Frames are subspaces of `F2^9` in the frozen source coordinates. New helpers
start source-independent, with arbitrary independent dirty values. They may
read immutable original X registers on their retained frame paths, mix by
rational ADDs at equal frames, and transport upward. No added operation reads
an original G/Q/D/private register or a Y target, writes an X register, or
transports information between unequal frames for free. Target writes are
additive and coefficients are input-independent. Each reinitialization starts
a new lifetime. Logical helper values restore at their final FULL chart;
physical entrance and exit arrays are not asserted equal.

For each of the **96 required target-source pairs**, the source's first frame
expansion already leaves that target's endpoint. There is no direct source to
target equal-frame contact. Every contributing dependence path must therefore
start with a read on the source's initial line. The 78 union sources have
distinct initial lines, and a monotone lifetime cannot visit two of them.
This proves the 78 lower bound even with arbitrary retiming along retained
paths, arbitrary relays/cancellation, and relaxed restoration. It is not a
finite search over programs and not a simultaneous physical stock bound.
[REVIEW.md](REVIEW.md) gives the full independent argument and finite witnesses.

The 18 shared sources have coefficient ratios nine `+1` and nine `-1`.
Capture `z_s=d_s+C[0,s]x_s` and gather them in `J=H0 intersection H1`.
Choose pivots a,b with ratios -1,+1. The two determinant-one shears
`u += v; v -= u/2`, followed by nonpivot additions, give
`u=sum z_s` and `2v=sum ratio_s*z_s`. Deliver u at H0 and 2v at H1.
Each 30-source exclusive group contributes one additional total. Initial
ZERO-frame compensation cancels every dirty contribution. At FULL, reverse
all gather shears and subtract the captured X terms to restore every helper.
No extra clean register or new private-copy lifetime is used.

The original 4,058 events retain their order. New insertions are at cuts
0 and 4058. [CIRCUIT.json](CIRCUIT.json) contains the literal shared word;
[SEPARATE.json](SEPARATE.json) is a checked comparison with one independent
dirty helper per nonzero correction entry, using no gather network.

## Complete local accounting

Here Hr is one logical nested transport with dimension gap r, not a scalar
primitive or a complete hosted recursive child invoice.

| Added quantity | Shared word | Independent-entry comparison |
| --- | ---: | ---: |
| Helper lifetimes | **78** | 96 |
| Rank mass under ZERO-to-FULL boundary | **702** | 864 |
| Scalar ADDs | 440 | **384** |
| Source reads | **156** | 192 |
| Nested transports | **236** | 288 |
| Rank profile | 142 H1 + 16 H2 + 18 H6 + 60 H7 | 192 H1 + 96 H7 |

Sharing saves 18 acquisitions and 162 boundary rank units (18.75%), while
using 56 more logical scalar additions. No scalar-count optimum is claimed.
The predecessor's different one-target two-arrival word is not used as the
384-ADD comparison.

The shared ADD bill is 96 dirty compensations + 78 captures + 92 gather
shears + 4 deliveries + 92 inverse shears + 78 cleanups = **440**. The full
partial channel has **4,734 events and 358 independent input columns**.
Its profile is `1216 H1 + 74 H2 + 86 H3 + 104 H4 + 48 H5 + 42 H6 + 68 H7 + 8 H8`,
rank mass 3070. All original 72 dirty helpers and all 78 added dirty helpers
restore. The original eight owned private-copy lifetimes are inherited.

Every monotone ZERO-to-FULL helper pays nine rank units by telescoping;
therefore 702 is sharp under that additional boundary/billing convention.
It is boundary progress, **not automatically recursive excess cost**.
The complete word's ideal logical row-l1 maximum is 106 and its maximum
coefficient denominator is 4, unchanged from the original channel. These
are exact logical prefix facts, not physical precision or roundoff admission.
[RESULT.json](RESULT.json) records every coefficient/invoice check and all
96 source-escape witnesses.

## Reproduce and evidence

Python 3.12, standard library, read-only direct commands:

```sh
python3.12 -I -O -B research/p104-two-target-sharing/verify.py --regenerate
python3.12 -I -O -B research/p104-two-target-sharing/independent.py
python3.12 -I -O -B research/p104-two-target-sharing/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-two-target-sharing
```

The primary replay uses sparse Fraction rows and enumerated binary subspaces;
it consumes the fixed circuit and compares every field of the fixed receipt.
The separate specialist's checker uses dense integer rows with power-of-two
denominators and binary Gaussian elimination; it imports neither the primary
checker, generator nor predecessor code. Both check all 128,164 endpoint
coefficients. Their endpoint hashes use different documented serializations;
acceptance is exact coefficient comparison, not hash agreement.

Eleven primary fault controls and seven independent faults reject; equivalent
binary basis order is accepted. Package tests exercise missing/changed evidence,
source drift, malformed JSON, exclusive output, Git-free read-only execution,
and sensitivity when the endpoint predicate is deliberately removed. Default
verification never regenerates missing evidence. `--emit-initial-result` is an
explicit authoring mode, separate from default verification.

The registered replay checks both complete regenerated JSON payloads rather
than container bytes. These checks do not run the selected frontier cold replay,
native transport compilation, hosted CI, or a formal proof kernel.

## Sources and credit

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
[SOURCES.json](SOURCES.json) pins the base, selection provenance and live inputs.
The immutable PR1972 word retained through PR1991 has SHA256
`0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e`;
the P104 fixture has SHA256
`516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4`.
The selected record and all predecessor files remain unchanged.

Credit commdata2338/PR2393 for the one-target proof/construction and sharing
handoff; Hiroki Kumazaki (kumagi)/PR2353 and Philippe Van Velzen's correction
screen for the monotone model and lifetime/cover distinction; Rohan Arun/PR1972
for the word, Chafik Boukhalfa/PR1991 for native realization, Adam Gall/PR1940
for the schedule, Josie Elliston/PR1071 for the fixture, Ali Romman/PR1125 and
the retained PR968/717/446/595/620 lineage. The pooled-space work of Gonzalo
Mier, Gareth Davidson and AAAmirinu and the 41-contact lift have different
information-access contracts and are not claimed here.

Prepared for Ross Richardson with substantial OpenAI Codex assistance in
derivation, implementation, checking and writing, including a separately
implemented mathematical specialist audit. No independent human review is
claimed. New material is Apache-2.0; source attribution and licenses remain.

## Open next questions

Can a third named target share acquisitions while permitting enough independent
collector totals in compatible common frames? First compute the union support
and common-frame coefficient ranks, then construct and restore a literal word.
Do not multiply the 48-source bound by the number of targets or assume this
78-helper construction scales. The source/collector rank and chronology are
the concrete gates; see structured questions in [TASK.json](TASK.json).

For this exact two-target word, a separate task can compile its 236 new nested
transports and verify native phases and both required orientations. Physical
scalar/address lowering, global owners, idle/residual recursive charges,
precision/tape, all-size admission and a completed 104-target moment remain
unverified. The fixed original channel's native proof does not automatically
cover these added transports. There is no favorable complete-supplier budget
or new kappa claim.
