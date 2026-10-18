# UT4 central-target tariffs with arbitrary dirty workspace

**Scoped lower theorem and attained coefficient relaxation; no new kappa.**
Adding a third adjacent generator changes the UT3 register model to
`F2[UT4(F2)]`. For `w` central targets and **every finite `r>=w>=1`**, with all
extra roles arbitrary dirty and restored, every word of nonzero binary
rank-one paid couplings requires

```
n_a >= 2w,    n_b >= 3w+[w=1],    n_c >= 2w.
```

The complete unit-price bill is at least `7w+[w=1]`; a direct formal word
costs `8w`. One target therefore costs **exactly eight**, even with arbitrary
workspace and nilpotent couplings. With positive uniform letter prices this
one-target optimum is `2alpha+4beta+2gamma`. Full multi-target optimality is
open: at two targets the proved interval is **14 through16 calls**.

The [written proof](PROOF.md) derives the outer bounds from natural and
contragredient representations and the new middle bound from
`ker(X)/im(Y)` together with degree-three mixed middle-span constraints. It proves the middle-factor relaxation optimum for every `w`,
with an explicit attained four-matrix fixture. That fixture is **not a full
chronological word**. A legal twelve-call trial passes the natural endpoint
but fails the contragredient and full formal endpoints, making the distinction
concrete. The theorem excludes every twelve-call two-target word in this alphabet.

## Explicit changed model and price boundary

The only paid address letters are `a=I+E12`, `b=I+E23`, `c=I+E34`; the target
is `diag([I+E14] repeated w, identity on the remaining roles)`. A factor is
`I+([g]+1)N`, where `N=xy^T` is any nonzero binary rank-one coupling, including
idempotents and nilpotents. Scalar mixing is optimistically free and normalized
into those couplings. There are no arbitrary free address maps, clean roles,
COPY, ERASE, higher-rank paid factors or uncharged undo. All calls, including
restoration, are counted. The direct `8w` word needs no extra roles or mixing.

This is a target-specific screening bound for a precisely specified nonabelian
alphabet. It changes the group and alphabet, rather than repeating a UT3 result
or a three-register abelian search. It establishes no rational-frame identity,
physical compiler, supplier profile, rank-shape gain or multiplication exponent.
The selected frontier and frozen sources are unchanged. Physical implementation,
common-label/hosting, precision/tape and analytic transfer remain outside scope.

## Exact evidence

| Completed check | Coverage |
| --- | --- |
| Formal and separately written faithful complete witnesses | 30 coordinate/conjugated fixtures, `r=1..5`, all `1<=w<=r` |
| Full witness basis columns | 7,040, including arbitrary dirty-role columns |
| Expanded ordered two-factor products | all729 on two roles |
| Chronological middle-coefficient identities | all19,683 three-factor words on two roles |
| Attained raw middle-factor relaxation | 128 fixtures, `w=1..64`, `r=w` and `w+2` |
| Degree-three quotient homomorphism / algebra associativity | all4,096 group products /4,913 basis triples |
| Independent literal group multiplication / associativity | 4,096 products /262,144 triples |
| Independent idempotent/nilpotent regular factors | 42 fixtures through five roles |

[CERTIFICATE.json](CERTIFICATE.json) retains transcript digests, exact relaxation
examples and the failed twelve-call word. [INDEPENDENT.json](INDEPENDENT.json)
records literal four-by-four address matrices and faithful regular operators.
The formal engine uses the six-coordinate group law; the independent engine
imports no local or predecessor implementation. They compare complete operators,
not sampled bits or the nonfaithful proof images alone.

Sixteen omitted-call controls reject; a dirty-role central action rejects. A
nonzero four-term kernel perturbation is invisible in all three proof images
and on clean-extra inputs, but changes all64 dirty-extra columns. This is a
diagnostic operator, not asserted to be an admitted paid-letter word. Eight
test groups additionally cover raw rectangular quotient ranks, the binary-field
boundary, illegal alphabets/domains/order, actual source/receipt corruptions,
occupied outputs and read-only optimized relocation. The all-workspace theorem
comes from the written rank argument and the fixed-group homomorphism lemma,
not extrapolation from finite role/target fixtures.

## Reproduce

From the repository root with Python3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/ut4-central-tariff-relaxation
```

Expect `PASS_UT4_CENTRAL_TARIFF_RELAXATION`,
`PASS_UT4_CENTRAL_TARIFF_INDEPENDENT`, eight passing groups and
`PASS_REGISTERED_RESEARCH_PACKAGE research/ut4-central-tariff-relaxation outcome=completed`.

Standalone checks support isolated optimized Python. Normal verification writes
nothing. Explicit regeneration uses `verify.py --write-receipt NEW_PATH` or
`independent.py --write NEW_PATH`; occupied paths are refused. Registered commands
and the one live pinned model input are declared in [VERIFY.json](VERIFY.json).
Actual local commands/environment and omissions are in [VALIDATION.json](VALIDATION.json).
Generic provenance checking requires the pinned Git history; direct source
exports can run the scoped standalone engines.

## Task, sources and predecessor credit

Base main: `c24fb5e6537d19d79c62265e4a12781aef9309cb`. Priority3 assignment
`bit-new-register-model`, nonce `825a224ec7f742d396fd07c46cd8f17c`, scope key
`7084092dd726e7ba1f2f`; scope refined to the specified nonabelian family and
target-specific relaxation method. [TASK.json](TASK.json) records the card,
model, claim, source-bound first command and overlap limitations.
[SOURCES.json](SOURCES.json) pins the model orientation, selected provenance and
catalog. No pending executable is imported or needed by the replay.

Credit **steph4n-gh's [PR1573](https://github.com/CrocSwap/integer-mult-bounds/pull/1573)**
at `0b8c5a69297c794f2de22c04494c83e41300ae36` for the UT3 all-register zero-sum
rank proof; **Arham Tahir's [PR1589](https://github.com/CrocSwap/integer-mult-bounds/pull/1589)**
at `010ec8c01c0edbbb08b541be236ab78d096f2ca1` for the expanded nilpotent
alphabet; **Hanson Sun (@bbMisk)'s [PR1607](https://github.com/CrocSwap/integer-mult-bounds/pull/1607)**
at `9d6117918025cee6a0c5b7ef30ff8d936ca0621f` for coefficient-span tariffs.
Those are two-letter UT3 results; this adds the class-three middle quotient, mixed middle spans and
its carefully separated attained relaxation. Credit juper997/PR1478,
woklerx/PR1443, Gareth Davidson/bitplane/PR1333, commdata2338/PR1414,
eumemic/PR288, Ali Romman/PR468 and the retained model lineage. No literature
priority claim is made.

Prepared for **@ToikY** with substantial **OpenAI Codex assistance** in derivation,
separate implementations, proof review, verification and writing. Two bounded
subagents; no independent human or proof-kernel review claimed. Apache-2.0.

## Open next questions

Can two central targets attain14 calls in the full alphabet, or do chronological
and remaining formal constraints force15 or16? Classify six-middle-call
rank-one sequences with both middle spans of rank two, then impose natural,
contragredient and degree-three coefficient equations before testing the full
formal endpoint. The attained four-matrix relaxation supplies headroom but no
paid chronology. Additional unpriced dirty roles cannot be treated as a
construction.

Sharp full multi-target tariffs, a kernel-checked proof and actual supplier
realization remain separate questions. [TASK.json](TASK.json) records the precise
first step and blockers; no physical or kappa claim follows from this package.
