# Arbitrary complex coefficients in the exact eight-term E8 decoder model

## Statement and convention

Let R be the matrix of the live true E8 roots, one representative of each
of the 120 real root lines, after a puncture P with `p=|P|<=24`. Put
`G=R R^transpose`. Let D,T be arbitrary **complex** matrices with exactly
eight columns satisfying

```text
D T^transpose = 2G
```

on **every** live row-column pair. Transpose is ordinary transpose, never
conjugate transpose. Each term costs the F2 rank of the PR717/PR968 label
pairing between the nonzero supports of its two columns. Then

```text
sum(term costs) >= max(72-p,56).
```

The lower bound is attained, over the choice of puncture set and decoder
at each size p, by PR968's real examples. Consequently the best ratio
over this class remains `56/104 = 7/13`, attained only at p=16. This does
not say every puncture of a given size admits an attaining decoder.

The new scope is arbitrary complex coefficients in the exact all-pairs,
eight-term model. PR968's proof explicitly defines D,T to be real. Its
real theorem is not being corrected. This note supplies the complex
bridge, including the point where a verbatim reuse of the real argument
would be invalid.

## Inherited real geometric facts

We use the pinned PR968 proof's label model and finite facts. Its label
space has dimension nine with nondegenerate symmetric pairing
`N[i,j] = (<r_i,r_j>+1) mod 2`. For label spans U,V,

```text
rank(N restricted to U x V) >= dim(U)+dim(V)-9.
```

The required real-normal facts are:

1. For any nonzero real normal w, reducing the label span of its surviving
   support to dimension at most seven requires at least 25 punctures.
2. With at most 15 punctures, a support span can have dimension eight
   only when w is proportional to a root alpha whose own line is
   punctured, or to a D7 flat normal whose unique 14-line violator set is
   punctured. All other real normals require at least 16 punctures.
3. Two different D7 directions have 14-line violator sets with union of
   size at least 21. A reduced root support is the eight-dimensional
   hyperplane `u_alpha^perp`. Its pairing with itself has rank eight.

These are consequences of PR968 F0-F5 and its Lemma 1. The eight
hyperplane-flat census rows, the all-120-root check and the 1,080-direction
D7 orbit are replayed by the package. The **standard classification of
real root-spanned E8 hyperplanes, PR968 F6, remains a cited premise**, and
the written Lemma 1 argument remains inherited. The finite replay does
not newly prove that classification or enumerate arbitrary complex
coefficients.

## Complex zero flats and support representatives

Write a nonzero complex normal `a=u+i v` with u,v real. Since the roots
are real,

```text
<r,a>=0 iff <r,u>=<r,v>=0.
```

Let Z(a) be the real span of all roots orthogonal to a. A real vector
`w=u+t v`, with t avoiding the finitely many real zeros of the nonzero
linear functions `<r,u>+t<r,v>`, has exactly the same root-zero pattern
as a. Thus every complex support has a real representative. This is a
statement about each support only; it does not assert that independently
chosen representatives still form dual bases.

Call a **genuinely nonreal** if it is not a complex scalar multiple of
a real vector, equivalently u and v are real-linearly independent. Then
`dim Z(a)<=6`. If `dim Z(a)=7`, both u and v lie in the one-dimensional
real annihilator of Z(a), so `a=lambda w` for a real normal w and
nonzero complex lambda.

For a genuinely nonreal a, a generic real representative w has the same
zero flat of dimension at most six. PR968 Lemma 1 therefore implies
that no p<=15 puncture can reduce its support label span to eight.
It follows that **every reduced complex support at p<=15 is complex
proportional to a real root or real D7 normal**. In particular its normal
is nonisotropic for the complex bilinear form:

```text
a^transpose a = lambda^2 (w^transpose w) != 0.
```

This restricted nonisotropy is the missing bridge for the counting
argument. The support-representative lemma alone would be insufficient.

## Exact complex duality and the isotropic pitfall

The live roots span R^8: at least 96 root lines survive, whereas a real
root-spanned hyperplane contains at most 63. Hence `rank(2G)=8`, also
over C. The all-pairs identity implies `col(D)=col(T)=col(R)` over C,
so `D=RA`, `T=RB` for invertible complex A,B. A real left inverse of R
gives `A B^transpose=2I`, equivalently `A^transpose B=2I`. For their
column normals,

```text
a_k^transpose b_l = 2 delta(k,l).
```

Columns on either side are pairwise nonparallel because they form bases.
Over R, cross-term parallelism is also impossible. Over C it is possible
for isotropic directions. In a two-dimensional block put

```text
a = e1+i e2, c = e1-i e2,
A = [a,c], B = [c,a].
```

Then `A^transpose B=2I`, but `a_1=b_2` and `a^transpose a=0`.
Embedding with A=I, B=2I on the other six coordinates gives an exact
eight-term decoder. The package checks all 14,400 root-pair identity
entries for this example. This is a counterexample to extending the
real nonparallel observation verbatim, **not** to PR968's real theorem.

However, two **reduced** cross-term normals cannot be parallel when
p<=15: each is nonisotropic by the previous section, and parallelism
would contradict their zero cross pairing. Exactly this restricted
version suffices below. No constraint is imposed on parallel isotropic
normals whose supports are unreduced.

## The count

For p<=24, support representatives and inherited fact 1 give dimension
at least eight on each side of every term. The label-rank inequality
gives term cost at least seven, hence total cost at least 56. This part
does not use cross-term nonparallelism at all.

For p<=15, call a side reduced if its label span has dimension eight;
otherwise it has dimension nine. If term k has cost rho_k, its saving
`s_k=9-rho_k` is at most the number of its reduced sides.

If any reduced side has a D7 direction omega, transpose the whole decoder
and relabel terms if necessary so that it is a_1. There is at most one
such real projective direction among reduced sides: two distinct ones
would require at least 21 punctures. For l!=1, a reduced b_l cannot have
that D7 direction, by restricted nonparallelism. It is therefore a root
direction beta_l. Complex duality implies the real equation
`omega^transpose beta_l=0`. Its self-line lies outside the support C(omega),
and therefore outside the 14-line violator set contained in C(omega).
At most `p-14<=1` such lines are punctured. The seven b_l are distinct,
so at most one of them is reduced. There are at most eight reduced row
sides and two reduced column sides in total. Thus

```text
sum s_k <= 10 <= p  (this case requires p>=14).
```

If no D7 direction occurs, every reduced side is a punctured root
self-line. Distinct terms use distinct such lines: same-side independence
and restricted cross-side nonparallelism give this. A term using two
different root directions has saving at most two. If both reduced sides
use the same root direction, their supports equal the same eight-dimensional
label hyperplane and the pairing rank is eight, so its saving is one,
not two. Each punctured root line can therefore pay for at most one unit
of total saving. Consequently `sum s_k<=p` and total cost is at least
`72-p`. This completes the arbitrary-complex extension.

## Exact evidence and limits

The verifier independently builds the E8 roots and compares every label
pairing entry with the pinned model. It implements Q(i) arithmetic and
integer denominator clearing to check all root-pair decoder identities.
Three exact examples cover scalar phases, isotropic cross-term coincidence
and twelve seed-44 complex shears. Their support geometry and costs are
checked for 25 puncture sizes. All 25 real attaining constructions are
also phase-scaled and checked with the new arithmetic. These checks expose
failure modes and support the argument; they do not exhaust C-valued
matrices or replace the written quantified proof.

Independent real projection can preserve every support yet destroy
duality: `A=(1+i)I`, `B=(1-i)I` has product 2I, whereas their real parts
have product I. Conjugate transpose likewise changes the model. Both
shortcuts are rejected by exact controls.

Nine or more terms, masked E-graph identities, p>=25, changed label
pairings, physical asymmetric-centre realization, shared-copy pricing,
native circuits and supplier/outer admission remain outside this note.
There is no new circuit, invoice, kappa or all-size multiplication claim.
