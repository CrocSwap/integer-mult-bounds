# Simpson/binomial tilt-root oracle

The audited law is the nine-atom declaration in the three frozen inert source objects, with positive weights P_r and tilted masses P_r*r^alpha divided by their sum. The target is E_alpha(log r)=log 5 at the two exact rational alpha endpoints in CASES.json. This engine has not read the separately authored primary implementation or a peer certificate. It uses no source calculator, floating-point arithmetic, Decimal or external dependency.

## Logarithm enclosure

All working real intervals have integer endpoints divided by D=10^100. To evaluate log r, write r=2^k*u, k=floor(log2 r) obtained by integer bit length, and u=r/2^k in [1,2). Then log r=k*log 2+log u. The value log 2 uses the same integral rule at u=2. Repeated rational u values are cached, without assuming unproved logarithm identities beyond this range reduction.

For rational u=a/b in [1,2], use log u=integral_1^u 1/t dt and composite Simpson quadrature with N=32768 even subintervals. At node j the integrand is exactly Nb/(Nb+j(a-b)). Its scaled value D times that rational is bounded by integer floor and ceiling division. Apply the positive Simpson weights 1,4,2,...,4,1 separately to the lower and upper values, multiply by (u-1)/(3N), and round the outer operation outward again.

The fourth derivative of 1/t is 24/t^5, bounded by 24 on [1,2]. Thus the absolute composite Simpson truncation error is at most

```
(u-1)^5 * 24 / (180*N^4)
    = (2/15)*(u-1)^5/N^4.
```

The implementation subtracts/adds the ceiling of D times this exact rational error, so it does not rely on the direction of the Simpson error. At u=1 the interval is exactly zero. Multiplication by nonnegative integer k and addition of intervals preserve enclosure. The reported log intervals are reduced rational endpoints, not decimal approximations.

## Exponential enclosure

Given an outward fixed-point interval x in [0,16), let m=2^128. The elementary logarithm inequalities log(1+t)<=t and -log(1-t)>=t, for t>=0 and t<1 respectively, imply

```
(1+x/m)^m <= exp(x) <= (1-x/m)^(-m).
```

The lower base is rounded down at x_lower and the upper reciprocal base is rounded up at x_upper. Both bases are positive. Each is squared 128 times, with lower squares rounded down and upper squares rounded up at D. Since squaring is monotone on the nonnegative reals, an induction gives rigorous enclosing endpoints after every squaring. The implementation checks x_upper<D*m before forming the reciprocal. The root-domain x values satisfy the stronger bounded-range guard. No convergence estimate is used as a certificate shortcut: the complete outward intervals are evaluated and their endpoint signs must be strictly separated from zero.

The binomial sandwich width is of order x^2/m; the fixed-point rounding error also grows under the squarings but remains enclosed by construction. These observations justify the planning precision, whereas the exact interval sign tests decide whether that precision actually succeeds.

## Tilted mean and signs

For positive rational alpha, multiply each log interval by alpha with directed integer division, then apply the exponential enclosure. Multiply by the exact positive weight and sum to enclose Z=sum P_r*r^alpha. Independently sum positive interval products to enclose N=sum P_r*r^alpha*log r. Dividing [N_lo,N_hi] by positive [Z_lo,Z_hi] yields the directed mean enclosure [N_lo/Z_hi,N_hi/Z_lo]. Subtract [log5_lo,log5_hi] outward to obtain the residual interval.

The left interval's upper endpoint must be strictly negative and the right interval's lower endpoint strictly positive. A crossed or zero-containing enclosure fails, even if its midpoint has the desired sign. All certificate rationals are in reduced integer numerator/positive denominator form. The two calculators need not produce the same interval endpoints because their rigorous methods differ; this oracle regenerates and compares its own entire actual retained certificate.

The universal uniqueness implication is written rather than extrapolated from two finite signs. For a finite law with at least two distinct positive ranks and all weights positive, every tilted mass is positive at every finite real alpha. Differentiating its log partition gives derivative of the mean equal to Var_alpha(log r)>0. Continuity plus the two strict signs yields exactly one root in the certified bracket and, by strict increase, at most one root on all real alpha. The engine checks the finite positivity/distinctness premises; the written argument supplies the all-real conclusion.

## Controls and file admission

Seven controls are executed. Swapped alpha endpoints fail their order guard. Adding one to the rank-two multiplicity reruns the actual endpoint evaluator and must fail the strict bracket signs. A singleton law fails nondegenerate support, and a zero weight fails positive-law admission. The JSON controls reject duplicate keys, a float token and a Boolean used as an integer. An arbitrary exception is not accepted: every control requires its named ValueError diagnostic.

Three literal metadata hashes are bound in source. FILES.json must list exactly eight paths: the two engines, three metadata objects and three inert source objects; each byte hash is checked. The source text must retain its literal law and positive-tilt/target equations. JSON rejects duplicate, float and nonfinite tokens. Retained certificate validation checks exact closed keys, reduced rationals, interval ordering, all nine log keys, both endpoint records and actual Boolean controls/conclusions. Default execution regenerates the complete ORACLE.json value and compares canonical compact sorted-key ASCII JSON. --certificate selects another actual retained file for the same comparison. Only --emit writes.

No numerical first run, import, compile, test or source/peer calculator execution was performed while preparing this code and note. Root owns the serial first-run command, status, resources and immutable receipts. The code uses bounded N-node sums, a handful of 128-step integer squarings and modest certificate output; under 180 seconds and 256 MiB is a planning allowance, not an observed claim. The result certifies the stated tilt root only. It does not discharge recovery, an all-size flow theorem, a physical supplier, all selected assumptions or a kappa/frontier change.
