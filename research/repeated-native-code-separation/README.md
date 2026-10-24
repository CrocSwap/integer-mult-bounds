# Repeated native code separation through degree 32

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

Reusing the same two native stages does not give a short scalar decoder
for the pinned center-free code. All 64 nonconstant reduced projection
words of degree at most 32 are independent after projection away from
the central address. The exact Gram determinant is 52006 modulo 65521.

This gives an all-width terminal obstruction for every reduced product
of the two codes with at most 32 alternating power blocks and arbitrary
nonzero integer exponents. It permits repeated stages, unlike the
fresh-stage theorem in [PR #5408](https://github.com/CrocSwap/integer-mult-bounds/pull/5408).
For each such product, the required scalar ADD count grows at least as
2f minus a product-dependent constant. The constant is not asserted to
be small.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[MOMENTS.json](MOMENTS.json) and [SOURCES.json](SOURCES.json).
This is a scoped negative result. It gives no cheaper circuit, no new
complete kappa bound, and no selected-frontier change.

## Reproduce

The registered replay uses Python 3.12 and NumPy 2.5.4. From the repository
root, with that dependency installed, run:

```sh
python3.12 -B scripts/research_package.py --package research/repeated-native-code-separation
```

Expected scientific marker:

```text
PASS_REPEATED_NATIVE_CODE_DEGREE32_NO_NEW_KAPPA
```

The full replay reconstructs all 7,280 moment entries from the dense
112-owner matrix, checks the source bytes and mode identities, and checks
the determinant by two exact algorithms. The registered optimized pass
checks the saved certificate and controls; it does not repeat the dense
replay. The dense binary64 products are exact integer calculations below
2^24, as proved and checked in the package. Rank is computed modulo a
prime, not with a numerical tolerance.

The separate C++17 replay uses the eight-mode factorization and integer
arithmetic. It needs a C++17 compiler. Use fresh output paths:

```sh
python3.12 -B research/repeated-native-code-separation/verify.py --native-input /tmp/repeated-native-source.txt
c++ -O3 -std=c++17 research/repeated-native-code-separation/native_replay.cpp -o /tmp/repeated-native-replay
/tmp/repeated-native-replay /tmp/repeated-native-source.txt 65521 65 > /tmp/repeated-native-moments.txt
python3.12 -B research/repeated-native-code-separation/verify.py --check-native /tmp/repeated-native-moments.txt
```

Both implementations reproduce every moment entry. Duplicate-word,
identical-stage, invalid-residue, degree-limit, inverse-cancellation and
nonzero-power controls are included. This is not independent human or
proof-kernel acceptance. No native supplier, full controller, compiler,
outer, selected cold, Lean or Docker replay is claimed.

## Exact scope and decision

The source is canonical main 1ec1119972c9aefe42525172d07b332fcff81cb4.
There is one shared binary axis and two private blocks of eight axes.
The normalizers are exactly those in the source. The polynomial
coefficients are scalar and do not depend on the tensor width. Adjacent
inverse powers can cancel before the reduced word is formed.

The proof allows arbitrary input owners, scalar mixing and owned scratch
in the decoder. It excludes only a fixed finite scalar/monomial decoder
for this terminal contract. It does not exclude paid Gaussian decoders,
new normalizers, three or more stages, longer reduced words, a different
shared space or a caller which uses retained correlated inputs.

The complete obligation ledger is unchanged: the producer and its coded
outputs are predecessor results; the proposed short-reuse decoder is
excluded in this class; a changed decoder and its complete paid bill,
restoration, compiler and outer closure remain unknown. Unknown costs
are not set to zero. This result ends this construction attempt. Merely
raising the degree limit is not a proposed follow-up campaign.

## Open next questions

- Can a changed normalizer assignment admit a short repeated code word
  whose terminal is monomial? First supply the literal signed maps and
  source endpoint. The present certificate is specific to the saved maps.
- Can an actual caller use its retained inputs to remove the code without
  a standalone terminal decoder? First give the independent-input
  endpoint and every paid operation. The arbitrary-terminal-input
  hypothesis would change, so this result does not settle that question.

The structured questions and overlap scope are in [TASK.json](TASK.json).

## Credit

Dillon's [PR #4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933)
supplies the physical common-query code, signed normalizers and caller.
Dugongue's [PR #4929](https://github.com/CrocSwap/integer-mult-bounds/pull/4929)
supplies the center-free code and its spectrum. Cinna Davis's
[PR #5065](https://github.com/CrocSwap/integer-mult-bounds/pull/5065)
supplies the two-stage terminal predecessor. Ali Romman's
[PR #5408](https://github.com/CrocSwap/integer-mult-bounds/pull/5408)
supplies the fresh-stage separation theorem and path-contraction method.
The present result replaces fresh-stage uniqueness by a finite exact
Gram witness for repeated native codes.

Retain Cinna Davis's cache, helper-basis and controller work; Cao Yifan's
native word; zxv's Clifford and compiler work; Jacob Alan Sussman's
mixed-target recursion; and the cumulative source lineage. The exact
[source notice](../coded-native-caller/NOTICE),
[origins](../coded-native-caller/ORIGINS.json) and
[license](../coded-native-caller/LICENSE) are declared package inputs.
