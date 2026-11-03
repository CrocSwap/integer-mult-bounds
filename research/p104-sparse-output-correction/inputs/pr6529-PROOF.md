# Construction and cost

All event indices in this table refer to the zero-based PR6453 source program.
The fields and frames retain their source labels.

| Field | First move | Export | New carrier injection | Sign change | Second move |
| --- | --- | --- | --- | --- | --- |
| 368 | 8352: 243 to 517 | 8398 | before 9101: add field 368 to field 782 at frame 243 | 12879 | 12893: 517 to 127 |
| 336 | 8393: 240 to 518 | 8402 | before 9048: add field 336 to field 781 at frame 240 | 12923 | 12924: 518 to 127 |

Each first, intermediate and final frame has dimension 4, 8 and 9. Each
interval contains one export and one `SCALE -1`, with no other write to the
held field. The constructor checks every event in each interval.

Delete the first move and the export. Keep the field at its first frame.
Insert the indicated carrier addition. Move the sign change to the held frame,
then replace the final move by the direct rank-five move to frame 127.
Both injections precede their sign change. If a scale preceded an injection,
the constructor would divide the injection coefficient by that scale.
All original public boundary frames stay fixed.

## Exact output correction

Let `S` be the desired scalar endpoint on all 770 public inputs. It is the
identity with the 104 main shears. The constructor starts its row calculation
in the coordinates `y = Sx`. Thus an unchanged source ends at the identity.
Owned initialization and erasure keep their literal chronological positions.

After both fusions, every output outside frame 127 is exactly its required
coordinate. The 572 outputs at frame 127 depend only on those same 572 output
coordinates. Only 28 rows in this block change. Exact rational elimination
reduces this block to the identity. It emits 569 dyadic scalar gates, all at
frame 127. Every pivot inverse is dyadic; the full word checker also verifies
that each scale is a signed power of two and every coefficient is bounded.

This supplies an explicit inverse for the changed block. It does not infer
invertibility from a modular rank or a numerical residual. A second replay of
the emitted correction returns every public row to the required endpoint.
The separate dense reverse checker then verifies all 799 columns, including
the owned coordinates. The retained explicit zero-cache check still passes
at the final frame-127 clear of field 782. Other owned erasures retain the
source's stated framework assumption.

## Native operators and complete price

Every remaining move has nested frames in its declared direction. The native
checker lowers each distinct map and checks its signed Pauli action and exact
global phase. It also checks all helper normalizers and 208 main adapters.
The scalar endpoint proof and these native identities give the same main and
independent-helper boundary at every positive tensor width under the retained
native framework assumptions.

Each fusion replaces a paid rank-four and rank-one job by one rank-five job.
It adds no productive target, owned lifetime or native boundary adapter.
Its scalar repair is included in the ordinary-work and coefficient bounds.
For `Hr = r^(1-kappa)` and `0 < kappa < 1`,

```text
old paid - new paid = 2(H4 + H1 - H5) > 0.
```

The unchanged mixed caller makes eighteen native calls. Its queries, idles,
main targets and ordinary normalizers remain charged. The complete signed
gain is `36(H4 + H1 - H5)`. The target count remains 13,652, the paid count
falls to 67,096, and rank-mass surplus remains 760.

`pricing.py` differs from the frozen source only by the six declared edits in
`PRICING-EDITS.json`: the claim, tested saving, comparison claim, paid count and
two result descriptions. It retains both rational interval engines, the strict
root enclosure, completion, compiler, precision and outer inequalities.
The final verifier also prices the unchanged source at the new claim; both
engines reject it. The source's inherited improvements are therefore separate
from the new increment.

This is a conditional construction with local verification. It does not remove
any of the five framework assumptions or establish independent acceptance.
