# Paid replica monotonicity and its T104 application

For 0.99 ≤ p < 1 define D(p) = 3*3^p - 5*5^p + 5*32^p - 3*48^p. The retained Mathlib proof `tail_power_positive` establishes D(p)>0 by setting t=1-p and bounding the expression below by 30*t-2404*t²>0. The logarithmic and exponential estimates, constants and domain are kernel checked.

The complete ten-replica periodic sum for the credited PR2802 supplier is

    P(p) = 216720 + 58320*2^p + 25011*3^p + 11520*4^p
             + 3675*5^p + 720*8^p + 3589*48^p.

The full count expression is R(T,p) = T*P(p)/10 + D(p)/5. The positive residue D(p)/5 remains charged. The exact T74 predecessor identity and T94 application are inherited from the previous deliverable; they are retained with their proof source and attribution.

The new `frontier_replica_monotone` proves for all real 0<S<T and 0.99≤p<1 that

    R(T,p)/(896*T*73^p) < R(S,p)/(896*S*73^p).

Divide the complete expression into P(p)/(8960*73^p) plus D(p)/(5*896*T*73^p). The first term is constant in T; the second strictly decreases because its numerator and denominators are positive. This is a universal sufficient cost inequality for separately realized profiles. It assumes no allocation oracle and does not assert that every real or integer T has a physical realization.

Taking S=94 and T=104 supplies the cost comparison for the independently constructed literal allocation. Its complete profile is {1:2253888,2:606528,3:260115,4:119808,5:38219,8:7488,32:1,48:37325}. Every one of 381888 roles has its actual helper width, integer-time window, distinct physical family and disjoint coordinate mask checked. Compact prefixes account for every residual child; rank mass is 65088*T and deficit 320*T. The native words, dirty endpoints, scalar prefixes, phases and cleanup are separately authenticated.

Independent directed rational arithmetic encloses the new root between .001717795222616587743198 and .001717795222616587743199. The full release target is the lower endpoint minus 10^-46 minus 10^-70 and strictly exceeds the exact full PR2824/T94 rational.

Both orientations of both native providers have measured scalar/Horner prefix at most 70 bits. A conservative 128-bit local reserve gives 128+37+936+936+4=2041<2048, while the actual complete prefix is 1983. All invocation, bridge, input conversion and arithmetic margin terms remain. Fresh invoice and independent guards reject a local prefix of 129. The actual row coefficient 19545 remains below the unchanged 20161 ceiling. No new per-replica norm estimate or uncharged dirty helper is used.

The full changed source/controller, physical invoice, ordinary bootstrap and modern outer release pass separately. All unchanged native chains are authenticated reuse from earlier fresh checks. These finite certificates retain the inherited all-size compiler, source-access, hosting, precision/tape, recovery, ordinary-recursion, bit-supplier and analytic-transfer contracts. The Mathlib module proves the stated cost inequalities; it does not prove the full unconditional multiplication theorem.

`replay.py` freshly rebuilds every owned module against pinned Lean 4.34.1 and Mathlib sources. The defining-module audit includes every private/generated declaration and traverses all axiom dependencies; only propext, Classical.choice and Quot.sound are permitted. Real ownership and unused/public/private bad-axiom fixtures independently test the auditor. See validation/KERNEL.json and FRONTIER.md for exact scope and attribution.
