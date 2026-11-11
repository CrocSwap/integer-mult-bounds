# Dimension-6 no-edge pools are not one coordinate class

**Result.** Not every complete no-edge pool of pattern dimension 4 and
joint-image dimension 6 is a coordinate permutation of one of the three
witnesses printed in #7139, Section 9. Two further pools, W and B, are
proved in [PROOF.md](PROOF.md). Both have pattern dimension 4, no matrix
unit, a complete pool of six projectors, and joint image of dimension 6.
Both have every covector of weight 1. A coordinate permutation preserves
support size and the sorted image and covector weights. Those triples
separate the three printed witnesses, pool W, and pool B from each other,
so the five explicit pools lie in five distinct orbits. **No new κ.** The
selected value remains `363005817/100000000000`.

This is a proof by counterexample. It is not a census of every
dimension-6 pool, and it does not replace the three printed witnesses
with a finished list of normal forms. The dimension bound of #7139 is
not reproved.

## Scope and evidence

Catalogue card: `bit-new-register-model`, priority revision 8, base commit
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status: **changed**. The
card asks for a new register alphabet. This package answers open question
2 of #7139: whether every dimension-6 pool is a coordinate permutation of
one of the three printed witnesses. The answer is no. The reason is
recorded in [TASK.json](TASK.json). The original native acceptance gate is
unmet, and the selected frontier is unchanged. Pattern dimension 5, and
the weight-1 image-dimension-4 question of #7138, are not taken.

[PROOF.md](PROOF.md) copies the three witness lists from #7139, Section 9
(the column-column list is also #7138, Section 6) and identifies pools W
and B at every width at or above their supports. The separation is the
invariant triple recorded in Section 2 of the proof. The five triples are
a comparison of five explicit pools, not an orbit census.

[verify.py](verify.py) rebuilds those lists, checks that each complete
pool equals the printed six projectors at the widths used in #7139
(including one spare coordinate), and checks pools W and B at widths
including a spare coordinate. It also enumerates the 16 patterns of each
4-dimensional space and checks that a coordinate swap moves pool W without
changing its invariant. These scans certify the explicit pools. They do
not enumerate all 4-dimensional pattern spaces. The case split in the
proof is what identifies W and B at every large width.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue is
provenance at the base commit, and the selected record is an input because
the verifier reads it. The witness coordinates are transcribed from
#7139 at fork head `007869ccdc22ee591b5a88d99a35f02511bffbee` and from
#7138 at fork head `5690b63f877654bca13e3d4777c081e7d538d7bc`. Those
commits are not ancestors of this branch, so they are not git pins; the
verifier rebuilds the transcribed lists and checks the pools. Full Git
history is needed to resolve the pins that are declared. Nothing here
reruns the selected baseline as a scientific replay.

Overlap was checked on 2026-11-11 against upstream main
`e54523517d0f03e58352e647c403a5af3e525a57`. Local
`scripts/find_overlap.py --offline` searched 10178 notes with a complete
inventory; the remote snapshot was unavailable in that run. A separate
GitHub search of open upstream PR titles and bodies found the dimension-6
pattern-dimension language only in #7139, #7138, and #7094. #7139 states
this classification as an open question and has no comments. #7138 proves
the weight-1 image bound and prints one dimension-6 witness; it does not
claim that witness is the only coordinate class. #7094 is the irreducible
dimension-5 witness. Discussion #1166 had no matching recent comment.
Closed-PR hits for the same words were other subjects, including #6962,
which attains irreducible dimension 4. No match is not a novelty
certificate.

## Reproduce

From the repository root, with Python 3.12 and the standard library only:

```sh
python3 -B research/dim6-no-edge-coordinate-class/verify.py
python3 -I -O -B research/dim6-no-edge-coordinate-class/verify.py
python3 -B scripts/research_package.py --package research/dim6-no-edge-coordinate-class --check-only
python3 -B scripts/research_package.py --package research/dim6-no-edge-coordinate-class
```

The verifier prints `PASS_DIM6_NO_EDGE_COORDINATE_CLASS`.

## Open next questions

1. **Column-column orbits.** Which pairs of 2-dimensional
   minimum-weight-2 column planes have image spaces meeting only at 0,
   and how many coordinate-permutation orbits do those pairs form? Pools
   W and B show that the printed complementary weight-(2,2,2) pair is not
   the only orbit. The first step is to list the weight triples of one
   such plane. This package does not make that list.

2. **The other two geometries.** Is every dimension-6 pool built from two
   normal-form triples, or from one normal-form triple and one column
   triple, a coordinate permutation of the corresponding printed witness?
   The counterexamples here are weight-1 column-column pools, so they do
   not decide those two geometries. The first step is the normal-form
   uniqueness statement on one 3-set in #7139, Section 2.

## Credit

The fiber lemma is Nick Petalas, #5921. The total-image bound and Lemma 3
are CubeJerry, #6838. The triple classification and the irreducible bound
3 are #6921. The dimension-4 irreducible 4-cycle is #6962. The
dimension-5 witness is #7094. The weight-1 bound and its printed
dimension-6 column witness are #7138. The three printed dimension-6
witnesses, and the question answered here, are #7139. Prepared by
unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0.
