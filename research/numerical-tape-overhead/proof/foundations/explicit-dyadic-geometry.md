# Explicit dyadic address geometry with a fixed odd radix

Status: **proved geometric/address interface; pending independent review**. This replaces the generic rational Gram quotient and arbitrary complement choices in the shared-swap geometry. It does not by itself establish a complete multiplier or a new overhead envelope.

Pins: programme `0607d044d1d09489580da0e5828588820e1a6775`; OpenAI math `3344da59991ed94f9ba711217b29c1d760badfa6`. Read dependencies: tape `build/interchange.tex`, especially the label Gram block, shared endpoint preparation, rectangle delivery and low-rank delivery; programme [characteristic-two-label-geometry.md](characteristic-two-label-geometry.md). The scalar transfer matrix and rectangle decomposition are retained. Only the rational address realization and its basis algorithms change.

## 1. Exact statement and why numeric size matters

Let d be a power of two at least 2, h=2d-1, q a power of two, U=[q]^h, n0=q^h, and labels v in U^h. Let Far(u,w) indicate inner Hamming distance d. Put

    k(v,w)=sum_(a=1)^h Far(v_a,w_a),
    D=2(2+h n0).

Use the scalar transfer matrix P_* and its directed product rectangles from the earlier characteristic-two label theorem. Their rank r_* and maximum endpoint incidence lambda are unchanged.

**Theorem B2 (explicit address geometry).** There is a uniform rational realization in dimension D of the pairwise blocks

    Gram((x_v,y_v),(x_w,y_w))
       =(1-k(v,w)/d) I_2+(k(v,w)/d) [[0,1],[1,0]].       (B2.1)

Each pair is orthonormal. Individual layouts, rectangle reserve-only preparations, common rectangle layouts and their inverses admit explicit factorizations into O(D) elementary coordinate shears, scalings and exchanges. Every scalar in these factorizations is dyadic, with numerator and denominator bounded by a fixed polynomial in d and D. In the constructions below, the nontrivial scalings are bounded powers of two, and the shears have coefficients among fixed multiples of 1, 1/2 and 1/d. Hence the address radix can be the **fixed prime 3**, independently of the batch width and m.

Using the source's actual elementary-stream algorithms, these factorizations take O(D) recursive field-interchange calls plus V times a polynomial in the finite geometric parameters in ordinary work, on a stream of volume V. The changes shared across all queries act only on occupied reserve fields. Thus the shared-pencil call form is retained, with D replacing the quotient dimension:

    O(D(1+lambda)(1+m r_*/N)) calls per independent row. (B2.2)

The coefficient-row maps are a separate interface. The source's b>batch-width choice is also separate: fixed radix 3 requires a multi-digit packed batching construction, not its literal one-digit split. That distinction is maintained throughout.

The point of this result is stronger than a polynomial bit-height bound. In the source increasing-piece implementation, a huge fixed integer can require a huge number of passes. Here the actual elementary multipliers and their inverses have small dyadic descriptions and bounded numeric numerators/denominators, with explicit operation lists.

## 2. A nondegenerate hyperbolic completion

Let W have basis e,z and f_(a,u) for a in [h], u in U; its dimension is r=2+h n0. Define a symmetric bilinear matrix B on W by

    B(e,e)=B(z,z)=2,
    B(f_(a,u),f_(b,w))=-(4/d) 1_(a=b) Far(u,w),

and zero on all other basis pairs. B need not be nondegenerate. Replace W by

    V_geom = W direct-sum W*,
    G = [[B,I],[I,0]].                                  (B2.3)

This is nondegenerate because its inverse is [[0,I],[I,-B]]. All displayed entries are dyadic with small numeric numerator and denominator. No radical computation, matrix inverse search, signature decomposition or determinant-height estimate is needed.

For a label v put

    a_v=sum_a f_(a,v_a),   z_v=z+a_v,
    x_v=(e+z_v)/2,         y_v=(e-z_v)/2,                 (B2.4)

in the primal summand. Since Far(u,u)=0,

    <z_v,z_w>=2-4 k(v,w)/d,    <e,z_v>=0, <e,e>=2.

Equation (B2.1) follows directly. The scalar rank and rectangles depend only on P_*, not on choosing a minimal-dimensional rational realization. The doubled dimension D is valid in the source endpoint argument.

## 3. Individual complement bases without elimination

For every label let C_v be the coordinate subspace spanned by all ambient standard basis vectors except the primal e and primal z. It is in fact the same coordinate subspace for every v. The decomposition

    V_geom = C_v direct-sum span(e,z_v)

is explicit: subtract a vector's e coefficient times e and its z coefficient times z_v. For c in C_v define

    p_v(c)=c-<c,e>e/2-<c,z_v>z_v/2.                     (B2.5)

The vectors p_v(c), for the coordinate basis c of C_v, form a basis of span(x_v,y_v)^perp. Injectivity follows because the kernel of orthogonal projection is span(e,z_v), which intersects C_v trivially. The dimensions agree.

The full basis M_v consisting of these D-2 complement vectors followed by x_v,y_v can be generated from the ambient coordinate basis as follows:

1. Replace z by z+a_v using h unit shears from feature coordinates.
2. Replace e,z_v by x_v,y_v with a fixed two-dimensional dyadic butterfly.
3. For each untouched coordinate c, subtract <c,x_v>x_v+<c,y_v>y_v.

Step 3 is two column shears per c. The relevant inner products are obtained directly from (B2.3): their numeric magnitudes are bounded by an absolute constant and their denominators divide a fixed multiple of d. The formula includes dual coordinates, where the only nonzero pairings are 1/2 or -1/2. All elementary diagonal scalings are fixed powers of two. Reversing the list gives the inverse with the same bounds. The list has O(D) operations.

Basis-column operations right-multiply the basis matrix, so corresponding address actions are applied in reverse temporal order; inverse lists reverse and invert those elementary factors. This is an explicit elementary factorization, not merely a claim that M_v and its inverse have small entries. Its orientation may be reversed to use y_v,x_v by one additional exchange.

For later use, if w lies in this orthogonal complement, its coordinates in the basis p_v(C_v) are particularly simple:

    coord_v(w)=(w-w_e e-w_z z_v)|_(C_v).                 (B2.6)

Indeed the vector inside parentheses lies in C_v and has orthogonal projection w. Subscripts e,z denote original primal coordinate coefficients, not bilinear pairings.

## 4. Product rectangles and their isotropic difference space

A directed outer rectangle has source set

    L=product_a L_a

and destination set K=product_a K_a. Outside its d differing outer coordinates, L_a=K_a is the same singleton. Inside them, L_a and K_a are disjoint nonempty subsets of U. This follows from the source first-differing-bit rectangle construction: at least one specified letter differs across the two inner sides. Choose anchors l_a in L_a and k_a in K_a. Choose one differing coordinate a_* and distinguish the feature f_(a_*,l_(a_*)).

At a source v use oriented pair (x_v,y_v); at a destination w use (y_w,x_w). Their sums are all e. Their differences are

    r_v=z_v at sources,   r_w=-z_w at destinations.

The rectangle Gram properties imply <r_i,r_j>=2 for every two oriented endpoints. Therefore the space E spanned by r_i-r_0, where r_0=z+sum_a f_(a,l_a), is totally isotropic and orthogonal to every endpoint pair.

It has the following explicit basis:

    s_(a,u)=f_(a,u)-f_(a,l_a), u in L_a except l_a,
    t_(a,u)=f_(a,u)-f_(a,k_a), u in K_a except k_a,
    g=-2z-sum_a(f_(a,l_a)+f_(a,k_a)).                    (B2.7)

For singleton common coordinates there are no stars. Stars on L and K have disjoint nonanchor pivots because the nontrivial sides are disjoint. The cross vector g has primal z coefficient -2, which no star uses. Thus these vectors are independent. They span every source difference using s stars, and every destination difference using g and t stars. This proves that they are a basis, rather than an arbitrary spanning set later requiring elimination.

Let C_R be the coordinate span obtained by omitting primal e, primal z, every star's nonanchor feature pivot, and the distinguished anchor feature. Then

    V_geom = C_R direct-sum E direct-sum span(e,r_0).     (B2.8)

One explicit construction of this basis starts from the coordinate basis: form the stars; replace z by g using a scaling -2 and anchor additions; replace the distinguished anchor by

    r_0 = -g/2 + (1/2)sum_a(f_(a,l_a)-f_(a,k_a));         (B2.9)

and retain e. The distinguished anchor has coefficient 1/2 in the last replacement, and all other anchors used there remain coordinate columns. The operations have coefficients ±1, ±2, ±1/2 and take O(D) steps. In fact the resulting complete basis is unimodular: the two distinguished pivot factors -2 and 1/2 multiply to -1, while star pivots are one. No prime other than 2 enters a required unit.

For endpoint i replace r_0 by r_i using its explicit E-coordinate combination: at a source add its s stars; at a destination add g and subtract its t stars. This uses O(h) unit shears. Replace e,r_i by the oriented pair and project the untouched C_R coordinates orthogonally onto its complement. E is already orthogonal and remains unchanged. This gives the source's desired complement basis

    (p_i(C_R), E),                                     (B2.10)

and a complete endpoint basis with O(D) small dyadic elementary operations and an equally explicit inverse.

## 5. The crucial preparation is reserve-only

The previous paragraph alone would not justify the source sharing: a factorization that uses a selected query's two main fields as temporary helpers could require different preparation for each query. Here the actual change between complement bases has a stronger form.

The individual complement uses the coordinates C_v from Section 3. Because every c in C_R has zero original e and z coefficients, equation (B2.6) sends p_i(c) to the identical coordinate vector c. Every star has original e,z coefficients zero and is already orthogonal, so its individual-complement coordinates remain the same star. Define the anchor difference

    a=sum_a(f_(a,l_a)-f_(a,k_a)).                        (B2.11)

Its distinguished-anchor coefficient is one. The common list

    (remaining coordinate units C_R, all stars, a)      (B2.12)

is a basis of the D-2 dimensional reserve coordinate space. It is explicitly unimodular: construct each star by a unit shear from its anchor, then replace the distinguished anchor by a through unit anchor additions. Every other anchor is retained as a coordinate column.

For g, equation (B2.6) gives

    coord_v(g)=2a_v-sum_a(f_(a,l_a)+f_(a,k_a)).           (B2.13)

Thus at a source v this column is

    a+2 sum_a s_(a,v_a),

while at a destination w it is

    -a+2 sum_a t_(a,w_a),                               (B2.14)

with an anchor's absent star interpreted as zero. Starting from (B2.12), these are only one sign scaling and O(h) shears of coefficient 2 into its last column. All operations act on the D-2 reserve coordinates alone. Their inverses use the same bounded coefficients. The list length is O(D).

After this reserve-only preparation, move the E coordinates to the prescribed late reserve positions with at most dim(E) field exchanges. The source's remaining per-query map is lower triangular: the projected C_R coordinates differ from the original C_R by endpoint-pair and E components, and each endpoint pair differs from the reference pair by E components. The common order is C_R early, reference pair in the selected main positions, and E late. Its coefficients are the explicit projections and E coordinates above, so they are small dyadics, not unbounded complement solutions. These lower triangular maps require no additional recursive calls. They retain all occupied coordinates and are inverted at destinations as in the source proof.

## 6. Low-rank delivery and conversion to a fixed common layout

The scalar matrix P_* is still over F2. Its independent-row/column factorization may use ordinary polynomial-dimensional binary elimination. No rational coefficient magnitude follows from that elimination or is needed: its entries and inverse are in F2.

A singleton common layout is M_v, already explicitly factored in Section 3. A rectangle common layout is the explicit basis (C_R, reference pair, E), with displaced spare fields included unchanged. Its basis construction is Section 4 plus a coordinate permutation, again O(D) small dyadic operations. Converting either to a fixed ambient order composes one such factorization with the inverse of another. This still has O(D) operations. The source uses these conversions only for the r_* internal vectors and their incident rectangles, so the normalized query-dependent call factor m r_*/N is unchanged.

## 7. Physical elementary operations and radix compatibility

For an elementary shear on two width-f radix-3 fields, a later target controlled by an earlier source is the source lower triangular operation: on a complete earlier-source fibre, calculate the modular shift and rotate the contiguous target blocks. Every denominator is a power of two, hence invertible modulo 3^f. The actual shift preparation uses ordinary integer arithmetic polynomial in f and the descriptor size. The fibre has at least 3^f positions, which pays for this polynomial work up to an absolute polynomial in the finite geometric parameters, including the bounded initial f range. Arbitrary intervening and trailing ranges increase the available volume.

An earlier-target shear can exchange its two fields, perform the lower triangular shear, and exchange them back. It therefore costs two recursive interchanges plus the same ordinary work. An elementary field exchange costs one call. Fixed dyadic diagonal scalings are implemented by the source increasing-piece routine for their small integer numerator or denominator, reversing for an inverse. Their numeric cost is polynomial in the finite parameters, uniformly over f. No gigantic modular inverse is treated as a fixed scaling with that many increasing pieces.

There are O(D) operations in each needed list. Thus the source stage accounting remains (B2.2), with an absolute change in its constant and D at most twice the previous coarse dimension bound. Its reserve-only preparations are shared across all m queries. Linearity, cancellation and actual common-address identification are exactly the source argument; the new basis choices satisfy every Gram premise it uses.

All geometric lists can be generated by bounded loops over labels, rectangle signatures, coordinates and the explicitly given stars. Under the existing accepted parameter guards N<=m^C and D,lambda,d<=m^C, both generation and retained descriptions are polynomial(m). Scalar row-index and repair processing are not included in this geometric statement and must be composed separately.

## 8. Consequence, limits, and next gates

This proves a small-magnitude, explicitly factored replacement for the generic rational-address data. It is compatible with characteristic-two scalar data while using the fixed odd radix 3 for physical addresses. Doubling the coarse ambient dimension changes absolute constants in the routing invoice, not its m^{o(1)} profile. The exact new constant must nevertheless be recomputed before reusing a numerical acceptance test.

The literal source additionally sets its radix above the batch width. That condition has not been retained: a compact multi-digit batch extraction is required, as a separate theorem. The new geometry plus the succinct scalar-factor theorem also does not automatically implement shift-check interpolation, full finite repair, numerical Walsh, recursion scheduling or the final common-cap multiplier. No new complete overhead bound is asserted in this note.

The next consequential question is whether all those remaining operations admit a jointly polynomial(m) physical profile. If so, this geometry removes a previous exponential numeric-address obstruction. If another interface remains exponential, that interface determines the global envelope instead.

## Credits and scope

The label matrix, rectangle partition and shared endpoint mechanism are from the OpenAI November 24 tape manuscript and the S002 characteristic-two label construction. Hyperbolic completion and elementary projection identities are standard linear algebra. The contribution is their explicit realization for these labels, the product-rectangle star basis, the reserve-only unimodular transition, and the complete small-dyadic operation lists enabling a fixed odd radix. Prepared for Jerry Chen (@CubeJerry), with substantial OpenAI AI assistance. No Lean kernel build, human referee review or full multiplier execution is claimed.
