# Exact finite-field count for two simultaneous capacities

## Contract and prior theorem

Let V and W have dimension n over F_q. Let h:U→W be an injection, with
u=dim U and E=h(U). Require an isomorphism g:V→W such that

`g|U=h`, `g(A)⊂C`, `g(B)⊂D`.

All inclusions allow equality. A and B need not be nested. C and D need not
be nested. ToikY's PR6535 gives the exact feasibility criterion and its
quotient proof. Nick Petalas's PR6489 gives the prior nested count.
Ali Romman's PR6533 counts arbitrary finite capacity families by an
exponential kernel lattice. Here we count every completion for exactly two
capacities by a sum with at most n+1 terms. These prior results retain credit.

Set UA=U∩A, UB=U∩B, U0=U∩(A+B), and Z=(E∩C)+(E∩D). First require

`h(UA)⊂C`, `h(UB)⊂D`, `h(U0)⊂C+D`.

If any test fails, the count is zero. Define

| Symbol | Dimension |
| --- | --- |
| a,b | dim A-dim UA, dim B-dim UB |
| s | dim(A+B)-dim U0 |
| c,d | dim C-dim(E∩C), dim D-dim(E∩D) |
| t | dim(C+D)-dim(E∩(C+D)) |
| j | a+b-s |
| tau | c+d-t |
| ell | dim(C∩D)-dim(E∩C∩D) |
| k | dim(A∩B)+dim(h(U0)∩Z)-dim UA-dim UB |
| eC,eD,eCD | dim(E∩C), dim(E∩D), dim(E∩C∩D) |

If `a>c`, `b>d`, `s>t` or `k>ell`, the count is zero. For the remaining
case put `alpha=a-j`, `beta=b-j`, and `H=tau-j`. For a valid contract the
prior exact sequence also gives `0≤j-k≤tau-ell`, hence H≥0.

Write

`Inj(m,r) = product_(i=0)^(r-1) (q^m-q^i)`

for the number of injections from a fixed r-dimensional space into a fixed
m-dimensional space. It is zero if r<0 or r>m. Empty products are one.
Write `[m choose r]_q` for the Gaussian binomial coefficient, with value zero
outside 0≤r≤m.

## Closed formula

Define

```text
S = sum_i [H choose i]_q [c-tau choose alpha-i]_q
          q^((H-i)(alpha-i)) Inj(alpha,alpha)
          Inj(d-j-i,beta) q^(i beta),

max(0,alpha-c+tau) <= i <= min(alpha,H).
```

Then the exact number of completions is

```text
Inj(ell,k) q^(ell(j-k))
  * q^(j(alpha+beta)) S
  * q^(eCD*j+eC*alpha+eD*beta)
  * product_(i=u+s)^(n-1) (q^n-q^i).
```

This integer formula holds over every finite field, including nonprime fields.
The first factor uses ker(delta), not the whole common source quotient. That
distinction is required by the nonzero-delta example below.

The formula uses at most n+1 summands and O(n^2) integer multiplications and
exact divisions with direct Gaussian products. This statement concerns the
formula arithmetic, not bit complexity, field-order validation or input basis
reduction. The API checks prime-power orders; its simple trial-division check
is not claimed optimal in log q. No subspace lattice is enumerated by the
counting routine.

## 1. Count the injective common lifts

Use the source theorem's quotients

`Abar=(A+U)/U`, `Bbar=(B+U)/U`, `J=Abar∩Bbar`,
`Cbar=(C+E)/E`, `Dbar=(D+E)/E`, `T=Cbar∩Dbar`.

There is an exact sequence

`0→H0→T --rho--> (E∩(C+D))/Z →0`,

where H0 is the image of C∩D modulo E. Its dimension is ell. The prescribed
map induces delta:J→(E∩(C+D))/Z, with dim J=j and dim ker(delta)=k.
Any quotient completion restricts to an injective j0:J→T satisfying
`rho j0=delta`.

Choose a fixed complement of ker(delta) in J and a fixed section of rho.
There are Inj(ell,k) choices for j0 on ker(delta). On its j-k dimensional
complement, each prescribed quotient vector has q^ell lifts. All those
choices are independent. They remain independent from j0(ker(delta)), since
delta is injective on that complement. Thus there are

`Inj(ell,k) q^(ell(j-k))`

injective common lifts. No basis choice is counted twice: the source basis
and complements are fixed during this count.

## 2. Extend the quotient map inside the two capacities

Fix one j0 and write L=j0(J). Quotient the target capacities by L. Their
dimensions are c-j and d-j, and their intersection has dimension H=tau-j.
The remaining source parts have dimensions alpha and beta and have zero
intersection. Choose the image P of the alpha-dimensional source part in
Cbar/L, and put i=dim(P∩(T/L)).

The number of such P is the classical subspace-intersection count

`[H choose i]_q [c-tau choose alpha-i]_q q^((H-i)(alpha-i))`.

Indeed choose its intersection in T/L, choose its projection in a fixed
complement of T/L in Cbar/L, and choose the graph map from that projection
to (T/L)/(P∩T/L). The graph has (H-i)(alpha-i) free field entries.
There are Inj(alpha,alpha) isomorphisms from the fixed first source part to P.

The second source part must map into Dbar/L with image disjoint from P.
The intersection of P with Dbar/L has dimension i. An injection modulo that
intersection has Inj(d-j-i,beta) choices. Its beta vectors have q^(i beta)
independent lifts. Summing over i gives S.

These choices specify the quotient map modulo L. Lifting the alpha+beta
source basis vectors back through L gives q^(j(alpha+beta)) choices. This
count depends only on dim L=j, so it is the same for every j0 in step1.

## 3. Lift back through the fixed image E

Fix a quotient map on (U+A+B)/U. The source theorem proves that compatible
lifts exist; its common-lift condition is exactly what removes the paired
representative discrepancy. The set of such lifts is an affine space.
Differences between two lifts vanish on U and map Abar into E∩C and Bbar
into E∩D. Their common J values must agree, so they lie in E∩C∩D.
Choose fixed complements of J in Abar and Bbar. The independent free entries
have dimension

`eCD*j+eC*alpha+eD*beta`.

Therefore this step has exactly the third power-of-q factor. Every resulting
map on U+A+B is injective: its quotient is injective, and its kernel on U is
zero because h is injective.

## 4. Complete the ambient basis

The fixed domain U+A+B now has dimension u+s and has an injective image.
For each remaining domain basis vector, choose its image outside the span
of all preceding image vectors. This gives the last product. Multiplying
the four independent counts proves the formula.

In particular, the formula is symmetric under exchange of (A,C) and (B,D),
although the displayed sum treats the first source part first. This is also
checked directly in every positive finite census case.

## Discriminating examples

For the source oblique example in dimension3,

```text
U=E=<e1,e2>, h=identity,
A=<e1+e3>, B=<e3>, C=<e1,e3>, D=<e1,e2+e3>,
```

one has k=1 and ell=0. The count is zero. Each separate capacity can be
satisfied, so separate counts cannot be multiplied.

For `U=<e1-e2>`, h=identity, `A=C=<e1>` and `B=D=<e2>` in dimension2,
delta has rank1, while k=ell=0. There is exactly one completion, the identity.
Replacing k by j would incorrectly give zero.

With no capacities the formula is the ordinary fixed-injection extension
product. With two complementary source blocks of size r and target blocks
of size r, each enlarged by E, the count is
`q^(2ur) |GL_r(F_q)|^2`. With r coupled differences fixed between two target
blocks, the constraints force the identity on both blocks; only the remaining
ambient basis extension is free. These independent product formulas also
check the large-dimensional cases in the receipt.

## Evidence and limits

The independent literal engine enumerates vector sets and complete GL actions.
It uses the polynomial x^2+x+1 for F4 and ordinary arithmetic for prime fields.
The full normalized census covers all fixed ranks in F2 dimensions0–3 and
F3/F4/F5 dimension2: 287,431 contracts, including 64,525 positive counts.
This is a count census, not just agreement of zero/nonzero decisions.
Independent changes of source and target bases put every prescribed injection
of a given rank in this normalized form.

Seventy-eight further contracts with arbitrary prescribed images agree with
PR6533's affine kernel-lattice rank count. Six named controls preserve the
oblique and nonzero-delta cases over F2/F3/F5. Sixteen dimension120 formulas
over field orders2,3,4,9 agree with separate product counts. Two literal
48-dimensional vector contracts agree as well. Four omitted-factor controls,
seven invalid inputs and three actual source-byte corruptions are rejected.

The proof is the all-field result. Finite checks corroborate it; they do not
replace it. The executable basis extractor uses prime fields. The scalar
formula accepts every prime-power order, with F4 checked independently.
The routine counts invertible completions only. It does not count every
singular rank, sample completions, or emit a native operator.

All spaces here are unrestricted linear spaces. Symplectic form, signed phase,
causal access, dirty restoration, physical routing, scalar/basis cost, precision,
stock, tape, compiler and outer costs remain separate. No actual selected
contact, supplier admission, new kappa or selected-frontier change follows.
