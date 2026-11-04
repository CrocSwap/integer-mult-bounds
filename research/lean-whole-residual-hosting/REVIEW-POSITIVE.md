# Independent review of the positive whole-hosting proof

Prepared with OpenAI Codex assistance. This review made no changes to
`CoordinateSwap.lean`, `Hosting.lean`, `PhysicalHosting.lean`, or
`PinnedWindow.lean`. The reviewer authored the supporting `BoundaryExamples`
and `PhysicalExample` modules, so those files are not independently authored
evidence.

## Verdict

No mathematical error, inconsistent hypothesis, or vacuity was found in the
new conditional bit window-absorption theorem. Fresh trust-zero compilation
passed for all five modules at the hashes below. The result is appropriately
described as an operator lemma under explicit complete-endpoint, ownership,
and common-chart contracts. It does not prove that the repository's physical
provider satisfies those contracts.

The initial formulation had a material application ambiguity: retaining an
old bank in `R` would require its output to agree after its residual had been
relocated away. The new `PhysicalHosting` projection adapter resolves that
issue by allowing different auxiliary layouts and comparing only the common
retained state. This is an actual clarification of the interface, not a
claim that old and new bank outputs are equal.

## Mathematical checks

`CoordinateSwap.lean:35-41` defines the bit residual as a coordinate swap
within one complete stream. Coordinate and payload types are arbitrary;
the argument does not depend on binary address values, zero scratch, or
separable arrays. The commutation theorem allows overlapping masks, while
union-based composition and child completion correctly require disjointness
and containment (`:58-71`, `:85-112`, `:134-150`). The overlap/containment
requirements are witnessed by explicit counterexamples in `BoundaryExamples`.

`Hosting.lean:29-43` makes each *complete retained endpoint* a product of a
coordinate action on the host and an arbitrary map of all other retained
state. This is sufficient to prove the full-state commutation required by
`:74-87`. It correctly avoids the weaker and false inference that preserving
the host component alone implies commutation. The residuals are delayed
through arbitrary finite event lists and then completed with the exact
remainder. There is no bounded enumeration of possible programs hidden in
the theorem.

`R` is genuinely arbitrary. It may contain all other physical streams,
retained scratch, and bookkeeping. Its transformation `other : R → R` need
not be linear, invertible, or clean. Universality over the complete state
allows correlated inputs; the context theorem permits arbitrary prefixes
and observations of the retained state. That generality is logically sound
because the required product endpoint is quantified over every state.

## Physical-layout projection adapter

The new module has the needed quantifier order and chronology:

- `PhysicalHosting.lean:21-25` permits original layout `S × B` and relocated
  layout `S × C`, where `S` is the common retained state. Both retained
  endpoint contracts hold for **every** `s` and auxiliary input. There is no
  initialization assumption or requirement that the old and new banks match.
- `:36-48` passes each actual complete output, including its changed bank,
  into the next invocation. Banks are not silently reset between calls.
- `:50-76` proves the two retained projection invariants by induction on
  these actual executions. Each induction step uses the universal contract
  at the predecessor's real output bank.
- `:80-89` applies window absorption to those retained projections.
  `:94-107` permits differently correlated original/relocated inputs and any
  observation of retained outputs, provided the retained inputs agree.

The contracts constrain no auxiliary output. Those outputs may depend on
the retained state and previous auxiliary state. The theorem therefore
proves no equality, restoration, erasure, space bound, or future-use safety
for excluded banks. The header at `:13-17` says this explicitly. Every
component whose output or restoration is claimed must be retained or
covered by an additional contract. This resolves the earlier concern without
introducing a restored-work claim.

The auxiliary type is fixed within each original/relocated window; the two
types may differ from each other. A provider whose internal representation
changes must first supply an appropriate whole-window state type or a
representation theorem. This is a modest expressiveness boundary, not a
logical defect.

## Nonvacuity and fresh checks

All five package modules were copied into a fresh temporary directory and
compiled with the official installed Lean 4.33.0 executable, `-t 0`, with
inherited extra Lean paths removed. The dependency directory was the only
extra import path. All 37 printed theorem axiom reports contained either
no axioms or only `propext` and/or `Quot.sound`.

A separate temporary review probe instantiated the physical interface with
nonempty retained state
`Stream Unit Bool Bool × Int`, old bank type `Int`, and new bank type `Bool`.
The first event has a nonempty hosted residual; the second has an intervening
idle factor and no hosted residual. Both increment the retained integer.
The original bank update is `bank + retainedInteger`; the relocated bank
update is Boolean negation. The endpoint projection proofs are reflexive,
so these contracts have concrete inhabitants without additional assumptions.

Lean checked the absorption instance for **arbitrary** old and new bank
inputs. It also checked the explicit two-step bank outputs:

```text
original bank output  = (bank + retainedInteger) + (retainedInteger + 1)
relocated bank output = !(!bank)
```

These equations demonstrate that the real auxiliary outputs are threaded
through the sequence while remaining outside the equality conclusion. The
two threading theorems use no axioms; the instantiated absorption theorem
uses only `propext` and `Quot.sound`. The temporary probe was removed after
compilation. At the implementing agent's request, the same example was then
retained as the 57-line `PhysicalExample.lean`, explicitly labeled as a toy
validation rather than a repository source provider. A further fresh
trust-zero compilation of its dependency chain and all three named theorems
passed with those same axiom sets.

## Source fidelity and remaining boundaries

The result matches the algebraic content of PR442's written hosting step:
move complete, wholly owned residuals through an admissible window and
absorb them into the pending child's exact remainder. The implementation
strengthens the wording "nothing touches the family" to the actual condition
needed: other endpoints are independent of the host, while host-local idle
factors commute in the same coordinate chart.

The selected `PinnedWindow` proves a concrete finite-mask coverage identity
for the stated source intervals, universally over stream contents. It does
not establish the physical chart, owner injection, full intervening schedule,
or the dirty-invocation endpoint. This review checked its Lean statements and
compilation; extraction and fresh-template matching are separate audit work.

The remaining source obligations are meaningful: deriving universal
projected dirty endpoints from the actual word; proving owner injections
and absence of aliasing; realizing a common chart and its conjugacy with the
physical factors; preserving cover-sweep chronology; implementing the
remainder child; and justifying any subsequent use of excluded auxiliary
state. No cost, larger κ, all-size compiler, or integer-multiplication claim
follows from this local theorem alone. The stated scope retains these limits.

## Exact reviewed snapshots

SHA-256 of files copied into the fresh build:

```text
CoordinateSwap.lean   74d47e67dad5e8d548e69b008de19b65cfd138d3be71cf80d0b6c6990cf65841
Hosting.lean          102084fe6a003ab54e3b1eace36ccd9d872857eb4fc9b0770de3d6f7961af1f9
PhysicalHosting.lean  edd25772ad9c7cbae66a65bd9bc5cb00b98cf79e0e44913df4ff5f940525bc48
PinnedWindow.lean     0b9c4a29a8f2d94f1d76a0760bacf65398c848794580222dcc880177e8b9fb34
BoundaryExamples.lean 6af4e1fc731daef67186cbdc4ef88478cb652b517c4944c6e37cfcced560f3d3
PhysicalExample.lean  a1394afe490bb5cd8837495a2b859575795d9f197ef27e380402fed4ba7d93da
```

Compiler: official Lean 4.33.0, commit
`d8b18978322de05a8f3dba51ef03cf5461676c17`.
Later edits require their own fresh replay; this review records exactly the
snapshots examined and compiled.
