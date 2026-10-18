# Investigating and repairing the kappa = 0.1 proposal

**The advertised paired-plane passing row is not a working kappa=0.1
construction. This investigation has not established a replacement supplier
or a new multiplication bound.** It does supply corrected accounting,
explicit tested replacement geometries, a general complex fitting-rank
obstruction, exact Fourier identities, and an outer arithmetic region that
can accommodate the target if the missing primitive and analytic contracts
are supplied.

User assignment: investigate the proposed 0.1 claim and attempt to repair it,
with the objective of getting kappa=0.1 working. This is an explicit target
assignment, not a randomly drawn donation task. Source base:
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`. All new work is isolated in this
package and five sibling packages. The selected conditional result remains
`836330098538459/500000000000000000 = 0.001672660197076918`.

This rechecks the conditional complex row in [PR #3107](https://github.com/CrocSwap/integer-mult-bounds/pull/3107).
It complements [PR #3111](https://github.com/CrocSwap/integer-mult-bounds/pull/3111),
which prices the selected bit supplier's fixed local histogram: the present
audit corrects the private-copy coverage charge and studies replacement
scalar-query geometries.

## What fails in the proposed passing row

The predecessor [budget screen](../kappa010-complex-lever-floor/README.md)
explicitly disclaims a supplier or new kappa. Its d=3 row reports target
moment `0.995605075916`, under hypothetical coverage and repacking assumptions.
We reproduced that arithmetic before changing its assumptions.

1. **Private copies need a complete charge.** For its stated 49-support
   implementation, the per-call copy profile is `{2:2d,4:31d,6:16d}` with
   rank mass `224d`. Under the inherited private-copy coverage law, this
   mass enters both the local profile and total paid mass. Putting it only
   in the former silently removes the same amount of public idle work.
   The corrected centre-retained d=3 moment is `1.091829820390`, above one.
   Even at exponent saving zero the centre-free ratio is `1+d/292>1`.
   A joint implementation replacing public work could change this law, but
   would need an actual operation trace and replacement coverage proof.
2. **Payload replication is not address dimension.** The cited block-rank
   theorem tensors coefficient payloads by I_d. It preserves the same
   binary two-plane geometry; it does not establish u=2d unpaid address
   coordinates. A true geometric lift changes the ambient chart, native
   ranks and recursive template. In particular, a size-three support of
   orthogonal nondegenerate 2d-spaces requires ambient dimension at least 6d.
3. **The original public legs also constrain repairs.** Retaining the
   paired-plane native implementation's 224 separate rank-seven data legs
   forces a moment lower bound of approximately `1.036807899646`, even granting a free decoder,
   two unpaid coordinates and linear-cost placement of all other work.

Exact statements, pinned sources, attribution and controls are in
[the paired-plane accounting audit](../kappa01-plane-audit/README.md).
These are scoped failures of named implementations and accounting laws,
not an impossibility theorem for kappa=0.1.

## Repairs actually attempted

| Attempt | Result and remaining scope |
|---|---|
| Larger port subspaces and a new stage count | A compressed-window necessary condition is k/h > 0.306330187868. The old line geometry, paired planes in nine dimensions and uniform direct-sum lifts fail at every odd stage count under the stated coverage/active-climb laws. See [density proof](../kappa01-bit-repair/PROOF.md). |
| True one-third-density ports in F_(2^k)^3 | Constructed the exact family and checked binary trace ranks. A C4-free complex-minrank argument forces more than V/4 paid scalar totals, each of rank at least k. Three-stage moment exceeds 1.051658213344872 for every field size. See [all-size family proof](../kappa01-fieldline-repair/README.md) and [finite controls](FIELD-GEOMETRY.md). |
| All nondegenerate rank-two planes in F2^5 | Enumerated all 80 planes and produced a 30-set exact independent-set cover. Every subset, with multiplicities allowed, has an independent set of at least 2V/5. Even unit-rank paid queries force three-stage moment above 1.016448096636709. The pressure proof also excludes every odd stage count under the same coverage and charge assumptions. See [construction and tariff](../kappa01-bit-repair/PLANE_REPAIR.md). |
| All distinct nondegenerate rank-two planes in F2^6 | Enumerated all 336 planes for each of two explicit forms. Closed row supports overlap in at most four positions, giving complex fitting rank greater than V/5 for every induced subset. Even unit-rank query prices force moment above 1.013886814008956200. See [dimension-six proof and exact masks](../kappa01-fieldline-repair/PLANES6.md). |
| Cheap asymmetric queries on larger binary ports | A character-matrix lift proves `sum_j (2^r_j-1) >= V*(2^k-1)` for arbitrary scalar-query cancellations and repeated ports. It excludes all rank-two binary-port geometries in dimensions four, five and six under the stated model. At h=8,k=3, queries capped at rank six fail, while rank-seven/eight relaxations remain open. See [the general query-charge bound](../kappa01-bit-repair/WALSH-CHARGE.md). |
| Indefinite rational bit geometry | An explicit nondegenerate pentagon escapes the positive-definite sign-class proof. Its complete binary fitting census still has minimum rank three, and it fails the target. The general indefinite family remains open. See the same construction note. |
| Cross-characteristic three-subset decoder | Constructed and priced Gaussian-dyadic queries with total copy charge C=n^2. At n=100 its copy ratio is 0.061843, but its data-only moment is 1.126460 because its port density is only 1/100. An identity-block witness prevents improving the same mask to the required density. See [explicit decoder](../kappa01-haemers-repair/README.md). |
| Replace the separate bit supplier with Fourier address operations | Proved exact shear and fused-swap identities, with an augmented recurrence criterion. A whole-chunk swap takes three joint-width Walsh calls. Applying this to a bit-dependent supplier without charging its adapters is circular. See [outer repair](../kappa01-outer-repair/README.md). |
| Extend the outer numerical parameter domain | Proved an arithmetic region containing bit saving 14/125 and complex saving 9/80. With explicit rational backoffs the controlling margin is 11666316669/115833100000 > 1/10. All 46 non-domain inequalities pass; the unchanged b<1/32 guard rejects. Actual primitive contracts, positive bridge premises and the analytic domain extension remain unproved. |

The scalar-query obstructions retain complete support-span tariffs and
separate public frame changes. They do not exclude a genuinely joint
multi-array primitive, a different free-entry mask or coverage law, or an
operator composition that changes those mandatory data occurrences.

The line-graph argument also has a [three-dimensional corollary](../kappa01-fieldline-repair/LINE3-COROLLARY.md)
for distinct nondegenerate lines over any label field, including indefinite
forms. Its fitting coefficients must be complex. It does not settle the
binary bit-decoder problem on indefinite rational labels; those are different
coefficient and label fields.

The character-rank proof does give a separate conditional bit-side result.
If an integral presentation of rational ports has every port Gram determinant
nonzero modulo 3 or modulo 5, reduction to that field and an odd-order
character table give a valid binary-scalar charge bound. Either good-reduction
condition excludes the rank-one, three-dimensional target. No such modular
condition is assumed for arbitrary rational geometries.

## Actual adapter fusion and the shared-Fourier-frame attempt

The [adapter compiler](../kappa01-outer-repair/ADAPTER-FUSION.md) consumes
both exact native local-interior event streams and implements their address
maps through Fourier calls. The best tested deferred-layout policy still
has target moments approximately 47.62 and 49.12. These are prices of
explicit implementations, not lower bounds on all compilers. Quadratic
phase completion is proved algebraically; the executable checks affine maps
and Fourier-child charges, without emitting a complete scalar/phase ledger.
A separate support argument excludes independent synthesis of the frozen
nonidentity map boundaries on one array, with nonzero diagonal wrappers and
Fourier calls and without auxiliary saved transforms. Fusion across those
boundaries, auxiliary saved transforms, or a different physical frame
assignment changes that model.

A more global repair sought a common Fourier basis in which all frame changes
would become diagonal. Existing degenerate canonical frames are not generally
convolutions, but that observation alone does not rule out changing them.
The [replacement-frame audit](../kappa01-outer-repair/CONVOLUTION-FRAMES.md)
therefore solves the actual source-carry and reader constraints for a
symmetric binary matrix A. It gives both a successful alternative at one cut
and an impossible cut at another. At forward event 13759, helper 445 carries
labels 140 and 161 and has reader labels 14 and 35. The equality

    140 xor 161 = 14 xor 35 = 45 != 0

would require both A45=45 and A45=0. Thus no linear A can satisfy this
particular fixed carry/read replacement contract. Arbitrary equivalent
circuits need not obey that contract; changing the source/read schedule is
an explicit remaining escape, not ruled out by this witness.

## A further elementary limit on coordinate-only repairs

If every port E_i is spanned by a subset S_i of one common coordinate basis,
then every scalar fitting decoder under the same full-orthogonality mask has
total pairing-rank charge C >= sum_i |S_i|. For each coordinate j, the ports
containing j are pairwise nonorthogonal, so the fitting matrix restricted to
those ports is an identity. At least that many rank-one query terms must
contribute to that restriction. Every such term has j in both its source
coordinate union and its reader coordinate union. Its pairing-rank tariff
counts exactly the intersection of these two unions. Sum over j to obtain
the bound. For rank-k ports this gives C>=Vk, which makes the usual deficit
`(s-1)Vk-sC` negative. Common-coordinate ports therefore cannot repair the
model, for any dimension or stage count. This argument does not apply to
arbitrary binary subspaces in different bases.

## Verification and limits

Source pins and exact receipts are retained in the corresponding packages.
All completed replays use CPython 3.14.7 and standard-library arithmetic;
mathematical acceptance uses rational/integer comparisons. The actual
adapter compiler additionally records diagnostic Decimal moments and exact
linear-rank rejection bounds. No CPython 3.12 or hosted CI result is claimed.
No complete selected-supplier cold replay, formal-kernel verification, or
independent human review was performed in this investigation.

The consolidated replay checks its frozen file hashes before and after the
scoped verifiers, and checks that the selected record and original
budget-screen files still match the pinned base. Run it from this worktree:

```sh
python3 -I -O -B research/kappa01-repair/verify.py
```

The original selected record and all frozen predecessor sources remain
unchanged. No public comments, PRs, pushes or selected-frontier updates have
been made. The local Git checkpoint is a research handoff, not certification
of a multiplication theorem. Substantial assistance: OpenAI Codex and its
parallel mathematical reviewers. Apache-2.0.

## Open next questions

The target under the retained transfer needs primitive savings strictly
above 1/9 on both sides, or a proved replacement for the bit-dependent
interface. The remaining construction problem is concrete: produce an exact
native word with its complete charged moment below one at such an exponent,
including its physical frame changes, independent payloads, dirty endpoints,
copy lifetimes, routing and precision costs.

The next useful attempts must change a hypothesis of the failed repairs:
noncoordinate block geometries with cheaper mixed-rank queries; a joint
consumer that actually replaces public work; or global frame/operator fusion
that crosses the frozen recursive child boundaries. The single-supplier
Fourier route additionally needs a self-contained recursion on every shape
used by the caller. The enlarged outer arithmetic region then needs its
supplier, stopping, finite stock, precision and analytic dependencies checked.
The active research objective remains unresolved.
