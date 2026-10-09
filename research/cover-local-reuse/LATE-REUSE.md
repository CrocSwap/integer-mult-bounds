# Later compensation reads and physical scratch reuse

The restricted h22 scalar DAG, its operation frames and source gauges are retained.
The change schedules each deferred old-value correction later, then reuses scratch
whose final forward workspace use precedes that correction. The source compiler
chooses the schedule and pairs deterministically from the actual DAG; no serialized
search state is an input.

## Read deadlines

Every deferred role has one old-value correction `y -= C_b z_b`, where `C_b` is its
exact future response to the targets. The role is untouched before its first
workspace gate, and its old-value read may therefore move anywhere before that
gate. Source roles are read before their delayed source injection at the end of
phase one. Readouts from completed copied centers remain in their original place.

For each target, the source-gauge subspaces of its deferred corrections form an
increasing chain. Process gauge dimensions in decreasing order. A role's deadline
is the earlier of its first workspace use and the already computed deadlines of
strictly larger gauge levels on any target it reaches. Equal gauge levels do not
constrain one another. Execute reads at their deadlines, ordered by gauge dimension
and role within a deadline. This keeps every target-frame transition nested and
retains its exact original histogram. The independent verifier reconstructs those
target chains from the actual schedule and checks every read occurs before its
first use.

## Compensated handoff

Choose an existing nonroot role `a` with zero source gauge and a previously unaliased
deferred copy-born role `b`. Require:

- The donor's last actual forward workspace use is before `b`'s old-value read.
- The donor's final operation frame is contained in `b`'s source gauge, which in
  turn is contained in `b`'s first operation frame.
- Neither endpoint belongs to another pair, and `b` is untouched before its
  copy birth. The donor is not a final readout root. The recipient may be a root; its final
  readout is retained on the shared physical bank.

The physical bank now contains some arbitrary value `z` when the recipient is born.
Its correction subtracts `C_b z`; subsequent computation contributes `C_b z` back,
so that value cancels exactly from every target. This argument holds for arbitrary
current `z`, including mixtures of initial scratch and source values. Every actual
physical source/workspace shear is then inverted in true reverse chronological
order. No zero initialization or independently preserved donor value is assumed.
The inverse restores the original physical bank, not two discarded virtual banks.

The donor begins at zero gauge and remains the physical source role. The recipient's
separate source slot and exterior disappear. Replace the donor's former final
transition from dimension `e` to `h` by its handoff transition from dimension `e` to
recipient-gauge dimension `d`. All operation frames, source gauges, scalar
coefficients and scalar-operation counts remain unchanged. The compiler retains
all source/target transitions and copied-center children.

## Verified finite instance

The canonical selector adds 780 disjoint handoffs to the existing 1,703, reducing
physical roles from 21,274 to 20,494. It schedules 2,865 deferred reads later than
the initial cut. The complete forward and reflected literal word still expands to
7,075,117 scalar operations per stage. Both directions retain exact same-frame
scalar incidences and the complete paid child inventory.

Controls reject an omitted correction and a correction moved prematurely before a
donor's final value-producing gate. The full dirty-scratch replay restores every
physical auxiliary and obtains exactly `y + x`; the exact coefficient/dependency
checks and literal frame audit are retained. The new role count flows into the
physical exterior inventory, padded triple sharing and complete finite assembly;
its conservative local scalar reserve still uses virtual roles.

The earlier compensated-reuse construction follows jamesyc's PR124. This extension
uses the retained local DAG and frame/gauge improvements, with OpenAI Codex
assistance. Existing contributor notices and inherited proof boundaries remain.
