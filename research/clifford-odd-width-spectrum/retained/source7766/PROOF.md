# The sharp four-qubit Clifford tensor threshold is thirteen

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Result and exact scope

Use the full Gaussian-dyadic n-qubit Clifford group G, its natural
representation V of dimension `2^n`, the Pauli subgroup P, and scalar
`z=iI`. These are the conventions in
[PR #6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714)
and [PR #7747](https://github.com/CrocSwap/integer-mult-bounds/pull/7747).
The scalar kernel is mu_4 and `G/P = Sp(2n,2)`.

**The four-qubit threshold is exactly T(4)=13.** At width eleven,
exactly two odd-sector blocks are absent, with quotient degrees 595
and 3213. At width twelve their inflated quotient modules are still
absent. All quotient rows occur at width thirteen. Thus the projective
operators are independent exactly at widths f>=13.

| Width | Gram statement |
| --- | --- |
| 10 | Nullity at least 14,400 from a degree-120 Dickson block |
| 11 | Exact nullity 2,733,412,864; exact rank 12,125,935,463,936 |
| 12 | Nullity at least 10,677,394; full nullity is not claimed |
| 13 and above | Full rank 12,128,668,876,800 |

Sections 1--6 give a separate table-independent obstruction. For every
positive n divisible by four, an actual module of degree
`N_minus = 2^(n-1)(2^n-1)` is absent at width `2n+2`. Its missing matrix
block has dimension `N_minus^2`, so `T(n)>=2n+3`. An explicit character
formula gives nonzero null coefficients. Section 7 strengthens the
four-qubit result to the sharp threshold using the published ordinary
Sp(8,2) character table through the retained exact projection.

No physical supplier, new kappa, selected-frontier change or discharge
of any of the five framework assumptions follows. Classical group
representation theory and the cited published table are mathematical
inputs; they are not reconstructed in a formal proof kernel.

## 1. The odd quotient is a tuple permutation representation

The Pauli representation with central character `z -> i` is unique and
has dimension `2^n`. Thus every G-representation R in this sector is
`V tensor Hom_P(V,R)`. The second factor is an honest representation of
`S=Sp(2n,2)`, with action `phi -> R(g) phi V(g)^(-1)`. This does not
assume a splitting of G over P.

For `n=4k`, write

```text
V^(tensor (2n+1)) = V tensor W.
```

Let `d(s)=dim ker(s-I)` on the binary symplectic space E. The Hermitian
Pauli basis makes conjugation by a Clifford a signed permutation. On the
fixed label space, its signs form a character. Varying a lift by Paulis
runs through all those characters. Hence each s has a lift g with
`|tr V(g)|^2 = 2^d(s)` and nonzero trace.

A Gaussian-dyadic number of this squared modulus has phase an eighth root
of unity. This follows by clearing its power-of-two denominator in the
sum-of-two-squares equation. Since `2n=8k`, character division on that lift
gives

```text
chi_W(s) = (tr V(g))^(2n) = 2^(n d(s)).
```

This is the fixed-point character of S on ordered n-tuples in E, including
zero entries. Equality of complex characters gives

```text
W is isomorphic to C[E^n].
```

For n=4 this is exactly the table-independent quotient identification in
Nick Petalas's width-nine proof. The same trace argument proves the stated
extension to every n divisible by four.

## 2. Quadratic characters and an actual stabilizer extension

Use `W_v = i^(a.b) X^a Z^b` for `v=(a,b)` in E. The one-dimensional
Pauli characters with `z -> -1` are indexed by quadratic refinements q
of the symplectic form omega:

```text
lambda_q(W_v) = (-1)^q(v).
```

The sign in Clifford conjugation is invisible in this central sector.
Thus G permutes these characters through the ordinary S action on the
quadratic forms. There are two orbits, with sizes
`2^(n-1)(2^n+1)` and `N_minus`, distinguished by the Arf invariant.

There is an explicit extension on each stabilizer. Put
`Omega = sum_x e_x tensor e_x` and
`b_t = (I tensor W_t) Omega`. The `4^n` Bell vectors form a basis of
`V tensor V`. Direct Pauli multiplication gives

```text
(W_v tensor W_v) b_t = (-1)^(q_0(v)+omega(v,t)) b_t,
q_0(a,b) = a.b.
```

Let q be one of these forms, and let T_q be its stabilizer in G. The
one-dimensional Bell line L_q is preserved by T_q. Its actual action
is a character eta_q, which extends lambda_q. No assumed abstract
extension or choice of projective stabilizer representation is needed.

The swap of the two factors acts on b_t by `(-1)^q_0(t)`. Hence the
minus-Arf Bell lines form the exterior square `Lambda^2 V`, of dimension
`N_minus`; the plus lines form the symmetric square. The action on each
orbit is transitive.

## 3. The Dickson sign is absent on n-tuples in minus type

Fix a minus-type q and put `K=O(E,q)=T_q/P`. The Dickson sign is

```text
delta(s) = (-1)^rank(s-I),       s in K.
```

It is a group character. We use D. E. Taylor's *The Geometry of the
Classical Groups*, Theorem 11.43, printed page 160, for this standard
homomorphism theorem. [Author's text](https://www.maths.usyd.edu.au/u/don/papers/gcg.pdf#page=168)

For q(v)=1, the map `t_v(x)=x+omega(x,v)v` preserves q. It differs from
identity by rank one, so `delta(t_v)=-1`.

Every ordered n-tuple has a negative-sign element in its K-stabilizer.
To prove this, let U be its span. Then `dim U <= n`, so `dim U^perp >= n`.
A minus-type quadratic space of dimension 2n has no n-dimensional totally
singular subspace. Therefore `U^perp` contains a v with q(v)=1. The
transvection t_v fixes every tuple entry and has Dickson sign -1.

Here is one direct justification of the dimension statement. The minus
normal form

```text
q_minus(a,b) = sum_i a_i b_i + a_1 + b_1
```

has `2^(2n-1)-2^(n-1)` zero vectors. If an n-dimensional subspace were
totally singular, it would be a symplectic Lagrangian. Extend its basis
to a symplectic basis. Since q vanishes on its first half, the new
quadratic expression has only hyperbolic products and linear terms on
the second half. Adjusting the paired basis vectors removes those linear
terms. This is the plus form, which has `2^(2n-1)+2^(n-1)` zeros, a
contradiction. The minus form does have an (n-1)-dimensional totally
singular subspace, but the upper bound is what is needed here.

Now a delta-eigenvector in `C[E^n]` must have zero coefficient at every
tuple: its stabilizer contains t_v, which fixes that coefficient but
must multiply it by -1. Thus delta is absent from `W restricted to K`.
This argument uses characteristic zero for the permutation module.

## 4. Induce the missing even-sector module

Inflate delta from K to T_q and define

```text
pi_minus = Ind_(T_q)^G (eta_q tensor delta).
```

It has degree `N_minus` and central character `z -> -1`. It is
irreducible: its restriction to P has each character in the minus orbit
once. A G-invariant subspace must be a sum of some of these distinct
one-dimensional eigenspaces, and transitivity forces either none or all.

On the other hand,

```text
V^(tensor (2n+2)) = (V tensor V) tensor W.
```

Its q-eigenspace for P is `L_q tensor W`. The T_q action there is
`eta_q tensor (W restricted to K)`. Section 3 says that this space has
no `eta_q tensor delta` constituent. Equivalently, by Frobenius
reciprocity, pi_minus has multiplicity zero in the full tensor power.
This proves the missing-constituent assertion.

## 5. Explicit null coefficients and the Gram bound

For any g in G, let s be its symplectic image. On a fixed minus Bell
line, the induced twist multiplies its trace contribution by
`(-1)^rank(s-I)`. This sign is the same for every q fixed by s. The
character is therefore

```text
chi_pi_minus(g)
  = (-1)^rank(s-I) chi_(Lambda^2 V)(g)
  = (-1)^rank(s-I) ((tr V(g))^2 - tr V(g^2)) / 2.       (1)
```

The rank-parity function need not be a character of the whole symplectic
group. Formula (1) follows from the induced character on the quadratic
stabilizers; it does not assert a global one-dimensional twist of V.

Choose one unitary representative U_a per projective Clifford class.
An explicit null relation at width `f=2n+2` is

```text
b_a = conjugate(chi_pi_minus(U_a)),
sum_a b_a U_a^(tensor f) = 0.                          (2)
```

Indeed, the central primitive idempotent
`(N_minus/|G|) sum_g chi_pi_minus(g^(-1)) [g]` acts as zero in this tensor
power. Group its four scalar lifts. Their central factors cancel because
both pi_minus and `V^(tensor f)` have central character -1. This gives (2).
The coefficient at identity is `N_minus`, so the relation is nonzero.
Formula (1) computes every coefficient from its actual operator and binary
symplectic action; no full even-sector character table is needed.

In the central-character ideal of C[G], the pi_minus matrix block has
dimension `N_minus^2`. Semisimplicity gives the same lower bound on the
projective Gram nullity. For n=4, `|G/<z>|=4^4 |Sp(8,2)|` is
12,128,668,876,800, giving the stated rank upper bound.

Finally, normalized tensor Grams satisfy `H_(f+1)=H_f circle H_1` and
`diag(H_1)=1`. The Schur product theorem propagates positive definiteness
from any width to every later width: if `H_f >= cI` for c>0, then
`H_(f+1) >= cI`. Singularity at `2n+2` therefore implies `T(n)>=2n+3`.

## 6. A separate exact quotient-table check for four qubits

This check uses the predecessor's retained CTblLib-derived projection;
the absence proof above does not require a character table. In `Sp(8,2)`,
the minus quadratic-form permutation character is `1+chi_119`. Thus

```text
Ind_K^S(delta)(s) = (-1)^d(s) (1+chi_119(s)),
m = (1/|S|) sum_s 2^(4d(s)) (-1)^d(s) (1+chi_119(s)).
```

The parity uses `rank(s-I)=8-d(s)`. Group the source projection by d.
Its nine exact numerator terms, for d=0 through 8, are

```text
9935585280, -317939712000, 3391368069120,
-15503358689280, 33073083187200, -34139956838400,
17352338964480, -4380866641920, 515396075520.
```

They sum to zero. The zero-dimension character sum is recovered from
orthogonality to the trivial character, not guessed. Replacing the minus
orbit with the plus orbit `1+chi_135` gives multiplicity one. Omitting
the Dickson sign gives a positive multiplicity. These controls distinguish
the missing module from the ordinary exterior-square module and from the
other quadratic orbit.

## 7. Widths eleven, twelve and thirteen give the sharp threshold

Now fix n=4 and write `S=Sp(8,2)`, with order 47,377,612,800. The
complex conjugate natural representation `V*` is the unique Pauli
irreducible with central character `z -> -i`. It gives an honest quotient
multiplicity space just as V does in Section 1. Hence

```text
V^(tensor 11) = V* tensor W11,
V^(tensor 13) = V  tensor W13.
```

On a nonzero-trace lift g, let `a=tr V(g)` and `|a|^2=2^d`.
The exact Gaussian phase identity is `a^4=(-1)^d 2^(2d)`. Therefore

```text
chi_W11(s) = a^11 / conjugate(a) = a^12 / |a|^2 = (-1)^d 2^(5d),
chi_W13(s) = a^12 = (-1)^d 2^(6d).                    (3)
```

Keeping this sign and using V* at width eleven are necessary. An
unsigned tuple character would describe a different representation.

Let b_i be the degree of ordinary quotient row i, and let A_i,d be
the retained sum of `|C| chi_i(C)` over classes with fixed dimension d,
for d=1 through 7. The unique d=8 class is identity. Since the two
characters in (3) equal one at d=0, subtract the trivial character to
eliminate those columns. For p=5 or 6, the multiplicity is

```text
m_i(p) = [i=1] +
 (b_i (2^(8p)-1) + sum_(d=1)^7 A_i,d ((-1)^d 2^(pd)-1)) / |S|.
```

`RESULT.json` lists all 81 multiplicities at both widths. They are
nonnegative integers. Their degree-weighted sums are `2^40` and `2^48`.
At width eleven, the only zero rows are 9 and 22, of degrees 595 and
3213. Their full G-modules have dimensions 9,520 and 51,408. The exact
missing regular block dimension is

```text
9520^2 + 51408^2 = 2,733,412,864.
```

At width thirteen every row has positive multiplicity; the smallest
multiplicity is 651. The complete odd central-character ideal is
therefore represented faithfully, giving the full projective Gram rank.

Width twelve needs no even-sector table. Tensor the width-eleven
decomposition with V:

```text
V^(tensor 12) = (V tensor V*) tensor W11.
```

The P-invariant part of `V tensor V* = End(V)` consists exactly of the
scalar identity, since V is Pauli-irreducible. S acts trivially on that
line. Thus the entire P-invariant subspace at width twelve is W11.
Every quotient irreducible inflated from S must occur inside this
P-invariant subspace. Rows 9 and 22 are absent there, so their inflated
G-modules of degrees 595 and 3213 are absent at width twelve. This gives

```text
nullity H12 >= 595^2 + 3213^2 = 10,677,394 > 0.
```

Other nontrivial-Pauli-character blocks may also be absent at width
twelve; the stated bound does not enumerate them. Singularity at twelve,
full rank at thirteen and the Schur-product propagation in Section 5
prove **T(4)=13** and independence at every larger width.

The multiplicity calculation has two further exact checks. First,
recover the d=0 class sum by orthogonality and evaluate all nine bins
directly; this agrees with the subtraction formula. Second, the squared
character in (3) is the permutation character on 2p ordered vectors.
Witt's lemma counts its S-orbits by the tuple kernel and the alternating
form on its quotient. For quotient dimension r and radical dimension u,
embedding in E is possible exactly when `r+u<=8`. There are
`[2p choose r]_2` kernels, `[r choose u]_2` radicals, and
`|GL(r-u,2)|/|Sp(r-u,2)|` nondegenerate alternating forms on the quotient
by the radical. Summing these counts gives the exact character norms
at tuple lengths ten and twelve. Both the multiplicity-square sums and
the fixed-dimension histogram moments agree with these separate orbit
counts. The argument permits tuple length above eight: the quotient
rank, rather than the number of tuple positions, is at most eight.

The original CTblLib 1.3.11 archive and its `ctosymp1.tbl` member were
SHA-256 authenticated. The unchanged predecessor extractor rederived
all 81 projected rows and fixed-dimension counts from that source.
The published table remains an input; matching bytes and character
identities do not constitute a reconstruction from group multiplication.

## Verification and limits

The verifier checks all 200,787 four-dimensional subspaces of F2^8. Every
one contains a nonsingular vector for the fixed minus form. A separate
extension enumeration gives singular-space counts `1,119,1071,765,0` in
dimensions zero through four. Orthogonal-complement bases verify the
fixing witnesses. All 136 nonsingular transvections preserve the form
on all 256 points and have odd Dickson sign. All 18,496 pairs have even
sign. A complete 120-element minus orthogonal group in dimension four
also checks all 14,400 sign products and exact tuple-character sums.

Literal four-qubit calculations check all 65,536 Pauli/Bell character
pairs, 65,536 Bell inner products and 5,120 Bell images under all twenty
Gaussian Hadamard, phase and CNOT generators. They give the actual
120/136 orbits. Exterior-square traces also agree with a separate sum
of 120 two-by-two minors for each generator. Formula (1) gives twisted
characters `-64i`, `8i` and `24` on the phase, Gaussian Hadamard and
CNOT generator types, respectively.

Scope controls exhibit a plus-type singular four-space and a five-tuple
whose minus-type orthogonal complement is singular. In the complete
small group, the sign multiplicity is zero at tuple lengths 0,1,2 and
positive at length 3. These are controls on the tuple argument, not
claims about the four-qubit width-eleven tensor. The unchanged width-nine
source checker and both exact signed quotient sums also pass.

The all-n Dickson statement is written mathematics, supported by finite
checks at n=4. No full four-qubit group or tensor matrix was materialized.
The width-ten and width-twelve nullities remain lower bounds; more missing
blocks may exist at those widths. The exact endpoint T(4)=13 uses the
published character-table input. Other qubit congruence classes, sharp
conditioning, native implementation and full caller pricing remain open.
The full three-qubit suite, selected cold replay, Lean and Docker were
not run. No independent human or proof-kernel acceptance or global
priority is claimed. All five framework assumptions remain unchanged.
