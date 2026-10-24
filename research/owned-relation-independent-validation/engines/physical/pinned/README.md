# Conditional kappa 0.00302235 from one owned helper relation

This construction gives **conditional kappa = 60447/20000000 = 0.00302235**.
The gain over Cao Yifan's final
[PR #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610)
value, 0.0030217758, is **2871/5000000000 = 0.0000005742**.
The construction changes the complete paid profile. It does not obtain the
gain by taking more digits of the old root.

One helper becomes owned storage in each backward call. A prepared relation
then makes one paid rank-eight center equal to an earlier saved value. The same
relation makes one later rank-one job act on zero. Both jobs can be removed,
with the rank-nine helper credit also removed. All other independent outputs
and all main interfaces keep their source operators.

[WORD.json.gz](WORD.json.gz) is the complete emitted word.
[RESULT.json](RESULT.json) records the exact native checks, the two source
identities, both full profiles, completion, compiler and outer calculations.
[SOURCES.json](SOURCES.json) pins every external input by Git blob and SHA256.
The proof below explains why the changed word has the stated contract.

## Source and scope

The base is canonical main
[7c472563474e60185e6ca101a17622133d047e56](https://github.com/CrocSwap/integer-mult-bounds/commit/7c472563474e60185e6ca101a17622133d047e56).
The native source is the final PR #4610 word at
[20bb93cd990d2ff683e4d0fc56b87a42cd5d3296](https://github.com/intqwq/integer-mult-bounds/blob/20bb93cd990d2ff683e4d0fc56b87a42cd5d3296/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz).
Its decompressed SHA256 is
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
The comparison value and old crossing come from its
[final compiler arithmetic](https://github.com/intqwq/integer-mult-bounds/blob/20bb93cd990d2ff683e4d0fc56b87a42cd5d3296/research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json).
All consumed bytes are already in the recorded main base.

This is one instance of the current `complex-new-helper-inventory` priority.
The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19153737)
reserves only the relation and two replacements below.
[Discussion #5355](https://github.com/CrocSwap/integer-mult-bounds/discussions/5355)
retains all 632 independent inputs and all eight centers.
[Discussion #4930](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930)
retains every original helper endpoint. This construction removes the
independent L230 job in backward calls. It does not claim those broader scopes.
The selected certificate is unchanged. A fresh check at 20:20 UTC found that
Discussion #5355 had released its original-input scope without a saving.
Canonical main still had the recorded base commit.

## Exact replacement proof

All indices below are zero-based indices in the frozen backward program.
Let `h_r` be the source logical input of helper `Lr`. The five helpers in

```math
\Delta=h_{230}-h_{324}+h_{326}+h_{328}-h_{333}
```

all start in frame 0 and finish in frame 1, of rank nine. The new backward
contract has 224 independent main fields and 407 independent helper fields.
L230 is private. Clear it, then use four same-frame ADDs to prepare

```math
h_{230}=h_{324}-h_{326}-h_{328}+h_{333}.
```

The other helper inputs remain arbitrary and independent. This preparation
sets Delta to zero for every input. It uses no recursive job. It removes one
rank-nine productive target; the dependent field receives no output credit.

Run the original source program on unrestricted inputs. Let `q` be the
logical row of L92 just after event 11205, a paid climb into frame 254.
The separate predecessor row engine gives these exact identities:

| Source position | Exact logical row |
| --- | --- |
| C0 at the rank-eight center, event 11332 | `q + Delta/4` |
| L92 at the rank-one climb, event 15584 | `-Delta/4` |

These identities are over rational coefficients and free native operator
words. They hold for every value of every source input and for every invertible
interpretation of the native symbols. They do not use numerical samples or an
assumed relation between distinct native maps.

For every positive tensor width f, substitute each native generator by its
source operator tensor power and each inverse by the inverse tensor power.
This defines a representation of the free group. Keep the rational scalar
coefficients outside the substitution. The two row identities therefore hold
at every such width. In particular, Delta/4 remains a scalar linear form; it
is not a tensor power of that sum. This uses the termwise argument recorded in
the [free-word tensor audit](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/free-word-tensor-lift-audit/PROOF.md),
which credits Cinna Davis's proposal and ToikY's scoped audit. Physical frame
realization and the complete all-size compiler retain their source contracts.

Immediately after event 11205, clear a new private field C1 in frame 254 and
COPY L92 into it. C1 is not written until the replacement of event 11332. At
that event, clear owned C0, set its frame to 254, COPY C1 into C0, then clear C1.
The copy coefficient is exactly one. Under Delta = 0, the copied field is the
same physical value as the old center output: the logical rows and the exact
frame gauge are equal. The old C0 input can be erased because C0 is owned.
This removes one rank-eight recursive job.

At event 15584, L92 is exactly zero in every input column. The physical
identity therefore has the same result as the old rank-one frame change.
`zero_retag` records this fact. It performs no physical write and is accepted
only when the full exact row is empty and the current frame is 254. It then
records frame 1. This removes one rank-one recursive job. It does not erase a
main input or replace a nonzero transform with a free frame change.

Every other event stays in source order. Clear private L230 at return. The
source clears C0, and the new program has already cleared C1. The original
linear endpoint identity, restricted by the prepared relation, gives all 224
main outputs and all 407 retained helper outputs. The literal new-word replay
checks these outputs separately, with all 631 retained inputs and all three
owned entry fields initially arbitrary. It also checks every scalar frame,
paid rank, native frame transition and final frame.

The 4,429 source frames, 72 native maps, all remaining paid operators, and main
adapters are unchanged. The source
[absolute-phase certificate](https://github.com/intqwq/integer-mult-bounds/blob/20bb93cd990d2ff683e4d0fc56b87a42cd5d3296/research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz)
is authenticated and reused. Same-frame COPY and identity on zero introduce no
phase recipe. The source's amplitude and Clifford-lowering checks are not
rerun by this package. The new free-word identities prove equivalence for the
source operators with their full phases, not just their projective classes.

## Complete cost and conditional compiler

The forward word is unchanged. Each backward call has these counts:

```text
paid:    {1:2200, 2:412, 3:510, 4:127, 5:40, 8:7}
helpers: {4:28, 7:7, 8:47, 9:325}
```

The full p16/a7 controller contains 16 backward calls, two forward calls and
15 query shears. Thus the complete difference is **minus 16 H1 and 16 H8 paid
jobs, and minus 16 H9 productive targets**. It includes every idle and main
target. There are 64,372 paid jobs and 10,912 productive fields. Their rank
masses are 238,990 and 239,742; the surplus remains 752.

For every real `0 < t < 1`, the complete target-minus-paid moment increases by

```math
16(1+8^t-9^t)>0.
```

For a direct proof, both `(1/9)^t > 1/9` and `(8/9)^t > 8/9`; multiply their
sum by `9^t`. The improvement is strict throughout the required range.

The backward word has 158,214 real scalar operations under the source macro
allowance, exactly 46 more than its source. Its maximum formal prefix L1 norm
is 169, with maximum denominator 64; both equal the source bounds. The forward
bounds remain 457 and 32. One extra physical private slot holds C1. L230 uses
an existing slot. The route bound also charges two routes for each of the two
new owned lifetimes. The local scalar-plus-route bound stays below 10^7, and
the complete raw nonrecursive bound stays **181,098,496 < 10^9**. Preparation,
COPY, CLEAR and storage therefore do not introduce an unpaid recursive cost.

Two rational interval engines check the complete moment. Its unique crossing
in `0 < kappa < 1` lies in
**(0.00302238736347, 0.00302238736348)**. The verifier proves the moment decreases
on `[0,0.05]` and remains negative on `[0.05,1]`. This is a ceiling for this
fixed complete profile, not an optimum over circuits or helper relations.
The claimed kappa leaves more than **0.00000003736347** raw headroom.

The separately tested saving is 0.00302236. The paid/target ratio is below
`0.999999971483293515393313955730`, with reserve `1e-9`. Both charged tails are
below `0.97`. The source power 1024, cutoff 20, floor 21, tail offset 1/5,
complement factor 63/64 and logarithm power 1000 still pass. The compiler gap
is `1/700000000`, with `j=44836`, `H=31385200000000` and `N=2^31385200000000`.
The exact integer test `(H+1)^1000 < 2^44836` passes; the preceding grid integer
fails. The uniform complex saving is `2115651/700000000`. All 54 strict outer
predicates and four functional predicates pass, using the retained ordinary
BIT saving 0.0034.

## Verification and reproduction

Use Python 3.12 or 3.14, with the standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/kappa-owned-relation-20261023 --check-only
python3 -B scripts/research_package.py --package research/kappa-owned-relation-20261023
```

The registered commands run normal and optimized Python. The direct command,
also used for a Git-free export, is:

```sh
python3 -B research/kappa-owned-relation-20261023/verify.py
python3 -O -B research/kappa-owned-relation-20261023/verify.py
```

Each prints status
`PASS_CONDITIONAL_KAPPA_00302235_ONE_OWNED_RELATION`.
The verifier reconstructs the word and compares its bytes and exact result with
the published artifacts. `--write` is a separate authoring command. It changes
only this package's word and result after all checks pass.

Fresh checks cover both source words, both candidate words, every independent
entry column and owned return, the two unrestricted source identities, retained
phase bindings, the p16 rational Laurent factorization, both scalar boundary
programs, two complete invoice counts, two rational interval engines, the fixed
profile ceiling, completion, compiler, BIT conversion and all outer predicates.
The emitted word replaces the old single `canonical.local_profile` metadata
field with explicit `paid_profiles` for the two directions.

Seven native controls reject a wrong relation sign, omitted input clear, wrong
snapshot, wrong zero frame, wrong paid rank, wrong copy gauge, and omitted
output clear. Five cost/outer controls reject the lost helper's output credit,
old BIT stock, closed uniform gap, unfunded endpoint and closed epsilon.

Normal and optimized registered replays passed on CPython 3.12.14. The direct
author check also passed on CPython 3.14. Source metadata and pins passed.
The optional full-history preflight is not claimed in the shallow checkout.
The publication handoff records export and committed-byte checks.

The full source phase lowering, BIT native replay, Lean, Docker, physical tape
execution, numerical precision execution, analytic decomposition and integer
recovery are not rerun here. The complete bound retains those predecessor
contracts, including permitted owned erasure, whole-job normalizers, mixed
productive-target recursion and all-size closure. The expanded compiled word
is specified by a finite algorithm, not materialized. This is a conditional
construction with exact finite evidence, not an unconditional multiplication
theorem, a practical timing result or independent human acceptance.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Cao Yifan's [PR #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610)
supplies the exact source word, phase evidence and previous compiler value.
Cinna Davis's [PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470)
supplies the p16 controller and helper-interface lineage. The source code keeps
credit for Dugongue's transported frames, zxv's native and finite-compiler
work, Jacob Alan Sussman's mixed-target recursion and their predecessors.
The [pricing source](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/kappa-interface-round2-20261022/price_profile.py)
and [literal native source](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/kappa-rebuild/complex/native_extensions.py)
are pinned as provenance for the adapted checks.

zxv's [PR #5283](https://github.com/CrocSwap/integer-mult-bounds/pull/5283)
supplies the related cache contract and the explicit handoff to find actual
matching rows and their lifetimes. Its standalone cache example is not part of
this word. The new contribution is the five-helper relation, its actual cache
and zero identities, the full owned-field replacement and the complete positive
bill. No priority is claimed for the general cache or paid-history ideas.

## Open next questions

Independent review should first check the three source rows and the physical
COPY/zero argument above, then the retained all-size and phase premises.
A later construction could test a different helper relation, but it must claim
a disjoint scope and pay every lost target and owned field. This package does
not classify such relations. [TASK.json](TASK.json) records the first steps,
relevance and blockers for both questions.
