# A native format theorem for the rank-seven A13 half-ADD

This closes one native-conversion part of the released
[PR3083](https://github.com/CrocSwap/integer-mult-bounds/pull/3083) and
[PR3084](https://github.com/CrocSwap/integer-mult-bounds/pull/3084) handoffs.
For the actual A13 boundary in both PR3076 providers, independent signed
P-bit normalized input components require exactly two fractional bits and
P+5 signed bits. At P=64 this is a 69-bit local format.

The theorem includes the Gaussian frame conversion omitted by the formal
scalar certificates. It is a conditional local physical-format result.
It does not establish a complete physical prefix, supplier or new kappa.

## Result and source boundary

The fresh emitted forward program has these consecutive events, at zero-based
indices 6683 through 6685:

```text
warp source83 from [382] to [45], operator 52
climb target126 from [] to [45], rank 1
target126 -= source83 / 2, in frame [45]
```

An exact free-warp prefix replay derives the normalized values

```text
source = u = initial83
target = v = (initial126 - initial127 + initial164 - initial165) / 2
```

Write E=[382], F=[45], K=K52 and W=T_F K T_E^-1. The physical entrance
fields are T_E u and v. The checked physical boundary returns

```text
source = S = T_F K u
target = V - S/2, where V = T_F v
```

All 512 columns, including phases, establish that W is a Gaussian monomial
and W T_E = T_F K. W differs from K. Substituting the logical warp for the
physical warp fails. Both normalized target dirt and source dirt remain in
the theorem. The [proof](PROOF.md) gives the exact input contract and sharpness.

For L=2^(P-1), P>=3, the global component ranges are:

| Field | Exact component range | Range after encoding on the quarter grid |
|---|---:|---:|
| Source S | ±(2L-1/2) | ±(8L-2) |
| Converted target V | ±(4L-2) | ±(16L-8) |
| Final target V-S/2 | ±(5L-9/4) | ±(20L-9) |

The extrema are attained over the independent input box, possibly at different
coordinates. The final row norm is 5. One fewer grid bit fails on a basis input;
one fewer signed bit fails at an explicit extremal input. Every source encoded
on the quarter grid is even, supplying the half-ADD alignment premise.

The native operator's gate endpoints and predivision C numerators fit the same
format. [PROOF.md](PROOF.md) also bounds partial four-term numerator sums.
These are arithmetic capacity bounds, not a bit implementation of the native
conversion or its storage/routing invoice.

PR3080's literal read-only half-ADD circuit executes the two extremal fixtures
at 69 bits, preserves the source and returns 68 clean carries. Its constructed
local tariff is 541 Boolean gates per real component, or 553,984 for all 1,024
components if executed sequentially with reusable carries. Clean carry backing,
exclusive source/target access, placement and every non-ADD cost remain additional.
The lower-width caller rejects the same fixtures before execution.

## Evidence and reproduction

[RESULT.json](RESULT.json) contains both fresh complete emitter checks, program
hashes, exact operator hashes, internal-format ledgers, attaining assignments
and literal bit-circuit results. Native transport/emission is reused, with
source bytes pinned in [VENDOR.json](VENDOR.json). The new sparse Fraction
operator evaluator is checked against the retained independent packed-integer
Clifford evaluator on every column. This is internal automated verification,
not independent human review or a proof-kernel theorem.

Python 3.12, standard library only. From the repository root, set RUN to a
fresh session-owned directory outside the checkout:

```sh
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -W error -B \
  research/rank7-native-half-boundary/verify.py --work "$RUN/replay" \
  > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-native-half-boundary/RESULT.json
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/rank7-native-half-boundary
```

Without `--work`, replay removes its temporary outputs beneath TMPDIR.
The registered replay also runs optimized behavioral tests. Controls include
wrong Gaussian signs, an omitted climb, insufficient formats, physical/logical
warp confusion, source-bound sign mutations, a hidden warped dependency and
mutable trace corruption. [CHECKS.json](CHECKS.json) records executed checks
and their limits. [ENGINEERING.md](ENGINEERING.md) records resource bounds.

## Open next questions

Can a concrete physical prefix supply these normalized entrance fields at a
paid format? Start by binding the entry adapters and the original global
normalized inputs to the five arrays here. The retained common-frame theorem
is an assumption of this local interpretation; approximate child defects and
the full prefix's internal precision are not checked here.

Can the consumer retain the saving after guards, routing and clean space are
charged? Start with the actual next A14 through A16 uses of source83, its
unwarp and the target's later climbs. Keep quarter bits live until a proved
return point. The complete ownership, consumer, restoration and supplier invoice
is missing. This contribution does not authorize a larger lowering search.

## Credit

Nick Petalas contributed this local native-format proof and replay. PR3083/3084
supplied the scalar-grid handoffs; PR3080 supplied the reused aligned bit
adder; PR3081 supplied the complementary local guarded caller. Credit
PR3076/3078/3060/3056, dcharb78/PR3042, Jeremy Kothe/PR3015,
Marius-Paul Dumitrean/PR2979, Cinna Davis/PR2226, DLamdata's retained exact
Clifford kernel, icekylinx and the retained Gaussian/native/geometry/owner lineage.
Frozen source notices are unchanged. New work is Apache-2.0. Development used
substantial automated assistance; scientific admission is not claimed.
