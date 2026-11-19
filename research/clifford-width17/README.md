# Gaussian-dyadic four-qubit Clifford recovery at width 17

For the normalized tensor columns of the full four-qubit projective Clifford alphabet, every integer width **f ≥ 17** admits an exact left inverse over **Z[i,1/2]**. The previous sufficient width was 256. The reported complex threshold is 13, leaving four widths, 13 through 16, where Gaussian-dyadic recovery remains open. For the larger alphabet of all eight-qubit stabilizer rays, the complex independence threshold is exactly 17. [Previous dyadic inverse #7797](https://github.com/CrocSwap/integer-mult-bounds/pull/7797) · [Complex threshold #7766](https://github.com/CrocSwap/integer-mult-bounds/pull/7766)

The normalized observation is a linear combination of columns `(vec(U)/4)^(tensor f)`, with one fixed representative per scalar coset. For each target, a change to Bell coordinates sends that column's single-copy state to the origin basis vector. A length-16 binary code cancels the quadratic phases on each linear subspace of the support. Möbius inversion isolates the target. The seventeenth coordinate kills supports missing the origin. Dropping it gives a false positive even on a four-qubit Clifford, as the checker demonstrates with one rephased Hadamard and three copies of HS. [Construction and lower bound](PROOF.md)

The resulting ordered tensor row has 417,199 nonzero entries before the change of basis and squared Euclidean norm 73,190,789,644,335,724. Starting from this exact inverse, dyadic Richardson iterations preserve exact recovery. Using the uniform spectral bounds of Ali Romman's #7772, 8,192 steps give a second exact inverse within **2⁻⁷⁸** of the canonical decoder in operator norm. Its noise amplification is **below 3.021** on arbitrary normalized observations. This estimate uses #7772's spectral theorem. The width-17 construction and the larger-alphabet lower bound are self-contained. [Stability proof](PROOF.md#4-exact-dyadic-stabilization) · [Pinned spectral result](https://github.com/aliromman/integer-mult-bounds/blob/1398fbdca3536389d8ac3c8b3aaa408f03e8f6c2/research/clifford-threshold-conditioning/RESULT.json)

These are algebraic results. The Gram matrix has more than 12 trillion columns. No complete physical evaluation, storage, precision or routing cost is known for this decoder, and no change to the selected multiplication exponent κ is claimed.

## Reproduce

Run from the repository root with CPython 3.12 and the standard library.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-width17
```

- `verify.py` checks seven literal four-qubit Clifford matrices, their 49 ordered recenterings, and all 417,199 subspaces on a full-support example. It reconstructs the squared row norm and checks five faulty variants.
- `independent_check.py` builds the 24-element embedded one-qubit projective alphabet and tests 9,216 normalized identities including all four scalar phases at widths 17–20. It expands 1,094 tensor coefficients for two target rows and checks 48 literal contractions. It rejects three mutations and imports neither other checker.
- `check_stability.py` authenticates the retained #7772 numerical receipt, checks its 81 spectral rows and proves the numerical margins by exact arithmetic. A small normalized matrix checks the iteration and its error recurrence through nine successive exact inverses.

Each checker runs normally and under optimized Python. The proofs cover the full alphabets. The replays use finite fixtures and never materialize the full Clifford tensor map or the 8,192-step dense decoder. The spectral identification, all-width propagation and the complex threshold from #7766 are attributed inputs. The only external research data consumed by the checks are bundled in `references/conditioning-result.json`. [Replay manifest](VERIFY.json) · [Sources and credit](SOURCES.json)

## Research context and credit

Prepared by **apoursh** with substantial OpenAI Codex and separate agent assistance under Apache-2.0. Ali Romman's canonical obstruction motivated the alternative decoder question. His work and Nick Petalas's work on code-based phase witnesses are predecessors to the present construction. Their Clifford and character-table sources retain the credit to alephnan and other contributors. The proof cites the classical stabilizer normal form and related work on Clifford invariants and tensor powers. [Canonical obstruction #7792](https://github.com/CrocSwap/integer-mult-bounds/pull/7792) · [Phase witnesses #5635](https://github.com/CrocSwap/integer-mult-bounds/pull/5635) · [Doubly-even codes #5902](https://github.com/CrocSwap/integer-mult-bounds/pull/5902)

This follows the intermediate-width handoff from #7797 on upstream `e54523517d0f03e58352e647c403a5af3e525a57`. The historical revision-8 audit card concerns a selected multiplier assumption. This follow-up addresses the algebraic feasibility of the proposed decoder and leaves those assumptions open. [Public claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19752782) · [Task and overlap record](TASK.json)

## Open next questions

1. Does the Clifford subset admit a Gaussian-dyadic left inverse at width 16, or even at 13? Start by restricting the incidence equations to the maximally entangled Choi rays. The diagonal phase averaging used for the larger-alphabet lower bound requires a family closed under those phases.
2. Is stable exact recovery affordable at one named caller? Price a single Gram application, including coefficient precision, movement, scratch space and restoration, before extrapolating to the full iteration.
