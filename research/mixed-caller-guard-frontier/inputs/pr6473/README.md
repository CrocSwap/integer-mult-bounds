# Nine guard bits for the complete mixed caller

The actual PR6398 caller needs exactly nine uniform guard bits in the
field-error contract of [PROOF.md](PROOF.md). This caller is also used by
PR6453. Exact source-bound bounds give signal amplification at most 18
at all 571 instruction boundaries and final error at most 943/2 times
the common primitive tolerance. A separate forward error execution gives
307 times that tolerance, so eight guard bits cannot serve this contract.

The result replaces a coarse ordinary-operation growth allowance with a
concrete native-interface requirement. It does not raise kappa. The norm
is the maximum field 2-norm, not a coordinate norm. Native routines must
still meet the input error contract; their interiors, physical tape costs,
owned erasure and complete compiler admission remain open.

## Evidence and reproduction

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/mixed-caller-error-budget
```

Expected marker: `PASS_MIXED_CALLER_ERROR_BUDGET`. Registered normal and
optimized runs check the entire caller, all prefix and suffix bounds, four
central characters, the literal normalizer's input and error columns, and
the independent exact lower witness. [RESULT.json](RESULT.json) retains
all 34 output budgets for each error class. The complete endpoint identity
is checked as an input premise, not claimed as a new independent audit.

## Source, overlap and credit

Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The retained caller is byte-exact from PR6398 at
`dee2663ba0918be86993fd9d63c8d64b020f4c83`. Source pins authenticate it
before calculation. No source code from that package is imported.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19362995).
The initial full overlap cache covers 406 open PRs and 6,358 discussion
records. PR6433 independently checks the endpoint and normalization
identity; this package checks the complete error-injection contract.
The search cannot cover unpublished work or all historical code.

Ali Romman with substantial OpenAI Codex assistance, Apache-2.0. The caller
is by Ali Romman; PR6348's binary caller and Cinna Davis's native interface
retain their credit. ToikY's PR6433 retains the independent endpoint-audit
credit. Exact polynomial norms and linear error propagation are standard;
the new result binds them to this complete source and proves the least
uniform integer guard count in the stated contract.

## Open next questions

- Implement each native primitive with the four declared field tolerances.
  Bind coordinate count, rounding error and native internal growth before
  converting the field norm to a fixed-point format. These physical bounds
  are not supplied here.
- Use the row-specific budgets to choose different primitive precisions
  after an actual cost law is available. Without that cost law, a numerical
  precision allocation would not establish a complete improvement.
