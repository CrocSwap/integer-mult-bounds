# Fixed-word frame search after PR952

This note concerns the actual PR952 word pinned by `SOURCES.json`. No gate
order, operand, source access, helper, COPY operation or restoration gate is
changed. The question is whether its shorter scalar program allows a lower
paid frame cost than the inherited PR589 frame assignment. The accepted
multiplication exponent and selected supplier are untouched.

## Search domain

The ambient vectors are the 111 supplied integer E8 root-line coordinates,
with spans and ranks over Q. A frame is the complete set of these live lines
in a subspace spanned by live lines. The domain is all such closed frames,
including frames absent from the word's original catalogue. Start and final
frames are frozen. A gate places every operand at its assigned frame, and
each register's successive frames must be nested. Targets remain at zero
before scatter. Each retained helper has its original frame at scatter, so
all nine COPY ranks remain seven.

One frame is assigned per serialized gate. A/B/C records each have one
source. The multi-source D records remain forced at frame zero by the
original preconditioner interface; D is not an unpriced resynthesis domain.

The gate operands and scalar semantics are frozen. For the negative search,
cleanup C is allowed any legal nested frame assignment, although H4 requires
the original literal cleanup at the full frame. This enlarges the search
class. A lower bound for this relaxation also holds when H4 is imposed.
The baseline is still checked against the original H1-H5 interface.

The search does not change COPY frames, register endpoints, gate order,
helper count, source labels, decoder, stage structure or hosting. It does
not exclude improvements that change any of these restrictions.

## Completeness of frame intervals and components

Propagate the span of the current operand frames forward. Every legal gate
frame contains that least frame. Propagate intersections of future allowed
operand frames backward from the frozen endpoints and scatter constraints.
Every legal gate frame is contained in that greatest frame. Induction on the
gate order proves both inclusions; intersection of closed frames is closed.

Every closed frame in an interval is enumerated by starting at its lower
bound and adjoining one live line from the upper bound, followed by closure.
Every target frame in that interval is reachable: adjoin a spanning subset
of its live lines. Thus this is not a scan restricted to the old catalogue.

Connect two free gates if they are consecutive uses of the same register,
with no fixed gate separating them. Each register's frame cost is a sum over
its successive uses, including its fixed start/end. Every term involving two
free choices joins those gates in the graph. Hence all variable nesting
constraints and costs lie within one connected component. Fixed boundaries
contribute constants. Summing independently minimal component costs therefore
minimizes the complete cost; multiplying component assignment counts is not
needed. The enumeration must still test nesting and actual scatter equality.

The source PR886 producer relaxes scatter equality in its cost replay. The
independent checker explicitly checks it. Its reported census distinguishes
this issue rather than assuming the producer implements the intended domain.
No improved construction is accepted solely from the producer's relaxation.

## Uniform comparison, not just one numerical endpoint

For a component alternative let `delta[d] = H[d] - G[d]`, where G is its
baseline histogram. Fixed register endpoints and fixed COPY ranks imply
`sum d*delta[d] = 0`. The checker confirms this identity for every alternative.
It also records the integer truncated sums

    Delta[k] = sum_d delta[d] * min(d,k),  k = 1,...,8.

Of the 934 strict component alternatives, **933** have all seven nonterminal
sums nonnegative, at least one positive, and terminal sum zero. Put `p=1-c`
and `s[d]=d^p-(d-1)^p`. For `0<c<1`, the successive slopes strictly decrease,
so every `s[k]-s[k+1]` is positive. The exact identity

    d^p = s[8]*d + sum_{k=1}^7 (s[k]-s[k+1])*min(d,k)

expresses every difference in paid moment as a positive combination of the
recorded Delta values (times `64^c`); the rank-mass term cancels. Each such
alternative is strictly worse throughout `0<c<1`.

The remaining alternative, in the component containing **A[1720]**, has

    delta = {1:+3, 2:-3, 3:+1},
    Delta[1..8] = [1,-1,0,0,0,0,0,0].

It **fails** the stronger truncated-sum test. We retain that failure explicitly.
Its paid difference is nevertheless

    3*64^c * (1 - 2*2^(-c) + 3^(-c)).

The parenthesized function g has `g(0)=0` and
`g'(c)=2*log(2)*2^(-c)-log(3)*3^(-c)>0` for `c>=0`, because
`log(4)>log(3)>0` and `2^(-c)>=3^(-c)>0`. It is therefore strictly positive
for every `c>0`. The checker admits **only this exact exceptional delta**;
an unclassified profile fails verification.

Thus every different component profile is strictly worse for every
`0<c<1`, while the 19 componentwise equal-profile alternatives tie for every c.
Component additivity proves that simultaneous changes cannot improve the
baseline anywhere in that interval. This is a uniform moment comparison,
not an inference from one rational evaluation. With the same nonnegative
call multiplier and fixed idle remainder, the complete supplier moments have
the same ordering. It excludes a larger bit saving from reframing this word
under that frozen accounting; it does not claim any new outer exponent.
The rational calculation at the PR589 endpoint is a separate numerical
cross-check, not a premise of the uniform argument.

## Complete cost and limits

For histogram H and bit saving c, the variable local moment numerator is

    sum_d H[d] * d * (64/d)^c.

H includes every register's climb and all nine copied ranks. No scalar gate,
copy or restoration is omitted from the fixed word. The 288 calls and frozen
idle remainder multiply/add the same terms for every candidate; they cannot
reverse a local moment comparison. This conditional comparison does not
claim that a changed physical frame layout can be hosted by the existing
owner map. Relaxing such constraints is safe for a negative result.

The inherited scalar program has 23,673 ADDs, including the literal cleanup,
439 arbitrary dirty helpers and nine copied totals. These are credited PR952
figures, not newly saved gates. The checked starting local paid histogram is
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`, of rank mass 5,129.
The global current construction is complex-bound. This package supplies no
new circuit, new hosted invoice, runtime measurement or kappa.

All-size compilation, common labels, mutable-source realization, hosting,
precision/tape and analytic assumptions remain inherited. Finite enumeration
and a written argument are not formal verification of the multiplication
theorem. See CERTIFICATE.json and README.md for the completed coverage and
exact comparison strength, rather than inferring a larger scope here.
