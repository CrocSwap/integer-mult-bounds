# Whole-owner construction with an explicit GL bit cover

The bit local word, scalar program and owner placement are the repaired PR473
construction, pinned at `ab9952829152ff9ad80b17d77369fdb72a8a1f71`.
The complete complex supplier is reconstructed from PR471 at
`56b3da6aa1295d37ce43f1753479bfe4737b7ac3`. No scalar instruction is removed
and no helper is split between physical families. The finite operator proofs
and the inherited all-size contracts are separate obligations.

## Whole-owner transport

For each complete invocation, a helper's entire array has an actual owner
pair consisting of a physical family and a full matrix sigma. The verifier
constructs those matrices and checks injectivity, common operand labels,
both reflected residual conjugations and the paid idle complements. The
complete local identities hold for arbitrary helper dirt and restore private
centres. Right multiplication by each sigma is a bijection on the cover.
Thus the local identity transports to every selected owner and the cover
sweep places each endpoint operator exactly once. The companion bridge proof
spells out the scheduling and remainder argument.

All bit routing matrices are orthogonal over the admitted odd primes and
therefore belong to GL_78. The same owner injection and group cancellation
proofs hold when the ambient cover is enlarged from O_78 to GL_78. Conjugated
bit projectors need only be split idempotents; the GL construction in the
pinned `invoice/pr465/three-stage-cover-bit.tex` uses that contract explicitly.
The complex supplier and its cover are unchanged.

## Sharp bad-class charge

Choose a fixed odd prime q>2^128 in the interval (2^128,2^129). The finite GL audit checks that all fixed
frame Gram determinants have only prime factor 2, all route denominators
are 1,2,4, and idempotence and trace preserve each rank for q>78. Thus
Bertrand's theorem supplies an admitted prime in that interval. Work over Z/q^w and average
separately over the low class g0 in GL_78(F_q) for each fixed edge type.
After clearing det(g), a leading minor of size k in the conjugated projector
has degree at most mk. Each polynomial is nonzero: a basis adapted to the
split image and kernel gives a witness. For rank r<m, the sum of the degrees
is at most m*r*(r+1)/2<m^3. The GL density among all matrices exceeds one half
because the product of (1-q^-j) is at least 1-1/(q-1).

Schwartz-Zippel and conditioning on invertibility therefore bound the bad
fraction by 2m^3/q<2m^3/2^128. There is no union bound across distinct edge
types: their costs are summed after their separate averages. For N=2m, the
pinned Gaussian fallback uses at most

    C(m) = 6N(N-1)+3N+6(N-1)

rank-one children, including reversals, pivots and paired diagonal scaling.
At m=78 this is 146478. We conservatively retain the good-class moment for
all classes and add the full bad-class overcharge. For the complete paid
profile H, the certified function is

    sum_r H[r]*(r/m)^(1-a)/W
      + (2*m^3/2^128)*C(m)*sum_r H[r]*(1/m)^(1-a)/W.

Both rational interval engines put it below one at
`a=1297306501736506556311/10^24` and above one at `a+10^-24`.

## Full invoices and outer assembly

The bit profile is
`{1:210255,2:94673,3:22528,4:27916,5:10032,6:7304,7:4249,8:792,56:654}`.
It has 378403 children, rank mass 745536 and deficit 3264 at m=78, W=9600.
The actual prefix takes 775 bits, charged 832; the depth-three coefficient
takes 2379 bits, charged 2432 as a normalized local invoice. Routing-time line items already use dimension
m^2 and retain the full explicit residual-isometry and owner-route charges.

The cover change must also change the row invoice. Since
`|GL_78(F_q)|<q^(78^2)` and `physical=9609<q`, low stock takes at most 6085
base-q digits. The high-matrix chart takes 6084(w-1) digits. Three halving
levels plus the inherited 9909 and 252 allowances give

    3*(6084+1)+9909+252 = 28416.

The change of cover also needs the retained fixed-GL-routing contract. Its
q-dependent constant is not silently included in the 2432-bit local charge.
Let B_GL be any finite nonnegative integer large enough to include that
constant. Each exact bootstrap gap g uses the symbolic cutoff

    ceil(max(36/g^2, 2*(4+2432+B_GL)/g)).

For every finite B_GL this cutoff exists, its square-gap product is at least 36,
and its gap product is at least 2*(4+2432+B_GL). The checker verifies the exact
affine identities for all six stages. The bootstrap exponents and final κ do
not depend on this cutoff. This explicitly retained routing contract is a
condition of the claim; no concrete upper bound for B_GL is asserted.

The strict outer row degree gap is now `10^6-(51/25)*28416>0`; using the
old 20161 allowance would be incorrect. The complex supplier retains row
allowance 20161 and its original complete invoice, including all 17162810
scalar primitives. Its certified saving is `1305231506267591/10^18`.

Six bootstrap steps and all 47 strict outer inequalities yield
`κ=80976604882529/62500000000000000`. The next 10^-18 grid point is rejected.
The construction remains conditional on the inherited all-size compilation,
restored-row and analytic interfaces; finite replay is not a proof of those
interfaces.

## Provenance

PR465's sharp-charge observation is credited and its source note and script
are pinned under `invoice/pr465`. PR473 supplies the bit word; PR471 supplies
the normalized complex program; PR478 supplies the integrated invoice engines.
PR442's whole-owner mechanism and the PR417/443, PR450 and PR458 source
lineages retain their notices. New GL transfer, independent audits, packaging
and assembly adaptation were prepared with OpenAI Codex.
