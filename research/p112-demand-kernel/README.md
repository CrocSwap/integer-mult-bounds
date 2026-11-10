# An exact 280-row P112 demand kernel

This contribution was produced by Nick Petalas. Claim type: finite certificate
and scoped equivalence proof. No new kappa.

For the fixed alphabet formed by the union of Jeremy Diviney's PR1422 support
layouts and the eight coordinate rectangles, all 262,928 orthogonal-clique
rank demands are equivalent to 280 saved demands. Exact duplicates leave
14 rectangles in this alphabet. Multiplicities can be any nonnegative real
numbers, in particular any unbounded nonnegative integer counts of terms.

Equal hit signatures give 1,141 inequalities. Keeping their maximum demands
and deleting rows dominated by a smaller hit set with at least as large a
demand leaves 280. Every retained inequality has a literal orthogonal-clique
witness. Every omitted original inequality has an explicit retained dominator.
[PROOF.md](PROOF.md) gives the equivalence argument; [RESULT.json](RESULT.json)
contains the generated kernel, exact alphabet and deterministic stream hashes.

This answers Open next question 2 of
[PR1422](https://github.com/CrocSwap/integer-mult-bounds/pull/1422) for a concrete
alphabet. It is a new smaller equivalent necessary-condition system. The source
census, counterexamples, costs and decoder claims are not audit deliverables.
The first strict reduction is the stopping point; no further optimization was
attempted. The broader current card's supplier/invoice task is explicitly changed
to this support-search side result in [TASK.json](TASK.json).

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p112-demand-kernel
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p112-demand-kernel/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/p112-demand-kernel/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p112-demand-kernel --check-source-history
```

Other machines can substitute their CPython 3.12 path. Expected scientific
marker: `PASS_P112_DEMAND_KERNEL`, with 262,928 complete demands, 1,141 hit
signatures and 280 retained rows. Each registered normal/optimized command
has a 300-second limit. No optional dependency or solver is required.

The verifier rebuilds every clique with a bitset prefix enumeration and a
separate literal-coordinate tuple enumeration. It checks every original
domination implication, every retained witness and pairwise nondominance.
It exhausts 16,384 binary multiplicity vectors, adds 256 integer vectors, and
checks 3,456 toy equivalence cases. Positive coordinate and known deficient-cap
controls, eight coordinate omissions and six malformed-certificate/domain
controls exercise the screen. A toy case prevents calling pairwise
nondominance full linear-program irredundancy.

`verify.py --emit` regenerates the certificate on stdout. Normal replay compares
its complete canonical JSON and prints a generated receipt bound to all eight
package-file hashes. No receipt is handwritten. The only live inputs are the
two exact pinned PR1422 JSON files declared in [VERIFY.json](VERIFY.json).
No predecessor executable is imported or replayed. Source/question provenance,
Git blobs and SHA256 hashes are in [SOURCES.json](SOURCES.json).

## Limits and open obligations

The theorem concerns the complete cap-based rank-demand screen for exactly
these 14 rectangles. Arbitrary repeated occurrences and independent whole-term
transposes are covered. Actual coefficient zeros or further support trims may
create stricter demands; the frozen cap kernel does not replace that changed
screen. Adding a rectangle or changing caps requires rebuilding the quotient.

The 280-row family is pairwise nondominated. No smallest-family, facet,
linear-program irredundancy or complete COPY floor is claimed. Passing it does
not provide coefficients or a decoder. No new runtime percentage is claimed.
Physical/native realization, access, dirty restoration, precision/tape, stock,
compiler closure, a complete signed invoice and outer integration are unrun.
The selected frontier and its five framework assumptions are unchanged.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Can nonnegative combinations of other inequalities remove any of the 280
  retained rows? Start with one row and a rational Farkas certificate. Such a
  calculation is not supplied, so pairwise nondominance does not settle it.
- Can changed caps pass the complete screen below COPY64 and admit exact
  coefficients? Specify the new alphabet and rebuild the complete quotient
  before synthesis. This fixed kernel and a support-level pass supply neither
  those coefficients nor a fully charged physical construction.

## Credit and overlap

Credit Jeremy Diviney / PR1422 for the explicit smaller-family question, complete
clique guard, pinned geometry and saved support caps; Cinna Davis / PR1347 and
PR1323 for the support model and geometry; Navinor, David Arias, Hanson Sun,
DreamingOfClouds, themilkman216 and the retained E8/label/decoder lineage.
Equal-row quotienting and monotone inequality dominance are classical. The
exact smaller system and its finite certificate are the contribution here.
All predecessor files and credits remain unchanged. Apache-2.0 for new material.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361613)
precedes the computation. Live open/account PRs, recent handoffs and local
reservations, main README quantity/formula searches, merged searches and the
cached overlap report were checked. The cache covered 369 open PRs and 6,284
Discussion records with complete pagination, but only 107 local notes against
8,917 at HEAD. Sparse notes, unpublished work and arbitrary historical code
remain outside that scan. No search absence is a proof of novelty.

PR5088's changed two-star dictionary and PR5064's changed-completion search
have different alphabets and coefficient objectives. Neither is repriced or
validated here. This result concerns the fixed PR1422 cap-screen inequalities.

## Verifier constraints

Functions are shorter than 60 lines. The verifier uses no recursion, subprocess,
network, dynamic evaluation or output files. It caps the geometry at 120 vertices,
cliques at 300,000, alphabet at 16 factors, and each JSON/source read at one MiB.
All loops have bounds from these caps; the actual alphabet has 14 factors.
Unexpected capacity exhaustion raises an error rather than truncating coverage.

Power-of-ten rule 3 deviation: CPython allocates integers and containers during
checking. The largest live collections are the bounded clique sets and the
current tuple-enumeration level, each capped by 300,000; signature storage is
at most 65,536 rows. These are one-shot exact finite checks, with ordinary scoped
file handles. Fixed allocation would require a separate runtime implementation.
Rule 9 deviation: six rejection callbacks have fixed named local targets and
finite fixtures; unexpected exceptions propagate. Both registered commands use
`-W error` and explicit guards, including under `-O`. No standalone linter was
available; syntax and AST function-length checks supplement those diagnostics.
