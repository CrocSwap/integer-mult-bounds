# Conditional kappa 0.00302666 from eight joint helper relations

This construction gives **conditional kappa = 151333/50000000 = 0.00302666**.
It improves the one-relation [PR #5377](https://github.com/CrocSwap/integer-mult-bounds/pull/5377)
value by **431/100000000 = 0.00000431**. The gain over the selected final
[PR #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610)
value is **24421/5000000000 = 0.0000048842**.

Eight independent helper relations replace all eight backward rank-eight
centers with exact saved values. They also remove eight later rank-one jobs
on zero fields. Each backward call gives up eight rank-nine productive helper
targets. All 224 main inputs and the other 400 helper inputs stay independent.
The forward word and p16 controller stay unchanged. This changes the complete
paid profile and proves a strict moment gain.

[WITNESS.json](WITNESS.json) lists the eight relations and source events.
[WORD.json.gz](WORD.json.gz) contains the complete literal program.
[RESULT.json](RESULT.json) gives the exact row identities and complete bill.
[SOURCES.json](SOURCES.json) pins every consumed input by Git blob and SHA256.
The package has no runtime dependency on the pending PR #5377 package.

## Source and research boundary

The branch starts at canonical main
[1ec1119972c9aefe42525172d07b332fcff81cb4](https://github.com/CrocSwap/integer-mult-bounds/commit/1ec1119972c9aefe42525172d07b332fcff81cb4).
This base selects the final PR4610 result with the independent
[PR #5241](https://github.com/CrocSwap/integer-mult-bounds/pull/5241) audit.
The [selected review](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/docs/research/pr-intake-evidence/pr4610/PROOF-REVIEW.md)
records its exact scope and five retained framework assumptions.

The frozen native source is Cao Yifan's
[round-three word](https://github.com/intqwq/integer-mult-bounds/blob/20bb93cd990d2ff683e4d0fc56b87a42cd5d3296/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz)
at final PR4610 commit `20bb93cd990d2ff683e4d0fc56b87a42cd5d3296`.
Its decompressed SHA256 is
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
The prior complete bill and crossing come from its
[round-six arithmetic](https://github.com/intqwq/integer-mult-bounds/blob/20bb93cd990d2ff683e4d0fc56b87a42cd5d3296/research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json).
All consumed source bytes occur in the recorded main base.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19154290)
covers only the eight named centers and their joint relation system.
The separate [no-snapshot relation search](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19154267)
has released its scope and explicitly excludes joint relations and center reuse.
The original-input cache search in
[Discussion #5355](https://github.com/CrocSwap/integer-mult-bounds/discussions/5355)
is also released. The coded caller in
[Discussion #4930](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930)
retains all original helper outputs. This package changes eight helper inputs
in backward calls. It does not take those other research scopes.

## General relation construction

Consider an exact linear register program with independent helper inputs in
one common input frame. Let r independent scalar relations have a reduced
basis with dyadic coefficients and r helper pivots. Make these r fields owned.
Clear them and prepare each pivot from the nonpivot inputs with scalar ADDs.
Each relation is then zero for every remaining independent input. The r owned
fields receive no productive output credit.

Suppose that an earlier field and a later owned center output have the same
exact frame, and their logical row difference is zero under these relations.
Clear a new owned field, COPY the earlier value into it and retain it. At the
center, clear the old owned center and COPY the saved value into that same
output frame. Clear the snapshot after use. This implements the old output
exactly without the center job. If another paid job has an identically zero
input row, the physical identity also implements that job on the restricted
domain. A frame annotation may change only after this exact zero check.

Each replacement preserves the source state on that domain. Induction through
the chronological word therefore preserves every retained output. Clear all
owned pivots at return. The complete cost must remove their productive
credits and count every new scalar operation and storage route. Independence
of the relations is necessary: counting eight apparent formulas is not a
proof of eight independent pivots or of eight distinct saved jobs.

## Eight exact source identities

Let h_r denote the unrestricted logical input of source helper Lr. Define:

```text
D1 = h230 - h324 + h326 + h328 - h333
D2 = h225 - h384 - h388 + h390 + h391 + h392 - h397
D3 = h225 - h227 + h229 - 2h231 + h232 - h234 - h235
     - h236 - h237 + 2h238 + h239 - h384 - h388 + h390
     + h391 + h392 - h397
D4 = h227 + h229 - h232 + h234 + h235 - h236 + h237
     - h239 - h324 + h326 + h328 - h333
D5 = h241 - h243 + h245 - h247 - h252 - h253 + h254 + h255
D6 = h225 - h241 + h243 + h245 - h247 - h252 + h253
     + h254 - h255 - h324 + h326 + h328 - h333 - h384
     - h388 + h390 + h391 + h392 - h397
D7 = h257 - h259 + h261 - h263 - h268 - h269 + h270 + h271
D8 = h288 - h294 - h296 - h297 + h300 + h303
```

Every helper in these relations starts in frame 0 and ends in frame 1, of
rank nine. Exact row reduction gives the eight pivots
**225, 227, 229, 230, 241, 245, 257, 288**. The reduced basis has no other pivot
in any pivot row. Its nonzero coefficients are integers or half-integers.
The emitted preparation thus uses only independent inputs and dyadic ADDs;
it has no cyclic dependence and needs no recursive job. The full reduced
basis is recorded in the word and result.

The following indices are zero-based indices in the frozen backward source.
A snapshot is taken immediately after its named event. The two last columns
are identities in the unrestricted source, before any relation is imposed.

| Relation | Snapshot event and role | Frame | Center event | Later zero event and role | Center minus snapshot | Later row |
|---|---|---|---|---|---|---|
| D1 | 11205, L92 | 254 | 11332 | 15584, L92 | D1/4 | -D1/4 |
| D2 | 11218, L57 | 274 | 11358 | 17264, L57 | D2/4 | -D2/4 |
| D3 | 11231, L81 | 619 | 11384 | 17256, L81 | D3/4 | -D3/4 |
| D4 | 11244, L224 | 279 | 11410 | 17722, L224 | -D4/4 | D4/4 |
| D5 | 11257, L11 | 621 | 11436 | 15876, L11 | D5/4 | -D5/4 |
| D6 | 11270, L240 | 280 | 11462 | 17245, L240 | -D6/4 | D6/4 |
| D7 | 11283, L9 | 624 | 11488 | 15870, L9 | D7/4 | -D7/4 |
| D8 | 11306, L288 | 281 | 11514 | 17580, L288 | D8/4 | -D8/4 |

The COPY coefficient is one in every case. All eight snapshots are live
before the first center replacement. They use distinct owned fields C1 through
C8. Each is read once and cleared after use. The source owned center C0 is
cleared before each replacement. Each later zero job changes from the listed
frame to frame 1 and has rank one. `zero_retag` is a physical no-op; the verifier
requires its complete row to be zero and checks both exact frame identifiers.

A separate source interpreter checks all sixteen identities on the unrestricted
632 source inputs. The new interpreter then executes the emitted program on
all **624 independent persistent columns and 17 arbitrary owned entry columns**.
It checks every scalar frame, paid rank, native transition, retained endpoint,
final frame and owned return. No independent input is silently set to zero.

The identities are over rational coefficients and reduced free operator words.
They hold for any invertible interpretation of the native generators. At
positive tensor width f, replace each generator with its source tensor power
and each inverse with the inverse tensor power. Keep each rational coefficient
outside this substitution. Evaluation is a representation of the free group,
so the identities still hold. In particular, no tensor power is distributed
over a sum. The retained
[free-word tensor audit](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/free-word-tensor-lift-audit/PROOF.md)
records this termwise argument and credits Cinna Davis and ToikY.

All 4,429 source frames, 72 native maps, adapters and retained paid operators
are unchanged. The package authenticates and reuses the source
[absolute-phase evidence](https://github.com/intqwq/integer-mult-bounds/blob/20bb93cd990d2ff683e4d0fc56b87a42cd5d3296/research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz).
Same-frame COPY and identity on zero add no phase recipe. This package does
not rerun the source Clifford lowering or amplitude checks. The new identities
hold for the full source operators, including their absolute phases.

## Complete bill and compiler

Each backward call has the following complete local profiles:

```text
paid:    {1:2193, 2:412, 3:510, 4:127, 5:40}
helpers: {4:28, 7:7, 8:47, 9:318}
```

The controller has 16 backward calls, two unchanged forward calls and 15 thin
queries. Every idle and main target remains paid or credited as in the source.
Compared with PR4610, the complete difference is **minus 128 H1 and 128 H8 paid
jobs, with minus 128 H9 productive targets**. Compared with PR5377 it removes
224 further paid jobs and 112 further productive fields. The complete bill has
**64,148 paid jobs and 10,800 productive fields**. The respective rank masses
are 237,982 and 238,734, with unchanged surplus 752.

For every real `0 < t < 1`, the complete target-minus-paid moment increases by

```math
128(1+8^t-9^t)>0.
```

Both `(1/9)^t > 1/9` and `(8/9)^t > 8/9`; summing and multiplying by `9^t`
proves the strict inequality. This comparison charges the lost helper jobs.

The backward scalar allowance is **158,744**, which is 576 above the source.
Its maximum formal prefix L1 norm is **163**, below the source value 169, and
its maximum denominator stays 64. The forward values remain 158,120, 457 and
32. Eight new physical slots hold C1 through C8; the eight private helpers use
existing slots. The local route allowance charges both routes for each of
these sixteen new owned lifetimes. It is **4,834,000**. The local scalar-plus-route
bill stays below 10^7. The complete raw nonrecursive bound remains
**181,098,496 < 10^9**. These bounds include preparation, storage, COPY and CLEAR.
The retained precision and tape prescriptions must use this expanded fixed
template, not a former numerical template-size cap.

Two rational interval engines verify the complete moment. Its unique crossing
in `0 < kappa < 1` lies in **(0.00302667476807, 0.00302667476808)**. Exact interval
bounds prove decrease on `[0,0.05]` and negativity on `[0.05,1]`. This is a ceiling
for this fixed complete profile. It does not optimize all relation systems.
The claimed kappa leaves more than **0.00000001476807** raw headroom.

The tested saving is **0.00302667**. The paid/target ratio is below
`0.999999995016963387587258118167`, with reserve `1e-9`. The two charged tail
ratios are below 0.957 and 0.952, respectively, hence below 0.97. Tensor power
1024, cutoff 20, floor 21, tail offset 1/5, complement factor 63/64 and logarithm
power 1000 all pass. The finite compiler uses gap `1/700000000`, `j=44836`,
`H=31385200000000` and `N=2^31385200000000`. The exact test
`(H+1)^1000 < 2^44836` passes; the preceding grid integer fails. The uniform
complex saving is `529667/175000000`. All **54 strict outer predicates and
four functional predicates** pass with the retained ordinary BIT saving 0.0034.

## Verification and limitations

Use CPython 3.12 or 3.14 and the standard library. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/kappa-joint-relations-20261023 --check-only
python3 -B scripts/research_package.py --package research/kappa-joint-relations-20261023
```

The registered verifier runs normal and optimized modes. The direct commands
also work in the official Git-free export:

```sh
python3 -B research/kappa-joint-relations-20261023/verify.py
python3 -O -B research/kappa-joint-relations-20261023/verify.py
```

Both print `PASS_CONDITIONAL_KAPPA_00302666_EIGHT_JOINT_RELATIONS`.
The verifier reconstructs and compares the literal published word and result.
`--write` is an authoring mode that writes only this package after all checks
pass. Regeneration compares decompressed payloads, not gzip container bytes.

Fresh checks cover both original and changed words, all retained and owned
entry columns, sixteen unrestricted source identities, exact relation rank,
phase source bindings, the p16 Laurent controller and both boundary programs,
two complete invoice counts, two interval engines, the fixed profile ceiling,
completion, compiler and every outer predicate. Seven native controls reject
a wrong preparation sign, omitted input clear, wrong snapshot, wrong zero
frame, wrong paid rank, wrong COPY gauge and omitted output clear. Five
cost controls reject unearned helper credit and four invalid outer parameters.

Normal and optimized registered checks passed on CPython 3.12.14. The direct
author replay also passed on CPython 3.14. Metadata and source pins passed.
The publication handoff records committed-byte and Git-free export checks.
The optional full-history preflight is not claimed in this shallow checkout.

These are author checks. The source phase lowering, BIT native construction,
physical tape execution, numerical precision execution, analytic decomposition,
fine-prime avoidance and exact integer recovery are inherited. They are not
rerun here. No expanded compiled word, Lean proof, Docker run or independent
human acceptance is claimed. The complete result retains the selected five
framework assumptions: all-column native realization, owned erasure, uniform
compiler closure, precision/tape and analytic recovery. No selected record is
changed. This is a conditional mathematical improvement, not a timing result.

## Credit

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The new code and proof generalize our
[frozen one-relation package](https://github.com/aliromman/integer-mult-bounds/blob/c448d13c71908647f968b06cddb795ce7d288139/research/kappa-owned-relation-20261023/README.md)
from PR5377. That package supplies D1, its COPY/zero argument and the original
complete-cost verifier. The new work is the joint rank-eight system, seven
further centers, eight simultaneous snapshots and the new complete bound.

Cao Yifan's [PR #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610)
supplies the exact word, phase evidence and compiler lineage. Chris R's
[PR #5241](https://github.com/CrocSwap/integer-mult-bounds/pull/5241) supplies the
independent admission evidence now used by main; that audit does not cover
this changed helper inventory. Cinna Davis's
[PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470) supplies the
controller and productive-helper lineage. zxv's
[PR #5283](https://github.com/CrocSwap/integer-mult-bounds/pull/5283) supplies the
related cache contract and handoff to actual row/lifetime matches.

The retained [pricing source](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/kappa-interface-round2-20261022/price_profile.py)
and [native source](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/kappa-rebuild/complex/native_extensions.py)
credit Dugongue's transported frames, zxv's native/compiler work, Jacob Alan
Sussman's mixed-target recursion and the earlier contributors. Their notices
and the original source bytes remain unchanged.

## Open next questions

An independent reviewer should check the eight pivot preparations and sixteen
unrestricted identities, then the COPY/zero realization and complete bill.
Independent physical and all-size acceptance remains necessary. A further
construction must change another paid job or relation system: all eight
backward centers are already removed here. Check live claims and price every
lost target before that search. [TASK.json](TASK.json) records both questions,
first checks and blockers. No optimum over helper relations is claimed.
