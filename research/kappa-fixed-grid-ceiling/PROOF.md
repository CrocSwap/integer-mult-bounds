# Maximum on the declared fixed kappa grid

Let C be the unchanged certified complex supplier endpoint, F=10^30046 the unchanged floor denominator, and B=10^(-30022) the unchanged positive backoff. Every point in this free-gap family uses 0<epsilon<1 and 0<q<b<C, and reports K=floor(F epsilon q)/F-B. Since C*F is an integer and epsilon*q<C, integer ordering gives

`K <= C - 1/F - B`.

This is a bound on the declared grid/backoff family, not on arbitrary suppliers, other backoffs or finer grids.

Choose r0=10^(-30080), zeta=r0/100, layout slack=gap=r0, stop=r0/10^6, b=C-r0, q=C-2r0, delta=(1025/1024)r0, epsilon=1-delta, beta=1-3delta. Then 0<C-epsilon*q<1/F, checked exactly. Hence the reported K equals the bound: `C-1/F-B`.

All 62 retained strict inequalities are rechecked. The main-binding family condition is made explicit as a 63rd guard: Gaussian saving minus main saving is delta*(1-2q)>0. This condition was previously implicit in the checked beta window. It matters for rejection controls when the kappa floor/backoff is coarser than the new free gaps: a beta outside the main-binding window might still exceed the lower rounded kappa, but is not in the declared main-binding family. The original 17 mutation vectors are retained; no original inequality or parent assertion is removed.

The independent nine-cost derivation verifies the new point, compares the exact prior PR2161 point, and proves the positive gain without using displayed decimals. The gamma spare power remains r0/1024>0. All eventual cutoffs remain asymptotic; no practical cutoff is claimed.

The supplier, native words, owner map, invoice, primitive endpoint and fine engines are unchanged. Their original complete finite admission is source-bound reuse of the previous personal replay. PROVIDER-POINT.json additionally records fresh evaluations of both original fine engines at b. The inherited all-size/compiler, realization, hosting, precision/tape, recovery, analytic, prime-theorem and bit hypotheses remain conditional.
