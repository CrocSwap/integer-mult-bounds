# Physical prefix codes and the current twiddle

There is a nonmonomial code family which passes through the actual
remaining forward transform without a decoder. The code acts only on
frequency bits that the forward DIF procedure has already written. It
must act on those bits in the physical record coordinates. A scalar
matrix in a moving owner chart is not sufficient.

The same property holds for a changed opposite procedure defined below.
The record layout, layer calls, cost order, and error bound of that
procedure are unchanged. This note does not supply a centre-saving
native layer or a recursively closed encoded child.

The main application boundary is precise. The selected supplier's
charts act only on the current selected bit offsets. A code on those
bits is not yet a code on completed bits: it must first pass the current
twiddle. An exact criterion below permits a changed monomial twiddle
and rejects an individual odd-line code and the paired code `T=QA`.
It does not reject every complete encoded supplier.

## Exact commutation

Use the named slots and forward schedule in Section 06 of the pinned
source from [OUTER-ENCODING-INTERFACE.md](OUTER-ENCODING-INTERFACE.md).
After some complete rounds, let `P` be any fixed set of slots which
already contain frequency bits. Let `Z` contain the remaining slots
and the polynomial coefficient payload. In these logical slot
coordinates the rest of the forward computation is

```text
I_P tensor T_Z.
```

To prove this statement, inspect one subsequent round. Its butterfly
changes one unprocessed slot in each participating axis. It does not
change or read `P`. Its twiddle exponent is

```text
-sum_i (2r/u_i) b_i k_i modulo 2r.
```

Here `b_i` is the bit that this round has just written and `k_i` uses
only the lower, still unprocessed slots of axis `i`. No earlier branch
bit enters the exponent. Thus the butterfly and the twiddle both act
as the identity on `P`. Induction proves the factorization. Physical
layout permutations preserve the statement if the descriptor carries
the named slots with them.

Consequently, for any linear map `A` on the `P` index,

```text
(A tensor I_Z)(I_P tensor T_Z)
    = (I_P tensor T_Z)(A tensor I_Z).
```

The equality holds over the polynomial coefficient ring, with arbitrary
data in all rows. It does not need a zero cache or independent values
in different rows. If `A` is invertible, it can remain until the end of
the forward transform and then be decoded. It need not preserve the
coordinatewise product, since decoding occurs before that product.

At most two initial parallel rounds give a completed frequency bit on
every axis: one possible extra round on the long axes, then one common
round. Any fixed number `h` of these bits is then available when `d`
is large enough. These initial rounds can be evaluated by individual
butterfly kernels in `O(Vd)` time. The selected exact margin
`1-epsilon-kappa>0` permits this startup cost. Moving the fixed `h`
named bits to a physical prefix and restoring that prefix costs
`O(Vh)=O(V)` by the elementary stream moves.

## Scalar role codes are already cheap

A fixed scalar matrix on a fixed number of role streams is not a
new recursive interface. If those output streams have the same full
frame and the inverse has a fixed scalar word, apply that word at the
end of each invocation. Its `O(V)` work is already a node overhead.
There is no need to carry this code through the outer transform.

The following fusion statement records what a physical prefix allows.
It does not turn a fixed scalar role code into a structural advance.

## Fuse a finite alphabet of fixed-bank codes

Fix `h` and put `w=2^h`. Let each subsequent layer leave a code `A_j`
on these same `h` completed slots. Assume all `A_j` belong to a fixed
finite alphabet in `GL_w(Z[i,1/2])`, and that the inverse of each
alphabet element is supplied over that ring. The codes can differ
between layers and need not commute with each other. They must be
fixed by the program, not by the input values.

Since each code commutes with every later exact forward round, the
complete exact endpoint is

```text
(A_last ... A_2 A_1 tensor I) T_forward.
```

There are `ell=Theta(p/d)` rounds. A common power of two clears all
denominators in the alphabet and its inverses. Matrix multiplication
then shows that every entry of the product and its inverse has
numerator bit length and denominator exponent `O(ell)`. For example,
if all row sums of absolute values are at most `M`, the product row
sum is at most `M^ell`. The fixed matrix dimension contributes only
a fixed factor to this bound.

Generate the fused inverse before the data scan. This uses polynomial
work in `ell`, which the complete polynomial-record stream absorbs.
Apply that inverse with a fixed number of row buffers. A direct
shift-and-add multiplication by an `O(ell)`-bit fixed coefficient
costs `O(p ell)` per `Theta(p)`-bit component. There are a fixed
number `w^2` of coefficients. Thus the terminal decoder costs

```text
O(V ell)=O(V p^(1-epsilon+o(1))).
```

It needs `O(ell)` extra exact grid and integer bits. An approximate
implementation also needs `O(ell)` extra precision for the product's
inverse norm. These bits are `o(p)` and do not change the record-width
exponent. They must be included in the new finite precision proof.
The selected condition `epsilon-kappa>0` makes this decoder smaller
than the target `V p^(1-kappa)` by a strict power. This uses the
dimension margin, rather than the different terminal tensor margin.

The fused matrices need not be added as new physical field families.
They are fixed controller coefficients. The finite row buffers are
ordinary work streams in the outer machine and are charged in the
linear scans. They give no productive supplier credit. A proposed
native layer must still establish its own private and borrowed-state
contract.

The input values in the `w` rows remain arbitrary. If a fixed role
count is not a power of two, embed its matrix as a block in `w`
rows and act as the identity on the other rows. This does not assert
that the existing recursive row allocation can use only these `h`
bits. It gives an endpoint type for a complete layer. Recursive
children and padding remain separate construction obligations.

## Interface test for a proposed supplier

A proposed whole-layer supplier can use this theorem if its physical
data map, in the outer layout, is

```text
(A_j on the fixed completed prefix) tensor H_current
```

and its other fields satisfy the required arbitrary-state contract.
It must prove that `A_j` has no action on the active address bits,
lower unprocessed bits, or polynomial payload. Merely writing its
logical query operators as a matrix over a regular cover does not
prove this condition. A change from owner coordinates back to the
outer coordinates can act on the active payload, and the twiddle
depends on those coordinates.

The current archive endpoint has active chart routes and residual
line frames. No physical completed-prefix factorization has been
proved for it. This theorem does not remove those obligations.

The opposite procedure in the existing source is reverse arithmetic.
Its completed lower input bits can enter later twiddle exponents.
The forward proof therefore does not apply to that schedule as written.
The next section gives a different schedule with the same endpoint and
the same physical slot order. It permits completed-bit codes in both
directions. A new encoded supplier must still pass its current twiddle.

## An opposite procedure with completed slots

For one axis of length `t=2^a`, let `B=B_t` reverse the `a` address
bits. The plus-sign DIF procedure in its usual high-to-low slot order
has exact operator `B F_t^+`. This follows from the proof of synthetic
DIF in Section 06 with all root exponents negated.

Now run that procedure with the physical bit names reversed. This is
a change of names in its gates, not an executed record permutation.
Its exact matrix in the original physical address order is

```text
B (B F_t^+) B = F_t^+ B = F_t^+ B^-1.
```

That is exactly the required opposite consumer of the stored forward
order. At physical stage `h=0,1,...,a-1`, its operations are

```text
H0 on physical slot h;
multiply the record by y^E,
E = (2r/2^(a-h)) x_h sum_(v=h+1)^(a-1) 2^(a-1-v) x_v mod 2r.
```

The selected slot increases from low to high, as in the retained
opposite schedule. After the butterfly, `x_h` is the new branch bit.
The displayed sum contains only unprocessed higher physical slots.
No previously completed lower slot occurs. Thus any code on completed
slots commutes with every later exact round.

For several axes, add the displayed exponents over participating axes.
Different-axis butterflies and twiddles commute by the same argument
as in Section 06. Long axes have `a_i=ell`, short axes have
`a_i=ell-1`. At stage `h`, include exactly those axes with `h<a_i`
and use their own coefficient `2r/2^(a_i-h)`. The layer still applies
the same `H0` to the same physical slots. It does not require the
current recursive lengths of the axes to agree. The complete logical
operator is `F_boldsymbol_t^+ B^-1`.

Keep the source layout `L` and its inverse. The named-slot descriptor
places each operation at the same physical slot as before. The new
opposite executes the conjugated logical procedure on the stored
layout, then applies `L^-1`. Its full operator is therefore
`F_boldsymbol_t^+ B^-1 L^-1`, as required. No additional bit reversal
or layout change occurs.

The new exponent can be computed from the existing named-slot table
and address counter in `poly(p)` time per polynomial record. Reversing
the significance of a listed tail changes that polynomial work only.
The source proves that the record's `Theta(rp)` bits absorb this work.
Multiplication by `y^E` uses the same two-piece coefficient split,
signed move, and merge. It costs `O(rp)` per record.

The layer cost, number of layers, prefix-bit work, chunk movement,
and final layout restoration are unchanged. A prefix round still
uses the same individual butterfly kernels. Every completed round
is a contraction. A signed coefficient permutation commutes with
`Q_p`, so the new sequence returns `Q_p(J_E H z)` in each round.
It has one truncation and error less than `sqrt(2) 2^-p` per round,
as does the source schedule. The disk and final convolution error
bounds are unchanged. This is an all-size opposite-transform
construction, not a claim about an encoded supplier.

After one common opposite round, one physical bit on every axis is
completed. After at most two forward rounds, the same is true in the
forward direction. Individual evaluation of these initial rounds
costs `O(Vd)`. Moving any `O(d)` of their named bits to a prefix and
restoring them also costs `O(Vd)`. The selected strict margin
`1-epsilon-kappa>0` admits this cost. These bits can supply a fixed
positive fraction of the current layer dimension as past coordinates.
Their use as a native catalyst needs a separate supplier construction.

## A whole completed axis supplies every recursive row digit

There is also a row allocation which works in either direction without
changing the opposite schedule. Complete one whole synthetic axis
first. Transform factors on distinct axes commute, so this gives the
same exact full transform in either direction. The axis has
`a=ell` or `ell-1` bits. All later operations on other axes act as
the identity on its index.

Individual butterflies and monomials on this axis cost `O(V ell)`.
Moving its `a` bits into one row prefix and restoring them costs the
same order by the elementary digit-move lemma. The new index may be
any arbitrary row value; the argument uses no independence assumption.
If the axis and the remaining axes are truncated separately after
each round, there are at most `2ell` truncations rather than `ell`.
The transform error bound then has an extra factor at most two.
One extra fractional bit covers this factor. This is a new precision
allowance; the original finite guard is not silently reused. One can
instead evaluate the first axis exactly on the `2^(-p-a)` grid and
truncate once at its end, since `a=O(ell)=o(p)` and all its rounds
are contractions. Neither option changes the time exponent.

For a finite supplier with row radix `W`, dimension divisor `m`, and
depth at most `k0=ceil(log_m d)`, it is sufficient that

```text
a >= ceil(k0 log_2 W).
```

The right side is `O(log d)`. The left side is
`Theta(p/d)=p^(1-epsilon+o(1))`, so the inequality holds for all
sufficiently large `p`. Add zero rows to the next multiple of
`W^k0`; the volume increases by less than two. Split the row field
by `u=Wg+w` at each recursive node, as in Section 05. Every resulting
role retains the full remaining active suffix. The original child
volume and fixed-tape stack arguments therefore still apply.

This padding is done once. If an encoded procedure mixes original and
padded rows, retain the padded rows until its code has been inverted.
Only then discard the rows which are again zero. Ordinary unchanged
layers leave them zero at each layer boundary. Physical work fields
required by the supplier retain their original contracts and costs;
the row argument creates no extra productive credit.

The added time is `O(V ell)=O(V p^(1-epsilon+o(1)))`. The selected
exact certificate gives `epsilon-kappa>99/100`, so this is strictly
below `V p^(1-kappa)`. No numerical threshold is asserted. Thus row
placement itself is not an obstruction to a whole-layer past-space
interface. The current twiddle and recursive child type remain
separate conditions.

## Exact criterion at the current twiddle

Fix one common round in which each selected axis has current length
at least four. Let `w` be a row-prefix index, `b` the current branch
bits, and `k` the still unprocessed bits. Suppose an invertible code
`E` acts on `(w,b)`, has complex scalar matrix entries, and fixes `k`
and the polynomial coefficient suffix. This includes the scalar,
cover, and complex-line operations under consideration here.

For fixed `k`, let `D(k)` be the actual recordwise twiddle. To carry
`E` past the round, the replacement twiddle must be

```text
D'(k) = E D(k) E^-1.
```

There is a recordwise monomial `D'(k)` for every `k` if and only if
each output row of `E` has nonzero entries in only one branch address
`b`. Different input row-prefix values at that same `b` may mix
densely. Invertibility then assigns exactly the full input-block rank
to each branch address. The new exponent is the old exponent at that
unique input branch address.

For necessity, set one lower bit of axis `i` to one and all other
lower bits to zero. This gives a diagonal `D_i` with entries `1` and
`z_i=y^(-2r/u_i)`, according to `b_i`. From `E D_i=D'_i E`, a
nonzero complex entry in an output row determines its diagonal
`D'_i` entry. A row containing both values of `b_i` would force
`1=z_i`, which is false in `C[y]/(y^r+1)`. Do this for every axis.
For sufficiency, each row has one branch address, so that branch's
twiddle factor can be factored out of the entire row.

Even an additional record permutation does not relax this criterion.
Indeed `D_i` satisfies `(D_i-I)(D_i-z_i I)=0`. Its conjugate does too.
In a monomial matrix, a permutation cycle of length at least three
would put nonzero entries of this polynomial in three different
positions of a row. A two-cycle would have off-diagonal term
`-(1+z_i)D'_i`. The coefficient `1+z_i` is a unit: `z_i` has
power-of-two order at least four and `z_i^(u_i/2)=-1`, so a finite
geometric sum gives its inverse with denominator two. Both cycle
cases are impossible. Thus the conjugate is diagonal. This statement
concerns record permutations with invertible polynomial monomial
weights, not arbitrary extra arithmetic.

This is a restriction on changing only the monomial twiddle. A new
native or arithmetic twiddle algorithm is outside its scope. Axes
at current length two have no lower bits and are also outside the
necessity statement.

## The actual odd line and paired code do not pass this test

For an actual port `q`, put `C_q=aI+bX_q`, where
`a=(1+i)/2` and `b=(1-i)/2`. Each row uses both branch addresses
`x` and `x+q`. Pick any coordinate in the support of `q` and a
nonterminal common round in the retained layout, where these are
current selected coordinates. The criterion excludes a recordwise
replacement twiddle for `C_q` or `C_q^-1`.

The conversion from `C^tensor(D)` to `H0^tensor(D)` is
`b^D S_D C^tensor(D) S_D`, as stated in Section 05. The diagonal
`S_D` changes the two coefficients by nonzero phases and does not
change their branch support. The same test therefore applies after
the actual butterfly conversion. At a cover vertex `g`, replace
`q` by the nonzero vector `gq`; some current coordinate still differs.

For the paired candidate, write

```text
T = [[0,Q],[Q^-1,0]],       Q=C_q^tensor(lambda),       T^2=I.
```

Its two block rows still mix branch addresses. In particular,

```text
T diag(D,D) T = diag(Q D Q^-1, Q^-1 D Q).
```

For a one-line factor with `D=diag(1,t)` and `t^2=-1`, both entries
in each row of either conjugate are nonzero units. The identity
`(1-t)(1+t)=2` proves this in the polynomial ring. In `lambda`
independent copies, one column has `2^lambda` nonzero record
dependencies. Row-prefix permutations and the `S_D` phases cannot
remove them. Involutivity by itself does not give a cheap past code.

The associated `A=[[0,I],[Q^2,0]]` is a record permutation and does
pass the criterion, with a changed address exponent. No cited native
packet is claimed to return the complete endpoint `A` alone. Also,
this test on one factor does not exclude cancellation in a complete
encoded endpoint. If a new construction places the full support of
every relevant `q` in already completed coordinates, these line maps
commute with the current twiddle. Such a construction is outside the
obstruction. Its actual cover, routes, and recursive child dimensions
must satisfy that placement; changing a name does not establish it.

## Recursive children remain a separate boundary

Using old certified children inside a changed top-level layer does
not improve the recursive exponent. A replacement child must also
compose inside its parent word. If the old transition from frame `U`
to frame `V` is `F`, and the proposed field codes are `E_U,E_V`, the
required physical transition is

```text
E_V F E_U^-1.
```

It is not in general the child map `E_child F`. The parent scalar
accesses must have equal codes on their source and target fields,
and each routed frame transition must have the displayed type and
a complete native cost. A code on address bits completed only by
the *outer* round need not commute with these intervening parent
operations. The whole-axis row allocation does not prove this
condition. A fixed scalar role-only code with common full endpoints
can instead be removed by the cheap per-invocation inverse described
above; that special case needs no new recursion theorem.

## Exact check and scope

`check_completed_prefix_codes.py` uses no producer imports. It reads
the pinned Sections 02, 05, 06, selected certificate, and assembly. It constructs an
actual two-axis length-eight DIF example over the exact field `F_97`,
with `y` of order sixteen and `2^-1` as the butterfly scale. It checks
every matrix entry for all remaining rounds and a nonmonomial code
on the two completed high slots. It also checks two noncommuting
codes inserted at different rounds and both inverse orders. The new
opposite is compared with all entries of `F_plus B^-1` for axis
lengths `(8,8)` and `(8,4)`, including completed-slot commutators.
The checker tests all 57,344 local spatial columns for the 112 actual
ports, both paired orientations, and the actual diagonal `H0` phases.
It also tests all 262,144 addresses of a small selected-offset chart
and its inverse, including untouched chunk bits and the third slot.
The finite
example verifies the implementation convention; the all-size
commutation and cost claims follow from the proof above.

Run:

```text
python3 -I -O -B check_completed_prefix_codes.py
```

Expected first line:

```text
PASS_COMPLETED_PREFIX_CODES
```

The result gives an exact opposite schedule and a usable completed
row prefix. It also gives a precise current-twiddle obstruction for
the odd-line and paired-code proposals. It does not claim that an
existing changed native word has a recursively closed encoded
endpoint, or that a full new multiplication construction has been
completed. It was prepared with OpenAI Codex assistance.
