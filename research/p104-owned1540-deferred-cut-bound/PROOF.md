# Exact suffix coordinates for the omitted role-1540 transfer

Fix exact #7481 and the signed #7113 caller. Remove the rank-one owned MOVE45656, its sole outward ADD45657 into role 756, and clear the old owned value in source chart 260. Preserve all other old arrivals and scalar contacts up to the cut before ADD58937. There is no intermediate outward use of role 756. It moves to chart 127 at clock 58936. The old owned value just before the removed MOVE is the correction required at this cut. The full signed gross is 17 raw before repairs, and one added rank-one paid position across the old caller consumes all 17. Productive ranks stay fixed.

Let u denote the original 1,501 public input coordinates and y the old final normalized public coordinates. The complete exact #7481 native certificate verifies `y=E u` on every old input. The block-diagonal E is the identity on helpers, with invertible hosted Type A shears and invertible Type B blocks on the main pairs. The replay authenticates the sealed certificate and converts the two required original covectors to output coordinates with these explicit inverse blocks. It checks round trips for both covectors.

Let x be the public state at the cut. Exactly one owned row is then live, role 1568 with value z in chart 240. The literal suffix is a linear map `y=A x+b z` with all other owned rows initialized within the suffix. Let k be the covector on final outputs with `z=k y`, and let t be the covector with required correction `m=t y`. Reverse the suffix on each of k and t to obtain `kA, kb, tA, tb`. If `1−kb` is nonzero, substitution gives

```
z = (kA x)/(1−kb)
m = (tA + (tb)/(1−kb) kA) x.
```

The old public cut map is invertible in this case. Substitution expresses all final coordinates y linearly in x, and their map from original inputs is the invertible E. Hence x determines u and, as the same finite dimension, is a bijective coordinate system. This does not assume that A itself is invertible. The literal values here are `kb=0`, `tb=0`, and `1−kb=1`.

The exact correction covector has 232 nonzero public cut coefficients. Fifty-five lie outside the 1,046 allowed old peer roles. The coefficient on old role 756 is zero, and the coefficient on role 882 is −1/2. The replay constructs original inputs for unit old cut states e882 and e756 by propagating the cut units through the old suffix with the derived live owned value, then applying E inverse. It checks each original input forward through the literal old prefix and verifies both the full cut state and the required old transfer.

The e882 probe has original inputs x772=x882=1 and all other inputs zero. It kills the full fixed peer bank, with old role 756 equal to zero and the old owned correction −1/2. Therefore the modified role 756 is +1/2. The e756 probe also kills all fixed peers, with old and modified 756 both equal to one and correction zero. Any proposed repair `old756=α·modified756+linear readout of fixed peers` would need α=0 on the first probe and α=1 on the second. This excludes arbitrary rational self scaling and ADDs from the fixed peer bank, including any sequence of local linear operations whose only original information comes from these values.
