# Independent conditional review of the last-K CRT exception

Reviewed against canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`,
PR4100 retained source `337d04939571a637aeab54a0f58f54fde811663a`,
`research/unconditional-batched-crt/CRT.md` Sections 2--4, and PR4174
`5fec853f0c048871de3b8098d1e30d4ee19cda23` reservoir proof/allocator.
I did not read the primary candidate implementation before this verdict.

## Verdict and exact assumptions

The elementary tail construction is correct, conditional on (1) a Boolean
control independent of its target and the whole borrowed H-bit suffix;
(2) a uniform sequential evaluator with paid time E(p,ell), including its
required source-coordinate reconstruction; and (3) the stated paid ordinary
interchange at width one. No new source obstruction was found.

This is more than a finite endpoint check only when accompanied by the
following two-block schedule and quantified tariff. It does not certify the
source's complete E bound, ordinary interchange construction, all CRT branches,
or multiplication theorem.

## Coordinate convention and dependency transport

Count physical address positions from the front/MSB, 0,...,L-1.
After PR4174 placement the layout is U,T,Y,B, with |U|=|T|=|B|=H.
The final physical Y bit is t=L-H-1. Its local arithmetic index inside Y
is zero. Source CRT.md's j_i are *arithmetic* Y indices; convert by
physical(j)=L-H-1-j before applying this proof. No reversal is free.

This lemma applies to **any** target in Y. It does not classify the
source's exceptional set. In particular, arithmetic additions at index j
carry toward larger arithmetic indices, which are nearer Y's physical
front. The source's phrase "last K positions" must not be identified
with the physical-last K positions. A finite caller that runs all of its
targets through this legal elementary branch is not a production
classification of which targets require the exception.

Let S exchange a target position q in Y with t (S=identity when q=t).
For a placed address z define g(z)=f(S(z)). An input original target bit
has moved to t, so g omits t. A possible dependency on the old last Y bit
has moved to q, which precedes t. The exchange touches no suffix position,
so g still omits B. All its dependencies therefore lie in the preceding
prefix P. If f also omits U,T, this remains true after the exchange.

For q=t, skip both exchanges rather than invoke an equal-position primitive.
For multiple tail targets, restore S before the next target. Even if t is
another active target, the unchanged coordinate interpretation is thus
preserved. The CRT layer's controls omit every active target, so earlier
completed switches also leave pending controls invariant.

## Explicit sequential two-block schedule

For each complete prefix P, lexicographic source order is

    (P,0,B=0..2^H-1), (P,1,B=0..2^H-1).

Evaluate g(P) once, using arbitrary fixed values for omitted t,B. Save its
single Boolean result. There are exactly N=2^(L-H-1) such evaluations.
Each target slice has A=2^H R payload bits, including arbitrary dirty data.

On a fixed temporary tape, stream the first slice into a single A-bit
buffer. If g=0, rewind/copy it to owned output, then stream the second
slice there. If g=1, stream the second slice first, then rewind/copy the
buffer. Both cases preserve the order within a slice. Return to and erase
the same temporary interval after every prefix. The source head always
moves monotonically apart from its final return; the work and output
heads each make a fixed number of complete sweeps. No per-prefix tape is
allocated and no record addressing is needed.

Thus the middle stage has exact endpoint t XOR=g(P), keeps B and every
other coordinate, and costs O(V+N(E+L^2)), allowing ample polynomial
coordinate/counter work. Its one-block buffer is 2^H R bits. Owned output,
preserved borrowed input, evaluator scratch and fixed work roles consume
O(V+E+L^2) visited space. Clearing and head returns are included. Paid S
and inverse S add at most two O(V) width-one calls, with O(V) space each.

Conjugating gives S T_g S = T_f. Since f omits q, T_f is an involution,
so the inverse uses the same construction and restores every dirty address.

## Conditional amortization

For R>=1, H>=G=64(ell+ceil(log2(p+2))) and

    E <= C 2^(4ell) (p+2)^16,

we have

    N E / V = E/(2^(H+1)R)
             <= (C/(2R)) 2^(-60ell) (p+2)^(-48).

The L^2 term is similarly absorbed under the actual L=O(p) caller.
There is no bad-density premise: every prefix owns its complete suffix.
Evaluating per record would instead cost (V/R)E and would invalidate this
invoice. At most K tail targets therefore cost O(VK), using constants
independent of p,ell and control truth tables. E remains a separately
unverified hypothesis in this review.

PR4174 supplies the dependency-safe H suffix and coordinate descriptor;
its allocator alone does not prove the evaluator-time hypothesis. The
elementary branch does not require guard-good states or sparse-hole repair.

## Independent finite evidence

`independent_tail_check.py` uses explicit payload labels at every address,
then independently compares direct target flips to conjugation plus
adjacent two-block output. It covers every Boolean function of every
non-target Y bit for Y widths 1--4, suffix widths 1--2 and all targets.
All U,T,B coordinates are arbitrary dirty address coordinates.

Ordinary replay passed 2,164 function/layout cases, 1,209,888 complete
address columns, 168,040 prepared complete fibers and 556 already-last-Y
cases. Inverse composition returns all labels. Omitting control conjugation
is detected, with first witness L=5,H=1,Ywidth=2,q=2,table=1: output
position 2 contains label 6 instead of 2.

This Python checker uses host arrays and is a finite semantic oracle,
not an implementation of the fixed-tape machine or a timing proof.

## Credit and remaining obligations

Cinna Davis supplies the audited CRT tail idea and bound; Hiroki KUMAZAKI
supplies PR4174's constructive placement. Vlado Vojdanovski, Jose Manuel
and the retained compact/routing lineage retain their source credit.
This review was prepared by OpenAI Codex as a separate agent. It is not
independent human review or a formal-kernel proof. No new kappa is claimed.

Next: authenticate the actual complete control evaluator with its
reconstruction/erasure/head returns inside E; independently establish the
ordinary width-one callee contract; then compose this branch with the raw
compact macro, full repair and complete CRT tariff. The selected frontier
is unchanged.
