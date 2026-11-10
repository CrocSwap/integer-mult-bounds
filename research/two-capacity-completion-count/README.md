# Closed count for two nonnested capacities

A prescribed injection and two simultaneous capacity constraints admit an
exact finite-field completion count with at most n+1 summands. This replaces
the general exponential kernel-lattice count for this two-capacity case.
The formula retains the coupled prescribed-image condition; separate capacity
counts cannot be multiplied.

Read [PROOF.md](PROOF.md), [count.py](count.py) and [RESULT.json](RESULT.json).
ToikY's [PR6535](https://github.com/CrocSwap/integer-mult-bounds/pull/6535)
provides the prior feasibility theorem and quotient construction. Ali Romman's
[PR6533](https://github.com/CrocSwap/integer-mult-bounds/pull/6533) provides the
prior general all-rank count. Neither result is claimed as new here.

## Scope and evidence

The formula is proved for all finite fields and dimensions. The basis extractor
uses prime fields. Literal GL enumeration checks all 287,431 normalized
contracts over F2 through dimension3 and F3/F4/F5 in dimension2, including
64,525 positive counts. The F4 oracle uses its actual field multiplication.
Seventy-eight arbitrary-image cases agree with the retained kernel-lattice
checker. Sixteen dimension120 formulas and two actual dimension48 contracts
match separate product counts. Named obstruction, nonzero-delta, factor
omission, invalid-input and source-corruption controls are retained.

This is unrestricted GL counting. It does not supply a native/symplectic map,
signed phase, actual selected contact, sampler, physical cost or new kappa.
The source heads and exact files are pinned in [SOURCES.json](SOURCES.json).
The proof and notice from PR6535 are inert retained evidence. Only PR6533's
exact linear algebra and bounded independent count are executed.

## Reproduce

```sh
python3.12 -I -Werror -B research/two-capacity-completion-count/verify.py
python3.12 -I -O -Werror -B research/two-capacity-completion-count/verify.py
python3.12 -B scripts/research_package.py --package research/two-capacity-completion-count
```

The standard library is sufficient. There are no external runtime files.
Large exact counts are stored as hexadecimal integers, so decimal conversion
limits do not affect the receipt. This is not a runtime benchmark.

## Open next questions

Can these counted choices give an exact uniform sampler with a polynomial
random-bit and arithmetic bill? Start by sampling each weighted intersection
term and each independent lift. A rejection or sampling bias must be charged.
No sampler is included here.

Can an actual shared native contact reduce to these two capacities? Extract
its fixed images and both target subspaces, then check the signed/symplectic
constraints and the complete physical invoice. A positive GL count is only
a necessary interface step for such a consumer.

## Credit

New count, proof and executable checks: Ali Romman with substantial OpenAI
Codex assistance; no subagents. Credit ToikY PR6535, Nick Petalas PR6489/4919,
Ali Romman PR6533, Brian/JoyboyBrian PR5020, Cao Yifan/intqwq PR4610,
codyw912 PR4735, Cinna Davis, Dugongue, zxv, Jacob Alan Sussman and the
retained native/compiler authors. The original PR6535 notice is retained.
Gaussian coefficients, subspace graph counts and basis extension are classical.
New work is Apache-2.0. Independent scientific review remains open.
