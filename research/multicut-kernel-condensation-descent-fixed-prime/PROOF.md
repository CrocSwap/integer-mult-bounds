# Exact fixed-prime endpoint on PR263 (whose package is PR259's with the descent retiming stage)

## Inherited physical profile

The input is PR259's complete finite construction, based on the pinned PR249 source package. Its 518 selected pivot entrances, four actual cut positions, explicit donor lifts, nondegenerate subframes, inverse gates, COPY/ERASE windows, and all 3,317,400 bank assignments remain unchanged. This extension changes no physical record, frame, route, role, replica, endpoint, or lifetime.

The freshly regenerated normalized price has `m = 120`, stock `173435`, `3,956,840` child calls, rank mass `20,777,000`, deficit `35,200`, and maximum child rank `50`. Its literal invoice contains 40 replicas, `19,784,200` children, `103,885,000` rank mass, and stock `867175`.

## Rare-class refinement

Fix

```text
q = 2^127 - 1 = 170141183460469231731687303715884105727
rho = 2*m^3/q = 3456000/170141183460469231731687303715884105727 < 10^-16
```

Only the rare-class probability changes from the inherited `10^-16` envelope to this exact density. Every rare child still pays the complete `32*m^2` fallback. The verifier reads the regenerated `62639556732985401` finite primitive coefficient and confirms it is below `2^80 < q`; it also checks the payload signed-prefix guard, 200-factor chart limit, 787 normalizer bound, and all other costs in the full invoice.

Two independent rational interval engines bracket the fixed-prime coarse endpoint on the `10^-27` grid. Both accept the selected endpoint and reject its adjacent successor with exact signs. Decimal arithmetic only proposes the bisection endpoint.

## Eight finite levels and outer assembly

Starting from PR259's completed value `384599/10^10`, each ordinary level follows

```text
a_j = (1-c)c + c*a_(j-1).
```

Eight exact levels reach the grid cap. Every stage records positive atom, borrowing, remainder, and stock gaps; all finite cutoffs are recomputed from the fresh coefficient and those exact gaps.

The outer assembly keeps `beta = 10^-9`, sets `eta = 10^-24`, and retains the complex saving `747454944651775/10^18`. It recomputes all 47 strict constraints and seven margins. The adjacent `10^-27` kappa grid point fails both at the finite saving and at the coarse cap.

```text
PR259 kappa: 142205877210807/200000000000000000
refined kappa: 711032242134072007667807/10^27
gain: 3933391878345881/10^27
```

The gain is exact and conditional. PR259's physical finite proof and PR249's inherited all-size interfaces remain the foundation; neither this certificate nor `Prime.lean` proves the unconditional multiplication theorem or practical runtime.
