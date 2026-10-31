# Unit-column completion and the concrete P104 handoff

This is a scoped algebraic construction and source-bound scalar-bill
improvement. Elementary shears are classical. The new result is their
application to the nonunit row in #6297, including the complete local word.
No whole-word optimum, supplier admission or new κ is asserted.

## 1. Column-unit completion

Let D be a commutative ring, let a be a row and b a column on the same finite
set of roles, and suppose ab=1. Choose a role p such that q=b_p is a unit.
Write e=e_p and a_off=a-a_p e^T. Define

\[
 T=I-ea_{\rm off},\qquad
 D_q=I+(q-1)ee^T,\qquad
 C=I+\sum_{i\ne p}(b_i/q)e_i e^T,\qquad R=CD_qT.
\]

The two shears have square-zero nilpotent parts. Thus they and D_q are
invertible, with inverses obtained by negating shear coefficients and replacing
q by q^{-1}. Directly, Te=e and CD_qe=b, so Re=b. For the other boundary,
aC has entries a_i for i≠p and pivot

\[
 a_p+\sum_{i\ne p}a_i b_i/q=ab/q=1/q.
\]

Consequently aCD_q=e^T+a_off and aR=e^T. This proves both identities over
D, without a unit coordinate in a and without an added spare role. It preserves
all arbitrary input degrees of freedom because R is invertible. Its determinant
is q. No complement action is prescribed by the dual-pair interface; R need not
equal the predecessor's Euclidean completion on that complement.

Execution order is T, then D_q, then C. In an ADD/SCALE program this is:

1. `x_p -= a_i x_i` for each nonzero a_i with i≠p.
2. `x_p *= q` if q≠1.
3. `x_i += (b_i/q) x_p` for each nonzero b_i with i≠p.

All input coordinates are arbitrary. For D=Z[1/2], q a dyadic unit makes all
emitted coefficients dyadic and the SCALE legal. The implementation also checks
the inherited strict coefficient bound |c|+1<2^16 on both the forward program
and its inverse. That extra acceptance test is required for the local caller;
the algebraic identity itself has no such size restriction. A tiny pivot can
have an oversized inverse, so checking only the forward SCALE would be wrong.

### One sparse preconditioner

Choose distinct nonpivot roles i and j and set S=I+e_i e_j^T. Define
 a'=aS^{-1}, b'=Sb. If R' completes (a',b'), then R=S^{-1}R' completes (a,b):
 aR=a'R'=e_p^T and Re_p=S^{-1}b'=b. Here S fixes e_p. The emitted program
 applies R' followed by one ADD x_i -= x_j. The new pair changes only
 a'_j=a_j-a_i and b'_i=b_i+b_j. Thus equal row coefficients and opposite
 column coefficients can cancel simultaneously. This is one specified
 preconditioner; choosing it does not prove any global circuit optimum.

## 2. Exact retained tariff

For a nonzero reduced dyadic coefficient c=n/d, with |n|>0 and d a power of
two, the retained real scalar allowance is

\[
 A(c)=2(3+\lfloor\log_2|n|\rfloor+\operatorname{popcount}(|n|)+\log_2d).
\]

For a dyadic-unit SCALE q, it is

\[
 S(q)=2(|\log_2|q||+\mathbf 1_{q<0}).
\]

These are the #5602 local replay tariffs, not unit-cost gate counts. The new
program's exact allowance is

\[
 \sum_{i\ne p,a_i\ne0} A(a_i)+S(q)
 +\sum_{i\ne p,b_i\ne0} A(b_i/q),
\]

where S(1)=0. Inverting the program preserves this bill: A(-c)=A(c) and
S(q^{-1})=S(q). No recursive helper operation, chart change, COPY, INIT or CLEAR is
introduced by this scalar factorization. All scalar operations stay at the
boundary chart where the affected roles are available. Physical native,
caller, compiler, precision and storage obligations outside this local word
remain separate.

## 3. The pinned #6297 instance

The source is the exact #5580 word retained at
`research/p104-coupled-helper-bases/inputs/pr5580-WORD.json.gz`, authenticated
against base `2485805a6d47f36ea83ddde6327d453ac82d44dc`. The #6297 head is
`2fbb316a7bd34fabebed8e47ed40017c150d71b8`; its README and verifier are retained
verbatim with Git-blob and SHA-256 records in `PREDECESSOR.json`.

Use p=596 and the following row at cut 13762 in frame 1053:

\[
 v=a=\tfrac5{16}e_{592}^T+\tfrac5{16}e_{593}^T
       +\tfrac58e_{594}^T+\tfrac38e_{596}^T.
\]

Its cut column is u=−e_592+e_593+e_594+e_596; its full output column is
b=−e_188+u. Both pairings are one and both pivot coefficients are one.
The row has no dyadic-unit coordinate, but the column does. Set
S=I+e_592 e_593^T. Equal row coefficients give a'_593=0 and opposite column
coefficients give b'_592=0. The preconditioned pair is

\[
 a'=\tfrac5{16}e_{592}^T+\tfrac58e_{594}^T+\tfrac38e_{596}^T,\qquad
 b'=-e_{188}+e_{593}+e_{594}+e_{596},
\]

with the e_188 term omitted at the cut. The two initial ADDs in R' are:

```
x596 -= (5/16) x592
x596 -= (5/8)  x594
```

They cost 22+20=42. Source completion then adds −x596 to x188 and +x596 to
x593 and x594, costing 24. Cut completion has only the latter two ADDs,
costing 16. Finally both programs apply S^{-1}, namely `x592 -= x593`,
costing 8. The source completion therefore uses six gates and allowance 74;
the cut completion uses five gates and allowance 66.

The full handoff contains source and cut programs and both inverses, so its
inserted bill is exactly 2(74+66)=280 and its inserted event count is 22.
The retained Euclidean compiler emits 36 source gates and 34 cut gates. Replaying
that exact compiler and the same literal handoff gives 140 inserted events and
allowance 1136, reproducing #6297. The new factorization therefore saves 118
scalar events and 856 allowance units at the same boundary contract. This compares the emitted Euclidean schedule, not a proved minimum weighted
allowance. The gate-count optimum is established separately below. The two
chosen basis matrices need not coincide on their unconstrained complements.
The preconditioner refinement was identified by the lead during independent
review; both workers separately checked the strengthened circuit.

## 4. Why the full dirty handoff remains valid

Let P be the source-to-cut linear map, Q the cut-to-output map, W=QP the
original complete word, R the source completion and S the cut completion.
The authenticated prefix and suffix give vP=a and Qu=b. Hence

\[
 e_p^T S^{-1}PR=vPR=aR=e_p^T,\qquad
 R^{-1}QS e_p=R^{-1}Qu=R^{-1}b=e_p.
\]

At the cut, S^{-1}PR has therefore isolated the original arbitrary helper input
x_p into the retired pivot. Replace only this active pivot slot by a fresh,
arbitrary public input z; preserve x_p as the retired output. After the suffix
and inverse output completion, the active outputs are

\[
 R^{-1}W R x-e_p x_p+e_p z.
\]

R is supported entirely on the (3,127) helper group, on which W is the
identity and which is disjoint from the main X-to-Y shear. Therefore R^{-1}WR=W.
The output is precisely the original word with that helper replaced by z,
while the retired output is x_p. Both input degrees of freedom are independent;
no zero or correlation assumption was used. [INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md)
records the separate reconstruction and its more explicit chronology checks.

The subspaces of frames 3, 1053 and 127 are strictly nested in that order,
with ranks 0, 5 and 9. The original public
helper 596 changes from rank 9 to rank 5, and the added public helper 735 has rank 4.
The complete target histogram changes from
`{4:83,5:5,8:15,9:424}` to `{4:84,5:6,8:15,9:423}` exactly as in #6297.
The complete paid histogram remains
`{1:2211,2:459,3:494,4:94,5:164,6:18,7:14}`.
All MOVE/COPY/INIT/CLEAR events of the #6297 handoff remain identical; only its
scalar completions change. All 736 public inputs and the eight formal owned
columns are checked, together with eight owned lifetimes and peak one.

## 5. Sharp ADD counts for the separate boundary maps

Consider any program of coordinate ADDs `x_i += c x_j` with i≠j and
nonzero coordinate SCALEs over a field. The dyadic-unit model is a subclass.
Suppose its matrix R obeys aR=e_p^T and Re_p=b. Extend a and b by zeros if
additional roles are permitted. These zeros describe absence from the dual
pair, not zero-valued physical registers; the latter may contain arbitrary dirt.

Following the partial program S from the identity tracks the dual pair
`(e_p^T S^{-1}, S e_p)`, initially `(e_p^T,e_p)`. An ADD i←i+cj changes only

\[
 b_i\leftarrow b_i+c b_j,\qquad a_j\leftarrow a_j-c a_i.
\]

Call a role blank, one-sided or double according to whether it appears in zero,
one or both supports. SCALE preserves these categories. If an ADD first activates
a blank i, it can create only b_i; since a_i=0, the same ADD leaves a_j unchanged.
If it first activates a blank j, it can create only a_j; since b_j=0, it leaves
b_i unchanged. Thus one ADD activates at most one blank role and an activating
ADD cannot create a second support on any other role.

Let N=|supp(a)∪supp(b)| and M=|supp(a)∩supp(b)|, with p in both final supports.
Each of the N−1 other final-support roles must appear for the first time during
an ADD: at least N−1 distinct activation ADDs. Each of the M−1 final nonpivot
double roles first appears one-sided and must subsequently acquire its second
support. Choose one such acquisition per role. None occurs on any activation
ADD, and a single ADD changes at most two roles, so at least ceil((M−1)/2)
additional ADDs are necessary. Therefore

\[
 \#\mathrm{ADD}\ \ge\ N-1+\left\lceil\frac{M-1}{2}\right\rceil.
\]

Cancellations, temporary disappearance of a role, and extra roles cannot avoid
these first-appearance and later second-support requirements. This proves the
bound for arbitrary coefficients and program lengths, without a finite search.

For the source pair, N=5 and M=4, giving six ADDs. For the cut pair, N=M=4,
giving five. The emitted programs attain both bounds with no SCALEs. An inverse
of either emitted matrix cannot have fewer ADDs: reversing such a shorter
inverse would contradict the corresponding completion lower bound. Hence the
minimum across the four **separately completed** basis/inverse-basis maps is
exactly 2(6+5)=22 ADDs, also 22 total scalar gates.

This does not constrain arbitrary interleavings across boundaries, a changed
handoff contract, a different whole word, or additional free gate primitives.
Nor does the count bound prove that the allowance 280 is minimal: different
six-/five-ADD completions may have different coefficient tariffs.
The support-activation argument was supplied by the lead and independently
checked by workers A and D. Finite corroboration enumerates 2,500 local rational
transitions covering all 16 support-type pairs; the actual orbit records show
four activations plus two double-creation gates at source, and three plus two
at the cut. Those finite cases corroborate, rather than prove, the universal
argument.

## 6. Evidence and limits

The universal completion and handoff statements rest on the written algebra,
not on finite testing. Exact finite evidence covers 160 deterministic dyadic
pairs through dimension 8 and 120 preconditioned pairs, both full local words,
all 22 single inserted-event omissions and the additional controls recorded in `RESULT.json`. The independent
checker neither imports the compiler nor the predecessor interpreter.

The complete candidate has 25162 events and scalar allowance 217708, against
25,280 and 218,564 for #6297, and 25,140 and 217,428 for the original word. Its paid
and productive histograms are identical to #6297. Consequently this is a scalar
boundary saving, not an improvement to that word's recursive power invoice.
The exact new basis maps may have different numerical conditioning; finite
coefficient compliance does not prove a rounded global precision bound.
Native/caller admission, compiler closure, uniform machine realization and the
outer theorem are not supplied. All five selected framework assumptions remain.
The selected #6030 record is unchanged. **No new κ.**
