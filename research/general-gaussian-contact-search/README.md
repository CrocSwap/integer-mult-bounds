# Costed non-nested Gaussian contact search

**Exact rank/invoice model and optional constructive search; no new kappa.**
This extends contact retiming beyond monotone climbs. Every former zero edge is
represented, every changed native warp is charged at its actual Gaussian rank,
and a helper's target rank is its whole relative Clifford rank. Both helper
boundaries may move. The unchanged main, adapter and owned interfaces are frozen.

The positive calibration independently rediscovers #4672's 49-contact / 13-helper
change on its older #4610 word and reproduces its entire paid/helper invoice.
That result and its kappa belong to the predecessor. Bounded searches on the
stronger round-three word have not found a profitable candidate. No exponent,
new physical supplier or universal negative result is claimed here.

## Changed search model

At a node with old subspace U choose either U or U intersect M, where M is the
common kernel of the supplied nonzero nine-bit functionals. A scalar contact
uses one common actual gauge for all operands. Main endpoints, explicit adapter
boundaries and all contacts involving owned C stay at their original gauges.

For canonical gauges C_U and C_V, the actual child C_V C_U^-1 has Fourier rank

    r(U,V) = dim U + dim V - 2 dim(U intersect V).

This applies to downward and non-nested edges. Dimension difference alone is
wrong outside ascending chains. An old zero edge U->U may become a positive
rank child when only one endpoint moves. For a native map K_G transporting the
source chart U to G(U), the changed physical warp is charged at r(G(U),V),
rather than being declared monomial. Whole helper jobs use r(U_start,U_final).
Every helper must remain strictly productive in the searched switch model.

`model.py` derives these ranks from explicit nine-bit subspace sets. It retains
all chronological contacts and previously zero transitions. Its baseline must
reproduce the source paid list exactly. Changed shared G matrices are outside
scope: the maps remain the same, while their changed physical implementations
may require Gaussian children of positive rank.

The subspace formulas are the canonical zero-form case of Dugongue's #4654 Lagrangian
chart grammar. If U subset V and intersecting with M removes alpha and beta
dimensions respectively, the paid four-state table is

    (r, r+alpha, r+2alpha-beta, r+alpha-beta),  r=dim V-dim U,

ordered (00,10,01,11). Thus the mixed state 01 must not silently be assigned
r-beta. Native warp tables are computed from their actual mapped subspaces.
The verifier compares the general rank formula with the exact Clifford B-block
on all 285 ordered subspace pairs in dimensions one through three.

## Explicitly paid symmetric phases

The `--mode phase` variant keeps each subspace U fixed and chooses the zero
form or Q restricted to U, where Q is the binary symmetric matrix
`sum(lambda * lambda^T)` for the supplied functionals. This includes compound
forms; the ambient common-Q switch family is a strict restriction of arbitrary
independent symmetric forms at every node. It changes the unchanged-paid-rank
premise of #4665 and uses #4654's full charged phase-rank grammar.

For a nested paid edge U subset V with old rank r, put
`t = rank(Q restricted to U)`. Its exact four-state rank table is
`(r,r+t,r+t,r)`. On a native warp G:U->V, the four ranks are the ranks of
`0`, `Q|U`, `(G^T Q G)|U` and `(Q+G^T Q G)|U`. A helper's table uses its
whole old rank plus the rank of the phase difference on its entrance space.
Both helper boundaries remain variable. Owned centers stay fixed and fully paid.

The verifier compares every symmetric form on every ordered pair of subspaces
in dimensions one through three against actual Clifford B-blocks: 66,368
transition checks. It also performs 50,128 native-warp checks on the first 12
invertible maps in product order per dimension (all maps in dimensions one and
two). These finite controls check the implementation; the rank identities and
complete source invoice are stated explicitly rather than inferred from samples.

```sh
python3 research/general-gaussian-contact-search/discover.py \
  --mode phase --functionals 1,2 --seconds 30 --output /tmp/phase-candidate.json
```

A synthetic moment sign control confirms that charging a paid rank increase
2->3 can cost less than a helper increase 1->2 earns. It is not a supplier.
Actual current-word phase search receipts are retained separately in
`PHASE-SEARCH.json`: all 511 rank-one forms and 18 named compound forms
returned zero best candidate energy in their bounded floating runs. This is
not an exact exclusion or a search of independently chosen node forms. No
profitable new current-word witness is claimed.

## Coupled subspace/phase moves from Pauli quarter turns

`--mode pauli --functionals X_MASK,Z_MASK` chooses a common Hermitian Pauli P
with those nine-bit masks, and at each contact chooses C_U or C_U S_P, where
`S_P = ((1+i) I + (1-i) P)/2`. This can change both subspace and phase form.
It is a broader neighborhood than the pure symmetric-phase switch family.
The pure-Z case agrees with the rank-one phase model on every edge and helper
of the complete nine-bit source; replay checks that equality.

In binary symplectic coordinates w=(x,z), S_P induces the transvection
`v -> v + <v,w> w`. The inverse zero-chart L_U has basis `(u,u)` for the
basis vectors u of U, together with `(0,z)` for z in U-perp. For Lagrangians
A and B the actual Fourier rank is `rank(stack(A,B))-9`. These definitions
price all four states of every chronological edge. On an ordinary edge the
table is `(r,s,s,r)`; s can be smaller than r. A native G sends the Pauli axis
to `(Gx, G^-T(x+z)+Gx)`, and all four warped costs are explicitly recomputed.
The helpers use the same full relative-rank calculation. No changed warp is
silently declared monomial, and every original zero edge remains represented.

The verifier constructs literal Clifford circuits for the Pauli quarter turns
and checks all nonzero axes on all ordered subspace pairs in dimensions one
through three: 66,060 transition checks and 50,208 native-warp checks (the
same first-12-map scope). This validates the implementation's rank convention;
it does not perform new source-word absolute-phase or supplier admission.

```sh
python3 research/general-gaussian-contact-search/discover.py \
  --mode pauli --functionals 1,0 --seconds 30 --output /tmp/pauli-candidate.json
```

`PAULI-SEARCH.json` names all 255 tested axes and bounded floating receipts.
They returned no profitable candidate. This is a sample of the 262,143 nonzero
nine-bit Pauli axes, with only a zero/common-quarter-turn switch at each node.
It is not an exclusion of all axes or of arbitrary independent Clifford gauges.

## Discovery and acceptance

`discover.py` converts each exact rank table into its rank-power energy at the
recorded test saving. Full paid energy minus full productive helper energy is
retained. In two-state coordinates any table is

    E00 + A*x + B*y + W*abs(x-y).

Physical edge costs are submodular; moving both helper endpoints can add
negative cut weights. A signed-cut mixed-integer model handles those terms.
The contact switches are binary; auxiliary cut variables can be continuous,
using the lower XOR envelope for positive weights and upper envelope for
negative weights. These envelopes give the exact table for binary endpoints.
The emitted switch list is repriced from the complete exact rank invoice and
must agree with the floating objective.

This is discovery only. Floating solver optimality is not an exact ceiling;
a timeout is not a rejection certificate. A useful candidate still needs exact
moment inequalities, an emitted physical word, all-column and absolute-phase
checks, complete compiler/ordinary/outer admission and the inherited analytic,
precision and execution contracts. No such new candidate is supplied here.

Optional discovery requires installed NumPy/SciPy; it is not installed by the
package and is not needed for the registered replay. For example:

```sh
python3 research/general-gaussian-contact-search/discover.py \
  --functionals 1,2 --seconds 30 --output /tmp/contact-candidate.json
```

Use `--source .../inputs/round2-word.json.gz --functionals 1
--fixed-helper-side exit` to rediscover the known positive calibration. It
finds the predecessor profile on the tested environment; no claim of a fixed
solver path or platform-independent discovery output is made.

## Exact replay and results

```sh
python3.12 -B scripts/research_package.py --package research/general-gaussian-contact-search
python3.12 -I -O -B research/general-gaussian-contact-search/verify.py
```

The standard-library replay verifies the 285 canonical ranks plus the charged
phase and native-warp cases above, the complete
source invoices, frozen-boundary rejection, new charges at previously zero
edges and the non-nested-rank counterexample. The fixed 62-node positive
calibration gives paid `{1:2183,2:416,3:507,4:135,5:40,8:8}` and helpers
`{4:28,7:5,8:38,9:337}`, matching #4672. Its strict local gain is certified
with rational logarithm and alternating-exponential bounds, independently of
the optimizer. This is a positive calibration of the model, not a new saving.

The current source has paid `{1:2201,2:412,3:510,4:127,5:40,8:8}` and helpers
`{4:28,7:7,8:47,9:326}`. `SEARCH.json` retains bounded floating experiments,
including uncompleted older product-linearized models explicitly labelled as
timeouts. They establish no theorem. The selected conditional kappa stays
0.00302015 at canonical base b58ad9ef4d4e861b0eaa5dba41742bdc072dca51.

## Open next questions

Change the scalar word or owned-center protocol before expanding these local
sweeps solely because a search implementation is available. Arbitrary
independent Clifford gauges also remain outside the tested finite families.
For any changed model, reprice every old and new edge before further native implementation. A
negative verified energy is the first stopping/expansion gate; solver status
alone is insufficient. The actual physical witness and its complete supplier
admission remain the blocker. This package supplies the search and invoice
mechanism, not an assertion that broader search will yield a breakthrough.

## Sources and credit

Both exact #4610 input words are retained with original commit/path/blob
provenance. The round-two payload is the input used by #4672; round three is
its stronger published successor at 1eb8da6cfb35512c0cc2533413e5ca42f48e13c6.
The optional solver is separate from the independent registered verifier.

Credit Cao Yifan/#4610 for the native words; Cinna Davis/#4672 for coordinated
contact cuts and the positive calibration; Dugongue/#4654 for the exact chart
rank grammar; Cinna Davis/#4470 and its controller lineage; zxv, Jacob Alan
Sussman and all retained E8/scalar/Clifford/native/compiler contributors. Prepared
by Cinna Davis with substantial OpenAI Codex assistance; Apache-2.0. Classical
signed-cut and linearization formulas are not claimed as new mathematics.
