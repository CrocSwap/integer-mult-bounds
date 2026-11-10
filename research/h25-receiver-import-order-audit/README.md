# Receiver import order with a missing gate

The current control receiver can try to import `hashlib` before reporting a missing configuration, review, execution, or funding gate. Its validator still rejects unset gates when called. The distinction matters: the existing missing-gate regression recipe asks for rejection before any receiver import attempt, so a successful check against the older guarded receiver cannot qualify the current receiver.

This archive establishes that source discrepancy and an exact historical template that restores the early check. It is part of [the original verification investigation, PR #6321](https://github.com/CrocSwap/integer-mult-bounds/pull/6321); see [the maintained handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/6321#issuecomment-6713710045).

## Source argument

The [receiver retained by PR #6885](https://github.com/CrocSwap/integer-mult-bounds/blob/6f9457478d22fa31c1e26b98ca4ee1ed43129ac4/research/h25-selected-child-custody-repair/reference/native-child/variant_validation_v1.py.txt) sets the four gate variables, then imports `hashlib`, `json` and the ELF helper. Its missing-gate check lives inside `validate_variant_producer`. The immutable copy in `reference/deferred_receiver.py.txt` is that exact public file, SHA256 `37f12c53804047ac1f76474639e801802ded977126f33f3e64aabc7cc83864e5`.

Replace the three comments in its prelude with the original three-line conditional restored by `check_prelude.py`. This gives guarded template SHA256 `5e099fbe13f9e6f548a36ba2202bceef2f5d479bed85529ce57b26654f7c0a98`; every other byte is identical, including the later validator check. Substituting four indexed gate declarations produces the retained private test image at `e06d247513370fb6ea3a2af9d8e490fcde26d1988885ff669b26edb57586375e`. The inverse restores the whole guarded file byte for byte.

For each of the four cases, only that gate is `None`; the other three values are present. In the deferred template, assigning those values leaves the first executable effect after the declarations as an import attempt. In the guarded template, the same declarations feed a disjunction of four identity tests; the chosen `None` makes it true and the exact `RuntimeError` precedes all three imports. With all gates present, the branch falls through to the first import. The branch uses ordinary `if` and `raise`, which do not disappear under Python optimization. These statements concern the receiver namespace's import attempts, including an attempt for a module already loaded elsewhere in the process.

## Reproduce the source check

```sh
python3 -B research/h25-receiver-import-order-audit/check_prelude.py
```

The checker verifies the original SHA256, exact replacement, full unchanged suffix, three import statements, derivative SHA256 and full declaration inverse. It reads the subject as text and parses its AST. It imports, compiles and runs none of the receiver, target, fixture or native sources. There is no replay registration in this archive.

## Open next questions

The guarded template would reject ordinary import with all four source declarations left as `None`. The [existing selected child](https://github.com/CrocSwap/integer-mult-bounds/blob/6f9457478d22fa31c1e26b98ca4ee1ed43129ac4/research/h25-selected-child-custody-repair/frozen/implementation/component_stage_entry_v1.py) imports its modules before the one-time binding step. Restoring the guard alone therefore breaks that boot path.

The next concrete check is whether the original owning parent's four genuine gate values can be pinned as literals in the actual staged receiver **before** import, with an acyclic dependency on the configuration, review, launch policy and reservation. The existing [literal inverse verifier](https://github.com/CrocSwap/integer-mult-bounds/blob/6f9457478d22fa31c1e26b98ca4ee1ed43129ac4/research/h25-selected-child-custody-repair/reference/native-child/configured_inverse_v2.py.txt) gives a byte-level relation, not independent issuance or launch authority. After that review, the original parent would still need to bind the exact staged image and independently authorized private instrumentation, retain the actual error and zero-import observations for all four cases in each mode, and preserve the original mode order and cost admission. No such control run or comparison is established here.

Predecessor credit: [PR #6885](https://github.com/CrocSwap/integer-mult-bounds/pull/6885) supplies the selected receiver and original Root/stage/owner boundary; [PR #6882](https://github.com/CrocSwap/integer-mult-bounds/pull/6882) supplies the earlier component judgement context. The local historical gate-check recipe supplies the exact guarded template and private-image pin. This audit and checker were prepared with AI assistance.
