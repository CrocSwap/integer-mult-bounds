# Common-head audit of one actual mixed root

## Result and exact scope

This audit checks root `('mixed',0)` in the 1,024-call schedule of PR7756,
scientific commit `9e051455757d1cc86b822e52e42e1e1c98ead417`. It checks its
sixteen physical visits, exact coordinate and phase maps, both directions
of each native boundary, and the added charge for both ordinary views.

The root has fourteen A contacts at port 0, with physical head 11, and two
B contacts at port 15, with physical head 81. Its head is the same canonical
axis `e0` after each return. All 128 body axes are spectators of the added
view maps. The root has sixty main-array visits. It requires 120 additional
permutations and 120 additional translations. The retained source bill
includes these occurrences on both entry and return.

No new kappa or whole-caller acceptance is claimed. The signed root word,
source graph construction, full native operator, numerical grids, scalar
service bounds, recursive compiler and complete price remain dependencies
or separate obligations. The selected frontier and five assumptions do
not change.

## Exact root and coordinate convention

The retained graph constructor produces SHA-256
`c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84`.
Its unchanged scheduler and binding code give global root offset 89,216.
The sixteen visits are physical calls 2 through 17. Calls 9 and 10 use
port 15; the other fourteen use port 0. Body color is `call mod16`, so
this root uses every one of the sixteen body blocks exactly once.

Coordinates are binary vectors with 137 axes. An integer `2^j` denotes
axis `e_j`. Axes zero through eight are central. Color `c` has the eight
axes from `9+8c` through `16+8c`.

For a physical head `q`, the columns of `P` are `q` followed by the eight
pinned central basis vectors. Extend `P` by the identity on the remaining
128 axes. The numerical coordinate permutation sends the delta at `x` to
the delta at `P x`, with coefficient one. Its inverse is the transpose,
because the columns are orthonormal over the binary field.

| Port / kind | Head | Nine columns of P | Entry translation | Return translation |
| --- | ---: | --- | ---: | ---: |
| 0 / A | 11 | 11,13,14,7,16,32,64,128,256 | 15 | 15 |
| 15 / B | 81 | 81,82,4,8,67,32,19,128,256 | 83 | 83 |

For these two actual bases, `P` equals its transpose and fixes its
translation. Thus each complete affine view is an involution. This is a
fact about these two maps, not a requirement on every possible port.
The checker tests every central coordinate `x` and every spectator axis.

## Absolute phases and the same head

For a Fourier character `k`, write `[a,k]` for binary dot product, taken
as zero or one. The directional Clifford has phase exponent `[a,k]`
modulo four. A phase expression is a sum of integer multiples of these
parities. Let `F(k)` be the sum for the nine original central axes.
The required entry translation is the unique vector `tau` with

```text
F(k) - sum_j [P e_j,k] = 2[tau,k]  (mod4).
```

The reverse computation uses `P^-1` and gives `P^-1 tau`. The checker
derives both independently and verifies the ordered inverse. It repeats
the equation for the Y frame, whose phase is `F-[q,k]` locally and
`F-[e0,k]` canonically. The same translations work for X and Y.
All four directed endpoint equations are checked on all 512 central
characters for both heads: 4,096 exact checks.

Conjugation by the numerical permutation takes `C(e0)` to `C(q)`.
Translations commute with these Fourier-diagonal operators. Therefore
the full affine view has the same conjugation action on the head.
The checker tests exponents `1,-1,2` on all 512 central characters for
each port: 3,072 signed-head checks. The squared head is the branch used
by the source normalizer. This verifies its head direction, not the
normalizer's numerical division or storage cost.

Every added view fixes all body axes. After return, the head is `e0`
again, independent of the next visit's port. The order of body colors is
`2,3,...,15,0,1`; it never changes the common head.

## Every native boundary, with a quantified phase certificate

At color `c`, the native route exchanges the eight pinned central basis
vectors with the current eight body axes. It fixes `q` and every other
axis. The checker reconstructs all 137 columns and verifies the route
inverse and every spectator.

The four boundary pairs are the X input, Y input, X output and Y output
frames. They retain the source's cumulative spectator frames and original
absolute phase convention. For each of the sixteen visits, the checker
derives the four forward shifts and the four inverse shifts. All 64
forward shifts agree with the retained source contact routine; all
inverse shifts equal the transformed forward shifts. `RESULT.json`
contains all four offsets at every visit.

These are 128 exact phase identities, not arbitrary sampled characters.
For binary coordinates, a parity has the expansion

```text
[a,k] = sum_{j in a} k_j - 2*sum_{i<j in a} k_i*k_j  (mod4).
```

Terms of degree three or more have coefficients divisible by four.
Thus every phase difference here has degree at most two modulo four.
The new checker obtains its constant, linear and quadratic coefficients
from its values at zero, the 137 single-axis characters and the 9,316
two-axis characters. Each identity uses 9,454 exact evaluations. Even
linear coefficients determine a unique translation. Zero quadratic
coefficients prove the equation for all `2^137` characters. Equality
at zero fixes the constant phase. Fourier characters span the whole
array space, so these equations apply to arbitrary numerical arrays.

The source checker constructs the degree-two coefficients directly.
The new checker derives them by finite differences of literal parity
values. Both paths share the exact source basis and boundary convention;
that shared dependency is explicit.

## Both ordinary views are charged

The fourteen A visits each bind four distinct main arrays. The two B
visits each bind two. This gives `14*4+2*2 = 60` owner visits. Each has
one permutation and one translation at entry, and another of each at
return. The certificate lists all 240 distinct occurrences, with call,
local slot, owner, side and operation. These are added ordinary views;
they do not replace the existing native contact adapters or their charges.

The first root has the same physical visits in the bounded 32-call batch.
The audit reads all 398,944 emitted records of that batch and projects
this root's sixteen ordered `ENTER,NATIVE,EXIT` triples. All 48 records
have the expected owners. This is an emitter and view-order check, not
execution or symbolic verification of the complete emitted caller.

For the complete 1,024-call source invoice, the added view allocation is
819,200 permutations plus 819,200 translations. The unchanged ordinary
budget function reproduces the retained receipt on the retained native
counts. Its separate view term is `4*400*1024 = 1,638,400` array traversals.
The source uses its default map allowance at ambient 153, with multiplier
`4*154^2`, although the mixed caller has ambient 137. This is conservative
for that parameter. This audit verifies the occurrence allocation; it
does not reprove the elementary implementation cost of each traversal
or every other term in the ordinary budget.

## Controls, provenance and limits

Omitting either entry or return translation fails on central character
one for both ports: the phase error is two modulo four. Reusing head 11
for the B contact fails on character two. Removing the return records
fails the required sixteen view triples. These are explicit bounded
controls, not claims that every conceivable malformed caller is rejected.

All 42 retained files have exact Git-blob and SHA-256 pins checked before
import. The graph, scheduler, binding and emitter are source dependencies.
No retained code is modified. The separate geometry engine runs before
the source phase cross-checks. Source tariff replay uses author-supplied
native counts; it is not another native physical replay.

The full 32-edit witness, all-column native physical replay, symbolic root
program, full 1,024-call instruction stream, other roots, interval price
gate, selected cold replay, Lean and Docker were not verified here.
Separate implementation does not imply independent human or formal-kernel
acceptance. Whole-caller admission remains open.
