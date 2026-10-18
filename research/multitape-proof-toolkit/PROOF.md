# Sufficient statements and assembly

## Machine and cost model

Fix finite types `K`, `Gamma`, and `Q`. A transition observes only a control
state and the tuple of scanned symbols. Each successful transition changes
finite control, writes at most the old scanned cell on each tape, and moves
each head by at most one. Tape words and absolute head coordinates are
unbounded; they do not appear as unbounded registers in the transition table.
`Runs P n c d` means exactly `n` successful physical transitions. A halted
configuration has no successor; there is no padding by fictitious idle steps.

The relative-tape and absolute-coordinate models are connected by
`cell(i,x) = tape(i).nth(x-head(i))`. Writing and moving satisfy the exact cell
identity. A no-write action becomes rewriting the already scanned symbol in
the absolute table. Thus every actual relative run has an absolute run of
the identical length, and halting is equivalent. This realizes the same
transition semantics as the inspected upstream model, without claiming that
different input/output conventions are already adapted.

## Constructive finite TM2 compilation

For a fixed program `M`, the compiled control consists of a member of the finite
set of its syntax nodes, a three-phase tag, and its finite source register.
No list is put in control. A source push is one local write/move; pop and peek
use bounded local phases, including the empty-stack branch. Each source
statement of depth `d` takes at most `2*d` physical transitions. Consequently
`overhead(M) = 2*max_label depth(M(label))` bounds every source macrostep.

For dependent finite alphabets `Gamma(k)`, embed symbols in `Sigma k,Gamma(k)`.
Actual mapped stacks contain only their own tag. Push preserves the tag;
pop/peek use a partial tag decoder, and the mapped execution identities prove
that they see exactly the original source symbols. Flattening preserves syntax
depth and exact macrostep counts. Reading the real compiled tape and decoding
its tags recovers the original source list.

The compiler therefore provides the physical run itself, its explicit cost,
its actual halt, and encoded output for every actual halted source execution.
`SourceComputesInTime` describes such executions and an output predicate;
`compiled_computesInTime` constructs the corresponding physical contract.

## Dirty data, traces, and termination

For any actual `n`-step run, each tape's executed footprint is the finite set
of its old head positions, of cardinality at most `n`. All cells outside it
are unchanged. Two configurations with equal control/heads and equal data on
that footprint execute in lockstep for the same `n` steps, retaining matching
control/heads and observed cells. Their arbitrary outside dirt remains their
own, rather than being overwritten by a reference execution.

Halting may depend on a symbol first scanned at the terminal head. Accordingly,
the completed-computation theorem adds that terminal position to each observed
footprint. The resulting set has cardinality at most `n+1` and guarantees both
the same actual transition count and genuine halt for every matching dirty
alternative. This adds an observation hypothesis, not an extra uncharged
machine transition. The actual Lean and finite fixtures exercise this distinction.

The simpler unit-speed cone theorem also protects every cell at distance at
least `n` from its initial head: writing precedes moving, so the boundary cell
is never written during those `n` transitions. `IdleOn` is a stronger table
certificate for preserving an entire tape and its head at every prefix. It
does not assert that the transition table ignores that tape's scanned symbol.

## Fixed subroutine scheduling and invoices

For two fixed machines on the same physical bank, finite sum control reproduces
each component's successful steps. A true first halt performs one stationary,
non-writing handoff to the fixed second entry. The exact cost is `n+1+m`.

For `k+1` fixed stages with common finite source control, the scheduler has
control `Fin(k+1) x Q`. Every nonfinal halted stage makes one literal stationary
handoff; the final stage genuinely halts. Actual stage runs and literal
head/cell agreement at each boundary construct a completed scheduler run of
exactly `sum(stageTimes)+k` transitions. This is an implemented finite table,
not a free meta-level composition. If stage time is at most `A*volume+B`, its
total is at most `A*sum(volumes)+B*(k+1)+k`. Checked idle spectators remain
unchanged through every scheduler prefix.

`k`, the stage programs, finite types, and entry states are fixed before input
quantifiers. A variable-size recursive call stack or physical row router is
not smuggled into this finite-stage construction.

## Main universal assembly

Given a fixed finite heterogeneous TM2 program of depth at most `D`, an actual
`n`-macrostep execution from `c` to halted `d`:

1. Construct its real compiled run in at most `2*D*n` transitions.
2. Realize its input and exact encoded final stacks in absolute coordinates at
   identical physical cost and true halt.
3. Construct the actual completed observation footprint of at most `t+1`
   cells per tape and transfer the entire completed run to every matching
   dirty alternative.

`VerifiedPipeline.compile_completed_frame` proves this exact composition. The
concrete copy example instantiates the physical table, actual run, output,
idle spectator certificate, and completed frame universally over arbitrary
initial head positions and entire tape functions.

## Asymptotic scope

`fixed_overhead_isBigO` transfers any established real Big-O target under a
literal pointwise fixed-factor cost bound. `compiled_and_adapter_isBigO`
also includes separately bounded adapter work. A uniformly bounded syntax-depth
family has an explicit common overhead; this alone does not make an
input-dependent family into one fixed machine. No fast multiplication program,
new kappa, selected supplier admission, or whole recursive implementation is
deduced from the toolkit in isolation.

## Concrete boundary proof

The child-independent closed construction fixes 5 tapes, 4 symbols and 90 states
before choosing x,y,h,past. Its finite sum tags each primitive phase; a 6-stage
physical scheduler includes an initial halted stage and 5 real routines.
Actual stage costs are 0,2|y|+2,2|x|+2,2|x|+2,2|x|+2,3|y|+5; 5 stationary
handoffs yield6|x|+5|y|+18. Every boundary is literal equality of all tape cells
and integer heads. The final stage halts with no next transition. The generic
wrapper has an explicit actual child execution premise, but the bit-flip
instance discharges it using its concrete table, not an oracle.

The arbitrary ancestor function is used only below the old parking separator.
Direct actual-transition phase invariants bound parking, output and temporary
heads for EVERY execution prefix. Bit branches cannot cross preserved separator
cells. Induction decorates the real Runs proof with finite observed footprints;
the write-frame theorem and marker invariance preserve the entire old prefix.

Canonical normalization consumes the actual MSB input, skips its leading zero
bits, pushes remaining bits and charges EOF. This reverses order through actual
push operations. A six-value finite register tracks only seen-one and an optional
held bit; width and n are proof parameters, not machine registers. Source length+1
steps compile with overhead10. The pure fixedBits/trim proof establishes Nat.bits.
The theorem reads the actual output stack and preserves any old suffix; it makes
no assertion about an origin-anchored upstream output tape.
