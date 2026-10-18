# Four fully occupied coordinate-SWAP roles require twelve calls

**Scoped written theorem; no new kappa.** In the formal
`F2[GL_2(F2)]` register model, four SWAP targets on exactly four roles
require **twelve** paid coordinate-CNOT calls. All four inputs are arbitrary;
there is no extra workspace role. Free scalar `GL_4(F2)` mixing is allowed.

This closes the balanced ten-call case **at four roles** left by Ross
Richardson's [PR1722](https://github.com/CrocSwap/integer-mult-bounds/pull/1722)
and investigated by Aaron Wang's
[PR1755](https://github.com/CrocSwap/integer-mult-bounds/pull/1755).
It does **not** exclude ten calls with active/dirty coupling on five or six
roles. The arbitrary-workspace question remains open.

The new step is an elementary twisted cyclic rotation, combined with the
credited label-saturation theorem. The proof is below and is self-contained;
finite checks corroborate its algebra and boundaries. No SAT solver, long
search trace or proof-assistant kernel is needed for the submitted result.

## Exact model and bill

Let `a=[[1,1],[0,1]]`, `b=[[1,0],[1,1]]`, and
`s=aba=bab=[[0,1],[1,0]]` in `G=GL_2(F2)`. A paid call is

`D_N(g)=I+([g]+1)N`, with `g in {a,b}`, `N=uv^T` binary, `v^T u=1`.

Every call, including an undo, costs one. Free scalar basis changes can be
moved to the right by conjugating the projectors; augmentation `[g] -> 1`
forces the remaining scalar factor to be identity. This normalization is
credited to Gareth Davidson/PR1333 and the coordinate-CNOT predecessors.
There are no free address maps, erasures, clean allocations or overwrites.
Equality is in the **full formal group algebra**, not just a small address
representation.

For `t` fully occupied roles, the target is `T=[s] I_t`. The direct word
uses `aba` on each coordinate projector and costs `3t`, including every paid
operation. This is an optimistic abstract tariff: scalar work and workspace
costs are free in this model. It supplies no physical compiler, hosting,
precision/tape or analytic bound and no new recursive profile or exponent.

## Proof

**Credited saturation lemma (PR1722).** For `t` SWAP targets and any number
of restored dirty extras, both label counts are at least `t`. If one count
is exactly `t`, the other is at least `2t`.

Here is the argument, restated with credit so this note has no unchecked
numerical dependency. Normalize the free scalar maps. The sign quotient
`G -> C2`, over `F2[epsilon]/(epsilon^2)`, gives `sum N_i=P`, where
`P=diag(I_t,0)`, and taking trace gives `q=t mod 2`. In the natural address
representation, the two paid maps are

`a: [[I,N],[0,I]]`, `b: [[I,0],[N,I]]`,

and the target is `[[I+P,P],[P,I+P]]`. Hence each label's image vectors span
`im P`, proving the count floor `t`.

If exactly `t` a-calls occur, their image vectors form a basis of `im P`.
Conjugate that basis to the active coordinate basis, keeping the dirty
complement fixed. Each active top row changes exactly once from `[e_i,0]`
to `[0,e_i]`, so the sum of the two top blocks is always `I`. The two bottom
blocks therefore have sum `I + sum_(preceding b) N_j`; their final sum is
`I`, so `sum_b N_j=0`. The full sign equation then gives `sum_a N_i=P`.
Since the a images are distinct coordinate vectors, their covectors are
also the corresponding coordinate covectors. At a's unique update of row
`i`, bottom row `i` must be `[e_i,e_i]`; its block sum is zero. Thus
`e_i^T=sum_(b before a_i) e_i^T N_j`, so all active covectors lie in the
span of the b covectors. If `U` contains the b images and `V` the b
covectors, `UV=0`, `rank U>=t`, `rank V>=t`. Rank-nullity gives
`n_b>=rank U+rank V>=2t`. Interchanging address coordinates proves the
symmetric case. The original frozen proof is retained unchanged in
[inputs/PR1722-PROOF.md](inputs/PR1722-PROOF.md).

**New rotation step.** Write a word in chronological order
`D_1,...,D_q`, so `D_q ... D_1=T`. At full occupancy, conjugation by
`T=[s]I_t` exchanges a and b and keeps every scalar projector `N` fixed:

`T D_N(a) T^-1=D_N(b)`, and conversely.

Consequently the chronological word

`D_2,...,D_q, T D_1 T^-1`

has the same target: its product is
`(T D_1 T^-1)(T D_1^-1)=T`. It has exactly the same number of legal paid
calls and flips just the moved call's label.

For four roles, a sub-twelve word has even length by the sign trace and at
least four calls of each label. Saturation excludes length eight and the
`(4,6)`/`(6,4)` length-ten counts. Only `(5,5)` remains. Rotate its first
call: the result has counts `(4,6)` or `(6,4)`, which saturation excludes.
Four direct `aba` words attain twelve. This proves the stated minimum.

**Uniform cut consequence.** The same observation is useful beyond four
roles. If a fully occupied `t`-target word saves over `3t`, then every
rotated cut must have both counts at least `t+1`, by saturation. Let the
original counts be `A,B`, and let `s_k` be a-prefix-count minus
b-prefix-count among the first `k` calls. Rotating that prefix flips all
its labels, so its new counts are `A-s_k, B+s_k`. Thus every cut obeys

`t+1-B <= s_k <= A-t-1`.

This integer interval has width `q-2t-2`. Since consecutive `s_k` differ
by one, `q>=2t+3`. If equality holds, the walk is confined to two adjacent
integers, so the labels strictly alternate. The retained trace parity
`q=t mod 2` still applies. For example, a possible thirteen-call saving
for five fully occupied targets must be strictly alternating. This note
neither constructs nor excludes that case.

**Workspace boundary.** For a partial target `I+([s]+1)P`, conjugation can
mix group coefficients with active/dirty blocks, and need not preserve the
paid alphabet. The verifier gives an explicit legal coupled projector
whose conjugate is not *any* allowed paid factor. Thus the rotation proof
must not be extended to arbitrary restored dirty workspace. If every
normalized projector commutes with `P`, each rank-one projector acts wholly
inside either the active or dirty subspace; restricting to the active
subspace gives the four-role word. Therefore any ten-call escape with
extras must use active/dirty coupling.

## Reproduce and checked scope

From the repository root, Python 3.12 and the standard library only:

```sh
python3.12 -I -B scripts/research_package.py --package research/four-swap-full-occupancy
```

The registered replay runs the primary exact checker, a separately written
faithful-operator checker, and the package failure controls. Expected markers
are `PASS_FOUR_SWAP_FULL_OCCUPANCY` and
`PASS_INDEPENDENT_FULL_OCCUPANCY`, with `minimum=12 no_new_kappa`.
Normal verification is read-only; `verify.py --write` explicitly regenerates
the deterministic receipt. Exact counts and source hashes are in RESULT.json.

The primary engine multiplies formal six-coefficient algebra entries. The
second constructs the regular action on the six binary address matrices and
compares complete binary operators. They share the declared model and receipt,
not executable mathematics. Both were written by one assisted author; this is
not independent human review or a Lean formalization.

The finite checks cover full-occupancy conjugation for every binary rank-one
idempotent through six roles, all cuts of diverse attaining words, the complete
binary-label cut screen through length sixteen, and a concrete partial-target
failure. They corroborate the written all-`t` argument; no finite search is
used to justify its universal quantifier. The selected-record check is separate
from a full selected cold replay, which was not needed or run.

## Provenance, overlap and credit

Base main: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Selected-record
SHA256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Chooser nonce: `31f0c7f2788860364077aac4b428311c`, priority revision 3,
card `bit-new-register-model`. TASK.json records the exact scope, initial
encoding experiment, final proof refinement, overlap coverage and pins.
The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18919990)
coordinates this contribution with the existing register-model thread.

Credit commdata2338/PR1414 and PR1491 for the formal model, sign invariant
and earlier swap results; Gareth Davidson/PR1333 for normalization; Cinna
Davis/PR1541 for arbitrary-workspace reasoning and role compression;
Ross Richardson/PR1722 for saturation; and Aaron Wang/PR1705 and PR1755 for
the four-target boundary, residual search and collapsed augmentation-layer
finding. The generic conjugation/cyclic-product identity is elementary;
no literature-priority claim for that identity is intended. The new
application excludes this exact residual and gives the cut constraint.

Prepared for **Ross Richardson** with substantial **OpenAI Codex assistance**
in reasoning, implementation, checks and writing. New work is Apache-2.0;
predecessor attribution and the selected frontier are unchanged.

## Open next questions

1. **Can active/dirty coupling realize four swaps in ten calls?** This is
   the remaining potential saving in the same alphabet. PR1722/PR1541 reduce
   arbitrary finite workspace to at most six roles. First test the balanced
   five-plus-five formal endpoint at five or six roles with a proof-producing
   solver; full target conjugation cannot be used as a symmetry there. A
   preliminary six-role conflict-budget run was inconclusive.
2. **Can five fully occupied targets use thirteen alternating calls?** The
   new cut constraint isolates this next candidate below fifteen. Start with
   either alternating label word and rank-one idempotent unknowns, retaining
   the full formal endpoint and sign equation. Noncommuting scalar-projector
   interactions remain the blocker. No success is predicted.
