# Signed dependent-source delivery with a restored dirty connector

**Scoped exact interface theorem and finite construction; no new kappa.**
Three successive sources `x,x+u,x+2u` admit four complete signed source queries
and six reader queries, versus six source and six reader queries when every
request closes its connector. The signed balance is `(1,-2,1)`: the middle
request leaves a doubled negative contribution, which the last request cancels.
The connector and outputs may be arbitrarily dirty; every output is delivered
within its own request. Source updates and final source restoration are paid.

[PROOF.md](PROOF.md) proves the all-word optimum for any finite rational
source-dependence matrix with nonzero rows, exact linear Q/C maps and positive
sign-symmetric complete tariffs. If `phi(0)=2` and `phi(t)=abs(t)` otherwise, it is

    2 sum a_i + min_{t in Z^k, M^T t=0} sum b_i phi(t_i).

Arbitrary query multiplicities and signed readouts are allowed in that grammar.
The result changes Adam Gall [PR2060](https://github.com/CrocSwap/integer-mult-bounds/pull/2060)'s
binary correlation algebra to characteristic zero, with no correction oracle.
It does not change the validity of that predecessor or claim priority for
dirty echoes, source dependence, integer kernel methods or signed queries.

The full macro comparison removes two **whole completed source calls**. If each
has child histogram `nu_r`, the delta is `-2 nu_r`, before all noncommon lifetime,
precision, controller, hosting and routing charges. A favorable real caller
requires those extra charges below the two removed complete calls. No selected
caller, supplier admission, new moment root or multiplication theorem is supplied.

## Exact finite calibration and limits

The pilot uses `B=[[1,1],[1,-1]]` and readers `(1,0),(0,1),(1,1)` on nine
distinct dirty scalar ports. Its source mutations are `+u,+u,-u,-u`, with the
last two explicitly restoring x after the third delivery. All B and A maps
are expanded to literal signed unit ADDs. No clean ancilla is used.

| Same ports and source schedule | Closed queries | Signed dependence | Direct fused maps |
|---|---:|---:|---:|
| Source B calls | 6 | 4 | 0 |
| Reader A calls | 6 | 6 | 0 |
| Source-update scalar ADDs | 8 | 8 | 8 |
| All scalar ADDs | 40 | 32 | 14 |
| Return-to-origin unit-cell head moves | 372 | 300 | 124 |
| Unit-cell steps, including each ADD | 412 | 332 | 138 |
| Exact primitive-prefix maximum row-L1 | 8 | 9 | 7 |
| Literal inverse maximum row-L1 | 9 | 8 | 7 |

The direct comparator is cheaper after opening the maps. This prevents an
unrestricted-optimality or physical-speedup claim. [RESULT.json](RESULT.json)
records every return-to-origin unit-cell head movement and exact intermediate
row-L1 bound, separately from the complete recursive query tariff. Unit-cell
movement is a specified finite model, not a fixed-tape bit-complexity proof.
The candidate crosses the conservative guard threshold from three extra
magnitude bits to four when all entry coordinates have the same bit bound.
This is real prefix growth: a target reader's component ADDs need not cancel
at its interior cut. A caller reserving one capacity for both a full forward
pilot and its literal inverse needs maximum 9 for both candidate and closed
words, so its precision charge need not increase. A fair comparison must price
the actual direction/range contract; fewer unit ADDs alone do not establish a
physical gain.
The full primitive inverse reverses the source mutations as well; inverse
admission to a forward-only source schedule is not claimed.

## Evidence and reproduction

From the repository root, standard-library CPython 3.12:

```sh
python3.12 -I -B scripts/research_package.py --package research/signed-dependent-delivery
```

Direct read-only commands work in a Git-free source export containing the three
declared predecessor README inputs:

```sh
python3 -I -O -B research/signed-dependent-delivery/verify.py
python3 -I -O -B research/signed-dependent-delivery/independent.py
```

The primary verifier checks 117 exact optimizer cases, all 81 endpoint
coefficients for each of three primitive programs, every delivery cut and
literal inverse, 19,683 dirty ternary-grid states, and all single-gate omission
and sign defects. It also rejects invalid contract inputs and the integer lift
of a merely binary-restored balance. These finite checks corroborate the
written all-parameter proof; they do not establish it by exhaustion.
The separately implemented unrestricted signed-query Dijkstra and its precise
covered cases are documented in [INDEPENDENT.md](INDEPENDENT.md). Both are AI
implementations under the same human assignment, not independent human review.
`--write` explicitly regenerates only the primary result receipt; default
verification writes nothing and compares its whole canonical payload.
The registered portability check also executes both verifiers in an optimized,
read-only Git-free export and rejects source drift, an undercharged receipt
and a bool/integer receipt substitution. All independent behavioral checks
remain active under Python optimization.

## Open next questions

1. Does one actual complex recursive caller have an exact affine source path
   `x,x+u,x+2u` with these delivery cuts? Extract its literal source updates,
   complete child histograms, frames and observer permissions before adopting
   the schedule. No such occurrence is established here.
2. Can the same caller retain its connector without losing profitable borrows
   or increasing precision? Join all physical lifetimes and compiled internal
   ranges, then compare the complete invoice against the best legal fused
   baseline. Stop if added costs exhaust the two completed-source-call saving.

## Pins, credit and scope

Scientific base: `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
The selected record and its conditional result are unchanged. Exact predecessor
README bytes and Git blobs are in [SOURCES.json](SOURCES.json).
Canonical claim/finding:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1776#discussioncomment-18983463

Credit **Adam Gall** PR2060 `3555161e4f292b49622ee05cfb3fbbb34ddfbf75` for the
known binary dependence matrix, unrestricted-multiplicity proof and incoherent
two-read attaining grammar; **Ross Richardson** PR1780/934/943 for imposed
updates, delivery cuts and the dirty-connector model; **woklerx** PR1439/1442
for mutable-source correction and delivery-cut precedents; **martinxxx9**
PR1088 for sign-symmetric complete signed prices and restored lowering.
The broader dirty-commutator and supplier lineage remains with those sources.
No predecessor code is imported or vendored, and no frozen package is modified.

Prepared by Ross Richardson with substantial OpenAI Codex assistance in
derivation, programming, documentation and separate mathematical verification.
Apache-2.0 under the repository LICENSE. Written proof plus exact finite checks;
no formal-kernel certificate, human theorem review or hosted CI pass is implied.
