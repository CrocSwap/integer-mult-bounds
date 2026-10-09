# Completing the bank scheduling argument

Douglas Colkitt, with OpenAI Codex assistance; Apache-2.0. This is a
maintainer proof supplement to PR186, not a new exponent claim.

PR186's exact finite checks pass. Its coordinate-projector calculation proves
the endpoint of a bank after its assigned completed cores have run. Efficient
physical scheduling is a separate obligation: batching incomplete cores that
share storage would be invalid. The following construction uses the existing
bit-side GL cover and low-residue streaming interface. It does not apply to
an arbitrary orthogonal cover or justify concurrent live-core overlap.

## Relative operator of one entire physical chain

At a surviving entrance gauge S inside the local active space A, the bit
core has raw endpoint D_A D_S^{-1}. The retained nested split projectors
commute and P_S P_A=P_A P_S=P_S. The defining partial-swap identity therefore
gives D_A D_S^{-1}=D_(P_A-P_S), of rank h-dim(S). This holds on arbitrary
contents, including contents correlated with other roles. A compensated
recipient is internal to that same physical chain, not a second entrance.
All internal operations, inverse cleanup, and target/data connectors remain
in the checked physical word. The local scalar identity is needed for this
raw endpoint; a coordinate-projector identity alone would not establish it.

For the selected bit word these ranks are four (2,200 chains) and 24
(15,828 chains). The reversed completed core has the same endpoint because
this partial swap is an involution. Its internal work is still charged.

## Explicit routing and a conflict-free batch schedule

Use nine disjoint scalar replicas, as in the submitted inventory. In each
of the three private stages, partition the selected role instances into
groups of 18 and the undeferred ones into groups of three. Each group has
its own bank family, indexed by the complete GL_m(Z/q^w) cover. Data roles
remain separate. There are respectively 1,100 and 47,484 groups per stage.

For a group, let E_s be the actual split residual projector of its role s.
Choose fixed rational invertible H_s taking E_s to coordinate block P_s,
so H_s E_s H_s^{-1}=P_s. This is possible for any split idempotents of the
same rank: concatenate bases of their image and kernel. The P_s form the
stated 18-by-4 or 3-by-24 partition of the 72 coordinates.

Choose the H_s pairwise distinct within a group. Scalar multiples leave
their conjugation action unchanged, and finitely many choices are excluded
at each step, so distinct rational choices exist. Choose the fixed prime q
after these finitely many matrices: exclude their denominator/determinant
primes and primes making any H_s-H_t zero. This uses the retained freedom to
choose a sufficiently large fixed prime; it does not assume that *every*
q>2^80 works for these newly introduced routing matrices. The submitted Gram
witnesses continue to cover the physical operation frames. Any additional
finite exclusions change constants, not the rank histogram or saving.

Route role s of invocation g to bank g H_s^{-1}. For each s this is a
bijection of the full group. At bank b, that invocation is g=b H_s; its raw
operator is D_(b P_s b^{-1}). A common ancestor-dependent weighting conjugates
every one of these maps by the same chart, as required by the original
weighted bit interface. Thus their completed product is the full weighted
interchange on that bank. Every role visits every bank once.

For efficient execution, process one low residue class g_0 in GL_m(F_q)
at a time. Within that class, batch all high-matrix lifts, completing the
entire local word before processing the next low class. If two roles in
the same group used the same bank, then

    g H_s^{-1} = g' H_t^{-1}.

When g and g' have the same residue g_0, reduction modulo q implies
H_s = H_t modulo q, hence s=t. Then the original equality gives g=g'.
Different bank families are disjoint. Therefore no two live invocations
within a batch share an auxiliary bank, and no invocation aliases two of
its own ports. Across batches, all prior local cores have completed, so
arbitrary-content restoration permits sequential reuse.

There are a fixed number of low classes independent of w. Right
multiplication has exactly the affine high-matrix/carry implementation in
notes/three-stage-cover-bit.tex. Each invocation still runs once, and each
internal edge still runs on its original total fiber volume. Splitting by
low class changes neither that volume nor the number of children per edge.
The number of operation types and fixed tapes remains independent of w.
Routing and fixed chart descriptions contribute fixed constants to the
existing ordered-adapter toll. They do not become unpaid rank children.

## Accounting and limits

The total stock is 3(1100+47484)+2*9*1760=177432. Dividing by nine gives
W=59144/3. Only the 2,200 rank-60 exterior corrections disappear from the
normalized original ledger; the internal, data, center and fallback children
remain. Rank mass is 1,417,520 and deficit is 1,936. This is the inventory
already priced by PR186; the scheduling completion adds no numerical gain.

`bank_schedule.py` exhausts a small GL_2(Z/9) model with 3,888 invocation
vertices, 48 low classes, 81 high lifts per class, and two residual blocks.
It checks within-class disjointness, every role/bank visit and every endpoint
basis column. This diagnostic supports the scheduling argument; it does not
instantiate the 72-dimensional production word or prove a full tape machine.

The all-size weighted compiler, ordered streaming, complete spectators,
borrowed rows, recovery and analytic multiplication transfer remain the
inherited conditional interfaces. The supplemental argument is mathematical
review, not a newly kernel-checked Lean theorem.
