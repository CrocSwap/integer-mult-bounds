# Written universal parity-header floor

**Conditional proof of M>=r+1 for r>=1.** The exceptional case r=0 has
floor0, not1. This is a written derivation under the exact algebraic alphabet
below, not a source replay, physical query bound or executed experiment.
The universal derivation below was written before either new implementation ran. Its author did not read or run source scientific programs or peer engines for that draft. The coordinator and oracle author had previously read inert source replay definitions during the separate second-fragment audit. This is code-disjoint corroboration, not source-unexposed discovery. The source application and actual execution evidence are recorded in section 8.

## 1. Ring and independent-input contract

Let K=Q(i), t=q^2, and define

    E=K[t]/(t^2-1),
    R=K[q]/(q^4-1)=E direct-sum qE.

The last equality is an equality of E-modules with basis(1,q), not a claim
that the ring is a domain. Every element has a unique representative
(a0+a2*q^2)+q*(a1+a3*q^2); uniqueness follows from the degree-below4 normal
form for division by the monic polynomial q^4-1. In particular no cancellation
argument divides by an arbitrary nonzero ring element.

An N-field computation acts on N arbitrary independent original inputs, so its
current whole coefficient matrix starts at I_N. Write its unique decomposition
as W=A+qB with A,B in Mat_N(E). Initially A=I_N,B=0. Equality is on every
input column. Fresh or retired roles may be scheduled later, but their original
independent input axes cannot be set to zero or silently redefined.

Legal free ordinary operations are even matrices O(t) whose two evaluations
O(+1),O(-1) are invertible over K. Paid odd queries are single-row off-diagonal
shears

    Q=I+c(t)*q*E_ds,  d!=s,  c(t) in E.

Their coefficient may depend on t and may vanish in one sector. The bound
does not require c to be a unit. Since E_ds^2=0, these query matrices themselves
are invertible, with inverse I-c(t)*q*E_ds. Operations are multiplied on the
left in their actual chronological order.

The target has r diagonal odd q monomials, or more generally q times even
units, and N-r diagonal even units. Its even-part rank will therefore be N-r
in each sector. All target units and r must be interpreted relative to the
same original input matrix, not only on initialized or prephased test states.

## 2. Sector ranks remain ordinary field ranks

For theta in{+1,-1}, evaluate only t at theta. The matrices A_theta,B_theta
are ordinary K-matrices. The residual symbol q is still formal in
K[q]/(q^2-theta), where(1,q) is again a unique K-basis. This is not the single
character evaluation q=1,-1,i or-i. The latter quotient can have zero divisors
as well, but those do not affect ranks of its K-coefficient matrices.

An even ordinary multiplication gives

    A_theta <- O(theta)*A_theta,
    B_theta <- O(theta)*B_theta.

It preserves rank(A_theta), and it preserves B_theta=0 before the first paid
query. Invertibility of O at both theta values is the declared legal ordinary
contract. Equivalently O is invertible over E: since2 is invertible,
e_theta=(1+theta*t)/2 are orthogonal idempotents and the sector inverses
assemble as e_+*O(+1)^-1+e_-*O(-1)^-1. No Gaussian phase is discarded.

In particular the permitted lambda controls are even units:

    lambda_sign(t)=(1+sign*i)/2+(1-sign*i)*t/2,
    lambda_sign(+1)=1,  lambda_sign(-1)=sign*i.

Their two values are nonzero. Thus they belong among the free invertible even
operations for this lower-bound argument; their presence does not turn an odd
q factor into a legal free ordinary multiplier.

## 3. A paid odd query can lower even-part rank by at most one

Multiply the current matrix by Q in the ring, retaining multiplication order:

    (I+c*q*E_ds)(A+qB)
      =(A+t*c*E_ds*B)+q*(B+c*E_ds*A).

After sector evaluation,

    A_theta' = A_theta+theta*c(theta)*E_ds*B_theta,
    B_theta' = B_theta+c(theta)*E_ds*A_theta.

The A update changes only destination row d. Its additive matrix has rank
at most1 over K, hence rank(A_theta')>=rank(A_theta)-1. This is a coefficient
rank statement, not a physical-port or block-call rank claim.

Before the first paid odd query, only even ordinary factors have acted:
B_theta=0 and rank(A_theta)=N. The displayed formula therefore leaves A_theta
unchanged at that first query. All subsequent even ordinary factors preserve
its rank. If there are M>=1 paid odd queries, at most the remaining M-1 can
decrease its rank, so

    rank(A_theta_final)>=N-(M-1)

in each theta sector. A first query whose coefficient vanishes in a sector
still does not help; counting it as a paid query only weakens this bound.
The argument never assumes that A or the whole W has a rank over a
zero-divisor coefficient ring.

## 4. Final target and the strict positive-r qualification

An odd monomial q^(2k+1)=q*t^k has zero even coefficient; its nonzero even
factor remains a unit in either sector. An even target unit contributes a
nonzero diagonal entry to A_theta. Thus the stated whole target has

    rank(A_theta_final)=N-r.

If r>=1, a word with M=0 cannot attain this target: all-even ordinary words
have B=0 and full-rank A_theta. Hence M>=1, and the preceding rank bound gives

    N-r>=N-(M-1),  therefore M>=r+1.

This derives the additional first-query overhead rather than assuming a query
has already been spent. For r=0 the identity target is attained by the empty
word, so M>=r+1 would be false; the appropriate lower bound there is0.
More generally the proof only needs a known final even-part rank defect r in
at least one sector, provided the same initial and ordinary/query contracts
hold. The displayed diagonal target makes that defect exact in both sectors.

## 5. Conditional6726 specialization, without source admission

The byte-bound actual6726 interface has N=34 independent fields and, after all
body symbols D1..D18 are set to1, r=32 odd final q monomials with two remaining
even/identity outputs. It declares33 paid odd queries:18 LOCAL and15 QUERY.
Under this literal closure, the theorem proves at least33, matching the
supplied33-query word within this formal alphabet.

The conversion of LOCAL matters: at bodies1, its forward action is precisely
I+q^-1 E_ds=I+t*q E_ds, a paid odd shear with even coefficient t. QUERY with
an odd exponent similarly has q^(2k+1)=t^k*q. Ordinary Gaussian-rational
bases and even q phases are allowed, lambda is an even unit as above, and
paid-body idles become identity. A byte-bound application still must classify
every actual instruction and exclude a free odd Q_POWER/row multiplier,
an odd coefficient hidden in an ordinary basis, a singular ordinary factor,
or an uncharged non-shear odd operation. The declared counts alone are not
that classification or an execution receipt.

Setting bodies1 is a ring homomorphism of the actual independent-stage formal
word. If its required whole endpoint is established before specialization,
it establishes this necessary specialized endpoint. This gives a necessary
header query count, not a complete multistage operator proof, independently
verified physical LOCAL law, pricing calculation or selected-caller admission.
The result does not classify arbitrary block/rank-t odd updates: their A-rank
change may exceed1 and require a different accounting unit.

## 6. Hand domain controls, not executed tests

**Allow free odd row multiplication.** On two independent inputs, the free
ordinary matrix diag(q,1) would attain a target with r=1 using M=0. It is an
invertible formal matrix, but is not even. The claimed bound2 fails in this
expanded alphabet. Thus treating arbitrary odd prephases as free ordinary
work invalidates the header floor; invertibility alone is insufficient.

**Collapse to q=i.** At that one character, constant diag(i,1) is an allowed
even Gaussian-rational matrix and matches specialized diag(q,1) with M=0.
This does not match the formal target at all q characters. It demonstrates
why the proof must retain the formal(1,q) coefficient split after evaluating
t=q^2, rather than equating formal odd q with a known Gaussian scalar.

**Initialize a nominal odd input to zero.** If the two nominal fields are
(x,0) instead of two independent inputs, target diag(1,q) acts as(x,0).
The empty word attains this restricted-input behavior with M=0 although the
nominal target lists r=1. Its full two-column matrix is not the claimed
target. Thus counting an odd target on an initialized/discarded direction
cannot support the rank defect in the theorem. This control does not claim
that initialized workspace automatically eliminates the cost for other,
nonzero independent odd outputs.

**Supply a prephased original input for free.** If the state preparation is
already(q*x,y) relative to named original unphased inputs(x,y), the same
formal target diag(q,1) is reached by doing nothing. Initial A was not I and
initial B was not zero relative to those original inputs. Calling the first
field a new arbitrary variable instead merely changes which target is asked
for; it is not a counterexample with the original fixed independent-input
contract. The distinction between extra prephase resource and variable
renaming must remain explicit.

None is a counterexample to the stated legal alphabet, a source program run,
or an independently priced physical mechanism. The generic parity argument
is prior work, not a new lower-bound method from these controls.

## 7. Credit, evidence and obligations

Credit the prior Matarener/PR6114 and Cinna Davis GLOBAL/parity-header lineage
identified in the task, together with the source query/controller and retained
native/caller contributors. This draft independently spells out their parity
rank method for this conditional formal interface; it claims neither world
priority nor a new physical theorem. The scalar-header byte closure and execution evidence are supplied in section 8; the actual physical operator law and source-to-physical implication remain required. No physical port coupling, absolute native phase,
paid/ordinary invoice, stock/erasure, compiler/precision/tape, full recurrence,
outer recovery, selected framework assumption, frontier or merge is admitted.

Source-aware OpenAI Codex-assisted written reasoning, not human acceptance or
proof-kernel verification. The written draft preceded the separately frozen execution evidence in section 8. Apache-2.0.


## 8. Byte-bound application and observed evidence

The eight inert source objects in SOURCE-PINS.json total 87,033 UTF-8 bytes, pinned to PR6726 head 435bbe91fb28cb1d7a569ca70c6c4e9eb302d486. The literal 606-event, 34-input word has ADD275, SCALE86 (all -1), SWAP94, LAMBDA100 (66 minus, 34 plus), QUERY15 and LOCAL18 (all query exponents -1), IDLE12 and IDLE_ONE6. There is no Q_POWER. Every healthy ordinary event is invertible and even under INSTRUCTION-CONTRACT.md; paid-body idles specialize to identity. Both separately authored engines authenticate all eight sources and the common contract/cases before parsing. They import no source or peer scientific engine.

Primary transports formal A+qB in each theta sector and computes Gaussian row ranks. Oracle transports four exact character matrices at q=1,-1,i,-i, reconstructs A and B pairwise and computes Gaussian column ranks. All four characters are retained for the complete q4 endpoint. A single character would not establish the formal phase; a single theta sector suffices for the lower-bound rank defect.

Both sealed first runs passed and produced identical complete 56,434-byte certificates, SHA256 f9203bdcf39e4f14bd85520d564c9412ad1d8b4835e9863935cf7f4ee72742ff. The packet contains all four 34x34 final A/B matrices (4,624 exact Gaussian cells), two complete 33-query traces (132 before/after rank values), the actual opcode census and four actual changed-word controls. Both theta traces run 34 -> 34 -> 33 -> ... -> 2. Thus the known 33-query word attains the lower bound in this formal alphabet. The exact raw diagonal is 32 copies of q^-1 and two identity entries, not 32 copies of q. Even-operation rank preservation is proved above; ranks were not numerically computed after every ordinary event.

Actual controls reject deletion of the first paid query, flipping the first lambda sign, insertion of a free odd Q_POWER, and an incorrect final odd phase. The last exposes what rank-only checking misses. The separate retained CLI harness rejected 60 corrupt/missing-input cases across both normal and optimized interpreters, including changed rank/floor/phase/matrix/source pins, missing trace/source, altered contract, malformed or noncanonical packets. Those are verification tests, not additional independently selected scientific experiments.

This contributes an external even-q²-controlled qualification and faithful literal phase/rank audit of the existing source floor. Matarener PR6114, the PR6120 boundary repair, Cinna Davis's GLOBAL/parity lineage and zxv PR6726 retain mathematical/construction credit. The q-independent ordinary proof applies sectorwise; no false-source-proof allegation is made. All source notices and licenses are retained. No physical port law, complete paid/ordinary invoice, native all-columns, owned erasure, compiler, precision tape, analytic recovery or frontier admission follows.
