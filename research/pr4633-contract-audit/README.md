# Endpoint-preserving repair bounds for PR4633

**The submitted quotient screens do not establish a new κ.** This audit reviews
PR4633 at `b390d64abfcdba1a3816b86fc763cbc95d43c12c` and keeps every submitted
package unchanged. The GitHub headline describes kernel 150 and BIT 0.012401086416;
the checked commit actually ships kernel span{150,102,255} and BIT screen
0.032249423394893. Both variants are checked here, along with the stacked complex
kernel-153 artifact. This is a finite audit, not a full multiplication theorem.

The publication package is based on canonical main and vendors six exact inputs
from the reviewed PR under `vendor/`; `VENDORED.json` records their original
paths, commit, Git blobs and SHA256 hashes. The vendored Python files are
unchanged. The audit binds the copied builder's `SOURCE` path to the original
PR589 source directory before calling it. `SOURCES.json` pins the remaining
inputs from main. Every audit input is available in the publication checkout.

## Overlap and the contribution here

The publication overlap check found [PR4636](https://github.com/CrocSwap/integer-mult-bounds/pull/4636)
at `b0a325a3e312b7c5ebceb420de4b8cb13181f43e`, which already supplies a broader
negative audit: rational-field counterexamples, endpoint failures, verifier
false positives and full scan discrepancies. Those objections are prior
concurrent findings; the endpoint and field checks below provide reproducible
context for this package's repair tests.

This package contributes the exact **636-frame contraction obstruction**, the
**general hyperplane-dimension obstruction for global full-image padding**, and
the **endpoint-preserving expansion candidate and its failed price**. PR4636's
README and both short verifiers were inspected at that head; no equivalent
repair-bound certificate was found in that scope.
[PR4642](https://github.com/CrocSwap/integer-mult-bounds/pull/4642), at
`d8c59e36a8efb301f0298871218cfe00f4e043f7`, independently audits complex re-padding
and its invoice. Its ledger corrections are separate from the repair bounds
here. `OVERLAP.json` records the bounded search coverage and exact related heads.

## What reproduces

The submitted BIT and complex verifiers reproduce their committed RESULT.json
files exactly. Their metadata/source-pin checks also pass. Logical maps, owned
cleanup and replay against the artifacts' own endpoints are consistent. Those
checks do not verify that the resulting physical local calls are the operators
used by the controller. `PASS` below means the audit detects that mismatch.

The controller's `replay_events` multiplies both fields of every LOCAL call by
the same stage symbol. Its `inventories` then credits all main outputs using
block 7 (BIT) or block 8 (complex), retaining a rank-one central factor. The
actual source contracts have X entrance P, X final full ambient, Y entrance
zero, Y final H, with P a line complementary to H. The original sources pass
these checks on every port. Checking these dimensions and complements allows
chart changes; it does not require equality of source frame labels.

## Finding 1: neither quotient satisfies its priced main-port contract

| word | main widths | ports meeting the invoiced contract |
| --- | --- | ---: |
| rational BIT source | {7:222} | 111/111 |
| BIT kernel 150 | {6:107,7:105,8:10} | 0/111 |
| BIT kernel span{150,102,255} | {4:103,7:70,8:49} | 0/111 |
| complex source | {8:224} | 112/112 |
| complex kernel 153 | {7:168,8:56} | 0/112 |

For complex kernel 153, 56 ports have widths (7,7) and a surviving central
complement; the other 56 have widths (7,8) and X entrance contained in Y final.
Neither type is the block-8 call priced by the invoice.

There is a general obstruction for the BIT builder's global full-image padding.
Let h be the original ambient dimension and K a nonzero k-dimensional kernel.
For a source hyperplane H, dim(phi(H)) is h-k or h-k-1. In the former case the
image is the full quotient and the builder re-pads it to dimension h. In the
latter case it remains dimension h-k-1 <= h-2. Thus **no Y terminal can have the
required dimension h-1**, for any nonzero kernel in this construction. This
rules out repairing the existing priced BIT contract by searching more kernels.
It does not rule out a new controller with different operator contracts.

The correct BIT rank-mass decomposition is:

| word | paid mass | main mass | helper mass | owned COPY mass |
| --- | ---: | ---: | ---: | ---: |
| source | 5129 | 1554 | 3512 | 63 |
| kernel 150 | 5023 | 1457 | 3512 | 54 |
| submitted three-dimensional kernel | 4842 | 1294 | 3512 | 36 |

Paid mass equals main + helper + COPY mass. Relative to the source, the
one-dimensional saving is **97 removed main ranks + 9 COPY ranks**, totaling
106. The submitted saving is **260 main + 27 COPY**, totaling 287. The increase
in the unchanged invoice's surplus is 18 times these totals. This slightly
corrects the earlier review's attribution of all 106 ranks to mains; the
contract objection still applies. No corrected complete invoice is asserted.

## Finding 2: BIT's GF(2) conversion changes the source geometry

The BIT source stores rational E8 frames. Its `frame_projectors` constructs
exact rational orthogonal projectors from B using B^t (B B^t)^-1 B. The quotient
builder instead reduces A's coefficients modulo 2 and takes a GF(2) nullspace.
These operations do not preserve the required incidence/orthogonality data.

An explicit witness is port 8:

```
u = (0,1,1,0,1,0,0,1)
H = {x : u dot x = 0}
u dot u = 4 over Q, but 0 modulo 2.
```

The rational entrance line is complementary to its terminal H. Its reduced
binary line is inside the reduced H. Even before applying any quotient, this
conversion leaves only 8 of 111 complementary pairs; the 111 distinct rational
entrance lines reduce to 22 binary lines. Matching every frame dimension and
recovering the old bill are insufficient calibration: those tests miss this
change in incidence. The source itself is not accused of this error.

## Repair attempts and what they establish

1. **Restore the source geometry through a monotone contraction.** For each
   rational source frame S, compute the span of all source entrance lines
   contained in S. This span equals S for **all 636 frames**, checked with exact
   rational elimination and A/B kernel-image consistency. If a framewise map F
   is monotone, fixes those entrance lines, and satisfies F(S) contained in S,
   then S is contained in F(S), hence F(S)=S. This entire contraction repair
   class therefore returns the original profile and screen 0.003464248972024.
   The lemma does not cover arbitrary resynthesis or role-dependent retiming.
2. **Expand frames while preserving all endpoints.** Replace S by the
   intersection of all source Y hyperplanes containing S (full ambient if
   there are none). This is a monotone expansion; all 661 start/final endpoints
   remain exactly fixed. It changes 36 frames and replays both logical
   directions. Its paid mass rises to 5138, surplus falls to 591, and the same
   screen drops to approximately 0.002750034070107. It is rejected as a repair
   before native lowering; native realizability is not claimed.

These checks supply no profitable repair of PR4633. A valid replacement would
need a different physical construction/controller and a fresh complete invoice.

## Finding 3: the outer admission is also missing

The two-constraint roots are supplier screens. They do not supply the ordinary
BIT conversion and full outer chain. The pinned query-thinned verifier separately
uses before/after cover savings, an old atom, an admitted BIT saving, and all
strict outer predicates. The submitted packages do not replace that chain or
replay it at a larger value. Increasing declared constants would require proof
of their hypotheses, including a supplier implementing the actual LOCAL operator.
The large outer value in the GitHub title/body is therefore unsupported as well.

## Reproduce

From the repository root, with CPython 3.12 and only its standard library:

```sh
python3 -I -B research/pr4633-contract-audit/verify.py
python3 -B scripts/research_package.py --package research/pr4633-contract-audit
```

The first command authenticates 19 inputs, checks the original source as a
positive control, recomputes both BIT logical replays and their contracts,
checks the stacked complex source/quotient geometry, proves the bounded
contraction obstruction, prices the expansion, and rejects five mutations:
wrong MOVE rank, dependent basis, changed source entrance, omitted source ADD,
and spoofed width metadata. The expected marker is
`PASS_PR4633_CONTRACT_AUDIT_NO_NEW_KAPPA`.

`RESULT.json` is the deterministic audit receipt. Float roots are labelled as
screens; only ranks, counts, incidences and source pins are exact claims.
The full submitted complex logical replay was independently rerun during the
review; this audit's registered command reconstructs its source and checks its
endpoint geometry, without repeating its full physical lowering.

## Open next questions

- Can an alternative local word preserve the invoiced operator while reducing
  the paid moment? Start with the original rational BIT frames or original
  complex endpoints and check them independently before pricing. The present
  global quotient with full-image padding cannot do this.
- Can a different controller use the quotient operators? Derive each actual
  main operator, its central factor and stage ranks, then factor the controller
  and reprice all outputs and idles. The existing block-7/block-8 invoice cannot
  be reused. This is a new construction, not a literal-constant repair.
- Any eventual supplier improvement still needs ordinary BIT conversion and
  the complete outer admission with strict predicates and sound source pins.

## Credit

DaysSky supplied both quotient packages (#4633 and #4629), built on
DreamingOfClouds's PR589 BIT word and the retained eumemic lineage, and Cinna
Davis's PR4470 complex construction on the credited zxv supplier work. The
endpoint concern was raised by pinterbanget (#4604), the quotient-kernel census
by Nick Petalas (#4627), and the per-port controller-contract audit by Rohan
Arun in his PR4633 comment. This audit independently checks those concerns,
adds the rational/GF(2) witness, covers the actual three-dimensional artifact,
corrects the COPY/main rank attribution, and bounds two repair routes. The
broader independent audit in #4636 already establishes the rational-field,
endpoint and verifier objections; this package's publication focuses on the
complementary repair bounds described above.

Prepared for Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
This package changes no selected-result record and claims no new κ. Its local
checks and publication status are separate from maintainer acceptance.
