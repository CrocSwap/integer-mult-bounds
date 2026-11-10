# Actual Full words as one synchronous global tensor program

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a new globally rounded execution of authenticated source programs.
It does not tensor nonlinear local rounded trajectories. The physical service
join is a separate explicit interface; no selected-rate claim is made.

## 1. Exact source and quantified reference

Fix K=2^ell complete coarse labels, g>=1 axes, and common side N=2^m>=2.
The complete field has T=K*N^g records and n=ell+gm binary address bits.
Axis zero is fastest. No coarse label or unused coordinate is discarded.

For every label c and axis a, give a rational Toeplitz matrix admitted by the
retained #4205/#4253 `FullRoot`, a complete wire permutation and a forward or
stored-inverse direction. The source leading-section, rational-phase and
complete-prefix theorems are inherited with their original scope. Let L_ca
be the requested exact matrix or inverse in physical wire order. The actual
stored plan has a linear endpoint U_ca and proves

```
||L_ca||_2 <= lambda_ca,    ||U_ca-L_ca||_2 <= e_ca,
||U_ca||_2 <= E_ca := lambda_ca+e_ca.
```

Here lambda_ca is the admitted norm bound for the chosen direction and is at
least one. Inverse plans reverse the stored gates and use their exact
reciprocals. An inverse is not an adjoint or a rounded round trip. Original
root, plan and reference-page seals remain checked.

The requested global map is the direct sum over c of tensor products of
L_ca. Its prepared reference is the direct sum of tensor products of U_ca.
These act on arbitrary complete vectors, including vectors correlated across
axes or labels; no product-state assumption is used.
Precisely, address `(c,i_0,...,i_(g-1))` means
`c N^g + sum_a i_a N^a`, and the c-block entry from digits j to digits i is
`product_a L_ca[i_a,j_a]`. In the usual most-significant-first Kronecker
matrix convention this is `L_c,g-1 tensor ... tensor L_c,0`; the same order
applies to U. Thus the fastest-axis convention is explicit in the target,
the source gates and the physical coefficient-page order.

For input Euclidean radius R=2^r>=1 and target tau=2^-t, telescoping gives

```
epsilon_source = R max_c sum_a e_ca
                   product_(b<a) E_cb product_(b>a) lambda_cb.       (1)
```

Coarse direct sums take a maximum, not a label-count sum. The code evaluates
(1) with exact prefix/suffix products. Put Lambda=max_ca lambda_ca. An
explicit preparation target is

```
t_source = t + ceil(log2(8 g R (Lambda+1)^(g-1))).                   (2)
```

Prepare each Full root at radius one and target t_source. The source theorem
gives e_ca<=2^-t_source<=1, hence (1)<=tau/8. Actual source bounds may be
smaller and are retained exactly. This uses linear endpoint defects, not
local nonlinear rounded guarantees. Source preparation is separately charged.

## 2. Synchronizing heterogeneous actual programs

The number depth_ca of logical Full matching layers depends on the coefficients:
the exact displacement-generator count can vanish. In the source witness,
three N=2 plans have 21 layers and a scalar plan has one. A common size does
not imply an already identical whole-program signature.

Each logical layer nevertheless lowers to a coefficient-independent signature.
The actual Beneš recursion on N=2^m has switch-bit order

```
0,1,...,m-1,...,1,0.
```

Induction uses the first and last bit-zero switches and two interleaved
(m-1)-bit networks. Only switch choices depend on the permutation. Each
switch emits H,D,H,D. Every source gate, scalar pair and idle pair has seven
diagonal positions and six bit-zero H positions. The return route reverses
the same network. Each logical matching therefore has

```
J_m=16m+5 stages,  h_m=8m+2 raw-H stages,  d_m=8m+3 diagonals.       (3)
```

Set L=max_ca depth_ca and append L-depth_ca empty logical matchings to each source
plan. The unchanged compiler completes these with genuine identity words.
All-one diagonal pages have the wrong six-H endpoint, as #4253 explains.
The exact endpoint remains U_ca. All added stages and roundings enter the
global allocation. The coefficient-independent Full depth bound keeps L
polylogarithmic; the actual source is not modified to force equal depths.

At an H position with local bit b, emit one request on the complete global
field, with mask `{a*m+b : 0<=a<g}` and all coarse bits preserved. At a
diagonal position, use the product of the g actual per-axis entries for that
record's label. Each global stage is the direct sum of tensor products of
padded local stages. Multiplicativity of tensor products proves the prepared
endpoint in Section 1. A separate finite check applies the original stored
logical gates without using the compiled primitive word.

There are exactly

```
J=L(16m+5),    H=L(8m+2),    D=L(8m+3)                             (4)
```

global events. No native call is made independently on a microbox or masked
coarse-label subset. Forward and stored-inverse words share the same signature
property, so directions can differ across labels and axes.

## 3. Actual-source prefix bounds, including padding

For each program, #4253 proves prefix and inverse-prefix bound C_ca for its
exact, unrounded compensated H0 word. The raw word replaces H0 by H and
removes the factor two from the immediately following diagonal. At each cut
their prefix operators differ only by a scalar in {1,2}; inverse prefixes
have the reciprocal scalar. The bound 2C_ca covers both raw operators.

Identity padding preserves the logical prefix/inverse-prefix bound Pi: after
each complete extra layer the map is the original endpoint. Within padding,
the existing complete identity/routing fragment bound is covered by the
source's 4096*Gamma allowance, with Gamma>=1. The same C_ca therefore applies
after padding; it is not multiplied once per extra layer. These are exact
reference bounds, not assertions about rounded factor tables.

Put

```
A = max_c product_a (2C_ca),       E = max_c product_a E_ca.        (5)
```

Every exact global prefix and inverse prefix has 2-norm at most A, and its
endpoint has norm at most E. This also covers an H event after only a subset
of its independent axes has acted. Tensor products multiply operator norms;
coarse direct sums take maxima. Arbitrarily correlated spectators remain
covered by these operator statements.

## 4. The new global rounding protocol

Use one F-grid, F>=max(1,F0), for incoming F0-grid data. The initial lift is
exact. Let u=2^-F and truncate both signed components toward zero only at
declared sites. Let B>=1 bound the complex l1 norm of every exact raw factor
entry, including padding; the code obtains an integer B from the actual
pages. Write b=B+1.

First truncate factor tables to the F-grid. At every diagonal stage and
coarse label, the required coefficient is the fresh nested expression
`q_g=1; q_a=T_F(dhat_a[digit_a] q_(a+1))` for a=g-1,...,0. Form the complete
complex product q_0 times the data, then truncate it to the F-grid. An
odometer cache may recompute affected suffixes on carries. A materialized
suffix expansion is equally valid if it produces the same nested value.
Never divide by an old entry, reuse a stale label cache, or invert a rounded
coefficient to prepare an inverse.

The established #4178 cached-product theorem gives

```
|stored_tensor_coefficient - exact_product|_1 <= delta
       := 4g b^(g-1)u,        |stored_tensor_coefficient|_1 <= 2b^g.  (6)
```

A correct cache or suffix expansion equals that expression at every address;
the error does not grow with scan length. This package consumes that result
at the actual Full pages; it does not claim a new cache lemma.

The coefficient error in a global diagonal has operator 2-norm at most delta.
Each coordinate's data-rounding l1 residual is at most 2u, so its whole-field
Euclidean residual is at most `2Vu`, with

```
V=2^ceil(n/2) >= sqrt(T).                                         (7)
```

The raw-H service must return the exact sum/difference transform on the actual
incoming F-grid data. H has integer entries, so its completed result stays
on that grid. There is no H-stage host-rounding residual. This differs from
the local #4253 H0/data-rounding trajectory. An imperfect H service requires
another funded term and is not covered by the present interface.

## 5. Complete error and state bounds

Let P_j be exact global prefix j and let Delta_j be the diagonal coefficient
perturbation, zero at H stages. Its conjugated factor is
`K_j=P_j^-1 Delta_j P_(j-1)`, with norm at most A^2 delta. If

```
v=D A^2 delta <= 1/2,                                             (8)
```

the product of any interval of `(I+K_j)` has norm at most exp(v)<2 and its
difference from identity at most 2v. Consequently the stored-coefficient
linear prefixes have norm at most 2A, their suffixes at most 2EA, and their
segments at most 2A^2. This interval argument gives 2A^2 directly; it does
not multiply two separately weakened prefix bounds.

The linear coefficient endpoint error is at most `2E D A^2 delta R`. Every
realized data-rounding residual is bounded on its actual input by (7).
Propagating those residuals through the stored-coefficient linear suffixes,
not through a nonlinear-rounder Lipschitz assumption, gives

```
epsilon_arithmetic <= [8E D A^2 g b^(g-1)R + 4EA D V] u.           (9)
```

Define the two bracketed terms as K_coefficient and K_rounding. The explicit
allocation

```
F >= max{F0,1,t+ceil(log2(4 [K_coefficient+K_rounding]))}.           (10)
```

funds (9)<=tau/4. It also gives `v<=tau/(8ER)<=1/16`, hence (8). Combining
(1) and (9), the actual globally rounded output differs from the exact
requested root/inverse tensor by at most `3tau/8<tau` in whole-field 2-norm.
No factor proportional to the number of coarse labels is introduced.

At any completed stage, realized data residuals give

```
||state||_2 <= 2AR+4A^2 D V u <= 2AR+A*tau/(4E) < 4A(R+1).        (11)
```

The same bound covers the unrounded value just before a data truncation.
The raw-H service's internal word widths and restoration must be charged
separately; exactness of its returned map does not make internal work free.
Its integer-array contract is the actual input to the physical composition.

## 6. Widths, complete bill and service domain

Let h=ceil(log2(4A(R+1))) and k=ceil(log2(2b^g)). The code requests:

```
data:       F+h+2 signed bits per component;
factor:     F+ceil(log2 b)+2;
cache:      F+k+2;
temporary:  2F+max(h,ceil(log2 b))+k+3.                            (12)
```

These cover both real products and the complete sums in a complex product,
before truncation. Incoming integers are lifted once from F0 to F. The actual
input-radius check uses 2T real squares and a sum; this ordinary boundary work
is separately counted. Immutable root/plan/page authentication and exact
proof observers are verification work, not hidden inside an accelerated
online kernel claim. A Python execution is not a fixed-tape implementation.

The retained hashes serialize exact rational integers in decimal. CPython's
default digit cap would impose an unrelated finite-width ceiling, visible
already at F0=16384 for the identity root. `sources.py` therefore encloses
trusted source preparation and hash checks in a serialized context that
temporarily disables that process-wide conversion cap and restores its prior
value in `finally`. It does not change arithmetic, input text parsing, the
source files or hash formats. The 16384-bit fixture and successful/exceptional
restoration controls check this implementation detail separately from (12).

For the actual source, log C_ca is bounded by
`O(log N+log lambda_ca+log Q_ca)`, with the source's polynomial factors and
constants retained. A raw diagonal is the quotient of two adjacent exact
prefixes, so its operator norm is at most `4C_ca^2`. Each complex entry's
l1 norm is therefore at most `8C_ca^2`; the same argument covers padding.
Thus `log b=O(1+max_ca log C_ca)`, independently of the exact denominators'
bit heights. Its logical depth is polylogarithmic in N. Consequently
(2), (5), (6) and (10) imply

```
F = O(F0+t+log R+n+log D+log g
       +g max_ca(log N+log lambda_ca+log Q_ca+1)).                 (13)
```

The same order covers (12), the per-root preparation targets and addresses.
Thus N=poly(p), lambda_ca,Q_ca=poly(p), g=p^beta with beta<1,
F0,t,log R,n=O(p) give O(p) words. The broader Gaussian gauge envelope can
also be substituted under its strict `beta+2xi-2<1` condition, as in #4178.
Offline exact source coefficients may have poly(p) height; that is separate
from the online operator bounds and O(p) encoded words. No offline table is
silently assumed to fit an online record before its declared rounding.

The source contributes H global native calls and D global diagonal stages
from (4), including all padding. For each diagonal, the inherited cache
protocol uses at most 4T coefficient products, T complete data products,
O(T) table/data moves and O(KgN) factor records. For N>=2 and g>=1,
`gN<=N^g`, so factor-page storage/loading is O(T) records per stage. Cache
initialization and every coarse-label reset are included. Initial field
lifting and final exposure are full paid scans. The separate `Setup` charge
includes actual Full admission and construction, lowering, source/plan/page
validation, the global allocation, and every conversion of an exact raw
factor to its F-grid page, including identity padding. It also includes the
physical control serialization and metadata preparation. Exact rational
coefficient heights enter this bill; coefficient-page rounding is not free
because it occurs before the sealed online call. Setup is amortizable by
complete microboxes only under the corresponding growing-g hypotheses.

If mu(w) is the charged cost of the physical scalar multiplication kernel,
and H_phys is the complete raw-H service cost, a symbolic online invoice is

```
Setup + H * H_phys(n,g,F,data_width)
      + O(D T [mu(temporary_width)+temporary_width])
      + O(T [mu(F0+r+n+1)+F+data_width]).                         (14)
```

Actual constants, registers, record directions, ownership, restoration and
all movement must be supplied by the physical service theorem. A Python
integer `*` is not by itself a proof of a quasi-linear tape kernel. The
semantic fresh-product oracle deliberately costs g products per record and
is outside this production invoice.
The sealed consumer may store all stage controls before execution. In that
implementation the explicit control volume is
`S_code=O(D K g N factor_width + H g log(n+1) + metadata)`; it is not always
O(T) records for fixed g. General total space includes this borrowed code
volume and retained entry backing as well as current owned work. Its
absorption into the complete data volume requires the stated growing-g
family, where `D g N/N^g` tends to zero.

The older physical H service additionally requires a complete global
address/precision regime `n=Theta(P)` and `g<=P^.997`, with its own normalized
entrance and return contract. Local Full fields alone need not meet this
regime. The present emitter exposes the whole field so that these conditions
can be checked. It does not assert them solely from common stage signatures,
nor transfer an older service's rate to the current selected supplier.

### 6.1 Exact scalar multiplication fits the complete global bill

The physical consumer uses the exact all-width `WordProduct` from #3709.
Its inherited recurrence is `M(w)=3M(ceil(w/2))+O(w)`, with fixed-size
schoolbook leaves. The retained theorem includes serialization, operand
copies, recursion-frame parking/restoration and zero padding, and gives
`M(w)=O(w^nu)`, `nu=log2(3)`, with O(w) live work. Complex multiplication
uses four such exact signed products and paid additions/truncations. This
choice has no scalar FFT approximation or scalar numerical-recovery premise.

For a concrete asymptotic family, suppose the hypotheses giving (13) hold,
`n=Theta(p)`, `N=p^O(1)`, `lambda_ca,Q_ca=p^O(1)`, and
`g=Theta(p^beta)` with a fixed `0<beta<.997`. Then F and data_width are
Theta(p): the upper bound is (13), and the `sqrt(T)` contribution to
K_rounding forces F=Omega(n). The temporary width is O(p). Set
`V=Theta(T p)` for the complete bit volume. Since D/H is bounded by 11/10,
the exact coefficient/data products and incoming radius work cost

```
O(D V p^(nu-1)),          nu-1 = .5849625007... .                  (15)
```

The inherited #3627 H invoice, with native precision `P=Theta(p)`, is

```
O(H V [g^alpha log p + (g+1)^eta (log p)^(1+eta)]),
alpha=99827101/100000000,    eta=332353/332929.                     (16)
```

When `beta*alpha>nu-1`, (15) is absorbed by the first term of (16).
The threshold is `beta>(log2(3)-1)/alpha`, approximately .585975647.
For example beta=.975 gives beta*alpha=.97331423475. The strict comparison
can be certified without decimal logarithms: `3^5<2^8` implies
`nu-1<3/5<beta*alpha`. This includes the same source depth on both
sides; Full depth and m are polylogarithmic in p. It is not an assertion
that either local H calls or a scalar product alone have the complete rate.

Native domain conditions, movements and any initial address gather remain
those of the actual physical H boundary. In particular a boundary requiring
`gm<=P^.997` satisfies that condition eventually for the stated strict beta
and `m=O(log p)`. Setup remains an explicit term. If the per-label source
generation and exact coefficient heights have polynomial(p) bounds, its
K g polynomial(p) cost is amortized by the complete `K N^g` field for growing
g and N>=2; coarse-label multiplicity is not discarded from that bill.

This is a compatibility and complete-cost consequence for the scoped global
caller. It does not prove the retained native, hosting or machine-refinement
premises, close the outer multiplication argument, or change kappa.
The full sum (14), including (15), remains the general bill. In particular,
an outer caller with `g=p^epsilon` below the displayed threshold cannot
absorb this exact Karatsuba diagonal in its H term by this argument. The
beta=.975 example does not retune that caller or replace its outer-compatible
fast scalar/diagonal obligation. A faster scalar service would need its own
actual-source, complete-cost and exact-return join.

## 7. Physical realization and remaining outer interface

[PHYSICAL-PROOF.md](PHYSICAL-PROOF.md) establishes the physical realization
of these typed complete-field H and D events under its explicit inherited
H service and integer-runtime premises. `PreparedFull` authenticates and
encodes the actual source events before execution. `FullPhysical` performs
the complete squared-radius check, exact incoming-grid lift, every H/D event,
and the protected complete return using one Count/Tape cohort. No decoded
intermediate list or host integer product implements an online payload step.

The physical diagonal expands the fresh rounded suffixes highest axis first.
Its lower-axis digit is the inner loop, so its completed field agrees with
the fresh-product protocol preceding (6), including every intermediate
component truncation and zero factor.
The number of coefficient products is less than twice the final field size,
and its page rewinds, buffer movement and cleanup have a geometric sum.
The raw-H bridge returns exact F-grid integer numerators; the subsequent
width restoration discards only redundant high sign bits, as justified by
the global raw-prefix bound above. Thus the physical endpoint is the same
new global rounded execution analyzed here, rather than an invocation of
the original nonlinear local source trajectories.

The physical proof supplies the concrete instance of (14), including source
preparation, encoded controls, native-owner construction, full word returns,
radius checks, movement, scratch initialization/erasure and retained backing.
Its scalar service is exact all-width Karatsuba, so it inherits no scalar FFT
recovery premise. The separate H child still retains its source native,
internal stock, numerical and ownership hypotheses and its complete global
address/precision domain. No favorable scalar comparison removes these.

The finite actual Full join uses the stored inverse of `(2+i)I_2`, all 21
stages and unchanged F407/W608. Separate nonconstant multi-axis service
controls distinguish label/axis order and coefficient/data truncations.
These corroborate the implementation; they do not prove a production native
or the universal numerical inequalities. Full Gaussian/core/halo assembly,
outer setup/grouping admission, final integer recovery and any new kappa
remain outside this scoped compiler composition.
