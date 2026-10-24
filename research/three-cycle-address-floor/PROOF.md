# One coordinate three-cycle costs six calls in every finite workspace

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This is a computer-assisted theorem with a written uniform reduction and an
explicit finite exclusion. It is not proof-kernel verification.

## Statement

Let n≥3 and R≥1 be finite. In M_R(F2[GL_n(F2)]), a paid call has the form

    D(g,N)=I+([g]+[e])N,   g=I_n+E_ij, i≠j,
    N=u v^T, v^T u=1.

Free scalar GL_R(F2) matrices may appear anywhere. There are no free address
maps. Equality is coefficientwise in the full group algebra for arbitrary
inputs. Let c cyclically permute three address coordinates and fix the others.
Then diag([c],[e],...,[e]) costs exactly six paid calls. Every additional
register is arbitrary dirty input and is individually restored. The result is
uniform in both address spectators and register workspace.

The lower bound also applies to any full formal endpoint having a nonzero
coefficient of [c] in any matrix entry. This does not make costs additive for
several target entries. The upper bound here concerns the stated single target.

## 1. Formal support survives arbitrary scalar mixing

For a matrix M over the group algebra, write supp(M) for the group elements
with a nonzero binary coefficient matrix. Scalar matrices have support contained
in {e}. A paid factor is

    D(g,N)=[e](I+N)+[g]N.

Expand a word containing m paid calls, keeping all intervening scalar matrices.
Every term chooses either e or g_i at each paid position. Its group element is
therefore a subword of the paid address-label sequence, in the same written
multiplication order. Its coefficient is the corresponding ordered product of
binary matrices, including the free maps. Cancellation can remove group
elements; it cannot introduce an element absent from every expanded term.
Thus if [c] has a nonzero coefficient, some paid-label subword of length at
most m multiplies to c. Reversing written order gives its chronological CNOT
execution; CNOT labels are involutions but no commutation is assumed.

This argument does not use a nonfaithful natural representation. It uses the
basis of the full group algebra. It does not require an augmentation
normalization or any bound on R. Rank-one idempotence is part of the paid model
but is not needed for this support implication.

It remains to exclude an ordinary address CNOT word for c with at most five
calls, uniformly in n. Such a word is an invertible n×n binary matrix word.

## 2. A short address word writes at most one spectator

Use chronological row operations starting at I_n: (i,j) replaces row i by
row i plus row j. Every intermediate matrix is invertible.

Each of the three cycled rows must be written at least once, since its final
row differs from its original unit row. If a spectator row is written exactly
once, before that write it is its original unit row e_i. Its sole write adds a
nonzero donor row: invertibility implies every row is nonzero. It is never
written again, so its final row cannot equal e_i, contradicting restoration.
Consequently every written spectator receives at least two writes.

At a total budget of five, the three active rows use at least three writes,
leaving at most two. Hence at most one spectator is ever written. Let S contain
the three cycled coordinates and every written spectator. Then |S|≤4.

## 3. Deleting never-written donors is a valid restriction

Let U be the complementary set of never-written coordinates. Every generator
of the short word writes a row in S; it may read a donor in S or U. The
coordinate subspace V_S={x:x_U=0} is invariant under every generator: no U
coordinate is written. Restriction to V_S sends a CNOT with donor in S to the
same coordinate CNOT on S, and a CNOT with donor in U to the identity. Deleting
the latter calls gives a word of no greater length on |S| coordinates.

Restriction respects the entire ordered product because V_S is invariant at
every step. Equivalently these generators lie in the block-upper-triangular
subgroup with lower blocks (0,I_U), and taking the S×S block is a homomorphism
on that subgroup. No projection from arbitrary GL_n matrices is asserted.
The final c restricts to the same three-cycle, fixing the possible fourth role.

Setting x_U=0 here is a mathematical restriction of an identity required on
all inputs. It does not authorize clean ancillas in the original paid model.
The surviving fourth coordinate remains arbitrary and must be restored.

Relabel the three active coordinates 0,1,2 and the possible spectator 3. If
|S|=3, pad with an untouched fourth coordinate. It is enough to exclude

    C=(e_1,e_2,e_0,e_3)

as a product of at most five among all 12 row CNOTs on four coordinates.
The inverse cycle has the same minimum by reversing a word.

## 4. Complete four-coordinate exclusion

The package recomputes, without pruning or symmetry reduction, the full balls
B_2 and B_3 around I_4 for the 12 CNOT generators. Exact distance layers are

    1, 12, 96, 542;   |B_2|=109, |B_3|=651.

Every word of length at most five splits into factors X and Y with X∈B_3 and
Y∈B_2. Therefore C would require X^(-1)C∈B_2 for some X∈B_3. The primary
checker tests all 651 possibilities and finds zero. It also reconstructs and
checks every stored word, so the list is tied to the actual generators.

A separate implementation uses the literal action on all 16 Boolean address
vectors, rather than row-bitset matrices or primary multiplication/inversion.
It independently forms its radius-two ball, the target radius-two ball, and
all 12 outgoing edges at each of 109 radius-two states. No middle edge reaches
the target ball; the two radius-two balls do not intersect either. This covers
all five-or-fewer words, including lengths below five. Its independently formed
radius-three ball agrees with the primary ball after exact conversion.

The finite exclusion is a premise supplied by these complete executable
checks, not by stored counts alone. Sections 1–3 show why it suffices for all
n and R. The proof does not inherit PR4968's n=3,R=2 search or its all-pairs
census, and no large finite search is run.

## 5. Six-call upper bound

Chronologically execute

    (0,1),(1,0),(0,1), (1,2),(2,1),(1,2).

The first three calls swap coordinates 0 and 1, the last three swap 1 and 2.
The endpoint is C as displayed. On target register 0 use N=E_00 for each paid
factor. The formal product is diag([c],[e],...,[e]); every other register and
address spectator is fixed. This proves attainment for every n≥3,R≥1.

The checker expands the group-algebra word and also tests dense scalar
conjugates and inverse cycles. Omitting a call, using an incorrect label,
accepting only a natural image, or dropping restoration are separate controls.

## 6. Scope and remaining question

The result closes the single-three-cycle all-dimension boundary in PR4968.
Support gives only the largest individual target word-length floor, not a sum
across target registers. Multiple three-cycles, mixed cycle/permutation targets,
and the optimum of the regular-representation cut relaxation remain open here.
Different paid labels, free address maps, unreturned address spectators and
clean-only endpoint contracts are outside the statement. This is a formal cost
screen; native realization, physical tariffs, compiler/stock/precision and a
new multiplication exponent are not supplied.
