# Whole selected-word stochastic precision

**Conditional precision theorem; no new kappa.** For the exact selected
PR6030 word, a conditional mean-zero completed-error contract certifies
13 guard bits for each individual RMS error. A stopped Hilbert-martingale
bound certifies 16 guard bits with failure below 2^-41 for all fields at
all prefixes. The matched absolute-error certificate needs 17 guard bits.
These are different guarantees, not least physical rounding precisions.

[PROOF.md](PROOF.md) states the contract, exact source, all-parameter proofs,
zero-input boundary, attribution and limits. [RESULT.json](RESULT.json)
contains the exact signed-transfer ledger, rational tail certificate and
rejection controls. The current selected conditional kappa stays 0.003125804;
all five inherited framework assumptions remain.

The input has 22,803 events and 799 fields, including 770 arbitrary public
inputs. Fraction and integer arithmetic agree on every ideal operand
weight. Forward and transpose engines agree on every final coefficient and
score. All peak rows have reverse checks. Exact adaptive-noise fixtures
exercise feedback, conditional randomness, COPY and reset semantics.
No predecessor executable is imported or changed.

## Reproduce

From the repository root, CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/selected-whole-word-stochastic
python3.12 -B scripts/check_research_commit.py --package research/selected-whole-word-stochastic --check-source-history
```

The registered commands run normal and optimized checks with warnings as
errors. Expected markers are `PASS_SELECTED_WHOLE_WORD_STOCHASTIC`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The verifier compares the receipt without writing it. `--output NEW_FILE`
creates a separate receipt and refuses to overwrite an existing file.

Conditional mean-zero native errors, exact COPY/INIT/CLEAR and deterministic
unitary decoded charts are explicit premises. No physical unbiased native
rounder, exact dirty restoration, complete multiplier or selected replay is
claimed. Guard bits describe the relative allowance u, not a materialized
integer format or a complete tape/storage bill. Prepared by Ali Romman with
substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

Bind one actual native implementation to the completed conditional mean-zero
contract, including internal rounding and random access costs. Price exact
restoration of dirty data and every owned reset before using the theorem in
a supplier. A complete caller must also supply its invocation count and
recovery probability budget. The source-specific constants do not transfer
to a different word without a new ledger.
