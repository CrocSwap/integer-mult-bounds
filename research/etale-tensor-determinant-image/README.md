# Exact determinant images of finite etale multiplication tensors

This contribution is produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Result and scope

Let K=F_q, let A be a nonzero finite etale K-algebra, and write

\[
 A\cong\prod_{i=1}^r F_{q^{d_i}},\qquad n=\sum_i d_i.
\]

Let t be its multiplication tensor in A* tensor A* tensor A, with the
ordinary covariant action of three general linear groups. The same statement
holds for every tensor in this GL orbit, with three independently chosen
factor bases. Let Delta(t) be the ordered determinant image of its stabilizer.

**Theorem.** Define e=2 if q is odd and either some d_i is even or some odd
degree occurs at least twice. Define e=1 otherwise. Then

\[
 \boxed{\Delta(t)=\{(u,v,w)\in(K^\times)^3:(uvw)^e=1\}.}
\]

For e=1 the image has (q-1)^2 elements. For e=2 it has 2(q-1)^2 elements.
Moreover, for fixed q, a deterministic algorithm extracts e and the three
bounded monomial equations of atlas A030 from t in polynomially many field
operations, under the promise that t is in such an orbit. It does not need a
supplied multiplication basis, an invertible slice, a list of field factors,
or enumeration of the tensor stabilizer. It recovers the degrees from the
left nucleus by linear algebra and Frobenius-fixed spectral projectors.

This is a **scoped mathematical proof**, with bounded exact computational
corroboration. It solves the promised finite etale multiplication class of
David Ganz's explicitly unproved atlas A030 in [PR #2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849).
It does not solve A030 for arbitrary tensors, recognize the promise, supply a
physical program, change the selected frontier, or prove a multiplication
bound. Global literature priority is unclaimed. The verifier's finite cases
are evidence for the implementation and the sign boundary, not a substitute
for the all-dimension proof below.

The main first fixture is A=F3 cubed. Swapping two one-dimensional factors
has determinant -1, so the image is all eight determinant triples. For
A=F3 times F27, the degrees 1 and 3 are odd and distinct, so the image has
only four triples, those with product 1. Repeated odd factors matter even
when Frobenius has positive determinant on each individual factor.

## Proof

### 1. Normalize every autotopism

Use the bilinear convention

\[
 F(x)G(y)=H(xy),\qquad F,G,H\in\operatorname{GL}_K(A).
\]

Set a=F(1), b=G(1). Substituting y=1 and x=1 gives
H(x)=F(x)b=aG(x). Thus multiplication by both a and b is invertible.
In a finite product of fields this says a,b are units. Put
sigma(x)=(ab)^(-1)H(x). Then

\[
 F=L_a\sigma,\quad G=L_b\sigma,\quad H=L_{ab}\sigma.
\]

Substitution in the autotopism identity gives
sigma(x)sigma(y)=sigma(xy), and sigma(1)=1. Invertibility makes sigma a
K-algebra automorphism. Conversely every pair of units and every such
sigma gives an autotopism by the displayed formula. This is the concrete
commutative specialization of the isotopy normalization in atlas A019;
its classical isotopy content is not claimed as new.

For the ordinary covariant tensor action the corresponding stabilizer
triple is (F^(-T),G^(-T),H). Indeed the transformed bilinear map is
H times mu(F^(-1)x,G^(-1)y), which equals mu(x,y). Therefore, writing
N(a)=det L_a and delta=det sigma, the determinant triple is

\[
 (N(a)^{-1}\delta^{-1},\ N(b)^{-1}\delta^{-1},\ N(a)N(b)\delta).
\]

Its product is delta^(-1). This inverse-input convention is necessary;
the three determinants of a bilinear autotopism are not the three
covariant tensor determinants.

### 2. Determine the automorphism signs and attain every allowed triple

A K-algebra automorphism permutes the primitive field idempotents, preserves
their degrees, and on each field is a power of Frobenius after a field
identification. Conversely all such choices are automorphisms.

On F_(q^d), the normal basis theorem makes Frobenius a d-cycle on a K-basis.
Its determinant is (-1)^(d-1). A transposition of two degree-d factors has
determinant (-1)^d: choose matching bases and exchange the d basis pairs.
These operations generate the automorphism group. Consequently every
algebra automorphism has determinant in {1,-1}. In odd characteristic a
negative determinant occurs precisely if a degree is even, or an odd
degree is repeated. If all degrees are distinct and odd, no factor can
be permuted and every Frobenius power has determinant 1. In characteristic
two all these signs equal 1.

The norm N:A^times -> K^times is onto. For a field factor it is
z -> z^((q^d-1)/(q-1)), onto the order-(q-1) subgroup of its cyclic unit
group; take 1 in the other factors. This is a classical finite-field norm
fact. Fix an automorphism of determinant delta. The two independently
surjective norms in the formula of section 1 realize every nonzero triple
whose product is delta^(-1). Thus the complete image is precisely the
inverse automorphism-sign image in the product coordinate. Signs are their
own inverses, proving the formula and its cardinalities.

For normal bases and the elementary finite-field facts, see J. S. Milne,
[Fields and Galois Theory](https://www.jmilne.org/math/Books/FT0.pdf),
sections on finite fields and the normal basis theorem. These are cited
classical premises; the contribution is the exact determinant-image
criterion and its extraction at this tensor interface.

### 3. Recover the algebra without finding an invertible slice

Given t as a bilinear map nu:U times V -> W, solve the linear equations

\[
 \mathcal N_L(\nu)=\{(X,Y)\in\operatorname{End}(U)\oplus
 \operatorname{End}(W):\nu(Xu,v)=Y\nu(u,v)\ \forall u,v\}.
\]

There are 2n^2 unknowns and n^3 scalar equations. For canonical
multiplication, substituting v=1 gives X=Y, and then u=1 gives
X(v)=X(1)v. Hence this nucleus consists exactly of (L_a,L_a), a in A.
If nu(u,v)=R mu(P^(-1)u,Q^(-1)v), its nucleus is

\[
 \{(P L_aP^{-1},\ R L_aR^{-1}):a\in A\}.
\]

This follows by substitution in the defining equations in both directions.
Projection to Y is faithful. The projected matrix algebra B is therefore
isomorphic to A and is the regular representation on W up to conjugacy.
It can be computed by Gaussian elimination, without knowing P,Q,R or A.

Compute the K-linear map Phi:B -> B, z -> z^q. It is linear because B is
commutative of characteristic p and scalar coefficients satisfy c^q=c.
Its fixed algebra C is isomorphic to K^r: each finite-field factor has
exactly K as its Frobenius fixed field. Compute a basis c_1,...,c_r of C.

Starting with the idempotent 1, refine each current nonzero idempotent h,
for every basis vector c_j and every lambda in K, by the nonzero matrices

\[
 h\bigl(1-(c_j-\lambda 1)^{q-1}\bigr).
\]

In C=K^r, this is the coordinatewise indicator of the coordinates where
c_j=lambda, restricted to h. Each round is an orthogonal idempotent
partition. The final partition consists of all primitive idempotents:
if two coordinates agreed on every basis vector, they would agree on
all of K^r, contradicting the coordinate indicator vectors. The rank of
each resulting matrix on W is its field degree d_i, since B acts in the
regular representation. This proves that the degree multiset is recovered
intrinsically from t.

The linear systems and matrix products have polynomial size. There are
at most n basis vectors, at most n current pieces, and q scalars per
refinement. Exponentiation takes O(log q) matrix products. For fixed q,
these operations and the rank computations are polynomial in n. No loop
ranges over q^n algebra elements or over automorphisms. Return the exponent
row (e,e,e), reduced modulo q-1, and two zero rows. These are three bounded
monomial equations in atlas A029/A030's convention. If q=2 the modulus is
one and all rows are zero. If q=3 and e=2 the returned first row is also
zero, correctly giving the full determinant group.

## Exact finite evidence and reproduction

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/etale-tensor-determinant-image/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/etale-tensor-determinant-image/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/etale-tensor-determinant-image
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/etale-tensor-determinant-image --check-source-history
```

For another machine replace the absolute interpreter prefix by its CPython
3.12 executable. The expected verifier status is
`PASS_ETALE_TENSOR_DETERMINANT_IMAGE`. Each run prints a generated JSON
receipt with its interpreter version, exact finite results and SHA-256
hashes of the five package files. No receipt is handwritten and no output
is written into the checkout.

The verifier constructs twelve literal product-algebra tables over F2,
F3 and F5, through dimension six. It recovers degrees both in the original
charts and after three independent factor changes, and explicitly realizes
every predicted determinant triple using literal unit and automorphism
matrices. The cubic and quadratic fixture polynomials are checked to have
no base-field root, which proves their irreducibility in these degrees.
For dimensions at most two, and dimension three over F2, it independently
loops over every invertible input-map pair, derives the only possible
output map from the unit, and tests every basis product. These are actual
complete stabilizer censuses on their named finite domains. No predecessor
program or census is replayed.

Controls distinguish a missing repeated-odd-factor sign, a missing
even-degree Frobenius sign, a spurious sign for distinct odd factors,
a repeated cubic factor, a singular matrix, a matrix outside the computed algebra, a zero tensor
with the wrong nucleus dimension and the inverse-input determinant
convention. Checks remain active under optimized Python.

## Provenance and limitations

The exact base is ff3cc58e370d0f678e529246f8c73e8094e18fcf. `SOURCES.json`
pins the atlas statements and credit as provenance, along with the task
catalogue and selected record. They are not executable inputs. The current
selected conditional kappa remains 0.00302015.

Credit David Ganz's atlas PR #2849 for A030's explicit extraction question,
A019's normalization and A029's bounded character-table framework. The
atlas retains the tensor and stabilizer lineage, including the classical
Chen, Grochow, Qiao, Tang and Zhang tensor-action context. Finite-field
cyclicity, norms, normal bases, primitive idempotents and Gaussian
elimination retain their classical credit. The all-tensor proposal and
other contributors' results are cited premises or context, not audit
deliverables. This package claims no global first discovery.

The algorithm is a promise algorithm, not a recognition algorithm. The
proof covers every finite base field; the executable fixtures use only
prime fields 2, 3 and 5. No proof assistant, arbitrary-tensor solver,
physical supplier, full selected replay, recursive compiler, precision,
hosting or complete multiplication theorem was run or established.

The verifier has no recursion or external process. All loops have finite
bounds from twelve fixed fixtures, p<=5, n<=6, at most 20,000 candidate
matrices and at most 250,000 input-map pairs per census. All functions
are kept within roughly one page. Its checks use explicit exceptions,
so optimization cannot erase the contracts. For Power of Ten rule 3,
Python's managed integers, tuples and elimination rows allocate during
execution. The bounded fixture domain and bounded collections compensate
for that runtime requirement; the script releases its memory on exit.
Moving to a general input CLI would require a separate input and memory
budget. Warning-strict normal/optimized replay is the available diagnostic
check; no separate static analyzer is required by this package.

## Open next questions

- Can this extraction extend to multiplication in finite local commutative
  algebras with nilpotents? The unit norms and automorphism determinants
  may have additional power restrictions. Start with K[z]/(z^m), deriving
  the exact determinant characters before combining factors. The etale
  Frobenius-fixed splitting proof does not apply to that class.
- Can an arbitrary tensor be recognized as isotopic to finite etale
  multiplication in deterministic polynomial time at fixed q, with a
  transporter witness? Start from the computed left nucleus and test its
  regular action and compatibility with the second input. The present
  theorem assumes that promise and does not supply recognition.

Structured versions of these questions are in `TASK.json`.
