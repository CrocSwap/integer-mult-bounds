# All-cap formal tariff for repeated A2 st targets

This answers the repeated `st` part of [PR6817](https://github.com/CrocSwap/integer-mult-bounds/pull/6817)'s
nondivisible-target question. It applies **established separate-letter cuts**
to that source's common concave rank price; no new cut principle is claimed.

Let K be any field, d>=1, b>=1, and r>=d any finite number of arbitrary-input
scalar roles. The only paid address generators are the simple involutions s,t
of S3. A paid factor is `I+([u]-[e])A`, u in {s,t}, with arbitrary scalar A
of positive rank at most b. A may be singular or nonidempotent. Interleaved
scalar GL_r(K) maps are free. The complete endpoint in M_r(K[S3]) is
`diag([st],...,[st],[e],...,[e])`, with d productive roles and every spectator
restored, including all off-diagonal group coefficients.

For a common nonnegative, nondecreasing, discretely concave price f on
0..b with f(0)=0, the exact tariff is

```
2 * (floor(d/b) * f(b) + f(d mod b)).
```

The selective regular-representation cuts `{e,t}` and `{e,s}` give separate
rank-volume demands d. Applying the credited integer-packing lemma to each
letter gives the lower price; disjoint coordinate blocks of size at most b
give a matching full formal word. [PROOF.md](PROOF.md) states the argument
over every field, including characteristic two, with arbitrary restored dirty
workspace. [RESULT.json](RESULT.json) retains the completed finite
corroboration. The universal statement is a written proof,
separate from finite execution, human review and proof-kernel acceptance.

The source's three-target/cap-two result and divisible cases are credited
positive cases. The new scope is all d and b, including every nondivisible
remainder for this specific two-letter target. Other multi-reflection or
heterogeneous targets are outside this result.

## Evidence and reproduction

The new standard-library verifier authenticates the four retained source
prose files before calculating. It checks the selective cut ranks with
arbitrary scalar couplings over finite fields, complete signed attaining
endpoints with dirty-role mixing, formal prices and meaningful semantic
controls. It imports and runs no predecessor scientific checker, word,
constructor, census or native program. The retained result covers all 722 scalar 2-by-2 matrices over F2/F3/F5
(668 nonprojectors), 2,888 one-gate cut checks, 108 complete formal endpoints
with 378 paid calls (297 mixing dirty roles), 144 exact price cases and seven
controls. Arbitrary-coupling exhaustion is a one-gate cut test, not all-word
optimality. Nonconcave/nonmonotone controls refute the packing lemma outside
its premises; they are not completed legal-word counterexamples. The first
run took 0.161 seconds / 21.65625 MiB; normal and optimized replays give the
same 49,624-byte packet. The written proof supplies the universal statement.

```sh
python3.12 -B scripts/research_package.py --package research/a2-st-all-cap-tariff
python3.12 -B scripts/check_research_commit.py --package research/a2-st-all-cap-tariff
```

SOURCES.json binds four canonical-main provenance files. SOURCE-PINS.json
records the exact foreign PR6817 head/path/blob/mode/hash associations and
authenticates the byte-identical retained prose. That foreign association was
checked during source acquisition; it is separate from the generic canonical
Git ancestry check. Caching an open PR's commit does not make it publication
history. Direct replay authenticates retained bytes, has no external live file
or network dependency, and does not claim foreign ancestry. Registered normal
and optimized commands compare the entire typed result. No new dependencies
are required.

## Open next questions

Can one actual rank-capped native call be implemented with a complete price?
Start with its native/address layout, arbitrary input and owned/restored fields,
coupling-rank interpretation, movement and precision before assigning a new
construction round. No such realization or map from scalar coupling rank to
recursive child rank is supplied here. Free scalar GL maps are a formal-model
assumption, not a physical cost waiver. Ownership, restoration, routing,
all-size compilation, stock, precision, outer bounds and the complete supplier
invoice remain open; all five selected assumptions and the frontier are unchanged.

## Credit and scope

Prepared for [ToikY](https://github.com/ToikY) with substantial source-aware
OpenAI Codex proposal, source/overlap, proof/implementation and related-role
review assistance. The provisional cut recipe arose during orientation before
the claim; expanded review then identified and credited its prior method.
Roles saw the sources and proposal; this is not blind independent acceptance.

Credit Adam Gall #1941's separate cuts; Ross Richardson #1966/#1989's odd
dihedral, separate-letter and symmetric cut work; Benny Zhao / zhaobenny
#6817's model, concave packing lemma and three-target tariff; David Arias
#2738's Coxeter framework; Nick Petalas #5083's distinct longest-element
schedule; own excluded #6550's rank-two shortest-word classification; and
their retained Adam Gall, Ross Richardson, ywz65, eumemic, Ali Romman and
Gareth Davidson lineage. Those theorems, classifications and old finite
replays are not claimed again. Rank subadditivity, regular representations,
concave concentration and block batching are classical. Source notices are
retained verbatim; new work is Apache-2.0. The `bit-new-register-model` card
is explicitly changed to this partial formal tariff application; its native
conversion and complete-supplier acceptance gate remain unmet.
