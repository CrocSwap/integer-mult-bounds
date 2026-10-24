# Exact four-call minimum with every odd S4 label

## Model and theorem

Let A=F2[S4] be the full formal group algebra, with [g][h]=[gh]
and gh acting as g after h. Fix any finite register count r>=2.
All register inputs are arbitrary. A paid call has unit cost and matrix

    D_N(g) = I + ([g]+[e])N = [e](I+N) + [g]N,

where g is any odd permutation and N is any rank-one idempotent in M_r(F2).
Every scalar GL_r(F2) map is free and may occur anywhere. No address map,
reset, clean register, erasure or additional operation is free.

For any nonidentity a,b in A4, including a=b, the target is the complete
formal matrix

    T = diag([a],[b],[e],...,[e]).

In particular all extra registers return individually to their arbitrary
entrance values and every off-diagonal coupling is zero.

**Theorem.** The exact paid-call minimum is four, independently of r.
This remains a four-call lower bound if any subset of the odd labels is
permitted; attainment below uses the full odd-label alphabet.

## 1. Normalize the scalar maps

For any scalar G in GL_r(F2),

    G D_N(g) G^-1 = D_(G N G^-1)(g).

Conjugation preserves rank one and idempotence. Move all free scalar maps
to the right, to write an arbitrary word as a product of the same number
of paid factors followed by one scalar map S.

The augmentation homomorphism aug:A->F2 sends every group element to 1.
It sends each paid factor to I, and sends T to I. Applying it to the word
shows S=I. Thus it suffices to study a product of paid factors alone.
This step counts scalar mixing at intermediate cuts and does not restrict
which dirty roles a paid projector can couple.

## 2. Every valid word has even length

The sign map S4->C2 extends to an algebra homomorphism

    pi:A->F2[C2],       pi([g]) = z for odd g,
    z^2=1,             pi([g]) = 1 for even g.

The ring F2[C2] is commutative. A scalar basis diagonalizes N to
`diag(1,0,...,0)`, since an idempotent splits its image and kernel.
Consequently pi(D_N(g)) is similar to diag(z,1,...,1), and its determinant
is z. Determinants multiply over this commutative ring. A product of L
paid factors therefore has determinant z^L after pi, whereas pi(T)=I
has determinant 1. The formal basis elements 1 and z are distinct even
in characteristic two. Hence L is even.

This is the sign-determinant method already used by Cinna Davis in #1734.
No determinant of a matrix over the noncommutative algebra A is taken.

## 3. Two calls cannot deliver two active even targets

Write a formal matrix as M=sum_g [g] C_g, where C_g is a binary scalar
matrix. Define its nonidentity even coefficient rank sum by

    E(M) = sum_(g even, g!=e) rank_F2(C_g).

The proposed target always has E(T)=2. If a!=b, its two nonidentity
even coefficients are the two distinct coordinate projectors, each of
rank one. If a=b, the single coefficient at a has rank two. Restored
spectators contribute only to the identity coefficient.

For odd s,t and rank-one idempotents N,M, direct multiplication gives

    D_N(s) D_M(t)
      = [e](I+N+M+NM)
        + [s](N+NM) + [t](M+NM) + [st]NM.       (1)

Repeated group labels in (1) are combined by addition in F2. The labels
s and t are odd. Thus the only possible nonidentity even label is st.
If st=e there is none. Otherwise its coefficient is NM, whose rank is
at most one. Therefore E(D_N(s)D_M(t))<=1, contradicting E(T)=2.

Zero calls cannot realize T because a and b are nonidentity formal basis
elements. Section 2 excludes one and three calls, and (1) excludes two.
Every valid word therefore has at least four calls. This is a written
argument for every finite r, rather than an inference from a register census.

## 4. Four calls attain every target

Fix the odd transposition tau=(12). For each even h, put u_h=tau h.
It is odd, and tau u_h=h. If E_i is the i-th coordinate projector, then
idempotence gives the formal identity

    D_(E_i)(g) D_(E_i)(h) = D_(E_i)(gh).

It follows that

    D_(E_1)(tau) D_(E_1)(u_a)
    D_(E_2)(tau) D_(E_2)(u_b) = T.              (2)

Equation (2) uses four paid calls, requires no extra registers or scalar
changes, and acts identically on every dirty spectator. Some u_h are
four-cycles, so the larger paid alphabet is used. These calls are
invertible but need not be involutions; their inverses use inverse labels.

## Scope and predecessor boundary

Cinna Davis's #1749 establishes a finite four-role result for eight
noncommuting three-cycle pairs using only adjacent transpositions.
Ross Richardson's #1989 already proves all-register exact inversion tariffs
for that adjacent-label alphabet, including those pairs. Neither earlier
statement is claimed as new here. The new theorem allows every odd S4
permutation at unit price, including nonadjacent transpositions and all
four-cycles, and covers every ordered pair of nonidentity even targets.
The proof combines the credited sign method with the two-call coefficient
rank sum in (1). No literature priority is claimed for determinant parity,
group-algebra expansion, rank submultiplicativity or coordinate projectors.

This is a scoped formal-alphabet proof. It supplies no native address
implementation, physical scalar or routing price, precision bound, stock
bound, supplier admission or complete multiplication theorem. All such
obligations remain unproved here. The selected frontier is unchanged.
