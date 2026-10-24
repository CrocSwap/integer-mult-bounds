# Exact simultaneous-success tradeoff

## Model and statement

Retain Alexander Templeton's [PR785](https://github.com/CrocSwap/integer-mult-bounds/pull/785)
fixed-support message model, using Douglas R. Colkitt's
[PR703](https://github.com/CrocSwap/integer-mult-bounds/pull/703) Hurwitz geometry
and pairing tariff. Those results are cited premises, not replayed results here.
The new premise permits decoding errors and measures simultaneous success.

There are five orthogonal mate pairs of Hurwitz lines. More generally, consider
an abstract matching with m pairs. Every port t holds an independent uniform
b-bit input X_t, with b a nonnegative integer. Each message j has fixed source
support A_j, fixed reader support R_j, fixed integer width q_j, and is an
arbitrary function of X restricted to A_j. A reader receives the whole message
when it belongs to R_j. Each receiver also knows its mate's input for free.
Every other observation must be included in the messages. There are finitely
many messages. There is no input-dependent support, timing or width metadata,
interactive relay, additional side information or correlated input.

The inherited tariff c(R,A) is zero for an empty support or orthogonal singleton
mates, one for every other case having a singleton support, and two when both
supports have at least two elements. The charge is the fixed integer
C_actual = sum_j q_j c(R_j,A_j). This is an abstract additive pricing premise.
No physical nonlinear copy-cost theorem is inferred from it.

**Theorem.** For any nonnegative integer budget C, the largest possible
probability that all 2m receivers are correct is exactly

    P_max(m,b,C) = 2^(-max(0, mb - floor(C/2))).                 (1)

The physical Hurwitz application has m=5. The arbitrary-m assertion is about
the stated matching tariff, without asserting that the same geometry exists
for other m. Independent shared or private random coins do not improve (1)
when every fixed-coin realization retains the fixed-width charge budget.

## Upper bound by successful fibers

A transversal T selects one endpoint of each mate pair, so there are 2^m
transversals. Let J_T contain messages whose reader and source supports both
meet T, and put Q_T = sum_(j in J_T) q_j.

Fix every input outside T. For a fixed displayed transcript of the messages
in J_T, there is at most one X_T assignment on which every receiver succeeds.
Indeed, messages received in T but absent from J_T depend only on the fixed
outside inputs. Every receiver's free mate input is also outside T. Thus each
receiver in T has identical observations on two assignments with the same
displayed transcript. Both assignments cannot be correct at every receiver in
T unless their complete X_T tuples agree. This is the successful-subset
version of Templeton's zero-error injection; correctness outside T need not be
used for this upper bound.

There are at most 2^Q_T transcripts. The conditional probability of simultaneous
success, under the uniform mb-bit X_T, is at most min(1,2^(Q_T-mb)). Averaging
over outside inputs leaves the same bound for the unconditional probability p.

Colkitt's transversal accounting gives, for every support pair,

    sum_T 1[R intersects T and A intersects T] <= 2^(m-1)c(R,A).

For completeness, a zero-tariff pair never meets one transversal on both
sides; a tariff-one pair has a singleton support, present in exactly half
the transversals; a tariff-two pair meets at most all transversals. No
geometry enumeration is needed for this elementary application.

Consequently sum_T Q_T <= 2^(m-1) C_actual <= 2^(m-1) C. Some transversal has
integer Q_T <= floor(C/2). Applying its successful-fiber bound and p<=1 proves
the upper half of (1). In particular the odd-budget plateau follows from an
integer transcript bound, rather than a continuous entropy relaxation.

## Attaining construction

There are mb pair-coordinate positions. Set k=min(mb,floor(C/2)) and choose
any k of them in advance. For each chosen coordinate of mate pair {u,v}, send
the one-bit parity X_u XOR X_v from support {u,v} to readers {u,v}. This costs
two units per coordinate and at most C in total.

For a transmitted coordinate each receiver XORs the parity with its mate's
bit and is correct. For an untransmitted coordinate each receiver guesses
its own bit equals its mate's bit. The two receivers are simultaneously
correct exactly when that pair's bits agree. This has probability 1/2, and
these equality events are independent across the mb-k omitted coordinates.
All receivers therefore succeed with probability 2^(-(mb-k)), attaining (1).
Unused odd budget does not help. No clean helper or physical implementation
is being supplied by this abstract code.

For random codes, fix all encoder and decoder coins independently of the
inputs. Each resulting deterministic code satisfies the same upper bound.
Averaging proves the random-code statement. The deterministic parity code
already attains it.

## Consequence and limits

Ten one-bit ports at budgets C=0,...,10 have exact optimum success probabilities

    1/32, 1/32, 1/16, 1/16, 1/8, 1/8, 1/4, 1/4, 1/2, 1/2, 1.

For any b>=1, saving even one unit below the zero-error floor 10b forces
simultaneous failure probability at least 1/2. Saving 2d units forces success
probability at most 2^-d. These statements concern simultaneous correctness;
individual receiver error rates have a different optimization problem.

An expected-charge budget with variable execution lengths is outside (1).
For example, choose independently of inputs between full parity delivery
with probability r and the zero-message strategy otherwise. Its expected
charge is 10br and its success is r+(1-r)2^(-5b), which need not obey (1)
with C replaced by that expected charge. This example does not contradict
Jerry Chen's PR912 zero-error expected-cost theorem. No adaptive-routing,
variable-length or unrestricted private-header theorem is claimed here.

The finite checks corroborate the proof by literal decoding and independent
decoder optimization; they do not prove its unbounded parameters. No native
supplier, Dfc admission, improved kappa or complete multiplication theorem
follows from the result. Source acquisition, encoding, decoding, physical
hosting, cleanup and tape costs remain outside this abstract charge model.

This contribution was produced by Nick Petalas. The matching geometry,
tariff, transversal method and zero-error transcript argument retain the
predecessor credit above. No literature priority is claimed for the general
counting method. Apache-2.0.
