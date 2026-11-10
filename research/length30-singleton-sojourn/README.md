# Length-30 eight-source sojourns miss a low-rank case

**Partial obstruction. No new κ.** In the restored binary singleton model,
`28 <= f(8) <= 32` remains the inherited bound. This package rules out low-rank sojourns and 4+4 prefix sets for a closed
length-30 word, and it records a legal word whose prefix differences miss
exactly one mask.

A length-30 word has a source of multiplicity 2. If the steps strictly between
its two occurrences use at most two other sources, the word is not universal.
If they use exactly three, the complementary layer has at least 17 distinct
projections. Separately, no prefix set of size 30 is contained in a direct sum of two
4-dimensional subspaces and still covers `F_2^8`. Every prefix set contains
the zero state, and every covering subset of such a union that contains zero
has at least 31 points. The coordinate Gray
concatenation of length 32 is unchanged and still universal.

The argument is in [PROOF.md](PROOF.md). Selected κ stays `781451/250000000`.

## Scope and evidence

Card `connector-alphabet-change`, scope **changed**. The card asks for one new
connector operation. This package stays in the published singleton alphabet and
answers the length-30 case of the eight-source gap left by PR3058 and narrowed
to `28 <= f(8) <= 32` by PR5234. The handoff is discussion #1166 comment
19377982. Rank at most 2 and the 4+4 containment are the part settled here.
The family is not being expanded into another word search.

The finite verifier checks:

- all 1016 admissible multiplicity vectors and their four shapes;
- the coset counts `2^(7-r)` for `r <= 3`;
- all 896 bent functions on `F_2^4`, the quadratic example `x0 x1 + x2 x3`,
  and the absence of a 3-dimensional bent family;
- both the coordinate and one sheared 4+4 union: the full 31-point set
  covers, every 30-point subset that keeps zero fails, and deleting zero
  covers but is not a prefix set; plus one 30-point cover that leaves the
  union;
- the length-32 Gray concatenation and its multiplicity-2 layer sums;
- the explicit length-30 witness of coverage 255, its three sojourn ranks,
  and a swapped failure control.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3 -B research/length30-singleton-sojourn/verify.py
python3 -O -B research/length30-singleton-sojourn/verify.py
python3 -B scripts/research_package.py --package research/length30-singleton-sojourn
python3 -B scripts/check_research_commit.py --package research/length30-singleton-sojourn --check-source-history
```

Expected marker: `PASS_LENGTH30_SINGLETON_SOJOURN counts=1016 bent=896 gray=32 witness_coverage=255`.
Checks raise on failure, so `-O` does not disable them.

Not run: a SAT encoding of the remaining rank-at-least-3 words, a proof
assistant, Lean, Docker, and the selected cold replay. `f(7)=24` is an
inherited hypothesis, not replayed.

## Open next questions

1. Does a universal length-30 word exist whose every multiplicity-2 sojourn
   uses at least three other sources, and at least 17 layer-0 projections when
   it uses three? The witness below shows coverage 255 is attainable.
2. Does a universal length-28 word with multiplicities `(4,4,4,4,4,4,2,2)`
   exist? That is the sharpness question of PR5234 and is not decided here.
3. If both 28 and 30 are impossible, then `f(8)=32` by the Gray concatenation.
   A caller that could use a shorter singleton word is still unidentified.

## Credit

The model and prefix criterion are Ross Richardson's PR943. The length-32
construction is Douglas Colkitt's PR1185. `f(7)=24` and the eight-source
question are conorholds's PR3058. The deletion bound `28 <= f(8) <= 32` is
Nick Petalas's PR5234. The fixed-projection lift obstruction that this
sojourn split does not reuse is Nicholas Stone's PR5430. The length-30
handoff, including the unpublished annealing note, is Nick Petalas's
discussion comment 19377982.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Independent human and proof-kernel review are unclaimed.
