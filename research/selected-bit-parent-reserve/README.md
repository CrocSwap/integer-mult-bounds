# An explicit parent reserve for the selected BIT bootstrap

Under the **retained full-cover and completed ordinary-leaf interfaces**, the selected PR589 nine-stage BIT stopped producer has the uniform parent-stock envelope

\[
\log_q S(e,w)\le 8194\,w(1+\log_2 e).
\]

This supplies the numerical coefficient in PR1965's H3 for the first native bootstrap stage. Its recorded cutoff passes that paper's sufficient stock-fit guard with `sigma=8194`. The result is a conditional space implication, not an implementation of the inherited interfaces, a proof of H2, a new supplier, a new exponent, or adoption of the outer proof.

The new step is the **selected-producer divisor/depth/restoration argument**, not another headroom calculation. The source pricer already contains the arithmetic `2*(64^2+1)=8194` as part of an outer row allowance. This package explains why that term bounds the stopped parent's stock when ordinary leaves are internally completed, and why the other outer allowances need not be inserted into it.

## Which producer is being bounded?

The source-pinned selected assembler in PR1094's `upstream1087.tar.gz`, member `code/assemble.py`, names PR589's ordinary BIT supplier, sets `BIT_L=9`, `BIT_T=32`, `BIT_M=1+7*BIT_L=64`, and binds the complete PR589 receipt by Git blob. The same file prices the **different** complex supplier at `m=73`. The bootstrap parameter is constrained by both savings, but the ordinary stopped producer is the BIT side.

| Source-bound quantity | Selected value |
|---|---:|
| Atom dimension `m=1+7L`, `L=9` | 64 |
| Live roles | 28,416 |
| Physical roles, including the nine additional work roles | 28,425 |
| Largest good child rank | 42 |
| Bad-class fallback child rank | at most 1 |
| Halving degree | 2, since `2*42^2=3528 < 4096=64^2` |
| Parent reserve coefficient | `2*(64^2+1)=8194` |

`research/e8-bit-p111-tuned/tune/EXPECTED.json` is the exact blob cited by the selected assembly. The vendored PR510 `assemble9.py` reads the hosted profile and computes `row=DEPTH*(m*m+1)+9909+252=18355`. The selected `adapt9p.py` changes the port/deficit binding, not this row formula. `emit_k.py` records `physical=LIVE+9`. These are authenticated source statements, not a new cold replay of PR589's circuit.

The historical five-stage `m=120` coefficient 57,604 is not used. Neither is 252 treated as a measured selected leaf reserve. PR1990 correctly leaves a selected binding open; the BIT/complex distinction is material when closing this particular ordinary-bootstrap obligation.

## Retained hypotheses and exact domain

Fix one eligible odd prime `q>2^80`, avoiding the selected recipe's finite denominator/rank exclusions, before choosing the widths. Let `e,w` be positive integers and let the coarse atom count satisfy `0<=n<=e`; at the native stage of interest `w=ceil(e^s)` and the body has at most `floor(e/w)` atoms.

The proof uses the following inherited interfaces explicitly:

1. **Selected full-cover realization.** The selected `m=64` finite physical recipe is realized over `GL_64(Z/q^w Z)`, with one fresh complete physical-role packet per active coarse level. Its role packet has `P=28425` slots, including work roles. A sufficient level divisor is
   `W_q(w)=P*|GL_64(F_q)|*q^(4096*(w-1))`.
   The selected all-size/compiler and hosting assumptions are still required to identify these packet slots with the physical word. A finite receipt alone does not construct that identification.
2. **Fixed atom width along a coarse call.** An internal child has atom count at most `r*floor(n/64)`, where `r<=42`; the conservative bad-class compiler has children at most `floor(n/64)`. Calls with `n<64`, peeled remainders, routing and high-part exchanges use completed ordinary operations, rather than another same-level coarse call.
3. **Fresh fields and restoration.** A child can use only the unused quotient of its parent's row packet; already exposed ancestor fields remain complete spectators. Every child returns its supplied row coordinate unchanged. Successive residuals, the two-call ordinary wrapper and other sequential calls reuse restored stock.
4. **Completed leaves.** The previous ordinary algorithm handles all required widths and complete spectators, borrows its own high digits internally and restores its row coordinate. It needs **no additional externally supplied row factor**. This is the reviewed PR185 contract retained by PR387, not an estimate of the leaf's internal memory or running time.

The generic full-cover cardinality and fixed-width recurrence are in `three-stage-cover-bit.tex`, lines 197–218 and 253–264. That file's displayed geometry is historical `m=67`; its numerical parameters are **not** copied. The present proof derives the cardinality identity for general `m`, then instantiates the selected `m=64` recipe under hypothesis 1. The reviewed PR185 proof, paragraphs “Nested row restoration and fixed tapes”, provides hypothesis 4. The original rows note's inherited old-leaf factor must not be retained a second time when its use is replaced by this stronger completed interface.

## Reserve theorem

### 1. Charge the entire level divisor

Reduction modulo `q` maps `GL_m(Z/q^w Z)` onto `GL_m(F_q)`. Every invertible residue matrix has exactly `q^(m^2*(w-1))` lifts; a matrix over this local ring is invertible exactly when its reduction is. Consequently

\[
|GL_m(\mathbb Z/q^w\mathbb Z)|
=|GL_m(\mathbb F_q)|q^{m^2(w-1)}<q^{m^2w}.
\]

Because the selected physical-role count `P=28425` is smaller than `q`,

\[
\log_q W_q(w)<4096w+1\le4097w. \tag{1}
\]

The high-matrix cardinality does cancel in the normalized time moment, but **does not cancel here**. The nine additional physical roles are also included. The proof needs an actual divisible packet, not merely a numerical upper bound on its size: reserve powers below use `W_q(w)` itself. A substituted divisor with fewer high fibers is rejected by the controls.

### 2. Bound active depth, including floors and fallback

Write `D(n)` for the maximum number of internal coarse nodes on any root-to-leaf path; `D(n)=0` for `n<64`. Every child satisfies

\[
n'\le42\lfloor n/64\rfloor\le (42/64)n.
\]

A two-edge path therefore gives `n'' <= (42/64)^2*n < n/2`. Fallback children satisfy a stronger bound. After `2*ceil(log2 n)` edges a positive integer atom count would be below one, so the path has already stopped. For `n>=2`,

\[
D(n)\le2\lceil\log_2 n\rceil;
\]

for `n=0,1` it is zero. Thus in all cases with `n<=e`,

\[
D(n)\le2\lceil\log_2\max(1,e)\rceil
\le2(1+\log_2 e). \tag{2}
\]

No unnamed additive `O(1)` is used. One-level halving is false: `n=128` permits the selected rank-42 child `84>64`.

### 3. Construct divisible stock, not a product over all calls

For the same fixed `w`, define

\[
S(n,w)=W_q(w)^{D(n)}.
\]

At a coarse node with depth `d>0`, split a complete row index into its role remainder modulo `W_q(w)` and an unused quotient of size `W_q(w)^(d-1)`. Every child has depth at most `d-1`, so that quotient is divisible by its required reserve. Any excess quotient is an additional complete spectator. Because the child restores its row, the quotient can be reused for each later child. The node's complete endpoint restores its own exposed role field. Induction supplies all nested calls and restores the entire row.

At a leaf there is no external factor: the ordinary operation supplies its own borrowing under hypothesis 4. Consequently the recurrence is multiplication by **one level divisor along an active path**, not multiplication over siblings, residuals, the two wrapper calls, or bootstrap levels. This is also why the previous ordinary **time** constant does not enter the reserve. If a leaf instead needs external factor `B>1`, the base case becomes `S_leaf=B`; the zero-external conclusion no longer follows. That is a genuine hypothesis, not something finite examples can infer.

Combining (1) and (2), for the parent construction at every integer `e,w>=1`,

\[
\log_q S(n,w)<4097wD(n)
\le8194w(1+\log_2 e).
\]

Use non-strict `<=` to include the zero-depth case. This is PR1965's H3 with **sigma=8194** under the stated interfaces. At fixed completed bootstrap depth the same proof can be reused, but this package binds and checks only the first native stage. It does not claim a new implementation or all fourteen independently admitted stages.

## First native cutoff

From the selected assembly, with exact rational arithmetic,

```
s = min(bit_lower, (1-10^-24)*complex_lower) - 10^-27
a0 = 384599/10^10
a1 = (1-s)*s + s*a0
delta = min(s-a1, 1-a1-s, 1-a1-s*(1-a0), 1-s)
L = 4785575287428
```

The independently derived coefficient needs only `ell=ceil(log2(8*8194))=17`. The exact checks prove

```
L >= 2
L*delta^2 >= 36
L*delta >= 2*(4+17) = 42
0 < delta <= 1-s
```

These are PR1965's sufficient fit premises, so `k=ceil(log_q S(e,w))<e/2` for every `e>=2^L`, with `w=ceil(e^s)`. The inherited sufficient-headroom value `floor(L*delta/2)-4=6562783` is included only to show the comparison; it is predecessor arithmetic, not the novelty. The powers `2^L` and huge stock sizes are not materialized.

This closes the *numerical parent-stock coefficient implication* at this stage under the explicit full-cover/completed-leaf assumptions. H2's cutoff-independent stopped time bound, any other primitive fit condition, and all selected all-size/compiler, common-label, mutable-source, hosting, precision/tape, exact-recovery and analytic obligations remain. The selected result and frozen proofs are unchanged.

## Reproduction and evidence

From the repository root, using standard-library CPython 3.12:

```sh
uv run --python 3.12 --no-project python -I -B research/selected-bit-parent-reserve/verify.py
uv run --python 3.12 --no-project python -I -O -B research/selected-bit-parent-reserve/test_verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/selected-bit-parent-reserve
```

The verifier authenticates every external input before reading its semantic fields and authenticates the archive member before parsing it. No predecessor Python is imported or executed. It derives the selected parameters, complete level charge, exact halving and cutoff comparison; independently checks the floor-depth recurrence over 20,001 atom counts; and uses small exact local-ring matrices and row permutations as finite controls for the proof's failure modes. Acceptance uses explicit exceptions, not removable `assert` statements. The regenerated `RESULT.json` payload must compare canonically with the committed one. `--write-result PATH` creates an external receipt and refuses overwrite.

The finite fixtures support the argument but do not prove its all-width quantifiers; those are proved above. Neither a complete selected cold replay nor a formal kernel is run here. See [TASK.json](TASK.json) for scope, provenance and open questions, [SELECTION.json](SELECTION.json) for the unchanged selection, and [SOURCES.json](SOURCES.json) for exact byte pins.

## Open next questions

1. **Realize the retained interfaces.** Construct the selected all-size GL64 role-packet/compiler map with fresh descendant fields and complete spectator preservation. Begin with one parent/child split and the common-label/mutable-source mapping. This would replace hypothesis 1's inherited implementation assumption; the finite cardinality proof cannot do so.
2. **Complete the time implication.** Trace every routing, padding, weighted-leaf, descriptor and high-part-exchange toll to prove H2 whenever stock fits with a cutoff-independent constant. The first step is an explicit quantified stopped recurrence. H3 alone cannot adopt PR1965's outer-proof repair.

## Attribution and limits

DreamingOfClouds supplied the selected tuned P111 word and parameterized PR589 pipeline, on eumemic's PR555 base and DreamingOfClouds' PR510 nine-stage work, with the credited geometry, whole-call hosting and compiler lineage. The finite-cover/local-ring and reviewed PR185/PR387 completed-leaf sources supply the retained interfaces. Josie Elliston's PR1956 and PR1965 isolate the carried-constant problem and time/space repair; ToikY's PR1990 independently checks the headroom and insists on the missing selected-source coefficient. Rohan Arun supplied the selected PR1094 assembly on Jeremy Kothe's PR1087 predecessor. Their results and numerical receipts are not claimed as new.

Prepared by Adam Gall with substantial OpenAI Codex assistance. No independent human review or unconditional multiplication theorem is claimed. Apache-2.0, following the repository and retained source notices.
