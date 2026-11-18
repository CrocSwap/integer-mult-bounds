# A causal single-delivery rank floor for the current BIT word

Every original paid arrival in the pinned PR7001 word already has minimum
rank among single nested deliveries from its original causal chart libraries.
The statement holds for all 2871 arrivals in each orientation. It permits
free storage of all past paid banks and free scalar XOR formation. No strictly
lower-rank replacement exists. This gives no new kappa.

## Boundary and optimistic library

Keep every original public input independent. Keep the required arrival row,
arrival chart and deadline of one paid MOVE. Let its source be A, destination
be D, clock be c and old rank be `r=abs(dim(A)-dim(D))`. At each retained chart
B, grant the span of all public entrance rows there and all original paid
arrivals at B with clocks strictly less than c. Grant storage and all scalar
XOR operations on these rows for free. A replacement can form one row at B
and deliver it to D through one nested transfer of rank
`s=abs(dim(B)-dim(D))`. The arrival must equal the original row for every
arbitrary input. Also permit a free same-chart reconstruction with s=0.

This is an optimistic algebraic model. It gives away formation, storage,
ownership, disposal and ordinary costs. It grants every rationally nested
pair from the 636 retained charts, even if a positive construction would need
further native or compiler work for that pair. Failure in this larger model
excludes its physical subclasses. There are no distinct equal-frame charts.

The model does not permit a new chart, changed deadline or required row,
multiple paid deliveries, cross-chart ordinary synthesis, matrix-valued
coefficients, a helper promise, or an adaptive change to the original library.
It does not classify general network rewrites.

## Why the library is complete

Every scalar row made by the original program at a chart lies in this library.
An entrance row is included. INIT adds zero. A cocharted ADD adds two rows
already in the span. SWAP carries each row with its chart. CLEAR removes a
row. A paid MOVE is the only operation that introduces a new row at another
chart, and that arrival is included at all strictly later clocks. Induction
therefore covers every original live or past row, and every scalar XOR of
those rows. No choice of a particular donor lane is imposed.

For a required arrival functional f and a candidate donor library V, a dual
z with `v*z=0` for every v in V and `f*z=1` proves `f not in V`. The all-zero
public input and the public input z give identical library observations but
different required arrivals. Thus no allowed scalar reconstruction can work.
The candidate transfer leaves the normalized scalar row unchanged, so a
lower-rank transfer cannot cure the missing source information.

## Exact whole-word certificate

The first geometry path uses primitive integer row elimination. The second
checks orthogonality against exact rational complement bases. They agree on
all 51156 ordered nested-or-identical chart pairs. This includes 636 identity
pairs and 50520 strict nested pairs. They check the full finite chart set,
including pairs not used by the original word.

For every original arrival, enumerate every pair ending at its destination
whose rank is strictly lower than the old rank. Keep the original deadline.
The certificate contains one separating dual for each ordered case.

| Orientation | Arrivals | Lower-rank cases | Library pairings | Nonunit duals | Maximum dual support |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forward | 2871 | 38580 | 291838 | 1771 | 72 |
| Transpose | 2871 | 31777 | 205844 | 1096 | 10 |

All 70357 required-arrival pairings equal one. All 497682 eligible-library
pairings equal zero. The largest permitted library has 545 independent rows.
The 5742 zero-rank cases cover destination reconstruction; the other 64615
cases test cheaper positive-rank paid paths. No case remains unresolved.
[CERTIFICATE.json.gz](CERTIFICATE.json.gz) contains the ordered geometry and
all clock/donor/rank/dual records. [RESULT.json](RESULT.json) gives the counts.

The original source library is a positive control. For every arrival, a
separate set-based rank check confirms that its required row is in the earlier
library at A. Its original route is nested and has rank r. Thus the lower
bound is attained in the declared model, rather than merely excluding an
empty class of replacements.

## Complete signed consequence

For every positive power t, the tariff `r^t` increases with r. Since no
replacement rank is smaller, no allowed one-delivery replacement reduces the
paid moment. Productive targets are unchanged. The source caller has 36 native
invocations, 107352 paid calls, 19950 productive targets and rank surplus 1506.
All fixed query, idle and root terms remain charged. Its compatible savings
upper is exactly zero. Any additional nonnegative completion cost preserves
this conclusion. This applies in particular for every `0<=kappa<1` with
`t=1-kappa`; no root approximation or historical caller ceiling is needed.

This does not exclude an adaptive sequence that first pays for new library
information, or a simultaneous network whose source rows differ from the
original libraries. Such a proposal needs a new contract and complete bill.

## Checks and scope of reliance

The unchanged PR7720 package first reruns its two native interpretations,
all public endpoints and paid rows, exact frame checks, complete invoice and
six controls. [SOURCE-PINS.json](SOURCE-PINS.json) authenticates every retained
file. Its prior single-relation conclusion is not needed for this new rank
floor; the source replay and exact input data are reused.

[generate.py](generate.py) constructs duals with packed binary elimination.
[verify.py](verify.py) reconstructs source rows as coordinate sets and checks
every dual by direct pairing. It independently enumerates the geometric domain
and all cheaper cases. It rejects a zero dual, a dual that fails a donor row,
an arrival used at its own deadline, an omitted case, a false paid rank and an
omitted nested pair. It checks all 5742 original-source attainments.

Both implementations are by the same author after source inspection. This is
not blind review, independent human acceptance or a formal-kernel proof.
The physical caller, native phases, owned storage, compiler, tape and analytic
interfaces remain inherited; all five framework assumptions remain. Full
predecessor suites, selected cold replay, Lean and Docker were not run. No
physical construction for the free retained storage is claimed. No selected
frontier change follows.
