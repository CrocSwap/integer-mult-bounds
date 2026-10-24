# Two-stage terminal cancellation fails for the actual physical codes

**Scoped all-width obstruction; no new κ or paid-decoder lower bound.**
For the two-distinct-stage physical code products in PR4933's actual negative
output banks 0 and 8, a fixed scalar/monomial postdecoder cannot recover the
old Gaussian jobs. The owner `(0,1)` block has a row with at least `4^(f-1)`
nonzero input coordinates at every positive digit-column width `f`.
Any exact word in the stated scalar alphabet therefore needs at least
`2(f-1)` ADDs. The selected conditional κ remains **0.00302015**.

PR4933's TERMINAL.md explicitly leaves products of distinct stage codes open;
its one-stage argument alone does not establish this result. PR5036 finds
PR4940's literal scalar-to-physical substitution gap, while leaving a changed
physical inverse-code thin shear open. This package tests the first actual
two-stage terminal products before expanding that repair. It does not reject
the changed thin shear's local cancellation or every possible continuation.

[PROOF.md](PROOF.md) gives the exact owner-path expansion and an explicit
marker-column identity that isolates intermediate owner 31. The scalar owner
coefficients are applied once at every width; no tensor power of a sum is
substituted. All four forward/inverse sign choices and the inverse
postdecoders are covered. The same-stage inverse product cancels in the
positive control.

## Reproduce

From the repository root, using Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/two-stage-coded-terminal
python3.12 -I -O -B research/two-stage-coded-terminal/verify.py
```

The read-only verifier checks source hashes, all 12,544 scalar polynomial
entries defining the inverse, signed normalizers and their absolute-phase
weight identities, all 112 owner paths in each of four sign cases, and an
independent row-based Q/K evaluation. It evaluates the isolated row through
width four, with 1,4,16,64 nonzero entries in each case. `RESULT.json` is the
exact deterministic receipt. `--write` is only an authoring option.

Canonical base: `4c0a359d88f22f05189d51f48387750b801a45d4`, priority revision 7.
The source, task-card and selected-record pins are in `SOURCES.json`.
The canonical investigation is [Discussion4930](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19140623).
The scope changes the historical rank-shape card to this current physical
consumer obligation; its historical balanced-inventory ceilings are not used.

## Consequence and remaining limits

This closes free postdecoding for two specified output banks under the fixed
native scalar-word contract. It does not give a minimum paid Gaussian charge,
a complete supplier invoice, a universal code-product classification, or an
obstruction to changed whole-controller boundaries or recursive job types.
Native correctness of the full source producer, all-column physical closure,
precision/rounding, ownership, compiler and outer hypotheses remain inherited
or unresolved. No full supplier, Lean, independent human review or theorem
verification is claimed by this local replay.

## Open next questions

1. Can the actual code be paired with an already-paid IDLE so that its
   conjugated inverse is executed within existing Gaussian work? Start with
   one explicit output/IDLE pair and an arbitrary-input identity, pricing each
   extra query. The support result does not exclude this paid resource.
2. Can a changed physical inverse-code thin shear yield a whole controller
   whose terminal codes cancel before output? Test every block and both
   boundaries; PR5036's scalar substitution does not supply that identity.
3. Is there a typed recursive job family accepting the coupled outputs without
   ordinary postdecoding? Prove one chronological child substitution and the
   next scalar/warp contact, with the full paid bill, before expanding it.

## Credit

Dillon/PR4933 supplies the actual signed monomial normalizers, complete coded
caller and one-stage terminal question. Dugongue/mdumitrean/PR4929 supplies
the center-free code. JoyboyBrian/PR5036 supplies the recent physical pair
counterexample and changed-thin handoff. Retain Cinna Davis/PR4694/4698 and
PR4440/4470, Cao Yifan/intqwq/PR4610, zxv, Jacob Alan Sussman, Ryanson Jonathan,
and the full native, Clifford, query, ownership, compiler and precision lineage.
Those source packages are unchanged. The new two-stage marker witness, proof
and standalone verifier are by Cinna Davis/1337isnot1337 with substantial
OpenAI Codex assistance; no subagents or independent human review. Apache-2.0.
