# Affine sector access: continuation record

This record joins the local access construction and its limit. The
construction gives exact access to one maximal affine part of the
correlated phase sector at every tensor width. The limit shows that a
literal affine Haar tree cannot extend the same geometric scan bound
to the complete positive-density sector. Neither result supplies the
remaining centre-information controller or a new kappa value.

## 1. What can now be done

Let the Fourier address have `n` rows and `lambda` columns. Put

    k = n ceil(lambda/2) - (lambda mod 2).

The chosen affine sector has dimension
`n floor(lambda/2) + (lambda mod 2)`. This is the sharp affine bound
for `n>=2`. Its signed translation projector is `Pi`.

The code in `affine-projector-stream/STREAM.md`, with its amendment
and `ODD-WIDTH.md`, implements

    (x,y) -> (x,y+Pi x)

on two arbitrary physical fields. It restores the source and retains
the target complement. A fixed address map is followed by a signed
Haar code. Only the active half is refined; every detail is retained
for the inverse. The two fields retain exactly their original combined
record count. The work tapes are cleared before the next owner call.
There is no extra owner family and no extra complex native child.

The selected bits, unselected slot bits, row indices, compact fields,
spectators, and polynomial indices all have explicit roles in the
layout. The address maps use the pinned compact-control primitives.
The complete layer has time

    O(V ((e log p)^tau+1)),  e=n lambda,  0<tau<1.

This is an asymptotic bound from the source primitives. It is not a
new explicit finite implementation constant.

At even width every completed odd-axis frame acts on the leaf by a
known Gaussian unit. At odd width one bit remains, and the exact leaf
action is a Gaussian unit times one of `I,C_u,X_u,C_u^-1`. This is an
actual two-point coefficient computation on the compressed leaf. It
is not an unpaid full-field native line call. Extra outer address
permutations still need their own binding.

The equal-frame shear needs `k` added fractional bits and one added
magnitude bit. The typed odd-width shear needs `k+1` fractional bits
and two magnitude bits. All operations are exact on that enlarged
dyadic grid. The recursive guard result is conditional on the stated
dependency-path envelope; a changed internal controller must establish
that envelope again.

## 2. The combined projected quarter turn

`affine-projector-stream/ONE-PASS-TURN.md` combines three projector
shears without three complete encodes. Encode both fields once, apply
the three leaf ADDs, then decode once. At equal frames the result is

    x'=(I-Pi)x-Pi y,
    y'=(I-Pi)y+Pi x.

It has fourth power identity and preserves every arbitrary complement.
Its precision is `k` fractional bits and two magnitude bits. For
different admitted completed frames, use the exact leaf map
`(a,b)->(-D^-1 b,D a)`, where `D=O_t O_s^-1`. At odd width a direct
two-point implementation needs `k+1` fractional bits. Do not infer
this guard from three separately rounded kernels.

## 3. Actual owner cuts and their limit

`affine-projector-stream/OWNER-BINDING.md` names two old Y families,
112 and 113. They are both at frame I before the first selected
provider event, and both at common F73 after the final all-live cover
correction. Source-domain separately confirmed these source types.
The boundary conjugation

    S^-1 F_all S = F_all

is legal for the projector shear or quarter turn because the projector
commutes with the completed frame. It keeps all old owner and helper
input values arbitrary. This uses the inherited exact all-role
provider contract. The owner-binding producer check is not an
independent full replay of the supplier. The stream reviews do not
claim otherwise.

This gives a concrete complete-boundary use of the layer. It does not
make a different internal canonical cut legal. It does not restore a
changed centre-query history, and it does not reduce the native rank
bill by itself.

## 4. What affine coverage proves

The independent rigidity proof is in
`review-gauss/maximal-affine-sectors/RIGIDITY.md`. For `n>=3`, every
globally maximal affine piece has a common row code. At even width
it is `(a+W)^n`, with W self-dual and a+W of constant weight modulo
four. At odd width it also has the common all-ones direction. The
restriction `n>=3` is necessary for this classification.

`affine-sector-cover/COVERAGE.md` and its amendment give a sharper
pointwise statement at every fixed phase residue. For a matrix X,
set `a=x_1`, `W_0=span(x_i+a)`, and

    E=omega^perp,
    q_a(w)=wt(w)/2+a.w modulo 2 on E.

Then X has a common odd-row phase d exactly when
`wt(a)=d modulo 4`, `W_0` is contained in E, and `q_a` vanishes on
W_0. The proof extends W_0 to a sharp totally singular code. It gives
an optimal product piece through every point and exact extension
counts. The binary construction is polynomial when the Fourier
address is explicit.

This is not a physical Fourier-address read. It does not price a
choice among the product pieces. In particular, it does not make an
exponential list of separate affine projector calls cheap.

## 5. The accepted scan limit

`affine-sector-cover/SPLIT-LIMIT.md` permits branch-dependent affine
tests, invertible affine coordinate changes, grouped Haar blocks,
and unequal leaf codimensions. Every rejected or detail branch is
retained. Each literal split is charged for the records it processes.

If accepted leaves partition S, the forward split record count is

    T = sum_(all leaves l) |A_l| depth_l.

If no affine subset of S has codimension below k, then

    T >= k |S| = k rank(Pi_S).

This identity is independent of the order and basis of the binary
tests. It also holds after literal unequal-depth blocks are grouped.
An arbitrary direct block algorithm is not charged as one free scan.

For the all-odd sector S_n, its exact density tends to

    2^-((n-1)(n+2)/2).

This is positive at fixed n. Thus an exact full-sector projector in
this literal fixed-format class needs `Omega(lambda V)` split work.
At n=73 the limiting density is `2^-2700`, and the exact density is
within one percent from lambda=152. The constant is very small; this
is not a useful numerical lower bound for the present finite budget.
The n=73 sector is sufficient for common native phase. It is not a
claim that this is the maximal sector of the actual supplier.

Sharing prefixes removes exponential enumeration in this model: a
full binary tree has at most `n lambda 2^(n lambda)` processed records.
It does not preserve the single-piece geometric scan bound.

The limit leaves these mechanisms open: non-affine blocks, overlap
and cancellation between codes, a query-only circuit that does not
form the full projector, productive native children, and a different
priced coefficient format. It is not a general linear-circuit or
centre-query lower bound. These are the useful next directions; more
classification without an access mechanism is not the current task.

## 6. Verification and preservation

`AFFINE-ACCESS-PINS.json` pins the producer files and separate review
receipts used by this record. The stream, odd-width, affine-cover,
and split-limit reviews used independent mathematics and checks.
The one-pass-turn review is a proof review; it does not rerun the
producer. The owner cut binding has the narrower status in section 3.
No complete new supplier, recursive finite invoice, or kappa result
is claimed.

The producer checks passed before this handoff. Only this handoff and
its pin file were added when the results were collected. Frozen proof,
check, and review bytes were preserved.

All work remains local. No PR, push, or commit was made. Before any
eventual PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
