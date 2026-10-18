# A common dual for mixed provider inventories

## 1. Object and catalogue

Fix the data word of PR942. Each replica has nine calls, 896 live families,
and the following idle bins:

| Capacity | Bins per replica | Signed bonus |
| ---: | ---: | ---: |
| 8 | 672 | 2 |
| 16 | 448 | 4 |
| 32 | 448 | 8 |
| 48 | 448 | -13 |

The total capacity is 48,384 per replica. A call can select any cost interface
in [CATALOGUE.json](CATALOGUE.json). This is the complete set of providers in
the 35 files that match `research/*/data/SPEC*.json` at commit
`8bddbee377e2f3ce1f1247196c4b290d55767d20`. The 71 source records give 25
distinct pairs `(inventory, expected_profile)`. A fresh source read checks
every record. A separate Git-tree pass checks complete source coverage.

For provider P, write `a_P,w` for its number of width-w helpers and `h_P,r`
for its number of paid rank-r local children. All widths belong to
`W = {4,5,7,8,9}`. Every provider has the same mass contract:

$$
\sum_r r h_{P,r}-M_P=1856,\qquad M_P=\sum_w w a_{P,w}.
$$

Let `T > 0`, `x_P >= 0`, and `sum_P x_P = 9T`. Actual call counts are
integers. The relaxation also permits real counts. The pool has `T` times
the capacity inventory above. Every helper stays whole inside a bin. All
time, replica, and matching restrictions are removed. Let `y_c,n` be the
nonnegative number of bins of capacity c that use helper count vector n.
Then

$$
\sum_n y_{c,n}=N_cT,\qquad
\sum_{c,n}n_w y_{c,n}=\sum_P x_Pa_{P,w},\qquad
\sum_w wn_w\le c.
$$

These equations define the complete packing relaxation. They do not assert
that any new mixture has a physical realization. Allowing all catalogue
providers at all calls can only enlarge the set being bounded.

The U8 interface, denoted U, has

```text
h_U = {1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}
a_U = {4:80, 5:32, 7:54, 8:122, 9:216}
M_U = 3778.
```

## 2. Common bin support

For `0 < b <= 1/500`, set

$$
\phi_b(r)=r(73/r)^b\quad(r>0),\qquad \phi_b(0)=0.
$$

Use the signed width prices from PR795 and PR942:

$$
(p_4,p_5,p_7,p_8,p_9)=(-1,-20,-8,-2,4).
$$

For a bin with capacity c and count vector n, put
`r = c - sum_w w*n_w` and `q = bonus_c + sum_w p_w*n_w`. Define

$$
\lambda_b=\frac{48\phi_b(1)-\phi_b(48)}{925},\qquad
A_b=\frac{13\phi_b(1)+19\phi_b(48)}{925}.
$$

The common bin support is

$$
\phi_b(r)\ge A_br+\lambda_bq.\tag{1}
$$

The multiplier is positive for `b > 0`. The complete Cartesian enumeration
contains 1,163 legal bin vectors. A separate recurrence maximizes signed
price at each exact filled width:

$$
D(0)=0,\qquad D(s)=\max_{w\le s}\{D(s-w)+p_w\},
$$

with unattainable states omitted. It gives the same 92 capacity/remainder
maxima. Since `lambda_b > 0`, checking the maximum price also checks all
lower prices. The only identically zero forms in (1) have residual ranks
0, 1, and 48. All other forms are strictly positive in the stated interval.

This support inequality is inherited work. PR942 proves it at the required
endpoint. PR995, PR1000 and PR1010 give uniform or sharp bounds for the fixed
U8 problem. The new result below is its application to all changes in the
catalogue inventory, with an exact positive penalty for each interface.

## 3. The mixed term

Define the local moment and signed helper price by

$$
\Phi_P(b)=\sum_rh_{P,r}\phi_b(r),\qquad
P_P=\sum_wp_wa_{P,w}.
$$

Sum (1) over the shared pool. Every width and signed price is counted once:

$$
I_b\ge A_b\left(48384T-\sum_Px_PM_P\right)
 +\lambda_b\left(BT+\sum_Px_PP_P\right),
\quad B=\sum_cN_c\operatorname{bonus}_c=896.
\tag{2}
$$

If a residual r is split into positive parts, its total moment is at least
`phi_b(r)`. This follows from `0 < 1-b < 1` and
`sum_j r_j^(1-b) >= (sum_j r_j)^(1-b)`. Thus (2) also holds with fragmented
idle remainders.

For each provider, define its reduced cost relative to U8:

$$
\Delta_P(b)=\Phi_P(b)-\Phi_U(b)
 -A_b(M_P-M_U)+\lambda_b(P_P-P_U).\tag{3}
$$

The terms after the local profile difference are essential. A provider can
use more total width or change the signed credit of the shared pool. A bound
on a separately packed instance does not fix either effect in a mixture.
For example, P01 has width 3,944 and signed price 14, while P02 has width
3,984 and signed price -746. Relative to U8, their signed-price changes
have opposite signs. The shared pool must account for both effects at once.

The U8 signed price is `P_U = -532`. Thus the all-U8 pool has residual mass
14,382 per replica and signed price -3,892 per replica. Direct substitution
in (2) gives

$$
A_b\,14382+\lambda_b(-3892)
 =\frac6{37}\phi_b(1)+\frac{11086}{37}\phi_b(48).
$$

Add the paid local profiles. For every point in the mixed packing relaxation,

$$
\sum_Px_P\Phi_P(b)+I_b
\ge T\left(9\Phi_U(b)+\frac6{37}\phi_b(1)
                  +\frac{11086}{37}\phi_b(48)\right)
       +\sum_Px_P\Delta_P(b).\tag{4}
$$

This is the common dual for the mixture. It treats the shared residual pool
directly. It does not take a convex combination of separate owner bounds.

## 4. Exact provider separation

Each reduced cost is zero at `b = 0`, by the common mass contract. The
checkers prove, throughout `0 <= b <= 1/500`,

$$
\Delta'_P(b)>19/10\quad(P\ne U),\qquad
\Delta'_P(b)>336\quad(a_P\ne a_U).
$$

Integration gives `Delta_P(b) > 1.9*b` for all 24 alternatives, and
`Delta_P(b) > 336*b` for all 22 interfaces with a changed inventory.
The U8 reduced cost is identically zero.

These signs use exact rational bounds. If
`l_r <= log(73/r) <= u_r`, then for `0 <= b <= B_0 = 1/500`,

$$
r l_r\le\phi'_b(r)\le r u_r\exp(B_0u_r).
$$

Apply these bounds to each rational linear form, reversing endpoints for
negative coefficients. The two retained engines use different logarithm
series and exponential bounds. Decimal values are only for display. The
same derivative method also checks (1), whose forms vanish at zero.

The separate checker multiplies (1) and (3) by 925. For a bin it checks

$$
925\phi_b(r)-(13r+48q)\phi_b(1)-(19r-q)\phi_b(48)\ge0.
$$

For a provider, with `dM = M_P-M_U` and `dP = P_P-P_U`, it checks

$$
925(\Phi_P-\Phi_U)+(48dP-13dM)\phi_b(1)
 -(dP+19dM)\phi_b(48)>0.
$$

It reads the 71 source records again and does not import the primary checker.
It shares only the retained arithmetic engine and pinned input data.

The table shows all interfaces. Each source is under `research/` and ends
in `/data/SPEC.json`. Alias counts sum to 71. The last column is a rounded
down strict lower bound on (3) throughout the root interval in section 5.
Full rational bounds, profiles, and all aliases are in the JSON files.

| ID | Representative source / provider | Records | Reduced cost > |
| --- | --- | ---: | ---: |
| P01 | complex-571-cold14 / atm3 | 5 | 0.89913 |
| P02 | complex-571-cold14 / ck | 5 | 0.86391 |
| P03 | complex-571-cold14 / jp8 | 7 | 0.79130 |
| P04 | complex-571-cold14-b3 / atm3 | 1 | 0.67358 |
| P05 | complex-571-cold14-b3 / jp8 | 1 | 0.56576 |
| P06 | complex-571-cold14-e1 / atm3 | 2 | 0.89163 |
| P07 | complex-571-cold14-e1 / jp8 | 2 | 0.78380 |
| P08 | complex-571-cold14-k492 / ck | 5 | 0.64162 |
| P09 | complex-571-cold14-k492 / jp8 | 5 | 0.56900 |
| P10 | complex-571-free4f / atm3 | 1 | 1.23326 |
| P11 | complex-571-free4f / ck | 1 | 1.19805 |
| P12 | complex-571-free4f / jp8 | 4 | 1.10685 |
| P13 | complex-571-free4fc / atm3 | 2 | 1.21932 |
| P14 | complex-571-free4fc / ck | 2 | 1.18411 |
| P15 | complex-571-free4fc8 / atm3 | 1 | 1.21467 |
| P16 | complex-571-free4fc8 / ck | 1 | 1.17946 |
| P17 | complex-571-hpe46 / atm3 | 3 | 1.05384 |
| P18 | complex-571-hpe46 / ck | 3 | 1.01863 |
| P19 | complex-571-hpem46 / jp8 | 2 | 0.94601 |
| P20 | complex-571-hpeq1 / atm3 | 4 | 1.07228 |
| P21 | complex-571-hpeq1 / ck | 4 | 1.03707 |
| P22 | complex-571-hpeq1 / jp8 | 1 | 0.96445 |
| P23 | complex-double-replica-owners / gauge44 (X4) | 2 | 0.00675 |
| P24 | complex-sw4-frame8 / gauge44 (SW4) | 3 | 0.01604 |
| P25 | complex-t21-owners / gauge44 (U8) | 4 | exactly 0 |

## 5. Root and outer consequences

Normalize (4) by `73*896*T`. The first term is exactly the U8/T37 moment.
Its integral profile is

```text
{1:848490, 2:112554, 3:148518, 4:53946, 5:23976, 8:2664, 48:11086}
live = 33152; deficit = 11840.
```

Both interval engines put its unique root `b_U` strictly between

```text
0.001664727258740678855772
0.001664727258740678855773.
```

For every mixture, the rank mass at zero is `73*896*T - 320*T`.
All children are proper, so its moment is strictly increasing in b.
Equation (4) and the positive penalties imply that its root is at most
`b_U`. Any positive use of an alternative interface makes the root strictly
smaller. This establishes an optimum of the full mixed relaxation, not just
an exclusion of one decimal endpoint. PR942 supplies the existing T37 owner
witness that attains the reference profile. This package does not replay it.

At the full root interval, a direct interval calculation gives the stronger
per-call floors `27/4000` for all alternatives and `113/200` for a changed
inventory. Thus (4) gives an explicit loss for each alternative call.

The PR589 bit lower endpoint, with its bad-residue surcharge, is
`0.001733427039589844234749`. It is above the complex interval. The retained
seven-step outer map is increasing here: each step is
`a_next = s*(1-s+a_old)`, and both partial derivatives are positive for
`0 < s < 0.002` and `a_old >= 0`. Its final rational map is also increasing.
Both complex endpoints give the same `1e-18` grid value,
`0.001661960547713947`. All 47 strict constraints and the retained next-grid
rejection pass. This ceiling uses that outer recipe. Its numerical driver
does not provide a finite physical invoice for a new construction.

## 6. Scope beyond the catalogue

A new provider can have negative reduced cost. This is the condition that
the old dual cannot exclude; it is not a construction certificate.
The controls give three concrete examples. The PR987 U10 profile changes
the U8 profile by `4*H3 - 8*H4 + 4*H5` at the same inventory. Strict concavity
makes this local cost change negative for `0 < b < 1`.

The R489 and R480 profiles in PR1004/1005 change the helper inventory. At
PR1005 head `779e80aef469bc3a28b19f1adde199871a9a22e3`, the exact source files
are `research/gauge44-leaver/data/SPEC.json` and
`research/gauge44-leaver8/data/SPEC.json`. Their SHA256 values are retained
in the controls. The respective reduced costs at the U8 root are between
`-0.158392` and `-0.158391`, and between `-0.253089` and `-0.253088`.
They are outside this theorem. The source hashes match their manifests;
their native programs and owner admissions were not replayed here.

There is a useful conditional extension for a same-inventory improvement.
If a new provider N has `a_N = a_U` and `Phi_N(b) <= Phi_U(b)`, then each old
provider has reduced cost relative to N equal to
`Delta_P(b) + Phi_U(b) - Phi_N(b) >= 0`. Thus mixing old providers cannot
beat the corresponding all-N reference on the interval where that local
comparison holds. This observation does not admit N or new owners.

New data capacities, helper migration across data boundaries, split helpers,
changed local paid contracts, restoration deferral, or a new outer recipe
require a different claim. In particular, PR1012's deferral model is not a
call contract in this catalogue. All inherited physical and asymptotic
assumptions remain. No unconditional multiplication theorem follows here.
