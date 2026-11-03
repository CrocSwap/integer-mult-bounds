# Fixed F4 arithmetic binding and the inherited constructor

This package supplies an executable fixed-F4 backend to the first-success
constructor of PR6543. It adds a source-bound implementation and independent
returned-witness evidence. The all-prime-power first-success theorem and its
arithmetic operation bound are inherited; no new threshold theorem or first
raw nonprime pencil algorithm is claimed. This is a written source/contract
argument with bounded exact checks, not proof-kernel acceptance.

## Field and representation

Use K=F2[z]/(z^2+z+1), with encoded elements0=0,1=1,2=z,3=z+1.
The defining quadratic has no root in F2, so K is a field of four elements.
The primary compiles the exact authenticated definitions of Ali Romman's
PR5664 `Field` implementation and calls only Field(2,(1,1,1)). Its addition,
multiplication, negation and inverse tables supply every scalar operation.
No tensor recognizer or predecessor scientific checker is invoked.

Encoded addition is coefficientwise modulo2; it is not integer addition
modulo4. For example,2+2=0,2*2=3 and2*3=1 in K. Scalar2 is the nonzero
element z, not a prime-field integer2=0. Every new raw matrix and polynomial
entry must be a canonical integer0..3 with exact integer type; booleans are
not coefficients. Digit extraction from a raw matrix index is a representation
operation, not field multiplication or reduction.

`constructor.py` ports the source algorithm's scalar operations to these
tables. Polynomial addition, negation, multiplication, long division,
normalization and exact division use only K operations. Bareiss computes
det(tA+B), including polynomial row pivots; infinity means the literal slice A.
Kernel elimination, scalar determinants and inverse normalization also use
the same field operations. Finite quotient elements are low-first polynomial
coefficient lists, reduced modulo a monic irreducible h in K[t].

The cardinality is q=4, whereas the characteristic is p=2. Frobenius root
tests, the Berlekamp fixed-space matrix and quotient inversion use q, not p.
In particular z^4=z but z^2!=z. The map a->a^4 fixes K and is K-linear on
the required fixed-space calculation; squaring does not fix all scalars of K.
For an extension of relative degree e the nonzero inverse exponent is4^e-2.
The code does not allocate a table of size(4^e)^2 for that quotient field.

## What transfers from the source proof

PR6543's proof assumes a supplied exact finite field; it does not rely on
integer representatives modulo a prime. Substituting the verified K
operations preserves each polynomial and matrix identity used there:

1. If det(A)!=0, infinity succeeds over K itself. Otherwise form f(t)=det(tA+B).
   A zero f is an identically singular pencil. Test distinct base elements
   in the source's fixed order; n+1 points suffice when there are that many.
2. On base failure, inspect e=2,3,... and gcd(f,t^(4^e)-t). A strict missing
   factor exists exactly when some affine element of F_(4^e) is not a root
   of f. The first successful e is least because every earlier field was
   checked. Repeated factors in f do not change the root test: the Frobenius
   polynomial is square-free.
3. The missing quotient consists of irreducibles of the chosen degree after
   the earlier-degree failures. The source Berlekamp procedure chooses one
   branch and returns a degree-e factor h, rather than enumerating every
   lower-degree irreducible. Its fixed space and splits are computed over K.
4. The residue alpha=t mod h gives the literal slice alpha*A+B. Gaussian
   elimination over K[t]/(h) returns its inverse. The validator separately
   checks h's irreducibility, canonical coefficients, the actual slice and
   both products against the identity. Earlier-degree failures are rechecked.

The inherited proof also bounds the dense extension search using the previous
failed field size. This package fixes the input field to K and dimensions
0..17; it does not expose a general finite-field framework or establish a new
bit, storage, tape or physical complexity bound. Code transfer remains subject
to human review; exact bounded execution is described in VALIDATION.md.

## Why the named extension tests are discriminating

For d=4 or16 take A=diag(I_d,0), B=diag(C,1), where C is the companion
of t^d+t. Characteristic two makes minus C equal C. Then det(tA+B)=t^d+t
and infinity fails. The degree5 homogeneous pencil fails all projective F4
points and first succeeds at relative degree2. The dimension17 pencil fails
F4 and F16 and first succeeds at relative degree3: F16 intersect F64=F4,
so F64 has elements outside the root set F16. These are inherited Frobenius
attainers, not new constructions or thresholds.

The frozen nonprime variants apply four invertible elementary operations in
literal order: row0+=z*row1, last row+=(z+1)*row0, column0+=(z+1)*last
column, then column1+=z*column0. They preserve singularity and successful
projective points over every extension, while putting genuine nonprime
coefficients into the raw inputs. Both engines use the resulting literal
matrices, rather than replacing them by their diagonal descriptions.

The repeated-root dimension9 fixture has determinant(t^4+t)^2 with an
infinity block. It still first succeeds in relative degree2. All2x2 F4
pencils have a base-field success when regular, because a degree<=2 nonzero
homogeneous form cannot vanish at all five projective F4 points. Thus that
complete census alone would not test extension selection; the named degree2/3
cases and validation of actual returned h, alpha, slice and inverse are needed.

## Limits and credit

Nick Petalas6451 supplies the sharp first-degree theorem and attainers,
including prior F4 threshold work. PR6543 supplies the first-success algorithm
and arithmetic proof. Ali Romman5664 supplies the exact field backend;
5692/5712 already handle raw F4 decomposition/transport, with F9 and extension
coverage in the retained lineage. Existing6309 nonprime pencil work remains
credited. Bareiss elimination, Frobenius root tests, Berlekamp splitting and
quotient-field inversion are classical. Full source notices and pins are
retained in NOTICE.md and SOURCE-PINS.json.

An extension-field slice is not an original-field SL transporter, coefficient
delivery schedule, native consumer or multiplication supplier. Field descent,
actual caller/native contracts, physical arithmetic/access/restoration,
precision/stock/tape/control, compiler and complete recursive/outer invoices
remain separate. All five selected framework assumptions remain, with no new
kappa or selected-frontier change. Independent human/kernel acceptance is
unclaimed. Open next questions are in README.md and TASK.json.
