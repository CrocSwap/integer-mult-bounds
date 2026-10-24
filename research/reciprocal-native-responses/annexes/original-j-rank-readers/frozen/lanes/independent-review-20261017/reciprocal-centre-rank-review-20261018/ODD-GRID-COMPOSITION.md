# A common odd grid for unfinished parent operations

The reciprocal E and G maps have coefficients with denominator 13. This
does not require the recursive native children to have rational endpoint
maps. E and G can be local operations in a parent word. The theorem below
states the condition under which a depth bound still pays for all such
denominators. A rational local endpoint is not, by that fact alone, an
admitted completed recursive child.

## Coefficient theorem

Put A=Z[i,1/2]. Represent a complete finite machine state by its numeric
fields, including all arbitrary borrowed fields. Add zero and private
fields as needed. Maps in this statement are exact linear maps on that
full state. Permutations, copies, clears of owned private fields, and
Gaussian-dyadic native operations have matrices over A.

Consider a finite recursive computation with these hypotheses:

1. At most L invocations are active at the same time. Count the root and
   the current leaf in L.
2. Each invocation has a finite parent word. In that word, replace each
   completed recursive child by its full endpoint map. Each such map has
   coefficients in A, on every permitted data and arbitrary helper input.
3. Apart from child calls, the local factors have coefficients in
   13^-h A, with h a nonnegative integer. The sum of these h values in one
   parent word is at most D. This bound also covers an operation stopped
   at any scalar prefix. A stronger proved bound on all local prefixes
   can be used instead of this sum.
4. All initial numeric values are dyadic. A separate binary guard and
   magnitude bound are valid for this new complete word.

Then every global prefix matrix has entries in

    13^(-D L) A.                                           (1)

Different bounds D_j at different active levels give the more precise
bound 13^(-sum_j D_j) A. An initial odd denominator height h_0 adds h_0
to the exponent. The bound depends on the active path, not on the total
number of completed child calls.

To prove (1), stop the execution at any event. Contract each completed
child call to its exact full endpoint matrix over A. The remaining
unfinished invocations form one active path. At each level, the executed
part of its parent word adds at most D to the denominator height. In a
product of matrices, the height is at most the sum of the heights of the
factors. Adding entries cannot increase this bound. Thus the total is at
most D L. This proof uses no commutation between different local maps.

A completed child may receive values with denominator 13 from its parent.
An A-linear endpoint does not add a new factor of 13 to those values.
Its own unfinished prefixes are covered by the next active level. The
claim therefore remains valid on rational inputs from an unfinished
parent, provided its exact full-column endpoint identity is valid there.
An exact linear identity over A has that scalar extension. A rounded or
input-restricted implementation needs a separate argument.

## Exact encoded execution

Let H=D L. Choose the binary unit 2^-P from a guard for the complete new
word. Use the common grid

    2^-P 13^-H Z[i].                                       (2)

At the outer boundary, multiply the padded integer numerator of every
physical numeric stream by 13^H. Include arbitrary borrowed data and
helpers. Private zeros remain zero. Do not scale addresses, tags, or
descriptors. Any nonzero numeric literal must use the same encoding.
The present linear words need only zero literals.

The initial states here are arbitrary dyadic values with this root
encoding. They are not arbitrary integer numerators on the finest grid.
That stronger claim is false: the finest-grid numerator one cannot be
divided exactly by 13.

Every algebraic prefix lies on (2), by (1) and the separate binary guard.
At a literal division by 13, the algebraic state after the operation
therefore also has an integer numerator. Its input numerator is divisible
by 13. Induction over the literal events shows that the integer scans
implement the rational word exactly. This is not an approximation claim.
The scalar root encoding commutes with every exact linear native map.

At the outer return, suppose the complete intended endpoint on all
physical roles has coefficients in A. Every final numerator is then
divisible by 13^H. Exact unscaling restores the original encoding of all
numeric fields, including the stipulated borrowed-state output. Final
truncation can occur after this unscaling under the separate original
error proof. No new rounding error or tolerance is introduced by (2).
Without a dyadic root endpoint, this unscaling conclusion does not follow.

The endpoint hypothesis is essential for a bound based only on depth.
Three consecutive completed children with endpoint x/13 can create
denominator height three at depth two. More such calls give unbounded
height at the same depth. If a changed controller exposes E or G as a
completed recursive provider with this rational endpoint, it needs a
different denominator theorem. Calling these maps local parent operations
does not by itself prove that the complete parent endpoint is dyadic.

## Signed scan and price

For a w-bit signed numerator N, start at its low bit with carry c=0.
For each input bit b, write a and update c by

    a=(b-c) mod 2,   c'=(c+13a-b)/2.                        (3)

The carry stays in {0,...,12}. After w bits, summing the bit equations
gives 13 Q_unsigned=N_unsigned+2^w c_final. If s_N and s_Q are the
two sign bits, the signed quotient is exact if and only if

    c_final=13 s_Q-s_N.                                    (4)

The quotient of an exactly divisible signed input cannot overflow its
input width. Formula (3) needs finite control and one scan; it does not
need another numeric array. Multiplication uses output bit
(13b+c) mod 2 and next carry floor((13b+c)/2). Its final signed test is
c_final=13s_N-s_output. The allocated magnitude guard prevents overflow.

These scans have O(w) arithmetic-head cost. The retained record and
descriptor work has a separate O(w) cost per record. The prior common-grid
packet gives the same finite-control construction for division by three;
changing the fixed carry set to thirteen states does not change the scan
order. This statement does not assign an old scalar-primitive price to a
new odd division.

If w is the guarded numerator width before the common odd scale, the
extra width is at most

    ceil(H log2(13)) <= 4H.                                (5)

This is an odd-denominator overhead. It is in addition to the binary and
magnitude guard for the changed word. For S real numeric records, root
conversion and final unscaling by repeated fixed scans cost

    O(S H (w+H)).                                          (6)

Each local real division by 13 costs O(w+H). All numeric streams that
need conversion belong in S, including arbitrary borrowed storage.
Descriptor, owner, routing, and hosting costs are still part of the
complete construction. Equations (5) and (6) do not pay for an omitted
controller or a native frame transition.

For a fixed finite parent word, D is constant. If its recursion depth is
O(log N), the extra width is O(log N). If its guarded word width is at
least proportional to H and V=S w, the outer conversion cost is O(V H).
An exponent claim also needs the full recurrence and its strict slack.
This theorem supplies neither a new moment bound nor a kappa value.

## Application to the actual reciprocal family

The actual coordinate projection P gives

    E=I+K((12/13)P-I)R,
    G=I+K((12/13)(I-P)-I)R.

Each is a fixed rational local map. Each has an endpoint denominator of
height at most one. The actual source has ||R||_infinity=56 and
||K||_infinity=1. Thus each endpoint has row-sum norm at most 57.
These endpoint facts do not bound every native implementation prefix.
One may use the literal number of /13 factors as a conservative D once
the complete word, its helpers, and its legal input states are checked.

The native H1 and H8 children can keep their original exact dyadic maps.
The parent can use E and G between such calls under hypotheses 1--4.
For a complete controller, it remains necessary to prove its ordered
endpoint, every borrowed-state output, the binary and magnitude guard,
and its actual recursive bill. In particular, EG=I in one scalar chart
does not prove cancellation of physical maps that contain port-dependent
q operators or changes of chart.

## Validation and prior work

`check_grid.py` exhausts all signed inputs at widths one through fourteen
for both fixed scans. It checks five nested test trees on all eight
independent input columns using integer numerators only. Every completed
child is a dyadic shear. Rational reciprocal centre scales surround two
child calls. The tree checks all divisions, every child endpoint, the
active-path bound, and final unscaling. Separate controls reject an
unscaled finest-grid input, repeated rational child endpoints, and early
unscaling. These tests support the general proof above. They are not a
native supplier or controller implementation.

The retained common odd-grid source is
`../../interface-proof/rational-decoder/sources/notes/stopped-product-complex.tex`,
SHA256 `4738089103a4b263b3b0ef458f5ef35519c696f1ea871ae79e508d3720f5870a`.
The local predecessor is
`../odd-grid-a8-20261017/A8-ODD-GRID.md`, SHA256
`e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01`.
The prior peer review is
`../../bridge-review-20261017/odd-grid-a8-review-20261017/REVIEW.md`,
SHA256 `0eee1c869ba6c1c5e75075bc9dbae3324468a27a6b0dd45cd16e4f7973f9eb05`.
This note states the same method for 13 and for explicit rational parent
operations. It does not claim to introduce common odd grids.

This work used OpenAI Codex under the user's direction. It remains local.
No publication is authorized.
