# Three eleven-piece P112 profiles excluded by quotient selection

Eleven independent P112 pieces with code-intersection dimension at least five
cannot have binary support-rank bounds `3,3,5^9`, `3,4,4,5^8` or `4^4,5^7`,
over any characteristic-zero field. These are three actual TWOSIDE `(5,6)`
survivors in DreamingOfClouds's [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154).

The original support-only test certifies no six-piece quotient basis for
these profiles: the minimum support-cap sum is 56, above the strict cutoff 53.
The new proof contracts four small pieces. Three remaining images in one
projective class would give a two-dimensional code kernel with common support
at most 68. Root rigidity forbids such a kernel. The seven images therefore
have a singleton class, supplying the missing five-piece selection. The
retained root A5 count then gives `795 <= 756`, a contradiction with margin 39.
[PROOF.md](PROOF.md) gives all hypotheses and the characteristic-zero argument.

[RESULT.json](RESULT.json) retains the full 3,309,747-flat census, chamber and
root-plane receipts, all 77 original weight-filter survivors and the three
application receipts. Seventeen behavioral groups include a separate filter
implementation, rational quotient ranks, 232 odd class partitions, an even
failure control, strict support cutoffs and changed-input rejection.

This is a scoped decoder obstruction. Full C5, `C(P112)>=64`, supplier
admission and an improved kappa remain open. Selected kappa stays unchanged
at `0.001672660197076918`. The scope change from the block-climb card and the
live overlap check are recorded in [TASK.json](TASK.json).

## Reproduce

Python 3.12 or later, standard library only. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-eleven-piece-replay"
mkdir -p "$RUN"
TMPDIR="$RUN" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-eleven-piece-quotient
```

An existing Python 3.12 executable can replace the `uv run` prefix. The two
registered commands run sequentially with 120-second limits, including tests
under optimization. `verify.py --output NEW_PATH` creates an external receipt
and refuses to overwrite a file. Direct Git-free replay needs this package
and its sole declared P112 input at the same repository-relative path.
[CHECKS.json](CHECKS.json) records actual commands, environments and limits.

## Open next questions

Can a remaining actual profile with quotient dimension seven or weight-six
pieces meet a comparable kernel support bound? Pin its live residue and first
calculate the support of a proposed multidimensional kernel. The present
proof needs a two-dimensional quotient after four small pieces and an odd
seven-point remainder. These conditions do not cover all profiles. The
structured question, relevance and blocker are in [TASK.json](TASK.json).

## Credit and limits

Nick Petalas contributed the new quotient-selection proof and three explicit
exclusions. DreamingOfClouds's PR3154 provides TWOSIDE, its necessary filters
and the C5 handoff. Nick Petalas's [PR3169](https://github.com/CrocSwap/integer-mult-bounds/pull/3169)
and [PR3171](https://github.com/CrocSwap/integer-mult-bounds/pull/3171) provide
the retained geometric and root-simplex arguments. `geometry.py` is copied
byte-for-byte from PR3171, following PR3164/PR3162/PR3161. The E8/P112 decoder
lineage includes DreamingOfClouds and joaqcoo's original model. Exact heads,
Git blobs, hashes and code origins are in [SOURCES.json](SOURCES.json).
Historical citation hashes were checked locally; fresh CI needs only canonical
base provenance and the declared live input.
Frozen predecessors are unchanged. New and reused code is Apache-2.0.

The standard Weyl-chamber theorem is an explicit dependency; no proof-kernel
verification or full supplier replay is claimed. Development and local checks
used substantial automated assistance. Internal read-only reviews are not
independent human review. [ENGINEERING.md](ENGINEERING.md) records bounded
implementation decisions and the retained decision trail.
