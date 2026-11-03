# Optimal central input-gauge capacity for forward B/C calls

This contribution was produced by Nick Petalas. Apache-2.0.

## 1. Contract and claim

Use the coordinate character model and the paid/helper profiles of Ali
Romman's [capacity proof](../complementary-caller-capacity-gate/PROOF.md).
Those are cited mathematical inputs. Their native counts and admission
obligations are not reverified here. In particular, ordinary caller maps
are complex-linear matrices over the even-power coordinate algebra, all
original inputs are arbitrary, and productive main outputs are independent
full Gaussian jobs. The 408 helper jobs of each call remain separate.

Restrict whole calls to the displayed forward orientations

    A = D [[1,0],[Q^-1,1]],
    B = D [[1,0],[1,Q]],
    C = D [[Q,0],[1,1]],

where D uses seven distinct transverse axes and Q uses another central
axis. Each B or C whole call has 56 A pairs and 56 exceptional pairs of
its own type. Width is any f >= 3, as in the cited character theorem.

Change one premise. A call may include a free central input gauge
G = diag(Q^a,Q^b) on each main pair, so its main matrix is A G, B G or
C G. Count one gauge occurrence for each odd a or b. Even powers remain
ordinary. There are at most 224 occurrences per call. The budget q is an
upper bound, and unused budget is allowed. Different pairs may choose
independently. This is a favorable resource grant, not an implementation
of those gauges. The count is of occurrences at calls, not distinct
prepared fields: sharing a preparation between calls does not reduce q.
All helpers and paid profiles are retained under the declared contract.
An actual changed producer must establish that same helper contract.

Put t = 1-C in (0,1), d = 8^t-7^t, and

    K(t) = 28 + 140*7^t + 84*8^t,
    a(q) = min(q,56),
    b(q) = min(56, floor(max(q-56,0)/2)).

The exact maximum of the integrated sign-cut charge of a whole call is

    K_B(t,q) = K(t) + d*(a(q)+b(q)),
    K_C(t,q) = K(t) + ((1+d)/2)*a(q) + d*b(q).                 (1)

Here "exact maximum" refers to this necessary rank-distance bound. It
does not assert that all of this capacity is attainable as independent
productive targets. If Delta_X(t)=P_X(t)-H_X(t)-K(t) is the cited
ungauged deficit, any complete caller in this changed contract satisfies

    F(t) <= sum_calls (K_X(t,q_call)-K(t)-Delta_X(t)).         (2)

The exact extra-query moment cancels as in the cited theorem. Equation
(2) covers arbitrary finite main wiring, axis reuse and ordinary mixing,
under its retained separate-helper and coordinate-target hypotheses.

At C=17/5000, the first positive right side of (2) for one whole call is
q=31 for B and q=23 for C. Budgets 30 and 22 respectively still give a
strictly negative upper bound. A positive upper bound is not a positive
realized recursive moment.

## 2. Complete local classification

Fix two sign characters in one even-power sector. Let c mark a central
sign flip and e the parity of transverse flips. Then Q changes sign if
c=1 and D changes sign if e=1. Only a,b modulo two matter. All entries
that do not cancel are nonzero multiples of 2, D and powers of Q.
The difference matrix is triangular. Its rank is two when both diagonal
entries are nonzero, one when just one diagonal or the lower entry is
nonzero, and zero otherwise. Consequently the following table holds for
every nonzero character value Q and D. The omitted (c,e)=(0,0) rank is zero.

| Pair | (a,b) | Gauge count | Rank (0,1) | Rank (1,0) | Rank (1,1) | Integrated gain over its ungauged pair |
|---|---|---:|---:|---:|---:|---|
| A | 00 | 0 | 2 | 1 | 2 | 0 |
| A | 01 | 1 | 2 | 1 | 1 | (d-1)/2 |
| A | 10 | 1 | 2 | 1 | 1 | (d-1)/2 |
| A | 11 | 2 | 2 | 2 | 1 | d |
| B | 00 | 0 | 2 | 1 | 1 | 0 |
| B | 01 | 1 | 2 | 0 | 2 | -d |
| B | 10 | 1 | 2 | 2 | 0 | d |
| B | 11 | 2 | 2 | 1 | 1 | 0 |
| C | 00 | 0 | 2 | 1 | 1 | 0 |
| C | 01 | 1 | 2 | 2 | 1 | (1+d)/2 |
| C | 10 | 1 | 2 | 1 | 2 | (1-d)/2 |
| C | 11 | 2 | 2 | 1 | 1 | 0 |

To derive the last column, independently flip axes with probability
p in (0,1/2). Write h_r=(1-(1-2p)^r)/2. A profile with ranks
(r01,r10,r11) has expected charge

    r01*h_7 + r10*p + (r11-r01-r10)*p*h_7.

Since 2*p*h_7 = h_7+h_1-h_8, its coefficient vector on
(h_1,h_7,h_8) is

    (r10+z, r01+z, -z),  z=(r11-r01-r10)/2.

The positive integral in the cited proof sends each h_r to r^t, with a
common normalization. Applying that linear integral gives the table.
For example B10 changes the pair capacity from 7^t+8^t to 2*8^t,
whereas C01 changes it to (1+7^t+3*8^t)/2. Their gains differ.

## 3. Optimal allocation and complete caller bound

Strict increase and strict concavity of r^t give 0<d<1. In an optimum
with an upper-bound budget, the dominated choices in section 2 can be
removed. An A pair offers only (cost,gain)=(0,0) or (2,d).
A B pair offers (0,0) or (1,d). A C pair offers (0,0) or
(1,(1+d)/2). Both exceptional gains are at least d.

If an optimum gauges an A pair while leaving an exceptional pair
ungauged, replace that A choice by the exceptional choice. Cost falls
by one and gain does not fall. Thus some optimum gauges exceptional
pairs first. There are 56 of them. The remaining budget purchases
floor((q-56)/2) A pairs, capped at 56. For q<=56 every available unit
can go to a distinct exceptional pair. This proves (1), including odd
budgets and the saturation at q=168. The indicated gauge choices attain
the bound within this local capacity relaxation.

For a full caller, use the same two-character telescoping inequality as
the cited proof, replacing the cut charge of each whole call by its
gauged charge. Gauges are included in that primitive, so they are not
silently treated as an ordinary step of zero character distance.
Average over sign cuts and integrate. Full independent main targets
contribute their rank^t moment. Additional queries contribute their
exact charged rank^t moment. Add the separate helper credit, subtract
the retained paid profiles, and cancel the extra-query moment. This
gives (2). No new native-count claim enters this argument.

If each odd gauge is instead supplied by its own paid H1 query, its
capacity gain is strictly smaller than its fee for 0<t<1. This is
consistent with the predecessor's already-covered paid-query case.
The new question requires a cheaper source of the gauged input contract.

## 4. Certified thresholds

The checker reads the cited P/H profiles and encloses r^(4983/5000)
between consecutive multiples of 10^-12. Decimal arithmetic only
proposes each lower integer l. Acceptance uses the integer inequalities

    l^5000 <= r^4983 * (10^12)^5000 < (l+1)^5000.

Signed interval addition then gives these outward enclosures:

| Type | Ungauged deficit | Last failing budget and margin | First passing budget and margin |
|---|---|---|---|
| B | (30.276795,30.276796) | q=30: (-0.582842,-0.582841) | q=31: (0.406957,0.406958) |
| C | (22.658954,22.658955) | q=22: (-0.771171,-0.771170) | q=23: (0.223728,0.223729) |

These are raw capacity-minus-paid margins. Monotonicity of (1) settles
every smaller budget. The threshold is for one whole call's optimistic
bill at the specified exponent, not a per-call requirement in arbitrary
mixtures. For mixtures use the sum in (2).

## 5. Evidence and limits

The proof carries the all-t and all-width quantifiers. The checker
compares the zero-pattern argument with 384 literal rational matrix
rank cases, enumerates all 256 sign masks for each of 12 local choices,
and checks the complete 0..224 budget curve by an independent dynamic
program for all 66 fractions n/d with 2<=d<=12 and 1<=n<d. This gives
29,700 budget comparisons. It certifies the threshold inequalities with
integer powers. A deliberately undercharged two-input A option must
violate the envelope. B/C and single/double A controls distinguish the
important local contracts. Its stdout receipt is generated from the
checks and binds the six package files by SHA256.

Not covered: inverses or transposes with this new gauge placement, output
gauges, gauges on other axes, shared helper/main state, a changed native
paid profile, a physical gauge producer, or a claim that capacity is
attainable as full independent outputs. Native replay, compiler, hosting,
precision/tape, all-size admission, proof-kernel review and the selected
cold replay are unrun. There is no new kappa or complete multiplication
theorem. The five selected framework assumptions remain.

Credit Ali Romman for the capacity theorem and retained profiles;
unpaidmoon for the odd-input-gauge handoff in PR6639; Dugongue, Cao
Yifan/intqwq, Chris R/Clear1nsight and the retained B/C lineage.
Dugongue's fine-gap-gaussian-boundaries/consumer.md constructs different
chronological B/C gauge incidences and prices an alternating schedule.
That construction is related work, not a result checked or used here.
