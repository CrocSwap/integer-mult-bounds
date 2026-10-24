# One returned clean role changes the exact projector-call minimum

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## Exact scope

Let N be any binary square-zero matrix of positive rank q on d arbitrary
data roles. Work coefficientwise over F2[C2], with one fixed nonidentity
involution g and t=1+[g], so t is nonzero and t²=0. Each paid call is
I+t xy^T with y^T x=1; every such coupling has binary rank one and is
idempotent. Constant binary invertible role maps are free and may be
interspersed. Any finite number of dirty helpers must be restored on every
input. Any finite number of clean helpers begin and end at zero. The data
endpoint is I+tN, with no output in any clean role on the active columns.

**Theorem.** The minimum number of paid calls is q+1. At positive even q,
one clean role suffices and saves one reflection against Nick Petalas's
dirty-workspace optimum q+2 in PR4912. At odd q his q+1 construction already
attains the clean minimum. The zero coupling costs zero.

This changes the workspace contract; it does not contradict the dirty
theorem. The clean role is an entire zero function of the address, not one
sample bit. A native source of this resource and its price are not provided.

## 1. Lower bound with unrestricted finite workspace

Include all dirty helpers among the d active roles, padding N by zero.
Let E embed these roles into the full active-plus-clean space. Commute all
free scalar maps to the input side, conjugating paid projectors. The word
has form P S, where P is a product of paid calls. Augmentation t->0 of
the required active columns gives S E=E. Consequently

    P E = E + t E N.

The inherited product identity of ywz65 PR2716 gives P=I+t sum_j x_j y_j^T.
Comparing the [g] coefficient gives sum_j x_j y_j^T E=E N. This is only a
column equation: no identity on the initially clean input columns is assumed.
It implies k>=q by rank subadditivity.

Suppose k=q. Put X=(x_1,...,x_q), Y with rows y_j^T, and V=Y E.
Then X V=E N has rank q, so X is injective and V is surjective. Its image is
exactly im(E N), which lies in the active subspace. Thus X=E X0 and
X0 V=N. Since N²=0, multiplication by a left inverse of X0 and right inverse
of V gives V X0=0. But diagonal entry j of this product equals
y_j^T E X0[:,j]=y_j^T x_j=1, a contradiction. Hence k>=q+1.

This proof permits arbitrary many clean and dirty roles, arbitrary free
scalar mixing, and any call order. It uses no finite census or trace
constraint on unused clean input columns. Imposing such a trace constraint
would incorrectly reintroduce the predecessor's dirty parity obstruction.

## 2. Explicit even-rank construction

Choose binary chain coordinates e_i,f_i for 1<=i<=q so N=Σ e_i f_i^T;
any remaining data coordinates are killed by N. Existence follows from
im N contained in ker N: choose an image basis e_i and preimages f_i,
then complete by kernel vectors. Keep all original data arbitrary.

Let h be one additional clean coordinate, and assume q>0 is even. Set

    x_i = e_i+h,              y_i^T = Σ_(k≠i) f_k^T+h^T  (1<=i<=q),
    x_* = Σ_i e_i+h,          y_*^T = Σ_i f_i^T+h^T.

Every pairing y_j^T x_j=1 through the h coordinate; therefore these q+1
couplings are legal rank-one idempotents. Summing their outer products gives

    Σ_j x_j y_j^T = N + h h^T.

Indeed the image e_i has coefficient (Σ_(k≠i)f_k^T)+(Σ_k f_k^T)=f_i^T;
its h coefficient cancels. In the h row each f_k occurs q times, hence
cancels, while h^T occurs q+1 times and survives. All other rows are zero.
The full formal product is consequently

    I+t(N+h h^T) = (I+tN) direct-sum [g].

On every arbitrary data input the clean output is zero. Its full auxiliary
input action is [g], so a dirty helper does NOT meet the same contract.
The construction neither erases dirty data nor assumes a zero data register.
It remains exact in every order because t²=0.

At q=2 the three pairs are

    (e1+h, f2^T+h^T), (e2+h, f1^T+h^T),
    (e1+e2+h, f1^T+f2^T+h^T).

For odd q use the predecessor's projectors e_i(Σ_k e_k^T+f_i^T)
and (Σ_i e_i)(Σ_i e_i^T). Their q+1 sum is N. That odd-rank identity,
the dirty optimum, normal-form background and involution-product identity
retain their original credit; the clean theorem and even construction are
the contribution here.

## 3. Literal coordinate lowering and complete local comparison

To implement an idempotent xy^T choose any pivot p with x_p=y_p=1.
Define the binary scalar involutions

    B=I+(x+e_p)e_p^T,   A=I+e_p(y^T+e_p^T),   S=B A.

Then S e_p=x and e_p^T S^-1=y^T because y^T x=1. A coordinate reflection
D_p=I+t e_p e_p^T therefore obeys S D_p S^-1=I+t xy^T. The chronological
literal word is B, A, D_p, A, B. Each B is exactly wt(x)-1 CNOTs, and each
A is exactly wt(y)-1 CNOTs. All inverse scalar work is included. No dense
XOR or bulk basis change is billed as one CNOT.

For the even clean word choose p=h. The first q projectors each need 2q
scalar CNOTs; the last needs 4q. Total: q+1 coordinate reflections and
2q(q+2) CNOTs. For an odd rank r the displayed predecessor word lowers to
r+1 reflections and 2r²+4r-4 CNOTs. Applying it on blocks q-1 and one gives
the positive-even dirty baseline q+2 reflections and 2q²-4 CNOTs.

Thus, at stationary complete coordinate-reflection price R, scalar-CNOT
price C and additional clean-resource charge H>=0, the explicit clean word
beats this explicit dirty compiler exactly when

    R > 4(q+1) C + H.

At rank two the comparison is 3R+16C+H against 4R+4C. Equality ties.
This is an exact comparison of two specified words, not a scalar-network
optimum or a claimed physical improvement. Adjacent inverse operations or
other lowerings could improve either baseline; they are not optimized here.

For a general N=T N0 T^-1, conjugate either complete word by T on the data
and identity on h. The verifier emits T^-1 and T as literal row-elimination
CNOT networks, using three CNOTs per row swap. The same transport cost
2 tau(T) C is paid on both sides and cancels in the displayed comparison.
This does not assert that arbitrary T is physically local or free. Any
nonstationary frame, tape, scalar or clean-resource tariff needs a new invoice.

## Proof versus corroboration

The all-q statement is the written rank argument and construction. The finite
verifier independently sums projectors, checks arbitrary square-zero matrices
through four data roles, and checks conjugated ranks through eight. Its
clean-column two-call search allows arbitrary projectors on all five roles.
A separate literal interpreter applies one CNOT or one address swap at a
time to every faithful input basis column. These are reproducible finite
corroborations, not independent human or proof-kernel verification. No native
supplier, recursive price, multiplication theorem or new kappa follows.
