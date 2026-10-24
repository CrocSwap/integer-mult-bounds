# Conditional kappa 0.00302728823 with a direct backward caller

This construction gives **conditional kappa = 302728823/100000000000 =
0.00302728823**. It improves the selected final
[PR #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610)
value 0.0030217758 by 0.00000551243. All 18 full calls use the completed
backward supplier from
[PR #5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383).
Two explicit caller wrappers replace the two forward calls. The backward
program, its eight relations and its owned storage schedule stay unchanged.

During this work, the separate
[PR #5392](https://github.com/CrocSwap/integer-mult-bounds/pull/5392)
reached the **same recursive profile** by circuit transposition. This package
uses direct conjugation of the full backward interface. It does not transpose
an instruction, a COPY, a CLEAR or a native phase recipe. Its bound exceeds
that PR's 0.00302725 by **3823/100000000000 = 0.00000003823**. That last increment
comes from a larger compiler threshold, not another paid-profile gain. This
is not a further paid-profile hill-climbing step beyond PR5392. The direct
wrapper is the distinct construction; the same profile gives the same ceiling.

[CONTROLLER.json](CONTROLLER.json) contains the literal caller.
[RESULT.json](RESULT.json) contains the exact finite evidence and full bill.
[SOURCES.json](SOURCES.json) binds each consumed input. The selected record
and all predecessor packages remain unchanged.

## Source, scope and coordination

The branch starts at canonical main
[1ec1119972c9aefe42525172d07b332fcff81cb4](https://github.com/CrocSwap/integer-mult-bounds/commit/1ec1119972c9aefe42525172d07b332fcff81cb4),
priority revision 7. The
[selected admission review](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/docs/research/pr-intake-evidence/pr4610/PROOF-REVIEW.md)
records the five inherited framework assumptions. That admission does not
cover this changed caller.

The local supplier is frozen at PR5383 commit
[4bd6efa51a495a7c7b7754915cf0244e7e60969e](https://github.com/aliromman/integer-mult-bounds/commit/4bd6efa51a495a7c7b7754915cf0244e7e60969e).
Its [native checker](https://github.com/aliromman/integer-mult-bounds/blob/4bd6efa51a495a7c7b7754915cf0244e7e60969e/research/kappa-joint-relations-20261023/native.py)
and [witnesses](https://github.com/aliromman/integer-mult-bounds/blob/4bd6efa51a495a7c7b7754915cf0244e7e60969e/research/kappa-joint-relations-20261023/WITNESS.json)
are copied without changes as runtime dependencies. Their bytes are retained
in this branch's ancestor `9078033224509f184e3da4ccfd9837d1e1ad314e`.
The metadata pins that ancestor and also records the original source pins.
A clean checkout needs no separate pending-PR fetch.

The verifier reconstructs the complete published local word. Its canonical
JSON payload hash is
`2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d`.
All 4,429 frames, 72 native maps, retained paid operators and owned operations
come from that source. Cao Yifan's underlying
[final native word](https://github.com/intqwq/integer-mult-bounds/blob/20bb93cd990d2ff683e4d0fc56b87a42cd5d3296/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz)
has decompressed SHA256
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
All eleven external runtime inputs occur in the recorded main base.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19154818)
separates this caller construction from the
[transpose claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19154367)
and the active
[backward paid-history search](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19154639).
The full open-PR and Discussion snapshot was refreshed during work. Targeted
Git-object searches covered relevant main README and proof text beyond the
sparse working tree. These checks do not certify novelty over all unpublished
or historical work. This package claims no source relation or transpose result.

## Direct caller identity

Use the source's
[normalized interfaces](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/query-thinned-controllers/PROOF.md).
On each port Q is the central Gaussian and D_s is the commuting stage
multiplier. At stage zero, D_0 is the nine-axis Gaussian times Q^-1.
At later full stages, D_s acts on eight fresh axes. Write

```math
B_s=D_s\begin{pmatrix}1&-Q\\0&1\end{pmatrix},\qquad
F_s=D_s\begin{pmatrix}1&0\\Q^{-1}&1\end{pmatrix}.
```

Define the two monomial matrices

```math
R=\begin{pmatrix}0&1\\-Q^{-2}&0\end{pmatrix},\qquad
R^{-1}=\begin{pmatrix}0&-Q^2\\1&0\end{pmatrix}.
```

Direct multiplication gives **F_s = R B_s R^-1**. In execution order, for
the two fields x and y, use:

```text
(x,y) <- (-y,x)
x <- Q^2 x
execute the unchanged complete B_s supplier
(x,y) <- (y,-x)
y <- Q^-2 y
```

The caller changes only the main fields. Each invocation keeps its own 400
independent productive helper inputs and the source backward helper boundary
normalizers. Its eight prepared pivots and nine owned center/snapshot fields
return zero. The wrappers do not read those fields. Thus the complete main,
helper and owned interface follows from the complete source interface, not
from a two-by-two identity alone. Helper normalizers are charged in the local
backward route allowance.

This proof needs no linear instruction transposition theorem. A completed
supplier with the same main map, independent helper contract and owned return
can use the wrapper even when its implementation is hidden behind that contract.

## Physical wrappers and tensor widths

For every source port q,

```math
Q=\frac{1+i}{2}I+\frac{1-i}{2}X_q,\qquad Q^2=Q^{-2}=X_q.
```

Here X_q is the native address translation. Its phase is exactly +1.
The verifier checks the Gaussian rational coefficients and every one of the
512 nine-axis input columns on all 112 ports at both changed sites.
It also checks the source phase polynomials, the orthogonal route and its
inverse, the preserved central direction and all four native boundary contacts
at **stage 0 and stage 32**. This gives **896 contacts** and **114,688 literal
central-square columns** in the full 265-axis layout. Stage zero uses its own
boundary formula; it is not inferred from a later-stage check.

At positive tensor width f, `(Q tensor f)^2 = X_q tensor f`. Every D_s commutes
with Q, so the matrix identity still holds after that substitution. Each scalar
minus sign acts on the whole field and stays outside the tensor product.
A signed swap uses three scalar additions and one scalar sign change. Each
translation uses the explicit address map. Neither wrapper needs a positive
Gaussian job or a new independent source.

The caller verifier replays every rational Laurent coefficient, with Q and all
33 stage variables formal and with no finite-order relation. It checks both
scalar boundary programs and all 32 main outputs. The physical check then
shows that the four even Q powers are legal translations. The source local
free-word proof applies at every positive tensor width; scalar coefficients
remain outside the operator substitution.

## Complete bill and conditional bound

Each of the 18 backward calls has

```text
paid:    {1:2193, 2:412, 3:510, 4:127, 5:40}
helpers: {4:28, 7:7, 8:47, 9:318}
```

Relative to PR5383, the two replaced forward calls remove **16 H1 and 16 H8
paid jobs**, and debit **16 H9 productive targets**. For every `0<t<1`, the
complete target-minus-paid moment increases by `16(1+8^t-9^t)>0`. To prove the
sign, add `(1/9)^t>1/9` and `(8/9)^t>8/9`, then multiply by `9^t`.
Relative to final PR4610, the full change is minus 144 jobs at each paid rank
1 and 8, and minus 144 targets at rank 9. Relative to PR5392, this recursive
bill is equal.

Both the event census and a separate delta from the selected bill give
**64,116 paid calls and 10,784 productive fields**, with rank surplus 752.
All 15 thin queries, 15 whole idle jobs and 3,584 main targets remain included.
No prepared helper or snapshot receives independent target credit.

The unchanged local scalar allowance is 158,744. The local route allowance is
4,818,000, and their sum is below 10^7. The four added signed swaps and four
translations cost at most `4*112*(26+1000)=459648` in the retained fixed-template
accounting. The translation changes only the nine old address bits; the fixed
1000 allowance exceeds those bit operations. The complete raw nonrecursive
allowance is **181,586,816 < 10^9**. Eight additional snapshot slots relative
to PR4610 suffice. Each full call has seventeen owned fields, including eight
old helper slots. The wrappers need no additional owned field. The completed signed swaps
and translations have norm one. The three-ADD swap can temporarily double
the two-field norm; this is a fixed factor. The precision and tape contracts
must use this full template, including that intermediate factor.

Two rational interval engines check the moment. Exact bounds enclose its
unique crossing in **(0.00302728824993, 0.00302728824994)**. They prove decrease
on `[0,0.05]` and negativity on `[0.05,1]`. This ceiling applies only to the
stated complete profile. The claimed kappa leaves more than `1.993e-11`
raw headroom.

The tested saving is 0.00302728824. The paid/target ratio is below
`0.999999999989608136845597542013`, with reserve `1e-12`. Both charged tail
ratios are below 0.97. Power 1024, cutoff 20, floor 21, offset 1/5, complement
factor 63/64 and logarithm power 1000 pass. The complete normalized paid bound
is `1048576000976562501/1048576001073741824 < 1`.

The compiler uses gap `1/700000000000`, integer `j=55099`,
`H=38569300000000000` and `N=2^38569300000000000`. The exact inequality
`(H+1)^1000 < 2^55099` passes; the preceding grid integer fails. All **54 strict
outer predicates and four functional predicates** pass with ordinary BIT
saving 0.0034. The larger threshold funds the smaller gap to the raw root.
The compiler word is specified by the inherited finite algorithm; it is not
materialized.

## Reproduce and assess the evidence

Use CPython 3.12 and the standard library. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/kappa-backward-controller-20261023 --check-only
python3 -B scripts/research_package.py --package research/kappa-backward-controller-20261023
python3 -B scripts/check_research_commit.py --package research/kappa-backward-controller-20261023
```

The registered commands run normal and optimized modes. Direct replay also
works in the official Git-free export:

```sh
python3 -B research/kappa-backward-controller-20261023/verify.py
python3 -O -B research/kappa-backward-controller-20261023/verify.py
```

Both must print `PASS_CONDITIONAL_KAPPA_00302728823_ALL_BACKWARD_CONTROLLER`.
Normal verification reads files and compares the regenerated caller and result.
The separate `--write` authoring mode writes only those two package artifacts
after all mathematical gates pass.

Checks cover the exact source word, all 624 independent persistent and 17
arbitrary owned entry columns, sixteen unrestricted source identities, both
actual wrapper boundaries, the full Laurent caller, two invoices, two interval
engines, completion, compiler and all outer predicates. Seven inherited native
controls reject relation, ownership, snapshot, frame, rank, COPY and return
errors. Four caller controls reject a missing translation, an unpaid odd Q
power, a wrong local orientation and a missing scalar sign. Seven cost/outer
controls reject false helper credit, two invalid reserves and four invalid
outer parameters. Checks use explicit exceptions and remain active under `-O`.
The registered normal and optimized replays passed on CPython 3.12.13.
The direct author replay also passed on CPython 3.14.7. Metadata and source
pins passed. The publication handoff records the committed-byte and export
checks; hosted CI is separate.

These are author checks. The source absolute-phase lowering and amplitudes,
ordinary BIT native construction, physical tape execution, numerical precision
execution, analytic decomposition, prime avoidance and exact integer recovery
are inherited and not rerun. No Lean, Docker, proof-kernel acceptance or
independent human approval is claimed. The optional full-history preflight is
not claimed in this shallow checkout. The five framework assumptions remain:
native all-column realization, owned erasure, uniform compiler closure,
precision/tape and analytic recovery. This is a conditional mathematical
construction, not a practical timing result or a selected-frontier update.

## Credit

Ali Romman, with substantial OpenAI Codex assistance; Apache-2.0.
PR5383 supplies the eight prepared relations, snapshots, zero rows, backward
word and retained native checker. Its
[proof and notices](https://github.com/aliromman/integer-mult-bounds/blob/4bd6efa51a495a7c7b7754915cf0244e7e60969e/research/kappa-joint-relations-20261023/README.md)
credit the earlier
[PR #5377](https://github.com/CrocSwap/integer-mult-bounds/pull/5377)
construction. No discovery credit for those relations is claimed here.

Cao Yifan supplies the final PR4610 native word and pricing lineage.
Cinna Davis supplies the
[PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470)
controller and helper lineage. The retained
[pricing source](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/kappa-interface-round2-20261022/price_profile.py)
and the linked predecessor proof credit Dugongue's frames, zxv's native,
completion and logarithmic compiler work, Jacob Alan Sussman's mixed-target
recursion, Cinna Davis and ToikY's tensor argument, and earlier contributors.
Chris R's
[PR #5241](https://github.com/CrocSwap/integer-mult-bounds/pull/5241)
supplies the selected source admission; it does not admit this changed caller.
The predecessor notices and copied source bytes remain unchanged.

Dugongue's
[PR #5387](https://github.com/CrocSwap/integer-mult-bounds/pull/5387)
is related smaller-reserve compiler work. PR5392 is the concurrent transpose
construction with the same paid profile. Neither package is a runtime input.
This package's new work is the direct caller identity, both physical boundary
checks, the emitted caller, its scalar bill and the stated full conditional bound.

## Open next questions

An independent reviewer should inspect both physical wrapper sites and the
complete price before admitting this caller. A stronger completed backward
supplier can use the same wrapper after its main, helper and owned interfaces
are checked. [TASK.json](TASK.json) records the first checks and blockers.
This result does not reserve the active paid-history, relation or decoder work.
