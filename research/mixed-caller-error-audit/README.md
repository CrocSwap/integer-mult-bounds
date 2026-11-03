# Independent audit of the mixed caller's nine-bit error contract

This package independently checks Ali Romman's PR6473 field-error contract for
the exact PR6398 mixed caller: 34 fields, 18 independent commuting unitary stages,
and 570 instructions. The author already established nine sufficient uniform
guard bits and an eight-bit obstruction. The contribution here is a separate
source-bound exact audit of that quantitative result, after PR6433's endpoint
check; neither predecessor result is claimed as new.

Both new engines reconstruct every prefix and suffix matrix before reducing
its cells to bounds. Their receipts retain all 571 boundary row vectors, all
34 output coefficients for each of four error classes, and hashes of the full
cell envelopes. Equal monomials are combined before absolute values; each
cell takes the maximum of its four central-character bounds before row sums.
The 18 stage variables remain distinct. Source specialization to identity is
used only for the permitted adversarial lower witness.

The checked constants are prefix amplification 18, scalar-error coefficient
795/2, LOCAL 28, QUERY 18 and idle 28, with maximum common-tolerance row 943/2.
The literal normalizer has error-column squared norms 1, 2, 1, 1 for both signs.
An exact backwards-dual/forwards-noise execution attains307. Consequently
256<307<=the true worst amplification<=943/2<512: nine is the least uniform
integer guard count **in this field-error contract**. The upper constant is
not asserted optimal.

## Reproduction

CPython 3.12, standard library, no network, Git or predecessor imports:

```sh
python3.12 -I -W error -B research/mixed-caller-error-audit/verify.py
python3.12 -I -W error -B research/mixed-caller-error-audit/oracle.py
```

Repeat with `-O`. Defaults require strict retained receipts; `--emit` writes a
candidate to stdout without changing files. Both implementations authenticate
the five inert predecessor files before parsing. `SOURCE-PINS.json` records
exact upstream Git blobs and byte hashes; `SOURCES.json` records canonical
provenance. Author Python is retained for review only and is never imported or
executed. The new engines share the mathematical contract and source word;
they use separate code, polynomial representations and suffix constructions.
This is independent implementation corroboration with substantial OpenAI
Codex assistance, not independent human or proof-kernel acceptance.

## Audit evidence

The character-first elementary-operation engine and formal-C4 block engine
agree on all 571 × 34 prefix rows and all 571 × 34 suffix rows, all 136 class/output
coefficients, complete cell-envelope hashes, both signs of every normalizer
error column, and the full final 34-field state of the 307 lower witness.
Normal and optimized emissions are byte-identical within each engine.

A literal ADD sign flip at event 0 changes output 4/input 5 coefficient 0 to 6
on stage monomial D10 D11 at Q=1. Omitting normalizer event 37 accounting
changes scalar output 0 from 795/2 to 393. Three executed mathematical toys
diagnose suffix orientation, the cell-maximum/row-sum order and incorrect
stage specialization; these are explicitly examples, not caller faults.
The oracle separately checks C4 reduction and rejects a corrupted source byte.

## Meaning and limits

Each field is an arbitrary complex Hilbert space. Q and the stages must be
pairwise commuting unitaries, Q^4=I. Errors are bounded in the field 2-norm,
relative to the exact operation on the actual approximate input. Errors can
be adaptive and need not cancel. SWAP and Q_POWER are exact. For a normalizer compatible with translation pairs
(Q² acts as the pair swap), the literal four-operation calculation gives a completed defect at
most (9/2)e_s. The abstract propagation for arbitrary fourth-order Q assumes
that completed-normalizer bound explicitly; Q^4=I alone does not supply a
four-operation pair realization. These are premises, not validated properties
of an actual native backend.

No coordinate count, actual rounding implementation, native interior range,
finite tape layout, precision price, owned erasure, accelerated supplier or
complete compiler/outer admission is supplied. The307 errors are allowed by
the abstract contract; actual rounding need not realize them. This older
mixed caller is not the selected PR6030 word. The selected frontier, invoice
and all five inherited framework assumptions are unchanged.

## Source, overlap and credit

Canonical base 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority 8, selected 6030.
The error-contract source is PR6473 head 15a7e8d2e90f23977393613e6d0889614b144ad7.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363999).
Bounded live PR/Discussion checks distinguish PR6433 endpoint, PR6500's nineteen
LOCAL contacts, PR6499/6506 selected scalar execution, and PR6477/6478's other
precision models. Sparse history, hidden replies and unpublished work remain
unknown; this is not a novelty certificate.

ToikY with substantial OpenAI Codex assistance, Apache-2.0. Ali Romman retains
the PR6473 theorem, PR6398/6453 caller and PR6348 binary-caller credit; Cinna
Davis and the retained native/compiler lineage retain their source credit.
ToikY/PR6433 retains endpoint audit credit. Spectral decomposition, polynomial
norm majorants and linear error propagation are classical.

## Open next questions

- Bind one actual native implementation, coordinate count and rounding law to
  all four declared field tolerances. Freeze its complete producer/consumer
  interface before attempting a physical precision price.
- Prove native interior range, tape access, owned cleanup and all-size/compiler
  admission with a complete paid invoice. These do not follow from an abstract
  guard count or an endpoint identity.
- Obtain independent human or formal proof review of the dimension-independent
  error argument. Executing these finite exact polynomials is corroboration.
