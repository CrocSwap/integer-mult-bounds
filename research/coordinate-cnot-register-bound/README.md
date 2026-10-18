# Two coordinate swaps need six paid coordinate-CNOT calls

**Scoped theorem; no new kappa.** Two coordinate-SWAP targets require exactly
six paid coordinate-CNOT address calls, even with arbitrarily many restored
dirty registers and free scalar register mixing, in the explicit formal model
below. [PROOF.md](PROOF.md) gives the written all-register proof. Two independent
finite implementations corroborate its smallest cases.

This answers the smallest two-dimensional gap instance of Gareth Davidson's
[PR1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333) first open
question. His broader affine rank-priced alphabet admits the swap as a single
unit and therefore prices these two targets at two. Restricting the alphabet
to the two coordinate CNOTs gives a direct bill of six; the result here proves
that mixing registers cannot lower it. The higher-dimensional question remains
open.

## Exact alphabet and endpoint

Let `R=F2[GL_2(F2)]` be the formal group algebra, with

```text
a = [[1,1],[0,1]],  b = [[1,0],[1,1]],  s = aba = bab = [[0,1],[1,0]].
```

For every finite `r>=2`, allow free scalar `GL_r(F2)` basis changes and paid
unit calls `I+([g]+1)N`, where `g` is **only a or b**, and `N=uv^T` is a binary
rank-one idempotent (`v^T u=1`). Require the complete formal boundary
`diag([s],[s],1,...,1)` on arbitrary register inputs. Every extra register is
dirty and restored. There are no free address maps, translations, copies,
erasures or clean allocations. Undo calls are charged.

Free scalar normalization follows the augmentation argument credited to
PR1333. The new lower bound uses the sign quotient of `GL_2(F2)` to force an
even call count. Every four-call label pattern then fails a coefficient-rank
test: in the alternating case, the sum of the swap and reverse-pair
coefficients is a product of two rank-one projectors, whereas the target
requires rank two. Six direct calls attain the full formal endpoint with no
additional roles or scalar operations.

This is an optimistic paid-call relaxation, not a physically admitted supplier.
The formal nonabelian address algebra differs from the retained rational
abelian three-register model; no rational entries are reduced modulo two.

## Exact checks

| Registers | Dirty extras | Paid generators | Exact distance layers 0,1,2,3 | Ball through 3 | Meets a two-call inverse ball at the target |
| --- | --- | --- | --- | --- | --- |
| 2 | 0 | 12 | 1, 12, 80, 466 | 559 | 0 |
| 3 | 1 | 56 | 1, 56, 1750, 45396 | 47203 | 0 |

Every word of length at most five splits into a prefix of length at most two
and a suffix of length at most three. These empty intersections therefore
certify the finite lower bounds without enumerating all literal five-call
words. The six-call witnesses are checked in the full formal algebra.

`verify.py` encodes all six formal coefficients per entry. `independent.py`
instead constructs binary address matrices, enumerates all scalar matrices
to find idempotents, and multiplies complete 12- or 18-dimensional matrices
in the faithful left regular representation. Their **entire state sets and
distance layers agree**. The second implementation performs 1,116 and 101,192
directed transition attempts. No natural two-dimensional representation is
used to accept formal equality.

The replay also checks all 31 label patterns through length four with
noncommuting scalar indeterminates, all 36 sign-homomorphism products, and
all 4,704 conjugations of the 28 projectors by `GL_3(F2)`. Identity and one-swap
meet-in-the-middle controls recover minima zero and three. Fourteen controls
cover each of six omitted calls, a wrong label, dirty-register restoration,
clean-only leakage, a nonidentity scalar residue, rank-two underpricing,
address-alphabet expansion, a nonfaithful representation, and multiplication
order. [EXPECTED.json](EXPECTED.json) records deterministic counts and state-set
hashes. These checks support, but do not replace, the written universal proof.

## Reproduce

Python 3.12 and the standard library suffice; no compiler or external package
is needed. From the repository root:

```sh
python3 -I -B research/coordinate-cnot-register-bound/verify.py
python3 scripts/research_package.py --package research/coordinate-cnot-register-bound --check-only
python3 scripts/research_package.py --package research/coordinate-cnot-register-bound
```

Expected direct-replay line:

```text
PASS_COORDINATE_CNOT_REGISTER_BOUND minimum=6 dirty_registers=arbitrary census_r=2,3 symbolic_patterns=31 controls=14 no_new_kappa
```

The registered replay also runs the six focused tests in `test_verify.py`,
including receipt/source corruption rejection and an unchanged read-only
relocated replay under isolated optimized Python. To inspect a newly computed
receipt without writing files, pass `--emit`. State hashes concatenate sorted
formal-state integers encoded in fixed-width little-endian bytes (3 bytes for
two registers, 7 for three). `SOURCES.json` pins the unchanged context input
and task/base provenance; PR1333 text has separate exact contextual pins and
is not a runtime dependency. No predecessor implementation is imported.

[VALIDATION.md](VALIDATION.md) records the observed local checks and their scope.

The all-register proof has not been checked in Lean or independently reviewed
by a human. There is no selected-supplier cold replay: physical compilation,
common-label realization, hosting, precision/tape and analytic transfer are
outside this result. The selected record and inherited assumptions are
unchanged. No multiplication-runtime claim follows.

## Task and overlap

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Card:
`bit-new-register-model`, scope key `7084092dd726e7ba1f2f`, priority revision 2;
chooser nonce `30b6519a75b5dea27cbfaca91b7e00af`. The claim is in
[discussion #1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317).
The initial fixed `r=2,3` question was strengthened to all finite register
counts using the same target and alphabet. [TASK.json](TASK.json) records the
refinement and structured next questions; [OVERLAP.json](OVERLAP.json) records
the searched snapshot coverage and exact neighboring heads.

PR1333 at `7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2` is the immediate
predecessor. PR468 and David Govea's PR720 at
`a942c0ae1b463710ca535c1fba1b07b6431b5a86` concern rational abelian targets;
they do not cover this alphabet. PR680/705/800/836 concern other formal
Clifford or complex register models. This account's PR1306 addresses XOR
compensation on a fixed dirty shear boundary, a different problem. Neither it
nor the existing helper-interface work is repeated here.

## Open next questions

1. **Three or more swaps in the same alphabet.** A general direct-sum bound
   would say how far this obstruction scales. Start with three swaps: the
   sign trace permits only odd lengths, so seek a seven-call identity or a
   coefficient obstruction against the direct nine. Longer alternating words
   and arbitrary dirty-register counts require a new argument; the present
   four-call proof does not cover them.
2. **A three-dimensional coordinate-CNOT target with a rank/length gap.**
   This tests the higher-dimensional branch of PR1333's question. First pin a
   target in `GL_3(F2)` and certify its direct coordinate-CNOT length; then
   test a two-role formal word below twice that length. Full formal equality
   and the complete paid/restoration bill are required. The six-element
   group argument here does not apply to that larger address group.

## Credit and license

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Credit Gareth Davidson (@bitplane) for PR1333's question and augmentation
normalization; eumemic (PR288), Ali Romman (PR468) and David Govea (PR720)
for the surrounding register-model and rational-address work. No new general
rank principle or literature-priority claim is made. New work is Apache-2.0;
predecessor sources and notices remain unchanged.
