# Alternate complete pivot for P104 type (4,4)

**Scoped independent audit; no new rigidity floor or κ.** PR1212's
type-(4,4) representative has an alternate live pivot with all 24
classes complete and all 14 blocks covered. Its original §10 check
chose a pivot that covered only 12 blocks and suggested every other
pivot had incomplete classes. The new verifier finds **24** complete,
14-block pivots, and supplies a fresh zero-exclusion certificate at
one of them. PR1212's original Lemmas 5–7 then prove rank-eight
gauge rigidity directly for that representative, and the independently
checked stabilizer action transports it to all 28 type-(4,4) units.

This is a second proof of a result **already established by PR1389**,
which kept PR1212's 12-block pivot and added a path-gluing lemma (6′).
Its incremental value is a route that needs only PR1212's original
Lemmas 5–7 and a two-family zero-exclusion certificate, a correction to
PR1212's pivot remark, an independent recomputation of the §10
stabilizer transport, and a written audit of the §8 cost bridge. See
[PROOF.md](PROOF.md) for the exact hypotheses and dependency on the
predecessor's written algebra.

The checker constructs all 120 E8 root lines, verifies 2,025 frames,
the 204 one/two-reflection stabilizer generators, P112 line
transitivity and the 28/336/896 second-frame orbit partition. At the
new pivot it checks the 24 complete Hadamard classes, 14 Steiner
blocks, 288 group witnesses and 1,952 ordered cross-class sign-rule
gluing checks. Its own positive-nonzero zero-pattern encoding yields
1,152 variables and 16,865 clauses; a 2,501-addition RUP proof derives
the empty clause.
The proof was found with Lingeling, but replay uses Python's standard
library only and checks every lemma by unit propagation. Mutation and
premise-omission controls are included.

## Reproduce

From the repository root:

```sh
python3.12 -I -B research/e8-rank8-transport-audit/verify.py
python3.12 scripts/research_package.py --package research/e8-rank8-transport-audit --check-only
python3.12 scripts/research_package.py --package research/e8-rank8-transport-audit
```

The verifier takes about five seconds here, is read-only by default,
compares the complete `RESULT.json`, and works under `-O`. PR1212's
`PROOF.md` (head `57099cb5`, byte-identical on main) and the retained
PR968 proof are pinned by SHA-256 and Git blob; the selected record and
task catalogue are provenance pins. Research base main `a18b4b01`,
rebased without input changes onto main `0b1cccf8`; selected record
#1094 is unchanged. No network is needed to replay.

The unit and pivot are bound to PR1212's published numbering: deleted
second frame `{2,3,16,17,46,47,52,53}`, PR1212's pivot
`{4,5,14,15,48,49,50,51}` (12 blocks), alternate pivot
`{12,13,22,23,30,31,36,37}` (14 blocks; also PR1212's published
type-(2,2,2,2) pivot). In review, PR1212's own `build_zero_cnf`
(two-term and diagonal families) was also run at the alternate pivot with
a SAT solver: unsatisfiable with `some zero`, satisfiable without it.
That cross-check used PR1212's code and is not part of this verifier.

## Open next questions

1. **Can this pivot shorten formalization of type-(4,4) rigidity?**
   It meets all four PR1212 finite hypotheses and uses the original
   complete-class and gluing lemmas. A first step is to formalize the
   finite zero-pattern implication from the shipped CNF/RUP proof and
   bind the four hypotheses to Lemmas 5–7. Those written lemmas and the
   finite RUP replay are not a proof-assistant artifact yet.
2. **Does the alternate pivot's refutation have a short readable core?**
   At this pivot the two-term and diagonal families alone exclude
   zeros, while at PR1212's pivot they do not. A human-readable reason
   would remove the solver certificate from the type-(4,4) proof. First
   step: compute a deletion-minimal unsatisfiable core of the shipped
   CNF and compare it with PR1212's 380-group P112 core. Blocker: no
   evidence yet that such a core is small.

This covers the #1212 §8/§10 steps that PR1670's audit of PR1560
explicitly left open; it does not re-audit PR1560 or PR1670.
@1337isnot1337's all-pivot census of one admissible P104 unit
([discussion 1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911752))
is a precedent for searching past PR1212's first pivot, on a different
orbit and with PR1389's three-row class lemma.

Credit Brett Halligan / @burntout76 and Ninefold for PR1212's E-graph
rigidity proof and four finite hypotheses; Josie Elliston's PR1389
for the already established type-(4,4) theorem; PR1497 for the
separate Lemmas 5–6 audit; @themilkman216 for PR968's eight-term
cost floor; and DreamingOfClouds for PR717's E8 decoder model.
Prepared for Josie Elliston by OpenAI Codex (offline session 17b of an
overnight donated run: audit, proof generation, code, controls and
writing), then reviewed, corrected and published by Claude (Anthropic;
session 19). Substantial AI assistance; Apache-2.0; no independent
human review is claimed.
