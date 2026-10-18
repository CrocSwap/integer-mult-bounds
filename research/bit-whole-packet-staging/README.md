# Stage a complete BIT invocation before touching its local word

**Conditional compiler construction and exact finite replay; no new kappa.**
For one low cover class, gather every owned packet into private work, align
each packet once, execute the entire local word there, then inverse-align and
scatter once. This replaces repeated extraction from the original families
inside that word with **two full scans per touched family and two owner-route
actions per role**. The original families remain parked while the word runs.

This supplies a concrete node-level staging option for Jose Manuel's
[PR2195 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2179).
Its section 4 supplies a restricted-fibre implementation of one ADD; its
section 5 leaves recursive work allocation and the numerical routing bill
open. We change the storage/selection schedule for a whole invocation and
give its boundary contract and parametric bill. The generic fact that a
disjoint gather can be inverted is not claimed as new mathematics.

The selected PR589 word and all 288 owner descriptors remain unchanged.
The result is **not** a new helper-star word, a new H2/K admission lemma, or a
full GL64 compiler. The card scope is changed because the basic H2/K question
is already covered by PR1194/1311/1806 and later semantic-D work.

## Contract and construction

Fix `R=Z/q^w` with odd prime `q`, a low invocation `d0`, and one node.
For role `i`, let `f_i` be its physical family and `sigma_i` its fixed owner
chart. Its owned packet is all matrices

`g in GL64(R)` with `g mod q = d0 (sigma_i mod q)^-1`,

together with **every** value of all unused row fields and payload addresses.
Let its volume be `L`; one physical family has volume `N L`, where
`N=|GL64(F_q)|`. Payloads are arbitrary and may be correlated and dirty.

Assume the following exact interfaces:

The physical families are already separately accessible streams with heads
at their origins. This is an explicit entry layout. If a caller instead
supplies one concatenated live array, first split it into the fixed number
of family streams and merge it after the invocations. The elementary stream
lemma gives an additional `C_layout*V` time charge and up to `V` extra copied
storage; neither is included in the per-call counts below. A packed-tape
implementation cannot substitute cost-free seeks between family blocks.

1. Roles in a shared physical family own distinct low packets. Pointwise
   inequality at each high matrix is insufficient. PR2195's support
   completions prove this stronger condition for the selected descriptors.
2. A completed route maps the entire packet from `g` to `d=g sigma_i`,
   including high-coordinate carries. Its inverse returns it to `g`.
   Routes preserve complete unused spectators, restore descriptors/heads,
   and close their private work. Their time and additional space are charged.
3. The local word has its complete packet address-callee contracts, literal
   COPY/ERASE guards and endpoint theorem in this aligned representation.
   In particular its callees preserve the cover/unused spectators. They do
   not access parked physical families. We inherit these hypotheses and
   PR1627/2195's frame argument; the new verifier does not prove their
   recursive physical implementations.

Perform these operations in order:

1. Scan each touched family once in its low/high/unused/payload order. Copy
   each selected low packet to its own blank role tape. Leave original
   family cells untouched and return the family head to its origin.
2. Route each complete role tape to the common invocation chart. The
   payload-address data charts and frame labels remain the inherited ones;
   this step aligns owner rows, not those payload addresses.
3. Execute the literal word on the role tapes, with one blank private COPY
   tape. All its ADDs and child actions use these staged tapes. Close COPY
   work and every child work region before returning from the word.
4. Inverse-route every role tape. Scan each original family once more;
   overwrite its selected packets from the corresponding outputs in order.
   Leave every unselected cell unchanged. This is an in-place sequential
   replacement, so no full-family output buffer is needed.
5. Clear role work, restore all heads, and only then start another low-class
   invocation. The next gather reads the current physical state.

There are finitely many role tapes (661 in the selected instance), independent
of `w`, row count and payload length. This is a fixed finite number **at one
node**. It does not allocate that many new tapes at every recursion depth or
claim to solve the depth-first parking obligation for recursive callees.

## Proof of the boundary implication

Within each family the selected packets are disjoint. Consequently the
gather copies each physical bit to at most one role tape, and the inverse
scatter has a unique destination for every output bit. Gather followed by
scatter is the identity if the local transformation is the identity.

The complete-packet routes are bijections, including their carries. Thus the
staged value at common coordinate `d` is precisely the role's current owned
value. The inherited frame/data-chart interpretation can be applied without
alteration. The local induction is valid on these arbitrary dirty functions:
equal-frame ADD, MOVE, transported COPY and ERASE see the same logical inputs
as an ideal direct invocation. Original family values are deliberately not
consulted during that induction. The local endpoint is then inverse-routed
and written to the unique owned packet. Unowned bits are never written.

This proves the exact physical-family endpoint conditional on the three
interfaces. A second invocation may reuse packets through other roles; it
must gather the newly written state. No independence or freshness assumption
on the dirty helpers is used. The executable two-call test exercises this
reuse and rejects substitution of the original, stale state.

The gathering of complete unused fields preserves PR2195's child stock
range; it neither promotes original input rows to blank work nor changes
the selected live denominator `28416*N`. Work copies are extra storage and
time, not new logical volume. Support separation proves the selected
application only with the inherited chart construction, not for arbitrary
chart replacements having the same ranks.

## Explicit bill and selected counts

For touched families `F`, let `G=sum_f V_f`, `r` be the role count, `A` the
number of ADDs and `c` the number of COPY episodes. Let `T_i^+` and `T_i^-`
charge the completed owner routes, and `T_e` charge each local address child.
One invocation has the parametric time bound

`C_sel(q,r)*G + C_lin*(r+A+c)*L + sum_i(T_i^+ + T_i^-) + sum_e T_e`.

`C_sel` includes the two family sweeps, their low-class selectors, descriptor
preparation, counters and head returns. `C_lin` includes role copying,
aligned XOR scans, private copies, valid erasures, all work clearing and
head returns. Constants are not silently assigned numeric values. Every
nonidentity owner route and every local child remains in the sum. The bound
does not say that source access, copies or route preparation are free.

With an output buffer for an ADD and at most one live private COPY, role-level
storage is at most `(r+2)*L`. Add `W_max`, the maximum **additional** workspace
needed by a sequentially invoked route/address callee, plus its charged
descriptor/counter space. Parked original families are input storage. This
gives `663*L + W_max` for the selected node, not a complete recursive scratch
bound or a bound including the optional family-layout copy. Calls are
sequential, so the same node-level work regions are reused.

The independent source-bound census finds:

| Quantity | Value |
| --- | ---: |
| Selected calls / roles per call | 288 / 661 |
| Owner occurrences / checked helper pairs | 190,368 / 181,056 |
| Touched families per call (number of calls) | 310 (64), 312 (64), 313 (32), 369 (64), 517 (64) |
| Family sweeps, summed over all 288 calls for one low class | 213,056 |
| Owner-route actions per call / summed over 288 | 1,322 / 380,736 |
| Local word in either orientation | 24,305 ADDs, 2,911 MOVEs, nine COPYs, nine ERASEs |

Route counts retain identity actions as well; a later implementation can
omit certified identities. These totals are per low class, not a full sweep
over all `N` classes. They are not rank mass or the numerical `B` invoice.
No global saving is deduced by comparing unlike per-ADD and per-call bills.
The existing local recursive ranks and selected global profile stay fixed.

## Executable evidence

The checker imports no predecessor implementation. It authenticates the
selected template, reconstructs every same-family support pair, checks both
literal local hashes, and propagates all 661 Boolean columns through both
27,234-event words. This last check covers decoded dirty algebra and COPY
guards; the rational frame/physical address theorem remains inherited.

The separate sequential compiler fixture covers the complete `GL2(Z/9)`
family: 3,888 matrices, 48 low packets, three complete unused values and
17 payload bits, hence 198,288 physical bits. Three roles use distinct
low packets and the unit-shear charts `I+tE01`, `t=0,1,2`. Their routes are
implemented by ordered sequential split/merge shifts with explicit carries;
payload routing uses no indexed lookup. Two successive invocations run a
dirty-helper wrap and live private COPY. An independently written full-ring
matrix oracle checks the entire output, including 45 untouched packets.
It also checks all 11,664 symbolic record columns; because operations act
independently on the 17 bits, this proves that fixture's full Boolean operator.

Both invocations together use four family sweeps, twelve owner-route actions
and 24 high shifts. Peak scratch is exactly five packet volumes, **20,655
bits**, and final scratch is zero. `RESULT.json` retains payload read/write,
erasure and head-movement counts. These are an explicit data-movement meter;
Python control arithmetic, descriptor work and allocation overhead are not
measured Turing-machine time. The parametric proof charges those separately.
The fixture needs no ordinary recursive address child; it is not a miniature
execution of all selected GL64 frame operations.

Seven controls reject a missing high carry, wrong inverse route, omitted dirty
restoration, incomplete unused range, same-low chart alias, stale second-call
state and a collision inserted into the actual selected owner certificate.

Python 3.12, standard library, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/bit-whole-packet-staging
python3.12 -I -O -B research/bit-whole-packet-staging/verify.py
```

Expected marker: `PASS_BIT_WHOLE_PACKET_STAGING`. Verification compares a
deterministic receipt without rewriting it. `--write NEW_PATH` explicitly
regenerates a receipt. A second registered command replays without Git in a
temporary source export, confirms that replay writes nothing, and rejects
actual on-disk receipt and source corruption. No selected cold replay or
hosted CI pass is claimed.

## Scope, provenance and credit

Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Task-picker seed `b1074e2d29bc056660070bddeb220bda`, bit-mechanisms track.
The assigned first working example passed with 661 columns and eight controls.
The changed scope and bounded live-overlap coverage are retained in `TASK.json`.
`SOURCES.json` pins consumed repository bytes and the exact external proofs.

Credit Jose Manuel / jmbarrancoml, PR2195
`3a1cf78a1ba6322129e42d80c50d21765524d612`, for complete-packet separation,
the per-ADD physical selector and live-row layout; alephnan, PR1627
`7943acd4b430dd4286e32954237136ee9657be3b`, for the literal and whole-call
proof; eumemic's PR490/555 and DreamingOfClouds' PR589 for the supplier;
the repository's elementary stream model; and the earlier hosting/owner work
retained by those sources. Ross Richardson's PR2437
`4ac2b3826140b782020145a547f9b6692ebd3d32` identifies the analogous remaining
physical obligation for the changed R439 word. We do not claim that word's
complete admission here or duplicate its ideal binding.

Prepared for **ywz65** with substantial **OpenAI Codex** assistance in scope,
proof, implementation, testing and writing. Apache-2.0. Separate AI review
is recorded in the submission handoff; no independent human review or formal
kernel proof is claimed. No selected exponent or supplier is changed.

## Open next questions

1. **Can the 663-packet node reserve be parked across recursive children on a
   fixed global tape set?** Start with the depth-first schedule in
   `upstream/build/sections/04-swap.tex` and specify child entry/return,
   parked parent payload and scratch separators. The unresolved contracts
   are completed weighted callees and their additional work volumes.
2. **Does this whole-call schedule improve a complete selected routing bill?**
   Instantiate `T_i`, `T_e`, selectors and preparation for one actual call,
   including good and fallback children. The concrete route/compiler costs,
   rather than the family-sweep count alone, determine admission.
