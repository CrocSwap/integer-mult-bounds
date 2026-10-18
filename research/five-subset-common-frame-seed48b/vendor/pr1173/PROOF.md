# Sharp threshold in the weight-five class

Use the class defined in README.md, over the standard binary dot product.
The proof combines PR920's residual dimension floor with PR1139's triple
support classification. The eight-coordinate complement step and the
nine-coordinate weight-five fixture are this package's additions.

## The four-plus-four floor

For any nondegenerate binary space W, its characteristic w_W uniquely satisfies
w_W dot x = x dot x for all x in W. A norm-one vector s splits W as its line
orthogonally summed with the nondegenerate residual W intersect s-perp.
That residual is alternating exactly when w_W=s: its characteristic vanishes
exactly when the characteristic of W lies in the line spanned by s.
This is the historical criterion used in PR920.

Distinct norm-one sources with s1 dot s2=1 span a degenerate plane E with
radical r=s1+s2. A nondegenerate U containing E cannot have dimension two.
If dim U=3, then E=r-perp inside U. Since r has norm zero, w_U lies in E.
Pairing w_U with both sources must give one; the only two possibilities
inside E are s1 and s2. At least one incoming residual is therefore an
alternating plane and has no orthonormal basis. Hence dim U>=4. Apply the
same argument to the targets inside U-perp to obtain dim U-perp>=4.
Thus h>=8 for every legal doubly degenerate norm-one rectangle.

## Eight-coordinate complements preserve the interface

In F2^8 let w be the all-ones vector and define J(x)=x+(x dot w)w.
The map is linear, w dot w=0, and J is its own inverse. Expanding the two
cross terms shows J(x) dot J(y)=x dot y. It is therefore an isometry and
preserves every containment, orthogonal complement, nondegeneracy and
orthonormal basis condition in the local interface. It also preserves
disjointness of E and T, since it is an invertible linear map.

Every weight-five label has odd parity, so J sends it to its three-element
complement. For two weight-five supports with intersection size k,
their complements intersect in k-2. Consequently
K(J(s),J(t))=-K(s,t); the entire 2x2 matrix changes by one common sign and
rank one is preserved. Degenerate pairs remain degenerate. A legal weight-five
rectangle at h=8 would therefore give a legal triple rectangle there.

## Why a doubly degenerate triple rectangle needs ten coordinates

The following is PR1139's small support classification, included to make the
dependency inspectable without importing pending code. Write source triples
as {c,a,b} and {c,d,e}, and let O be the other coordinates. Every triple
even-orthogonal to both sources has one of four forms:

| Type | Support | Signed kernel column |
| --- | --- | --- |
| A | three elements of O | (+1,+1) |
| B | {a,b,o}, o in O | (-1,+1) |
| C | {d,e,o}, o in O | (+1,-1) |
| D | {c,x,y}, x in {a,b}, y in {d,e} | (-1,-1) |

If c is present, parity forces one element from each displayed pair. If c
is absent, each pair contributes zero or two elements. This proves the list
complete. Rank one groups the two targets into A/D or B/C. A/D targets are
disjoint, and two distinct B or two distinct C targets intersect twice,
so those pairs are not degenerate. Two D targets intersect once only when
their x and y both differ; their sum is the nonzero source radical
{a,b,d,e}. Likewise a B/C pair intersects once only with a common o, and
then has the same sum. These possibilities violate E intersect T={0}.
Only A/A remains, requiring five coordinates outside the five source
coordinates. Thus h>=10. In particular no such triple rectangle exists
at h=8, even before checking incident residuals.

The isometry excludes weight-five rectangles at h=8. The general floor
excludes h<8. Together these prove the lower bound h>=9 in our local class.

## Nine coordinates attain the bound

Take sources (31,481), targets (47,87), and U=span(31,481,3,40) in F2^9,
with the masks defined in README.md. The endpoint intersections are one and
three, every cross intersection is even, and the kernel is
[[1,1],[-1,-1]]. Direct span inspection gives E intersect T={0}.
U is nondegenerate, contains E, and is orthogonal to T. The four explicit
residual bases in README.md each span their full residual and have identity
Gram matrix. These exact finite vector identities certify this witness;
both implementations check them. Therefore the minimum ambient dimension
for this weight-five class is exactly nine.

For h>9 embed these supports and U by zero extension. The complement becomes
the old U-perp orthogonally summed with standard coordinate lines; each
outgoing residual gains those same orthonormal lines. Thus existence holds
for every h>=9. This proves a threshold, not a classification or count of
all weight-five rectangles in larger dimensions. The h=9 exhaustive census
is separate finite evidence. No complete supplier, global simultaneous
frame assignment, cost recurrence or new multiplication exponent follows.
