# Odd fresh links give further irreducible no-edge pools of image dimension 7

**Result.** On two fixed disjoint normal-form blocks, a square link that meets
each block in at most one coordinate has a 5-dimensional unit-free pattern
space, a complete pool of seven projectors, and joint image of dimension 7.
The action is irreducible if and only if both of those coordinates are the
hubs and the remaining support is a nonempty fresh set of odd size. Every
such odd size works, at every large enough width. **No new κ.** The selected
value remains `363005817/100000000000`.

The fresh-size-1 pool is the seven-projector witness of open PR #7237. The
fresh-size-3 pool has linking image weight 5 and linking pattern weight 20,
while the witness has linking image weight 3 and linking pattern weight 6.
A coordinate permutation preserves both weight multisets, so the size-3 pool
is not a coordinate permutation of the witness. Question 2 of #7237 therefore
has a negative answer: an irreducible complete no-edge pool of pattern
dimension 5 and joint-image dimension 7 need not be a coordinate permutation
of those seven projectors.

The seven projectors have the same covector-image incidence for every odd
fresh size. This package does not claim a new configuration of lines, and it
does not claim inequivalence under an arbitrary linear change of basis.

## Scope and evidence

Catalogue card: `bit-new-register-model`, priority revision 8, base commit
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status: **changed**. The
card asks for a new register alphabet. This package answers open question 2
of #7237 by the link-matching step named there. The reason is recorded in
[TASK.json](TASK.json). The original native acceptance gate is unmet, and
the selected frontier is unchanged. Question 1 of #7237, whether 7 is an
upper bound, is not answered. The dimension-6 coordinate classes of #7221
are not these pools.

[PROOF.md](PROOF.md) is the argument. Theorem 1 constructs the odd-fresh
family. Sections 2–4 identify the pattern space and the odd coset without
the fiber lemma. Section 5 cites the fiber lemma of #5921 for the even
coset, which is what extends the pool identification to every width.
Section 6 proves irreducibility. Theorem 2 classifies every other square
whose support meets each block in at most one coordinate: the complete pool
is still seven projectors and the image still has dimension 7, but a missed
block leaves that block's coordinate space invariant, and a leaf leaves the
weight-2 image that omits the leaf invariant. Section 8 separates fresh
sizes by Hamming weight. Section 9 records the common incidence matrix.

Section 10 is an exhaustive finite census, not a substitute for those
proofs. With the two blocks fixed, every one of the 8128 idempotents at
width 7 was adjoined. The only irreducible image of dimension 7 is the
fresh-size-1 witness. Every odd-weight square at widths 8 and 9 was
adjoined. The irreducible hits are the fresh-size-1 squares on the
available fresh coordinates, and, at width 9, the single fresh-size-3
square on all three fresh coordinates. Squares that meet a block twice are
inside those domains and are not hits. Non-square idempotents at width 8
or more were not enumerated.

[verify.py](verify.py) repeats the family at fresh sizes 1, 3 and 5,
including one padded width for sizes 1 and 3, the incidence matrix, the
weight multisets, the leaf and missed-block controls, the deleted-link
control, and both censuses. These checks certify the stated pools and the
stated finite domains. They do not enumerate five-dimensional pattern
spaces that do not contain the two blocks.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue is provenance
at the base commit. The selected record is a live input because the verifier
reads it. Full Git history is needed to resolve the pins. Nothing here reruns
the selected baseline as a scientific replay.

Overlap was checked on 2026-11-11 with `find_overlap.py` at base
`e54523517d0f03e58352e647c403a5af3e525a57`, while this package was still
untracked. Local coverage searched 10180 notes against a complete head
inventory of 10178; the two extra notes are this package. The open-PR
snapshot had 570 records and the discussion snapshot had 7245, both with
complete pagination. The matches are this package, the pattern-dimension
at most 3 and 4 predecessors, and open #7094, #7138, #7139, #7218, #7221
and #7237.
#7237 asks the uniqueness question and exhibits the fresh-size-1 witness;
it does not classify other links. #7221 separates dimension-6 pools at
pattern dimension 4. Closed work was searched through local notes and the
ledger, not through a separate closed-PR body fetch. No match is not a
novelty certificate.

## Reproduce

From the repository root, with Python 3.12 and the standard library only:

```sh
python3 -B research/no-edge-dim5-fresh-link/verify.py
python3 -I -O -B research/no-edge-dim5-fresh-link/verify.py
python3 -B scripts/research_package.py --package research/no-edge-dim5-fresh-link --check-only
python3 -B scripts/research_package.py --package research/no-edge-dim5-fresh-link
```

The verifier prints `PASS_NO_EDGE_DIM5_FRESH_LINK`.

## Open next questions

1. **Is 7 an upper bound at pattern dimension 5?** Does every complete no-edge
   pool of pattern dimension 5 have total joint image at most 7? This family
   attains 7 and shows that 6 is too small. The zero-edge quotient bound is
   still 31. The smallest next step is a one-dimensional extension of a
   dimension-6 pattern space. Another fresh set on these two blocks does not
   decide the bound.

2. **Is there an irreducible image of dimension 7 with no two disjoint
   normal-form blocks?** The width-7 census fixes the blocks. A pool that is
   not a coordinate permutation of any odd-fresh link would be a different
   coordinate class. The smallest next step is to decide whether every
   irreducible image-7 pattern space of dimension 5 contains a normal-form
   triple. Enumerating 5-planes in the 42-dimensional space of 7×7
   zero-diagonal matrices is not a feasible substitute for that reduction.

3. **At width 8, does a non-square idempotent extension of these two blocks
   have irreducible image dimension 7?** The width-7 census includes
   non-squares and finds none. Width 8 has 32640 idempotents, and this
   package did not enumerate them. The smallest next step is the same
   complete-pool test. A partial sample would not be that census.

## Credit

The fiber lemma is Nick Petalas, #5921. The normal-form triple and the
irreducible bound 3 at pattern dimension at most 3 are #6921. The
pattern-dimension-4 irreducible image is #6962. #7139 proved the
pattern-dimension-4 total-image bound and asked the pattern-dimension-5
questions; that bound is not an input. #6782 supplies the zero-edge quotient
bound 31. Open #7237 exhibits the fresh-size-1 witness and asks the
uniqueness question answered here; its existence proof is not redone. Open
#7221 classifies dimension-6 pools and is not this seven-projector family.
Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0.
