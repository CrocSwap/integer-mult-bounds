# All-order three-axis margins in three narrow source intervals

## Status and source scope

This is a new scoped theorem candidate, with complete finite algebra and
a separate mixed-coefficient reconstruction. It covers all 40,320 orders
of three actual extremal physical source factors under narrower prime
intervals and a stronger size guard. It does not claim the result for
every separated-prime triple from the preceding two-order theorem.
Both completed repository packages remain unchanged.

Canonical source base: `e54523517d0f03e58352e647c403a5af3e525a57`.
The literal selector, phase/chirp-preserving factor formula and aliases
are from #7599 at `702c7616667c5f4e583eb73687944d148b7a1ccf`.
Fine-prime padding and integer alpha are the canonical
`research/native-kappa-30201655/modern-sources/FINE-PRIME-PADDING.md`.

## 1. Uniform common-lower-entry theorem

Let `eta=(33,47,62)/64`. Suppose

```
0 < h <= 2^-30,
0 < w <= 2^-42 h^4,
0 <= c_l <= 1,
max_l |c_l-eta_(pi(l))| <= 2^-24
```

for some permutation `pi` of the three centers. Set

```
U_l=1-h c_l,
B_l=[[1,U_l],[w,1]],
B=B_0 tensor B_1 tensor B_2,
E(A)=A-Z A Z^T,
D=2^-18 w^4.
```

Vertices have index `4x_0+2x_1+x_2`. For every simultaneous
vertex order `o`,

```
|det E(B[o,o])| >= D,
sigma_min(E(B[o,o])) >= 2^-21 D,
sigma_min(E(B^(-1)[o,o])) >= 2^-49 D.                 (1)
```

Any tensor of factors whose entries differ from the corresponding
`B_l` entries by at most `2^-71 D` is invertible, and all orders
retain forward and exact-inverse displacement margins `2^-22 D`
and `2^-50 D`.

## 2. Complete lower-degree certificate

Write the formal common-lower tensor as

```
H=[[1,u],[w,1]] tensor [[1,x],[w,1]] tensor [[1,r],[w,1]].
F_o=det E(H[o,o])=sum_j w^j Q_(o,j)(u,x,r).
```

The only order symmetries used are permutation of the three bit axes
and complementation of all bits. Axis permutations relabel `u,x,r`.
Full complementation transforms `H` to `H^T`, and
`E(A^T)=E(A)^T`, preserving the determinant. Their 12-element
action on complete vertex orders is free: an element fixing an order
fixes every vertex, hence is the identity. Consequently there are
exactly 3,360 classes of 12 orders. Partial bit complementation and
order reversal are not invoked as forward-determinant symmetries.

For each class representative, let `d` be its first nonzero
coefficient in `w`, and let `K` be the first total degree in
`delta_0,delta_1,delta_2` of
`Q_(o,d)(1-delta_0,1-delta_1,1-delta_2)`.
The complete exact classification is:

| d | K | Classes |
| ---: | ---: | ---: |
| 0 | 0 | 1277 |
| 0 | 1 | 575 |
| 0 | 2 | 80 |
| 0 | 3 | 12 |
| 1 | 0 | 775 |
| 1 | 1 | 337 |
| 1 | 2 | 84 |
| 1 | 3 | 14 |
| 1 | 4 | 1 |
| 2 | 0 | 124 |
| 2 | 1 | 55 |
| 2 | 2 | 3 |
| 2 | 3 | 4 |
| 3 | 0 | 5 |
| 4 | 0 | 14 |

`classify_leading.py` constructs every representative and expands
only successive truncations through `w^4`. It uses exact integer
sparse polynomial arithmetic with three upper-entry variables.
A truncation preserves every coefficient it contains; the first
nonempty truncation proves that all lower coefficients vanish
identically. This is not interpolation from numerical values.
Packed four-bit digits record upper-entry exponents, each at most
eight in a determinant product, so no exponent addition carries.
Then exact binomial substitution computes each leading homogeneous
Taylor polynomial `T_o(c)` in

```
Q_(o,d)(1-h c_0,1-h c_1,1-h c_2)
    = h^K T_o(c) + higher powers of h.
```

The certificate verifies these uniform bounds over all 3,360 classes:

```
min_(o,pi) |T_o(eta_(pi(0)),eta_(pi(1)),eta_(pi(2)))|
    = 7/131072;
max_o K sum_e |coefficient_e(T_o)| = 156;
max_o sum_e |coefficient_e(Q_(o,d))| 2^(e_0+e_1+e_2)
    = 6656 < 2^13.                                   (2)
```

There are 2,677 distinct leading polynomials before identifying
further coefficient symmetries. The full ordered certificate hash is
`fa160c08f3d96fdb8fc91484a71bcea6d26419ffb9b1430ce7e1ee178784b730`.

The separate `check_mixed_columns.py` imports no primary code. It
constructs the literal tensor after `U_l=1-c_l h`, then extracts
the mixed coefficient `[w^d h^K]` by column multilinearity and
fraction-free scalar determinants. All 20,160 class/center-permutation
checks agree with the symbolic values, using integer center numerators
and the normalization `64^K`. They use 547,158 scalar
determinants. Its ordered value hash is
`2e8b2bd99de3def044bac976a7b1be46b1c6845b87af20948d44f5a23902e141`.
This independently checks the nonzero leading values. The symbolic
lower-degree vanishing and mass bounds in (2) remain the primary
certificate's separate, explicitly inspectable obligations.

## 3. Uniform remainder and determinant bounds

On `[0,1]^3`, the sum of absolute first derivatives of each `T_o`
is at most 156, by the second bound in (2). Therefore, throughout
the specified center boxes,

```
|T_o(c)| >= 7/131072 - 156*2^-24
         = 740*2^-24 > 2^-15.                         (3)
```

The third bound in (2) bounds the absolute coefficient mass after
substituting `U_l=1-delta_l`, since a monomial of total degree `m`
has binomial coefficient mass `2^m`. As `h<=1` and `0<=c_l<=1`,
the higher Taylor terms have magnitude at most
`6656 h^(K+1) < 2^13 h^(K+1) <= 2^-17 h^K`.
Thus

```
|Q_(o,d)(1-hc)| >= 2^-16 h^K.                         (4)
```

Each tensor entry is a monomial. Each displacement entry has at most
two monomials. The entire determinant therefore has absolute
coefficient mass at most `8!*2^8 < 2^24`, before or after collection.
For upper entries and `w` in `[0,1]`, the sum of terms of lower-entry
degree greater than `d` is at most

```
2^24 w^(d+1) <= 2^-18 w^d h^4
             <= 2^-18 w^d h^K.                      (5)
```

Equations (4) and (5) give
`|F_o| >= 2^-18 w^d h^K`. The table has `d<=4`, `K<=4`,
and `K=0` when `d=4`. If `d<=3`, then
`h^K>=h^4>=w`, so `w^d h^K>=w^(d+1)>=w^4`.
For `d=4`, the same bound is immediate. This proves
`|F_o|>=2^-18 w^4=D` for all orders.

The reasoning proves a continuous parameter-box statement. Finite
center checks supply exact nonzero coefficients and bounds, while
(3)-(5) pay the complete continuous variations and remainders.

## 4. Actual extremal source family

Let integer `p>=2^20` and let `t` be a dyadic integer satisfying
`t>=p^72`. Let distinct odd primes `s_l` satisfy, for some
permutation `pi`,

```
gamma_l = 2p^2(t/s_l-1),
|gamma_l-eta_(pi(l))| <= 2^-26.                       (6)
```

These are narrower, explicitly stated source intervals. Put

```
L=ln(16p), alpha=ceil(sqrt(4L/pi)), a=pi alpha^2,
w=exp(-2a), h=a/p^2.
```

As in #7599, `4L<=a<=9L`. For `p>=2^20`, also
`L<=p/9216`: the difference `p/9216-ln(16p)` is increasing
and at `2^20` exceeds `2^20/9216-24>0`.
Thus `a<=p/1024`, `h<=2^-30`, and `a>32`.
Since `w<=(16p)^-8`,

```
w/h^4 <= 2^-32/a^4 <= 2^-42.                         (7)
```

The source intervals imply the original fine-prime guards. Indeed
`1/2+1/128 < gamma_l < 1-1/64`, while

```
1-s_l/t = gamma_l/(2p^2+gamma_l).
```

For `p>=2^20`, this lies in `[1/(4p^2),1/(2p^2))`.
Also `s_l>t/2>=p^4`. The three center gaps exceed `1/8`
after their error allowances, and the two source ratios have product
less than two, giving `|s_l-s_m|>t/(32p^2)`.

Choose the exact extremal same-cell index from #7599. Its literal
phase/chirp-retaining factor is

```
C_l=[[1,U_l],[V_l,1]],
U_l=exp(-a(2(t-s_l)+1)/s_l),
V_l=exp(-a(2s_l-1)/s_l)=w exp(a/s_l).
```

Write `chi_l=gamma_l+p^2/s_l` and
`c_l=(1-exp(-h chi_l))/h`, so `U_l=1-hc_l` exactly.
Here `0<chi_l<1`. The elementary estimate
`0<=chi_l-c_l<=h chi_l^2/2` yields

```
|c_l-eta_(pi(l))|
 <= 2^-26 + 2p^2/t + h/2
 <= 2^-26 + 2p^-70 + 2^-31 < 2^-24.                 (8)
```

Consequently the common-lower tensor `B_l=[[1,U_l],[w,1]]`
satisfies the all-order theorem. Actual physical lower entries have
not been identified with `w`: their difference is explicitly charged.
Since `a/s_l<1/2`,

```
0 < V_l-w <= 2aw/s_l <= 4aw/t.                       (9)
```

Use `w>=(16p)^-18` and `a<=p/1024`. Relative to the
factor allowance `2^-73D`, the last quantity is at most

```
(4aw/t)/(2^-73D)
 = 2^93 a/(t w^3)
 <= 2^309 a p^54/t
 <= 2^299 p^55/t
 <= 2^299 p^-17 <= 2^-41 < 1.                        (10)
```

Thus actual physical lower-entry differences cost at most `2^-73D`
per factor entry. The hypothesis `t>=p^72` is explicit and essential
to this particular conservative comparison argument.

## 5. Inverse, aliases and precision

Every entry of the common-lower tensor is at most one, so its
displacement norm is at most eight. Each factor inverse has norm
at most four, so `||B^-1||<=64`, `||E(B^-1)||<=128`, and
`0<det B<=1`. The Schur/reversal identity

```
det E(A^-1) = det E_rev(A)/(det A)^2,
E_rev(A)=J E(JAJ) J
```

and all-order coverage give the inverse determinant bound. Dividing
the determinant by the seventh power of the respective norm proves
the singular-value bounds (1).

For an eight-by-eight entry perturbation bounded by `epsilon`,
matrix and displacement norms are bounded by `8epsilon` and
`16epsilon`. If `epsilon<=2^-68D`, Neumann inversion gives
invertibility and inverse displacement change at most
`2^17epsilon<=2^-51D`. These estimates retain the forward and
inverse margins `2^-22D` and `2^-50D`.
Factor entry error `zeta<=2^-71D` produces tensor entry error
`<=7zeta<2^-68D` and therefore suffices.

The matched periodization of the literal source factor has alias
error at most `4 exp(-a t^2/8)` by the pinned #7599 argument.
For `a>=1,t>=32`,

```
4 exp(-a t^2/8) <= 2^-73D,
```

because the required inequality is
`a(t^2/8-8)>=93 ln2`, and `t^2/8-8>=120>93 ln2`.
Combining (10), aliases and a further periodic-table error
`<=2^-73D` costs at most `3*2^-73D<2^-71D`.
Thus all 40,320 orders of that rounded tensor and of its exact
inverse retain the stated margins.

Since `a<=9ln(16p)`,

```
D=2^-18 exp(-8a) >= 2^-18(16p)^-72
                 = 2^-306 p^-72.
```

A sufficient further periodic-factor accuracy is therefore

```
b >= ceil(379+72 log2 p).                             (11)
```

At `p=2^20`, the right side is 1819. The difference
`p-379-72log2p` increases thereafter because its derivative
exceeds `1-144/p>0`. Thus `p` fractional accuracy bits suffice;
any fixed positive `Cp` bits suffice eventually.

The inverse is the exact inverse of the selected tensor of rounded
factors. Additional tensor/inverse arithmetic requires its own paid
error budget. No principal section of a full source inverse is
identified with this inverse, and no coefficient producer is admitted.

## 6. Actual prime witnesses and eventual availability

`source-fixture.json` contains three exact Proth certificates with
`p=2^20`, `t=2^1440=p^72`, `s_l=k_l*2^720+1`,
odd `k_l<2^720`, and witness 3 satisfying
`3^((s_l-1)/2)=-1 mod s_l`. Every prime divisor of such an
`s_l` is `1 mod 2^720` and exceeds `sqrt(s_l)`, proving
primality. `find_source_fixture.py` found the witnesses after
178,133,2 increments in the three respective narrow intervals.
The certificate verification does not require replaying the search.
These fixtures certify the local source guards, not a complete
outer production instance.

For eventual existence, the source interval for center `eta_j` is

```
J_j=( t/(1+(eta_j+2^-26)/(2p^2)),
      t/(1+(eta_j-2^-26)/(2p^2)) ].
```

Its length is at least `t/(2^27p^2)`, and its endpoints lie
in `[t/2,t]`. Trudgian's theorem 2,
[arXiv:1401.2689v2](https://arxiv.org/html/1401.2689v2#S2),
has the exact estimate

```
|pi(x)-li(x)| <= .2795 x (ln x)^(-3/4)
                     exp(-sqrt(ln x/6.455)),  x>=229.
```

For `ell=ln t` and `t>=458`, the two endpoint errors sum to
at most `2t ell^(-3/4) exp(-sqrt(ell/12.91))`.
Their ratio to the logarithmic-integral main term is at most

```
2^28 p^2 ell^(1/4) exp(-sqrt(ell/12.91)) -> 0
```

at the retained scale `ell=Theta(p^(1-epsilon))`, fixed
`0<epsilon<1`. Each interval therefore eventually contains a prime;
`t>=p^72` also eventually holds at that scale. The threshold may
depend on the exponent and scale constants. No availability for
every finite `p>=2^20` or practical asymptotic threshold is claimed.

Trial division scanning remains `O(t^(3/2) poly(log t))` bit work
with logarithmic local arithmetic scratch and charged outputs.
Its logarithm is `o(p)` at the retained scale. This does not pay
the coefficient producer or complete outer caller.

## 7. A precise obstruction to dropping the new interval guard

The unique class `(d,K)=(1,4)` has representative
`o=(1,2,4,0,7,6,5,3)` and exact first `w` coefficient

```
Q_(o,1)=-(r-u)^3 (x^2-ru) (x-r-u).
T_o(c)=(c_0-c_2)^3 (c_0-2c_1+c_2).                  (12)
```

Pairwise distinct, well-separated center values can make this
leading Taylor polynomial zero; equally spaced centers do so.
Thus the earlier two-order argument based solely on pairwise source
gaps does not automatically prove this all-order leading certificate.
This is an obstruction to that proof method, not a physical
source counterexample. Higher Taylor terms, higher powers of `w`
and the actual `V_l-w` terms can change the conclusion.

A second explicit center failure is `T=-c_0+5c_1-6c_2`
for order `(1,3,5,2,7,0,6,4)`, which vanishes at
`(c_0,c_1,c_2)=(37,59,43)/64`. The chosen centers
`(33,47,62)/64` avoid every leading zero in the complete certificate.

## Limitations and credit

Only three axes and eight vertices are covered. The source intervals
are much narrower than the original fine-prime interval, and the
`p>=2^20,t>=p^72` restrictions are explicit. Arbitrary separated
source triples, close primes, differing targets, growing dimension,
producer admission and complete analytic recovery remain open.
All five selected assumptions and conditional kappa remain unchanged.

Credit #7599/#7598/#7600, the two local companion packages,
Chafik Boukhalfa, Vlado Vojdanovski, IdeaOuter, Jeremy Kothe,
Tim Trudgian and the retained bilateral/framework lineage.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI
assistance. The separate arithmetic paths were written by the same
AI worker; no human or formal-kernel acceptance is claimed.
Apache-2.0.
