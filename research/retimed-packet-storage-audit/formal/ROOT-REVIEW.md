# Root review of the capped-power formal supplement

Accept the universal natural-number predicate theorem and its inspected
correspondence to the pinned #8042 source. The author and orchestrator each
compiled the same proof SHA256
`ee9ec96c4f92b2a45f6d2998db0383b43e4051b32131be09ff1c3a36d3b1bec2`
with Lean 4.36.0 and `LEAN_PATH` unset.

I read the complete Lean development, the exact extracted Python predicate,
the source correspondence and its AST checks. The cap lemma applies to every
natural exponent and positive accumulated value. The induction decreases the
remaining exponent by division by two, preserves the positive capped base
and accepted accumulator, and rejects any selected product above the ceiling.
Equality at the ceiling remains accepted. The exponent-zero case genuinely
requires the accepted accumulator hypothesis; the proof states that domain.

The source version uses the actual nonzero low-bit test and omits the final
square. Its equality with the convenient induction loop is proved for all
natural states. The final caller theorem includes the carrier short circuit,
and its negation gives the strict failed-parent relation used in STOPPING.md.
Thus the formal statement covers the actual predicate's Boolean chronology,
not just a mathematically similar uncapped power comparison.

All fifteen printed axiom reports contain only the declared standard Lean
axioms `propext`, `Quot.sound` and, where the standard bitwise theorem is used,
`Classical.choice`. No new axiom, sorry, admit, unsafe declaration, native_decide
or external proof oracle is present. The exact source wrapper also checks
the profile exponent and parameter forwarding, eight boundary cases and
cap/equality/initial-domain controls. Both frozen execution receipts are
included separately; the failed initial root command referenced a nonexistent
local extraction path, then the corrected documented path passed. It made
no mathematical or source change.

The publication wrapper restores the existing authenticated source archive
offline, discovers the actual resolved positive module, and invokes the same
source/kernel checker. It additionally fixes the reviewed proof hash. It
does not install Lean, download dependencies, or use Mathlib. Its single
fresh publication replay is recorded in `publication-evidence/`.

Kernel acceptance applies to the stated Lean propositions. The mapping from
Python integer operations to Lean naturals is inspected and hash/AST checked;
Python operational semantics are not formalized. Machine time, the 98-product
charge, counter encoding, scratch retirement, recursion geometry and the full
multiplier remain outside this kernel proof. The earlier source OuterStop.lean
has priority for its abstract volume inequalities, which are not reclaimed here.

This is a compatible follow-up to the same stopping-control proof chain in
#8091. No new kappa or complete foundational-premise removal is asserted.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
