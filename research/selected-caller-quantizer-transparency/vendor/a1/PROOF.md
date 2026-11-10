# Exact native traces and the complete selected tensor interface

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a source-bound algebraic certificate and a written universal argument.
It proves the exact-operator assertion labeled `native_all_columns` for the
pinned selected P104 native layer and its assembled caller. Physical
implementation, selected-rate dispatch, owned allocation/erasure and the other
framework premises remain separate. No admission record or kappa is changed.

## 1. What must be composed

The selected word is DreamingOfClouds' #6030 at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Its local certificate, the
all-forward P104 caller and the native tensor interpretation are different
objects. A dense equality at column width one cannot identify a sum of
different native group elements at all widths. Conversely, equality of two
*products* of unitary native gates is sufficient once every factor is lifted
columnwise and exterior scalar coefficients remain exterior.

The local common-chart argument is already present in the P104 source and
#6635. #6043 independently checked every selected native operator densely.
#6546 supplies a numerical execution and tensor lift of the fixed local word,
and explicitly separates that from identifying recursive callers with it.
#5442 proves an all-width certificate for the different #5413 caller.
The contribution here is an independent exact trace acceptance mechanism and
its complete source-bound composition for the selected #6030 local word,
helpers, wrappers and all-forward caller. These predecessor identities are
credited, not asserted to be new lemmas.

## 2. Exact traces of the native grammar

Let the address dimension be n. Accepted primitive gates are an invertible
binary address permutation P_A, a binary translation X_v, a phase i^c,
a diagonal i^q(x), and

    C_v^s = ((1+s*i) I + (1-s*i) X_v)/2,  s in {+1,-1}.

Here q is a Z/4 polynomial with arbitrary linear coefficients and even mixed
coefficients. The source additionally requires its symmetric quadratic matrix
and diagonal-parity convention. The checker validates this grammar, every
binary inverse and every sign before using a trace. P_A and X_v permute an
orthonormal basis, diagonal phases have modulus one, and X_v is a self-adjoint
involution. On its +/- eigenspaces C_v^s has eigenvalues 1 and s*i. Thus every
accepted gate and every compared complete product is unitary, including its
normalization. Scalar ADD/COPY/SCALE programs are **not** passed to this test.

Introduce n initial-address bits x and one binary branch t for each C gate.
The identity

    C_v^s = (1+s*i)/2 * sum_(t=0,1) i^(-s*t) X_v^t

expresses every path amplitude as a known Gaussian dyadic scalar times
i^Q(x,t). Throughout the circuit each current address bit is an affine
Boolean form in x and previous branch variables. A phase gate contributes
only a quadratic polynomial modulo four: for a parity L=sum x_j mod2,

    L = sum x_j - 2 sum_(j<k) x_j*x_k  (mod 4),

and twice a product of affine Boolean forms has degree at most two modulo
four. Translations, address permutations and C branches update affine forms.
Induction over the literal gate list therefore gives exactly

    tr(U) = [product_C (1+s*i) / 2^h]
            * sum_(z: final_address(z)=initial_address(z)) i^Q(z),

where h is the actual number of C gates. The final equality is an affine
binary system. RREF either detects inconsistency (trace zero) or parametrizes
every satisfying assignment exactly once by free variables. Substitution into
Q preserves the displayed quadratic form. No exponential path enumeration is
performed by the checker.

### Quadratic elimination

Write Q=c+sum a_j x_j+2 sum_(j<k) b_jk x_j*x_k modulo four. All expressions
below are exact, including constant phase and normalization.

If a_j is odd, put L=sum_(k!=j) b_jk*x_k mod2. Summing x_j gives

    sum_(x_j=0,1) i^(a_j*x_j+2*x_j*L)
      = (1+i^a_j) * i^(-a_j*L).

Delete x_j, multiply the accumulated Gaussian integer by 1+i^a_j, and add
-a_j*L to the remaining quadratic. The parity expansion above implements
that update, including its new mixed terms.

If all a_j are even and b_jk=1, write the terms involving x_j,x_k as
2(x_j*x_k+u*x_j+v*x_k), where u,v are affine Boolean forms on the other
variables and include a_j/2,a_k/2. Then

    sum_(x_j,x_k in {0,1}) (-1)^(x_j*x_k+u*x_j+v*x_k)
      = 2*(-1)^(u*v).

Delete both variables, multiply the accumulated scalar by 2, and add 2*u*v
to the remainder. If no mixed term remains, an isolated coefficient 2 makes
the sum zero; each isolated coefficient 0 contributes 2. Finally multiply
by i^c. Each step eliminates at least one variable. This proves
`gauss_sum`, independently of a Clifford tableau or any selected basis state.

For k=n+h path variables and g literal gates, this implementation uses a
polynomial number of bit/integer operations. A deliberately coarse bound is
O(g*n^2*k^2+k^4) elementary set/coefficient operations: dense affine
substitution costs at most O(k^4), and elimination at most O(k^3). Stored
phase data use O(k^2) bits/entries, and Gaussian numerators have O(k+h) bits.
The claim is polynomial finite-certificate verification, not an asymptotic
runtime bound for multiplying input integers.

### Trace acceptance

For two checked unitary D-by-D matrices U,V,

    ||U-V||_F^2 = 2D - 2 Re tr(V* U).

Consequently exact `tr(V* U)=D` implies U=V on every input. The converse is
immediate. The circuit for V*U is the chronological word for U followed by
the reversed adjoints of V. The checker computes an exact Gaussian numerator
and power-of-two denominator, cancels powers of two, and requires precisely
`(2^n,0,0)`. A global i phase is not discarded. The test does not assume that
equal unsigned symplectic actions, equal output at zero, or equal traces of U
and V separately suffice.

The frozen candidate recipes are rebuilt using the credited source compiler,
and their **complete** payload hash must equal the selected RESULT.json
registration. The acceptance engine imports neither that compiler nor its
Pauli/column verifier. The expected chart circuits come from the pinned frame
definition. An error common to a candidate compiler's tableau and zero-column
implementation is not a shared dependency of this trace calculation.

## 3. All-column tensor interpretation

For f>=1 and an arbitrary spectator coefficient space S, write
L_f(U)=I_S tensor U^(tensor f), with the fixed address shuffle placing columns
in the source's slot order. Then

    L_f(UV)=L_f(U)L_f(V),  L_f(U*)=L_f(U)*.

This is a statement about full arrays, including arrays correlated across
columns and spectators: tensor basis vectors span the full space. It does
not require a pure-tensor input or zero spectator coordinates.

Every accepted native equality is an equality between complete products.
Therefore each such equality lifts under L_f. A rank-r positive child lifts
to the identical elementary C on r*f selected binary axes. A monomial with
constant phase c contributes i^(c*f), and its remaining phase is the sum of
the one-column phase polynomials at all columns. A scalar coefficient a in a
register ADD or SCALE remains a, not a^f. In particular L_f(iI)=i^f I differs
from the exterior scalar iI in general. Likewise the width-one expansion of
C_v into two scalar-weighted translations is not an allowed termwise tensor
rewrite. The verifier tests both errors with exact width-two witnesses.

The same argument extends a complete local address operator by identity to
any complement and conjugates it by any complete coordinate bijection.
Thus it supplies the algebraic input needed by #6878's occurrence-specific
full-field embeddings. It does not price those bijections or replace their
physical field-placement and ownership hypotheses.

## 4. Complete caller join

### Statement and hypotheses

Fix exactly the WORD, RESULT, CONTROLLER, source chart definition, compiler
recipe payload and original port data pinned in SOURCES.json. Let f be any
positive integer. Each productive register contains an arbitrary vector in
S tensor (C^(2^145))^(tensor f), for any finite-dimensional coefficient space
S; equivalently one may use the source's 265 rows and its 120 unused identity
spectator rows. The 13,444 productive registers are independent inputs, not
copies or zero-filled helpers. Interpret native products by L_f, rational
register coefficients as exterior scalars, and INIT/CLEAR by the ideal owned
zero/reset operations in the source semantics. All coordinate maps below are
complete bijections, including their complementary coordinates.

Under these hypotheses, the literal 18-forward-call supplier with its 16
five-step wrappers, 15 thin queries, whole-idle jobs, scalar boundary programs
and whole-job adapters has the stated diagonal positive-Gaussian endpoint on
all 13,444 arbitrary productive inputs and returns its 29 local owned labels
to zero. Its paid and productive profiles are exactly those in the selected
RESULT. The proof is uniform in f and S. This is a theorem of the exact typed
algebraic program; it assumes ideal owned resets and native calls. It does not
establish an encoded tape implementation, an accelerated primitive tariff,
precision control, analytic recovery, or physical owned erasure.

### Local chart induction

Write Gamma_a for the full signed canonical chart associated with frame a.
The independent trace acceptance checks each selected native recipe as

    M_left G_r M_right = Gamma_b Gamma_a^*,

where G_r is the product of positive elementary Gaussians on the first r
axes. This includes 2,886 distinct MOVE pairs, the additional whole-helper
pairs, and all 208 ordinary main adapters. The union has 2,922 pairs. The
identity is between full operators, so Section 3 gives its exact L_f lift.

If a register's physical value is L_f(Gamma_a) z, a MOVE to b makes it
L_f(Gamma_b) z. ADD at a common current chart performs

    L_f(Gamma_a) z + c L_f(Gamma_a) w
      = L_f(Gamma_a) (z+c w).

SCALE is the same linearity identity; a COPY uses an owned zero target.
The coefficient c is retained outside L_f. All actual 18,404 ADD, 861 SCALE
and 23 COPY events satisfy their current-chart and ownership tests, rather
than relying on a declared common-chart convention. INIT establishes zero
and its recorded chart; CLEAR deletes only a currently owned value. This
last operation is an inherited ideal reset, not a deduction that arbitrary
nonzero data can be physically erased for free.

The exact rational sparse replay starts with 799 independent formal inputs,
including the 29 owned entrance labels. After the 22,803 literal events it
checks every endpoint coefficient: the 770 public coordinates are unchanged
except Y_r -> Y_r+X_r at the 104 selected pairs; every owned entrance column
has been eliminated and every owned output is zero. There are 31 distinct
owned lifetimes, with peak 13. Finite verification determines this one fixed
word's rational identity. The preceding symbolic induction, rather than a
finite sweep of f values, proves that identity for all f and S.

For each main port q put Q=C_q^+ and H_9=product_(j<9) C_(e_j)^+.
The actual ordinary main entry/exit recipes are checked against

    A_X = Gamma_initial-X Q^*,
    A_Y = H_9 Q^* Gamma_final-Y^*.

The source entrance frame of X is the one-vector frame [q], but its canonical
chart Gamma_initial-X need **not** equal the translation Gaussian Q. The
actual ordinary A_X above is therefore essential. The other two boundaries
are Gamma_initial-Y=I and Gamma_final-X=H_9. Combining the three nonzero rational endpoint paths with
these exact adapters gives, on the two main registers,

    F_0 = D_0 [[1,0],[Q^(-1),1]],   D_0=H_9 Q^(-1).

The checker verifies all three complete products separately at every port,
including their constant phases. The displayed 2-by-2 notation is a matrix
of native operators and exterior rational coefficients, not a matrix that
is itself tensor-powered.

For every arbitrary helper, the chart endpoint is Gamma_b Gamma_a^*.
Apply M_right^* before the complete local word and M_left^* after it. Its
entire productive endpoint is then G_r. All 69 distinct helper boundary
types are checked as complete products; their multiplicities give all 562
helper inputs. These normalizers are whole-job boundaries, not uncharged
adapters inserted at each recursive child.

### Source raw contacts and arbitrary spectators

The original raw construction uses 265 formal binary axes e_j. At stage s>0
the actual route swaps the source's eight orthonormal q-complement vectors
b_i with its eight fresh axes e_(9+8(s-1)+i), and fixes q and the remaining
orthogonal complement. The source port data are checked to make
(q,b_0,...,b_7) an orthonormal basis. These eight disjoint orthonormal swaps
give a complete involutive orthogonal map R_s. The explicit binary formula
in caller_check.py is checked to perform exactly those swaps and fix q.

A product of translation Gaussians has Fourier-character eigenvalue

    i^p(z),   p(z)=sum_v c_v (v dot z mod2)  (mod4).

Its polynomial has linear and even mixed coefficients, and constant zero.
Polynomial equality therefore proves equality on every character; Fourier
characters form a basis. An even linear difference 2(t dot z) is exactly the
translation X_t, with absolute phase +1. The checker computes the complete
entry/exit translations and their inverses from these polynomials. Their
ordered payload equals the **already registered selected** route hash
`7f4f0ca768ffbc4f93dcff575592c4c67411f46b4289e45b73f715a2ad47b142`.

This is more than comparing abstract frame labels. If a native convolution
path has phase p and the actual entry and exit maps are X_u P_R and X_v P_R,
their executed composition is

    X_v P_R A X_u P_R
      = X_(v+R u) (P_R A P_R).

Thus its eigenphase is p(R z)+2((v+R u) dot z). The checker uses the actual
four contact records to verify both diagonal paths as D_s and the cross
path as D_s Q^(-1), where D_0=H_9 Q^(-1) and, for s>0, D_s is the product
of the eight positive fresh-axis Gaussians. This checks 5,616 composed paths
through all 7,488 actual contacts, including spectator charts on entry and
exit. It does not only compare their marginal source/target phase profiles.

Only stages 0,1,3,...,31,32 occur. All 120 rows of the other stages are fixed
by every actual contact and absent from its translations, main products and
idle products. Taking the nine source rows and the 17 retained eight-row
blocks identifies the actual 145-row supplier. This is a checked application
of the retained-row construction credited to #6878, not a new compression
claim. Every positive main/idle canonicalizer is explicitly completed on
all 145 retained coordinates; the unused 120 rows and arbitrary further
spectators are preserved as identity factors. Section 3 then transports
each equality through the complete occurrence embeddings in #6878. No
assumption about vanishing or independent spectator coordinates is used.

The application to #6878 is source-compatible in a checkable sense. At its
head `41febf890fbbb852c6059d4c0cc8c593ae9dfa5c`, that package pins the same
CONTROLLER, original port data and caller implementation as SOURCES.json
here, with identical full SHA256 values. Its ordered retained set is
precisely the 145 indices just constructed, and its section 1 re-emits
positive canonicalizers with the selected positions followed by the full
retained complement, as done here. Its extension lemma takes a complete
ambient-m unit with endpoint G_r tensor I, uses a complete coordinate
bijection on entry and its inverse on return, and permits arbitrary
spectators. Those are exactly the operator and spectator hypotheses proved
here. Its compiler scalar contacts require routing entire participating
fields into a common coordinate order; our induction likewise uses exterior
scalars on complete aligned fields. Thus there is no model, width, phase or
scalar-type mismatch at that algebraic interface. The current package needs
no unmerged code to prove its own theorem. The larger compiler, ownership,
movement and cost premises of #6878 remain as stated there.

### All-forward controller and whole-job completion

Each physical LOCAL has forward orientation. The source's 16 reverse
interfaces use the literal five-event word

    Q_X^(-2), SIGNED_SWAP(X,Y), F_s,
    Q_Y^(+2), SIGNED_SWAP(Y,X).

With chronological action and SIGNED_SWAP(X,Y):(X,Y)->(Y,-X), this word
implements D_s [[1,-Q],[0,1]]. The minus sign is an exterior coefficient.
The equality Q^(+2)=Q^(-2)=X_q has absolute phase +1; it is checked at every
port. Each thin query realizes Q^(-1)=X_q Q by a positive rank-one Gaussian
conjugated through the complete port basis, plus its ordinary translation.
Its separate owned scratch label t has the explicit semantic macro

    INIT t=0; COPY t=X; apply Q^(-1) to t; ADD Y+=t; CLEAR t.

It leaves X unchanged, replaces Y by Y+Q^(-1)X, and returns t to zero under
the stated ideal-reset semantics. The complete query basis and its inverse
restore the original full field coordinates before ADD. The scratch label
is outside the 29-label local owned bank and is reused only after CLEAR.
This makes the additional owned return explicit; it neither supplies a
physical erasure algorithm nor adds another paid native call. Each of the
15*104 thin queries still invokes one rank-one positive child.

To verify the *actual* controller, source_algebra.py propagates each of the
32 final coordinate functionals backwards through every literal event and
both scalar boundary programs. Coefficients lie in the free Laurent ring

    Q[Q,Q^(-1),D_0,D_0^(-1),...,D_32,D_32^(-1)].

This is independent of the predecessor's forward row-matrix replay. It
checks all 1,024 entries of the resulting 32-by-32 operator and compares
the literal boundary programs with their stored matrices. There is no
Q^4=1 quotient that could conceal a central-power error. At every port the
native operators Q,D_s commute, since they are products of the commuting
translations X_v. Evaluation in this commutative operator algebra therefore
preserves the verified identity. Their columnwise lifts also commute, while
the rational coefficients stay exterior. Consequently the same exact raw
diagonal endpoint holds at every f and every spectator space.

For each of the 3,328 main fields, the raw endpoint is Q^epsilon product D_s,
with epsilon in {+1,-1}. If epsilon=-1, its whole-job translation X_q changes
the Q exponent to +1. The polynomial check establishes equality to the
positive Gaussians on the complete recorded target axes. If stage 0 is
present, use the original nine coordinate axes; otherwise use q and its
eight-vector orthonormal complement. Append the selected fresh axes and
**all** other retained coordinates. The complete invertible map conjugates
this product to G_r, where r=1+8 times the number of selected stages.

Each whole-idle product similarly receives one positive G_(8k) child with
its complete basis and the exactly calculated whole-job translation, where
k is the actual number of distinct stages in the window. All 3,120 fields
are checked, including the windows that contain stage 0. A rank-r child
becomes exactly rank r*f after the tensor lift; spectator coordinates remain
untouched. The raw positive query, main and idle normalizations are all
identities of full products, so no tensoring of a scalar-weighted sum occurs.

Finally, every local call maps its 208 main public roles to the actual pair
of controller rows, its 562 arbitrary helpers to fresh public inputs, and
its 29 owned roles to the returned shared owned bank. These maps are checked
as injective on all 799 labels, and the thin scratch label is separate.
There are 3,328 arbitrary main and 18*562=10,116 arbitrary helper inputs.
The local gauge identity, complete whole-helper normalization, complete raw
caller identity and whole-job normalization prove the asserted direct-sum
endpoint, with no remaining unspecified local algebraic adapter.

## 5. Accounting and limits

This package leaves the selected bill unchanged:

| Quantity | Exact count |
|---|---:|
| Arbitrary productive fields | 13,444 |
| Paid calls | 66,834 |
| Paid rank mass | 240,152 |
| Productive rank mass | 240,912 |
| Actual forward local calls | 18 |
| Five-step wrappers | 16 |
| Thin rank-one calls | 1,560 |
| Whole-idle calls | 3,120 |

The complete paid profile is 18 times the selected local MOVE profile, plus
the 1,560 positive rank-one thin calls and the 3,120 whole-idle calls. The
productive profile is 18 times the 562-helper profile plus the complete main
endpoint profile. These profiles are compared exactly with selected RESULT,
including every multiplicity. This verifies algebraic accounting; it does
not reprice ordinary adapters, infer a physical runtime from a recipe, or
claim that the positive rank margin alone proves a multiplication bound.

The selected record states `native_all_columns` as: retained native operators,
phase conventions, spectators and whole-job adapters work at every positive
column multiplicity. For the exact P104 objects and assembled caller pinned
here, that algebraic assertion is now the theorem of Sections 2--4. Its status
does not depend on a future maintainer admission or a physical dispatcher.
The theorem does not silently extend to a different upstream native family.

The result supplies this proved algebraic endpoint to a later physical
dispatch theorem. That theorem must still realize every typed
native product, whole-field scalar operation and coordinate map on the
prescribed layouts, preserve or discharge the owned-reset semantics, and
charge source access, staging, restoration and recursive children at the
selected tariff. Existing physical monomial constructions #3055/#3087 and
old-controller #3385 are credited but do not automatically establish that
current combined tariff. The other framework assumptions remain explicit.
No selected record or accepted kappa is changed. **No new kappa.**
