# The dyadic formal error peak has leading constant two

**Exact counterexample and scoped written proof; No new κ.** In the unchanged
balanced dirty word, the proposed universal Omega cut does not maximize
accumulated independent completed-leaf errors. At 128 factors a later scratch
readout has total formal channel mass **26,144**, versus **26,028** at Omega.
The same mechanism gives a family of counterexamples at every dyadic size
from 128 onward, and an asymptotically sharp all-cut upper bound:

\[
E_\infty(2^h)\le 2\cdot4^h-3^h,
\qquad \lim_{h\to\infty}\frac{E_\infty(2^h)}{4^h}=2.
\]

The old fixed Omega cut has leading constant 11/6. This is a result about
formal free-algebra error mass, not a multiplication speed improvement or
physical rounding lower bound. The complete argument is in [PROOF.md](PROOF.md).
It uses credited source lemmas; neither human independent review nor a formal
proof kernel is claimed. Finite checks corroborate, rather than prove, the
all-height statements.

## Exact result and chronology

For height h>=2, use the positive word on n=2^h factors; number registers
x=0, y=1, z_j=j+1. Read z_2 at completed-leaf count
`4^h-(4^(h-2)+2)/3`. Its exact total channel mass is

    K_h = (47*4^h - 68*3^h + 48*2^h - 20)/24.

Subtracting the fixed Omega mass gives
`4^h/8-3^h+2^(h+1)-1`, positive for every h>=7. At h=7:

| Readout | Completed leaves | Register | Nonzero channels | Total mass |
| --- | ---: | ---: | ---: | ---: |
| New cut | 16042 | 3 | 15594 | 26144 |
| Omega | 15018 | 8 | 14891 | 26028 |

[WITNESS.json](WITNESS.json) includes both full profiles and SHA256 digests of
**every signed channel polynomial**, including zero channels. The first error
budget at which this new profile wins is 15479. At budget 29 the old cut still
wins, 176 versus 175: the new cut is not a replacement universal profile.

A deeper version of the same cut family approaches leading constant two.
The upper bound pairs a forward prefix with its complementary inverse prefix,
and charges their combined mass to complete-call exit supports. Section 6 of
the proof gives explicit finite formulas and the limiting argument. We do not
claim the first possible counterexample, an exact finite-height global
maximum, or a maximizing cut for every error budget.

## Source pins, novelty and credit

Base and checkpoint canonical main:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
[SOURCES.json](SOURCES.json) pins all five live inputs by SHA256 and Git blob,
and the selected certificate/task catalogue as historical provenance.
The selected accepted value at this base is 0.003125804, from #6030's audited
source `772dd10a5859a1d15f4851feb371519789213ad8`; it is unchanged.

- Chafik Boukhalfa's #628 supplies the balanced reserved-depth dirty word.
- Philippe Van Velzen (`philippeVV`), #2177, original head
  `2cbbb48d3b580e018312278c97b63817de963be7`, supplies the single-error and
  prefix/exit lemmas, finite accumulated-error census, and conjecture C1.
  Its substantial Claude assistance and predecessor credit remain intact.
- ywz65, #2735, original head `90a507b39063cfaebdf92794fcb9d18f358439a6`,
  proves the fixed Omega profile and complete-call support recurrences,
  explicitly leaving C1 open. That fixed-cut theorem is unaffected.
- Adam Gall's #2067 supplies endpoint channel counts. Retain the earlier
  transport lineage credited by #2177, including woklerx, Charles Bethin
  (#1416), Arham Tahir (#1374) and Hanson Sun (#1085).
- The overlap review also considered #5938, #6668 and #6770. Their
  single-channel/count or interval-transport scopes differ from the sum over
  all independent errors in a chronological prefix here; they are not inputs.

The new contribution is the C1 counterexample, its exact all-height family,
and the matching leading asymptotic for global formal total mass. No copied
source verifier or recurrence engine is used. The primary replay extracts only
an authenticated predecessor leaf generator for an explicit order comparison;
its own word and polynomial engines remain separate. The forward replay uses
neither that generator nor the primary engine.

Prepared for **@CubeJerry**, with substantial **OpenAI Codex assistance** in
mathematics, code, verification and writing. All new files are Apache-2.0.
No delegated agents or independent human review are represented.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/dyadic-omega-counterexample
```

Expected: `PASS_REGISTERED_RESEARCH_PACKAGE research/dyadic-omega-counterexample outcome=completed`,
with `PASS_DYADIC_OMEGA_COUNTEREXAMPLE`, `PASS_FORWARD_OMEGA_COUNTEREXAMPLE`, and
`PASS_COLD_OPTIMIZED_AND_TAMPER_CONTROLS`. The package authenticates its five
source inputs. A Git-free export runs the three registered commands directly;
provenance/metadata validation through the repository hook additionally uses Git.

The bounded replay checks:

- 134 literal source-order comparisons; 32 full profile comparisons through
  height 8; 28 literal generalized-family cases; 4950 integer
  recurrence/formula pairs through height 100.
- A separately written **forward** interpreter of all 16,384 witness leaves,
  using reversed literal lists for inverses and integer-encoded words rather
  than backward tuple words. Both complete signed polynomial digests match.
  Another 1954 paired-prefix/readout cases check the upper-bound mechanism
  through height 4, including scratch-bound equality.
- Ten primary and four forward controls, including wrong inverse order,
  omitted restoration, endpoint/wrong-register substitutions, independent
  versus shared opposite errors, and altered typed/profile/digest receipts.
- Cold Git-free replay under optimized Python (`-O`) with warnings treated
  as errors, then actual corruption of each source input and the witness,
  all required to fail. This is a portability/failure-detection check,
  not a third independent mathematical implementation.

[VALIDATION.md](VALIDATION.md) records the executed checks and their limits.
[TASK.json](TASK.json) records the changed scope, seed, local claim,
search/overlap coverage and stopping rule; [VERIFY.json](VERIFY.json) registers
exact commands. Sparse archive search and live term searches are not an
exhaustive novelty certificate. No repository-wide historical scientific
replay is needed or claimed for this isolated result.

## Scope and inherited assumptions

Errors are distinct formal symbols injected **after completed leaves**.
Factors are free and noncommuting; the source's prefix and exit lemmas and
exact scratch restoration are retained. Mass bounds operator error for
contractive factors by the triangle inequality; simultaneous realization
by native operators or rounding is not proved. The package does not cover
internal leaf intermediates, numerical inverses, aliasing, a rounded caller,
or precision/tape costs. All five selected assumptions remain:
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`,
`analytic_recovery`. C1 is a separate conjecture, not a selected assumption.

## Open next questions

1. Determine exact finite-height maxima and error-budget tradeoffs. A useful
   next step is a proved phase recurrence preserving complete channel profiles
   and collisions; a mass-only exploratory recurrence is insufficient.
2. Connect this formal envelope to one pinned native rounding implementation,
   including inverse phases, restoration, boundaries and tape costs, before
   pricing any effect at the selected multiplication caller.

The finished result requires neither question to be settled. **No new κ.**
