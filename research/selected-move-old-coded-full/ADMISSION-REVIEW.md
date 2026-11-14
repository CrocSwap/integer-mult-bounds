# Independent review: unchanged full MOVE admission

Status: numerical/source derivation, complete static composition audit and
final proof prose review pass. Reviewed final `PROOF.md` SHA256
`4dda913877963bebd0fc61ce04f14a594a78bdd781154d9a92961cd528e830d0`.
Prepared for @CubeJerry with OpenAI assistance. This is a complementary
mathematical and port audit, not independent human or formal proof acceptance.

## Fixed sources and scope

Canonical main: `e54523517d0f03e58352e647c403a5af3e525a57`.
The exact selected event is zero-based 24472,
`["MOVE",415,3,99,false]`, from frame 3 = `[]` to frame 99 = `[239]`.
The 350722-byte selected archive has SHA256
`2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883`.

The unchanged same-width 31-tape full core is retained from
CrocSwap/integer-mult-bounds#7563 at CubeJerry commit
`5dd80e8ab9c989336b5e448e14147c2ba29da89b`:

* `inputs/core/move.py`: SHA256
  `42e4293ab59ffa1c99e0dbbd5fded0833a5d726e1e794f0f263ae9a4686587a5`;
* `inputs/core/reference/RECIPE.json`: SHA256
  `96fadb44c3316be93c6c02f50cd2c841a9541d67b98fd94fc47b73fa64dd404c`;
* its exact graph: 82813 locations, SHA256 of `repr(code)`
  `14f38b15157a9c9cd2828861f6904701a29b1e27507a7e43d60030e1ae4d9238`.

The pending OLD23 join is
`worker-c/wave3/research/selected-move-old-coded-full/compose.py`, initially
SHA256 `572e2c5de3b210ef34ed8f26f51fb1a2a6b4306fc355f93368504ad79308561c`.
Its OLD23 bridge is the already published CubeJerry commit
`30497f40d89f2a137a4bc31a4fee1229b9af1440`, bridge SHA256
`119b69594a2a33550eec9b6e083db8f496c3fb3d9c1214b6703d687a0a662eba`.

The numerical premise is the selected application review section 5,
SHA256 `4501502c2ceb9759b20372435fe4beb51082c5a5e2910c1fd5dbe6edca415055`,
and its already established every-prefix deduction in
CrocSwap/integer-mult-bounds#7578, head
`e9b6d75397e3553af77bab81d5816e4b8708a501`, retained proof SHA256
`ceb2cd71379644ab2c4f8e36489996436a11eb345a275d21ea487de59264e308`.
This review extends the location of that admission boundary to before the
actual right monomial. It does not claim a new Clifford denominator theorem.

## Precise admission corollary before the complete right monomial

Let the supplied OLD23 field faithfully represent the ideal selected current
field before this MOVE, with its complete root factor and all spectator
coordinates retained. Assume the selected invariant

`z = sum c U x`,

where each U is a Gaussian-dyadic Clifford on that same complete n-bit root,
the original real and imaginary coordinates are on grid `2^-p` and have
absolute value strictly below `2^h`, exterior coefficient denominator height
is at most `178t`, exterior Gaussian coefficient mass is at most
`2*2^(161t)`, and `356t<n`. Keep the selected per-native-call 1125 source
route and its exterior coefficients; do not insert interior rounding.
Assume `p,h>=0`, `9f<=n`, `f<=cutoff`, common grid `2^-(p+n)`, and stored
width `w=p+h+2n+3`. All physical OLD23, ownership and transport premises
remain separate from these numerical premises.

Then every numerical guard in the unchanged full MOVE succeeds. In
particular the right phase, right binary map, right offset, every low-bit-
first central C-axis prefix, left phase and final binary map are all
admissible on the same width and quantum, with no extra `2^f` input reserve.

Proof: each completed monomial prefix and each subset of central C axes is
itself a Gaussian-dyadic Clifford on the same complete factor. Its product
with each U absorbs into U and changes neither the exterior denominator
height nor the coefficient mass. The retained complete-root row theorem
therefore gives at most

`p+ceil(n/2)+178t`

fractional bits and absolute real/imaginary magnitude strictly below

`2^(h+ceil((n+1)/2)+161t+1)`.

The integer depth condition implies `ceil(n/2)+178t<=n`. Also
`ceil((n+1)/2)+161t+1<=n+2`: for n even use `178t<n/2`, and for n odd use
`178t<=floor(n/2)`; `161t<=178t`. Thus the component is exactly on the
common grid and its stored numerator has absolute value strictly below
`2^(p+h+2n+2)=2^(w-1)`.

The strict symmetric inequality excludes the most-negative signed endpoint.
Every Gaussian-unit phase swaps components and/or negates them; these
operations therefore fit even when a negation is performed before a swap.
During partial phase writes the components are either old or new bounded
components. Complete C-axis outputs are integral by the same ideal-prefix
grid theorem, and fit the same signed width. Its four-term numerator is
formed in `w+2` signed bits, within the retained `w+26` temporary allowance.
Induction over the actual literal factors proves successful exact execution;
the ideal prefixes are defined algebraically before literal exactness is
deduced. There is no circular numerical-exactness premise.

This is stronger than endpoint integrality and is not admission of every
integer packet having representable complete endpoints. The following
controls delimit the difference.

## Explicit phase-negation boundary witness

Use `f=r=P=S=1`, `w=2`, `cutoff>=1`. In packed native tuple notation place
the sole nonzero value `-2+0i` at

`(a0,...,a8)=(1,0,0,0,0,0,0,1,0)`.

This is one-column mask 129 but MSB-first physical address 258. The exact
right recipe gives phase `1+3+2=6 mod4`, hence multiplies this value by -1.
It must form +2, outside the 2-bit signed interval [-2,1], and the unchanged
literal phase rejects. The complete MOVE nevertheless has two nonzero
Gaussian outputs with components in {-1,1}. Both entrance and final
endpoints fit the ordinary signed interval and are integral.

This is a valid boundary counterexample to endpoint-only admission of the
unwrapped core. It is not reachable under the stated strict common-root
bound, and it is not an input to the stronger symmetric-input promise of
the endpoint wrapper in #7563.

## Endpoint integrality does not imply integral central prefixes

For `f=2`, put real ones at central entrance a0=0 and a0=3, all other
native coordinates zero. The four central values are `[1,0,0,1]`. After
the first low-bit C axis they are

`[(1+i)/2,(1-i)/2,(1-i)/2,(1+i)/2]`;

after both C axes they are `[0,1,1,0]`. Apply the inverse exact right
monomial to obtain the complete native entrance, and the exact left
monomial to obtain the complete endpoint. Both consist only of Gaussian
units and zeros, so `w=2` fits even the symmetric interval [-1,1], but the
unchanged core rejects the nonintegral first prefix. This is the existing
#7578 endpoint obstruction transported through the actual full monomials,
not a newly claimed obstruction theorem.

The widening/scaling endpoint wrapper shipped alongside #7563 is distinct
from its unchanged `compile_move()` core. Its extra scale changes this
example's intermediate grid. The once-rounded wrapper in #7568 has yet
another numerical contract and cannot be substituted into the selected
exact-interior route without a separate precision and error argument.

## Independent source oracle and exact reproduction

`check_admission.py` imports no retained verifier, Clifford producer or
factor helper. For the unlowered source frame `[239]`, it completes that
direction to a binary basis by explicit enumeration of its span, computes
the inverse bijection by enumerating the fixed 512 addresses, and evaluates
the canonical-frame conjugation directly. With chart G and its source
quadratic Q, the frame is

`D_Q P_G C_0 P_G^-1 D_Q^*`.

Its basis column at x has the unshifted coefficient `(1+i)/2` and the
coefficient `((1-i)/2)i^(q(x XOR 239)-q(x))` at `x XOR 239`. This oracle
is independent of the actual right/left lowering. All 512 one-column
basis columns agree with the lowered composition. Four additional
two-column basis controls check the tensor and repeated phase convention.
A changed right absolute phase and a changed source direction are both
detected. The numerical witnesses above are checked exactly over Gaussian
Fractions. A bounded scan of 6948 `(n,t)` pairs, `1<=n<=2048`, corroborates
the universal inequalities; it is not their proof.

The full archive was independently re-extracted using the pinned compressed
and canonical JSON hashes, including the actual event and complete frames.
No archive-wide native replay was run.

Executed command, from the shared run root:

```sh
python3 -I -W error -B worker-b/wave3/check_admission.py \
  --package worker-c/wave3/research/selected-move-old-coded-full \
  --archive worker-b/selected-native.json.gz \
  --output worker-b/wave3/ADMISSION-CONTROLS.json
```

Expected marker: `PASS_FULL_MOVE_ADMISSION_CONTROLS`.
The archive argument is optional when only the retained compact witness is
available; the receipt distinguishes that case explicitly.

## Literal port, guard and ownership audit

`check_composition.py` independently compares all 88816 emitted instructions
with the two exact predecessor graphs. The 6003 bridge locations differ
only at its one PACKED halt; all 82813 child locations preserve their
source-symbol tests, writes, unit moves and fixed branch destinations under
the explicit port map

`HEADER0 -> GAMMA3`, `DATA1 -> PACK2`, `private t>=2 -> t+41`.

The resulting ports are 0 through 71. Child-private ports are exactly the
29 distinct owners 43 through 71, disjoint from all 43 bridge roles. The
child never writes OLD0, CONTEXT1 or GAMMA3. No child port reaches the
bridge's suspended geometry guides. Every branch target lies within the
fixed graph, and every action uses the four-symbol alphabet and a unit
move. The one child halt returns to the original bridge EXIT. Its
successful terminal instruction and the bridge PACKED instruction are
replaced by unit-cost jumps; no extra host operation is inserted.

The graph SHA256 is
`5cd132ae9c4234dbd7a0a591186d8506e9ea50658b7c5b0f4d7e0da8e49fc403`.
Omitting the child call and aliasing HEADER to DATA both fail the independent
all-instruction comparison. This is static literal-simulation evidence,
not another execution of the author's tape interpreter.

The guard boundary is substantive. All 43 bridge roles have the inherited
permanent LEFT at origin-1; each of the 29 new core roles instead enters
blank at origin-1. Core WORK and TRACE install and retire their own guards.
Its 27 reusable module roles do the same within each successful factor.
The protected bridge PACK/GAMMA guards are public guards for the core and
remain untouched. All heads at the call seam are at first body cells,
not on LEFT. Preserved heads, bridge guides, packed cardinality and same
width supply the exact EXIT precondition after the core succeeds. Entry
guards, full clean capacity, disjoint physical ownership and prior
historical backing remain supplied premises; an object-identity check
cannot establish those properties for arbitrary external wrappers.

The unchanged source core's transaction protects its public PACK until
its last commit; the surrounding bridge additionally protects OLD through
inverse preparation. Rejection before successful return preserves OLD and
CONTEXT values, but it need not restore heads/private banks. No retry or
global rollback follows from this theorem.

Executed command:

```sh
python3 -I -W error -B worker-b/wave3/check_composition.py \
  --package worker-c/wave3/research/selected-move-old-coded-full \
  --output worker-b/wave3/COMPOSITION-CONTROLS.json
```

Expected marker: `PASS_FULL_MOVE_LITERAL_COMPOSITION_AUDIT`.

## Complete bound calculation

Let `V_o` be the original coded payload length, `V_p` the packed length,
E the OLD23 header length and `E_gamma` the six-Gamma length. The retained
bridge and core give respectively

`T_bridge <= 2^20((9f+1)V_o+E+1)`,

`T_core <= 2^24(f V_p+E_gamma+1)`,

and historical increments `64(V_o+E+1)` and
`1024(V_p+E_gamma+1)`.

The exact volume relation is `V_o/V_p=3(b+1)/b>3`.
Also `E_gamma<=V_p+E`. To prove this without omitting large binary cutoff
cost, the Gamma cutoff code has at most the length of its old canonical
code. For the other five positive values, `length(Gamma(x))<=2x-1`.
Writing `q=P S r b>=2`, the four-value sum is at most `q+3`, so these
five Gamma codes have total length at most `2f+2q+1`, below
`V_p=2q*2^(9f)` for every f>=1. Thus cutoff contributes its encoded length,
never its numerical value.

Consequently the complete joined time is bounded by

`[10*2^20+(2/3)*2^24] f V_o + [2^20+2^24](E+1)`

which is below `2^25(f V_o+E+1)`. Historical increments sum to at most

`[64+(2/3)*1024]V_o + [64+1024](E+1)`

which is below `2048(V_o+E+1)`. All 72 owners' earlier history belongs in
the entry term. Retiring a role does not release visited capacity. The
proof deliberately sums even overlapping per-owner spans, so its double
counting is safe. The private guard cells and head returns are already
part of the retained complete bills.

This establishes `O(f V_o+E)` for the direct local service. At a fixed
base-case cutoff it is linear with a cutoff-dependent constant. No
accelerated nonleaf tariff, recurrence or provider selected rate follows.
The cutoff test is in the central leaf after the right factors; the
success theorem requires f<=cutoff and makes no early-rejection cost claim.

## Review disposition and remaining boundaries

No mathematical, source-order, port, guard or complete-bound defect was
found in the frozen `compose.py` and its stated success domain. This review
does not duplicate the author's full tape replays; it supplies an
independent source-frame oracle, exact numerical admission proof, two
boundary counterexamples, every-instruction translation check and separate
cost inequalities.

The final proof's two domains, strict phase margin, wrapper comparison,
encoded-cutoff charge, exact source/spectator action and cofinal direct-
controller lower-bound scope agree with this review. Its executed fixture
claims remain the author's primary evidence; this review did not rerun
those expensive tape fixtures. The general theorem does not infer legal
selected stock, actual root execution or physical caller acquisition from
their synthetic OLD23 test packets.

The result proves no caller field acquisition, global source dispatcher,
stock admission, recursive child theorem, foundational assumption removal,
or new kappa. Source-bound operand415 and frames3->99 describe the admitted
local occurrence; they do not locate that operand in an enclosing native
execution or advance its external frame ledger. The full selected
multiplication theorem remains conditional.
