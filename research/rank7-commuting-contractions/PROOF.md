# Exact commuting contractions and their native bound

## Statement and source

For each of the two PR3042 words exported by PR3060 at
`df16ae619b858c5344a797c4424e0bafc2e69f62`, the 24 sequential witnesses in
`EDITS.json` preserve the complete forward operator on arbitrary dirty inputs.
They remove 27 A gates. Deriving the inverse with the unchanged private-buffer
renaming removes another 27 cleanup gates. They preserve every non-scalar native
event, all ordered helper widths and all 91 private buffers.

Applied after PR3060's disjoint restore substitution, the complete native
real-component primitive bound becomes 157,784 forward and 157,832 backward,
340 below PR3060. This is a theorem about the stated compiler's finite cost
contract. It is not a count of materialized physical instructions or a new
recursive exponent.

## One witness

Write a scalar ADD as `T(t,s,a) = I + a E(t,s)`, with `t != s`. The elementary
matrix satisfies `E(t,s)^2 = 0`, so

`T(t,s,b) T(t,s,a) = T(t,s,a+b)`.

For an intervening ADD `T(u,v,c)`, both products commute when `t != v` and
`s != u`. A SCALE or a native warp on a different register also commutes with
the moved ADD. The checker conservatively rejects every SCALE or warp on either
operand. When an intervening scalar event shares a register, its binary frame
must equal the moved gate's frame as a subspace. Thus the common invertible-frame
interpretation gives the same elementary-matrix calculation. Disjoint-register
events may have other frames. This argument uses the inherited native common-frame
contract; it does not replace that contract with an idempotent projection rule.

Each witness moves the first ADD right through only such commuting events,
then combines it with the second ADD. A zero sum deletes both gates. The checker
checks both literal preimages, every intervening event, the exact rational sum
and a strict native-tariff decrease. This proves equality of each changed
subprogram, including its intermediate dirty state at the subprogram boundary.
Induction through the 24 witnesses proves equality of the complete A operator.
The unchanged remaining forward sections therefore have the same inputs and
outputs. This proof is stronger than testing the whole word followed by its own
inverse, which could conceal an erroneous forward edit.

For example, two `target -= source` gates become `target -= 2*source`.
The source may feed other targets between them. An intervening read of the
changed target, or a write to the source, is a barrier. The negative controls
exhibit a wrong dirty-output row if that barrier is ignored.

## Cleanup, frames and complete cost

The first 84 A events are unchanged. The retained cleanup producer takes the
inverse reverse of the remaining A, B, native warps and restore, omits the same
correction-target operations, and renames the same 91 restored helpers into
private buffers. Its preimage and generated result are checked literally.
Its projection and renaming preserve the identities used here. No transformed
pair targets a correction register: every witness target is at least 224.
Thus none of its two constituent ADDs is lost through the correction-target
omission. The derived inverse retains the same arbitrary-dirty inverse action.

The finite-set frame tracker checks identical dimension itineraries and ordered
widths across all 704 original registers. The native comparison additionally
requires the complete non-scalar event sequences to be byte-equivalent as parsed
JSON, including climbs, centres, warps, wrappers, allocation and erasure events.
The native checker verifies all 632 live input columns in both orientations.
The unchanged paid profile is

`{1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}`.

For an ADD with reduced nonzero dyadic coefficient `p/q`, the inherited
one-real-component bound is

`3 + floor(log2(abs(p))) + popcount(abs(p)) + log2(q)`.

The 24 strict decreases sum to 85 in A, and the derived inverse saves 85 again.
Both real components are charged, giving `2 * (85 + 85) = 340`. All other events
remain in the complete invoice. The emitted scalar-macro count falls from 17,449
to 17,395; the total event count falls from 22,760 to 22,706. The 240 native warp
events and all private erasure predicates remain unchanged. Source-pin and
wrong-tariff/profile/erasure/non-scalar controls reject.

The producer commutes exactly with PR3060's restore substitution because the
two changes affect disjoint sections and cleanup is derived after both. Replaying
PR3042 separately measures the combined 364-unit decrease, with 24 units credited
to PR3060 and 340 to these contractions. Both provider words are replayed, even
though their local emitted programs coincide.

## Limits

The finite native checker is reused, not independently reconstructed. The
independently implemented edit certificate and its elementary-matrix argument
supply forward equality; native endpoint success alone is insufficient.
No optimality or complete rewrite-class exhaustion is claimed. The preliminary
shared-update probes did not find a verified recursive-profile gain and supply
no exclusion theorem.

The recursive bill and packing cap are unchanged. Ownership, physical movement,
materialized coefficient-stream prefix and precision costs, all-size/compiler
theorems and supplier/outer admission are not freshly established here.
