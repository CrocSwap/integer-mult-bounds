# A sharp radial provider with Gaussian phase symmetry and complete ports

This package supplies an exact-sum Gaussian-pair bijection with error at
most h on the grid `h Z[i]`, where `h=2^-g`. Its forward, inverse outward
and absolute radial suprema are all `h/sqrt(2)`, the minimum from
[PR #7696](https://github.com/CrocSwap/integer-mult-bounds/pull/7696),
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/d7be8d9131a948ea1d25833e96906ea3da979764/research/gaussian-exact-sum-global-optimum/PROOF.md).
Unlike that package's particular construction, this provider commutes
with global Gaussian units. Its inverse is its componentwise conjugate.
It also preserves wire swap and common Gaussian translations.

The provider is installed through the unchanged backend interface of
[PR #6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509),
[pinned port](https://github.com/aliromman/integer-mult-bounds/blob/a4173e810c4d34a1d13b9745af123ad0ec6cfed5/research/conservative-gaussian-rounding/ports.py).
The full two-/three-call programs return both arbitrary stored dirty banks
exactly under reverse execution. Their retained coordinate error requests
remain valid. New radial envelopes cover every call and both complete port
directions. These are indexed numerical programs, not accelerated native
suppliers or fixed multitape graphs. No new kappa is claimed.

## 1. The parity-dependent matching

First set h=1. Use the definitions from PR #7696:

```text
s=x+y, d=x-y,
J(a,b)=(-b,a), B(a,b)=(a+b,a-b), T=B/2, Q=-J,
L=(Z+1/2)^2, H(a,b)=(a,-b).
```

Let M pair consecutive vertices of each square ring in L, starting at
the top right corner and walking along the top, left, bottom and right
sides. Each side includes its initial corner and excludes its final
corner. This is the prior individual-ring involution. It flips the color
given by the integer coordinate sum modulo two.

Write `R=2r=2k+1` for the odd integer side length in unit steps. The
cycle has 4R vertices. Its matching sends index j to `j+(-1)^j` modulo
4R. A half-turn adds 2R, an even integer, so M is odd. The reflection H
sends j to `3R-j` modulo 4R. Since 3R is odd, this reflection commutes
with M. Thus M commutes with H and with -I.

For a mixed-parity sum set `p=Re(s) mod 2` and define

```text
M_1=M, M_0=Q M Q^-1.
```

The implementation stores doubled odd coordinates (a,b) and radius R.
Its cycle index is `(R-a)/2` on the top side, `R+(R-b)/2` on the left,
`2R+(a+R)/2` on the bottom and `3R+(b+R)/2` on the right. The same
half-open corner convention makes the cases disjoint. Each index is an
integer in [0,4R). Toggling its last bit gives its partner; four comparison
branches recover the coordinates without division by R.

Both are involutions, flip colors, preserve square rings and commute with
H and -I. For M_0, use `Q^-1 H Q=-H` and the two symmetries of M.
For both values of p the identity

```text
M_(1-p) Q = Q M_p
```

holds. In the second direction this uses `Q^2=-I` and oddness of M.

## 2. Positive and negative providers

For equal-parity sums use the exact ideal difference `f_sigma(d)=sigma Jd`.
For mixed sums use

```text
f_+(d)=B M_p(T Jd),
f_-(d)=-J B M_p(T d),
F_sigma(x,y)=((s+f_sigma(d))/2,(s-f_sigma(d))/2).
```

The sum and p remain unchanged. The input difference has parities
`(p,1-p)`. The color of T Jd is 1-p, and M_p changes it to p. Applying
B gives the required difference parities. The negative formula has the
same property, with the final -J exchange. Both output halves are exact
Gaussian integers. The identities `T B=I` and `M_p^2=I` give both inverse
compositions. No error bits or history are stored.

A unit matching edge gives squared pair error one. Equal-parity sums have
zero error. Thus every input is a nearest Euclidean Gaussian-grid output,
with each complex-coordinate error at most `h/sqrt(2)`. This pointwise
nearest-error property is retained predecessor work, not a new grid
lower bound.

Global multiplication by i sends p to 1-p and the transformed point t
to Q t. The displayed intertwining identity therefore gives
`F_+(i*x,i*y)=i*F_+(x,y)`. The inverse has the same covariance. For
componentwise conjugation K, the identity `T J K B=H` and commutation
of M_p with H give `K F_+ K=F_-`. Conjugation preserves p, so the same
matching is used on both relevant sum fibers.

Oddness of M_p gives wire-swap covariance. A common Gaussian translation
changes s by twice a Gaussian integer and leaves d unchanged. It preserves
p and hence commutes with the map. Equal inputs and zero are fixed. These
claims hold for all magnitudes on the grid. Finite words require the
range conditions below.

## 3. Sharp radial bound and its native-stage consequence

For mixed sums write `c=|s|^2/2>=1/2`. The squared input and output norms
are `c+|t|^2` and `c+|M_p(t)|^2`. Both matchings use only tangential
square-ring edges. Apart from a zero-cost sign toggle, such an edge has
one coordinate of magnitude r and other magnitudes u and u+1, where
`r>=u+1` and `u>=1/2`.

If `A=c+r^2+u^2`, the squared-radius increment is 2u+1. The radial gap
is less than `1/sqrt(2)` because
`(2u+1/2)^2 < 2A`: the left side is `4u^2+2u+1/4`, while the right side
is at least `4u^2+4u+3`. This also proves the inverse bound. The sum-one
matching is unchanged from PR #7696, so its explicit forward and inverse
sharpness sequences remain:

```text
F_+(-k*i,1+k*i)=(k+1,-k),
F_-(1-k*i,k*i)=(-k,k+1),  k>=1.
```

Their outward gaps tend to `1/sqrt(2)`. The general Hall lower theorem
in PR #7696 applies because this class still preserves exact sums and is
injective. The three suprema are therefore sharp. None is attained at a
finite input. Scaling by h gives the stated grid constants.

Now take a layer of N/2 disjoint pairs. Write a and b for the vectors of
pair norms before and after that layer. Each component satisfies
`|b_j-a_j|<=h/sqrt(2)`. The reverse triangle inequality in R^(N/2) gives

```text
abs(||layer(z)||-||z||) <= h*sqrt(N)/2.
```

This layer bound is sharp: use the same forward sharpness pair at every
site, then let k increase. The joint output error from the ideal layer is
at most `h*sqrt(N/2)`. The radial and approximation bounds are different
statements; the smaller radial constant does not reduce the error constant.

A native call on `N=8^f` applies f literal layers, at bits `3j+axis` with
axis 0 or 2. Its inverse reverses this order and uses F_-. For every call
and every prefix of j layers,

```text
abs(||prefix_j(z)||-||z||) <= j*h*sqrt(N)/2,
||rounded_call(z)-ideal_call(z)|| <= f*h*sqrt(N/2).
```

The first bound follows by adding the layer radial changes. The second
uses the ideal layers' unitarity. No independent-error premise is used.
The factor f is a sufficient bound; no sharpness claim is made for a
complete multi-layer call. Every spectator-fiber sum is preserved exactly,
as each pair has exact sum. There are 4^f such independent complex sums.

## 4. Complete retained ports and radial envelopes

The root ports.py and predecessor/rounded.py are exact copied source
bytes. ORIGINS.json pins their public Git objects. The only supplied new
operation is the explicit numerical backend argument. The source uses
its actual P, Q, W and M monomials, its triangular addition and all k paid
calls, for k=2 or 3. No source function is patched. The kernel.need function
implements the port's unchanged predicate interface.

The monomials are exact grid permutations with unit phases. The mix is
`y += (P+2Q)x`, has operator norm at most three in its source argument,
and has its literal subtraction inverse. Every native call has its
literal inverse. Reading the complete reverse port shows precisely the
reverse operation order. Induction gives exact return of both arbitrary
stored banks in either composition order, whenever range checks permit
the execution. No bank is assumed zero or discarded.

Let X and Y be the Euclidean norms of the two entry banks and put
`D=f*h*sqrt(N)/2`. The full port bounds are

| Direction | Output x norm | Output y norm |
| --- | --- | --- |
| forward, k calls | at most X+D | at most Y+3X+(k+2)D |
| reverse, k calls | at most X+D | at most Y+3X+(k-1)D |

For forward execution, x gains at most D before it is used in the mix.
The mix gives at most `Y+3(X+D)`. The y bank then has k-1 native calls,
which add at most `(k-1)D`; the exact wrappers add zero. For reverse
execution, y first has k-1 inverse calls, then subtracts the mix formed
from the still-unmodified entry x. The inverse x call comes last. The
same argument with fewer completed layers bounds every native prefix.
These are complete sufficient envelopes, not optimal port constants.

The coordinate approximation contract is the one used by the source.
Each layer has maximum complex-coordinate error `h/sqrt(2)`, and its
ideal infinity norm is sqrt(2). Thus
`delta_(j+1)<=sqrt(2)*delta_j+h/sqrt(2)`, from delta_0=0, yields
`delta_f<2*2^(f/2)*h`. The unchanged source tolerance requests are

| Port | q |
| --- | --- |
| two-call forward | P+f+3 |
| three-call forward | P+ceil(3f/2)+3 |
| two-call reverse | P+ceil(f/2)+2 |
| three-call reverse | P+f+2 |

The grid `g=q+ceil(f/2)+1` therefore retains complete error at most
`2^-P`, using the source's port propagation proof. This package checks
that premise on actual paid inputs and against a full rational oracle;
it does not claim first discovery or independent proof of the retained
port budgets. The exact source proof is in predecessor/PROOF.md.
Initial quantization remains a separate charge.

## 5. Word range and the complete direct cost

Stored data use signed w-bit integers. The pair routine checks all four
inputs and all four outputs. It returns only after all output checks pass.
On valid inputs, let M bound their absolute components. Each sum or
difference is at most 2M. Doubled half-grid coordinates and the ring radius
are at most 4M. The cycle index is less than 4r, hence at most 16M.
The branch formulas use only fixed small multiples, additions, signs,
parities and exact halves. All their intermediate magnitudes are at most
`16M+2`. Signed `w+6` auxiliary bits suffice for w>=2. There is no
variable divisor, growing table, matching search or real arithmetic in
the runtime provider. The verifier checks the no-variable-division property.

The source data width
`w=H+g+2f+ceil(f/2)+9`, for H>=0, remains sufficient under its entry
magnitude and grid premises. The stored-output growth and coordinate
error bound are the same as in the source proof. The new auxiliary words
have the stated extra six bits; they are not charged as free storage.
This is not a claim that the old eight-word scratch allocation is reused.
Whole-call range failure can occur after earlier pair writes; no atomic
whole-call failure contract is asserted. Successful inverse return is the
contract tested and proved above.

A complete k-call port performs exactly `k*f*N/2` pairs, including zero
pairs. Every pair has a bounded fixed number of full-word operations,
eight stored range checks, four real reads and four real writes. Its
constant number of auxiliary words can be initialized and cleared in
O(w) bit work. The direct work bound includes these steps, parity/side
selection and output range decisions; there is no unit-cost lookup oracle.

The unchanged source mix adds 4N real additions and 2N shifts. It retains
two monomial mix terms and four full wrapper passes for k=2, or six for
k=3. Each pass builds its address/phase records in O(fN) word work,
executes the permutation and clears its owned route/visited state. Both
dirty banks and all route data remain in the storage accounting.

Thus the complete indexed reference has O(fN) bounded-word work,
`O(fN*(w+f))` bit work and `O(N*(w+f))` stored bits. These are constructive
asymptotic bounds, not an exact tape-transition invoice or a measured
speedup. A fixed multitape graph, recursive exchange rate, physical routing,
compiler stock, owned backing and selected caller admission remain open.

## 6. Verification, excluded identities and credit

The exact receipt checks all pair inputs in [-4,4]^4 in both directions,
all four Gaussian phases, conjugate inverse, swap, translation and radial
bounds. Complete signed-width domains 2, 3 and 4 check success exactly
when final outputs fit. Complete ring walks check the direct formula and
its reflection/half-turn symmetries. The sharpness sequence includes
4097-bit inputs. Actual complete native calls and all four port directions
for f=1,2,3 check every paid cut, full rational error, radial envelopes,
fiber sums, phase covariance and exact dirty return. Aligned inputs agree
with the source port and ideal oracle.

The fourth power and tensor-stage commutation fail on retained examples.
Wrong inverse stage order also fails. The square/fourth identities of
some earlier providers are not preserved, and the actual ports do not use
them. The negative provider must use the stated inverse and reversed
stage order. No ideal native graph identity is inferred from this local
bijection. Invalid formats, wrong axes, aliased banks and real signed
output overflow are rejection controls.

The new result is the parity-selected sharp radial provider and its
complete source-bound radial/port contract. Generic phase restoration,
reversible rounding and this port interface are prior work.
[CREDITS.md](CREDITS.md) gives exact source roles, including CubeJerry's
distinct four-axis phase construction and the retained native lineage.
Prepared by Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. Independent human and formal-kernel review are unclaimed.
The selected frontier and all five selected assumptions remain unchanged.
