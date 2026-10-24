# Exact four-bit support-partition discriminator

**PASS as a finite calibration.** Three explicit invertible weighted monomial matrices satisfy both required conjugate memberships, preserve the stated support partitions, and give 108 exactly nonmonomial terminal sandwiches when the input direction has a nonzero U component. The controls discriminate omitted hypotheses and the previously invalid central-fixed inference. This does not prove the 17-axis or all-width theorem, classify the admissible monomial group, or supply a Gaussian/rank lower bound.

The basis is (q,u1,u2,w), encoded as bits (1,2,4,8). Matrices are 16 by 16, act on column vectors, and compose rightmost first. Every scalar is an exact pair of standard-library Fractions for its real and imaginary parts; all values in these examples are Gaussian dyadics. No floating calculation decides equality, support or monomial membership. A matrix is monomial only if every row and every column has exactly one nonzero entry. The checker verifies invertibility of the positive examples and their transported matrices, so the negative support results do not arise from singular or zero matrices.

For every nonzero translation direction v, the Gaussian is exactly

`C_v = ((1+i) I + (1-i) X_v)/2`.

The inverse is the actual conjugate transpose. The checker verifies C_v^2=X_v for the central instance, Q^-1 Q=Q Q^-1=I, and D^-1 D=D D^-1=I with Q=C_q and D=C_w. In particular C is not treated as self-adjoint or as an involution. The two exact intertwining equations are h Q=Q(Q^-1 h Q) and D h=(D h D^-1)D.

The positive examples are:

* A Toffoli permutation with target q and controls u1,u2, weighted in column x by 2^(u1*u2).
* The same weighted Toffoli with target w.
* The cubic diagonal phase CCZ(q,w,u1), followed by the required transport k=D h D^-1.

For each weighted Toffoli, the Boolean second difference on inputs 0,u1,u2,u1+u2 is the nonzero target vector; this proves the address map is not affine. The nonunit weights are independently retained rather than projected away. Both actual conjugates equal h in these two examples. For CCZ, both actual conjugates are also monomial, but the transported k need not preserve q-cosets. All three h preserve q-cosets, W-cosets and their join; all three transported k preserve W-cosets and the join.

The CCZ transport explicitly sends the q-edge (u1,u1+q), encoded (2,3), to (u1,u1+q+w), encoded (2,11). The address difference becomes q+w. On input q=u1=1,w=0, k has output phase -i, fixing the conjugation orientation. Reversing the D conjugation gives a different matrix; omitting the inverse also gives a different matrix. Moreover Q^-1 k Q is nonmonomial. Thus the old central-fixed inference and the unproved reuse of the original Q-conjugacy condition after transport are both rejected by actual matrices. The correct join partition is preserved.

For each transported example, the checker uses all six directions v in span(q,u1,u2) with a nonzero U component and all three nonzero directions t in span(q,w). It verifies that the monomial address permutation cannot send v-cosets to t-cosets and computes both

`C_t^-1 k C_v` and `C_t^-1 k C_v^-1`.

Every one of the 3*6*3*2=108 exact matrices is nonmonomial, with an explicit branching column and exact coefficients saved in RESULT.json. The first family is the requested two-sided intertwiner discriminator; the second also checks the same-support inverse convention relevant to the two inverse outside Gaussians in the source endpoint. These finite examples do not substitute a sign change for a general theorem about arbitrary phases.

The controls change the answer when a premise is removed:

* The literal swap u1<->w remains monomial and satisfies Q^-1 h Q=h, but D h D^-1 is nonmonomial. Its column zero has rows 0,2,8,10 with coefficients 1/2,i/2,-i/2,1/2. It breaks the W and join partitions.
* Using that swap itself as k, C_w^-1 k C_u1 is exactly the original monomial swap. Thus a blanket nonmonomial conclusion for arbitrary monomial k, without join preservation, would be false.
* When the nonzero-U condition is removed, C_q^-1 k C_q for the weighted target-q example is monomial. The condition is substantive.

Normal and optimized runs use `python3 -I [-O] -B -W error check_support.py`. They complete in less than one second locally and produce byte-identical RESULT.json and MATRICES.json. MATRICES.json retains exact sparse entries for the main Gaussian, positive and control matrices, while RESULT.json records every terminal digest, row/column support counts and branching witness. Source hashes are checked before and after each run; no source file is edited. No source model, large alphabet enumeration, solver, native circuit, compiler, factory or Lean process runs.

The proposed support-partition proof is separately reviewed. These finite examples neither establish its tensor-separation argument nor discharge its finite complete-product support premise. Fixed finite generating alphabets with unbounded width-dependent products remain outside that proposed theorem, as the revised proof states.

Credit the released four-control equations, source real normalizers, native/Clifford/helper/precision/compiler lineage, and the proof's retained contributors. This bounded exact discriminator was produced with OpenAI Codex assistance. It admits no physical implementation, paid cost, caller transfer or kappa improvement.
