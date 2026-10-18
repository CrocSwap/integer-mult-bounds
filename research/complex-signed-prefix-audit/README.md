# Selected PR1094: signed prefix precision audit

Contribution: [PR1282](https://github.com/CrocSwap/integer-mult-bounds/pull/1282).

The unchanged R480 programs have exact signed scalar/Horner prefix maxima
**131088 forward and 1154896 backward**, requiring sufficient **18/21-bit**
envelopes rather than the retained positive-recurrence estimates of 52/68
bits. Exact squared inequalities also cover partially stored real/imaginary
components within the same 18/21 bits.

This is a **conditional precision-interface audit**, with no new κ. The
[prefix norm proof](PROOF.md) is a corollary of the credited Lemma G
common-frame conjugation theorem. It specifies why unitary labels, exact
recipes and equal labels at ADD are required, and gives exact counterexamples
to omitting them. Cancellations are evaluated before taking absolute values.
The existing larger bound remains valid.

Under the inherited global execution/precision hypotheses, replacing only
the local term in the selected formula gives **397 → 350 sufficient bits**.
The production payload remains **512**; the supplier, paid profile, selected
record and all predecessor files are unchanged. This is not a fixed-point
roundoff theorem or a new physical compiler admission.

## Evidence and reproduction

Python 3.12+ and the standard library, from the repository root:

```sh
python3 -I -B research/complex-signed-prefix-audit/verify.py
python3 -I -B research/complex-signed-prefix-audit/controls.py
python3 -I -B research/complex-signed-prefix-audit/source_check.py
python3 -I -B research/complex-signed-prefix-audit/test_package.py
```

The first command checks all **39,386 scalar prefixes** with sparse rational
and dense integer engines; both 704-column endpoints; frame/wrapper incidence;
960 wrapper unit rows; and Horner scratch. Separate reverse functional and
literal primitive executions certify both attaining inputs and reproduce
**198766/198814** real-component primitive counts. EXPECTED.json records the
complete peak rows, all phase maxima and portable trace digests.

The controls check 216 exact unitary-frame words, 2,376 prefix cuts and 57,024
matrix entries, four mathematical boundary examples, and eight selected-word
or bound controls. In particular, omitting scratch underestimates the actual
forward peak: **131088 > 131072**. The source command runs the byte-identical
original driver with assertions enabled and all 25 inherited mutations;
its entire regenerated local receipt matches the archive. The package tests
cover dyadic cancellation, strict bit boundaries, read-only isolated/optimized
relocation, source/pin corruption and a one-unit understated receipt.

The opt-in registration is:

```sh
python3 scripts/research_package.py --package research/complex-signed-prefix-audit --check-only
python3.12 scripts/research_package.py --package research/complex-signed-prefix-audit
```

See [VALIDATION.md](VALIDATION.md) for the actual environment and results.
The original driver is run in a temporary directory; other default commands
are read-only. `verify.py --output NEW_PATH` writes a checked receipt and
refuses to overwrite an existing file. Immutable source archives are pinned
byte-for-byte; regenerated receipts are compared as decoded JSON.

## Scope, task and overlap

Base `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`; selected PR1094 source
`0fc329d0bec93ca7cd288eaea1295172e8789810`, parent PR1087
`589d1cedf5ef5f231182f4ec86408616311a8af0`.
The fresh OS nonce `9e66acdf5b86cc4b02a0d212138d7b3e` assigned adversarial audit,
`uniform-transfer-audit`, catalogue revision 2. The baseline binding command
passed before refinement. [TASK.json](TASK.json) records the bounded question,
refinement and open questions; [SOURCES.json](SOURCES.json) binds every external
input and historical task provenance.
[Discussion #1260](https://github.com/CrocSwap/integer-mult-bounds/discussions/1260)
records the scoped claim and result.

The initial replica-prefix idea was stopped when overlap checking found
[PR821](https://github.com/CrocSwap/integer-mult-bounds/pull/821), head
`6b832a6ba4dce8dd6e2fb0897dd4543364b932f8`. Its replica-norm argument is not
repeated here. Other nearest work is:

- [PR1184](https://github.com/CrocSwap/integer-mult-bounds/pull/1184),
  `2f1c9e0e671bb10aecd452e18449130b0601932d`: faster execution of the same
  original positive-envelope checker. Integer-row arithmetic is credited
  prior technique; this package's result concerns the signed physical norm.
- [PR734](https://github.com/CrocSwap/integer-mult-bounds/pull/734),
  `ba76ba3321d000c8996b0b254bcf0d7260e1bbb6`: changed signed-Horner circuits
  preserving the older envelopes. Here the unsigned source circuit is unchanged.
- [PR745](https://github.com/CrocSwap/integer-mult-bounds/pull/745),
  `fc6ebccca3bd61a6eaf6ec3fcbf2e99d2888c35c`: reverse endpoint checking and
  a private-clear witness. Reverse-mode checking is credited prior technique.
- [PR1255](https://github.com/CrocSwap/integer-mult-bounds/pull/1255),
  `add1e2673ef000c097ec0fd70058e644af048d6b`: exact residual chart phase;
  this package leaves charts fixed and audits a different norm implication.

The fresh search covered open PR bodies, Discussion bodies/comments and
local package notes; it does not establish worldwide novelty. The scalar
and frame-local checks are fresh. Native Clifford replay, whole global
controller/owner replay, cold supplier regeneration, Lean, full compiler,
roundoff/tape/exact recovery and analytic transfer are not run or discharged.
The source record's retained conditions still apply.

## Open next questions

1. **Formalize the prefix norm and partial-store corollaries.** This would
   make the precision-interface statement reusable alongside Lemma G. Start
   with `Stream.conj_matrix` for an arbitrary prefix and diagonal unitary
   labels, then the orthogonal projection inequality. The blocker is a
   scoped Hilbert-norm extension to the current algebraic formalization;
   finite Python examples are not a formal substitute.
2. **Admit the signed envelope in the production invoice.** It may reduce
   conservative reserves for future constructions. Start by integrating the
   signed-row checker and exact split-component inequality into one provider
   recount, preserving all source/admission controls. Complete native/global
   replay and the precise internal compiler/precision obligations are still
   required. This package changes neither the 512-bit charge nor κ.

## Credit

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance in the
proof, implementation, checks and writing; no subagents or independent human
review. Apache-2.0. The conjugation theorem and scalar interface are inherited
from Zhihao Chen/PR425 and Lemma G/PR484 (DreamingOfClouds); whole-helper and
normalization work credits chafreaky/PR458, Dugongue/PR471, and the Lemma G,
Lemma A and hyperplane-end formalization authors. Rohan Arun supplies the
selected PR1094 placement; Jeremy Kothe, Hao Yan (icekylinx), Josie Elliston,
Douglas Colkitt and the retained gauge44/Clifford/compiler lineage supply
this provider and its original audits. Sagar Thakrar's adjoint/lowering work,
PR734's authors, and the PR1137/1156/1184 integer-row work retain their credit.
The norm corollary is standard linear algebra; no priority claim is made
for that argument, signed-row arithmetic or reverse functional replay.
