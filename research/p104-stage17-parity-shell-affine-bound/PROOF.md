# A changed erased map and its affine volume

At the exact Type B clocks 4646 and 4660 the #7113 word uses stage-17 IDLE_ONE on role 36. Let M be the scalar window of 13 literal events between the idles. Normalizing the old word on the left by M inverse produces I+P⊗(D−I), where P is the sum of the two complementary rank-one projectors and D is the stage-17 body. The independent engine recomputes M and its inverse, checks both zero corner entries and orthogonality, and matches the rank-two P to exact #7406. Both dirty lanes are independent in the range of P.

On the selected axes 137 through 144, let m=8f for integral width f≥1. The physical body is D=C^⊗m, with C equal to the symmetric Gaussian matrix with diagonal (1+i)/2 and off-diagonal (1−i)/2. It acts as identity on parked axes. The binary square C² is the bit flip, so X=D² is translation by the all-ones vector on these m bits. Define

```text
E = ((1+i)I + (1−i)X)/2.
```

Grant the changed erased map I+P⊗(E−I) and all its work free. The normalized residual that the core must supply is P⊗(D−E). In the common Walsh character with weight w, D acts by i^w and X acts by (−1)^w. E therefore acts by 1 on even w and i on odd w. The four forward residual eigenvalues in residues 0,1,2,3 are (0,0,−2,−2i), with (0,0,−2,+2i) for the adjoint. Transposing the rational P gives the role action of the normalized adjoint. The support in each input lane is exactly the weights 2 and 3 modulo four.

At width one the two active residue counts are 56 and 64 per lane, giving 240 active lane/address pairs and raw residual volume 240/256=15/16 of one old lane. For general width, the roots-of-unity filter has (1+i)^m=(1−i)^m=2^(4f). The weight-2 residue count is 2^(m−2)−2^(4f−1) and the weight-3 count is 2^(m−2). The two-lane rank divided by one old lane volume is therefore 1−2^(−4f).

## Affine chart and directed price

In a fixed parked fibre the retained chart model routes one affine subset of the joint lane selector and common Walsh address, with arbitrary affine coordinate changes. To reproduce arbitrary residual inputs, its image must include every nonzero address in both lanes. An omitted coordinate carries an arbitrary input with nonzero required residual and cannot be restored by the granted fixed erased map.

For every address bit j, choose two other distinct address bits. The weight-two point on them and its weight-three extension by bit j both lie in the residual support in the same lane. Their difference is the j-th unit vector. The same weight-two address in opposite lanes gives the lane-selector unit vector. This construction applies at every m=8f≥8 and shows that every containing affine chart has the full m+1 dimensions. Its size is 2^(m+1), exactly two old lane volumes. The full affine hull and this lower bound survive any invertible affine relabeling of the combined addresses.

For one rank-16 core with charged volume ratio t, #7397’s conditional tariff gives gross 16H(8)−8tH(16) over the eight ports, with H(r)=r^(1−κ) and all other paid and productive terms fixed. A strict saving requires t<2^κ. The directed price at the old crossing bounds 2^κ above by 1.003. The hypothetical t=1 quote is about +0.320691708235 raw, while the required t=2 has upper below −126.39 raw. The exact rational intervals are in `receipts/LEAD.json`. Because H(16)>H(8) for 0<κ<1, the required t=2 cannot improve the paid moment anywhere in this range.

The argument excludes one pure affine address chart for this exact parity erased map, fixed common Walsh fibres and conditional volume tariff. A non-affine extraction, multiple charts, mixed parked fibres, another erased map or a different tariff requires its own charged test. No physical parity shell, routed residual supplier or new recurrence was built.
