# Two directions are missing at the retimed receiver

Use the exact #7481 native word. The public role 992 moves from chart 520 to 529 at event 39818. Its only later contacts before the removed arrival are ADD39819 from 913, ADD39878 from 1451, and ADD39883 from 1444. The test grants delaying its existing move until after ADD39876, then processing those three destination contacts in the old order. The old role-1451 arrival at event 39877 is retained. No other producer or receiver row may change. This fixes the old bank just before event 39884, with roles 146, 162, 228, 440, 744, 913, 927, 1197, 1358, 1444, 1451 and 1494.

The original removed operation moves owned role 1532 from chart 520 to 529 at rank one. The old tape scales it by −1/2, adds it to role 913 and clears it. A valid replacement must restore the old current role-992 form and the old post-transfer role-913 form, namely \(r_{913}-r_{1532}/2\) at the cut. Grant the single retimed role-992 arrival any rational linear form of the original inputs. If the receiver bank has row space \(U\), the enlarged space has dimension at most \(\dim(U)+1\).

Reverse reconstruction gives \(\dim(U)=12\), rank 13 with the old 992 target and rank 14 with both targets. It also gives the exact identity

\[
r_{1532}=8r_{146}-4r_{992}+2r_{913}-4r_{1444}-4r_{228}+4x_{146}.
\]

For a direct certificate, set \(x_3=-2,x_{22}=-1,x_{32}=-1\) and all other coordinates zero. Every fixed receiver row vanishes and the targets give \((1,2)\). On \(x_0=1/2,x_{146}=-1/2\), with all others zero, the bank also vanishes and the targets give \((0,1)\). The target evaluations have determinant one, so the two target classes are independent modulo \(U\). The independently signed forward probe replay checks the original target values through the old transfer and ADD39886. The unchanged suffix contains no further old external arrivals to chart 529 after this transfer. Jointly changing another arrival would change the premise.

In the exact 17-stage #7113 caller the removed rank-one operation is repeated 17 times. Its full gross credit is exactly \(17\cdot 1^{1-C}=17\) raw at any admissible \(C\), with productive ranks fixed in the proposed edit. Adding a rank-one paid position per call consumes all 17. The exact rowspace obstruction already excludes the stated one-arrival repair when all other costs are granted free. No new word was built.
