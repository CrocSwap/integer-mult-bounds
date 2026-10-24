# Independent review of the odd-width stream

Result: accept `ODD-WIDTH.md` in its stated local scope. Its proof hash
is `5971697aea4c7681234f96bec4dd97ee30983e45c594e91b05e9ebd5b480100f`.
This review inherits the accepted even-stream proof and its amendment.
It does not change those files or their reviews.

## Sector and actual leaf coordinate

The paired-column equations each impose one independent affine bit
condition. The last column belongs to `span(omega)`, which imposes
`n-1` more conditions. Thus the codimension is `nf+n-1`.
The last-column translation characters must be positive. The proof's
product has these signs and gives the stated support.

The paired address addition sends a paired translation to its second
bit. The last-column additions send `e_0+e_i` to `e_i` and retain
`u=x_0+...+x_(n-1)` as the first output. On dual coordinates they send
`t omega` to `t e_0`. Thus the residual character belongs to the
specified physical leaf bit. There is no extra basis map at that step.

Both signs of the local code have the stated inverse. The first row
selects the corresponding signed average; the zero-detail inverse
gives the corresponding signed constant. The earlier proof of
`B^-1 E B=P Pi P^-1` therefore applies with these mixed signs.
All detail values stay available. The shear restores an arbitrary
source and preserves the target complement.

## Native phase and frame match

An odd line sees one 0 and one 1 in each paired Fourier column, and
sees `t` in the last column. Its phase is `i^(f+t)`. A common
translation has phase
`(-1)^(f omega.delta) (-1)^(t omega.delta)`.
This gives exactly

    L C_q^(tensor lambda)=i^f C_u L,
    L X_delta^(tensor lambda)=(-1)^(f epsilon) X_u^epsilon L.

For the complete frame as stated in the proof, multiply the line
factors and use `X_u=C_u^2`. The result is

    O_leaf=i^(gamma+r f) (-1)^(f epsilon) C_u^(r+2epsilon).

Here `gamma` is the total tensor phase. It is not a one-column phase.
The frame must have the stated product of forward line kernels;
rank alone is not a substitute for that operator hypothesis.

The projector commutes with these frames. With `JL=Pi` and `LJ=I`,
the leaf update gives
`J O_target,leaf O_source,leaf^-1 L=O_target Pi O_source^-1`.
This proves the logical shear on arbitrary input fields. For the
example with source `C_1` and target `i X_1 C_1 C_2` at width three,
the leaf frames are `i C_u` and `i I`; their ratio is `C_u^-1`.

An orthogonal conjugation inside the displayed native product does
not change the argument. An additional outer address permutation can
act on the other retained leaf coordinates. The proof does not remove
such a permutation, and neither does this review.

## Stream and precision obligations

The unequal `f/f/1` layout is permitted by the inherited compact-map
lemma. Each pair of half-slots has equal width, other chunks can be
spectators, and the final additions have width one. The original
complete control fields are sufficient. When `f=0`, only the width-one
additions remain. There are at most `2n-1` additions; `n` is fixed in
the inherited time bound.

After the fixed basis maps, each selected bit can be split in its
current shorter address without a bit shuffle. Reverse merges restore
the layout. The full record retains its polynomial and protected
fields. The geometric active volumes and detail-stack argument are
the same as in the accepted stream review.

The extra kernel is a fixed two-point coefficient computation on the
leaf. Split on the remaining bit `u`, keep the two source operands,
compute the target updates, and merge. This costs the leaf volume,
including its fixed-tape movement. It is not a free operation on a
full native field. All work areas and descriptors must satisfy the
same pinned stream assumptions.

The Gaussian half-integer kernel needs at most one fractional bit
beyond the `k` code bits. In the real-component maximum norm, each
kernel output has row norm at most two. Its unhalved sum has norm at
most four. Adding the old target gives norm at most three. During
decoding, the old target is a partial average and the added signal is
a signed constant. Saved operands therefore give the stated two-bit
magnitude allowance for all these prefixes. This uses the specified
correlated shear, not arbitrary changes to encoded detail values.

The conditional dependency-path requirement in `AMENDMENT.md` still
applies. The proof does not establish a new path bound for a changed
internal controller. The separate actual-owner boundary packet is not
part of this review.

## Independent exact checks and limits

The checker forms the leaf map directly as one signed average per
physical input column. It does not import or execute the producer.
It checks 256 native-line columns and 512 translation columns in
three small layouts. One layout has nonadjacent selected bits and a
protected address bit. It checks `LJ=I` on the leaf image, `JL` as an
idempotent projector, and 64 direct source-update columns for the
frame-matched example. Adding the arbitrary target identity then gives
the full shear. The unchanged source identity is part of its definition.

The check also verifies both local code signs and all 16 combinations
of Gaussian unit and `C_u` power. The exact real-component kernel norm
is two and its coefficients need at most one fractional bit. Three
wrong-last-sign controls fail as required. The producer's 1,728-column
full Haar replay was read but not rerun; it is not counted as an
independent replay here.

This is a proof and selected exact check of a local stream layer.
It is not a full native owner replay, a new finite machine invoice,
a completed controller, a recursive supplier, or a kappa claim.
The exponentially small affine support remains a limit.
No producer or earlier review file was changed. No PR, commit, or push
was made. Before a future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
