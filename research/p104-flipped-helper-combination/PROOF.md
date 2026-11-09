# Source-bound composition of flipped mirrors and helper splits

This is a conditional construction on the exact #6917 word at
`07e81202470957555569d0c1077b2d6915e897fe`. It uses the helper mechanism of
Ali Romman (#5599), the retiming/retirement extension of @CubeJerry
(#6805/#6824), and the implementation retained in #6916. It does not assume
that a suffix block of the flipped word is an inverse transpose. Every cut
is proved against the complete, actual prefix and suffix.

## 1. The source boundary and the new independent fields

There are 104 native ports. At the 96 type-A ports the normalized endpoint is

\[
 X=x,\quad Y=x+y,\quad X_2=x_2-y_2,\quad Y_2=y_2.
\]

At the eight type-B ports it is

\[
 X=x-y,\qquad Y=(x+y)/2.
\]

The 400 main fields are protected. Every other public field is an autonomous
helper, with identity scalar endpoint between its designated input and output
charts. Owned fields start at zero and return under the inherited erasure
semantics. The program may mix main-port types transiently; the full endpoint
equations, not a ban on such intermediate traffic, establish separation.

For a cut, write its full normalized prefix and suffix as P and S. A witness
gives row vectors a,c, column vectors b,d, a pivot helper p, and a frame F:

\[
 aP=c,\qquad Sb=d,\qquad ab=cd=1.
\]

The supports of a,b are coframed at F. The supports of c,d are exclusively
public helpers with the same boundary U,V, with
\(U\subsetneq F\subsetneq V\). No main or owned field is in c,d.
The prefix equation ranges over every arbitrary public input; the suffix
equation includes every other public and owned final output.

Choose elementary invertible dyadic bases B0 and BF such that

\[
 e_p^T B_0=c,\quad B_0d=e_p,
 \qquad e_p^T B_F=a,\quad B_Fb=e_p.
\]

They are constructed and multiplied exactly. The `dyadic-unit-v1` rule
selects an available dyadic-unit direction coordinate, normalizes it, clears
the other direction coordinates, and adjusts the pivot row. Every emitted
SCALE is an invertible dyadic unit; arbitrary non-dyadic divisions are not
permitted. The bases are identity outside their stated supports.

Set \(C=B_FPB_0^{-1}\) and \(D=B_0SB_F^{-1}\). Then
\(e_p^TC=e_p^T\), \(De_p=e_p\), and \(DC=E\), where E is the source
endpoint. The last equality follows because B0 acts inside an identity
helper block and commutes with E, regardless of the mixed main blocks.
The cut coordinate is exactly the old independent input x_p; no other
final output depends on that coordinate. Retire that field at F and use
a fresh independent input z at F in its place in the suffix. The old field
returns x_p at F, the successor returns z at V, and every other output is
unchanged. Thus one U-to-V helper becomes two independent helpers.

All owned labels are shifted when a new public label is inserted. The new
field never aliases owned storage. This proof does not invert P or S;
INIT/CLEAR projections are allowed only under the inherited reset contract.

## 2. Chronology, retiming, and COPY

The frozen sequence contains 58 steps. Thirty-two cuts retime 60 single
public MOVEs. Each is moved inside a window with no other read or write of
that field, and the cut chart is one of its original endpoint charts. Thus
the same literal chart operator is moved, with no new recursive job. The
complete paid operator multiset, including exact chart pairs, remains equal
to the source with multiplicity. No owned MOVE is retimed.

`construct.py` regenerates each basis and its full forward-prefix/suffix
equations. The separately retained `independent_directional.py` computes
prefix functionals backward and suffix perturbations forward, reconstructs
and checks every contact-free window, and checks the witness source hash.
Its 19 future-COPY guards prove that the new perturbation is zero at each
later COPY destination. Full replay also proves that each COPY enters an
actually zero owned field on every arbitrary public input. This is an
addition into admitted zero storage, not an overwrite of an unknown value.

The final exact forward and reverse checks cover 1,420 public fields and
2,016,400 endpoint coefficients. Every fresh helper input has its own column.
There remain 51 owned labels, 54 lifetimes, peak 30 live owned fields,
53 dirty clears and 23 upward owned moves of total rank 56. Every one of
those moves is paid; none creates a productive input.

## 3. Physical maps and all-column scope

In current signed canonical frame coordinates, MOVE is the identity and
coframed scalar operations act on whole arrays. `native_physical.py` obtains
each native/helper rank factorization from the retained Clifford compiler
and proves its signed Pauli action and absolute phase with the separate
Gaussian-dyadic interpreter. It checks every distinct map from the final
word, all main boundary adapters, and a phase-only corrupted recipe.

These fixed nine-axis maps lift columnwise under the inherited frame and
ordinary monomial interfaces. Scalar coefficients remain outside tensor
powers. The arbitrary-input matrix identities therefore act on arbitrary
full arrays at each width under those interfaces. Exact nine-axis finite
checks alone do not establish their tape implementation, precision, or
admission of general owned lifetimes.

The caller's unchanged geometry has 9 central axes and 18 fresh stage
blocks of eight axes, hence physical ambient 153. The retained caller
physical audit verifies the contact phases, current shapes, complete idle
jobs and all port assignments. Both second-main charts are explicitly
bound to the first-plane charts. At each stage the 400 main slots are
injected into distinct caller roles of their own type, and helpers receive
distinct labels `(helper, stage, local label)`. Including all caller roles
gives 22,504 independent productive fields, with no shared helper counted
twice inside a joint call.

The separate caller reverse check proves all 6,084 coefficients over
\(\mathbb{Q}(i)[q,D_1,\ldots,D_{18}]/(q^4-1)\). The D variables are free;
exponents are not reduced as idempotents. A conservative occurrence bound
prevents carries in their packed representation. This proves a formal
endpoint, not a physical multiplier implementation.

## 4. Exact transfer of the caller compression

Extracting the type-A events and converting each joint to its A HOST2 event
gives exactly the original caller retained by #6916, including its roles,
ambient, diagonal and all nonconstant boundaries. Its constant-block
replacement proves 38 complete 40-by-40 matrix identities (60,800 scalar
equalities), and preserves every nonconstant event and its metadata.

Between joints, all A operations act on A roles and all B operations on
disjoint B roles. Such operations commute as operators even when their
current values are correlated. The compressed A stream can consequently
be interleaved with the unchanged B stream between the same joint
boundaries. `compress_caller.py` checks the disjoint supports, every original
A event, each joint boundary, and the unchanged ordered B/J subsequence.
The final mixed caller has 3,221 events instead of 4,519. Both complete
caller variants receive separate formal and physical checks.

## 5. Full signed invoice and ordinary budget

Every cut splits a rank-nine helper. With \(g_r(t)=r^t+(9-r)^t-9^t\), the
complete gain over #6917 is exactly

\[
18\bigl(21g_4(t)+30g_3(t)+2g_2(t)+5g_1(t)\bigr)>0,
\qquad 0<t<1.
\]

Each native call has 1,020 helpers and the original 6,379 paid MOVEs.
Across all 18 joints and the complete caller, there are 22,504 productive
fields and 119,046 paid jobs, with paid rank mass 317,444 and surplus 1,520.
`RESULT.json` records every coefficient. A literal caller recount and a
separate derivation from the two exact root matrices agree term by term;
a third implementation independently rebuilds the literal invoice.

Added fields, normalizers and scalar basis changes are all paid. The native
scalar upper is 1,343,940 and native route charge 9,835,000 per call. Original
caller rest is 782,308,192. In addition to the whole reviewed envelope, pay
all \(96\cdot124+8\cdot82=12,560\) global LAMBDA translations at 1,000
source-accounting units each:

\[
18(1343940+9835000)+782308192+12560000
=996089112<10^9.
\]

The constant-block replacement removes exactly 1,298 A events, saving
\(1298\cdot32\cdot40\cdot96=159498240\). Its complete ordinary charge is
836,590,872, with exactly the same target/paid moments. No recursive savings
are credited for this ordinary compression.

The normalizer lowering is the retained #6913 all-width identity
\(\Lambda_s=(1+si)I/2+(1-si)Q_f^2/2\), where
\(Q_f^2=X_q^{\otimes f}\). Its scratch-copy, fixed NOT records, scalar
combination and clear use the existing returned query bank sequentially.
It introduces no productive field or recursive child. Applying this
portwise to both types uses the same shape and central direction; its
complete translation debit above is new for this exact mixed caller.
This retains the monomial movement and owned-erasure hypotheses.

## 6. Strict conditional price and compiler application

Three rational implementations prove the signs at the headline, tested
price and raw bracket, and a strictly negative derivative through the BIT
pin. The raw crossing lies in
\((0.003579065166491,0.003579065166492)\). Choose headline
\(\kappa=0.00357906\) and tested saving 0.00357906007, with grid gap
\(g=10^{-11}\).

For cutoff 11, completion 12, offset 1/7 and chronological power 1920,
the fresh complete target and paid moments satisfy the strict tail bounds
\(\alpha<1-10^{-27}\), \(\gamma,\delta<31/32\). In particular the
extra independent fields are counted in the delta term. The composite
bound is \(1/(1+1920\cdot10^{-27})+4(31/32)^{1920}<1\).

The general ambient-cap theorem in `retained/compiler/PROOF.md` sections
5–7 uses the actual carrier cap \(153^{1920}\), while the largest target
is \(145^{1920}\). Its general hypothesis is a complete chronological
mixed-rank supplier on actual arrays with all whole-job and owner contracts;
it does not require one particular two-chain main block. Section 8's
four-main example is not automatic admission of this source. For this
application, sections 1–5 above supply exact endpoints, fresh fields,
chronology, physical factor checks and a full invoice; admissibility of
the inherited mixed-port and owned-storage realization remains conditional.

Fresh logarithm power 2300 satisfies the capacity and integer-exit bounds.
The separate retained rational range proof covers every saving through
0.0036. The exact first winning grid point is j=122,933, giving
H=12,293,300,000,000,000 and finite template rank \(N=2^H\). This enormous
template is specified, not materialized. [PRECISION.md](PRECISION.md) defines
new finite scalar, stock and precision constants; no old literal native
event or width cap is reused. All 54 strict and four functional outer
predicates pass with the inherited open BIT pin 0.00376669. An insufficient
BIT pin and an overstated saving are rejected.

The result is a conditional candidate improvement. The five framework
assumptions, BIT admission, completed physical/precision/stock contracts,
owned erasure and mixed-port admission are not proved here. This package
neither changes the selected frontier nor claims a global optimum.
