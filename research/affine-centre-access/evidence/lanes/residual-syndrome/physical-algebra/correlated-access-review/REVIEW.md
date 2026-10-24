# Independent review of the affine access theorem

Status: accepted for Sections 2 and 3 and their stated limits.

The source is `portable-source-codes/correlated-access-20261015/ACCESS.md`,
SHA256 `a5a91cdc4deed08aa15693aedbcc01f48186859f8902acdb864aa74fb6feba4d`.
The source files were not changed. The review did not import or run the
producer checker. The CSS and Bell review is a separate check.

## The affine bound

Let an affine set `a+V` lie in the odd-constant sector. The coordinate
lines are odd, so all row weights agree modulo four on that set.
For each coordinate, the second difference of binary weight is
`2 u.v mod 4`, including a nonzero offset. Thus the forms pulled back
from all row projections are one form `B` on `V`.

Let `r=rank B` and `K=rad B`. For a row projection `p_i`, its kernel
is in `K`. The surjection from `V` to `W_i=p_i(V)` therefore identifies
the quotient form of `B` with the restricted dot form on `W_i`.
In particular, `rank(W_i)=r` in the bilinear-form sense, and
`p_i(K)=rad(W_i)`. If the latter space has dimension `s_i`, then
`dim W_i=r+s_i`. Its radical is contained in its orthogonal complement
in the nondegenerate ambient space. Hence `r+2s_i<=lambda`.

The joint row projection is injective on all of `V`, and thus on `K`.
It follows that

    dim V <= r + sum_i s_i <= r+n floor((lambda-r)/2).

For `n>=2`, the maximum is `n floor(lambda/2)+(lambda mod 2)`.
This includes odd `lambda`, where rank one of the common form gives
the extra dimension. If the phase is fixed, each row weight is constant,
so `B=0` and the bound is `n floor(lambda/2)`.

The affine pair code in the source attains both bounds for every `n>=2`
and every positive width. Each pair has exactly one nonzero bit in every
row. An odd sum of rows still has exactly one nonzero bit in each pair.
At odd width the common last bit adds one free dimension and changes
the common weight by one. Fixing that bit gives the fixed-phase bound.

The union bound uses cardinalities in the full `n lambda`-bit Fourier
address space. The independent correlated-sector review proves
`delta_152>=2^-2700` for `n=73`. A largest affine part at that width has
fraction `2^-5548`. At least `2^2848` parts are needed to cover the full
sufficient sector. The bound also applies to a spanning family of
subspaces with those supports. For a positive sum of support projectors,
evaluation at each outside basis vector prevents cancellation.
It does not apply to signed cancellations or to a general circuit.

The independent checker enumerates every affine subspace in the five
listed ambient spaces, of dimension at most six. It checks the radical
images directly for every accepted direction, both dimension bounds,
and equality examples for `n=2,3,4` and widths one through six.
These checks support the proof; they do not replace its quantifiers.

## The signed projector graph

On a physical coset `p+H`, write `epsilon_j=(-1)^(a.(j+p))`.
The first reduction forms `sum_j epsilon_j x_j` in the pivot.
The broadcast therefore adds

    2^-k epsilon_i sum_j epsilon_j x_j

to target coordinate `i`. This is exactly the corresponding row of
`2^-k sum_h (-1)^(a.h) X_h`. The pivot scale and the reverse reduction
restore every source coordinate, for arbitrary initial source and target.
The inverse changes only the sign of the target additions.

Each selected physical coset has a one-dimensional image spanned by
its signed constant vector. Thus the rank is the number `c` of selected
cosets. The Fourier projector for the full physical support has rank
`N/2^k`. Restricting the physical support to a union of `H`-cosets
commutes with the translation projector.

The graph has `(s-c)+s+(s-c)=3s-2c` complex unit additions and two shifts
of length `k` for each pivot. The stated arithmetic convention gives
`24s+(4k-16)c`. The bound by `25N` for full support is valid, including
`k=0`. The prefix pivot magnitude is at most `2^k ||x||_infinity`.
An exact implementation needs `k` added fractional bits for the divided
pivot and target. The source claim is exact only with those bits retained;
it is not a rounding analysis or a finite record-width admission.

Three such shears act as `(x,y)->(y,-x)` on the projected range and as
the identity on its complement. They have fourth power identity on all
inputs. No source baseline is discarded.

## The actual phase identity

For the pair code, the Fourier columns satisfy
`chi_(2j)+chi_(2j-1)=omega_n`. Every orthogonal address map fixes
`omega_n`, so it preserves this affine set. The projector is Fourier
diagonal and commutes with complete native translation kernels. Each
odd native line is `i^k` on the range, where `lambda=2k`.

The cover sum absorbs right translations of the cover index. The scalar
matrix `R` commutes with the same payload projector on each field.
These facts justify the ordered identity

    A Pi G'_s = (1-i^k) R A Pi.

This does not treat an arbitrary internal canonical frame as an
orthogonal completed frame. It also does not identify a commuting CSS
projector with this affine projector.

## Separate continuation

A new signed reduction and expansion stream is written in
`physical-algebra/affine-projector-stream/`. It uses an intact source
and owned work tapes. It does not change the source packet or its
original pivot graph. The new stream requires its own layout and guard
proof. Neither result supplies access to a positive-fraction sector or
a complete centre-information controller.

Research and independent review: OpenAI Codex under the user's direction.
No independent human review is claimed. No PR, commit, or push was made.
