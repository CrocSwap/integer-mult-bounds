# Independent PR5405 controller ceiling via exchange and discrete convexity

Every invoice in Ali Romman's fixed PR5405 FULL/QUERY prefix/suffix controller family has strictly positive paid-minus-target moment for **0.00302728825 <= κ < 1**. This package independently checks the three exact rational signs needed by the retained exchange and strict-discrete-convexity proofs, and separately audits the normalized monotonicity extension. It answers a scoped fixed-family ceiling question. It supplies no κ gain, physical/native/compiler admission, global circuit optimum, formal-kernel theorem, independent human review or transfer to PR5402.

The exact source head is `314b56a6c0056c2358538f072c6fde9d365be44d`, retained against canonical main `1ec1119972c9aefe42525172d07b332fcff81cb4`. The premise is source equation (1), the fixed paid/helper profiles, rank-eight stages, rank-one query price and prefix/suffix idle law. Derivation from the original Laurent/native controller and its framework assumptions remains separate. No selected record is changed.

## Proof and scope

Read [the full independent proof](numerical/PROOF.md), [the exchange reduction](numerical/inputs/5405-concavity-exchange-reduction.md), and [the all-n discrete-convexity proof](numerical/inputs/5405-discrete-convexity-three-value-gate.md). The exchange argument reduces every source invoice with n FULL stages to an attainable canonical invoice C_n. Strict discrete convexity on every nonnegative integer, including the small-count junction, then makes the following signs sufficient:

| Exact quantity | Strict rational bound |
|---|---:|
| C18 | > 0.000000014914967918767741908079 |
| C18−C17 | < −0.271338621904872494155700553536 |
| C19−C18 | > 0.022748156490424972863108432493 |

These displayed decimals are rationals with denominator 10^30. The raw receipts retain finer integer endpoints over 2^256. They establish the unique minimizing FULL count n=18 and positivity for every n at κ0=.00302728825. A separate normalized whole-invoice monotonicity argument, with the n=0 and zero-partial-count cases explicit, extends this conclusion to κ0<=κ<1. The finite tiny-mask checks are indexing controls; all-n coverage comes from the analytic proofs.

The new standard-library engine implements directed integer log/exp intervals with rigorous remainders. It independently reconstructs the complete invoice from paid/target histograms, checks 456 tiny invoice identities, verifies canonical coefficient identities at n=0,...,5 and 16,...,20, and rejects changed source bytes, reversed sign, a missing 112-rank-one QUERY invoice, omitted full-path targets and a changed paid-profile coefficient. Omitting targets is numerically favorable, so that control must fail accounting identity rather than a final sign. It imports no original numerical engine and runs no author 10,290,000-state DP, native/cold replay or Lean process.

[The independent read-only audit](audit/REPORT.md) records its exact scope and final freeze. It is an independent agent check, with no claim of human acceptance.

## Source binding and correction history

The original source is retained in [original/PROOF.md](original/PROOF.md), Git blob `5ad89d4ba1836d47798bdb856e3726c70a7b1922` (10,029 bytes; SHA256 `77dc9ce552be7dc9c9a32850c2f2cf0eff92cfe2e0a0e316db210a1667a8d32b`). The monitor copy consumed by the frozen theory/numerical work is 10,030 bytes, SHA256 `5c82c9f1650b0ffb352f2aa7eaac3aa283754028e41cd85d1ee848af9d18cd37`, exactly the original plus one LF. The wrapper checks this representation bridge without replacing either frozen source. [Git-free origin proofs](origins/) authenticate the raw commit and every tree edge to the source blob; canonical guidance, catalogue and selected-record provenance have their own origin proofs. The PR head is not represented as a canonical ancestor.

The raw v1 and v2 receipts and exact executed checkers remain preserved under [numerical/receipts](numerical/receipts/). The independent auditor identified that v2's acceptance `assert` statements disappear under optimized Python. V2's ordinary arithmetic endpoints remain retained; v3 supersedes its acceptance checker with explicit require/raise predicates. The final v3 ordinary/optimized runs agree on every scientific output and the earlier arithmetic endpoints. [RUNS-v3.json](numerical/RUNS-v3.json) and the frozen manifests preserve this correction. No historical receipt is silently repaired.

[INTEGRITY.json](INTEGRITY.json) inventories retained scientific/source/theory/audit/metadata bytes. The wrapper pins that inventory, authenticates both source representations and Merkle origins, then reruns the small independent engine in a temporary directory and compares every scientific result; environment/timing fields are excluded from scientific equality. A changed-byte control and a forged-tree control exercise authentication. Canonical source pins in [SOURCES.json](SOURCES.json) are historical provenance; every scientific input is retained inside this package, so a Git-free export runs offline.

## Reproduce

From the repository root:

```sh
python3 -B scripts/research_package.py --package research/controller-ceiling-convexity
python3 -B scripts/check_research_commit.py --package research/controller-ceiling-convexity --check-source-history
```

The registered command pair runs the same explicit acceptance conditions in normal and `-O` Python. Each independent arithmetic run takes about 0.1 seconds on the recorded Linux workstation, within a 60-second/256MiB engine cap. This bounded wrapper execution is separate from the original expensive author replay. There are no third-party Python dependencies.

In an extracted Git-free bundle:

```sh
python3 -I -B research/controller-ceiling-convexity/verify.py
python3 -I -O -B research/controller-ceiling-convexity/verify.py
```

Add `--integrity-only` to authenticate frozen inputs, exact origins and corrections without arithmetic replay. Publication-byte/source-history checks and export integrity are transport checks; hosted CI and maintainer selection remain distinct.

## Open next questions

The structured questions in [TASK.json](TASK.json) identify relevance, a feasible first step and blockers. A human or formal-kernel reviewer can check the exchange inequalities, the small-count convexity junction and the rational remainder derivations. Binding the original physical/native controller to equation (1) is a separate admission task. Escaping this obstruction requires a changed premise and a complete new bill, such as provider/consumer contract, stage rank or idle law; the scalar signs do not transfer to changed-profile PR5402.

## Credit

Ali Romman supplied PR5405's invoice family, original unbounded ceiling and DP, and the owned/transposed local profile. Preserve Cinna Davis's paired path/query controller, Cao Yifan's native source, zxv's interval/preflight and compiler/precision lineage, Chris R's prior controller screening and independent admission, Dugongue's frames and compiler contributions, Jacob Alan Sussman's recursion, and all retained native/helper/compiler/analytic contributors and source notices. The root coordinator proposed the exchange and discrete-convexity conjectures; the sole Astra theory worker supplied the frozen independent analytic proofs. The successor worker independently reconstructed the numerical invoice, implemented the new rational engine and audited normalized monotonicity; a separate agent audited the resulting proof and acceptance controls.

New independent research, review and packaging by **Chris R / Clear1nsight, with substantial OpenAI Codex assistance**. New work is Apache-2.0. [The original source notice](original/source/NOTICE.md) and [canonical LICENSE/NOTICE](canonical/) remain unchanged. No new construction priority, independent human review or global theorem is claimed.
