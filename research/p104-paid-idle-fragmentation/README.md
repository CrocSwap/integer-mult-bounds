# Two paid idle fragments improve the complete P104 caller

This package records **conditional κ = 0.00330720**, a gain of 0.00000300 (+0.09079%) over [PR6716](https://github.com/CrocSwap/integer-mult-bounds/pull/6716), and the separate **ordinary BIT dependency saving 0.00376669**. All five framework assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`.

The actual source is the unchanged native supplier retained by PR6716 at `a467457692bc9e11113d9b2e2e34ea8ffb553b58`, with [PR6702](https://github.com/CrocSwap/integer-mult-bounds/pull/6702) source `edd6a37a9ff87b254fb7466184348d1432d0c8c0`. Two paid idle fragments and two independent fresh-input handoffs change the complete caller. No selected-result file is changed.

The immutable export in [frozen/](frozen/) contains proofs, literal callers, invoices, constructors, retained source dependencies, notices, validation logs, and the original 215-file manifest. Its scientific bytes have not been edited for packaging. [FINDINGS.md](FINDINGS.md) separates paying constructions, algebraic exclusions, finite pilots, and reopening conditions. [supplemental/](supplemental/) preserves late exploratory receipts recorded after the original positive archive was frozen. Those late pilots are not part of the portable mathematical replay.

## Reproduce

From this package directory, Python 3.11 or later, standard library only:

```sh
python3 -I -B frozen/verify_bundle.py
python3 -I -B frozen/allocation_tail.py
python3 -I -B frozen/internal_prefix_lemma.py
```

The bundle runner authenticates its inputs and replays in a disposable copy. Default replay fully checks the changed complex caller and both BIT admissions while reusing the hash-bound native evidence. The other two commands check the all-size allocation ceiling and the exact prefix-matrix fixtures. The generic registered-package workflow is not enabled by this export; use the direct commands above.

An optional full unchanged native replay is available:

```sh
python3 -I -B frozen/verify_bundle.py --full-native
```

The original source replay and portable Python 3.11.11/3.14.5 logs are retained under [frozen/validation/](frozen/validation/). Fresh packaging checks and their coverage are recorded separately under [packaging-validation/](packaging-validation/). Neither implementation independence nor successful replay constitutes independent external scientific admission.

## Open next questions

1. Independently review the two [literal retirement witnesses](frozen/two-fragment/RETIREMENT-WITNESSES.json), arbitrary input ownership, and absolute phase at the second handoff. First inspect [PROOF.md](frozen/two-fragment/PROOF.md), then [independent.py](frozen/two-fragment/independent.py). External review is outstanding.
2. Discharge the retained all-size framework assumptions. The finite certificates and compiler specification are evidence within that conditional framework; they do not materialize the enormous uniform multiplier.
3. Reopen construction search only with a changed root, source schedule, or legal source-bound unit pair and a profitable complete bill. Allocation-only extensions of the exact complex root are retired at their raw ceiling; tested unsuccessful rewrite, internal-fragment, and promotion branches are parked. No supported next construction action is currently recommended on those branches.

## Credit and license

New construction and transfer developed with substantial OpenAI Codex assistance for [zxv](https://github.com/zxv). Original predecessor source, licenses, and full attribution remain in the frozen notices. The package retains the [PR6716](https://github.com/CrocSwap/integer-mult-bounds/pull/6716), [PR6702](https://github.com/CrocSwap/integer-mult-bounds/pull/6702), [PR6545](https://github.com/CrocSwap/integer-mult-bounds/pull/6545), and [PR6348](https://github.com/CrocSwap/integer-mult-bounds/pull/6348)/[PR6398](https://github.com/CrocSwap/integer-mult-bounds/pull/6398) contributions and their nested lineage. New contributions are Apache-2.0.
