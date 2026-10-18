# CK target forests: arbitrary dyadic numerators do not lower the floor

**Scoped negative complex-supplier result; no new κ.** The historical PR626 CK
single-parent target-forest floor remains **16,364 primitives per real component**
when each edge may use **any nonzero dyadic rational**, not just a signed power
of two. The existing PR816 witness attains this floor. No new circuit saving,
selected-supplier admission, runtime improvement or global circuit optimum is
claimed.

This closes the explicitly unexamined non-power numerator class in
[Gareth Davidson's PR964](https://github.com/CrocSwap/integer-mult-bounds/pull/964).
It credits and adapts the universal tail reduction and forest-exchange argument
from [woklerx's PR961](https://github.com/CrocSwap/integer-mult-bounds/pull/961),
which checks the **different X4 matrix**, not this CK matrix. The new evidence
is the complete CK all-dyadic finite core, including a concrete reason the
stronger root-only domination argument from the power class cannot be reused.

## Exact evidence and reproduction

From the repository root, Python 3.10+ and the standard library suffice:

```sh
python3 -I -O -B research/ck-all-dyadic-forest-seed23/verify.py && python3 -I -O -B research/ck-all-dyadic-forest-seed23/independent.py
```

Expected output:

```text
PASS_CK_ALL_DYADIC_FOREST cases=13501152 floor=16364 margin=63 columns=716x2 controls=10 no_new_kappa
PASS_CK_PACKED_ORACLE cases=13501152 exact_lane_bits=20 full_receipt_match
```

The finite core covers all **12,432 ordered distinct target pairs** and **1,086
coefficients** `n/8`, `1 <= abs(n) <= 543`: **13,501,152** cases, of which
**13,476,288** are nonunit. The core's minimum excess over the cheaper same-parent
signed-unit/root alternative is **63** component primitives; a witness is
child123, parent125, coefficient `-3`. This margin is a finite-core statement,
not a claimed uniform bound on the infinite tails.

Root-only domination is false: child114, parent184, coefficient `-3` costs
**116 less than making child114 a root**, while still losing to a same-parent
signed-unit alternative. This is a concrete counterexample to extending PR964's
root-only comparison unchanged, not a counterexample to its correctly scoped
power-of-two theorem. There are **941** finite nonunit directed
edge/coefficient cases beating their root. `EXPECTED.json` records the exact
complete margin histogram, root-winning census, witness tie-breaking, and
per-histogram cost stream digest.

The primary implementation uses gcd-reduced rational prices, sparse ordered
coefficient histograms and 16-bit packed cost vectors decoded by `struct`. The separate
oracle reads the dense CK matrix afresh, uses integer repeated division for
prices, and extracts 20-bit lanes by masking. Both check explicit no-carry
bounds; they share the histogram/packing idea, not implementation code. The
oracle reproduces every certificate field in the finite census, including
the full cost-stream digest. These are two AI-written implementations, not
independent human review. All 4,409 possible finite-core scalar coefficient
numerators receive a separate literal binary-Horner operation-count check.

Dense Prim and all **12,544** signed-unit/root cycle inequalities recheck the
existing attaining witness. Exact sparse dyadic-integer replay checks **all 716
arbitrary input columns in both orientations**, both for the original unit witness and
for a mixed nonunit forest with all106 parent edges changed, including overlapping
ancestor/descendant branches. Ten controls reject missing or misordered boundary
work, wrong signs, stale residuals, overstrong root/alphabet claims, non-dyadic
inputs and an invalid denominator-tail threshold. Private work is initially
cleared and finally cleared by the explicitly charged lowering; the panel
replay is on logical registers, not a fresh native primitive/frame emission.

`--record` explicitly regenerates only this package's receipt. Default execution
compares every regenerated receipt field and never writes research artifacts.
This is complete deterministic coverage, not a timed optimizer or a failed search.

## Cost class and proof

Let `C` be the frozen CK quarter-grid matrix, with 112 target rows and492 helper
columns. Its 8,704 nonzeros are `a/4`, where `0 < abs(a) <= 4`. The compensated
map is `(y,h) -> (y+C h,h)` with arbitrary initial target and helper dirt.

For reduced dyadic `q=n/2^d`, the retained independent binary-Horner lowering is

```
H(0)=0; H(q)=3+floor(log2(abs(n)))+popcount(abs(n))+d.
```

This includes initial coefficient-work CLEAR, numerator doublings and source
access additions, denominator halvings, signed target accumulation, and final
CLEAR. There is no cross-ADD work reuse. In particular `H(±1)=4`; this is the
historical tariff, **not** the stronger PR696 copy/unit tariff. Put
`R(v)=sum H(v_h)`.

Choose any acyclic one-parent target forest and any nonzero dyadic `lambda_i`
on each child. Execute `y_i -= lambda_i*y_parent` in leaf-before-parent order,
then the residual update `(TC)h`, then the exact reverse inverse shears. Because
parents still hold their original inputs during preparation, row i of T is
`e_i-lambda_i e_parent`, without ancestor terms. Therefore

```
T^-1 (T y + T C h) = y + C h.
root price: R(C_i)
child price: E(i,j,lambda)=R(C_i-lambda*C_j)+2H(lambda).
```

The bill is the sum of these local prices. Both preparation and restoration
are charged; arbitrary target dirt cannot be discarded. Children refer to the
original parent compensation row even when the parent has its own parent.
Inverse-transposition swaps logical gate endpoints and negates coefficients,
retaining order, so the same sign-invariant bill applies. It does not transpose
private CLEAR instructions.

### Universal tails (credited to PR961)

The maximum original cell price is eight:
`H(1/4)=6, H(2/4)=5, H(3/4)=8, H(4/4)=4`.

Write a reduced noninteger dyadic as `lambda=s*m/2^k`, m odd and positive.
If `k>=4`, a residual cell is `(a*2^k-s*m*b)/2^(k+2)`.
For `b!=0`, `v2(b)<=2<k`, so its numerator is nonzero and has exactly valuation
`v2(b)`, including when `a=0`. Its reduced denominator exponent is
`k+2-v2(b)>=4`. Thus its price is at least `4+4=8`. For `b=0`, the original cell
is unchanged. Every cell therefore costs at least its original price.

If `abs(lambda)>=68`, then for every `b!=0`,
`abs((a-lambda*b)/4)>=(abs(lambda)-4)/4>=16`.
For reduced `q=n/2^d` of magnitude at least16, `floor(log2(abs(n)))>=d+4`,
so `H(q)>=3+(d+4)+1+d>=8`. Again cells with `b=0` are unchanged.

In both tails the residual is no cheaper than the original root row, and
`2H(lambda)>0` gives **strict** root domination. Any dyadic outside both tails
has denominator exponent at most3 and magnitude less than68, hence appears
uniquely as `n/8`, `1<=abs(n)<=543`. The tails are universal written valuation
and magnitude arguments, not claims that finite distant samples prove infinity.
Starting the denominator argument at3 would be unsound: original cell `3/4`
with parent cell1 and `lambda=5/8` becomes `1/8`, with price7 rather than8.

### CK-specific finite inequality and forest exchange

The complete census verifies for every nonunit coefficient in the core:

```
E(i,j,lambda) > min(R(C_i), E(i,j,-1), E(i,j,+1)).
```

This is **not implied by the quarter alphabet**. A synthetic pair with100
copies of child entry `3/4` and parent entry `1/4` admits a cheaper coefficient3;
the checker retains this counter-control. Actual CK matrix information matters.

For any nonunit edge in any admissible forest, choose its certified cheaper
alternative. A signed-unit alternative retains the same parent; a root
alternative deletes the edge. Neither creates a cycle. Descendants retain
their original parent rows and local costs. Repeating removes every nonunit
edge, strictly decreasing the total bill. The resulting signed-unit forest
has minimum16,364, checked by dense Prim and the pinned PR816 attaining tree's
cycle certificate. Because signed-unit forests are a subclass, the all-dyadic
minimum is the same. Every optimum in this precise class is signed-unit.

Nonunit edge prices are directed: applying an undirected MST directly to all
dyadic edges would be invalid. The exchange step comes **before** using the
signed-unit undirected graph. The bound says nothing about arbitrary multi-parent
systems, arbitrary sequential shears, helper-basis changes, different lowering,
shared coefficient work, changed frames, or folded boundary work.

## Provenance, selection and single pivot

Base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`; OS assignment seed23,
complex-supplier track. `CLAIM.json` records three candidates and the single
pivot. The initial powers-of-two idea was abandoned on discovering PR964's
stronger existing exclusion; none of that duplicate is presented as new work.
The seed selected this track/object, not a different random replay.

At the base, the selected reviewed conditional κ is
`836330098538459/500000000000000000 = 0.001672660197076918`, PR1094 with PR589/555.
We followed its selected record to `community-frontier1094-audit/ASSEMBLY.json`,
source manifest and `docs/research/community-batch1099-review.md`; the complex
side is binding. This historical CK result is **not** a new selected witness.
The ledger and live PR bodies were checked, including PR816/917/961/964/1080/1081.
PR1081 changes helper pairs under two tariffs; PR1080 changes the U8 two-sided
forest. Neither is composed with this fixed CK matrix result. There was no
pinned coordination issue; discussions1163/1166/1167 had no entry claims, and
a narrow local claim was reserved with the coordinating parent.

`SOURCES.json` binds the two consumed runtime files by immutable bytes or
decompressed payload. The main checkout's source packages, selected frontier,
and `upstream/` are unchanged. Rooted-forest preparation, the existing circuit
and its66,520-real-primitive saving remain predecessor contributions.

No full native re-emission, fresh whole-program prefix/precision check, global
owner/invoice/outer assembly, selected cold replay, full repository suite,
Lean theorem, hosted CI success or production integration is claimed. The
unchanged outside work and recursive children cancel in this local exclusion;
there is no improved fully paid recursive moment to feed into a new κ.
All-size/compiler, realization, hosting, precision/tape/exact recovery and
analytic assumptions remain inherited. This is not formal verification of
the full multiplication theorem.

## Attribution and license

Prepared by **Adam Gall (@adamgall)** with substantial **OpenAI Codex assistance**
in research, implementation, proof, controls and writing. Apache-2.0 under the
repository license. No independent human review is claimed.

Credit **Gareth Davidson (@bitplane), PR964**, for the CK power-weight boundary;
**woklerx, PR961**, for the all-dyadic tails and forest-exchange method on X4;
**@dd-hemant, PR816**, for CK target forests and the attaining witness;
**ToikY, PR909**, for quarter-grid tail methods; **Oscar Fennell, PR759**, and
**Sricharan Vagvala, PR749**, for restored forest/pair predecessors;
**Ross Richardson, PR917/932**, and **David Awad, PR807**, for related compensation
work; and **Chafik Boukhalfa, Jeremy Kothe, icekylinx, DreamingOfClouds, eumemic**
and the retained source contributors for the CK supplier/compiler lineage.
All original notices and source licenses are preserved in place.
