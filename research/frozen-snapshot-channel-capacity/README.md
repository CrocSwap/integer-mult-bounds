# Sharp channel loss from frozen live snapshots

This contribution was produced by Nick Petalas. Claim type: scoped algebraic
proof with exact finite corroboration. No new kappa is claimed.

If an insertion must preserve a live copied value, its direction must lie in
the kernel of that snapshot map. Over D = Z[1/2], imposing constraints of
rational rank r removes at most r normalized unit channels. This bound is
sharp even when the rational rank of the eligible pairing does not change.
Thus rational pairing rank can miss the entire loss at a live-copy boundary.

The new step combines a chronological frozen-snapshot contract with the
saturated dyadic pairing. It supplies a restriction formula, a sharp loss
bound and explicit extremizers. It does not validate a predecessor result.

## Contract and theorem

Let K be an m-by-n matrix over D. Its unrestricted unit-channel capacity is

```text
c(K) = max { t : X K Y = I_t for matrices X,Y over D }.
```

Let C be any s-by-n matrix over D. The insertion columns must now satisfy
C Y = 0. Define

```text
c_C(K) = max { t : X K Y = I_t and C Y = 0 }.
r = rank_Q(C).
```

All coefficient matrices are finite. A zero-dimensional identity is allowed.
Let Q have columns forming a full D-module basis of ker_D(C). Then

```text
c_C(K) = c(K Q),
max(0, c(K) - r) <= c_C(K) <= c(K).
```

The exact value can therefore be obtained by applying the cited Smith
unit-block criterion to K Q. It is the number of unit Smith factors of K Q,
or equivalently its minimum rank modulo an odd prime. Q must be a saturated
module basis; a rational nullspace basis scaled column by column is insufficient.

For every c,r >= 0 and every integer loss ell in [0,min(c,r)], there are K,C
with c(K)=rank_Q(K)=rank_Q(K Q)=c, rank_Q(C)=r, and c_C(K)=c-ell.
The ambient number of insertion coordinates in this construction is c+r.
These are sharp algebraic examples, not physical P104 cuts.

## Why this is the frozen-copy equation

At a nominated chronological comparison boundary, let z be the current cut
state and let the unchanged copied snapshot be t=S z. Suppose the allowed
insertions are z -> z+R0 Y a, where a is arbitrary source data. Keeping t
unchanged requires

```text
S R0 Y = 0.
```

If eligible reader rows are L0, the normalized source-response condition is
X L0 R0 Y = I_t. Use K=L0 R0 and C=S R0 in the theorem. The rank in the loss
bound is rank_Q(S R0), which can be smaller than the number of copies.
Dependent copied functionals must not be counted repeatedly.

This is an insertion interface with fixed eligible L0,R0 and frozen copied
slots. It does not classify all helper basis changes. It does not grant a
free read of dirty state, prove an arbitrary basis sequence legal at every
intermediate comparison, or permit an ERASE at an unverified intermediate
state. Every comparison boundary needs its actual equation. If the copied
slots also change, the contract changes and this restriction need not apply.

## Proof

First, ker_D(C) is saturated in D^n. If a nonzero d in D satisfies C(dv)=0,
then d C v=0 implies C v=0 because D is an integral domain. More explicitly,
D^n/ker_D(C) is isomorphic to im_D(C). This image is a free module of rank r,
because D is a principal ideal domain. The quotient is free, so the sequence
splits. Consequently Q extends to an invertible n-by-n matrix V=[Q P] over D,
where P has r columns. This splitting also covers zero C and a zero kernel.

Every admissible column of Y lies in ker_D(C), so Y=Q Z for a unique matrix
Z over D. Conversely every Q Z is admissible. Substitution into X K Y=I_t
proves c_C(K)=c(K Q). Restricting admissible Y proves the upper bound.

For the lower bound, reduce modulo any odd prime p. Every invertible D-matrix
remains invertible over F_p, so

```text
rank_Fp(K mod p) = rank_Fp([K Q | K P] mod p)
                  <= rank_Fp(K Q mod p) + r.
```

The single-cut capacity theorem of Ali Romman's PR5615 states
c(A)=min_(odd primes p) rank_Fp(A mod p). Applying that cited theorem to K
and K Q gives c(K Q)>=c(K)-r. Capacity is nonnegative, which gives the stated
lower bound. This argument does not replace ker_D(C) by ker_Fp(C mod p).
Those two kernels can have different dimensions.

For sharpness, choose any odd prime p and let K=[I_c | 0_r]. For j<=ell,
the j-th equation of C is

```text
x_j + p y_j = 0.
```

For ell<j<=r, its equation is y_j=0. The coordinates are x_1,...,x_c and
y_1,...,y_r. The equations are independent over Q. A full kernel basis has
columns p e_(x_j)-e_(y_j) for j<=ell and e_(x_j) for ell<j<=c. Every solution
is an arbitrary D-linear combination of those columns. Multiplying by K
gives diag(p I_ell,I_(c-ell)). Its rational rank is c and its dyadic capacity
is c-ell. Selecting the final c-ell coordinates explicitly attains that unit
block; reduction modulo p gives the matching upper bound. Empty blocks cover
c=0, r=0 and ell=0.

## Smallest displayed loss and dirty realization

Take K=[1 0], C=[1 3]. The full kernel basis is Q=(3,-1)^T. The unconstrained
capacity is one, while K Q=[3] has capacity zero and rational rank one.
Over Q, division by three normalizes the response; it is unavailable in D.

A synthetic reversible word realizes this restricted direction on arbitrary
source x and dirty helpers h0,h1. Retain the snapshot t=h0+3h1. Execute

```text
h0 += x       three times
h1 -= x
              reading cut: h0=h0_initial+3x, h0+3h1=t
h1 += x
h0 -= x       three times
              ERASE comparison: both helpers restored, h0+3h1=t
```

The source is unchanged. There are eight unit-coefficient ADDs and one
retained snapshot, whose production and erasure are declared operations,
not given a physical COPY tariff here. Snapshot equality is asserted at the
two displayed boundaries, not between every ADD. The dirty contribution to
the reader remains h0_initial; no independent target is credited. An
unrestricted direction (1,0)^T would yield unit response but changes the
snapshot by x and fails the frozen comparison.

Saturation must precede modular reduction. For K=[1 0], C=[3 0], the true
kernel is span_D((0,1)^T), so the constrained capacity is zero. Modulo three,
C becomes zero and taking its full modular kernel would incorrectly allow
one channel. Separately, replacing the same true kernel by the nonsaturated
column (0,3)^T can falsely lose a real unit channel when K=[0 1]. These two
controls distinguish opposite implementation errors.

## Evidence and reproduction

From the worktree root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/frozen-snapshot-channel-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/frozen-snapshot-channel-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/frozen-snapshot-channel-capacity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/frozen-snapshot-channel-capacity --check-source-history
```

Any CPython 3.12 interpreter can replace this local path. Expected markers
are PASS_FROZEN_SNAPSHOT_CHANNEL_CAPACITY, PASS_REGISTERED_RESEARCH_PACKAGE
and PASS_RESEARCH_COMMIT_BYTES. The verifier writes no files and emits a
generated JSON receipt binding the results to the SHA256 of every package
file. It imports no predecessor executable and reruns no predecessor census.

The finite checks enumerate:

- All 4,096 pairs of a 2-by-2 K and a one-row C with entries in {-1,0,1,3}.
  Exactly 2,100 pairs lose capacity; 108 of these retain rational pairing rank.
- All 6,561 pairs of 2-by-2 K,C with entries in {-1,0,1}.
- All 69 sharp constructions with c,r in {1,2,3}, all permitted ell, and
  p in {3,5,7}; each has its predicted capacity and unchanged rational rank.
- All 343 integer triples (x,h0,h1) in {-3,...,3}^3 for the displayed word,
  totaling 2,744 unit ADD updates, including the two snapshot boundaries.
- Eleven labelled semantic, boundary and malformed-input controls.

Kernel equations, rational dimensions and gcds of maximal minors check full
kernel saturation. Determinantal divisors compute unit capacities, and
separate rational and prime-field elimination checks the bounded prime-rank
profiles. The prime list through 31 covers the executed small census; it is
not a claim that these primes suffice for arbitrary matrices. The integer
kernel constructor uses unimodular Bezout column operations. Clearing powers
of two reduces general dyadic equations to integer equations in the written
proof; the finite matrix census is over the stated integer domains.

## Source, credit and limitations

Base: canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority
revision 8, selected PR6030. The selected binding baseline passed; it is
metadata orientation only. The original p104-side-correction card is retained
in TASK.json, with the changed scope and its connection to live-cut eligibility.

Credit woklerx / [PR1437](https://github.com/CrocSwap/integer-mult-bounds/pull/1437)
for the chronological live-COPY stabilizer and the opening for multiple live
functionals, with Sagar Thakrar / PR1062 and the credited R439 lineage.
Credit Ali Romman / [PR5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615)
for the dyadic single-cut unit-capacity theorem, with PR5599/5602/5609/5611,
Nick Petalas / PR5115 and their retained helper/native/controller lineage.
Both predecessor texts are exact provenance pins in SOURCES.json. Smith
normal form, saturation, splitting over a principal ideal domain and the
rank inequality are classical. The new contribution is their frozen-snapshot
restriction, sharp loss envelope and arbitrary-dirty realization above.
Apache-2.0.

Overlap checks inspected live open PRs, recent handoffs, active Discussions,
account PR history, merged PR searches and main-tree READMEs. The cached report
covered 409 open PRs and 6,361 Discussion records; its sparse local inventory
covered 128 of 8,917 note paths. Direct Git searches supplied additional
main-tree coverage. These are bounded novelty checks and exclude unpublished
work. No claim is made that every historical package was searched.

This result supplies no selected-word L0,R0,S, physical carrier, legal native
frame, productive output, favorable complete invoice, supplier admission or
complete multiplication theorem. Basis synthesis and intermediate legality,
copy costs, ownership, dirty cancellation, coefficient growth, precision/tape,
compiler and outer obligations remain. The selected frontier and its five
framework assumptions retain their status. Selected cold replay, Lean and
Docker were not run. Independent human and formal proof-kernel review are
unclaimed.

Power of Ten inspection bounds the verifier to matrices with at most six rows
and columns, integer coefficients of at most 256 bits, 514 Euclidean iterations,
fixed finite fixture products and at most 720 permutation terms per determinant.
No recursion or dynamic dispatch is used for scientific checks. Functions stay
below sixty lines. Explicit exceptions keep acceptance checks active under -O.
Rule 3 has a Python managed-runtime deviation: integer, Fraction and collection
allocation is dynamic. Fixed domains, matrix limits, coefficient limits and
streamed cases bound live state. The available diagnostics are warning-strict
normal and optimized execution; no separate static analyzer is installed or
claimed, and no repository-wide analyzer configuration is changed. Revisit the
allocation deviation if this finite verifier becomes a production solver.

## Open next questions

1. Does an actual proposed P104 live cut lose capacity after its copied
   snapshot equations are imposed? First nominate the changed physical word,
   derive full eligible L0,R0 and every unchanged snapshot map S, then compute
   ker_D(S R0). A physical proposal and source-bound bases are missing here.
2. Can changing copied slots recover a lost unit channel at favorable complete
   cost? First specify an admissible copied-slot update and inverse, with all
   COPY, ERASE, native-frame and target charges. A complete producer/consumer
   contract and tariff are missing here.

TASK.json records the same questions with first steps and blockers.
