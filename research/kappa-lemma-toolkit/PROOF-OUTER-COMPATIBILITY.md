# Source-bound capped-fusion compatibility

The reusable Lean lemmas are the principal contribution of this package. This
note separately checks how its improved finite supplier can be consumed by the
existing capped-fusion outer proof. The resulting sufficient conditional target
is `kappa=168357/100000000=0.00168357`, using the actual complex supplier saving
`b=84179/50000000=0.00168358`. This is not a Lean formalization of that outer
proof or an unconditional multiplication theorem.

## The completed operator actually consumed

PR1673's *Conditional capped-fusion transfer* and its supplier-support audit use
a globally complete selected-bit tensor call, on arbitrary coefficient data,
with identity on dirty helper, row-label, coarse-label and spectator coordinates
at each completed boundary. Its paid cost must be
`O(V*g^(1-q)*polylog(p))`. It is not enough to have one selected output, a rank
histogram, or an all-zero-helper calculation.

Our finite word and physical admission have that required local scope: both
orientations restore arbitrary dirty input columns, all helper endpoints have
actual normalized `C_w tensor I` wrappers including phase, all original child
translations are retained, and each helper occupies one whole owner slot. The
new canonical owner-table SHA256 is
`11a8742b501446c258ef4a1fa423ec2f8c041135c94f4d82356f7bd6f7da3d1c`.
It has 31,392 roles in 72 calls, with 436 helpers per call, on the unchanged T8
chronology of forty forward and thirty-two backward calls. The complete
recounted profile is

```
{1:176252, 2:30096, 3:30903, 4:10152, 5:4512, 6:4,
 7:485, 8:577, 32:8, 39:4, 40:2, 48:2497}.
```

Its rank mass is 520704, live stock is 7168, and deficit is 2560. Both independent
exact moment engines accept `b=0.00168358` for both the native profile and the
retained conservative bad-residue surcharge. These checks bind the same owner
table, complete physical profile, literal traces and finite invoice; an old
supplier endpoint is not substituted for the new construction.

To make the normalization explicit, write `C=a0*I+b0*X`,
`a0=(1+i)/2`, `b0=(1-i)/2`, and `S=diag(1,i)`. Direct multiplication gives

```
b0*S*C*S = H/2,       H=[[1,1],[1,-1]].
```

Tensoring this identity gives the required normalized Hadamard on every input,
with the same spectators, from the completed global C tensor. The phase scans
and dyadic scalar are the retained exact wrapper operations. The raw H used by
the outer circuit compiler is obtained by one scalar shift `2^g`; its extra
magnitude/denominator allowance is O(g). The tensor lifts include the actual
scalar phase raised to the repeated-coordinate multiplicity.

## Why the supplier substitution is generic

The original PR1673 theorem was stated with a T8 supplier before its later T74
substitution. Its section *Updated T74 supplier* explicitly parameterizes the
proof by effective supplier rate. The accompanying substitution review states
the functional interface: normalized completed transform, arbitrary dirty
restoration, O(p)-bit coefficient encodings, and the paid global selected-bit
call. Gaussian blocks do not inspect donor labels, helper multiplicities,
replica count or a particular parent-word order.

Our fixed native dimension is 73 and largest child rank is 48;
`73^2>2*48^2`. The exact row/stock invoice retains 492 old helper reserves and
adds all 75 private cleanup arrays, charging 7745 physical families altogether.
Its row coefficient is `16467<20161`; the exact local magnitude allowance is
`244*lambda<512*lambda`; its fresh common-exponent reserve fits `C0=2^210000`.
All of these are fixed supplier constants.

The precision interface is exact Gaussian-dyadic recursion, with no
intermediate child rounding. The active-depth lemmas in `Recursion.lean`
justify the sufficient recurrence-to-linear-guard implication, including
arbitrary widths and tails. They do not independently establish the inherited
all-size implementation contract. The outer requires that contract with
online dimension exponent C1=1. Increasing its fixed coefficient does not
change its exponent: because beta and epsilon are strictly below one, the
fixed-constant O(g) and O(d) terms are eventually o(p). Offline coefficient
setup has its own separately paid precision budget.

There are material restrictions on this substitution. Each simultaneous
Hadamard is global over complete coarse-label ranges; borrowing inside a
single fixed-label microbox is invalid. Support routing uses complete
K-neighborhoods and the paid equal-chunk interchange. Its tightened condition
is `K>=G+4*ceil(log2(p))+10`; one must not claim `K=128G` satisfies the former
stronger wording `K/log(p)->infinity`. The row reservation is the product of
nested bit and complex stocks, not their maximum. Phase padding adds complete
rows and removes them at the completed phase boundary. None of these operations
is supplied by a rank moment alone; they remain the retained all-size and
support-local construction interfaces.

## Actual rate consumption and a sufficient parameter point

The retained bit endpoint is `0.001733427039589844234749`. Use the following
exact rational point:

```
b=.00168358, q=b-1e-9, a_eff=(q+b)/2,
epsilon=1-1e-6, beta=1-3e-6,
r0=1e-7, zeta=1e-9, layout_slack=1e-8, stop=1e-9,
tau=45/16, c=(3-tau)/2=3/32,
xi=epsilon*(1+q)-c+layout_slack.
```

Here `0<q<a_eff<b<bit`. The supplier's stopped internal and leaf exponents are

```
internal=(1-a_eff)+(1-stop)*max(a_eff-b,0),
leaf=(1-b)+stop*b.
```

Both savings exceed q; the leaf saving also exceeds a_eff. Thus the supplier is
consumed first in the stopped support-local global H call and then in the
outer costs, rather than merely appearing as a number in a final inequality.
The nine paid savings are respectively

```
epsilon*q, a_eff, 1-epsilon+q*beta,
1-epsilon+a_eff*beta, 1-epsilon+beta,
c+xi-epsilon, xi+1/2-epsilon, epsilon,
1-(epsilon+beta+48-128+2).
```

Every one strictly exceeds `kappa=.00168357`. The smallest is the main saving
`epsilon*q=.001683577316421`, with exact gap `7316421/10^15`.
All 54 strict inequalities of the retained outer ledger also hold at this
point, including the main-binding Gaussian row, stopped-supplier rates,
record/header work, source-axis growth, cap, halo/core and fine-prime guards.
The independently evaluated point uses moderate strict slacks; it does not
need PR2265's 200-digit endpoint or fixed-grid maximum. No practical eventual
cutoff is claimed. Every implementation constant must still be absorbed at
its own sufficient cutoff.

## Fine prime padding and additional outer premises

The modern conclusion uses more than the former balanced-prefix 47-row outer.
It uses PR1673's capped phase-cell fusion, PR1758's gauge-free shifted kernels
and per-visit radix-union accounting, and PR1786's fine prime padding with
separate setup precision and enlarged polynomial halo. The boundary here is
explicit Strassen, using `7^16<2^45`; the structured-boundary stability claim,
rectangular matrix improvement, and an assumed `omega_C<=9/4` are not consumed.
PR2180/2161's fixed-grid-max refinement explains upstream numerical retunes,
but that grid optimum is not needed for the sufficient point above.

PR2265's tree omits the written fine-prime source referenced by its composition
note. This review retrieved it separately from Chafik Boukhalfa's PR1786,
commit `c52345caa318fc6b1b6e2659c57d746317a72823`, path
`research/fine-prime-padding/FINE-PRIME-PADDING.md`, SHA256
`47d1b1b4df28aadda3cd6bdeb1fbc47290595e9208cd09c1a1f338520d33fdce`.
That source explicitly proves the changed prime interval, conditioning,
setup/online precision separation, normalization and polynomial locality.

Its cited prime-count error estimate matches theorem 2 of
[Trudgian's primary paper](https://arxiv.org/html/1401.2689v2#S2).
For fixed epsilon<1, the exponentially decaying error in sqrt(log(x)) is
eventually smaller than the required relative interval width p^-2, since
log(x) has positive power growth in p. The resulting interval contains more
than d primes. This is an asymptotic sufficient argument; the small prime
fixtures alone would not prove it.

The written padding proof separately uses
`P_setup=C*p+64*p^2*ceil(log2(p))`, rather than rounding full-cell weights at
Cp bits. Actual online capped circuits avoid those full weights and need only
O(p) bits under `beta+2*xi-2<1` and `beta<1`. Polynomial setup and halo/core
work are amortized against complete superpolynomial payloads. Its generic
Neumann locality polynomial has halo exponent48 and core exponent128; it is
used to construct coefficient pages, not iterated on every online record.
The source-prime capacity, distinctness, exact recovery and fixed-tape
prime-packing interfaces remain explicit.

## Source and proof scope

Reviewed outer source is PR2265 head
`9c559717f848498618eb229573cb5183e3d1f38f`, including PR1673's complete note,
`SUPPLIER-SUPPORT-AUDIT.md`, `TENSOR-COMPILER.md` and substitution review, plus
`outer/FINE-PADDING-COMPOSITION.md`, `GAUGEFREE-INTERIORS.md`,
`UNION-SCHEDULE.md`, and both independent ledger implementations. Those proof
files are checked against the upstream manifest, and the separately recovered
PR1786 note has its own source pin. All preceding authorship and license notices
remain applicable.

This establishes a source-bound sufficient compatibility argument under the
stated all-size computational and analytic interfaces and the cited outer
constructions. It does not turn the finite replay, the rate arithmetic, or this
written review into a full Lean proof of multiplication. The reusable Lean
collection remains separately kernel- and axiom-audited and can support future
suppliers without depending on this particular numerical point.
