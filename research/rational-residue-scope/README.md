# Exact rational borrowing: numerator and residue contracts

**Research consolidation with an exact comparison construction; no new κ.**
This makes the representation boundary between Ali Romman's PR1135 exact-lift
comparison and Gareth Davidson's PR1159 residue backend explicit and executable.
Neither predecessor is contradicted. PR1135 already limits its numerator-width
claim to its representation and excludes denominator-cancelling kernels.

Exact rational factors with **odd reduced denominators** act on binary residue
registers. When their completed map is integral, an endpoint bound recovers the
integer output. The unchanged PR1057 word and PR1159 backend then restore every
dirty bit pattern. Coefficient inverses, conversions, tables and source routing
are additional paid work. This does not implement rounded rational leaves or
decode arbitrary nonintegral outputs.

| Source / representation | Required boundary | What its result does not imply |
|---|---|---|
| PR1057 additive borrowing | Exact additive child shears; restored private dirt | Arbitrary deterministic or rounded children need not satisfy it |
| PR1135 rounded restoration | No wrap; same-grid rounded maps; stated translation/summary contract | Its scoped obstructions do not exclude every changed representation |
| PR1135 common numerators | Coarse inputs embedded with denominator `q^D`; sufficient numerator and product headroom | `q^D` is not an unconditional lower bound for cancelled factors or residues |
| PR1159 integer residues | Integer factors; residue boundaries; integral bounded endpoint | Signed decoding alone does not recover a nonintegral rational |
| This comparison | Odd reduced denominators; exact rational factors; integral bounded completed map | Even denominators, rounded substitutions and general supplier admission remain outside scope |

## Fixed source-bound example

Take the **52 integer matrices and 1,376-call word of PR1159**. Multiply the
even-indexed factors by `1/3` and the odd-indexed factors by `3`. These central
scales cancel in the ordered product without commuting any matrices. The
complete product is exactly the original integral matrix. Intermediate factors
and data are rational. Input and initial-output bounds remain seven, giving

```text
R = 7 + 7*2^52 = 31525197391593479 < 2^55.
```

Thus the residue data still use **56 bits**, with three dirty length-two arrays,
one source array, one output array and the same four private work registers.
The following comparisons distinguish bounds from minima:

| Quantity on this fixed word, both directions | Certified value |
|---|---:|
| Formal noncommutative prefix degree D | 65 |
| Generic common denominator `3^D` | 104 bits |
| Least common denominator of all actual rational prefix coefficients | **9** |
| Sufficient common-numerator data width using denominator 9 | **94 bits** |
| Sufficient common-numerator data width using `3^65` | 194 bits |
| Residue data width from the endpoint guard | **56 bits** |

The numerator bounds cover source/output magnitudes at most seven and dirty
integer entries of magnitude at most `2^55`. They concern data registers;
numerator products, initialization and division need their own workspace and
costs. They are not minimum bit-width claims. The least denominator **is** exact:
all formal prefix coefficients divide nine, and coefficient `-2584/9` at forward
leaf 80, row 8, column 0 forces a multiple of nine. The conservative `3^65`
comparison is not presented as necessary for this instance.

Four explicit executions use small and arbitrary signed 56-bit dirty values,
in both directions. Every literal leaf agrees with a separate Fraction lift.
The latter reaches 90 signed numerator bits in the dirty stress fixture; all
residue data remain 56-bit patterns. The example is a representation tradeoff,
not a measured runtime improvement.

## Paid model

The unchanged kernel executes **52,292 commands**, including 13,760 reductions.
The added bounded-register preparation executes **2,406 commands**: 114 for
the two denominator inverses (including the trivial denominator one) and 2,292
for 208 coefficient conversions with all private clearing. Together these
parts execute **54,698 commands**. A multiplication command has its actual
width-dependent cost; this is not a machine-time estimate.

Both phases reuse the original **283-bit** private allocation, including the
112-bit product register. Data occupy 560 bits, residue coefficients 11,648,
the inverse table 112, and fixed-width original rational descriptors 1,040:
**13,360 model bits**, plus private work and the inherited 17,888-bit leaf-word
encoding. Preparation uses 836 explicitly routed accesses, 24,452 bit actions,
and 5,438,192 head-bit moves in the declared field layout. Including the kernel
gives 949,124 bit actions and 81,869,808 head-bit moves. These counts price the
declared external-field scans; private arithmetic and its routing are the
primitive cost terms from PR1159.

**Additional costs remain explicit:** admission, rational descriptor validation
or normalization, source/input conversion, final signed decoding, program and
preparation-control dispatch, original input storage, and a physical tape
adapter. The verifier's generic integrality admission multiplies the complete
rational product (416 rational multiplies and 416 adds here). If used online,
its coefficient-height cost and product-matrix workspace must be paid separately.
The fixed central-scaling family also has the written integrality proof below;
an offline proof is not a claim of free runtime certification for arbitrary
inputs. [PROOF.md](PROOF.md) gives the conditional full cost expression and
the priced preparation's descriptor-size restriction.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -I -B research/rational-residue-scope/verify.py
python3 -I -O -B research/rational-residue-scope/test_package.py
```

Expected marker:

```text
PASS_RATIONAL_RESIDUE_SCOPE: 52 rational factors; 1376 calls; 56-bit data; 54698 priced kernel/preparation commands; 144 small cases; no rounded contract or new kappa
```

The verifier regenerates [CASE.json.gz](CASE.json.gz) and compares the complete
deterministic [EXPECTED.json](EXPECTED.json). It checks all ten formal columns
at every forward/reverse prefix, 144 smaller dimension/denominator/sign cases,
128 unit inverses, 120 nonunit exclusions and 65,520 quotient-addition cases.
Twelve mathematical/admission/price corruptions reject. Three concrete
counterexamples distinguish nonintegral signed decoding, rounded evaluation
despite an integral ideal product, and actual nested dirty-helper corruption.
Eight package tests include real subprocess mutations and recompression.

Use `--output /absolute/new/path --receipt /absolute/new/file.json` to retain a
regenerated case and receipt. Outputs must be new; sources are never regenerated.
The complete receipt agrees between CPython 3.14.4 and a read-only relocated
3.12.3 run with `-I -O -B`; see [VALIDATION.md](VALIDATION.md).
The optional [VERIFY.json](VERIFY.json) registers these same two commands for
the repository's bounded Python 3.12 replay hook. It can be run locally with
`python3.12 scripts/research_package.py --package research/rational-residue-scope`.

## Open next questions

The structured questions and blockers are in [TASK.json](TASK.json).

1. Does a useful exact segment of a selected supplier satisfy the odd-denominator
   and integral-boundary contract? This determines whether the comparison helps
   an actual supplier. First extract the rational coefficients of PR1094's
   retained scalar A segment, record their reduced denominator valuations at
   two, and check its exact boundary on formal columns. Even denominators,
   rounded/irrational leaves and nonintegral boundaries need another interface;
   physical admission and complete paid costs would still be required.
2. Can a structured integrality certificate cost less online than forming the
   complete rational matrix product? Admission cost and workspace can offset
   data-space gains. First emit and price a certificate for the central-scaling
   family, including descriptor reads and normalization. No generic cheap
   integrality certificate is supplied here.

## Provenance and remaining work

Consolidation seed **99**, drawn before detecting the revised task gist; the
already assigned task was retained. Base:
`1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`. Scoped coordination is in
[Discussion 1202](https://github.com/CrocSwap/integer-mult-bounds/discussions/1202).
[CLAIM.json](CLAIM.json) records alternatives and limits; [SOURCE-PINS.json](SOURCE-PINS.json)
pins 20 files from PR1057, PR1135, PR1159 and the selected context. The sources
are preserved byte for byte, including notices and licenses.
Submission is based on `49b3157d1d89adcef16df8be98445451672be5ba`, with the
experimental inputs unchanged. [SOURCES.json](SOURCES.json) preserves the
originating card/context provenance for the optional replay hook. TASK records
the changed scope: the executable comparison is broader than a pure navigation
edit. The final overlap snapshot covered all 836 open PRs (through PR1228), all
six Discussion threads and their comments, and local package notes. No matching
borrowed-word unit-denominator comparison was identified under the declared
search terms; this is not a novelty certificate. PR1199/1203/1205 concern deferred
readers and PR1211 prices a different balanced factor tape.

This neither replays all of PR1135's rounded-leaf experiment nor changes any
predecessor disposition. The selected PR1094 frontier and PR589 supplier stay
unchanged. PR1164 changes echo arity and remains a separate contribution;
PR1155 changes batch restoration. This uses neither mechanism. Existing
all-size/compiler, common-label, hosting, precision/tape and analytic
obligations remain. No supplier, complete multiplication algorithm, arbitrary
rational reconstruction, or rounded-interface repair is supplied.

Prepared by **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance**. Credit **Ali Romman PR1135**, the retained PR1057/1159 lineage and
the classical localization/Newton-inversion principles. No algebraic priority,
subagent review or independent human review is claimed. Apache-2.0.
