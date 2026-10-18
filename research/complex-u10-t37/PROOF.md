# U10 local word (this package)

The only mathematical change relative to PR942 is the local word. U10 equals PR869's U8 plus two further
triangle-hybrid deliveries (construction/u10/RECIPE-U10.json). Its scalar map, frames, entrances and cones
are checked exactly by the independent `audit_local.py`; its paid profile is
`{1:2548,2:338,3:450,4:154,5:76,8:8}` with unchanged widths, start/end frames and local prefixes. Every
statement below about the owner construction, banks, prefix charge and the all-replica bound applies
verbatim with the U10 local profile in place of U8's; the all-T bound is recomputed for U10
(evidence/ALL-T-BOUND.json) and its grid upper equals the claimed 0.001662039077758742.

# Conditional T37 whole-owner construction

The frozen construction gives conditional

\[
\kappa=0.001661960547713947,
\]

an increase of 0.000000002773066918 over PR890. It retains the U8 local word,
its whole-helper widths, the nine-stage geometry and the PR589 bit supplier.
The changes are a 37-replica owner assignment and a charged 1024-bit complex
prefix allowance. The all-size and physical-realization assumptions listed
below remain hypotheses.

## Frozen owner construction

Start with the source-bound T21 assignment from PR890 and the inherited T16
assignment. Give T16 a disjoint namespace by adding 21 to its replica and
owner-replica indices, 2352 to its copy indices and 18816 to its family indices.
The complete-call orders have 189 and 144 entries, respectively. Merge the
T21 entry at index i with key `(144*i,0)` and the T16 entry at index j with
key `(189*j,1)`. Sorting these keys preserves both old orders and breaks ties
in favor of T21. It yields 333 distinct stage/replica calls.

Apply the eight explicit role changes in `EDITS.json`, then recompute their
copy and physical-family identifiers from their owner, child and port. The
files `ORDER.json` and `OWNERS.json.gz` freeze the result; no optimizer or
choice of a favorable run is part of verification.

The local remainder trade is

```
44 + 3 + 2  ->  48 + 1.
```

The affected width-four, width-nine and width-eight roles can fill the two
capacity-32 slots as `32 = 8 + 6*4` and `31 = 3*9 + 4`. Their exact identities,
source locations and destination offsets are specified by the eight edits.
The other 167,824 roles are unchanged apart from namespace and call-time
renumbering. The final residual histogram is `{48:11086, 1:6}`.

Stable interleaving retains the predecessor timelines, but it alone does not
justify a new cross-group owner assignment. The independent owner audit
therefore reconstructs each actual source-event and bridge window and checks
every one of the 167,832 roles. It checks full width, physical-family identity,
the coordinate chart and offset, disjoint occupancy, inactivity of the owner
during the complete invocation, and complete residual coverage. A helper is
never divided between physical owners. The independent frozen constructor
rebuilds the assignment from the T16 and T21 source data without importing a
search program. Omitting any one of the eight edits is rejected by the
construction/owner controls.

## Local provider and global profile

Every call uses U8 with local profile

```
{1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}
```

and width inventory `{4:80,5:32,7:54,8:122,9:216}`. There are 504 helpers
per call, 333 calls, 33,152 live families and 33,666 physical families. Adding
the actual residual histogram gives

```
{1:848490, 2:112554, 3:148518, 4:53946,
 5:23976, 8:2664, 48:11086}.
```

Its rank mass is 2,408,256 and its deficit is
`73*33152 - 2408256 = 11840 = 37*320`. The controller audit derives this
histogram from the emitted program and the literal owner assignment; it is
not accepted solely as an input to the arithmetic.

The reconstructed U8 provider retains its complete arbitrary-input scalar
identity in both forward and inverse-transpose orientations, exact native
phase recipes, residual wrapper frames and the inherited end controls.
The five temporary dedicated-bank groups have 8,8,8,8,5 active lanes.
The independent parent audit checks the partial group's complement coordinates
as well as the four full groups. Every dedicated bank is removed from the
final hosted controller, leaving the stated physical stock.

## Charged prefix and finite invoice

The retained conservative prefix estimate at T37 is

```
72 + 37 + 333 + 333 + 4 = 779 bits.
```

This does not fit PR890's 512-bit complex allowance. The present construction
charges 1024 bits, including a row-prefix charge of 2048, and recomputes the
finite invoice and bootstrap cutoffs with that value. It does not assume a
sharper unproved prefix estimate. The retained bit supplier keeps its original
512-bit allowance.

The resulting physical row coefficient is 17495, strictly below the retained
20161 ceiling. The proper-child halving check is `73^2 = 5329 > 4608 = 2*48^2`.
The finite bridge and coefficient bounds are checked against the unchanged
retained constants. The widened allowance follows the existing parameterized
invoice convention; numerical savings do not excuse any prefix or row cost.
The payload controls mutate the actual prefix, allowance and row fields and
require the adapted assembly to reject invalid cases.

## Exact price and fixed-family upper bound

Two retained, independently implemented rational interval engines establish
that the complex moment is less than one at

```
b = 0.001664727258740678855772
```

and greater than one at its successor on the 10^-24 grid. The unchanged PR589
bit endpoint is `0.001733427039589844234749`, with its existing exceptional-
residue accounting retained. The seven-step outer construction checks all
47 strict inequalities at the claimed kappa and rejects the next 10^-18 grid
value. Its finite bootstrap cutoffs use the charged 1024-bit complex allowance.

[ALL-T-PROOF.md](ALL-T-PROOF.md) proves that every positive replica count in
the same U8 profile, whole-helper width, idle-capacity and outer-recipe family
has the same kappa grid upper bound. It uses the inherited signed bin prices
and a new supporting cost/credit inequality. It relaxes chronology and owner
geometry; this construction supplies a feasible witness attaining its grid
bound. The result does not prove the exact real-valued optimum or uniqueness
of an owner assignment, and does not exclude different words, helper splitting,
provider mixtures, capacities or outer geometries.

## Verification and remaining hypotheses

The default package verifier cold-rebuilds the selected PR589/PR741/PR799
ancestry, verifies its mandatory stage coverage and source/artifact bindings,
then reconstructs U8 and runs the new construction, parent, owner, invoice,
arithmetic and admission checks. An explicitly supplied completed PR799 replay
must pass those same ancestry and binding checks. Generated adaptations are
bound to the pinned sources and literal edit records; the strict replay
rechecks the discovery nomination independently. Final binding requires the
matching word, role, chart, parent, profile, invoice and price receipts and
the complete required control inventories.

The proof establishes a finite conditional construction, not an unconditional
integer-multiplication theorem or a measured implementation speedup. All-size
compilation, common-label/mutable-source realization, whole-call hosting,
precision and tape bounds, analytic transfer and the bit H1-H5 contracts remain
inherited hypotheses. Verification covers the selected dependency lineage and
this construction; it does not claim execution of every historical test in the
repository. Source attribution and AI assistance are recorded in
[NOTICE.md](NOTICE.md).
