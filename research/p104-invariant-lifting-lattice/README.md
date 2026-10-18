# A common invariant period lattice for P104 lifting

The fixed P104 integer-lifting transform has a common forward/return
period lattice of index **2^401 at rank seven**, compared with the forward
period group's 2^343. Both lifted directions are ideal linear maps on this
common lattice. Whole-array Gaussian-integer ADDs preserve it, but a
structured address-dependent phase and an integral quarter division can
leave it. This is a local interface result and a stopping point for this
proposed caller contract, with **no recursive-cost improvement or new kappa**.

Let Gamma_r be the prefix-parity period lattice of Nick Petalas's
[PR3035](https://github.com/CrocSwap/integer-mult-bounds/pull/3035) and
[PR3037](https://github.com/CrocSwap/integer-mult-bounds/pull/3037), and U_r
the ideal signed Gaussian transform for Tekalign's fixed PR3025/3033
lifting word. The new entrance contract is

    Lambda_r = Gamma_r intersect U_r Gamma_r.

[PROOF.md](PROOF.md) proves that this is the largest U_r-invariant
sublattice **contained in Gamma_r**, for every finite rank. Both literal
lifting and its literal inverse agree with their ideal maps there. It is
not claimed maximal among every state exactness domain: rank one already
has a larger exact invariant lattice outside Gamma_1. A phase failure here
rejects the period entrance contract; it is not by itself an output-error
witness or a barrier to every lattice interface.

| Rank | Forward index log2 | Common index log2 |
| ---: | ---: | ---: |
| 1 | 2 | 2 |
| 2 | 6 | 7 |
| 3 | 15 | 17 |
| 4 | 34 | 39 |
| 5 | 75 | 87 |
| 6 | 161 | 187 |
| 7 | 343 | 401 |

The rank-seven quotient is
`(Z/16)^4 x (Z/8)^29 x (Z/4)^91 x (Z/2)^116`.
These exact indices cover ranks 1–7; no all-rank index formula or
formal-kernel proof is asserted.

## The mechanism tested and its complete-cost boundary

Restricting every completed boundary to Lambda could remove repeated
nonlinear residue correction. For arbitrary lattice-valued dirty x,y,
the explicit local macro `L(x); y+=x; L^-1(x)` implements
`(x,y)->(x,y+U x)`, restores x literally, and uses two completed transforms
plus one whole-array ADD, with no private helper. Temporary source mutation
requires an unobserved interval. This does not compare its price with an
already admitted recursive child.

The proposed reuse fails two relevant closure tests. Starting with the
constant array of ones, multiplying addresses with one selected bit equal
to one by i leaves Gamma and Lambda. A quarter ADD also needs more than
integral coordinates: at rank seven `16 e_a` belongs to Lambda but its
integral quarter `4 e_a` does not. Unit ADD is safe only when its full source
and target arrays have the declared lattice contract.

For an actual q-call consumer, the exact-cost gain test is

    encoding + decoding + sum(adapters + added full-call costs)
        < sum(complete old work actually removed).

Backend children, precision, all live/borrowed/private storage, copies,
movement, access and inverse restoration must appear on the applicable
side. An encoder B changes a physical U call into logical `B^-1 U B`;
source-to-literal correspondence or a paid intertwining adapter remains
essential. The index difference from the scalar period grid's 1,024 bits
is **not** a 623-bit physical storage saving. No encoder, full consumer,
admitted backend tariff, recursive moment or exponent change is supplied.
The cost comparison and its necessary/sufficient bound directions are
spelled out in PROOF.md. Stop at this bounded interface decision.

## Reproduce and evidence

From the repository root with standard-library CPython 3.12:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/p104-invariant-lifting-lattice
```

The primary checker uses exact index-two changes of a primal lattice
basis. A separate [independent.py](independent.py) uses the image of a
congruence matrix and modular Smith elimination, importing neither primary
nor predecessor implementation. Both methods agree on every displayed
index. Its 256 complete 2x2 mod-four matrices cross-check the modular-image
routine against direct enumeration. [INDEPENDENT.md](INDEPENDENT.md)
records that mathematical review, its finite domains and the important
larger rank-one exactness control.

The primary additionally verifies all 508 common-basis columns, their
ideal U invariance and literal forward/return maps, 35 signed dirty macros
including 4,001-bit coefficients, 28 structured phase witnesses, coordinate
ADD failures, and integral quarter counterexamples. The seven behavioral
groups reject missing reverse constraints, a wrong inverse, malformed
types, source drift before executable loading, typed-receipt corruption
and overwritten evidence; an optimized Git-free relocated replay leaves
all package bytes unchanged. The independent checker also exhausts the
binary input cubes at ranks one and two and 625 bounded rank-one inputs
for the changed exactness-domain control. All proof-relevant checks remain
active under Python optimization.

`RESULT.json` is a deterministic finite receipt. Ordinary replay is
read-only; `verify.py --write` creates an absent receipt exclusively.
There are no network, third-party-package or Git-history runtime needs.
SOURCE metadata records the fixed scientific base and predecessor bytes;
future selected-frontier changes are provenance, not runtime inputs.

## Sources, credit and limits

Scientific base: `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision
6, selected-record SHA256
`bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`.
The existing [canonical lifting investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18983457)
coordinates this distinct obligation. TASK.json records the changed card
scope and bounded next questions. The independent inverse extractor and
restricted-source-update batch obligations are separate.

Credit Tekalign for PR3025/3033's fixed lifted word; Nick Petalas for
PR3035/3037's forward lattice and full-period theorem; Arham Tahir for
[PR3046](https://github.com/CrocSwap/integer-mult-bounds/pull/3046)'s inverse
image/permutation; Ross Richardson's PR3043/3059 reducer and consumer limits;
and the original P104/native/geometry lineage retained in those works.
The two unmodified source copies and original Git/SHA256 pins are retained
under vendor/. This package adds the common-invariant entrance, its exact
finite index, independent congruence calculation and caller closure tests.

Prepared by Ross Richardson with substantial OpenAI Codex assistance,
including a separate mathematical specialist. Apache-2.0. Separate
automated review is not independent human review. The inherited maximal
period theorem is a written source premise, not a new formal proof here.
No native-wrapper compiler, full P104 consumer, all-size implementation,
physical tape/precision invoice, selected cold replay or hosted CI pass
is claimed.

The verifier is a finite managed-Python reference: rank<=7, matrices have
at most 256 columns, test coefficients have at most 4,001 bits, and JSON
receipts are capped at 100,000 bytes. Managed allocation, test-only dynamic
module loading and temporary copies are explicit deviations from a fixed
finite-tape implementation. These limits bound the checker, not the
written all-rank invariance argument.

## Open next questions

Specify one complete consumer and its exact codec/intertwining map, then
trace every phase, quarter ADD and completed transform through declared
boundary lattices and a complete physical/recursive bill. The explicit
closure failures and unknown codec/backend costs block that transfer.
Alternatively, a larger integral-prefix exactness domain changes the
Gamma premise; first name the consumer and price its compatibility before
launching another index or circuit census. This package does not carry
out that broader investigation.
