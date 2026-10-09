# Terminal dirty accumulators need not exist

Consider a deferred physical auxiliary role u that never controls an
auxiliary update and has a single ordinary output read with coefficient
α. Its initial dirty value is z_u. Its forward destination updates have
the form `u += a_j` (including one possible clean input injection), at
their actual original times t_j. Then its entire contribution is

`−α z_u + α(z_u + Σ_j a_j(t_j)) = Σ_j α a_j(t_j)`.

Delete u, its initial garbage readout, final readout, forward destination
updates and their inverse cleanup. At the exact original forward times,
execute the corresponding direct output updates. Every other auxiliary
role evolves identically, because u never controls one. There are no
snapshots, reordered source reads, or new copied streams. This is an
identity over Q, with arbitrary dirty auxiliary inputs, not merely over
F2 or on clean inputs.

For several such roles, deletion composes if none is a source of another
and each target's new update frames are nested. Here source-count zero
establishes the first property. The selected547 roles have distinct
targets; all complete incoming-frame sequences are nested.

## Physical schedule restrictions, all checked

The scalar identity alone is insufficient. Every selected role:

- is deferred and untouched by the retained-center phase;
- has no auxiliary source incidences, exactly one ordinary root, no
  center component in its adjoint, and adjoint column exactly α=±1/2;
- receives all updates after every center copy/scatter and the complete
  old garbage-readout phase;
- has every redirected source still in its original gate frame, at its
  original operation index;
- has every incoming frame containing the target's final old garbage
  frame and nested with all earlier redirected update frames.

The two selected input-start roles inject their clean input during the
original late-V phase at their original one-dimensional source frame.
The other545 roles begin with a copy. Nothing is moved into phase one.

The new word retains every original target-frame advance, even where its
associated garbage read was removed. Thus old target nesting is never
assumed to disappear for free. Redirected updates may require additional
advances between the final old readout frame and the final hyperplane;
these are explicitly emitted and charged. Each old source gate incidence
survives as a direct-output source read at the same node/frame, preserving
the complete frame chain of every retained auxiliary.

## Exact complete cost, not subtraction alone

For each removed role with initial readout dimension σ and frame chain
σ→…→h, its old internal-plus-exterior child mass is

`2v[(h−σ)+(h²−h+σ)] = 2v h²`.

Removing547 roles reduces W by2v·547. The added target-front subdivisions
have the same total rank as the old jump, so the complete rank deficit
is unchanged. But they do change the power moment, and are retained in
the certificate. An all-concave improvement follows from the exact packet
lemma below, not merely from W.

The constructed candidate has

```
h=24, v=2024
R: 38506 → 37959
W: 164065440 → 161851184
rank: 94499831360 → 93224419904
deficit = 1862080, unchanged
direct output updates = 1141
```

The exact target-front histogram difference (already replicated by2v)
is preserved in `terminal-elided-cyclic/word.json.gz`, including the
increased numbers of narrower children. For example, 141680 width-five
children disappear, while some width-one/two/three children are added.

No new coefficient exceeds the old coefficient bound: α=±21/42 uses the
same fixed odd divisor21 and dyadic normalization. Each removed role
loses two readouts, and each incoming update/inverse pair is replaced by
one fixed-coefficient output term. The existing scalar-group expansion
can therefore be retained conservatively; the producer also records the
reduced literal term count under that same expansion. Root/assembly
analysis must propagate any chosen bound rather than assume it is free.

## Exact all-concave packet lemma

Let M be the final old garbage-readout dimension of this target and F0
the first role-frame dimension. The candidate checks establish
`σ ≤ M ≤ F0 ≤ h−1`. All later role-chain jumps cancel, in the difference
of the old and new profiles, against the new output-front subdivisions.
After padding the smaller-width new construction by one dummy width-m
child per removed role, the remaining comparison is

```
old: [m−h+σ, 1, F0−σ, h−1−M]
new: [m, F0−M, 0, 0].
```

The masses agree. The new largest entry m exceeds every old entry, and
its first two entries already contain all the mass. Thus the new packet
strictly majorizes the old one and reduces every strictly concave power
sum. Distinct targets let these comparisons add without double-counting
target fronts. `verify_terminal_majorization.py` checks all547 packets
and exact equality with the full paid-profile difference. All576 global
integer hinges are nonpositive (minimum−5,966,752).

If the old power numerator is below W_old, subtracting these padded
dummy contributions gives the new numerator below W_new. Thus every old
strict moment certificate survives, with positive margin. Other assembly
constraints still require repricing; moment dominance alone is not a
claim that the final κ bottleneck cannot change.

## Reproducible evidence and current proof status

`inventory_deferred_roles.py` finds the source/destination candidates;
`inventory_terminal_schedule.py` verifies the exact adjoint and full
output-chain conditions. `eliminate_terminal_roles.py` exports the
literal stage-one event word, target frames, removed/retained role IDs,
selection, full profile and source closure. Two arbitrary-dirty modular
replays (prime2^61−1, fixed independent seeds) restore all remaining
scratch and add exactly the input vector to the outputs.

The algebraic rewrite and its frame restrictions are exact. Modular
replays are checks, not a proof over Q. The critic independently verified
the exact local all-input identity, original source chronology, forward
and reflected frame traces, and full profile:469,814 physical events.
Six actual mutant files were rejected, including a changed coefficient
and an omitted update. Receipt:
`../critic/terminal-cyclic-audit-cached/receipt.json`.

Independent complete arithmetic assembly gives
`κ=9.410004476791e−5`, a finite improvement over direct cyclic deferral,
but below the newer PR114 construction. The inherited all-size tape and
analytic interfaces remain dependencies; no unconditional theorem or
publication-level novelty claim is made.

```sh
python3 round15/workers/construction/inventory_deferred_roles.py --word round15/deferred-cyclic/word.json.gz --out round15/workers/construction/reproduced-role-inventory.json
python3 round15/workers/construction/eliminate_terminal_roles.py --word round15/deferred-cyclic/word.json.gz --profile round15/deferred-cyclic/complex-profile.json --inventory round15/workers/construction/reproduced-role-inventory.json --out round15/workers/construction/reproduced-terminal-elision
```

The broader pure-source identity is also sound with appropriate source
frames, but this word contains no eligible deferred no-target leaf
roles. This experiment is specifically terminal-accumulator elimination,
not a renamed pure-source shortcut.

## Transfer to the stronger compatible-deferral core

The same unchanged generator was applied once to `round15/salvaged-core`.
All conditions were re-established on the actual new word, not inferred
from the previous count. It eliminates556 roles with distinct targets,
using1,168 direct updates. The complete result is R=37,303,
W=159,195,696 and total rank91,694,858,816. Both dirty replays pass.

`terminal-elided-salvaged-core/` contains the exact event word and profile.
`terminal-majorization-salvaged-core.json` links the same packet lemma
to this complete profile and checks all576 hinges (minimum−6,225,824).
This establishes a basis-independent mechanism with a second exact
instance, not merely a smaller profile on the first isolated graph.
Independent full audit and assembly are performed separately by the other
workers. Later public frontier movements must be compared separately.

## Bounded zero-σ extension: no missed roles on these words

Deferral is not algebraically necessary. The identity and packet lemma
also permit an initial garbage read at σ=0, provided every redirected
incoming update remains after centers and all garbage reads, and its
frame contains the current target frame. A read-only inventory tested
exactly that broader criterion, without moving source snapshots or early
clean-input injections.

On the direct cyclic word, all4,196 nondeferred terminal roles are blocked:
70 have a phase-one destination update,369 an early clean-input injection,
and3,757 a target-frame obstruction. On the compatible-deferral core,
the corresponding1,872 roles split into92,369 and1,411. No additional
eligible role exists under this fixed-time criterion. These are classified
failures of the specified schedule, not a general impossibility of
zero-σ terminal elision. The exact role IDs and reason codes are retained
in `zero-sigma-*-inventory.json`, generated by
`inventory_zero_sigma_terminals.py`.

## Latest-basis composition (PR116 cube + refined placement)

After the public frontier moved again, the unchanged elision template
was applied to the coordinator's separately verified `refined-cube`
word. It finds1,179 eligible roles on1,179 distinct targets and performs
2,476 direct output updates. Both arbitrary-dirty replays pass. The
complete result is

```
R=34499, W=147845104, total_rank=85156917824,
deficit=1862080.
```

The full difference, including all new output-front subdivisions, matches
the same two-child packet formula. All576 integer hinges are nonpositive,
with minimum−12,929,312. Artifacts are
`terminal-elided-refined-cube/` and
`terminal-majorization-refined-cube.json`. The upstream frame/DAG/placement
composition and our terminal-elision increment must be credited and priced
separately. Exact final assembly and independent word audit are separate
worker outputs, not inferred from this larger role count.

## PR118 selected-word composition

The frontier moved again to a more heavily shared physical word. Applying
the same unchanged terminal-elision generator to `refined-replayed`
selects393 roles on393 distinct targets, including accumulators with up
to seven incoming destination updates. It executes1,221 direct output
updates. The exact final finite quantities are

```
R=28312, W=122800128, total_rank=70731011648,
deficit=1862080.
```

Here every selected role satisfies `σ=F0=M`. After fully charging the new
target-front subdivisions, each removal therefore deletes exactly2v
copies of three children

`[m−h+σ, 1, h−1−σ]`,

whose widths total m. The complete histogram difference has no positive
entries. The old local word loses3,228 literal terms (updates, inverses,
and two readouts per role) and gains1,221 fixed-coefficient output terms,
a net reduction of2,007 under the same scalar expansion. The fixed odd
divisor and coefficient-height bound do not change.

Both modular dirty replays pass, recorded in the event word. The profile's
inherited `replay.scope` only describes its base placement; it is not the
receipt for these new replays. `terminal-majorization-refined-replayed.json`
links all393 packets to the complete child profile; all576 hinges are
nonpositive, minimum−7,541,424. The candidate is in
`terminal-elided-refined-replayed/`. Independent audit and exact final
assembly are handled separately. No further frame/order search was used.
