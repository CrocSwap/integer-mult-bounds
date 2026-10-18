# Semantic-D bridge for the composed R439 A/B/star word

**Scoped independent application of an existing lemma; no new circuit or κ.**
The exact 10,652-ADD candidate of Gareth Davidson's [PR1122](https://github.com/CrocSwap/integer-mult-bounds/pull/1122)
satisfies the proposed semantic zero-frame D contract argued by woklerx in
[PR1194](https://github.com/CrocSwap/integer-mult-bounds/pull/1194).
That proof's original application fixed the 11,500-ADD PR1062 word; PR1122 also
changes A and its cleanup. This package checks the resulting continuation,
not just equality of D. The selected supplier remains unchanged.

## Exact application and evidence

Sources are main `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, PR1122
`a2551e70fce0cc34348f50f1a94e7cc4c80bbcbf`, and the substitution proof at PR1194
`2e39c98238f543d988f9efc1b076590a4b780dca` (`research/r439-semantic-d-contract-seed10/PROOF.md`).
Only PR1122's exact candidate is copied; `inputs/SOURCE.json` records its Git
blob and SHA-256. `SOURCES.json` pins the three consumed main inputs. No
predecessor semantic verifier, producer or optimizer is imported. The inherited
owner checker is intentionally reused unchanged, not presented as independent.

The independent set-valued calculation establishes, on all 661 input columns:

- D preserves arbitrary sources, helpers and target basis, adding exactly `N h`
  to the targets. Its source-free, common-zero-frame gates respect H1. D is
  identical to PR1062's and its operator also equals original PR589 D.
- For the **actual changed-A continuation** `W0=(A,scatter,B)`, the helper/source
  outputs contain no target columns, and targets have `V=I`, `J=I`, `K=N`.
- A proof-only word retaining the candidate's literal A/scatter/B/C and replacing
  D with PR589 D passes every original H1–H5 and U/J/K/C flag. The actual word
  retains exactly its two documented syntactic H2/K failures. Full geometry and
  endpoint checks pass on both.

Consequently the proof-only prefix and actual prefix have equal values **and
frames** before the identical continuation. PR1194's substitution argument
applies: XOR matrices act identically on every F2 module, so equality of the
zero-frame prefixes holds for arbitrary dirty streams under the inherited
common-frame interpretation. The original chronological lemma applies to the
proof-only word; replacing that prefix gives the same conclusion for this
candidate. This is an application of the predecessor's proof, not a new lemma.
The more general raw block identity alone would not justify frame-sensitive
execution; the literal original-D bridge is checked separately.

`RESULT.json` records N, all owner flags, both complete local bills and controls.
Independent literal COPY/ERASE execution checks both directions, including
arbitrary dirty inputs and clean copy-temporary lifetimes. Recounted values are:

| Quantity | PR1122 candidate |
| --- | ---: |
| ADDs / D ADDs | 10,652 / 5,548 |
| COPY / ERASE | 9 / 9, each copy rank 7 |
| Paid rank mass | 5,129 |
| Positive forward / reverse bounds | 15,223 / 3,910,388 |
| Local / nine-stage bound bits | 92 / 176 (caps 104 / 192) |

The profile is `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` and all ordered
register frame paths match PR589. The checks compare exact integers
`64 F^3 B^2 < 2^104` and `2^18 F^5 B^4 < 2^192`, not rounded bit counts.
All costs and savings above belong to PR1122 and its predecessors. The
proof-only D is not executed or billed as the candidate.

Nine controls reject an unrestored helper, residual target mixing, wrong dirty
compensation, neutral forbidden target feedback, neutral source access, neutral
nonzero-frame operations, changed raw J, changed raw V, and stale cleanup.
The last control **passes the full binary endpoint** but fails H4: semantic
endpoint success alone does not establish this inherited bridge. A neutral
restored helper pair is a positive contract control. Package tests run a minimal
relocation and reject candidate, dependency and receipt corruption.

## Reproduce

Python 3.10+ standard library only:

```sh
python3 -I -B research/r439-abc-semantic-bridge/verify.py
python3 -I -O -B research/r439-abc-semantic-bridge/test_package.py
python3 scripts/research_package.py --package research/r439-abc-semantic-bridge --check-only
```

Expected `PASS_R439_ABC_SEMANTIC_BRIDGE columns=661 ADDs=10652 controls=9 no_new_kappa`.
The verifier takes about one second on the tested macOS/Python 3.14.7 host.
`--write` regenerates the deterministic receipt after checking sources and
claims. The opt-in `VERIFY.json` registers bounded replay under Python 3.12.
Both commands pass under Python 3.12.14; its replay matches the receipt
generated under Python 3.14.7. The research test suite passes 20 tests with
one skipped test. Selected-source baseline binding also passes.

## Scope and overlap

Card `bit-helper-contract`, refined to a source-bound bridge application;
OS nonce `09c41251dd3913927a6d642281ba7824`. See `TASK.json` for the exact scope.
The final overlap snapshot covered 803 open PRs (including drafts) and 53
discussion records with complete pagination at 2026-10-13 22:24 UTC. This
literal search excludes arbitrary diffs and nested source files; it is not a
novelty certificate. Exact predecessor heads were rechecked unchanged.
The first prescribed PR1062 replay passed. PR1194 already supplied the general
lemma; PR1122 already supplied native 5/9/11-stage replay **including PR1062**,
so neither is claimed as a new result. This adds an independent executable
check connecting the proof to PR1122's changed-A candidate. Discussion #1290
instead relaxes target-feedback restrictions; H1 remains required here.

Native replay, full hosted emission/invoice, all-size compiler/common-label
realization, precision/tape, recovery and analytic transfer were **not run or
proved here**. PR1122's native evidence is credited, not freshly reproduced.
This finite application does not authorize selected-supplier adoption and does
not improve the paid moment or multiplication exponent. No human peer review
or proof-assistant formalization is claimed.

## Open next questions

Can this exact candidate pass complete hosted-supplier admission under the
semantic contract? First bind PR1122's native receipts and this bridge to a
fresh changed-word hosted emission/audit. Maintainer acceptance of the replacement
interface and complete physical/compiler/precision evidence are the blockers.
The same question is structured in `TASK.json`.

## Credit

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
Credit **woklerx / PR1194** for the semantic contract and chronological
substitution proof, **Gareth Davidson / PR1122** for the composed word and
native evidence, **Sagar Thakrar / PR1062** for B/star composition, **Sricharan
Vagvala / PR967** for helper stars, **Aaron Wang / PR1015** and **Ross Richardson /
PR923** for B circuits, **DreamingOfClouds / PR589**, **eumemic / PR555/543**,
**Zhihao Chen / PR425** and the retained scalar-interface/checker lineage.
See `NOTICE.md` for the copied candidate's predecessor notice.
