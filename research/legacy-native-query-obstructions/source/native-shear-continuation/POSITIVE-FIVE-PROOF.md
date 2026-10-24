# Five positive plane queries cannot complete three roles

Work in Mat_3(F2[G]), where G is a group of rational plane ADDRESS maps.
Each native query has the form H_N(g)=I+N(g-1). The binary matrix N is
a rank-one idempotent. The rational map g is nonidentity, has positive
determinant, and has rank(g-I2)=1. The complete arbitrary-input endpoint
is z I3, where z=-I2. This packet proves that five such queries cannot
reach the endpoint. It gives no integer-multiplication lower bound or
kappa gain.

## Two normal forms from ADDRESS support

A product of two positive rank-one plane maps cannot equal z. If h g=z,
then h=-g^-1. The eigenvalues of g are 1 and lambda=det(g)>0. The
eigenvalues of h are -1 and -1/lambda. Neither is one, contrary to
rank(h-I2)=1. A singleton is also not z.

Every target ADDRESS branch therefore selects at least three queries.
The target-subset rank argument in PROOF.md requires three distinct first
selected query indices and three distinct last selected query indices.
With five queries, the last indices must include 3, 4 and 5. The first
indices must include 1, 2 and 3. Write the chronological maps A,B,C,D,E.
The branches with last index 3 and first index 3 give

    C B A=z,             E D C=z.

Thus E D=B A. A target branch with last index 4 is one of 124, 134,
234 or 1234. There are no shorter target branches.

- Branch 1234 forces D=I2, which is excluded.
- Branch 124 forces D=C and E=z C^-2. If the eigenvalues of C are
  1 and det(C)>0, the eigenvalues of E are -1 and -det(C)^-2.
  This excludes rank(E-I2)=1.
- Branch 234 gives D=A and E=B.
- Branch 134 gives D=C B C^-1=A^-1 B A and E=A.

Consequently every candidate has one of these chronological forms:

    A,B,C,A,B             or             A,B,C,C B C^-1,A,

with C B A=z. This reduction does not assume unit determinants.

## Nonunit positive determinants

Let lambda=det(A), mu=det(B) and nu=det(C). The triple relation gives
lambda mu nu=1. Apply the ADDRESS determinant homomorphism to the
commutative binary group algebra F2[Q_(>0)]. A query with binary
rank-one idempotent N has determinant equal to its ADDRESS determinant
group element: binary scalar conjugation puts N in the form E00 and
puts the query in diagonal form.

The complete endpoint has determinant group element one. In either
five-query form, the product of the five determinant group elements is
lambda^2 mu^2 nu. It must equal one. Thus lambda mu=1 and nu=1.

Suppose lambda differs from one. Restrict G to the subgroup generated
by the five query maps. The relation CBA=z puts the endpoint in this
subgroup. Its determinant image is the infinite cyclic subgroup generated
by lambda. Map lambda^n to
1+(n mod 2)e in F2[e]/(e^2). This is a valid group homomorphism because
lambda is positive and differs from one. It extends to the binary group
algebra. Four queries map to I+e N_i. The C query and the endpoint map
to identity. Therefore the four corresponding projectors sum to zero.

The four-projector rank argument in PROOF.md applies without using
determinant signs. It forces the remaining C image to be a coloop.
The stronger coloop lemma then forces C=z, contrary to rank(C-I2)=1.
This excludes lambda != 1.

## The unit determinant case has one rational model

Now lambda=mu=nu=1. Each nonidentity rank-one update is a rational
unipotent. Choose a rational basis so that

    A=[1 2; 0 1].

Write B=[1+s t; r 1-s]. Since C B A=z and C is unipotent,
tr(B A)=-2. Hence r=-2. The equation det(B)=1 gives t=s^2/2.
The conjugation S^-1 B S, with S=[1 -s/2; 0 1], leaves A fixed and gives

    B=[1 0; -2 1],        C=[3 2; -2 -1].

This is a common rational conjugation of all ADDRESS maps. It preserves
every subset-product collision. Thus the two exact canonical forms
cover every unit determinant candidate from the preceding reduction.

## First form: A,B,C,A,B

The only target ADDRESS subsets are 123, 234 and 345. The full selected
word has ADDRESS product C^-1, which occurs in no other subset. These
finite assertions follow by multiplication of the 32 canonical subsets.
The checker records all 32 products with exact rational entries.

Write N_i=u_i v_i^T and Q_i=I-N_i. The three target coefficients are

    K123=Q5 Q4 N3 N2 N1,
    K234=Q5 N4 N3 N2 Q1,
    K345=N5 N4 N3 Q2 Q1.

Each has rank at most one. Their sum must have rank three, so all three
must be nonzero. The first forces v2^T u1 and v3^T u2 to be nonzero.
The last forces v4^T u3 and v5^T u4 to be nonzero. Therefore

    N5 N4 N3 N2 N1
      =(v5^T u4)(v4^T u3)(v3^T u2)(v2^T u1) u5 v1^T

is nonzero. But it is the sole coefficient of C^-1. The complete
endpoint requires that coefficient to be zero. This is a contradiction.

## Second form: A,B,C,C B C^-1,A

The only target ADDRESS subsets are 123, 134, 235 and 345. Exact
canonical multiplication checks that no four- or five-query subset
adds another target term. Put

    M=Q4 N3 N2 + N4 N3 Q2.

The target coefficient is

    Q5 M N1 + N5 M Q1.

The first term has rank at most one because N1 has rank one. The second
has rank at most one because N5 has rank one. Their sum has rank at
most two and cannot be I3. This is a contradiction.

## Verification and scope

The proof uses exact formal group-algebra equality. Equality on one
finite ADDRESS grid is not sufficient. Free binary DATA basis changes
must first be absorbed into effective rank-one idempotents. The separate
note independent-audit/HELPER-AUDIT.md extends the argument to arbitrary
dirty helpers that return identity on every input. Initialized, discarded,
or other partial helper endpoints, higher-rank ADDRESS maps, and a
different compiler model are outside the proof.

The finite backup in positive_five_check.py uses the two literal rational
normal forms. Common scalar conjugation fixes the first projector to
E00. Each form starts with all 28^4 remaining projector choices. Complete
span and no-coloop conditions retain 82,320 choices. Exact replay found
no word in either form. The proof above does not depend on this search.

No short word, supplier gain, PR, or global novelty claim was produced.
AI assistance was used in the proof, search and independent audit.
