# Reachable finite symbols in the pinned FinTM2 interface

This is a boundary lemma for the independent model review requested by PR2411.
It is not a defect in that proof and does not reprove multiplication. The
external theorem is pinned at `38ef57bb8155b1c3f3a607b7b8e4ae5d1addd117`;
its manifest pins Mathlib at `d13f23b723b8a846827a245b89c10fc7d3f11612`.

## The actual premise

Mathlib's `FinTM2` has finite stack indices K, labels Lambda, control states
sigma, and input alphabet Gamma(k0). It does **not** require every declared
Gamma(k) to be finite. The comment above `Gamma(k0)` should not be interpreted
as an all-stack premise. This creates a small model-interpretation obligation,
not an unbounded computation oracle: the only constructor that creates a
stack symbol is `push k f`, where f maps the finite control type to Gamma(k).

Fix complete finite lists L and V of labels and control states, and a finite
list I of tagged initial symbols `(k,x)`. For a statement q, let P(q) contain
every `(k,f(v))` for every push substatement in q and every v in V. Include
both sides of every branch, whether or not a particular input executes them.
Let

    A = I ++ concat_{l in L} P(M(l)).

A is a finite list depending only on the machine and initial alphabet, never
on the input length, values, or running time. Duplicates are harmless.

## All-prefix invariant

If every initial stack symbol belongs to I, every symbol in every stack at
every defined execution prefix belongs to A. In particular, actual
`initList` puts symbols from the finite Gamma(k0) on the input stack and
leaves all other stacks empty, so one fixed A covers **all** inputs.

The Lean theorem `input_prefixes_allowed` states this for arbitrary dependent
stack alphabets, arbitrary callbacks of the pinned statement types, complete
label/control enumerations, arbitrary input words, and every natural prefix
length. `all_prefixes_allowed` also permits arbitrary initially dirty stacks
whose symbols are covered by I. It does not silently assume such coverage.

Proof: a push inserts a value explicitly included in P(q); pop only removes;
peek and load change only the finite control; a branch selects a covered
substatement; goto and halt change only the label. Induction on statements
gives `stepAux_allowed`; induction on execution length gives the prefix
theorems. No finite test is used in either induction.

## From symbols to fixed-cost primitives

Each callback is now restricted to a finite domain: push/load/branch/goto
read a finite state; peek/pop read that state and a reachable stack head or
the empty marker. Thus each can be represented by a fixed finite table.
Even when declared symbols have an infinite type, they can be renamed by
indices in A. A callback's cost as an arbitrary host-language function is
not charged as a unit operation by this argument: its **finite table** is
what a finite machine implements. This is an existence argument; no
effective compiler from arbitrary noncomputable Lean functions is claimed.

Define D(q) as one plus the continuation depth, with max over the two
branches, and D(goto)=D(halt)=1. The separately defined `work` follows the
actual stack/state semantics and counts each executed constructor.
`work_le_depth` proves work(q,v,S) <= D(q) for arbitrary stacks. The theorem
`work_le_programBound` bounds it by the maximum over the fixed finite label
list. Therefore t macro steps require at most Dt primitive actions for
one fixed D. D need not be one; the 32-action control illustrates that error.

With one tape per stack, a head kept at its stack top, and a distinct empty
marker, push/pop/peek have constant tape cost. Fixed finite tables and the
fixed number of tapes add only another machine-dependent constant. This
last conventional multitape interpretation is the written argument here,
**not a Lean-verified tape compiler or a new machine simulation theorem**.
The Mathlib file also contains a different single-tape simulator that
shuttles to stack ends; its runtime must not be substituted for this claim.

## Source and kernel boundary

`Extracted.lean` isolates the exact Stmt constructors, Cfg fields, dependent
update body, and stepAux/step equations of the pinned Mathlib source.
Section parameters and recursive type shorthand are made explicit, and
universes are specialized to Type, as in FinTM2. `verify.py` checks those
transformations and all source hashes. The kernel compiles the isolated
definitions plus `Closure.lean` against Lean/Std 4.34.1. It imports no Mathlib
oleans. Four transitive axiom reports contain only propext and Quot.sound.

Accordingly the kernel result is about the source-extracted definitions;
their correspondence to the actual Mathlib names is source-checked and
reviewed, not an elaborated equality inside a full Mathlib build. Applying
complete lists from FinTM2's Fintype instances and its initList is the
written source-interface instantiation. No build of the external completed
multiplier or its axiom audit is claimed. A direct imported-Mathlib bridge
is a useful next step, with the same hypotheses and source pin.

The generic Python hook checks extraction, source pins, exact finite models
and rejection controls. Only the dedicated `--kernel` workflow compiles Lean.

## Controls and interpretation

An independently written literal interpreter executes all seven constructors
on 1,533 cases: all binary input words of lengths zero through eight and
three possible control entries. Its noninput alphabet is natural-valued;
the fixed reachable list has seven tagged symbols. It checks 24,582 macro
prefixes and 116,778 primitive actions, complete data return and empty work.

Six controls reject incomplete state ranges, an omitted label, a dropped
branch, an unadmitted dirty initial symbol, unbounded control, and unit
macro-step pricing. The unbounded-control example creates 1,001 distinct
symbols with the same finite program shape. These are countermodels to
weakened hypotheses, not counterexamples to FinTM2. Seven reporting controls
reject missing/duplicate/wrong theorem reports, custom axioms, sorry, and
diagnostics. The universal claims are the kernel inductions and written
source correspondence; finite controls do not establish universality.

Credit Dan Brown and Kenny Daniel for the external multiplier and explicit
review request; Pim Spelier, Daan van Gent, Mario Carneiro and the Mathlib
contributors for the model and semantics. Source copyright/license notices
are retained. New proof and audit by ywz65 with substantial OpenAI Codex
assistance. No independent human review, selected-supplier admission, or
changed exponent is asserted.
