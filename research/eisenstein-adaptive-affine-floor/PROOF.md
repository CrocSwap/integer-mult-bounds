# A pathwise Eisenstein floor for adaptive affine broadcasts

## Model and statement

Use PR2017's fixed 40 Eisenstein E8 lines and its source/reader pairing charge
c(R,A). For each port t, the input X_t is an arbitrary independent b_t-bit
vector, b_t>=0; let N=sum_t b_t. Receiver t must recover all of X_t exactly,
using the complete public paid transcript and the full inputs at ports
orthogonal to t. There is no other free input-dependent information.

A protocol is a finite deterministic rooted decision tree. At a nonterminal
node, determined solely by the prior public answers, it chooses a source set
A, a width q>=0, a binary q-by-N matrix E supported on the input bits of A,
and a constant vector c. It broadcasts y=Ex+c to ALL 40 ports. All q bits
are paid, including redundant or constant answers, at charge

    q c(All,A).

The next node and the decision to terminate are functions only of the paid
answer history. Node identifiers, coefficients and supports are deterministic
functions of that same history: they cannot be an uncharged private header.
Payload queries are affine at each node, although the global encoding function
can be nonlinear. Decoding, query count, source support, coefficients and width
may vary between transcripts. There are no privately chosen branches, relays
with undeclared side information, errors or nonlinear payload queries.

**Theorem.** Every reachable leaf of a correct protocol has total charge at
least N. Direct one-bit broadcasts attain N for every input. In particular,
the optimal per-execution, worst-case and expected charge for equal b-bit
demands is 40b, in this model. The expectation statement holds under every
input distribution because the lower bound is pointwise.

This extends PR2017's fixed-support block-linear floor to a genuinely adaptive
class. The affine-fiber/linear-algebra argument is standard; the contribution
is its precise application to this source-pinned pairing-cost contract, with
pathwise certification and explicit metadata/query exclusions. It does not
claim an optimum for arbitrary nonlinear Eisenstein encoders.

## 1. The entire leaf fiber is affine

Fix a reachable leaf with observed answers y_1,...,y_m. Freeze the matrices
E_j and constants c_j on that path, and concatenate them into E and c. Its
input fiber is EXACTLY

    S = {x in F2^N : Ex = y+c}.

Every input reaching the leaf satisfies these equations. Conversely, an input
satisfying them gives y_1 at the root. By induction it has the same public
prefix at every subsequent node, so the deterministic controller chooses the
same next query and gets the specified next answer. It terminates at the same
leaf. This converse is essential: a mere affine superset would not suffice.
Since the leaf is reachable, S=x_0+ker E for any x_0 in S. Zero-width queries,
repeated answers and early stopping do not change this argument.

## 2. Nonlinear leaf decoding yields linear recovery on the difference kernel

Let P_t select the full orthogonal side-information coordinates available to
receiver t, and let e_k be a demanded coordinate at t. If v lies in ker E and
ker P_t, then x_0 and x_0+v lie in the SAME exact leaf fiber and give receiver
t the same side information. Exact deterministic decoding forces v_k=0.
Therefore

    ker [E;P_t] is contained in ker e_k.

Over F2, a linear functional that annihilates a matrix kernel belongs to its
row space. Thus e_k=d_k E+s_k P_t. This conclusion does not assume that the
receiver's declared decoder is linear. Stack d_k over all N demanded bits,
forming D, and write B=DE. The diagonal port blocks of B are I_(b_t), and
its off-diagonal blocks at distinct NONORTHOGONAL ports are zero. All remaining
entries occur only at the permitted orthogonal side-information ports.

The fixed path has therefore supplied a fitting block-linear identity, even
though its affine transcript might be one branch of a globally nonlinear
encoding. Constants disappear only after passing to the difference kernel;
they are not silently assumed zero in the protocol.

## 3. Apply the retained good-reduction rank certificate

PR2017 constructs a normalized Hermitian Gram matrix H over
Z[omega,1/3], with diagonal 1 and zero at orthogonal line pairs, and reduces
it modulo 2 to Hbar over F4. Its retained proof establishes, for all supports,

    rank_F4 Hbar[R,A] <= rank_Q(pairing spans R,A)/2 = c(R,A).

The radical/minor argument and good-reduction construction remain credited
to PR2017; this package replays their actual exact verifier and checks the
geometry used by its new paths. It does not infer an all-support theorem
from sampled ranks.

Lift Hbar by repeating the port row/column t exactly b_t times, obtaining G.
The fitting conditions imply G o B=I_N, where o is entrywise multiplication.
Split E into its path blocks E_j and D into the corresponding column blocks
D_j. Then B=sum_j D_j E_j. Expand each q_j-dimensional block product into
q_j rank-one terms. Each resulting Schur product has rank at most
rank_F4 Hbar[All,A_j]: repeating rows and columns and multiplying them by
scalar diagonal matrices cannot increase rank. Rank subadditivity gives

    N = rank_F4 I_N
      <= sum_j q_j rank_F4 Hbar[All,A_j]
      <= sum_j q_j c(All,A_j).

This is the cost of this specific execution, not a maximum over other paths.
For attainment, broadcast each demanded bit from its own singleton port;
c(All,{t})=1: the singleton source is a two-real-dimensional plane, so its
rational pairing rank is at most two, and its nondegenerate self-pairing
already has rank two. The price is half that rational rank. This costs
exactly N on every input. More generally, k mutually orthogonal source lines
span a nondegenerate 2k-dimensional rational space, and pairing against All
has rank exactly 2k; thus their price is k. Neither upper-price statement
is inferred from the one-sided mod-2 rank comparison.

## 4. Actual adaptive fixture and changed-hypothesis controls

The retained ten orthogonal four-frame partition gives parity broadcasts.
For one bit per port each frame parity costs four and recovers every port
from its three orthogonal frame mates. The ten broadcasts cost 40.

Our adaptive protocol first sends parity z0 of frame 0. If z0=0 it next sends
z1; if z0=1 it next sends z1+z2. It then sends z2 and the other seven frame
parities. The second answer is globally z1+z0*z2, which has a nonzero mixed
Boolean derivative and is not an affine input function. Every NODE query is
affine and the controller depends only on the paid first answer. All query
source spans, including the union of two frames, have rank four. Every leaf
still costs 40. A variant repeats a paid affine answer on one branch and
has leaf costs 40 and 44, explicitly exercising variable termination and
redundant queries. Unequal/block-demand fixtures use per-bit-plane frame
parities with their actual source ranks, attaining sum b_t.

A purported hidden controller that selects a public leaf label from private
frame parities can reveal all demanded inputs using side information at zero
payload charge. This is a correct decoder but violates the paid-history
controller premise. A genuinely nonlinear node query x_a*x_b has a zero
fiber of size three on two independent bits, not an affine fiber; the path
argument cannot be used for it. These examples delimit the theorem rather
than claim lower costs under the allowed protocol.

Removing an actual frame query leaves a receiver difference direction
undetected; the checker exhibits that kernel vector. Other controls freeze a wrong branch coefficient, omit declared sources or
affine constants, and undercharge a block width. They reject for distinct
reasons. Exact geometry and the logical observation interface are kept
separate; no selected native supplier is executed.

## 5. Supplier interpretation and limits

The task's initial ceiling verifier and lever table were run before synthesis.
The protocol changes the alphabet/observation model, so we do not insert it
unjustifiably into the incumbent 112-port ceiling. Instead, under the
ADDITIONAL inherited Eisenstein Dfc stage identity, equal demands give

    D/T = (s-1)*80b - 2s*C <= -80b

for every positive stage count s. Even granting all other operations zero
cost cannot yield positive deficit within that conditional format. This is
an exact replacement screen, not a physically admitted supplier.

The charge q*c is an explicit abstract pricing premise. Public broadcasting
means all receivers observe every paid bit; localized/private observation
trees are not covered. Input-dependent private headers, nonlinear payloads,
errors, correlated entrance restrictions, cheaper physical sharing, other
geometries and changed stage laws remain outside the theorem. PR814's wider
nonlinear fixed-support class retains its separate 22b-to-40b interval.
No new kappa, selected change, hosting/precision/compiler proof or proof-
assistant verification is claimed. Finite path tests corroborate the written
all-width theorem and do not replace its quantified argument.
