# Restricting the global controller to 112 Hamming ports

This note proves the global data interface used by the new whole-owner
construction. It is a restriction of the verified PR514 interface with a newly
verified local provider. It does not infer a new global exponent from a local
rank profile alone.

## The selected coordinates

The original Hamming description has eight coordinate-root ports and 112 code
ports. In the canonical binary labels the eight deleted indices are

`0, 13, 22, 35, 40, 51, 54, 119`.

`PORT-MAPPING.json` gives the increasing injection from the 112 new indices to
the 120 old canonical indices. The new binary port labels are exactly the
selected old labels. The local ambient dimension remains nine, and all 560
helper frames and all helper entrance and final frames remain unchanged. There
are eight private centers instead of sixteen.

The local restriction is not justified by deleting arbitrary internal wires.
`RESTRICTION.json` binds the exact raw and canonical register restrictions;
`TRANSPORT.json` checks the complete transport, including all 12,094 nonzero
arbitrary-helper-dirt compensations. The new independent expanded-program
replay checks all 784 data and helper columns in both orientations, all frame
incidences, the ordered residual wrappers and private erasure. Its final
normalized data action is diagonal in the retained port index, with the same
forward and backward shear identities as the old provider. The new exact
Clifford recipes include scalar phase for every local frame transition and
endpoint adapter.

## Why the global data construction restricts

At the boundary of a complete local invocation, the inherited controller is a
direct sum over the port index. Its nonlocal operations—the paired bridges,
idle children, stage alignments, terminal translations, signed exchange and
cover correction—also preserve that port index. The controller never
interleaves two local invocations. Consequently the subspace containing all
replicas and pair positions of any selected set of ports is invariant under
each complete step of the controller. Restricting to the 112 selected ports
therefore retains the inherited controller identity on this invariant
subspace.

This statement concerns complete, normalized local invocations. The mutable
basis and the dirty-helper cancellation inside an invocation can mix ports;
their legality is supplied by the new local proof and replay. No assumption
that the individual internal scalar gates are portwise is used.

For a retained port, the nine stage recipes in `DATA-PHASES.json` are copied
exactly from its old canonical port. Only the display index `port` changes.
Every binary label `q`, every actual orthogonal axis, every entry and exit
translation, every idle translation and the literal terminal translation is
unchanged. Thus the parent's exact phase-polynomial equalities apply verbatim
to each selected recipe. The inherited number of polynomial evaluations is
explicitly marked as inherited; it is not reported as a new numerical run.
The independent restriction audit additionally reconstructs all 112 actual
orthogonal 73-coordinate bases and checks the literal idle axes against them.

The data family renumbering is explicit. An old family

`replica * 960 + (2 * pair + side) * 120 + old_port`

becomes

`replica * 896 + (2 * pair + side) * 112 + new_port`.

All 16,128 data-owner roles in the 72 calls satisfy this formula. Each call
uses the newly verified local-program hash. All 2,016 nonzero idle-child
records are the selected old records with unchanged ranks and eightfold
replication. The full source-event order, paired bridges, terminal operations
and cover correction are preserved.

## Helpers, stock and the conservative parent invoice

Before final hosting, the 5,040 old bank families are retained and shifted
down by 512 family indices. All 40,320 helper roles preserve their old route,
width, residual interval and spectator coordinates. Every entering helper
still has one whole bank owner during its complete invocation. The restricted
parent has 7,168 data families and 5,040 banks, for 12,208 live families. Its
private intervals reserve eight centers, 560 tableau streams and two
coefficient streams, giving 12,778 physical families.

The old parent contains a legacy bank-padding display field mentioning only
axis 72 and rank one. The actual entering-bank remainders also include rank
nine and rank seventeen. This field is not used as evidence for an executable
bank-padding implementation. The restriction audit reconstructs every bank
footprint from the serialized owners. Their complementary ranks are exactly

| Rank | Number of bank remainders |
| ---: | ---: |
| 1 | 3,492 |
| 9 | 1,386 |
| 17 | 162 |

The fresh conservative invoice uses these actual ranks, together with all 72
new local profiles and all selected idle children. Its total child rank mass
is 888,624, so

$$
73\cdot12,208-888,624=2,560.
$$

The deterministic finite-operation allowance is recomputed with the new
counts. It keeps the inherited compiler factor `64 * 74**3`, the same
orthogonal-cover formula and the same large finite constants. The separate
whole-owner constructor removes every bank family and replaces pending data
children by actual helper routes and complementary remainders. Its serialized
chronology, physical owner uniqueness, phase maps, paid profile and finite
invoice must pass the final independent audits. No whole-owner exponent or
execution claim is made merely from this restricted parent.

## Independent verification

`audit_global_restriction.py` imports only the Python standard library. It
reads the old and new serialized artifacts, without importing the restriction
emitter, local emitter or hosting optimizer. It binds the new local scalar and
phase certificates by hash, checks every retained phase recipe and owner
record, verifies all private ranges, reconstructs the actual bank remainders,
and independently recounts the parent rank mass. Negative controls cover port
selection, binary labels, idle axes, terminal corrections, data families,
canonical routes, local hashes, helper owners, omitted invocations and idle
children, the cover correction, private reserve and unpaid bank remainders.

The result is `GLOBAL-RESTRICTION-AUDIT.json`. The final global kappa receipt is
a separate artifact of the complete new whole-owner program.
