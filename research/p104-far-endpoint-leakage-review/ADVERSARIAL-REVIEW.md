# Adversarial static review of the far-endpoint leakage audit

**Verdict: PASS for the stated conditional section6 audit; no unresolved
mathematical finding.** One scope qualification was raised and incorporated
before this final review: the characteristic-two control concerns the
displayed matrix hypotheses after deletion of the field restriction, not
a separately imposed genuine shortest-word condition.

This review checks the algebra directly. It does not treat agreement with
another agent as proof. I read the coordinator derivation and the three
frozen source texts, but did not read the separate MATH-REVIEW, execute or
import mathematical code, run a proof kernel or contact the network.
Only this review file is authored by this reviewer.

## Exact objects reviewed

The source is thu-nmrc PR6717, current head
`3c9072b8738323dda9f9c7dfb421d578ed3fc17a`, particularly PROOF section6.

| Object | SHA256 |
| --- | --- |
| Coordinator derivation, after characteristic-two qualification | `22e5e1fa64b2aba2a5d8d8df4f5f06c8f6313493778f33ac07f3a8d4222c6d6c` |
| 6717-PROOF.md | `9e108fdf827ffe92215be5e782f763a18968ce7613b66dfdd25a38f94958ce18` |
| 6717-README.md | `02fc8aa47e0f3b9ff042caad5f9049325f6b32dc4fff9d816136037b0402e188` |
| 6717-TASK.json | `67bce2c4caa1ff3fce659c5f7033ad1fad08c42f786efbfc749c6a3cedc20ca0` |

The original coordinator draft is separately retained as
`COORDINATOR-DERIVATION-BEFORE-CHAR2-QUALIFICATION.md`. The correction is
scope wording, not a changed rank calculation or new computational result.

## Kernel lemma and ordered leakage identities

For an idempotent Q, `ker(I-Q)=im(Q)`. Therefore the retained column
subspace A0 has dimension `a-alpha`. Likewise `c=cQ` characterizes the
row space of Q, so the retained row subspace C0 has dimension `c-beta`.
The restriction of C0 to im(Q) is injective: vanishing on that image gives
`cQ=0`, and `c=cQ` then gives c=0. Consequently the map from im(Q) into
C0* has rank dim(C0). Its kernel contains A0 because every original row
in C annihilates every original column in A. Rank-nullity gives exactly

`rank(Q) >= a+c-alpha-beta`.

This uses actual kernels, so there is no unjustified simultaneous choice
of separately retained columns and rows. It works over arbitrary fields
and needs neither positive inner products nor simultaneous diagonalization.

The leakage derivation also preserves matrix order. From `QU=U` and
`PQ=QP`, `PU=PQU=QPU`, hence `(I-Q)PU=0`. From `VQ=V`,
`VP=VQP=VPQ`, hence `VP(I-Q)=0`. Substituting P=E+F yields

`(I-Q)EU=-(I-Q)FU`, `VE(I-Q)=-VF(I-Q)`.

The two right sides each have rank at most rank(F)=e. Since the map
already vanishes on U, its image on span(U,EU) is precisely its image
on EU; there is no second q-dimensional leakage contribution. The
same argument applies to the row closure. Thus alpha,beta<=e is valid
without assuming any internal block commutation or e<=q.

The decomposition rank(F)=rank(P)-2q remains an explicitly inherited
forced-projector premise. Given that premise, this argument makes no
additional rank-minimality assumption on P or Q.

## Endpoint formulas, minors and all four pairings

For the left endpoint, `v0=-tail0`. For odd i>=3,
`E_i e0=e_i+a_i` and `v0 E_i=-(e_i^T+tail_i)`. These follow directly
from `h_i e0=1`, `v_i e0=1`, `v0 e_i=-1` and `v0 a_i=1`.
The column minor on coordinates0,1 is
`[[1,1],[0,-1]]`, determinant -1. The row minor on coordinates1,i is
`[[-1,-1],[0,-1]]`, determinant1. Both are units over every field.

The four pairings vanish separately: `v0 e0=0`,
`v0(e_i+a_i)=-1+1=0`, `(e_i^T+tail_i)e0=0`, and
`(e_i^T+tail_i)(e_i+a_i)=1-1=0`. The last row's overall minus sign
does not change zero pairing.

For the right endpoint, `u_n=(-1,1,...,-1,1)^T` and `v_n=h`.
For odd i<=n-3, `h_i u_n=0`, `v_i u_n=-1` and `h a_i=0`,
so `E_i u_n=-a_i` and `h E_i=h_i`. The column minor of
`[u_n,-a_i]` on coordinates0,i+1 is
`[[-1,-1],[-1,0]]`, determinant -1. The row minor of `[h;h_i]`
on those coordinates is `[[1,1],[1,0]]`, also determinant -1.

The four right pairings are `h u_n=0`, `h a_i=0`,
`h_i u_n=0`, `h_i a_i=0`: every relevant alternating sum has even
length. The dimensions and annihilation claims therefore hold with
no characteristic-zero counting assumption. Tensoring these fixed scalar
closure matrices with I_q gives dimensions2q and2q and zero pairing.
This does not tensor a scalar classification of arbitrary P or Q.

A far endpoint exists at every allowed boundary. Odd i>=3 permits the
left endpoint; the remaining possibility i=1 permits the right because
n>=4 implies i<=n-3. In particular n=4,i=1 uses the right endpoint,
while n=4,i=3 and i=n-1 use the left.

## Rank debt and written countercontrols

Applying the kernel lemma gives `rank(Q)>=4q-2e`. Independently,
compatibility with a rank-q square-zero query gives rank(Q)>=2q:
its rank-q image and rank-q supported row space have zero pairing.
Writing rank(Q)=2q+f therefore gives `f>=max(0,2q-2e)`.
For e>=q, e+f>=q follows from f>=0. For 0<=e<=q,
e+f>=2q-e>=q. The remaining endpoint contributes another2q.
The sole-odd selected triple consequently has total rank at least7q.
Large e creates no sign or negative-dimension gap.

All three written controls are valid at their stated scopes:

1. At n=4,i=1, the left near endpoint satisfies `E_i e0=e0`
   and `v0 E_i=v0`. Its two closures each have dimension1, so using
   the left endpoint's supposed dimension2 here would be false.
2. Without CA=0, Q=I on K^2, A=K^2 and C=(K^2)* give
   alpha=beta=0 but rank(Q)=2<4=a+c. Independent row/column
   dimensions cannot simply be added without annihilation.
3. In characteristic two, five copies of `e0 e1^T` have rank1,
   square zero and factors `I-2R_j=I=-I`; three copies of
   `diag(1,1,0,0)` at distinct sites satisfy the displayed compatibility,
   prefix and pairwise commutation conditions but have total rank6<7.
   However, this five-query word is not genuinely shortest there:
   the endpoint I has a zero-query realization. The amended coordinator
   text correctly limits this control to deleting the field restriction
   from the displayed matrix hypotheses. It is not a counterexample
   to the field-independent leakage lemma or to a different theorem
   imposing genuine minimality separately.

## Scope, credit and remaining acceptance

The coordinator accurately treats the complete shortest-query normal
form, canonical prefix formula, forced odd projector and compatibility
floor as inherited premises. This review independently checks the kernel
argument, ordered leakage application, endpoint closures and sole-odd
rank conclusion conditional on those premises. It does not certify the
source's even-interior branch, two-odd branch, normal-form derivation,
all-n attaining word, physical Gaussian/native implementation or invoice.

The source's rank threshold and application remain thu-nmrc's work with
substantial OpenAI Codex assistance. Ali Romman's PR6398 and retained
alternating-caller-closure tools, complete coupled normal form, Cinna
Davis's query/controller lineage and all earlier notices retain credit.
The review is a classical linear-algebra audit, not invention of a new
general rank lemma. This separate AI review gives no independent human
acceptance, proof-kernel certification, κ improvement, selected-frontier
change or discharge of the five framework assumptions.

No further correction is requested for the reviewed final derivation.
