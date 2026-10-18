# Literal ripple-counter costs with direction reversals

This audits the fixed-direction hypothesis of
`CounterArithmetic.total_steps_bound` at the source pins in `SOURCES.json`.
That theorem and its README correctly restrict the direction. We find no
counterexample to that theorem. The result below supplies a more general
accounting contract for clients that change direction, and concrete
counterexamples to dropping the existing hypothesis.

## Model and exact identity

Use the pinned `RippleCounter.instruction` without modification. A call starts
with the head on the least significant cell of a width-w binary word bounded
by two separators. Increment is direction 1, decrement direction 0. A call
finishes at the **first** done state, with the head returned to its initial
position. A carry/borrow out is a wrap. No reset or other operation intervenes
between calls in this statement. Exterior cells are arbitrary and untouched.

For direction d, let P_d(x) be the number of bits of x equal to d. Thus
P_1 is the number of ones and P_0=w-P_1. If k initial bits propagate the
carry/borrow, the physical call costs c=2k+2. Let o be 1 for a wrap and 0
otherwise. A nonwrapping call deletes k propagating bits and creates one;
a wrapping call deletes all w propagating bits and creates none. In both cases

    P_d(x') - P_d(x) = 1-k-o,
    c = 4 + 2 P_d(x) - 2 P_d(x') - 2o.                 (1)

This includes width zero: k=0, o=1, c=2. The source's `counter_correct` and
`counter_running` justify the literal cost and first completion for every word;
the new argument uses the exact wrap correction instead of discarding it.

For N>0 calls with directions d_1,...,d_N and states x_0,...,x_N, let O be the
number of wraps and define the signed switch sum

    J = sum_{i=1}^{N-1} [P_{d_{i+1}}(x_i)-P_{d_i}(x_i)].

Terms with no reversal are zero. Summing (1), with matching indices, gives

    T = 4N + 2 P_{d_1}(x_0) - 2 P_{d_N}(x_N) + 2J - 2O.  (2)

An increment-to-decrement switch at a word with h ones contributes w-2h
to J; the reverse switch contributes 2h-w. Ignoring these signed terms is
not a valid telescope. For N=0, T=0 and the endpoint expression is unused.

## Uniform bounds, including wraparound

Suppose w>=1. Split a nonempty direction sequence into K maximal nonempty
constant-direction runs. Let H be the number of runs containing at least one
wrap. Thus K=1+(number of reversals), and 0<=H<=K. Then

    T <= 4N + 2(w-2)K + 2H <= 4N + 2(w-1)K.             (3)

Proof: on a run of length L, (1) telescopes without a switch term to
`4L+2P_start-2P_end-2O_run`.

* If the run has no wrap, its initial word cannot have all w bits equal to
  its direction (the first call would wrap), so P_start<=w-1. Its last call
  resolves a carry and leaves at least one bit equal to that direction, so
  P_end>=1. Its cost is at most 4L+2(w-2).
* If it has a wrap, P_start<=w, P_end>=0, and O_run>=1. Its cost is at most
  4L+2(w-1).

Sum these run bounds. This proves (3) for every finite sequence, with no
assumption about intermediate values or wrap frequency. For w=1 the
nonwrapping run surcharge is negative; the same proof applies (a nonwrapping
run then has length one). For width zero the sharper exact statement is T=2N.
For the empty sequence use N=K=H=T=0.

With no wraps, (3) reduces to `T<=4N+2(w-2)K`. Even for a single direction,
this improves the existing valid `4N+2w` bound: the uniform bound is
`4N+2(w-1)` for N>0, and `4N+2(w-2)` when no wrap occurs.

## Sharp families and the precise negative finding

These coefficients are sharp as uniform per-run surcharges with leading
term 4N; no optimality for every prescribed (w,N,K,H) is asserted.

* Start at 2^w-1 and alternate increment, decrement, increment, ... .
  Every call wraps, costs 2w+2, and is its own run. Hence K=H=N and equality
  holds in both inequalities (3). Reducing the uniform surcharge 2(w-1)
  by any positive amount fails on this family.
* Start at 2^(w-1)-1 and alternate increment, decrement, ... . Every call
  crosses the middle edge, propagates w-1 bits, costs 2w and never wraps.
  Thus K=N, H=0, with equality in the first inequality (3). This also works
  for w=1. Reducing the nonwrapping surcharge 2(w-2) fails.

Seed 67 selects w=4 and N=7 for explicit receipts. The middle-edge family
costs 56 transitions and the wrapping family costs 70, whereas an invalid
application of the old fixed-direction bound gives only 4*7+2*4=36.
The stronger nonwrapping example shows that merely excluding wraps does not
restore an O(N+w) guarantee for arbitrary changes of direction.

In particular, as w and N grow, these families cost Theta(Nw). There can be
no uniform O(N+w) bound for arbitrary direction sequences of **this literal
primitive**, even with wraparound forbidden. This is not a lower bound for
other counter encodings or a counterexample to any selected multiplication
construction; no selected routing client is shown here to use these sequences.

## Interface consequences and limits

The safe primitive-call invoice is O(N+wK), or the exact (2) if states and
switches are known. A sufficient condition to retain O(N+w) is
`wK=O(N+w)`; it is not necessary, since signed switch terms may cancel.
The no-wrap condition alone is insufficient.

A composed tape routine must still add initialization, mode dispatch/restart,
payload processing, template copies, resets, and all other head movements.
A reset breaks the state sequence assumed in (2), so split at resets and
charge each reset and the new initial potential. No free restoration,
source access, helper, or recursive call is inferred from this bound.
This audit neither constructs a full routing controller nor discharges the
selected certificate's compiler, hosting, precision, tape, or analytic
assumptions. There is no new kappa and no proof-assistant verification of
this extension. The universal statement is the argument above; the finite
replay is supporting evidence with explicitly bounded coverage.
