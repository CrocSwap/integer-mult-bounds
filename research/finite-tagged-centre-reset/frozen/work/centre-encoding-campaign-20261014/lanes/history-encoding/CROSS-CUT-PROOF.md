# Transfer through a common centre cut

This result applies to two separate local words in the same native chart.
The first word is forward. The second word is backward. It does not prove
that the selected global owner schedule can stop both words at this cut.

The base is `FULL-MODE-PROGRAMS.json.gz`, with decompressed SHA-256
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
The checker pins the canonical word as well. All values can be arbitrary.
In particular, neither of the two eight-mode inputs must be zero.

Write `K=R^T/4`. At the cut just before `retained_centre_scale`, the eight
centre registers contain

    W_F = R x_F + u_F,
    W_B = R y_B/4 + u_B.

The corresponding centre registers have the same native frame in the
two words. Each frame has rank eight. Remove the eight scales by -1
from each word and apply a two by two matrix C to the two values at
each centre. Then execute both retained suffixes. The result is

    u_F_new = C00 W_F + C01 W_B - R x_F,
    u_B_new = C10 W_F + C11 W_B,
    y_F_new = y_F + x_F - K W_F,
    x_B_new = x_B - y_B + R^T (u_B_new-u_B).

The other two data banks stay fixed. All 944 ordinary helpers are
restored. A dyadic invertible C gives a reversible local interface.

To prove these formulas, use the exact suffix responses. A change d
in the forward cut changes only its mode output, by d. A change d in
the backward cut changes its mode output by d and its X output by
`R^T d`. These responses include all 704 outputs of each word. Linearity
then gives the formulas, including the complete arbitrary helper claim.

The checker independently derives the two cut queries and the two
suffix responses from the pinned programs. It also emits three literal
instances and checks all 1,408 input columns, all scalar frame accesses,
and all ordinary helper outputs.

| C | Scalar gates at the cut | Complete real component bound |
| --- | ---: | ---: |
| `[[0,-1],[-1,0]]` | 32 | 409012 |
| `[[1,1],[0,1]]` | 8 | 408868 |
| `[[1,1],[0,-1]]` | 16 | 408884 |

These bounds include the two retained local scalar words. They exclude
native child cost, address cost, and any global owner repair. The native
mass is twice 5522. No new child or array is added by the cut coupling.

## Physical maps at the cut

The scalar theorem also gives the exact order for an operator transfer.
Let `B_k` be the physical native frame of centre k. For a physical
pointwise monomial M between the matching centre registers, the logical
coefficient is

    C_k = B_k^-1 M B_k.

For the Walsh retarget, replace `B_k` by its exact retargeted frame.
The common-frame relation remains true. A physical sign, translation,
unit phase, or address permutation can therefore be inserted without a
new recursive child. Its logical value must use the displayed ordered
conjugation. A logical monomial need not remain a physical monomial under
that conjugation. This result does not identify a port-dependent map on
112 data families with one of these eight centre maps.

The same suffix proof applies to operator entries of C. No entry is
commuted through R or K. A reversible block monomial can be lowered by
its explicit address and phase rules. Such rules, their cost, and their
native chart are required before an operator instance is admitted.

## Reproduction and scope

Run `check_cross_cut.py` with the pinned canonical word, the pinned full
mode program, and `verify_echo.py`. The output program is
`CROSS-CUT-PROGRAMS.json.gz`; the receipt is `CROSS-CUT.json`. The status is
`PASS_EXACT_COMMON_CUT_TRANSFER_AND_MIXING`.

The local role sets in this check are separate. A simultaneous cut in the
selected supplier needs a new owner audit. The sequential endpoint-pair
owner patch does not supply that audit. No complete supplier, final
decoder, or kappa improvement is claimed here.

Research and verification: OpenAI Codex under the user's direction, with
substantial AI assistance. No independent human review is claimed.
