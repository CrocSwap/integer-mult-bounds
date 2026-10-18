# Three coordinate swaps need nine paid calls on three registers

**Finite certificate; no new kappa.** In the formal `F2[GL_2(F2)]` model,
three coordinate-SWAP targets on **exactly three registers** require exactly
nine paid coordinate-CNOT calls, even with arbitrary free scalar `GL_3(F2)`
mixing. The complete boundary is checked for arbitrary inputs. Additional
dirty registers are outside this result.

This resolves the first open question of this account's
[PR #1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414) for the
smallest register count. That predecessor proves **two** swaps need six calls
for any number of restored dirty registers. Its four-call coefficient proof
does not exclude seven-call words for three swaps. Here a complete new
radius-four census supplies that exclusion; no predecessor implementation is
imported. [PROOF.md](PROOF.md) gives the model, parity argument and coverage
proof.

## Alphabet, complete bill and result

Let `a=[[1,1],[0,1]]`, `b=[[1,0],[1,1]]`, and
`s=aba=bab=[[0,1],[1,0]]`. A paid unit is

`D_N(g) = I + ([g]+1)N`, with `g in {a,b}` and `N=uv^T`, `v^T u=1` over F2.

There are 28 scalar projectors and 56 paid generators. Free scalar invertible
basis changes are normalized by augmentation, leaving no final scalar residue.
There are no free address maps, copies, erasures, clean allocations or extra
registers. Every undo call costs one. Equality means equality of **all formal
group-algebra coefficients**, not equality in the natural address representation.

The direct word `aba` on each of the three coordinate projectors has exactly
nine calls and endpoint `diag([s],[s],[s])`. It needs no scalar changes or
additional roles. A shorter word must have odd length: the sign quotient to
`F2[epsilon]/(epsilon^2)` gives `sum N_j=I_3`, whose trace is one. Therefore
excluding all words through seven excludes every possible saving.

| Exact distance | Distinct formal states | Outgoing attempts used to reach this distance |
| ---: | ---: | ---: |
| 0 | 1 | 0 |
| 1 | 56 | 56 |
| 2 | 1,750 | 3,136 |
| 3 | 45,396 | 98,000 |
| 4 | 1,047,437 | 2,542,176 |

The radius-three and radius-four balls contain **47,203** and **1,094,640**
states. The intersection `{x T : x in B_3} intersect B_4` is empty, with
`T=diag([s],[s],[s])`. The involutive alphabet makes each ball closed under
inversion, so this excludes every word of length at most seven. This is a
complete finite exclusion, not an unsuccessful heuristic search.

Free scalar work is an optimistic relaxation of a physical implementation.
The certificate prevents a saving in this exact alphabet and register count;
it does not price or admit a replacement for the selected bit supplier.

## Independent checks and controls

`verify.py` packs the 54 formal binary coefficients and multiplies on the right.
`independent.py` independently constructs the group from binary 2x2 matrices,
enumerates all 512 binary 3x3 matrices to select projectors, and multiplies on
the left in the **faithful regular representation** (complete 18x18 matrices).
Every exact-distance state set agrees after conversion, not just the counts
or hashes. Both target intersections are computed separately. The second
implementation additionally checks all **101,192** transitions through radius
three using generic dense matrix multiplication.

[EXPECTED.json](EXPECTED.json) records the exact layers, transition counts,
both sets of deterministic hashes and 25 semantic controls. The controls
reject nine omitted calls, nine wrong labels, a missing third target,
nonidentity scalar residue, an expanded address alphabet, a nonidempotent
scalar factor, rank-three underpricing, a natural-representation kernel and
commuted address labels. Positive minimum controls recover 0, 3 and 6 for
zero, one and two swaps in the same three-register domain.

The seven tests also check 4,704 scalar conjugations, all 3,024 optimized
generator actions on a complete 54-vector formal basis, all four target maps
on that basis, same-cardinality wrong state sets, altered receipts and source
bytes, and an isolated optimized replay of a read-only relocated package.
The linear-basis test is exhaustive for each optimized transition map. The
read-only test also rejects a falsified minimum in the receipt under `-O`.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -I -B research/three-swap-cnot-census/verify.py
python3 scripts/research_package.py --package research/three-swap-cnot-census --check-only
python3 scripts/research_package.py --package research/three-swap-cnot-census
```

Expected direct line:

```text
PASS_THREE_SWAP_CNOT_CENSUS minimum=9 registers=3 ball3=47203 ball4=1094640 meet=0 controls=25 no_new_kappa
```

The registered hook runs the complete census and all seven focused tests.
Direct replay takes approximately eight seconds and 356 MiB in the measured
CPython 3.12.3 environment; these are verifier observations, not multiplication
performance claims. `--emit` prints a newly computed receipt after comparison
with the committed receipt and does not write files. Hashes concatenate each
sorted exact-distance layer as seven-byte formal or 41-byte regular integers,
little endian. Equality checks compare the actual sets before hashing.

[SOURCES.json](SOURCES.json) pins the unchanged rational-model context README
as a live input, historical catalogue/selected-record provenance at the base,
and the inspected predecessor texts separately. No pending PR is a runtime
dependency. The direct verifier works from a source export; the package
metadata check uses Git history for historical provenance.

## Scope, assignment and overlap

Base: `4040a0f46d67b41c36a472a7cd4af791fd4c36cc`. Chooser nonce:
`f327083ac49b0ead4b280ae0236eac2d`, bit-mechanisms, priority revision 2,
task `bit-new-register-model`, scope key `7084092dd726e7ba1f2f`.
[TASK.json](TASK.json) records the refinement. The claim is in
[discussion #1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18912673).

Immediate predecessors are PR #1414 at
`9e1640094f649ba6db9742796825a8d6c238989b` and Gareth Davidson's
[PR #1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333) at
`7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2`. PR #1333 permits all affine
rank-one address maps as units, including the swap itself; its different
alphabet would price the three targets at three. PR #468/#720 concern
rational abelian addresses. No rational frame data are reduced modulo two.

[OVERLAP.json](OVERLAP.json) records snapshot coverage and the neighboring
claims. The concurrent `UT_3(F2)` two-commutator question has a different group
and endpoint. The `GL_3(F2)` spectator-swap and order-four-target claims expand
the address group and generator alphabet; neither is this three-swap problem.

The proof is written and computer-assisted, not Lean-checked or independently
human-reviewed. No fourth-register census, arbitrary-register theorem,
physical compilation, common-label realization, whole-call hosting,
precision/tape, analytic transfer or selected-supplier cold replay is claimed.
The selected result is unchanged.

## Open next questions

1. **Can a fourth, restored dirty register help these three swaps?** This
   tests whether the finite obstruction persists under borrowed workspace.
   Start with the same formal target `diag([s],[s],[s],1)` and alphabet;
   prove a reduced-state coverage rule before extending the radius-three/four
   search. The larger projector/state inventory blocks simply extrapolating
   this three-register receipt. Existing parity still excludes even lengths.
2. **Can a coefficient argument exclude seven calls with arbitrary extra
   registers?** Such a proof would extend this finite finding to a general
   three-swap theorem. First expand the 128 seven-label patterns, combine
   equal-label runs, and seek a coefficient functional whose target has rank
   three but whose product expansion has rank at most two. Longer alternating
   runs are not covered by PR #1414's four-call argument; this package does
   not assert the required functional exists.

## Credit and license

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Credit this account's PR #1414 for the restricted model, sign-trace method,
two-swap result and explicit three-swap question; Gareth Davidson (@bitplane),
PR #1333, for the restricted-alphabet research direction and augmentation
normalization; eumemic (PR #288), Ali Romman (PR #468) and David Govea (PR #720)
for the surrounding register-model work. The new contribution is the complete
three-register, three-swap exclusion and its independent exact census.
No claim of priority for general rank or group-algebra methods is made.
New work is Apache-2.0; predecessor sources and notices remain unchanged.
