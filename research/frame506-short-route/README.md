# Sixteen factors for the fixed frame506 matcher

This contribution was produced by Nick Petalas. Apache-2.0.

**Finite factorization certificate and scoped tensor-lift proof.** The exact
eight-dimensional matcher of JoyboyBrian's [PR4989](https://github.com/CrocSwap/integer-mult-bounds/pull/4989)
has a new word of **16 elementary column factors**, comprising five swaps,
four scalings and seven additions. Its published word has five swaps, five
scalings and fourteen additions. The matrix, native cut and low/high carry
contract stay fixed. No optimality or new kappa is claimed.

Both routing directions together remove `14 N f` ordered shifts and `2 N f`
unit scalings, with `N=8f`. The complete addressed schedule therefore loses
`16 N f = 128 f^2` steps in either ROW branch. No additional cache, native
call, carry site, ordinary swap, borrowed lifetime or low-type permutation
is introduced. These are contract-machine counts. Coefficient-specific
physical costs and the complete supplier invoice remain separate obligations.

## The literal word and proof

Read `add(i,j,c)` as `x_j <- x_j+c*x_i`, `scale(i,i,c)` as
`x_i <- c*x_i`, and `swap(i,j,1)` as a coordinate interchange. The
chronological word is in [WORD.json](WORD.json). Its first eleven factors are

```text
add(2,1,1); scale(2,2,2); add(1,2,-1)
add(7,4,-1); scale(7,7,2); add(4,7,1)
add(1,4,1); add(5,1,1); add(6,1,1)
scale(5,5,2); scale(6,6,2)
```

Finish with `swap(0,4)`, `swap(0,2)`, `swap(0,5)`, `swap(1,3)` and
`swap(1,6)`. All operations act on the current values, with no extra register.

For an arbitrary row `x`, put `u=x1+x2`, `v=x2-x1`, `w=x4-x7`,
`z=x4+x7`, `a=x5` and `b=x6`, using the incoming values on the right.
The eleven arithmetic steps give

```text
(x0, u+a+b, v, x3, u+w, 2a, 2b, z).
```

The five swaps give

```text
(2x5, 2x6, x1+x2+x4-x7, x1+x2+x5+x6, x0, -x1+x2, x3, x4+x7).
```

That is exactly `x S8` for `S8=[B^T|A^T]` at frame506 in the pinned
frame bank. The verifier multiplies all eight rational basis rows through
the new word and compares every entry with that source matrix. Reversing
the word and inverting each factor supplies the literal inverse; both
matrix-product orders are checked. Forward coefficients are `1,-1,2`.
The inverse adds `1/2` and is defined over `Z[1/2]`, hence modulo every odd
prime power in the source contract.

For any positive integer `f`, use each factor on the column pairs
`(i*f+lane,j*f+lane)`, `0<=lane<f`, in every one of the `N` matrix rows.
Disjoint lanes commute, and tensor multiplication gives exactly
`S8 tensor I_f`. Thus all positive `f` follow from the eight-dimensional
identity. Different owners, head/tail coordinates, ancestor fields and
exposed ROW values are not addresses of the new arithmetic. Their physical
preservation continues to require the inherited leaf contracts.

## Carry and complete scheduling consequence

Retain PR4989's cache, whole-route carry and low-type commit. With `q` odd,
`w>=2`, and a row written `g=l+q h`, the new high-factor product gives
`h S8` modulo `q^(w-1)`. Let `l'` be `l S8` modulo `q`, and let
`c=(l S8-l')/q` modulo `q^(w-1)`, with modular rational interpretation.
Adding `c` and committing `l'` gives exactly `g S8` modulo `q^w`.
The carry depends on the full matcher and the original low row, so it is
identical for this new factorization. The inverse has the same argument.
Every swap uses the retained completed ordinary or ROW-wrapped leaf;
those leaf implementations are premises, not replayed results.

The positive counts for the complete route/native/inverse shell are

| Item | New count |
| --- | ---: |
| Completed ordinary high-coordinate swaps | `10 N f` |
| Unit scalings | `8 N f` |
| Ordered linear shifts | `14 N f` |
| Low-controlled carry shifts | `2 N^2` |
| Low-cache copies and clears | `2 N^2` each |
| Low-type permutations | `2` |
| Canonical rank-`4f` native invocation | `1` |

Among the new ordered shifts, `8Nf=64f^2` target the smaller address and
`6Nf=48f^2` target the larger address. Unpaidmoon's
[PR6291](https://github.com/CrocSwap/integer-mult-bounds/pull/6291) reports
`64f^2` earlier-target and `160f^2` later-target sites in the old word.
Thus all fourteen removed shifts per row/lane are later-target shifts;
the number of unresolved earlier-target transposition leaves does not grow.
The new counts come from every emitted address pair, not a presumed symmetry
of forward and inverse routing. The predecessor's physical oracle gap is
retained as a cited premise.

The fixed thirteen shell steps are retained. A fallback swap is one
addressed step, giving `13+6N^2+32Nf` total. A borrowed swap expands to ten
steps, giving `13+6N^2+122Nf`. Subtract the published PR4989 expressions
`13+6N^2+48Nf` and `13+6N^2+138Nf`, respectively, to obtain `16Nf`
removed steps in either branch. The published comparator is cited, not
replayed or presented as a new validation result.

In particular, the source's three shapes have new counts 653, 1,373 and
5,453, compared with its published 781, 1,501 and 5,965. The word does not
alter `N^2 ceil(log2(q))` owned cache bits, padding extent, the complete
body/spectator fibre, the `30Nf(e-k)` body-addition count in the borrowed
branch, or any primitive's supplied width. Unknown physical tariffs are
not zero. The ledger emitter records operation names and addresses for
counting; it is not a replacement finite-alphabet runtime.

## Reproduce and evidence

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/frame506-short-route/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/frame506-short-route/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/frame506-short-route
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/frame506-short-route --check-source-history
```

Any CPython 3.12 path may replace the displayed local path. Expected marker:
`PASS_FRAME506_SHORT_ROUTE`, with 16 factors, 936 modular rows and 27
rejecting controls. The fixed domain has `f=1,2,3`, `q=3,5,7,11` and
`w=2,3,5`, with basis rows, deterministic mixed rows and carry boundaries.
Each row compares literal modular factor execution and the low/high
implementation with a separate dense source-matrix product, then checks
complete inverse restoration. The ledger emitter covers both branches at
`f=1,2,3,8`. The written proof, rather than finite sampling, gives all `f`
and admissible widths.

Controls reject omission of each of the sixteen factors, all seven changed
addition signs, reversed chronology, an omitted nonzero global carry,
a Boolean address and using the inverse as the forward word. Checks stay
enabled under `-O`. [RESULT.json](RESULT.json) is a generated receipt bound
to package and source hashes. `--emit NEW_PATH` regenerates it exclusively;
normal replay writes no files. No predecessor executable is imported.

The fixed checker has no recursion or network access. Loops are bounded
by at most 32 factors, the stated fixture lists and at most 64 coordinates.
The largest emitted schedule has 87,053 steps. Functions stay below sixty
lines. Dynamic allocation by Python/Fraction is the managed-runtime
Power of Ten deviation; those fixed bounds constrain live memory. A native
implementation would need fixed-capacity storage and the retained physical
leaf implementations. Warning-strict ordinary and optimized Python supply
the local diagnostics.

## Scope and credit

The originating `bit-helper-contract` card is changed to an addressed-route
construction. It reduces one implementation count at a fixed matcher; it
does not change the BIT target/paid moment, the selected frontier or kappa.
Native/ROW/scaling/ordered-shift leaf realization, physical routing,
coefficient preparation, cache retirement, stock/P3, tape and precision,
compiler closure and all five selected framework assumptions remain open
at their inherited strength. No selected cold replay, full predecessor
suite, Lean or Docker run is claimed. Independent human and formal
proof-kernel review are unclaimed.

Credit JoyboyBrian / PR4989 for the matrix, addressed shell, owner/ROW
contract and published comparator, ai-nanachi / PR4760 and PR4814,
Chris R / Clear1nsight / PR4957, rohanarun / PR185 and PR199, Maxime
Fleury / PR204, Cinna Davis, zxv, Jacob Alan Sussman, Mark/Matarener and
the retained native/E8/ordinary/routing/precision/tape lineage. Unpaidmoon /
PR6291 supplies the earlier-target physical gap and old directional counts;
JoyboyBrian / PR5052 supplies the separate completed signed-scaling API.
Elementary elimination and two-coordinate sum/difference transforms are
classical. The new contribution is this shorter fixed-matcher word,
inverse and complete conditional scheduling consequence.

## Open next questions

The next steps are coefficient-specific physical pricing and direct
installation into the current caller. Start with one existing unit-scale
and ordered-shift leaf at its actual address and charge all movement and
coefficient preparation. The changed intermediate factor order must be
accepted by that physical interface. Optimality of sixteen factors is
not established or needed for this result. Construction search stopped
at this first exact improvement.
