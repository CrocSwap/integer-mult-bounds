# Live projected copies: the exact invisible-update space

In an explicitly changed **rational vector-state model**, a live copy
`t=P c` permits a helper shear `c+=A d` until ERASE exactly when `P A=0`.
For the rank-seven projectors associated with all 111 pinned PR589 line
normals, the entire update space is `A=q v^T`, of dimension eight. Every
nonzero such map has rank one. Two distinct such projections simultaneously
copied from the **same center** force A=0.

This is a conditional replacement-interface lemma and a fully priced toy
fixture. The original `bit-copy-live-stabilizer` concerns scalar complete-value
copies, and its condition remains valid. The actual PR1062 word has nine
serial COPY/ERASE pairs; it supplies no simultaneous-copy production example.
We therefore explicitly changed the representation and operation alphabet.
Neither vector addition nor the hypothetical projected-COPY instruction is
claimed to be an admitted selected bit scalar operation or physical address map.

## Full dirty and chronological contract

Let c,d,y be arbitrary vectors in a finite-dimensional rational vector space,
with a clean temporary t. Let P be an idempotent linear map. Execute:

1. COPY `t=P c`.
2. Prepare `c+=A d`.
3. Read `y+=t`.
4. ERASE only if `t=P c` at this cut.
5. Restore `c-=A d`.

The ERASE condition for every dirty c,d is equivalent to `P A=0`, since
the difference is exactly PAd. Testing on basis vectors proves necessity;
linearity proves sufficiency. When it holds, the complete boundary is
`(c,d,y)->(c,d,y+P c)`, for arbitrary initial y as well. Eventual restoration
alone cannot repair an illegal step 4. Moving step 5 before step 4 repairs
any A at the same update cost, but changes when c is available.

For a rational projector of rank r on dimension m, each column of A must
lie in ker(P). Thus the legal update space has dimension `m(m-r)`, and
`rank(A)<=m-r`. These are exact linear-algebra statements, not finite-search
inferences. For `P=I-q q^T/(q^T q)` on dimension eight, ker(P)=span(q), so
`A=q v^T`; the eight maps `q e_j^T` form a basis. A nonzero scalar update
`A=lambda I` cannot satisfy the condition because P is nonzero.

If a second live copy from the same c uses P', the condition is
`im(A) subset ker(P) intersection ker(P')`. For distinct line kernels this
intersection is zero. Two copies of different centers are a different
contract and are not excluded. This distinction prevents overgeneralizing
either the scalar stabilizer or this vector extension.

## Charged model and stopping decision

The hypothetical rank invoice charges the COPY/ERASE pair rank(P)=7,
the target read rank(P)=7, and the two nonzero update orientations rank(A)=1
each. There are three persistent vector roles c,d,y and one clean temporary;
none is discarded. Total rank mass is 16 versus 14 for direct copy/read/erase.
At power p in (0,1], the difference is exactly `2*1^p=2`.
Thus even this optimistic model supplies no saving by itself. A real lowering
may add frame changes, storage or other costs. No physical recursive pricing
rule is inferred from a rational matrix rank, and no new kappa is proposed.

## Source-bound evidence

```
python -I -O -B research/live-projected-copy-kernel/verify.py
python scripts/research_package.py --package research/live-projected-copy-kernel
```

The verifier imports no predecessor engine. It reads the pinned PR589 word's
111 normals, checks their norm-four geometry, rank-seven idempotent projectors
and all 888 update-space basis maps. It executes the full boundary on every
one of the 24 dirty input basis columns: 21,312 cases. For every projector,
a wrong-line rank-one update passes the endpoint-only test but fails at ERASE;
restoration before ERASE repairs all 111 controls. Exact Gram determinants
certify distinct kernels for all 6,105 pairs. No floating arithmetic is used.
SOURCE hashes and full receipt comparison are checked directly; the registered
runner also checks Git blobs and historical task provenance.

Native replay, source scalar-interface admission, all-size compilation,
physical hosting and outer assembly are unrun. The source normals specify
the geometry only. Reusing them does not make this hypothetical copy semantics
identical to an existing physical bit operation.

## Open next questions

Can a real compiler represent the projected copy and lower one kernel update
while it is live? First give an explicit state interpretation and frame-legal
rank-one implementation, charging both orientations and every role. The absent
lowering and an already unfavorable toy invoice block a construction claim.
The structured question and changed-scope declaration are in TASK.json.

## Credit

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; revision 3 draw
`f1c1d66540cfadcdd568ab787b11b53f`. Credit the prior scalar COPY stabilizer
and Cinna Davis's rational family-projector audit (following 1337isnot1337
PR1351), DreamingOfClouds PR589, eumemic PR555, and Sagar Thakrar's PR1062
example. Their retained checks are not alleged to have a defect. Prepared
by woklerx with substantial OpenAI Codex assistance. Apache-2.0.
