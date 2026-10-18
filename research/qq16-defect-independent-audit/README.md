# Independent QQ16 defect audit and a 20-bit feedback guard

**Result:** a separately written, JSON-only reverse-covector interpreter
corroborates PR2628's completed-instruction error envelopes at **all 2,680
initialized changed-field boundaries** of PR2540's unchanged 2,463-event word.
It also checks all five envelope metrics for all **464 final fields**.
The same certified feedback inequality permits a **20-bit** sufficient guard,
one bit smaller than PR2628's conservative 21-bit guard. The original guard is
correct. This is a scoped precision implication, not a decoder modification,
physical rounding format, supplier admission or new kappa.

## Exact sources and added value

Base: canonical main `b4560d9e7216f72b73c5aa940ac099c05e33ccf9`, priority
revision 5. The sole selector nonce was `7895d4b19cc7dc36ccded3c9bb293ae6`.
The recursive-interface card was changed to this independent precision audit
after live overlap found the newer precision results. See `TASK.json` for the
scope change, overlap coverage, stopping rule and structured next question.

- [PR2628](https://github.com/CrocSwap/integer-mult-bounds/pull/2628), ywz65,
  `e64a7babb285f22baeee89a9d88f5e79c512909a`, supplies the stability contract,
  unitary-frame argument, claimed envelopes and 841 transient witness.
- [PR2540](https://github.com/CrocSwap/integer-mult-bounds/pull/2540), ywz65,
  `630d557af5088f66b45c447969cee9576600e50b`, supplies the literal decoder word
  and its exact native/frame premises.
- Main's `research/joint-query/certificate.json.gz` supplies the 104 actual
  current-chart owner maps. Its immutable SHA-256 is
  `a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7`.

`SOURCES.json` pins the pending snapshots by commit, original path, Git blob
and SHA-256. No predecessor Python code is vendored, imported or executed.
The source proof and result are retained verbatim with their attribution.
The independent checker reconstructs every cut by reverse covectors; the
predecessor's forward computation and selected reverse checks are credited,
not presented as new methods. This audit extends independently implemented
reverse coverage to every initialized changed-field boundary, and adds the
exact uniform-guard calculation.

## Domain and verified envelopes

Use PR2628's norm: the maximum over owners of individual payload Hilbert
norms, at every positive payload tensor depth. There are sixteen earlier and
224 current temporal entries, each bounded by B. They are treated independently;
this favorable-to-analysis relaxation includes actual correlated observations.
It does not supply the entry bounds or the intervening F0/B1 execution.

At the completion of each ADD, native line/stage or cover map, the destination
may receive an arbitrary additive defect, including a state-dependent one.
Owned CLEAR, control, addressing, wrappers and the frame identities are exact
premises. Initial owned dirt and newly allocated private dirt are unbounded
until their first CLEAR; no bound is claimed for these uninitialized fields.

| Envelope | All initialized cuts | Final fields |
|---|---:|---:|
| Temporal input coefficient P | 240 | 121 |
| Unit absolute-defect coefficient A | 1,529 | 818 |
| State-relative weighted coefficient K | 2,298 | 1,253 |
| Native defects only | 192 | 96 |
| Cover-map defects only | 280 | 140 |

All five all-cut maxima occur in scratch F0 after zero-based event 1717.
The 2,136 distinct defect sites comprise 1,688 ADDs, 224 rank-one lines,
sixteen rank-eight stages and 208 cover maps. The complete local trace digest
and final-envelope digest are in `RESULT.json`.

## Why the independent check proves the finite envelope

Retain PR2628's logical-frame reduction: native/frame operators are unitary;
the correctly aligned cover maps become isometric owner pullbacks. This audit
does not recompile the native kernels or prove their physical frame identities.

For a queried field at a cut, initialize its covector to the identity owner
operator and walk the actual word backwards. At `dst += a*src`, retain the
destination covector and add `a` times it to the source. At a cover action h,
a covector g becomes g*h, in that order. Native frame changes preserve the
logical covector. An exact CLEAR kills only its destination's covector.
The temporal boundary extracts the 224 current-entry coefficients while
preserving every retained R coefficient. Uninitialized owned/private dirt
must have zero sensitivity.

At every defect site, record that destination's current covector before
undoing the instruction. This is exactly the site's coefficient in the
queried result. Equal owner matrices within a site are combined with exact
rational signs before taking absolute values. Distinct sites remain distinct.
Sum these absolute values for A; weight an ADD site by `1+abs(a)` and every
native/cover site by one for K. Restrict the sum to the appropriate site kinds
for the other two defect metrics. The same row sum over temporal entries is P.
The triangle inequality and owner isometry establish the stated envelopes.

The checker starts a fresh reverse traversal for **every** changed-field cut,
including all 224 temporal replacements and zero results of CLEARs. Unchanged
initialized fields retain their preceding bound, so these cuts plus the
initial entry bound cover every initialized prefix state. All final fields
are compared individually with the source receipt. This checks sufficient
coefficient envelopes, not their sharpness as physical operator norms.

## The smaller sufficient guard

With the predecessor's state-relative defect premises and finite-run maximum
initialized operand/result norm M, the verified P and K imply

```
M <= P B + K u M,
error/B <= P K u / (1-Ku),       Ku < 1.
```

For an integer b>=0, substitute `u <= 2^(-b-g)`. The sufficient condition
`error/B <= 2^-b` is

```
P K + K 2^-b <= 2^g.
```

Its strongest case is b=0. Here
`K(P+1) = 2298*241 = 553818`, strictly between `2^19` and `2^20`.
Consequently **g=20 works for every integer b>=0**, with a positive feedback
denominator. At b=0 the bound is `275760/523139 < 1`; with g=19 it is
`55152/52199 > 1`. Thus 20 is the smallest uniform integer guard obtained by
this particular sufficient feedback inequality. This does **not** prove that
19 bits, a different analysis or a physical implementation must fail.

## Behavioral evidence and reproduction

From the repository root, standard library only:

```sh
python3.12 scripts/research_package.py --package research/qq16-defect-independent-audit
python3.14 -I -B -O research/qq16-defect-independent-audit/verify.py
python3.14 -I -B -O research/qq16-defect-independent-audit/test_verify.py
```

The first command runs metadata/source validation, the complete audit and
nine behavioral control groups. Direct `verify.py` is read-only; `--write`
creates an absent local receipt and refuses to overwrite one. Acceptance
checks remain active under `-O`.

A separate numeric interpreter reproduces the source's signed-defect 841
interior witness. It uses the actual invariant constant-owner, constant-payload
subspace: permutations and native C operators fix the normalized constant
payload vector. Collapsing each peak site's owner coefficients determines
one signed unit defect at that site; the literal scalar execution reaches
841 at F0. Hence a final-only envelope of 818 really can miss an interior
error; 1,529 is still not claimed attained. This witness is corroboration of
PR2628, not a new counterexample.

Other controls verify that capture errors cross the temporal boundary,
cleared accumulator errors still reach 56 outputs, and a borrowed native-line
error survives its nominal inverse. Noncommuting binary owner maps distinguish
composition order; a tiny cancellation example distinguishes signed merging
from premature absolute values. Early capture after B1, an uncleared owned
output, and a corrupted source snapshot must fail. Exact feedback substitution
checks b=0 and large b without floating point.

Local validation used CPython 3.12.14 and 3.14.7 on macOS. No independent human,
proof-assistant, hosted-CI or selected supplier cold-replay pass is claimed.
The registered replay, optimized replay and control commands passed; an export
containing only this package and its declared certificate also passed read-only
without Git or source executables.

## Remaining obligations

This audits the coefficient/feedback implication under the declared native,
frame and exact-owned-CLEAR premises. It does not independently replay F0/B1,
compile native children, establish entry bounds, admit finite component
rounding, or price retention, movement, hosting and restoration. Borrowed
restoration under defects remains approximate. No selected frontier, frozen
source, word, invoice or recursive profile is changed.

## Open next questions

Can an actual rounded rank-one child realize the 20-bit completed-instruction
defect allowance? Start by bounding one child's internal errors and converting
component rounding to the per-owner payload Hilbert norm. This is needed to
turn the conditional relative-error allowance into a physical format and cost;
entry/B1 numerical bounds and restoration remain blockers. The structured
version is in `TASK.json`; this audit does not start that implementation round.

## Credit and license

Credit ywz65 for PR2511/2512/2540/2603/2628 and the error contract, and the
PR2096/2166/2503 Hilbert-defect/feedback lineage. Credit Ali Romman for QQ16,
thakrarsagar for L2/native/retention work, starship-s for the cut/F0 decoder,
Ross Richardson for the retained observation-contract work, and all credited
geometry/native/supplier predecessors. The elementary reverse linear-algebra
and feedback manipulation are standard.

New independent checker, controls and guard refinement by **Arham Tahir** with
substantial **OpenAI Codex** assistance in derivation, inspection,
implementation, testing and writing. No subagents or independent human review.
Apache-2.0, retaining the source documents' notices.
