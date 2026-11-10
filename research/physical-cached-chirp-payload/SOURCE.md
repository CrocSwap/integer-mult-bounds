# Certified source tables and actual-input precision for one cached chirp pass

Canonical source: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Contribution by @CubeJerry, with substantial OpenAI assistance.
**No new κ.** This is the numerical/source contract for the accompanying
physical pointwise pass. It does not assemble a Fourier transform, Gaussian
resampling operation, integer multiplication algorithm, or the five global
assumptions.

## 1. Source, predecessor boundary, and interface

CrocSwap/integer-mult-bounds#4100, retained as
`research/unconditional-batched-crt/PROOF.md`, specifies

\[
 a(x)=\prod_{i=0}^{d-1}a_i(x_i),\qquad
 a_i(x_i)=\exp(-\pi\mathrm i s_i x_i^2/t_i).
\]

Every `t_i=2^{ell_i}>=2`, every `s_i` is odd, and axis zero is
fastest and has largest radix. The source uses distinct positive prime slopes;
the producer permits arbitrary odd signed slopes, reduced modulo `2t_i`.
It preserves the association between an axis, its radix and its slope.
Evenness of `t_i` makes the chirp periodic with period `t_i`. The first
`t_0` complex entries already form one source polynomial record: no layout
conversion is hidden in the source contract.

CrocSwap/integer-mult-bounds#4325 proves the cached-suffix numerical and
odometer lemmas and leaves physical multiplier/payload interleaving open.
CrocSwap/integer-mult-bounds#5987 proves the stronger largest-fastest table
travel bound. Neither theorem is claimed anew. The contribution combines
the physical consumer with a finite, certified producer of its actual phase
banks and an allocation for the supplied data radius. It does not require
deciding exact irrational floors at grid boundaries.

The unchanged elementary interval source is
`research/certified-gaussian-recovery/intervals.py`, Git blob
`91d458865aa026bdf0d59653a4ecbfe3a178ecbc`, SHA256
`159d2a7d32a8cc7c8f56632a8ef127308b984a0a6753c9d6bdccacc6e7d6d4df`
at the canonical base. Its Machin identity, Taylor enclosures and inward
quantizer are inherited, not new analytic lemmas. The source retains
Mason Hale's authorship and Apache-2.0 notice.

`prepare(radices, slopes, R, tau, oracle=I, incoming_precision=f_in)`
returns immutable integer tables and a plan. The integer `R>=1` bounds
the modulus of **each actual input coefficient**; `tau>=0` requests an
absolute component-l1 error at most `2^-tau`; `f_in>=0` is a minimum grid
precision. The radius is a mathematical admission premise, not a property
checked by the physical caller. The producer never reads payload values.
The interval module must be authenticated by the source loader.

All phases and payload records use the common grid `h=2^-f`. Physical
tables contain an axis page marker, then `t_i` pairs `(Re,Im)` of signed
`W`-bit two's-complement words in increasing `x_i`, then an end marker.
Shape fields contain `ell_i` zero bits and an axis marker. Shape length
is `sum_i(ell_i+1)`; table payload length is `2W sum_i t_i`; framing adds
`2d` symbols. The physical loader pays literal serialization of the returned
integers. A numerical receipt does not replace source authentication.

## 2. Certified entries without an exact-floor premise

Set `q=2f+32`, `u=2^-q` and compute exactly

\[
 j=(-s_i x_i^2)\bmod(2t_i).
\]

If `4j` is divisible by `2t_i`, emit the exact quarter root `1,i,-1,-i`.
In particular every `a_i(0)` is exactly one. Otherwise call the pinned
`root_of_unity(j,2t_i,q)` and quantize each component toward zero from
its **inner interval endpoint**. For a positive enclosure `[l,v]` use
`h floor(l/h)`; for a negative enclosure use `-h floor(-v/h)`; for a
zero-crossing enclosure use zero.

Each output component has the true component's sign or is zero, and its
magnitude is at most the true component's magnitude. Thus the stored point
lies in the closed unit disk. An enclosure of width at most `h` gives
component error at most `2h`: one ulp for truncating the inner endpoint
and one for the enclosure width. This is a two-ulp statement; simply
flooring a lower endpoint does not establish a one-ulp error from the
unknown true value. The producer checks exact endpoint distances and the
squared unit-disk inequality using integers.

Here is a conservative width bound for the **pinned implementation**.
Its Machin enclosure has width at most `3u`: the two alternating
remainders are below `2^-(q+16)` and endpoint rounding adds less than
`2u`. After reduction to the nearest quarter root, the rational multiplier
of pi is in `[-1/4,1/4]`. Its dyadic enclosure has width at most `u`;
the product interval has width at most `8u`. For `q>=36`, its endpoints
have magnitude below `4/5`. Its squared interval consequently has
absolute upper bound at most `2/3` and width at most `16u`.

If a Taylor-term enclosure has magnitude at most one and width `v`,
one multiply and division by the integer denominator (at least two)
produces width at most `v/3+11u`. Every term therefore has width at
most `17u`; the magnitude bound remains at most one. Sine's initial
width is at most `8u`; cosine's is zero. The stopping test fires by
term `q`, since its factorial remainder is then smaller than `2^-(q+4)`.
Same-grid additions of interval endpoints are exact; the final remainder
widening adds `2u`. Every returned component has width at most

\[
 (17q+10)2^{-q}\le 2^{-f}\qquad(q=2f+32,\quad f\ge2).
\]

Quarter rotations preserve width. Reduced arguments remain bounded even
when `ell_i` is much larger than `f`; exact modular reduction and rational
argument acquisition are still paid. The runtime width check rejects an
invalid or accidentally weakened enclosure instead of accepting it under
an unjustified error claim.

## 3. Cached expressions and the actual data radius

Let `F_d(x)=1` and, recursively, let
`F_i(x)=fl(tilde a_i(x_i)*F_(i+1)(x))`, where `fl` truncates each
completed component toward zero. The actual cached state at coordinate
`x` equals this **fresh rounded suffix expression**, not only its ideal
analogue. At initialization all phases and caches are exactly one. If an
odometer increment changes axes `0,...,j`, higher coordinates and caches
are unchanged, so cached `F_(j+1)` is already the fresh expression at
the new coordinate. The consumer recomputes axes `j,...,0` in descending
order using that suffix. Induction proves the invariant after each update.
There is no feedback from an overwritten cache into itself and no error
accumulation over earlier tensor records.

Section2 gives `|tilde a_i-a_i|<=2 sqrt(2)h` and `|tilde a_i|<=1`.
The arithmetic child forms every complex product from four exact integer
products, then truncates **once per completed component**. A truncation
changes a complex number by at most `sqrt(2)h` and cannot increase its
modulus. Every cached suffix is therefore in the unit disk. The last
factor times terminal cache one is grid-exact. The inherited suffix
induction counts d table errors and d-1 nontrivial product errors:

\[
 |\widetilde a(x)-a(x)|\le(3d-1)\sqrt2\,h.               \tag{1}
\]

For an actual supplied coefficient `z` with `|z|<=R`, the final rounded
product satisfies

\[
 |\operatorname{fl}(z\widetilde a)-za|
 \le[R(3d-1)+1]\sqrt2\,h,
\qquad
 \|\operatorname{fl}(z\widetilde a)-za\|_1
 \le2[R(3d-1)+1]h.                                    \tag{2}
\]

Conjugation preserves both norms and the grid, so the same theorem holds
for the conjugate pass. Completed output has modulus at most `R`.
A component-l1 input promise `<=R` suffices since it implies the modulus
promise; the output is not claimed to preserve that stronger l1 radius.
The number `T=product_i t_i` of distinct pointwise outputs does not enter
the error bound. The physical shape and carrier checks do not verify the
mathematical admission promise `|z|<=R`.

The producer chooses

\[
 f=\max\{f_{in},2,\tau+
 \lceil\log_2(2[R(3d-1)+1])\rceil\},                    \tag{3}
\]

which makes (2) at most `2^-tau`, and chooses a scalar carrier

\[
 W=\max\{f+\lceil\log_2(R+1)\rceil+2,
          \max_i\ell_i+2,\lceil\log_2(d+1)\rceil+2\}.   \tag{4}
\]

This covers completed payload/cache records and local encoded fields.
The unchanged arithmetic child still allocates and pays its wider exact
product and sum scratch: a product of two W-bit integers is not claimed
to fit W bits. Input records must already use the chosen common grid.
A caller's data-grid conversion is a separate paid operation; the
input-independent producer does not perform or conceal it.

## 4. Fully charged source preparation and retained storage

Let `m=sum_i t_i`. Let `B>=16` dominate `q`, `W`, `max ell_i`,
the binary input lengths of all slopes, `log_2(d+1)`, `log_2(R+1)`,
`tau` and `f_in`. Source preparation starts from these encoded parameters,
not a free phase oracle. Signed slope reduction and each modular square
use schoolbook bounded-integer arithmetic. Each phase calls at most one
of the inherited elementary routines, with at most `O(B)` Taylor terms.

The Machin rational partial sums have numerator/denominator length at
most `O(B^2)`: they contain `O(B)` denominators, each with `O(B)`
bits, and a common product denominator suffices. The factorial and
rational remainder tests have polynomial bit length, at most `O(B^2)`.
The sine/cosine working intervals stay on one q-bit grid; their term
recurrences use `O(B)`-bit dyadic endpoints and integer denominators.
Elementary addition, multiplication, division and Euclidean gcd on these
encoded integers give a deliberately loose `O(B^12)` bit-work allowance
per phase and `O(B^4)` transient storage. These are sufficient upper
bounds, not benchmark claims or unit-cost rational arithmetic.

To remove any free indexed-memory interpretation of the Python preparer,
retain an encoded store containing its output, current cache entries,
parameters and temporary integers. With no prior cache history its size
is bounded by `O((m+d)B+B^4)` bits. A root-cache entry includes its
phase/denominator/precision key and its two endpoint intervals; it is not
treated as a costless table lookup. Let `H_prev` count **all** retained
data from previous preparations, including historical `pi_interval` and
`root_of_unity` caches and prior per-role high-water backing. Use

\[
 D=O(H_{prev}+(m+d)B+B^4).
\]

Sequentially scanning the encoded store for each source access gives the
explicit conservative fixed-tape simulation bound

\[
 C_{setup}=O((m+d)B^{12}D+Wm+\sum_i\ell_i+d),\qquad
 S_{setup}=O(D).                                      \tag{5}
\]

The last terms pay table/shape serialization. This is an existence bill
for the finite elementary setup, not a claim that Python dictionaries
are literal tapes or that this setup has the same measured receipt as
the online consumer. A fresh authenticated interval module namespace
sets the historical source-cache term to zero; if an existing namespace
or owner is reused, its retained history remains in (5). Old caches are
not silently discarded. The receipt's own serialization/hash occupies
and scans `O(mB)` additional bits, already covered by the bound.

For the actual #4100 source regime, `d=poly(p)`,
`ell_i=Theta(p^{1-epsilon})=o(p)`, and positive slopes have
`O(ell_i)` bits. Conditional on the caller's admitted `R<=2^{O(p)}`
and requested `tau,f_in=O(p)`, (3)-(4) give `f,q,W,B=O(p)`.
Fresh setup (5) is then `d*2^{O(ell)} poly(p)=2^{o(p)}`;
the squaring of `m` caused by the deliberately slow sequential simulation
is absorbed into `2^{O(ell)}` and a polynomial in p. The source
proof already budgets setup at this scale. The preparation contains
no factor `T*d` from reading online data. These deductions invoke the
actual p/ell/d/radius bands; they are not asserted for arbitrary huge
radices, slopes, requested precision or unbounded retained histories.

The accompanying physical proof prices cached products, phase-page travel,
payload multiplication and restoration. Adding (5) gives

\[
 O(T M(W)+TW+d^2W+C_{setup}),                          \tag{6}
\]

where `M(W)` is the full cost of the unchanged real-word arithmetic
service, including its own premises and scratch. This source proof
neither substitutes unit-cost word multiplication nor discharges those
premises. The retained online data/table/cache space and child backing
remain additive to (5).

## 5. Reviewable evidence and limits

The source controls include exact quadrant handling, signed slopes,
modulo-equivalent slopes, small grids with larger radix fields, rejection
of non-dyadic/even-slope/misordered parameters, a deliberately wide
enclosure, a false point outside the unit disk, and an interval whose
inner-endpoint floor really needs more than one ulp of error allowance.
They are exact integer/rational checks. They do not prove a universal
analytic theorem by finite replay; that theorem is Sections2-4.

The independent `dyadic_chirp_oracle.py` uses repeated positive half-angle
square roots with directed integer-isqrt bounds and complex powering,
with no Machin/Taylor reuse. `chirp_source_review.py` passed normally and
with `-I -O` on five families: 342 phase entries and their 342 literal
conjugates, including the actual distinct-prime fixture
`(t_0,t_1)=(8,4)`, `(s_0,s_1)=(7,3)`, radices up to 256 and a signed
100-bit slope. Six decisive mutations reject sign, denominator, odd-slope,
coordinate-square, unit-disk and axis/slope-association errors. The oracle
has SHA256 `e115bc53870a620431a9a2616ca1a3ff4967caf369296cfb575959e34636f4b6`;
its adapter has SHA256
`a34f4516aed6f6986fa522f6da83592f3c2bfa6584d2ae16e50818869f9ba87f`.
The independent oracle's soundness is analytic, but its finite refinement
limit can return inconclusive; universal termination is not claimed.
For radius one and target exponent ten, the actual-source fixture has
`f=14`, `W=17`, six exact-quarter entries and six interval entries;
the allocated component-l1 payload error is `3/4096<2^-10`.
The physical verifier separately checks actual payloads, conjugation,
cache carries, preservation, cleanup and exact rounded-stage behavior.
The actual-source 32-record fixture completed both forward and conjugate
passes with 264 exact scalar products each. Its direct full-angle payload
check does not read produced tables or cache states; that additional
check does share the pinned elementary interval library. The half-angle
source check above supplies the distinct elementary numerical mechanism.
All source checks use the frozen authenticated file hashes.

This is one integrated source-bound diagonal pass. It does not supply
the remaining transform stages, an outer precision induction, a new
integer-multiplication exponent, or a new κ.
