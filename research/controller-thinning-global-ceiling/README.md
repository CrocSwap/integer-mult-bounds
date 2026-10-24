# Arbitrary stage thinning cannot improve the retained p16 moment

**No new kappa.** With Cao Yifan's frozen PR4610 round-three local profile,
the retained paired-path moment has its best raw crossing in
**(0.0030217758, 0.0030217759)**, attained by the existing p16 controller.
The result covers every pair count, every prefix/suffix split and every
binary choice of full versus query-only stages, under the stated endpoint
contract. It is a written infinite-family reduction with an exact arithmetic
certificate, rather than an optimality inference from a finite search.

Read [PROOF.md](PROOF.md) for the hypotheses and proof. Three concavity
moves reduce every stage mask to eight canonical families. Their surplus
sequences are discretely concave, so exact adjacent differences certify
their maxima over all pair counts. A separate derivative and small-exponent
bound excludes every larger saving C<1. Changed words, idle topologies,
query alphabets and local profiles remain open.

An optimistic corollary removes all eight owned-centre charges and reoptimizes
the whole family. Its best raw crossing is only
**(0.0080596238, 0.0080596239)**, at p5. Thus even free centres cannot reach
C=0.01 through this path. Free centres are a hypothetical relaxation;
this does not supply a construction at that larger value.

The source binding checks the literal path's rational projector identities and
all 12,744 full/thin stage subsets, for every split through p5. This bounded
operator check supports the invoice binding; the proof supplies the infinite
claim. It does not prove native or absolute-phase admission for unexecuted words.

Source commits, Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json)
and [FROZEN-SOURCE.json](FROZEN-SOURCE.json). The PR4610 arithmetic is retained
byte for byte, including its original line endings. We use its local profile
as the theorem's fixed input, without adopting every claim in that artifact.

```sh
python3.12 -B scripts/research_package.py --package research/controller-thinning-global-ceiling
```

The registered replay requires Python 3.12 and the standard library only.
It verifies the committed [RESULT.json](RESULT.json), source/profile pins,
outward rational intervals and charge controls. A second replay rejects four
actual source/profile mutations, including an unpaid owned-centre profile
with its hashes maliciously rebound. `--write` regenerates the
receipt and is an authoring command, not the publication replay.

No selected record, BIT construction, compiler, production verifier or
canonical mathematical source is changed. This establishes no higher K,
unconditional multiplication theorem or independent human acceptance.

## Open next questions

Publication refresh found concurrent [PR4658](https://github.com/CrocSwap/integer-mult-bounds/pull/4658):
it certifies C<0.003022 for three pinned profiles through p64 using a max-plus
DP. This contribution instead proves the reduction for unbounded p, sharpens
the round-three bracket and adds the globally retuned free-centre corollary.
PR4658 was inspected at the description level; no independent replay is claimed.

The concurrent [typed quotient interface, PR4654](https://github.com/CrocSwap/integer-mult-bounds/pull/4654),
is outside this theorem. [PR4660](https://github.com/CrocSwap/integer-mult-bounds/pull/4660)
reports that extracting its B pairs and keeping an A-only path fails for all p
and C. Its remaining constructive target is a controller that keeps both types
active, or a changed centre/phase schedule. These are provisional source claims,
not newly replayed native constructions in this package.

Find a profitable change outside the retained path: a different scalar word,
idle topology, nonbinary replacement or native query interface. First emit its
complete endpoint contract and paid/target moment. An optimistic moment gain
is a reason for native replay, not supplier admission.

Credit Cao Yifan (PR4610), Cinna Davis and the cumulative PR4470/controller
lineage, zxv, Jacob Alan Sussman, and all retained source authors. Prepared
for Cinna Davis with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. See PROOF.md for precise scope and predecessor credit.
