# A private header is charged on the joint transcript cut

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof. The finite replay corroborates new private
protocols and boundary failures. It does not re-establish the cited geometry.

## Contract

Use the sixty Gaussian E8 ports and pairing price c(R,S) of ywz65's PR2641.
Port t supplies an independent uniform b_t-bit string X_t. Its receiver must
recover X_t on every input and initially knows only orthogonal-port inputs.
Source encoders and demand receivers are distinct roles. Source access and
encoding are free in this abstract message model. Bit delivery pays the
declared pairing rank. Put B=sum_t b_t.

Fix nonempty source and reader sets A,R. A deterministic header M=h(X_A)
has a finite prefix-free binary code. Deliver it only to receivers in R,
at price c(R,A) per bit. Put L=E[length(M)]. No other receiver observes its
value, length, presence, timing or routing. The protocol has these two parts:

1. A fixed finite ordered payload list, with source sets, reader sets,
   functions and finite prefix-free codebooks independent of M.
2. For each M=m, a finite ordered private payload list. Every reader set
   is contained in R. Each source set S_j(m) contains A. The encoder can
   therefore compute h(X_A) from its declared original inputs and select
   its branch without another uncharged delivery of M. It sends a function
   f_j(m,X_S_j(m)) using a finite prefix-free codebook fixed by m.

The private list can change its length, order, supports and codebooks with m.
Its descriptions are fixed in advance as functions of m. Receivers in R know
m and the corresponding schedule. Receivers outside R observe only their
fixed-list payloads. Every additional input-dependent signal is excluded,
including an observable absence of a private message outside R. Payloads do
not relay earlier payloads. Arbitrary nonlinear encoding and decoding are
allowed. Fixed and private payloads pay c(R_j,S_j) per delivered bit.

The requirement S_j(m) contains A is sufficient, rather than asserted
necessary. It is deliberately explicit about encoder knowledge. The theorem
does not cover an encoder secretly supplied M or private schedules visible
at an additional reader. Prefix-free codes charge termination information.

## Theorem

Let Q range over the 640 retained nonorthogonal cliques, each of weight
1/192. Define

    eta(A,R) = sum_Q [Q meets A and Q meets R]/192.

Under the contract above, with total charge C,

    E[C] >= (2/3) B + c(R,A) L - eta(A,R) H(M)
         >= (2/3) B + (c(R,A)-eta(A,R)) L
         >= (2/3) B.                                      (1)

Thus the expected and worst-case Gaussian charge for equal b-bit demands
remains at least 40b in this private-reader model. This is not a pointwise
bound and does not establish a positive private-header surcharge.

The cited geometric premises are incidence 128 at every port, and

    sum_Q [Q meets T and Q meets S]/192 <= c(T,S).          (G)

These are Sagar Thakrar's PR738 results retained in PR2641. They are premises
here, not fresh enumerations or independently verified geometric claims.

## Joint-cut simulation lemma

Fix a clique Q and fix X outside Q. Orthogonal side information of a receiver
in Q lies outside Q. For each payload retain its codeword exactly when both
its source and reader sets meet Q. Include M in the retained transcript only
if both A and R meet Q. There are three cases.

If Q misses R, no receiver in Q observes the header or private list. Its
fixed-list messages omitted from the retained transcript have sources
outside Q, so the fixed outside inputs determine them. The retained fixed
transcript consequently determines all receiver observations in Q.

If Q meets R but misses A, the fixed outside inputs determine M. They also
determine the entire private schedule. Every omitted message received by Q
has its source outside Q, so it is computable from those inputs and M.
Again the retained transcript determines all receiver observations in Q.

If Q meets both A and R, retain M first. It specifies the private schedule.
Every omitted payload received by Q is computable from M and the fixed
outside inputs. The receiver observations in Q can therefore be simulated.
Receivers outside R are simulated using their fixed list only; the argument
does not silently deliver M to them in the actual protocol.

In every case equal retained transcripts imply equal demanded X_Q, by exact
decoding. No conditional independence after observing M was used.

## Entropy accounting

Let P be total payload charge and write B_Q=sum_(t in Q) b_t. The simulation
lemma, entropy subadditivity and the prefix-code bound give

    B_Q <= [Q meets A and Q meets R] H(M | X_outside_Q)
           + E[sum_j length(Y_j) [Q meets R_j and Q meets S_j]]. (2)

For the case missing R there is no branch-dependent received list. In the
other cases condition on M before applying subadditivity to the finite list.
Each conditional distribution uses a subset of its specified prefix-free
codebook, so its entropy is at most expected codeword length. Varying list
length is known from M only to R; the simulation cases justify this use.
The same argument applies to the fixed list, whose distribution can be
conditioned on M when M is retained or already determined by outside inputs.

Multiply (2) by 1/192 and sum Q. The left side is (2/3)B. Bound each header
entropy by H(M), and apply (G) to every realized payload support pair. This
gives (2/3)B <= eta(A,R) H(M)+E[P]. Adding c(R,A)L proves the first inequality
in (1). Kraft's inequality gives H(M)<=L, and (G) for the header gives
eta(A,R)<=c(R,A), proving the rest. Finite alphabets justify every sum.

## Why a strict surcharge is not obtained

The retained PR738 certificate already gives source F=(0,1,2,11,12,45) and
reader G=(0,3,4,5,6,7,8,9,10,54,55,56,57,58,59) with pairing rank one and
192 joint clique hits. Thus c(G,F)=eta(F,G)=1, a cited datum.

Give the six ports of F independent bits and use their parity as M. For
each clique meeting F, this parity has conditional entropy one after fixing
outside-Q inputs. Consequently the joint-cut header term is exactly
eta(F,G)H(M)=1. The comparison c-eta can have zero gap. This proves sharpness
of that entropy comparison, not attainment of a complete 40b communication
code or impossibility of stronger private-header lower bounds.

The replay implements parity, a nonlinear Boolean header and a variable
prefix header on these six active inputs. Only active recipients at lines
0 and 45 learn M. Remaining active demands receive their fixed direct bit.
Private payload sources declare F, including any additional demanded source;
their singleton reader price is one. Header price one is the cited pair's
price. These are exact small protocols, not a claimed optimal code.

## Failure boundaries

An outsider can learn a hidden bit from the presence or absence of a
zero-bit message. Its payload bit charge is zero, but its schedule observation
has two values. This violates the private-list recipient rule. The replay
keeps this literal leak, and rejects a branch-dependent message outside R,
an encoder without A, a changing fixed schedule, non-prefix codebooks and
an actual missing-demand message.

Removing these premises is a different communication model. No physical
primitive, native source, restored helper, stock/precision/tape bill, supplier
admission, selected-frontier change or multiplication theorem follows from
(1). All five selected framework assumptions remain.

## Sources and credit

ywz65 PR2641 supplies the public-header theorem, conditional transcript
argument and open localized/private-header question. Sagar Thakrar PR738
supplies the Gaussian geometry, joint support inequality and cited sharp
support pair. ToikY PR888, Alexander Templeton PR785, Michael Fischler PR814
and Jerry Chen PR912 retain the transcript and paid-header lineage, alongside
Joel Pulikkan, Douglas Colkitt and DreamingOfClouds.

Nick Petalas PR4897 studies localized sources with public readers and proves
a strict surcharge in that different contract. Its theorem, construction
and flat-census transformation are not used here. The new step is the
private schedule simulation and the joint A,R cut, derived directly from
the source observation contract. Entropy and prefix coding are classical;
global literature priority is unclaimed. Independent human and formal
proof-kernel review are unclaimed.
