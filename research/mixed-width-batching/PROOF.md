# Least replication with compatible supplier-width menus

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with finite exact corroboration.
The arithmetic below does not establish a physical supplier or a new kappa.

## 1. The changed chronological contract

Fix a nonempty finite list of chronological batches. Batch j contains q_j
independent jobs before replication, where q_j is a positive integer. All jobs
in that batch have the same rank and required arbitrary-input endpoint. Give
the batch a nonempty finite menu W_j of positive integer productive widths.

A width w in W_j denotes an available completed program on exactly w such
jobs. Each menu program must have the same required endpoint per job and
compatible entry, ownership, spectator and return contracts. Under common
positive integer replication a, the batch has a q_j jobs. The allowed policy
partitions those jobs into whole menu invocations. It completes every invocation
and that entire batch before its chronological parent resumes. Distinct cuts
remain distinct, even when they have equal ranks or equal multiplicities.

No partial invocation, padding with additional productive inputs, job sharing,
cross-cut pooling or unfinished return is allowed. These restrictions define
the optimization problem. The theorem makes no claim about more general
schedules.

Mihir Srivastava's PR4507 gives the exact local LCM when each smaller rank has
one prescribed width. Its global fixed-library successor PR4892 retains that
one-width contract. Here the menu is a changed premise: even one batch may
combine programs of different widths. This is not a different rank profile or
stopping-height instance of the old recurrence. The recent homogeneous-width
PR6612 also retains a single prescribed width at each rank.

Define the additive monoid

    H(W) = {sum_(w in W) c_w w : every c_w is a nonnegative integer}.

By the policy itself, a is feasible exactly when

    a q_j belongs to H(W_j), for every batch j.                 (1)

Necessity counts the jobs served by each whole invocation. For sufficiency,
choose the indicated disjoint partition and run the completed programs in
sequence at that cut. Compatibility and completed return are hypotheses of
this abstract composition. Formula (1) does not construct compatible physical
menu members or their routing.

## 2. Finite residue certificates

For one menu W, let d=gcd(W), let V={w/d : w in W}, and let m=min(V).
The integers in V have gcd one. On the m residues modulo m, put a directed
edge r to r+v modulo m of positive weight v for each v in V. Residues reachable
from zero form a submonoid of the finite additive group Z/mZ. A finite
submonoid is a subgroup: repeated addition supplies each additive inverse.
Since gcd(V)=1, the generated subgroup is all of Z/mZ. Every residue is
therefore reachable.

Let A_r be the shortest-path distance from zero to residue r. Equivalently,
A_r is the least member of H(V) congruent to r modulo m. The empty path gives
A_0=0. Positive weights allow a shortest path without a repeated vertex, so

    A_r <= (m-1) max(V).                                      (2)

Store one attaining coefficient vector for each A_r. For any integer n>=0,

    n belongs to H(W)
      iff d divides n and n/d >= A_((n/d) mod m).              (3)

The forward direction follows from minimality in the residue. For the reverse
direction, append (n/d-A_r)/m copies of the minimum coin m to an attaining
representation of A_r. This is an integer and is nonnegative. Rescaling by d
gives the literal invocation counts in W.

The residue table has a small independently checkable certificate. Verify
A_0=0, the residue of every A_r, nonnegative attaining coefficient vectors,
and all inequalities

    A_((r+v) mod m) <= A_r+v.

The inequalities imply that each A_r is at most the weight of every path to r,
by induction from zero. The attaining vector gives a path of weight A_r. Thus
the table is exactly minimal, without trusting the algorithm which found it.

These are classical numerical-semigroup and shortest-path facts. The new
application is the chronological menu contract and exact replication procedure.
No literature priority for Apéry sets or shortest paths is claimed.

## 3. A bounded exact least-replication procedure

For batch j, write d_j, m_j and A_(j,r) for the preceding quantities. Put

    C_j = max_r A_(j,r) - m_j + 1.

Every integer at least C_j belongs to H(V_j). Indeed, if n has residue r and
n<A_(j,r), then n<=A_(j,r)-m_j<=C_j-1. If m_j>1, a residue attaining the
maximum also proves that C_j-1 is a nonnegative missing integer. If m_j=1,
C_j=0 and H(V_j) is all nonnegative integers. In particular C_j is always
nonnegative.

The divisibility part of (3) is equivalent to

    d_j/gcd(d_j,q_j) divides a.

Set

    L = lcm_j d_j/gcd(d_j,q_j),
    h_j = L q_j/d_j,
    T = max(1, max_j ceil(C_j/h_j)).

All h_j are positive integers. Every feasible replication is a multiple L t.
At t=T, the normalized size h_j T is at least C_j for every j, so every
batch is feasible. Therefore the exact answer is

    a_min = L min{t in {1,...,T} :
                    h_j t >= A_(j,(h_j t mod m_j)) for every j}.       (4)

This is a finite terminating decision for every finite positive input list.
The coefficient vectors from (3) produce all required invocation witnesses.
Testing every smaller t proves minimality. Formula (2) also gives

    C_j <= (m_j-1)(max(V_j)-1).

The implementation bounds widths by 64, menus and batches by eight, and
multiplicities by 4096. Consequently T<=3969, L<2^48, and a_min*q_j<2^72.
The public partition operation accepts totals below 2^80. These are executable
capacities, not restrictions on the written theorem. It uses residue Dijkstra
with at most 64 settled vertices and scans at most 3969 multiples of L.

For a singleton menu W_j={B_j}, the normalized menu is {1}, C_j=0, and T=1.
Formula (4) reduces exactly to the predecessor's LCM. For general menus the
gcd condition alone is insufficient. W={4,7}, q=1 has L=1 but a_min=4.
Pooling two q=1 cuts with W={2} would also be invalid: each cut still needs
even a, although their aggregate job count is even at a=1.

## 4. Strict and unbounded improvement over every single-menu-width choice

For every integer N>=2, take two separate cuts of the same job rank, with

    W={N,N+1},   q_1=N,   q_2=N+1.

The menu policy has a_min=1. Invoke the width-N program once at the first cut
and the width-(N+1) program once at the second cut. Positive replication cannot
be smaller than one.

If one width must be selected for that job rank and used at both cuts, choosing
N requires N to divide a(N+1), hence N to divide a. Its exact minimum is N.
Choosing N+1 has exact minimum N+1, by the same coprimality argument. Thus

    best single-width replication = N,
    mixed-width replication       = 1.

The reduction factor is exactly N and is unbounded. If the parent has a fixed
positive source count S and productive width S a, the same factor applies to
that productive width. This is a conditional batching family, not an assertion
that the selected construction already supplies the two programs.

Actual mixing within one cut is also possible: W={4,7}, q=11 has a_min=1
with counts (1,1), whereas either singleton choice needs replication at least
four. Both effects are described by the same procedure, rather than an LCM
over all menu widths or a single choice per rank.

## 5. Cost boundary

Suppose each menu program's complete charged cost is exactly lambda_j times
its productive width, with the same lambda_j for that batch. The total cost
at cut j is then

    sum_w c_w lambda_j w = lambda_j a q_j.

Dividing the complete sum by a parent productive width S a cancels a. The
normalized cost is sum_j lambda_j q_j/S. An upper bound lambda_j w for each
complete program similarly gives an upper bound on the normalized bill.
There is no exponent improvement from merely reducing replication under this
linear-cost hypothesis.

Equal endpoints or equal normalized paid-rank histograms do not establish
that hypothesis. Per-invocation overheads, unequal tariffs, storage extent,
physical movement, native adaptation, owned lifetimes, precision and stock
must be included before a physical menu can use the conclusion. If menu
members have different normalized costs, equation (4) still solves job-count
feasibility, but cost optimization is a different problem.

The exact finite tests use compatible direct-sum shear programs on independent
triples (x,y,dirty), sending each to (x+y,y,dirty). They execute every declared
invocation and every cut, and compare complete outputs. Their synthetic linear
bill illustrates the conditional identity; it is not a native caller invoice.

## 6. Evidence and stopping boundary

The verifier checks residue certificates against a separate total-size dynamic
program, compares least replication with an exhaustive positive-integer oracle,
executes the strict-family invocation schedules, and rejects malformed menus
and corrupted certificates. No predecessor verifier, native construction or
published numerical result is replayed as the deliverable.

The universal statement rests on this written proof. Its finite corroboration,
metadata/source bindings and hosted execution are separate evidence types.
Independent human and formal proof-kernel review are unclaimed. The first
strict improvement above ends the research scope. A real compatible menu and
its full physical bill are open next questions, not assumed follow-on work.
