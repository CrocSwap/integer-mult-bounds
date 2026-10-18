# Batched integer lifting with a specified clean-work bound

I construct a new order of the reversible Gaussian integer lifts with core
time

    O(N r^(2-997/600000)),  997/600000 = 0.001661666...,

at linear precision W=Theta(r), N=2^n and n=Theta(r). I retain the
earlier selected exact C-layer construction and its physical/compiler
premises. I charge additional clean workspace

    O(N r^(1197203/600000)) + fixed compilation storage.

This is a conditional standalone core bound, not a new multiplication
exponent or native P104 supplier. I use clean computation history and do
not claim linear space or arbitrary dirty-helper hosting.

## The changed backend contract

Ross Richardson's [PR3072](https://github.com/CrocSwap/integer-mult-bounds/pull/3072)
reduces the narrow correction cost if an exact source-preserving backend
can process its dense local cubes. The selected C-layer interface instead
needs spaced axes and exponentially long coefficient records. Adding those
fields to an isolated cube would expand its volume.

I process all existing cosets together. I retain a permanent low-address
suffix as coefficient fields and process the other axes in offset blocks
of complete K-bit chunks. Reclassifying those bits changes no flat address
and moves no payload. I defer fewer than ell+K axes to direct lifts and
keep the short-group charge in the bound.

This defines a new nonlinear word. I supply its exact inverse by reversing
that order, while its ideal C tensor remains unchanged. Both directions
have absolute error at most r sqrt(N/2) in integer units. The finite
noncommutation control rejects identifying the new word with the old one.

I instantiate both scaled linear orientations from the earlier exact C
endpoint, including normalization, exact output shifts and real/imaginary
exchange. I then charge compute-copy-reverse history to obtain protected
XOR oracles. Four such oracle calls implement a complete in-place batch.
Read [PROOF.md](PROOF.md) for the full time/space ledger and source premises.

## Evidence and reproduction

Run from the repository root with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/batched-spaced-lifting
```

I check 5,250 finite plans, signed predecessor-pair identities, complete
ambient arrays through 512 Gaussian entries and 257-bit inputs, both
scaled orientations, exact paired return, private macro cleanup and the
rational exponent comparisons. Controls reject the old inverse order,
insufficient scaling guard and omitted backend cleanup. I also check the
Hilbert-error inequality on signed fixtures.

The executable uses direct linear evaluation as its semantic oracle. It
does not execute or benchmark the fast physical C algorithm or its
reversible trace. The written construction supplies that conditional
implication; the finite checks do not prove an asymptotic claim by
extrapolation. `RESULT.json` binds complete typed receipts, and the
registered checks include optimized Python controls.

## Scope and credit

I credit Tekalign's PR3025/3033 literal floor word and residue split, Ross
Richardson's PR3072 blocked evaluation and cleanup construction, and the
PR2287/PR2899 selected-layer and ordinary-interchange sources. Their exact
pins and retained attribution appear in [SOURCES.json](SOURCES.json).
I use Bennett's classical reversible simulation with an explicit history
charge; I do not claim that simulation or the inherited algebra as new.

I add the all-coset, permanent-suffix contract, the new spaced lifting order,
its exact scaled-linear source instantiation and the complete standalone
time/space deduction. External monomial wrappers, the collector consumer,
clean-space hosting and full supplier admission remain open. I leave the
selected frontier unchanged.

## Open next questions

- Price one actual native wrapper and collector around this changed-order
  core. First verify that the caller accepts this rounded map and its exact
  inverse, then add its complete storage, access and consumer bill. The
  frozen P104 profile obstruction remains in force for its original model.
- Reduce clean history while retaining the proved time exponent. First
  select a named backend subroutine and account for its recomputation and
  cleanup. A space improvement must preserve the complete tariff; the
  current theorem already includes its larger history cost.

I coordinated the investigation in
[2750#18986351](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18986351).
Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including analysis subagents. Apache-2.0. I claim no independent human or
proof-assistant verification.
