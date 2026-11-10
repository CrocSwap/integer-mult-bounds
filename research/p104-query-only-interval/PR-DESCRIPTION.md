## Problem and result

DreamingOfClouds' E-free caller in CrocSwap/integer-mult-bounds#6937 avoids
empty-mask main productive credits but introduces two QSELF operations. The
earlier public owned lowering gives them relative typed-IR lifetimes while
leaving their new physical token registry uninstalled.

This package replaces the exact separated interval 457..575, including all
intervening source operations, by a word using three existing QUERY(-1)
operations and existing ADD/SWAP/LAMBDA operations. That equals the interval's
original paid budget of two QSELFs and one QUERY. No new helper, initialized
role, target credit or operation type is introduced. The generated complete
caller has 3,095 events and zero QSELFs.

## Exact theorem and novelty

For commuting Q,D1,...,D18 with Q^4=I, the new caller has exactly the original
operator on all 76 independent inputs. All D variables stay formal. The new
four-input three-query identity is joined to the actual separated sites by
an explicit even basis and source conjugation; a same-cut pair identity alone
would miss the intervening query's contribution. The noninvertible D9 operation
is never inverted. The source LAMBDA is a unit in both q^2 sectors.

Credit for the E-free source and prior QUERY-only feasibility suggestion stays
with DreamingOfClouds and #6937; that source reports a gadget and says its whole
QUERY-only caller was not built. The unchanged local native source comes from
CrocSwap/integer-mult-bounds#6936. The public owned-lowering package at
[4e2fd1b6](https://github.com/CubeJerry/integer-mult-bounds/tree/4e2fd1b6abed49c202a057fd5c73ead0a460f976/research/p104-qself-owned-lowering)
supplies the exact source semantics, formal engines and invoice baseline.

## Complete costs and kappa status

Every rankwise target and paid count is unchanged, so the full moment
polynomial is identical at every kappa. Totals remain T=23,050 and P=117,846;
the surplus is 1,520 and paid rank mass 317,324. The conditional inherited
ordinary invoice rises from 811,461,936 to 826,265,904, leaving 173,734,096 below
the stated 10^9 cap. The 104 additional A events and 28 additional A LAMBDAs
are explicitly charged. All 416 outer jobs are now existing QUERY lifetimes.

**No new kappa; no unconditional theorem; selected certificate unchanged.**
The historical scalar/routing tariff remains conditional. New intermediate
formats, signed headroom, rounded errors, physical bit-tape rates, retained
backing and literal compiler/provider bindings require further proof. Existing
opcode support does not establish a physical full-caller execution.

## Source pins and verification

- Canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
- #6937 head `a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`.
- #6936 head `03626137d0bd57f09b0bf9597376183ce6fa9683`.
- New exact 38-input interval matrix with unrestricted D multiplicities.
- Reused full76-input forward certificate and separate backward covectors;
  all 18 D variables remain formal, with exact q^4 quotient coverage.
- Eight algebra failure controls plus a fourth-query paid-budget control.
- Registered normal and optimized suites, committed-byte/export checks as
  recorded in `REVIEW.md`; no selected nine-axis physical caller run claimed.

```sh
python3 -B scripts/research_package.py --package research/p104-query-only-interval --check-only
python3 -B scripts/research_package.py --package research/p104-query-only-interval
```

The package includes the complete generated caller, exact patch, proof,
source capsule, invoice, receipts and structured open next questions.
Prepared for **@CubeJerry** with substantial OpenAI assistance in mathematical
derivation, implementation and verification; separate AI/code-assisted reviews
are not human or proof-kernel acceptance. Predecessor notices remain intact.
