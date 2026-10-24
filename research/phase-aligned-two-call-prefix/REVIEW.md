# Independent subagent review of the phase-aligned prefix

Reviewed on 22 October 2026 by the `refit_candidate` OpenAI Codex agent for
Yiyang. This is a second computational/mathematical review in the same agent
team, not independent human review. No candidate files were modified.

Verdict: the stated local construction, fixed-target continuation obstruction,
and all-extra-width hook-rank argument are sound within the explicit scope.
No completed five-in-fourteen unit or improved multiplication bound follows.

## Fixed-target missing dimensions

Let E be the span of all current quotient rows on the original input domain,
and fix the required target rowspace T. Then

`d_T(E)=dim(T)-dim(T intersection E)`.

A free letter preserving N induces a map on H/N. Its new rows are combinations
of the old quotient rows. Copies, arbitrary scalar register mixing and erasure
therefore give E_new contained in E and cannot decrease d_T.

For one paid operation C on one current register A, choose any linear
projection p onto N. The new quotient map is

`q C A = q C p A + q C (I-p) A`.

The second summand factors through qA, whose rows were already in E. The first
has rank at most rank(qC restricted to N)=80. Thus E_new is contained in E+W
for some W of dimension at most80, even if old rows are erased. Hence
`d_T(E_new) >= d_T(E)-80`. No injectivity assumption on the state or the free
mixing is needed.

For the literal two-call beginning on one fresh input, the bad cut has
dim(E)=160 and dim(T+E)=280+4*224=1176. Its remaining deficit1016 requires
at least13 more calls. A retained copy of the first paid output adds no
quotient rows because its stacked rank with F_old is already160. This proves
fifteen total for that beginning only. It does not rule out arbitrary
pre-encoding, later reuse of the word, or a general five-in-fourteen circuit.

The repair changes the joint rank to224, so the remaining deficit is exactly
64+4*224=960. Matching the twelve-call capacity is a necessary condition,
not a continuation algorithm.

## All-extra-width argument

The new family is a sum of two individually tensorized branches. It is never
the tensor power of the two-branch sum. On H tensor V^r it has the form

`A5 tensor A^tensor r + 2 B5 tensor B^tensor r`.

Left multiplication by the invertible extra-column operator
`(A^tensor r)^-1` reduces this to
`A5 tensor I + 2 B5 tensor (A^-1 B)^tensor r`.
The relative operator is similar to R=P^-1Q, with R^4=I. Over characteristic
zero it is diagonalizable and all eigenvalues lie in {1,-1,i,-i}. The four
checked pencil ranks are all160, so every spectral summand has that rank;
summing their multiplicities gives160*8^r. Exact branchwise containment in
the target rowspace tensors with the additional columns, giving joint rank
224*8^r. This proves the advertised family of lifted cuts for f=5+r, r>=0.
It does not assert every possible certificate at every width passes.

The invertibility proof is separate and applies to every positive digit
width: R_f^4=I and
`(I+2R_f)(I-2R_f+4R_f^2-8R_f^3)=-15I`.
No inverse needs to be executed by the forward two-call prefix. The schedule
must restore its retained first output using Q^-1, not Q; the README says so.

## Residual and sector phases

The two exact branch-word identities are sufficient to tensorize the residual
identity without tensorizing a sum. The coefficient2 remains2 at every width.
The explicit free factorization of M uses only Pauli, address permutation and
S/parity phase letters; J has exactly one paid C2 call.

For the sector transport, R commutes with both middle generators. Together
with the checked input and output conjugations this gives the intertwining
identity separately for both branches, not merely for their width-one sum.
Consequently the tensor sign is epsilon=(-1)^f, exactly as stated. The four
sector projections preserve the omitted pieces as an outstanding obligation;
they do not create independent-array target credit automatically.

## Verification scope

This note records an independent agent review in the same research team. The exact package replay is the reproducible numerical evidence; this review is not independent human or formal-kernel acceptance. The phase alphabet and fresh-input beginning are explicit premises.
