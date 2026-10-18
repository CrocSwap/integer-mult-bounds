# Whole-residual pooling and per-invocation kernel choice

## The sufficient construction

Retain the whole-residual hosting interface of PR442/451. A local invocation's
helper, including its entire address-space function, is placed in ONE idle data
family. Its full residual projector block has width w and is contained in that
family's pending idle projector. Use the prescribed residual isometry, slot
permutation, and its inverse around the COMPLETE dirty invocation. The route does
not replace one family function by functions on several families.

The invocation's endpoint on that family contributes the projector factor D_P.
Its target data effect is unchanged by the checked local all-column theorem. The
family is untouched until its named idle child, so that factor can be commuted to
the child. On the SAME family, D_P D_(Q-P) = D_Q for P≤Q; the replacement complementary
child therefore restores exactly the original child. The rule works for arbitrary
correlated contents under the retained complete-dirty-slot interface. Within one
family, multiple residual blocks are disjoint, and the chronological windows are
checked for every invocation.

A replica number is only a selector naming physical families. The above sufficient
proof uses the actual host pair, family, support and idle window; it never requires
the host and invocation replica numbers to be equal. Assign whole residuals from
all eight replicas to a common pool of 1920 copies of each child. Preserve each
helper as one family slot. This reduces fragmentation without the disputed
cross-family splitting of PR448. Every extra selector and route factor is charged.

## Heterogeneous, but equivalent, complete invocations

The base rank149 kernel and the rank147 kernel obtained by removing pivots963,970
have the same universal scalar endpoint, including every dirty column and erased
private work. Both actual forward and reverse streams and source-span legality
are separately checked. Therefore a call site may select either complete stream.
This is substitution of an equal implementation at an entire call boundary, not
splicing partially initialized programs.

Select the rank147 provider only at stage5, replicas0 through4. Stage5 is reverse;
these calls use the checked full `variant-reverse` stream. All83 other invocations
use the base provider. Each selected invocation changes the local histogram by
{1:-2,4:-4,5:+4}, and two width7 helper residuals become width8. The resulting ten
extra residual coordinates are packed in the GLOBAL whole-owner pool, so local
and exterior costs are recomputed together.

The frozen finite assignment gives65120 whole residuals on9600 live families,
physical reserve9609, no helper banks, no padding, and no split owners. Its final
paid profile is:

1:217742; 2:93314; 3:23976; 4:30912; 5:8732; 6:5752; 7:5168; 8:792; 42:1; 56:444.

Rank mass is745536 and deficit78*9600-745536=3264. Maximum child rank56 satisfies
2*56^3 <78^3. Relative to the uniform rank149 globally pooled witness, the complete
change is {1:-10,4:-20,5:+20,52:-1,42:+1}. No component gains are added.
Exact rational moment and outer assembly belongs to the root deliverable's receipt.

## Explicit realization and independent checks

`emit_whole.py` reads frozen integer bin patterns and stage/width counts. It
allocates one complete residual to one bin interval. The family address is
`hostReplica*1200 + hostPair*240 + copyWithinPair`. Its pending-axis start is
`8 + 7*sourceLevel + offset`. Every coordinate is checked against the child's
actual interval and current chronological window.

`audit_whole.py` does not import the generator. It rederives all windows, checks
all physical (family,absoluteAxis) coordinates globally, verifies each local width
and exact provider dispatch, rejects duplicate/omitted owners and every split,
reconstructs the paid profile and emitted instruction digest, and runs adverse
controls. Its provider registry binds word hashes, source records, all helper
entrance frames, residual-isometry recipe hashes and local stream hashes. Legacy
top-level source metadata is explicitly labelled as describing the base provider;
the per-call registry is authoritative for mixed calls.

A fresh unbanked scalar replay executes all88 actual selected streams, bridge
shears and terminal exchanges on9340 independent basis columns per replica,
including all8140 helper columns, with private scratch zero at each call boundary.
This checks the heterogeneous controller itself, in addition to the two source
providers' native checks. Physical hosting follows the retained universal dirty
slot theorem and the independent whole-owner/window audit.

Route-extra3 is conservatively charged: the single whole residual requires the
same slot/basis route asPR442; the extra selector allowance covers foreign replica
selection. Program dispatch and both source-provider finite reserves are charged
in the final root invoice. The exact final artifact never uses the earlier
experimental cross-family coordinate pieces.

## Sources and structural analogues

- PR442/451: complete dirty invocation hosted WHOLE in an idle family; window
  commutation and complementary same-family projector child.
- PR450: target mixing; PR451: rank149 kernel and the cross-family trace review.
- Mathlib/Data/Matrix/Block.lean, `Matrix.fromBlocks_multiply` atline214 supplies
  the same-family projector identity by exact block multiplication.
- Mathproof/MUBProjectionInduction20260923.lean, `atoms_mul` and `weighted_mul`,
  expresses orthogonal-idempotent factor arithmetic. Source inspected by the
  independent scheduling reviewer. This does NOT identify family direct sums
  with tensor products of address-coordinate arrays.
- Mathproof/LinearAlgebra/Matrix/DeterminantalComplexity.lean aroundlines98-105
  uses explicit matrix reindexing for block construction. Here reindexing is used
  only to rename an entire family slot, never to split a function among families.

These library links are structural/source analogues, not new Lean certificates.
The transport optimization uses known integer pattern packing and exact finite
witness reconstruction. The new construction relative to the read PRs combines
whole-family global replica pooling with per-invocation equivalent-kernel choice.
No literature-wide novelty claim is made for either general principle.

## Scope and rejected draft

The earlier `PROOF.md` is explicitly RETRACTED: its proposed cross-family splitting
confused address-coordinate factorization with family-space direct sums. PR451's
trace obstruction applies. Its combinatorial receipts are not operator evidence,
are excluded from the final construction, and establish no kappa improvement.

The successful result retains PR442/451's whole-dirty-slot, all-size compiler,
compressed-window, precision, row and analytic assumptions. It is a finite
conditional construction, not an unconditional integer multiplication theorem or
Lean-certified closure. Independent native provider tests plus this audit and the
root exact invoice/moment assembly establish precisely the packaged conditional
claim, once those receipts are all present.
