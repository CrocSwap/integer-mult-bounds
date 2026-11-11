# No-edge pattern dimension 5 has an irreducible image of dimension 7

**Result.** For every ambient width at least 7, the seven projectors

```text
(e0+e2)(e1+e2)^T,
(e1+e2)(e0+e2)^T,
(e0+e1+e2)(e0+e1+e2)^T,
(e3+e5)(e4+e5)^T,
(e4+e5)(e3+e5)^T,
(e3+e4+e5)(e3+e4+e5)^T,
(e2+e5+e6)(e2+e5+e6)^T
```

are the complete pool of their pattern span. That span is five-dimensional
and contains no matrix unit. The joint image is seven-dimensional and the
action is irreducible. **No new κ.** The selected value remains
`363005817/100000000000`.

A complete no-edge pool of pattern dimension 5 therefore need not have total
joint image at most 6, and its irreducible image can have dimension 7. The
parity construction one dimension above the pattern-dimension-4 example still
has total image 6 and is reducible, so it does not decide either question.

## Scope and evidence

Catalogue card: `bit-new-register-model`, priority revision 8, base commit
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status: **changed**. The
card asks for a new register alphabet. This package answers open question 1
of #7139: whether a complete no-edge pool of pattern dimension 5 still has
total joint image at most 6, and whether its irreducible image can exceed 5.
The reason is recorded in [TASK.json](TASK.json). The original native
acceptance gate is unmet, and the selected frontier is unchanged. Question 2
of #7139, the coordinate classification at pattern dimension 4, and question
3, the paid-rank split, are not this result.

[PROOF.md](PROOF.md) is the argument. Sections 2–6 identify the pattern space
and prove that the complete pool is exactly these seven projectors at every
width at least 7. Section 7 proves the action is irreducible: a vector hit
by the linking covector generates the whole image, and a subspace killed by
that covector cannot contain a block image, which forces it to be zero.
Section 8 records the even-weight column of dimension 5: total image 6, with
the even-weight space invariant. That is the parity construction named in
the question. It is a comparison, not a bound.

[verify.py](verify.py) repeats the finite parts: the pattern-space weights,
the six linking entries on every odd coset vector, the dual bases, the
complete pools at widths 7, 8 and 9, the closure of all 127 nonzero image
vectors, the deleted-link control, and the parity pool at widths 7 and 8.
Deleting the linking projector leaves the coordinate block on {0,1,2}
invariant. The parity pool's even-weight line is invariant, while closing an
image vector under that pool spans the whole image, so the reducible control
is not an arbitrary seed. These checks certify the two explicit pools. They
do not enumerate five-dimensional pattern spaces. Sections 4–7 are what
cover every width.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue is provenance
at the base commit, and the selected record is an input because the verifier
reads it. Full Git history is needed to resolve the pins. Nothing here reruns
the selected baseline as a scientific replay.

Overlap was checked on 2026-11-11. A local `find_overlap.py --offline` search
at base `e54523517d0f03e58352e647c403a5af3e525a57` covered 10178 notes with a
complete head inventory. The matches are the predecessor packages for pattern
dimension at most 4. The remote overlap cache was not available in that run.
A live GitHub search of `CrocSwap/integer-mult-bounds` for the pattern-dimension-5
no-edge question returned the predecessor chain and open #7094 and #7139, which
ask the question and do not answer it. Open #7138 is the weight-1 pattern-dimension-4
bound. Recent comments on discussion #1166, checked the same day, do not take
this question. No match is not a novelty certificate.

## Reproduce

From the repository root, with Python 3.12 and the standard library only:

```sh
python3 -B research/no-edge-dim5-irreducible-seven/verify.py
python3 -I -O -B research/no-edge-dim5-irreducible-seven/verify.py
python3 -B scripts/research_package.py --package research/no-edge-dim5-irreducible-seven --check-only
python3 -B scripts/research_package.py --package research/no-edge-dim5-irreducible-seven
```

The verifier prints `PASS_NO_EDGE_DIM5_IRREDUCIBLE_SEVEN`.

## Open next questions

1. **Is 7 an upper bound at pattern dimension 5?** Does every complete no-edge
   pool of pattern dimension 5 have total joint image at most 7? This witness
   shows that 6 is too small. The zero-edge quotient bound is still 31. The
   smallest next step is the one-dimensional extension of a dimension-6
   pattern space. A width-bounded search would not prove the bound.

2. **Is the dimension-7 pool unique up to coordinates?** Is every irreducible
   complete no-edge pool of pattern dimension 5 and joint-image dimension 7 a
   coordinate permutation of these seven projectors? The existence proof does
   not identify the pools. The smallest next step is to match the two
   normal-form blocks and the linking vector.

## Credit

The fiber lemma is Nick Petalas, #5921. The parity construction compared in
Section 8 is CubeJerry, #6838, moved up to pattern dimension 5. The normal-form
triple is the one classified in #6921; this proof uses only the displayed
projectors and the fiber lemma. #7139 asked the question and proved the
pattern-dimension-4 bound; that bound is not an input. #6782 supplies the
zero-edge quotient bound 31. Prepared by unpaidmoon with substantial Cursor
Grok assistance. New work is Apache-2.0.
