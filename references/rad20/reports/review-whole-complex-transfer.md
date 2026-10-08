# Independent review of whole-rank complex phase calls

The new whole-rank complex construction passes independent analytic transfer
review. An admitted binary residual of rank r can use **one complete
`C^(r*f)` child**, with the already paid binary basis adapter, in place of
r separate `C^f` children. For the independently accepted h28R88377 circuit,
a simple strict phase branching saving is **b_phase=10^-6**. It is above
twice the independently certified generic bit saving
`143492327855947419/10^24`, so beta1/2 leaves room for a bit-limited full
composition. This report accepts the new construction and its branching
bound; a final multiplication parameter assembly remains separate.

This is a changed recursion. The full complex runtime still pays binary
address movement at the bit exponent tau. The result does not assert a
standalone complex runtime exponent below tau, omit a basis adapter, or
use characteristic-zero rational frames as binary complex frames.

The immutable campaign start is 2026-10-07 22:25:21 UTC. Its historical
deadline is 2026-10-08 08:25:21 UTC and its user-extended active deadline
is 10:00 UTC. The primary phase interface is the original manuscript at
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`, sections03 and05. The compact
movement/layout input is pinned to
`6e564879f51ae16f23d392e9e196c605f36d90df`. The two new written transfer
inputs are frozen and byte-pinned:

| Written input | Bytes | SHA256 |
| --- | ---: | --- |
| [whole-complex-concatenation.md](whole-complex-concatenation.md) | 11385 | `5781af807210dc3ac740e876cdb8073683ea3658f4b8aa067605608919a8f520` |
| [whole-complex-prefix-and-wrapper-qualification.md](whole-complex-prefix-and-wrapper-qualification.md) | 3815 | `84ebd3bb5327ccd04134db36d0b109b377c6d6cf2c0c82923d1c35b596dc43b2` |

## Exact mixed phase, without a gather

Fix the supplied width K and selected offset rho of one outer round.
Every recursive descendant retains them. Balanced chunk widths may vary
between outer rounds; all axes within one round have the same supplied
K_j, so the common K assumption is valid at every invocation.

For e=mf+t, f=floor(e/m), the main mf selected bits occupy m adjacent
complete fields of length fK. The selected bits in slot h are
`rho+(h*f+j)*K`, for j=0..f-1. The final tK field is a complete spectator.
An existing invertible binary adapter has the chosen orthonormal residual
basis as its first r columns. Apply its paid inverse to the selected
m-bit column at every j. The first r fK slots are now adjacent complete
fields in their actual physical order. Their union is one complete rfK
field, with selected positions `rho+j*K`, j=0..rf-1. Only its descriptor
changes. No additional record permutation, noncontiguous pivot gather,
padding, conversion of K, or loss of unused coordinates is involved.

An orthonormal residual vector can have weight1 or3 modulo4. The phase
interface may therefore require either C or C^-1, including on reversed
edges. For the Gaussian dyadic kernel,

```text
C=aI+bX, a=(1+i)/2, b=(1-i)/2,
C^-1=-i Z C Z.
```

If n_minus of the r directions are inverse, their complete f-column
mixed tensor is exactly

```text
(-i)^(f*n_minus) Z_minus C^(r*f) Z_minus.
```

Z_minus is parity on the selected bits of the negative slots. It does
not touch the unselected bits in their complete K-bit chunks. The already
reviewed aligned phase-counter scan evaluates this mask in a fixed number
of bit-volume passes, with its actual selected offsets and descriptors.
The last factor is a single fourth-root unit depending on f modulo4 and
fixed basis data. Thus two paid diagonal scans and one unit operation
replace the individual inverse wrappers; no additional recursive call or
XOR address translation is required. The inverse basis adapter restores
the complete external field order afterwards.

This argument is applied within one edge, before its next pointwise
scalar gate. It does not commute a phase call past unrelated scalar gates.
The common-frame identity consequently sees exactly the same edge operator
and retains the same signed role permutation on arbitrary Gaussian dyadic
arrays, including arbitrary dirty auxiliary values.

## Arbitrary integer widths and tail action

The new child contract accepts every integer e. It is not the old
power-of-m routine applied r times. During the complete main invocation,
the trailing tK field stays a spectator, including during source/sink
corrections, basis changes, all scalar gates and the corrected bank return.
Those source/sink phases use precisely f main columns.

After the main mf call has completed, apply the t<m exact individual C1
kernels to the trailing selected positions, once per returned original
row. Their complete two-element ranges permit the original stable split,
aligned pair scan and merge. Each kernel takes a fixed number of full
volume passes and restores the original lexicographic order. The same
operation on a padded zero row leaves it zero. Since main and tail selected
positions are disjoint, their tensor product is C^e for arbitrary input
arrays. No tail crossing or growing sort is needed: the tail is already
the complete trailing field. Width e<m uses only this fixed-size base case.

Each saved-input pair uses Gaussian sums and differences, unit phases and
exact halves. A conservative32 coefficient-depth units per tail bit are
included below. The original fixed fine-grid representation is retained
throughout; recursive outputs are not rounded or compacted.

## Exact volumes and simultaneous row stock

At a complex node, split the complete preceding row index as `u=Wc*g+w`.
All Wc role streams retain the same complete suffix and guarded record
width. Every child has exactly V/Wc logical bit volume regardless of its
active width rf. Inactive slot fields, the tail, ordinary polynomial indices
and arbitrary scratch remain spectators. A depth-first implementation
parks the other fixed number of role streams at the top of a LIFO work
tape and restores them on return. Its push/pop/copy work is proportional
to the current node's volume; it does not scan ancestor parked data.

A bit adapter invoked inside a complex descendant also needs complete
rows. The safe stock is the **product**

```text
Q_rows=Wc^Dc * Wb^Db.
```

Using only the larger separate polynomial would not establish this nested
contract. At complex depth j, the inherited row count stays divisible by
`Wc^(Dc-j)*Wb^Db`. A bit invocation can temporarily split its current
complete row prefix by Wb, park its other roles, and restore the prefix
when its complete address operation returns. The Wb factor is reusable;
the next complex child consumes another Wc factor. The two selector sets
and all active coordinates are disjoint at completed boundaries.

There is a concrete physically preceding stock, without moving a suffix
for free. At the top of the outer invocation, set
`q0=ceil(log2 Q_rows)`, computed exactly as `(Q_rows-1).bit_length()`.
Apply C1 to its first min(e,q0) selected positions, preserving each entire
complete K-bit chunk. If e<=q0 this completes the invocation at cost
O(Vlogp). Otherwise their already transformed q0K field is a leading
row prefix of size `R=2^(q0*K)>=Q_rows`, immediately followed by the
remaining active field with the same rho and K. This initial tensor acts
on disjoint axes from every completed remaining invocation.

Only **after** this initial transform, append zero rows to reach
`Q_rows*ceil(R/Q_rows)<2R`. External activation metadata is kept out of
Gaussian coefficient operations. Padding occurs once. All descendants
inherit that same prefix; they do not repeat its C kernels, duplicate the
prefix, or introduce further volume doubling. Each complete remaining call
acts within its row and restores scratch, so the extra rows return to
zero and can be removed at the completed boundary. The first q0 axes and
the remaining axes together have received exactly C^e.

Because both depth bounds are O(logp), q0=O(logp), with a fixed constant.
The preprocessing costs O(Vlogp) once per outer round, absorbed only by
the retained strict power gaps. If the prefix would consume the available
axes, its elementary fallback has exactly that same bound. At a new
balanced outer round the supplied K_j and rho may change, and the one
preparation is performed again; a recursive child never starts a new
preparation. Its selected mask and shape descriptors remain O(p).

For h28, m=21952 and rmax=m-2h=21896,
`m^272>2*rmax^272`. Hence complex depth is at most272ceil(log2 e).
The accepted generic bit input has depth at most651ceil(log2 e),
Wb<2^49 and Wc<2^41. Under the retained eventual conditions e<=Cp,
p>=C and log2p>=25,

```text
log2 Q_rows <= (49*651+41*272)*(2+1/25)*log2p
            = (2195601/25)*log2p <89000*log2p.
```

The conservative supplemental suffix condition
`b_input^(1-epsilon)>356000*(log2b_input+8)`, together with the retained
ell and p comparisons, also covers this product stock. A final composer
must check its new compressed powers and retain uncomputed fixed table,
prime, descriptor and polylogarithm absorption thresholds. This review
does not replace that obligation by the old maximum-only66000 estimate.
The concrete initial-prefix construction independently explains where the
required physically preceding rows come from.

## Semantic precision with near-parent children

The completed grouped child on rf selected bits has entries in
`2^(-rf) Z[i]` and absolute row sum at most `2^(rf)`. The same holds for
its corrected inverse. This is precisely the semantic charge of the
r replaced complete children. A child may visit a finer grid internally,
but its completed excess does not accumulate into the next child's bound.
No actual rounding, lower-width rewrite or Fraction cancellation is used
to implement this fact.

The actual accepted finite circuit has

```text
R=88377, c=94966, W=1967894720064, s=43199206864789248,
G=13074237304128,
E=487736851028968488321153678560340410432.
```

The stronger literal node bound pays original scalar evaluation, up to
three extra unit wrapper operations for every positive call, one further
rank unit of slack, and all short tail kernels:

```text
2GW^2+8s+4W+4+32m
 =101262834558282155716455420252358273284
 <E,
E-depth=386474016470686332604698258307982137148>0.
```

There are at most s positive calls, because every such call has rank at
least one. The reduced physical role count cannot replace c in G, and
the false shortcut G<6W is not used.

Before an active child, all completed calls have total selected width at
most sf. Their semantic charge is therefore at most sf. Fixed scalar,
wrapper and tail work is covered by E. The correct active recurrence is

```text
A(e)<=A(rmax*floor(e/m))+s*floor(e/m)+E.
```

It is not the uniform-child A(e/m) recurrence. Set B=s+E>=8. A leaf has
A(e)<=8e. At an internal node e=mf+t and f>=1, induction gives
`A(rmax*f)<=2B*rmax*f`. Since rmax<m,
`2B(m-rmax)>=s+E`, proving A(e)<=2Be, including E and the nonzero tail.
Thus near-parent children do not introduce an uncharged numerical depth
factor. Across the complete outer selected-axis decomposition, the sum of
piece widths is at most d. Preprocessing, outer phases and normalization
use the retained additional18d units, so

```text
A_layer<=(2B+18)d<C0*d,
C0=32mB^2, C1=1.
```

The common fixed fine-grid coefficient format therefore remains the
accepted O(p)-bit format when its strict guard condition and cutoff hold.
The single outer normalized butterfly truncation stays at its original
boundary. Neither temporary phase values nor unfinished child maps are
treated as contractions.

## Variable-width stopped-tree cost

Let n_r be the number of proper children of relative width r/m, including
the retained individual calls as r=1. Each has volume V/Wc and width
`r*floor(e/m)`, no larger than (r/m)e. Choose sigma with the strict
homogeneous characteristic

```text
z=sum_r(n_r/Wc)*(r/m)^sigma<1.
```

For the actual recursion, weight each node's e^sigma by its logical
volume relative to the root. The children of every internal node have
at most z times its potential. At depth j, total active potential is at
most z^j d^sigma. Retaining stopped leaves in the frontier also proves
that their total final potential is at most d^sigma, even though they
occur at unequal depths.

Stop at e<d^beta. Linear leaf work satisfies
`e<=e^sigma*d^(beta*(1-sigma))`, giving the leaf exponent
`sigma+beta*(1-sigma)`. The bit adapters still have node exponent tau.
If tau>=sigma their characteristic is also at most z, so internal costs
sum geometrically to O(d^tau). If tau<sigma, every internal e>=d^beta
has `e^(tau-sigma)<=d^(beta*(tau-sigma))`. Summing its sigma potential
gives O(d^(sigma+beta*(tau-sigma))). Therefore the retained internal
exponent is

```text
chi=tau+(1-beta)*max(sigma-tau,0).
```

The fixed strict denominator1-z, tail/parking O(1) work, paid phase scans
and leading O(logp) work enter the implicit constants and polylogarithms.
The final parameters must retain
`max(tau,sigma,chi)<lambda<lambda_prime`, the leaf gap, the compact
reservation exponent max(1-c,0), K geometry, precision and resampling
constraints. The accepted d^beta>2m cutoff may be retained for the full
stopping interface, although this upper leaf-potential proof does not
need a lower bound on leaf size. No equal-depth-tree assumption is used.

## A simple independently certified phase characteristic

Only three disjoint physical boundary families are grouped. With
v=C(h,3), N=v^3 and J=(R+h+1)v^2:

| Family | Residual rank | Multiplicity |
| --- | ---: | ---: |
| Final middle-bank complement | m-h^2=21168 | J=948788751456 |
| Shared first/third auxiliary join | m-2h=21896 | J=948788751456 |
| Two stage3 data increases | (h^2-1)(h-1)=21141 | 2N=70317217152 |

The middle bank's final label is `F tensor F tensor line(t_B)`, so its
full sink complement has the displayed rank. The joined labels E and H
have dimensions h and m-h with E contained in H; their residual has
rank m-2h and the accepted outside-coordinate norm-one witness. The two
stage3 data increases are X incoming-to-time2 and Y time0-to-time1,
with residual `(line(t_1 tensor t_2))^perp tensor t_3^perp`. Both factors
are nondegenerate and nonalternating. The latter is not Y incoming-to-time0,
whose residual is zero. The three families are different physical edges.
Controller and delayed clones change internal side allocations, not these
external labels. Every other rank remains an individual r=1 child.

The resulting integer child histogram is

```text
n1=853991784277632,
n21141=70317217152,
n21168=n21896=948788751456.
sum n_r*r=s=43199206864789248.
```

Independent80-term rational logarithm series prove ln(m)<10 and ln(r)>9.9
for every grouped rank. If credited rank is T and
M_L=9.9T, the positive normalized characteristic has the sufficient gap

```text
D-b*(10s-M_L)-b^2*(100s/2)/(1-10b)>0.
```

This follows from
`exp(x)<=1+x+x^2/[2(1-x)]` for0<=x<1, applied to
`x=b*ln(m/r)`. At b=10^-6 the exact gap is
`111225521101498713/21171875>0`. Consequently sigma=1-b satisfies
the strict characteristic. This deliberately coarse b is already above
twice the accepted generic bit saving, with exact difference
`356507672144052581/(5*10^23)>0`. At beta1/2, the phase leaf margin
b/2 exceeds that bit saving. A sharper phase root is optional and cannot
improve a composition whose bit branch is already limiting.

## Independent executable evidence and limits

Three fresh runs separate algebra, characteristic and final written-input
qualifications:

| Run | Main checks | Wall / peak RSS |
| --- | --- | --- |
| [0718Z](../runs/20261008T0718Z-review-whole-complex/report.md) | Mixed directions/binary adapters, fixed-grid unequal children and tails, layout, guard, stopped trees | 3.84s /23212KiB |
| [0728Z](../runs/20261008T0728Z-review-whole-complex-characteristic/report.md) | Independent80-term logs, full rank histogram, b=10^-6, bit comparison | 0.04s /19656KiB |
| [0732Z](../runs/20261008T0732Z-review-whole-complex-transfer/report.md) | Frozen report hashes, stronger8s+32m guard, combined89000 degree, leading prefix/product row return | 0.17s /20920KiB |

All used Python3.14.7, one owned worker, one numerical thread, a16GiB
address-space limit and zero swap. Each owned reservation was released.
The precise actual execution times are in their protocols; the short UTC
run labels are experiment identities. Their sources are
[review_whole_complex.py](../code/review_whole_complex.py),
[review_whole_complex_characteristic.py](../code/review_whole_complex_characteristic.py)
and [review_whole_complex_transfer.py](../code/review_whole_complex_transfer.py).
No new producer batching, cloner, characteristic or stopping code is imported.

The controls check224 mixed phase probes/19472 exact entries in both
orientations with complete binary adapters,607488 asserted exact integer
halvings,180 variable-width fixed-grid probes,2140 completed-child bounds,
23760 stopped guard recurrences,2255 complete layouts and92625 selected/
spectator memberships. Twenty-four heterogeneous stopped trees cover tau
1/4,1/2 and3/4 around sigma1/2. The final labelled-row controls check55180
exact nested returns at42 complex depth boundaries. Omitting the mixed
wrappers, omitting a nonzero tail, repeating the prefix at a child, and
omitting the V/W volume factor all discriminate.

These exact small tests support the analytic proof. They do not materialize
the entire giant phase table, execute a full h28 array of size v^3, or
constitute a fixed-tape timing experiment. The finite complex witness,
binary residual existence, generic rational bit primitive and all setup
thresholds remain the previously reviewed inputs. The new proof uses
their actual paid tape interfaces and supplies the missing arbitrary-width,
mixed-direction, nested-volume and semantic guard arguments.

Reproduction follows each run's protocol command with fresh output paths.
Hashes of every source, accepted finite/bit certificate and frozen written
input are in the protocols and compact certificates. Exact mathematical
results are regenerable; historical timing, admission and process records
are observational. The last short run records the finite queue handoff
received after its terminal return rather than claiming its legacy marker
as a current-pool audit. No scientific result or source bytes were changed
by that handoff.

Confidence is high for this explicitly scoped whole-child transfer. Novelty
is unclaimed. A full exact multiplication witness must independently
compose its phase branching exponent with the paid bit exponent, linear
semantic guard, balanced/unbalanced transform choice, bulk Gaussian
resampling, new joint row stock, and all strict cutoffs. No final kappa
is asserted here.
