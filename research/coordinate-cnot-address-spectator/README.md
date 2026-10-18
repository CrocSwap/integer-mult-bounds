# A third address coordinate does not cheapen two swaps at two or three registers

**Finite certificate: the minimum is six paid calls; no new kappa.** Two
coordinate-SWAP targets still cost six when all six coordinate CNOTs on
**three address coordinates** are allowed, for exactly two or three scalar
registers. Free scalar mixing is allowed. At three registers, the extra
register is arbitrary dirty input and is restored.

This answers a bounded part of the higher-dimensional alphabet question in
this account's [PR1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414).
That predecessor permits only the two CNOTs on two address coordinates and
proves an all-register result. The present certificate adds the four gates
touching a third address coordinate, but its lower bound covers only `r=2,3`.
It is separate from the concurrent three-SWAP investigation in the original
two-dimensional alphabet.

## Exact model and result

Work in `M_r(F2[GL_3(F2)])`. A paid call is
`I+([I+E_ij]+1)N`, for all six `i!=j` and all binary rank-one idempotents
`N=uv^T`, `v^T u=1`. The target is `diag([s12],[s12],1,...,1)`, where `s12`
swaps address coordinates 1 and 2 and fixes coordinate 3. Equality is formal
group-algebra equality on arbitrary inputs. There are no free address maps,
translations, copies, erasures or clean allocations; undo calls are paid.

[PROOF.md](PROOF.md) states the full contract and finite-coverage argument.
Free scalar `GL_r(F2)` mixing normalizes away by augmentation. A formal word
maps to binary matrices of size `3r` through the natural representation.
An exhaustive rejection in that representation proves rejection of formal
words. Natural matrix equality is **not** used to accept a formal identity.
The direct six-call upper bound is checked in the full group algebra.

| Registers | Paid generators | Exact distance layers 0,1,2 | States within two calls | Edges scanned by each checker | Short target matches |
|---|---:|---|---:|---:|---:|
| 2 | 36 | 1, 36, 816 | 853 | 30,708 | 0 |
| 3 | 168 | 1, 168, 17,346 | 17,515 | 2,942,520 | 0 |

Every word of length at most five splits into a prefix of at most three
calls and a suffix of at most two. Streaming every edge from the radius-two
ball therefore gives complete coverage without storing the third layer.
There is no symmetry reduction or sampling. Two code-disjoint implementations
agree on their entire generator sets and radius-two balls; both independently
reject every target intersection. The second enumerates all scalar matrices
and uses column operations and right multiplication, rather than the first
implementation's rank-one parametrization and left row updates.

[EXPECTED.json](EXPECTED.json) records exact counts and deterministic state
hashes. The direct replay includes 25 positive, boundary and model controls
across the two register counts. These include all six omitted calls, a wrong
spectator label, unreturned address state, a dirty-only fault, a nonzero
formal element with zero natural image, and a forbidden rank-two unit-price
alphabet. The focused tests check algebra compatibility and free-scalar
conjugation, and reject real source and receipt corruptions.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -I -B research/coordinate-cnot-address-spectator/verify.py
python3 -B scripts/research_package.py --package research/coordinate-cnot-address-spectator --check-only
python3 -B scripts/research_package.py --package research/coordinate-cnot-address-spectator
```

The direct replay prints:

```text
PASS_COORDINATE_CNOT_ADDRESS_SPECTATOR minimum=6 registers=2,3 address_dimension=3 controls=25 no_new_kappa
```

The registered replay additionally runs the seven focused test groups,
including an isolated optimized replay from a read-only source export.
`verify.py --emit` recomputes and prints the deterministic receipt without
writing files. There are no solver, compiler, network or third-party package
dependencies. [VERIFY.json](VERIFY.json) declares the bounded replay.

## Scope, provenance and overlap

Base: `4040a0f46d67b41c36a472a7cd4af791fd4c36cc`. Task:
`bit-new-register-model`, priority revision 2, scope key
`7f5f4426ef796683c485`, chooser nonce `70587133f1c80395ae4658456ec59584`.
The claim is in [discussion #1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317).
[TASK.json](TASK.json) contains the refined task card and next questions.
[SOURCES.json](SOURCES.json) records exact provenance and contextual predecessor
heads; [OVERLAP.json](OVERLAP.json) records snapshot coverage and distinctions.
No pending implementation is imported.

Gareth Davidson's [PR1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333)
allows all affine rank-one labels at unit price, including the swap itself;
its rank-floor theorem therefore uses a different paid alphabet. PR1414
restricts to two-dimensional coordinate CNOTs. The concurrent `UT_3(F2)`
central-commutator investigation uses another group and target. The
[concurrent order-four GL3 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18912727)
uses two copies of a different target, with all three coordinates essential
and direct bill eight, instead of two order-two swaps with direct bill six.
None of those results is silently generalized here.

The source-bound baseline confirms that the selected complex supplier remains
the binding side. This is a bit-mechanism cost screen, with no change to the
selected record, paid recursive histogram or exponent. It does not cover
arbitrary extra registers, more address coordinates, general nonabelian
targets or another scalar field. The proof is not Lean-checked or independently
human-reviewed. Physical realization, compiler, hosting, precision/tape and
outer analytic transfer are unrun; no selected-supplier cold replay is claimed.

## Open next questions

1. **Does six remain the minimum with arbitrary restored dirty registers?**
   This would turn the finite screen into an all-register obstruction for the
   enlarged alphabet. A feasible first step is a separately bounded `r=4`
   natural-image census, or a rank argument for all five-call label patterns.
   The blocker is the absence of a dimension-independent compression or
   coefficient argument; these two finite cases do not supply one.
2. **Can a second address spectator change the cost?** Enlarge to all twelve
   coordinate CNOTs in `GL_4(F2)` at `r=2`, keeping the same two-swap endpoint.
   This tests whether the present obstruction survives another operation
   alphabet. Recompute the full natural-image census, checking any surviving
   candidates formally; a faithful group action alone cannot accept a group-
   algebra identity. No higher-dimensional exclusion is inherited here.

## Credit and license

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Credit Gareth Davidson (@bitplane), PR1333, for the restricted-alphabet
question and augmentation normalization, and this account's PR1414 for the
two-swap predecessor and explicit higher-dimensional question. Credit eumemic
(PR288), Ali Romman (PR468), and David Govea (PR720) for the rational abelian
register-model lineage. The two checkers were written separately within this
AI-assisted contribution; this is not independent human review. New work is
Apache-2.0; predecessor source files and licenses are unchanged. No literature-
priority or general rank-principle claim is made.
