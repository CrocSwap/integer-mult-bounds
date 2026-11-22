# Partial tensor fusion: a strictly better prospective outer balance

This is a prospective cost theorem, not an implemented resampler. It changes the full-fusion target to a smaller interface whose precision is payable.

Suppose the normalized holes construction is completed so that a g-axis Gaussian group is a fixed number of tensor geometric/Toeplitz convolutions, diagonal factors, and corrections supported on the hole rows, and suppose its halo gather/scatter has the same asymptotic cost. Let d=p^epsilon and a=Theta(log d), theta=Theta(1/d).

The exact normalizations developed in HOLES-AND-Q-LDU.md have local logarithmic range O(a/theta)=O(a d) per axis. Therefore g axes can be fused with O(p) guard bits if

```
g*a*d = O(p).
```

Taking `g=p^(1-epsilon-zeta)` for fixed zeta>0 pays the logarithm and leaves strict slack. There are d/g groups. A group convolution using the retained supplier with saving q costs, after division by full volume,

```
g^(1-q) polylog p.
```

Thus all Gaussian groups cost

```
(d/g)*g^(1-q) = d/g^q
             = p^[epsilon-q*(1-epsilon-zeta)].
```

Its saving is `(1+q)*(1-epsilon)-q*zeta`. The main synthetic transform, using deferred reservations, retains saving epsilon*q. Ignoring the arbitrarily small fixed zeta and strict absorption gaps, balancing yields

```
epsilon=(1+q)/(1+2q),
kappa=q*(1+q)/(1+2q).
```

This exceeds the old `q/(1+q)` by exactly

```
q^3 / ((1+q)*(1+2q)).
```

That is a new outer balance, rather than tighter rational margins in the old family. At the selected complex endpoint the difference is about 4.7e-9. For example take q equal to the selected complex saving minus 10^-10, zeta=10^-8, the displayed epsilon, and kappa ten^-11 below the smaller main/Gaussian margin. The resulting exact arithmetic target is approximately

```
0.00167266475042434534254271472,
```

about 4.55335e-9 above the selected 0.001672660197076918. This is only a prospective target until both missing interfaces below are established.

## Other paid terms

The bit routing saving is larger than q at the selected pair. Moving a group of O(g log p) small coordinate bits across spectator fields costs O(V g^(1-a_bit) polylog p) per group, hence O(V d/g^a_bit polylog p), below the convolution cost since a_bit>q. A superpolynomial untouched spectator suffix remains available while processing a group, so the compact supplier's descriptor work can still be paid; pointwise small-polynomial products require a separately paid small-field transpose but only logarithmic-width fields.

The g-axis scalar normalization costs O(g a), and the stronger local weights cost O(g a d); both fit O(p) by construction. For local convolution window L=O(p/a+d), take a dyadic microtile N≫gL. The total halo volume is bounded by `(1+O(L/N))^g=O(1)`. The gauge increment bound implies total logarithmic variation O(g[a theta N+a/theta]); with N=Theta(gL), the extra condition is g^2<=O(d). It holds at the proposed epsilon near one, since 2(1-epsilon)<epsilon.

The hole system has only theta times the rows. The favorable complementary Gaussian width is O(sqrt(p theta/a)); even a classical banded application has regular cost O(V d theta*(p theta/a)), which at theta≈1/d is O(V p/(a d)). This is far below the proposed main exponent. This cost statement still requires the symbolic-normalization adapters to preserve that sparsity.

## Precisely unproved steps

1. Complete normalized holes factorization into a fixed number of grouped convolutions and a genuinely hole-supported correction, with O(p) records after all diagonal cancellations. The weighted full-geometric component is proved in the companion note; the Toeplitz/complement adapters are not.
2. Implement g-axis near-one halos/gathers in the proposed group cost, instead of silently using g full scans. A dyadic boundary-subset decomposition has total volume `(N+O(L))^g=O(N^g)`, but this does not itself prove fast movement of the nonlinear boundary signature. Padding all axes to 2N would be invalid.

The unchanged paid resampler retains Vd work and rejects this target. These are explicit positive next lemmas, not conditions erased from a certificate.
