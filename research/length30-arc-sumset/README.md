# Rank 3 does not give a universal length-30 word

**Partial obstruction. No new κ.** In the restored binary singleton model,
`28 <= f(8) <= 32` remains the inherited bound. A universal closed word of
length 30 would need a multiplicity-2 source. This package proves that the
open sojourn of any such source cannot use exactly three other sources, and
it records pair-count floors on the complementary layer at ranks 4, 5 and 6.

Selected κ stays `781451/250000000`. The argument is in [PROOF.md](PROOF.md).

## Scope and evidence

Card `connector-alphabet-change`, scope **changed**. The card asks for one new
connector operation. This package stays in the published singleton alphabet and
answers the rank-3 half of the length-30 question left open by the sojourn
obstructions. The handoff is discussion #1166 comment 19377982. The predecessor
package is upstream pull request 6943, head
`c1cf726df3a06e50ef655ae91e8c8aac942b19a7` (fork pull request 154). It records
that rank at most 2 is impossible and that rank 3 forces at least 17 layer-0
projections. Those two statements are cited, not rerun. The 4+4 prefix-set
obstruction and the length-28 sharpness question are also left untouched.
An open-PR search on 2026-11-10 found no other length-30 arc-search package.

The new statements are:

- outside a rank-`r` sojourn flat, `Q0 + Q0` must cover `128 - 2^r` vectors,
  so `|Q0|` is at least 16, 16, 15 and 12 at ranks 3, 4, 5 and 6;
- rank 3 forces the layer-1 projection to be the whole 3-flat;
- the complementary arc then needs at least four height steps, which leaves
  only the shapes `(a,q,k) = (7,16,5)` and `(8,16,4)`;
- an exhaustive placement search on the 108 canonical quotient walks misses at
  least two vectors outside the 3-flat. The minimum is 2, so none covers.

A universal length-30 word, if one exists, therefore has every multiplicity-2
sojourn of rank at least 4. The rank-at-most-2 half of that sentence is the
cited predecessor. The explicit coverage-255 word of that predecessor has
sojourn ranks 6, 4 and 7, so it survives these floors. The length-32 Gray
concatenation is still a universal upper example.

## Reproduce

From the repository root, CPython 3.12 and gcc, standard library only:

```sh
python3 -B research/length30-arc-sumset/verify.py
python3 -O -B research/length30-arc-sumset/verify.py
python3 -B scripts/research_package.py --package research/length30-arc-sumset
python3 -B scripts/check_research_commit.py --package research/length30-arc-sumset --check-source-history
```

Expected marker:
`PASS_LENGTH30_ARC_SUMSET rank3=none best_miss=2 walks=108 floors=16,16,15,12`.

The C search is compiled by the verifier and runs one exhaustive pass. Checks
raise on failure, so `-O` does not disable them. `f(7)=24` was not replayed.
No Lean, Docker, or selected cold replay was run.

## Open next questions

1. Does a universal length-30 word exist when every multiplicity-2 sojourn has
   rank at least 4, with at least 16, 15 and 12 layer-0 projections at ranks
   4, 5 and 6? A yes answer lowers the upper bound on `f(8)` from 32 to 30.
   The coverage-255 witness shows that these floors are compatible with
   missing only one mask.
2. Does a universal length-28 word with multiplicities `(4,4,4,4,4,4,2,2)`
   exist? That is the sharpness question of #5234 and is not considered here.

## Credit

The model and prefix criterion are Ross Richardson's #943. The length-32
construction is Douglas Colkitt's #1185. `f(7)=24` and the eight-source
question are conorholds's #3058. The deletion bound is Nick Petalas's #5234,
and the length-30 handoff is discussion comment 19377982. The rank-at-most-2
obstruction, the bent lower bound, the 4+4 argument and the coverage-255
witness are the length-30 sojourn package, upstream pull request 6943
(fork pull request 154). This search does not reuse Nicholas Stone's
fixed-projection lift obstruction.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Independent human and proof-kernel review are unclaimed.
