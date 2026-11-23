# Apply spectral downset bounds to the unchanged direct-circulant word

Author-stage derivation, awaiting independent review. The exact source pins,
scope, decisive obligations and complete optimistic budget are in TARGET.md.
The first-wave source-cut audit is a dependency, not part of this review.

## 1. Prospective theorem

Under the same source phase/rank, exact represented-input native H, Fourier
and recovery contracts as #8093, let d>=1 axes have widths ell_i>=1, true
orders 2<=r_i<=t_i=2^ell_i, public precision p>=1 and L=sum ell_i. Put

```
E = ceil(257*L/2)+1354*d
A = 20*L+303*d
J = 20000*(d+1)*(max ell_i+2)^6
C = 4*J*(d+1)^2+d+1
P = 4*p+A+2*E+bit_length(C).
```

Use Grid(P) and the unchanged producer target P+8. The same complete padded
input half-disk contract then gives raw coordinate error strictly below
2^(-4p). The inherited public-grid recovery theorem consequently retains its
144/B_radix^2<1/2 error bound for B_radix>=32 under the separate scale, true
volume, no-wrap and CRT-character premises.

The linear term is 4p+277L+3011d+(L mod 2). It saves exactly 1084L+1735d
fractional bits against #8093 at fixed p and widths. This is a sufficient
selector comparison, not measured speed, space, optimal precision or kappa.

## 2. Use smaller spectral constants only in the proof

For every P>=1, the parent's root synthesis and accretivity argument gives
the actual stored padded root T the spectral estimates

```
||T|| < 2,
||T_b^-1|| <= 4*r <= 4*t   for every leading section.
```

Take Lambda=2, Q=4t and chi=8t as mathematical estimates. The executable
component envelopes remain lambda_c=max(1,norm_upper(T)) and Q_c=8tr. No
smaller spectral number is passed to the stronger component-guarded factory.

Nick Petalas's #4852 theorem applies to every matrix with invertible leading
sections and every contiguous-interval elimination tree, including the
source's non-Toeplitz identity-padded root. Thus each ideal completed downset
and its inverse have cap 2*sqrt(t)*chi^2<=Bnew=2^7*t^3. The theorem bounds
finished forward block rows by Lambda+Lambda^2 Q and untouched rows by
sqrt(1+chi^2); finished inverse block columns are original leading-inverse
restrictions with bound Q, while untouched columns have the block-solve bound
sqrt(1+chi^2). Summing squared block bounds gives the result. The full
credited proof is retained unchanged; this result does not claim that theorem
or Brian's subsequent #4977 allocation adapter as new.

The old allocation uses
Bold=256*t^3*(lambda_c*Q_c)^12>=256*t^3>Bnew. Its actual atomic error eta
therefore obeys

```
theta_new=(3t-2)*Bnew^2*eta <= theta_old <= 1/4.
```

For each fixed external P, this reanalyses the exact word produced by the
original allocation at that same P. No child target, grid or coefficient is
changed relative to that source call. Choosing the new external selector
does change P, and therefore regenerates the word through the unchanged
factory's precision rules; identical coefficient bytes across two different
external selectors are not claimed. The forward endpoint synthesis error is
still the parent's original source-allocation theorem at P+8, not an endpoint
estimate obtained by passing smaller spectral numbers to component guards.

## 3. Bound the actual prepared children

For each source full split the original-leading-solve identities imply
||K||,||L||<=chi=8t. The displacement E=X-ZXZ^T has norm at most 2chi.
For a child of side m<=t, the exact component row/column envelope returned by
generator.prepare is therefore

```
be <= sqrt(2m)*||E|| <= 2*sqrt(2m)*chi <= 4t*chi.
```

The source forwards this actual be and actual rank to generator.allocation;
it does not substitute the full compiler's larger global envelope. Retaining
rank<=2ell+8<=5t, the literal child formulas give

```
alpha=2*rank*m*be <= 320t^4
KG=2m+16m*be <= 514t^3.
```

By the first-wave source-cut proof, the actual child four-way fragment cap at
arbitrary matching subsets is
max(3200m^3,2+2KG)*(10+4alpha+2KG). Hence

```
max(3200t^3,2+1028t^3) <= 3200t^3,
10+1280t^4+1028t^3 <= 2318t^4,
Hgen <= 7,417,600t^7 < 2^23*t^7.
```

Ideal scalar pivots have modulus between 1/Q and
U=Lambda+Lambda^2 Q=2+16t<=18t. The unchanged eta satisfies
eta<=1/(2Q_c)<=1/(2Q), since r>=2. Stored scalar and stored inverse fragments
have bounds U+1 and 2Q, both below Hnew=2^23*t^7. Thus Hnew bounds every
actual local fragment and inverse. The old full-level component guards and
their larger recorded fragment bound remain unchanged.

## 4. All lowering, routing and tensor factors

Use L0=max(1,Lambda,Q)=4t. The four-way cut and relative-interval lemmas give

```
K=2*L0*Bnew*Hnew <= 2^33*t^11,
G=2*Bnew^2*Hnew^2 <= 2^61*t^20.
```

K bounds prefixes/suffixes and their inverses; G bounds arbitrary intervals
and inverses, including each original source gate. These are exact stored
operators before data rounding.

The parent's pivoted sixteen-H proof supplies at most forty ordinary factors
of norm and inverse norm <=64, and exactly one pivot factor bounded both ways
by 2G. A routed partial switch contributes four; each matching is a direct
sum. Every routed root prefix and inverse prefix consequently have cap

```
4*K*64^40*(2G) <= 2^337*t^31.
```

The two root passes and two external diagonals, each bounded both ways by
2t, give the one-axis cap 2^676*t^64. The retained partial tensor-H allowance
is 2^d at each interval end. Tensoring axes therefore gives spectral interval
cap 2^(1354d+128L); converting to infinity norm costs sqrt(2^L), proving
the stated 2^E envelope. One joined diagonal scalar has modulus at most
64^40*(2G)<=2^302*t^20, including the exterior and routing cases.

## 5. Close the complete local numerical budget

Retain the parent's proved odometer invariant: each stored suffix is the
rounded product of its current factors, using at most d-1 multiplications.
It does not accumulate one error per earlier scan record. The new scalar
bound gives local defect epsilon*(1+||z||_infinity), where

```
epsilon=(d+1)^2*2^(-P+A),   A=20L+303d.
```

The stage count J and exact-native-H premise are unchanged. Root-column
synthesis and exact endpoint bias also remain unchanged; their tensor bias
is bounded by beta=(d+1)*2^(-P+E), since
2^E>=2^(d-1)*sqrt(2^L). With prefix and interval caps R=M=2^E, the same
bootstrap gives

```
raw error <= J*M*epsilon*(2+2R)+beta
          <= C*2^(-P+A+2E).
```

For the proposed P this is strictly below 2^(-4p), as C<2^bit_length(C).
The bootstrap spend is strictly below 2^(-4p-E)/4<=1/4, so the computed-state
bound closes without circularity. Both signs use these absolute bounds.

No helper operation, native private arithmetic, physical setup, copying or
restoration is repriced. The statement is the complete local numerical
budget under its named interfaces, not the complete multiplication recurrence.

## Verification boundary and remaining questions

Check every exact exponent and positive polynomial comparison, the unchanged
Full/generator allocations and their actual argument forwarding. Include
bounded padded root words with r<t and independent spectral admission checks.
Controls must expose whole-matrix-only inverse information and conflation of
component admission with spectral bounds. These finite checks do not replace
the source bridge or the credited all-size block-solve proof.

The intended contribution retains every predecessor's license/credit,
particularly Jose Manuel, Vlado Vojdanovski, Chafik Boukhalfa, Ali Romman,
Nick Petalas #4852 and Brian/JoyboyBrian #4755/#4976/#4977. Prepared for Jerry
Chen/@CubeJerry with substantial OpenAI assistance. Separate review remains
required; all five selected assumptions and kappa remain unchanged.
