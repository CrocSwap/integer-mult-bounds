# Exact pairing spectrum for every standard-coordinate D_n puncture

For any subset of the projective roots `2e_i +/- 2e_j` of `D_n`, with its
**fixed standard-coordinate Gram decoder**, the minimum COPY cost over every
admissible binary pairing is twice the number of represented coordinate edges.
This includes asymmetric pairings. Consequently no such puncture has cost below
its number of root lines. A puncture ties exactly when it is a union of complete
opposite-sign pairs.

This answers the pairing-minimization handoff in Aaron Wang's
[PR 2272](https://github.com/CrocSwap/integer-mult-bounds/pull/2272), Open next
questions item 2, retained by
[PR 2518](https://github.com/CrocSwap/integer-mult-bounds/pull/2518).
All 1,023 previously observed D5 ties remain optimal over **all** admissible B.
The new result is the arbitrary-pairing theorem and exact cost distribution;
the B0 puncture counts and original root model belong to those predecessors
and DreamingOfClouds's
[PR 2125](https://github.com/CrocSwap/integer-mult-bounds/pull/2125).

## Model and theorem

Let `n >= 2`, and choose any nonempty subset S of the `n(n-1)` root lines,
represented once by `2e_i+2e_j` and `2e_i-2e_j` for `i<j`.
For each coordinate j let `I_j` be the live roots having nonzero j-th coordinate.
Use the exact decoder `Gram(S) = sum_j p_j p_j^T` with these coordinate columns.
An admissible matrix B over F2 has diagonal one and `B_ts=0` for distinct
nonorthogonal roots. All ordered entries at orthogonal pairs are free;
symmetry is an optional additional constraint. The raw cost, without a floor w,
is `C(B) = sum_j rank_F2 B[I_j,I_j]`.

Count the underlying unordered coordinate edges `{i,j}`:

- m edges have both signs present; s edges have just one; e=m+s.
- v=2m+s is the number of live root lines.
- d is the number of unordered live-root pairs on disjoint coordinate edges.
- k is the number of the m complete sign pairs whose **two directed** mate
  entries in B are not both one.

Then, for every admissible B,

```text
C(B) = 2e + 2k.
min_B C(B) = 2e = v+s.
sum_{admissible directed B} z^C(B) = 2^(2d) z^(2e) (1+3z^2)^m.
sum_{admissible symmetric B} z^C(B) = 2^d z^(2e) (1+z^2)^m.
```

Every minimizer has both entries equal to one at each complete sign pair.
Its entries between disjoint edges are arbitrary. Thus there are exactly
`2^(2d)` directed minimizers and `2^d` symmetric minimizers. Dense orthogonal B0
is one minimizer; no monotonicity of binary rank is assumed.

## Proof

Two distinct roots in the same coordinate support I_j either lie on the same
coordinate edge or on two different edges sharing j. In the latter case their
inner product is `+4` or `-4`, hence both pairing entries are forced zero.
The former case is the opposite-sign pair on that edge, and is orthogonal.
Reordering I_j by coordinate edge therefore makes its principal pairing block
block diagonal. A single root contributes `[1]`, of rank one. A complete pair
contributes `[[1,a],[b,1]]`. Over F2 this block has rank one precisely when
`a=b=1`, and rank two for the other three choices. Rank adds across these blocks.

Every represented coordinate edge occurs in exactly two supports, its endpoints.
Its singleton or good mate block therefore contributes two to C; a bad mate
block contributes four. This proves `C=2e+2k` and the minimum. Since
`v=2m+s`, the minimum equals `v+s`; equality with v is equivalent to `s=0`.

All distinct orthogonal root pairs are either the just-described mates or have
disjoint coordinate edges. A disjoint-edge pair cannot belong together to any
I_j, so neither of its directed entries affects any block being priced. There
are exactly 2d independent such bits, giving the factor `2^(2d)`. Each complete
mate has one good directed assignment and three bad assignments, with cost
increment two in the bad case. Multiplying their independent generating
factors proves the directed polynomial. Symmetry identifies the two entries:
each disjoint pair leaves one free bit and each mate has one good/one bad
assignment, proving the symmetric polynomial. This proves the all-n statement,
not merely its checked finite instances.

For all punctures of D_n, put `E=binom(n,2)`. There are `2^E-1` tied nonempty
punctures, because each edge is absent or complete. The number of punctures
whose minimum exceeds v by j is
`binom(E,j) * 2^E - [j=0]`: choose the j singleton edges and their signs,
and independently omit or complete the other E-j edges. The subtraction removes
the empty puncture. For full D5, `(e,m,d)=(10,10,60)`, minimum 20, with `2^120`
directed or `2^60` symmetric optimizers. These large counts follow from the proof;
the verifier does not enumerate that many matrices.

## Exact checks and boundaries

`verify.py` implements root geometry, admissibility, actual binary row elimination,
and an independent row-span cardinality rank algorithm. It does not import any
predecessor code. The source order and scale agree with PR2272's D(n) constructor.
`RESULT.json` is regenerated in full and compared, including every reported field.

- D3: all 342 nonempty relevant pairing states, with both rank algorithms.
- D4: all 117,648 relevant pairing states over all 4,095 punctures, checking each
  puncture's directed and symmetric coefficient distribution. Disjoint-edge bits
  are fixed at zero in this finite census; their freedom is proved above. This is
  a quotient census, **not** enumeration of all admissible D4 matrices.
- D5: all 1,048,575 nonempty punctures at B0; every principal subblock rank used
  in the lookup (1,280 total) is checked by both rank algorithms. The exact margin
  histogram has 1,023 ties and matches the formula. This independently reproduces
  predecessor counts as a positive control, not a new B0 census claim.
- 360 deterministic directed admissible pairing samples in D2 through D10,
  with disjoint-edge entries varying independently; direct rank bills match.
- Controls reject a missing diagonal and nonorthogonal nonzero entries. An
  inadmissible all-ones pairing on D3 would give cost 3 < 6. The four directed
  mate assignments cost `[4,4,4,2]`, so merely one directed bit being set does
  not obtain the rank-one cost. Finally the same singleton Gram `[8]` costs two
  in the standard basis but one with factors `(1,0)` and `(8,0)`, showing why
  the fixed coordinate-decoder hypothesis is essential for the exact formula.

This does not minimize over other factor bases, overcomplete factorizations,
different roots, or physical helper circuits. In particular it proves neither
the general T^2 threshold law nor a supplier, legal compiler, or new exponent.
The exact decoder identity follows directly from Gram construction; COPY pricing
is a scoped algebraic model, not a complete physical gate bill.

## Reproduce

Python 3.12+, standard library, from the repository root:

```sh
python3 -I -O -B research/dn-coordinate-pairing-spectrum/verify.py
python3 -I -O -B research/dn-coordinate-pairing-spectrum/test_boundary.py
python3 scripts/research_package.py --package research/dn-coordinate-pairing-spectrum
```

The verifier is read-only by default and uses explicit checks that survive `-O`.
To regenerate, pass `--out` with a nonexistent filename; overwrite is refused.
The boundary test exercises a Git-free package export, corrupted and missing
receipts, full regeneration, and exclusive output. The symbolic all-n proof is
the written argument above, not a Lean proof or an implication of finite testing.

## Open next questions

1. Can changing the factor basis of a tied D5 puncture lower cost below v when
   B is optimized jointly? This matters because the coordinate proof no longer
   applies. Start with one elementary basis shear and classify support changes;
   the blocker is the infinite rational factorization family.
2. Can the same two-by-two block argument be extended to a non-coordinate root
   alphabet? This would identify a broader obstruction. Start by characterizing
   intersections of factor supports; larger orthogonal induced blocks need new
   rank bounds and need not decompose into independent mate blocks.

Contributor: ywz65, with substantial OpenAI Codex assistance in derivation,
implementation and writing. Separate AI review is recorded in TASK.json when
completed; no independent human review is claimed. Exact predecessor heads,
catalogue, selected-record pins, selection and overlap freshness are recorded in
SOURCES.json and TASK.json. No frozen source or selected frontier is changed.
