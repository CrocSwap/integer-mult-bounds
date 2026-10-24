# Exact determinant characters for truncated-polynomial multiplication tensors

This scoped proof gives the exact stabilizer determinant image for multiplication tensors of A=F_q[t]/(t^n), for every prime power q and n>=1. It answers the named truncated-polynomial case of the nilpotent-algebra question in Nick Petalas's [PR #5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252), at [proof commit 07e6f55d18d2d3fd6dcea19bd642d71657c5fe14](https://github.com/CrocSwap/integer-mult-bounds/blob/07e6f55d18d2d3fd6dcea19bd642d71657c5fe14/research/etale-tensor-determinant-image/README.md). No new kappa is claimed.

Let mu in A* tensor A* tensor A be multiplication, with the ordinary covariant action of GL(A*) times GL(A*) times GL(A). Let Delta(mu) be the ordered determinant image of its stabilizer. For r>=0, put H_r={c^r:c in F_q^*}; in particular H_0={1}. Set N=n(n-1)/2. Then

```text
Delta(mu) = {(u,v,w): v w in H_n, u w in H_n, u v w in H_N}.
```

Put m=q-1, g=gcd(n,m), h=gcd(N,m), e=m/g and f=m/h. Equivalently the image has the three bounded monomial equations

```text
(v w)^e = 1,    (u w)^e = 1,    (u v w)^f = 1.
```

Reduce the exponent rows (0,e,e), (e,0,e), (f,f,f) modulo m. This is the equation format of David Ganz's atlas A029/A030 in [PR #2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849), with the [atlas statement pinned at main](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/pure-math-atlas-400/volumes/01-algebra.md). The image size is m^3/(g^2 h). The single GL orbit splits into exactly g^2 h orbits under the product of the three special linear groups.

The determinant image is unchanged by independent basis changes in the three factors. Therefore, under the explicit promise that an n-by-n-by-n input tensor lies in the GL orbit of this multiplication tensor, its dimensions and q alone give the three exponent rows. Computing the two greatest common divisors and reducing the rows takes polynomially many bit operations. This is a promise algorithm. It does not recognize the orbit, recover a multiplication basis, or produce a transporter.

For q=5,n=2 the image has 16 elements and the orbit splits into four special-linear orbits. For q=5,n=3 the image is the entire 64-element determinant group. Thus automorphism determinants for this nilpotent family need not be signs. For q=7,n=3 the image has eight elements and the orbit splits into 27 special-linear orbits. At n=1 the formula reduces to u v w=1. At q=2 the determinant group is trivial.

**Proof: unit and automorphism characters.** In the basis 1,t,...,t^(n-1), multiplication by a=a_0+a_1 t+... is triangular with diagonal a_0. Thus a is a unit exactly when a_0!=0, and det(L_a)=a_0^n. Its determinant image is exactly H_n, attained already by scalar units.

For n>=2, an algebra automorphism sends t to c_1 t+c_2 t^2+...+c_(n-1)t^(n-1), with c_1!=0. The constant term is zero because t is nilpotent. Conversely every such substitution is well-defined, and its matrix is triangular with diagonal 1,c_1,c_1^2,...,c_1^(n-1), so it is invertible and is an automorphism. Its determinant is c_1^N. The determinant image is H_N, attained already by t mapping to c_1 t. For n=1 only the identity automorphism exists, which agrees with H_0.

**Proof: all stabilizers and attainment.** Use the bilinear autotopism identity F(x)G(y)=H(xy), with F,G,H invertible. Put a=F(1), b=G(1). The unit substitutions give H(x)=F(x)b=aG(x), so multiplication by a and b is bijective. A bijective multiplication map makes its element a unit: surjectivity gives an inverse, and commutativity gives both products equal to 1. The map sigma=(ab)^(-1)H is then an algebra automorphism, and

```text
F=L_a sigma,   G=L_b sigma,   H=L_(ab) sigma.
```

Conversely these maps give an autotopism for all units a,b and every algebra automorphism sigma. This is the classical normalization in atlas A019, retained by PR5252; the argument is included to fix its hypotheses.

The covariant tensor stabilizer is (F^(-T),G^(-T),H), not (F,G,H). Set x=det L_a, y=det L_b and z=det sigma. Its determinant triple is

```text
(u,v,w) = (x^(-1) z^(-1), y^(-1) z^(-1), x y z),
where x,y in H_n and z in H_N.
```

The inverse coordinate formulas are x=v w, y=u w, z=(u v w)^(-1). They prove both necessity and sufficiency of the three subgroup conditions, with no additional relation. Scalar units and linear substitutions attain every choice of x,y,z. The power subgroup H_r of the cyclic group F_q^* has size m/gcd(r,m) and is defined by the power m/gcd(r,m). This gives the equation rows and image size, including r=0.

Independent changes of tensor bases conjugate the stabilizer inside the product GL group, and determinants are invariant under conjugacy. Finally the product SL group is the kernel of the surjective determinant map from the product GL group to (F_q^*)^3. Its orbits inside the fixed GL orbit are the cosets of Delta(mu) in that determinant group. Their number is the index g^2 h. This completes the proof.

**Evidence.** The standalone checker constructs 1,734 literal scalar-unit/substitution autotopisms in 24 contexts, with q=2,3,5,7 and n=1 through 6. Their covariant determinant triples attain every predicted image. Separately, seven complete small domains enumerate all 260,985 invertible input-map pairs, derive the only possible output map from the unit identity, and test every basis product. They accept 1,729 autotopisms, including nonconstant units and nonlinear substitutions, and recover exactly the predicted images. These complete domains are (q,n)=(2,1),(2,2),(2,3),(3,1),(3,2),(5,1),(5,2).

Seven controls distinguish the inverse-input convention, non-surjective unit norms, automorphism determinants outside the sign subgroup, n=1, q=2, and two unsupported checker domains. In particular at q=7,n=4 the raw autotopism determinant triple (2,1,2) is excluded, while its correct covariant triple (4,1,2) is admitted. Normal and optimized warning-strict CPython 3.12.14 checks pass. The proof covers every finite field; these finite fixtures use prime fields only. No predecessor executable is imported or replayed.

Credit Nick Petalas's [PR #5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252) for the finite-etale result, the inverse-input convention and the explicit nilpotent follow-up. Its [pinned proof](https://github.com/CrocSwap/integer-mult-bounds/blob/07e6f55d18d2d3fd6dcea19bd642d71657c5fe14/research/etale-tensor-determinant-image/README.md) is context, not an imported algorithm. Credit David Ganz's [PR #2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849) for atlas A019 normalization, A029 character equations and A030 extraction. Classical isotopy, cyclic-group and truncated-polynomial-algebra facts retain their credit. No general literature-priority claim is made.

**Limits.** This is the single truncated-polynomial local algebra, not every finite local algebra or product of local factors. Orbit recognition, a transporter, physical coefficient preparation, native realization, movement, precision and supplier/outer admission remain open. No new multiplier is supplied. No selected cold replay, predecessor scientific suite, native build, Lean or Docker run was used. No independent human or proof-kernel acceptance is claimed. Base: canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority revision 7. Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/truncated-tensor-characters
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_TRUNCATED_TENSOR_CHARACTERS`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Extend the character calculation to a specified multivariable local algebra or recognize the orbit promise. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
