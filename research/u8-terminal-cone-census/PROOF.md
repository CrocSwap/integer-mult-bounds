# Necessary terminal cones under monotone common-frame restoration

Let `P` be the exact compensated U8 scalar prefix and `B_k` its end-of-B
binary frame on register k. There are 728 independent arbitrary scalar
inputs, including 504 arbitrary helper contents. Fix the prefix, its frame
assignments, entrance frames and end-B frames. The suffix may change its
scalar word and helper endpoints, subject to these restrictions:

- Only invertible linear ADD and nonzero SCALE primitives on the same registers.
- Each ADD acts on two registers at the same current frame.
- After end B, frames only grow by subspace inclusion.
- No new COPY, ERASE, clean ancilla, frame reset or descent.
- The prescribed final data shear is independent of incoming helper dirt;
  each helper is restored identically, without residual scalar helper mixing.

These are the scalar/common-frame hypotheses of this note. Native lowering,
phases and physical hosting are additional obligations for a construction.

For helper q, every possible terminal frame `U_q` contains

```
C_q = span(B_q,
           {B_k : (P^-1)[q,k] != 0},
           {B_k : k != q and P[k,q] != 0}).
```

All supports refer to exact rational nonzeros. This joins full subspaces,
not the count of distinct generators. The criterion follows the cold-ended
helper lineage in PR591/604/635; this note applies it to all 504 U8 helpers.

The first term follows directly from monotonicity. For the inverse-row term,
the suffix scalar map is `C = J P^-1`, where J is the prescribed final shear.
The helper row of J is the q-th identity row, so `C[q,k]=(P^-1)[q,k]`.
Track formal dependencies on end-B coordinates during the suffix. A nonzero
dependency originating at register k can reach q only along ADD edges whose
common frames contain `B_k`; frame growth never removes that subspace.
Thus every nonzero entry of the final row requires `B_k` contained in `U_q`.
Cancellation can remove a dependency, but cannot create an entry without
such a path.

For the dirty-column term fix a proposed `U_q`. At suffix time t let `H(t)`
be the registers whose current frame is **not** contained in `U_q`. The set
only grows. Equal-common-frame gates never cross from H to its complement:
the two incident frames either both lie in `U_q` or both do not. Scalar
gates within H are invertible on its entire vector of coefficients of the
independent incoming dirt variable q. Promotions append coordinates to that
vector, preserving a preexisting nonzero vector. Hence a nonzero q-column
coefficient in any register initially in H cannot disappear from the entire
H vector. The final q frame is `U_q`, so q is outside H; every other final
register has zero q-column coefficient by the prescribed endpoint. The final
H vector is therefore zero. It follows that initially `P[k,q]=0` for every
k in H, proving the dirty-column clause.

This promotion argument uses arbitrary independent helper contents and
invertibility. A cleanup with erasure, extra clean storage, a reset, unequal
frame ADD or a nonidentity helper endpoint is outside the statement.

The exact finite census finds `C_q = U0_q` for **every** current helper
endpoint U0. Therefore any terminal frame strictly contained in U0 is
excluded under these hypotheses. For a dimension-preserving different
orientation, containing C also forces equality to U0. Larger endpoints
remain possible. This does not prove that the present tail has minimum
paid cost: one can seek cheaper climbs or scalar words at the same endpoints.
Changed prefix dirt responses or end-B frames also escape the result.

The row plus own-monotonicity clause alone closes 496 helpers. Helpers
347, 349, 359, 361, 370, 371, 372 and 373 have a rank-eight row-only minimum
and a rank-nine joined minimum. Their independent dirt columns supply the
missing dimension. All begin in rank one; their residual widths remain
eight. These eight indices are not identified with U8's eight added holders.

The structural argument above is a written lemma; the programs independently
certify its finite premises and joins. Neither is a formal verification of
the all-size integer-multiplication theorem.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
