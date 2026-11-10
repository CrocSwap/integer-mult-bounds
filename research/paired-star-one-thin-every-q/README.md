# One thin map misses the three-leaf paired star for every q

**No new kappa. Evidence class: proof.** Over every field of characteristic
2, and for every port count q ≥ 1, one constant thin map does not meet the
paired-star endpoint at g = 3. The call order may interleave the two halves
of a stage, and the off-diagonal block B may be nonzero. The adjacent word
with two thin maps still meets the endpoint for every q. The selected
frontier stays 781451/250000000.

This is the uniform question left open by
[PR #7010](https://github.com/CrocSwap/integer-mult-bounds/pull/7010).
The F_2 census in
[PR #6922](https://github.com/CrocSwap/integer-mult-bounds/pull/6922)
is a finite statement at block size 2. It is not used as a premise and it
does not lift. The argument here forces the single thin map to be one
explicit matrix and then repeats the one-sided determinant comparison of
PR #5673. The statement, the hypotheses, and the limits are in
[PROOF.md](PROOF.md).

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 781451/250000000. This package
uses that record and edits neither file.

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
query demand removes real work. The assigned question is whether one thin
map fails at g = 3 for every q. The answer is a proof under the paired-star
hypotheses of PR #5747. It is not a caller, a native bill, or a change of
kappa.

The same identity shows that one constant thin map fails for every g ≥ 3,
on any orthogonal resolution of the stage supports. At g = 2 the count does
not start, and one thin map meets the endpoint. Neither sentence is a
search, and neither decides a five-map word.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-one-thin-every-q
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_PAIRED_STAR_ONE_THIN_EVERY_Q`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/paired-star-one-thin-every-q/verify.py
```

The polynomial words are exact identities in F_2[D_0, D_1, D_2, e] / (e^2).
They cover the two-map construction at q = 1 and q = 2, and they show that
the forced one-map matrix misses representative adjacent and interleaved
words. Those words are controls. The proof is the determinant comparison
for every q, not the list of controls.

## Open next questions

- Does any paired-star word at g = 5 meet the endpoint with exactly two
  constant thin maps, for some q? One map is impossible for every g ≥ 3, and
  at g = 4 the only positive count below ceil(g/2) is one map, so g = 5 with
  two maps is the smallest count this argument does not settle. A yes answer
  would be an interleaved escape below ceil(g/2). The first step is q = 1,
  one fixed legal pair, and one order that separates a stage: solve the two
  constant gaps by the specialization formula already used for the three-leaf
  census. Nothing in the star contract blocks that calculation. A failed
  search is not a proof. This is not the five-map question at g = 13 or
  g = 31.

## Credit

The paired-star contract, the rank floor, the one-sided column theorem, and
the two-map word are from PR #5747 (Ali Romman), including PR #5673,
PR #5681, PR #5631, and PR #5617. The adjacent-halves count that left this
uniform question open is PR #7010. The F_2 one-map census that does not lift
is PR #6922. Prepared by unpaidmoon with substantial Cursor Grok assistance.
Independent human review and a proof-assistant proof are unclaimed.
