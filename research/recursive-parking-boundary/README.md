# Recursive parking: a precise call-boundary contract

**Scoped written proof and source-bound finite audit; no new kappa.**

The retained tape package proves individual push/pop round trips and explicitly
leaves intervening children and scheduler composition open. This successor
supplies the finite controller for **one park/call/restore boundary**, including
active I/O movement and dispatch. For fixed `W >= 2`, role lengths `n_i`, total
logical volume `V = sum(n_i)`, and active role `a`, its exact wrapper charge is

```
5 V - n_a + 9 W - 2 transitions, excluding the child's execution.
```

For equal positive lengths `n_i = n`, the child receives exactly `n = V/W`
bits and the wrapper uses at most `14 V` transitions. This separates logical
volume from workspace and parked ancestor storage. It does not change a paid
supplier profile or discharge the complete fixed-tape multiplier.

There is also an all-length counterexample to a weaker contract: preserving
all parked bytes **and the parking head at return** does not bound a child's
time uniformly in ancestor length. A fixed finite controller can scan the
entire ancestor and return unchanged. Restoration, trace locality, and a
uniform child-time bound are separate obligations. This is not a defect in the
upstream manuscript: it explicitly forbids ancestor scans.

## Model and boundary hypotheses

Use `W+3` bidirectional tapes: `W` roles, child I/O, parking, and one temporary.
The alphabet is exactly blank, separator, zero, one. One transition reads the
current symbols, writes at most one symbol per tape, and moves each head by
at most one cell. `W` and the active role are fixed when compiling the
controller; neither is an input-dependent tape allocation.

A **marked stream** of length `n >= 0` has separator at position -1, its `n`
arbitrary bits at positions 0 through `n-1`, blank everywhere else, and head 0.
A **marked empty** tape has just that separator and head 0. It is not literally
all blank. The parking interface at top `h` has separator at `h-1`, arbitrary
finite contents strictly to its left, blank at and to the right of `h`, and
head `h`. No length or absolute position is readable by a transition.

At wrapper entry, all roles are marked streams; I/O and temporary are marked
empty. Park all inactive roles in increasing index order, move the active
stream to I/O, call the child, move its result back, and pop the inactive roles
in decreasing index order. At child entry every role and the temporary are
marked empty, I/O contains exactly the original active stream, and the parking
top is

```
h_child = h + sum(i != a)(n_i + 1).
```

The **semantic child contract** is: starting at that interface, return the
specified length-preserving function `F` of the I/O bits, with I/O head 0 and
marker intact; return every reused role and temporary marked empty; restore
the entire parking tape and its exact head `h_child`. The specified `F` must
not depend on the parked ancestor. Other child tapes or a descriptor stack,
if supplied, need their own restoration and cost contracts.

For the **whole nested trace** to avoid ancestors, additionally require that
the child visits no parking cell below `h_child-1` and writes no cell below
`h_child`. For a running-time conclusion additionally supply a child-time
bound uniform over the permitted ancestor contents and top position.
Locality alone does not imply a running-time bound: a child can also waste
arbitrary time without moving its parking head.

## All-length proof

The proof below is an induction on stream length and on the fixed phase list,
not an inference from the finite test range. [machine.py](machine.py) gives the
literal rules and [verify.py](verify.py) binds the inherited rules to source.

### Three primitive facts

1. **Push.** After `i` copy steps, the source head is `i`, its first `i` bits
   are erased, and those bits occupy parking cells `[h,h+i)` in original order.
   The next source bit advances both heads by one. At the first blank, write a
   separator at `h+n`, advance parking to `h+n+1`, and start rewinding the erased
   source. Its `n` blanks and left separator take `n+1` further transitions to
   restore head 0. Total: `(n+1)+(n+1)=2n+2`. Parking never visits below `h`.

2. **Pop.** From that parked record, two entry steps move onto and erase its
   right separator. Transfer its `n` bits right-to-left into the temporary;
   they appear there reversed. On reading the old separator at `h-1`, leave it
   intact, return parking to `h`, and move temporary left. Reading temporary
   right-to-left now writes the original bit order to the empty output,
   erasing temporary as it goes. Its left separator returns its head to zero
   and starts output rewind. Rewinding the output stops at its own separator
   and returns head zero. The three loops each take `n+1` transitions, so the
   total is `3n+5`. Parking stays in `[h-1,h+n+1]` and only writes `[h,h+n]`.
   The original parking frame and marked-empty temporary are restored.

   These are the actual `TapeStackPush.instruction` and
   `TapeStack.instruction` tables, not list append/reverse primitives. Their
   existing Lean proofs retain credit. The bounds are also exact first-done
   times on these interfaces: the copy and rewind phases cannot finish before
   seeing their delimiters. Empty streams give two and five steps respectively.

3. **Move.** On a source bit and destination blank, erase/copy and advance
   both heads. At the first source/destination blank pair, move both left.
   Rewind over source blanks and destination bits together; at the pair of
   left separators, move both right and finish. This leaves the source marked
   empty and destination equal to its old source, both heads at zero, in
   `2n+2` steps. Both heads stay at or to the right of -1. The loop invariants
   are the same copied/erased prefix invariant as push, with simultaneous
   rewind. A malformed interface has a rejecting branch.

The inherited Lean proofs establish the endpoint identities at the stated
iteration counts for facts 1 and 2, at every length. They do not separately
formalize first-done minimality or intermediate trace bounds. Those additional
claims use the phase and position arguments above. We have not rerun the
inherited Lean kernel. Fact 3 and the composition below are also written proofs
and executable controllers, not new Lean theorems.

### Composition and cost

Let `i_1,...,i_(W-1)` list the inactive roles. Induction on `j` shows that after
their first `j` pushes, precisely those roles are empty, their records are
stacked above the entry delimiter in that order, and all unpushed roles are
unchanged. Move preserves the active bits and empties the last role. Thus all
semantic child preconditions hold. Applying the child contract supplies its
output and exactly the interfaces needed by the reverse move and the pops.
Induction backwards through the parked records restores every inactive role
to its own original contents and head. The final active role holds `F(x_a)`;
I/O and temporary are empty and the parking frame is exactly its entry frame.
The bits of all roles were arbitrary throughout.

For locality, each push starts at a top at least `h`, and the last pop stops
at the original delimiter `h-1`. Every intervening top is farther right.
Consequently the wrapper never visits below `h-1` or writes below `h`.
Applying the child's stronger locality contract gives the same conclusion
for the complete trace, and permits induction over any finite nesting depth.
No equality of role lengths is used in the restoration or locality proofs.

`boundary_program(W,a)` is the explicit compile-time phase list. Its state is
a phase index and the current primitive state; tape selectors in each phase
are fixed constants. Each primitive's done state makes one stationary dispatch
transition to the next phase, and the child's done state makes one such return
transition. There are `2W+1` phases including the child. The inherited tables,
the move table, and these fixed dispatch edges therefore specialize to one
finite controller with no length tests, seek operations, or data-dependent
tape selectors. A child subroutine is composed through its entry/done states;
its own execution is accounted separately.

Adding the costs gives

```
sum(i != a)(5 n_i + 7) + 2(2 n_a + 2) + (2 W + 1)
  = 5 V - n_a + 9 W - 2.
```

For equal `n>=1`, this is `(5W-1)n+9W-2 <= (14W-3)n <= 14V`.
For `n=0` the exact cost is `9W-2`; a bound by `14V=0` is deliberately **not**
claimed. A fixed list of `s` child calls can join final dispatches directly
to the next boundary, giving at most `14sV` wrapper steps for positive equal
roles, plus the child costs and the separately priced parent operations.

Marked interfaces are explicit preconditions. If a surrounding routine must
install and later remove all `W+2` work-tape markers, the inherited two-step
install/remove operations add `4(W+2)` steps, once per such lifecycle. The
existing parking delimiter belongs to the caller. The `14V` formula does not
silently include marker installation, descriptors, or row routing.

### What this gives to a recurrence

Assume separately that row splitting supplies equal complete role streams,
every child preserves length, the finite call plan has `s` children of width
`e/m`, and all remaining node work has a uniform `cV` bound. Then

```
T(V,e) <= s T(V/W,e/m) + (14s+c)V.
```

Dividing by logical `V` yields the `s/W` coefficient in the upstream normalized
recurrence. Temporary or parked storage is not substituted for `V`. An unequal
pair of role lengths `(1,2)` with active role zero instead sends one bit to its
child, whereas `V/W=3/2`: stack restoration alone cannot establish equal-volume
normalization. This corroborates, and does not replace, the manuscript's
complete-row hypothesis.

## Endpoint-only counterexample and controls

For `W=2`, two one-bit roles and active role zero, the wrapper costs 25 steps.
Give parking `L` contiguous ancestor bits below its original delimiter. Once
the inactive bit is parked, one fixed four-state child does this: step left,
scan left through nonblanks until a blank, scan right through nonblanks until
the blank at its entry top, and finish. It neither writes nor changes I/O.

This child restores every bit, head, and work interface, yet takes exactly
`2L+9` transitions. Thus endpoint restoration alone cannot imply a uniform
bound depending only on the child's one-bit volume. The finite witnesses
`L=0,7,63` give 9,23,135 child steps and the same 25 wrapper steps. No selected
child is alleged to execute this scan.

The thirteen receipt controls cover both source-table corruptions, parked-byte
and head mutations, role/temporary cleanup, I/O length/head changes, an
unchecked head drift that actually breaks restoration, wrong role pop order,
omitted dispatch cost, unequal-volume normalization, and the endpoint-preserving
ancestor scan. Contract guards and trace observations are **test instrumentation**,
not unpaid tape-machine validation routines.

## Reproduction and finite coverage

From the repository root, standard-library Python 3.12:

```sh
python3 -B scripts/research_package.py --package research/recursive-parking-boundary --check-only
python3 -B scripts/research_package.py --package research/recursive-parking-boundary
```

Direct replay is `python3 -I -B research/recursive-parking-boundary/verify.py`.
Expected line:

```
PASS_RECURSIVE_PARKING_BOUNDARY: 396 source-table entries; 22308 equal-role boundaries; 4044 nested boundaries; 13 controls rejected
```

[RESULT.json](RESULT.json) is deterministic and compared in full. The receipt
records 12 push and 384 pop table rows checked against separate decision rules,
8,001 exhaustive primitive round trips (all payloads of lengths 0..6, all
ancestors of lengths 0..2 over four symbols, three translated stack origins),
22,308 equal-role boundaries, and 300 unequal-role cases. Equal-role domains
are all payloads and active roles for `(W,max n)=(2,5),(3,3),(4,2)`, with four
ancestor fixtures. Ninety nested fixtures exercise 4,044 inner boundaries on
the **same reused role, parking, I/O, and temporary tapes**, depths 0..4,
`W=2..4`, and ancestor lengths 0 or 257.

Nested fixtures deliberately use abstract Python row split/merge shims outside
the measured boundary. They test the assumed recursive interfaces and do not
implement or price physical row routing. Six additional test groups cover
longer move payloads, extractor grammar rejection, a semantic table-corruption
witness, repeated changing active roles through `W=8`, identical local traces
under ancestor replacement/translation, and the unbounded scan counterexample.

The extractor accepts only the literal syntax used by these two pinned tables;
it is not a Lean elaborator. Live input SHA256 pins are checked by direct replay;
the registered package checker also checks Git blobs and historical provenance.
Use `--write-result NEW_PATH` only for explicit regeneration; it refuses to
overwrite an existing file. Python timing and memory overhead are not machine
transition counts or integer-multiplication runtime measurements.

## Limits and attribution

The new result is the specified conditional boundary proof, explicit control
composition, independent table extraction/replay and boundary counterexample.
It is not a complete recursive scheduler, physical row/descriptor implementation,
selected call-plan binding, all-size supplier/compiler theorem, new Lean proof,
or a native/selected cold replay. Precision, tape layout of the mathematical
arrays, complete caller integration, analytic transfer, and independent human
review remain open. No selected certificate, frozen source, or supplier changes.

The source package by [rfu08](https://github.com/rfu08), in the PR64 transfer
lineage, already supplies and proves the push/pop machines; it was introduced
on main at `2d970ab3ca0271cfb2b609dc9aae1b7073b7774d`. The upstream manuscript's
fixed-tape schedule and the ranked-pair transfer review already explain the
intended linear overhead. Those results retain their credit; this does not
claim a new stack algorithm. [PR861](https://github.com/CrocSwap/integer-mult-bounds/pull/861)
is nearby counter-cost work and explicitly excludes recursive scheduling; no
code or theorem from that pending PR is imported.

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Selected PR1094
`0fc329d0bec93ca7cd288eaea1295172e8789810` is context only. There are no pending
PR dependencies. Exact Git-blob and SHA256 source pins are in
[SOURCES.json](SOURCES.json); assignment, scope, and coordination are recorded
in [TASK.json](TASK.json). New contributions use the repository's Apache-2.0
license; all predecessor files and notices remain unchanged.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

## Open next questions

1. **Formal boundary composition and trace frame rule.** This would connect
   the existing kernel-checked stack primitives to recursive handoffs. Start
   by formalizing the marked-stream move and the quantified intermediate head
   bounds, then induct over `boundary_program`. Blocker: the new composition
   and trace statements have not been implemented or compiled in Lean.
2. **One physical complete-row split/merge caller.** The boundary only earns
   `V/W` under equal complete rows. Start with a fixed `W=2` caller and explicit
   row payload width, retaining every spectator and counting counter/reset
   movement. Blocker: the current nested test uses abstract routing shims;
   descriptor and dispatch-stack integration need their own uniform cost proof.
