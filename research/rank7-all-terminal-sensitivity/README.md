# PR2979 terminal sensitivity at individual calls

Two widened endpoint occurrences already fail PR2979's claimed complex
budget, even with arbitrary fractional repacking in its fixed capacity pool.
This holds across all 22 original jointly lowered helpers and all 666 calls,
not only uniform changes to the four V45 endpoints. The exact complete-moment
lower bound is greater than `1.000000000041`.

The count two is sharp for this relaxation. Either one-occurrence width class
has an explicit nonnegative tight-pattern primal with moment below one.
Those primals are fractional, not physical allocations. The unchanged literal
source profile also passes its positive moment check. No new supplier,
kappa, selected-frontier change or full multiplication theorem is claimed.

## Added coverage

PR3237 at `9881b9d5dfe20017503c8d14baaae8629c5afb10` already rejects all
15 uniform terminal-widening controls on V45's four endpoints. This package
credits that result and does not claim those cases as new. It proves a
common dual sensitivity for both width classes, checks the literal terminal
paths of all five groups in both providers, and derives a universal bound
for nonuniform changes among 14,652 individual occurrences. There is no new
lowering census or root-digit refinement.

All gates, partner frames, later stages, entrances, cleanup and the capacity
pool stay fixed. One widened occurrence adds one rank-one terminal child and
changes width 6 to 7 or 7 to 8. Both changes have the same shadow price.
[PROOF.md](PROOF.md) gives the complete model and weak-duality argument.
[RESULT.json](RESULT.json) records all endpoint frames, the formal dual,
exact enclosures, and both one-change fractional witnesses.

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/rank7-all-terminal-sensitivity

# Direct checks also work in a Git-free export of the package and its seven inputs.
python3.12 -I -Werror -B research/rank7-all-terminal-sensitivity/verify.py
python3.12 -I -Werror -B research/rank7-all-terminal-sensitivity/test_verify.py
```

Expected markers are `PASS_ALL_TERMINAL_SENSITIVITY`, eleven passing
behavioral groups, and `PASS_REGISTERED_RESEARCH_PACKAGE`. `verify.py --emit`
regenerates the complete receipt to stdout without modifying files. Normal
execution compares every regenerated field with the committed receipt.

The checker independently reconstructs both frame profiles and all endpoint
changes. It enumerates all 2,551 bin patterns and checks every dual inequality.
An alternate combination enumerator checks pattern completeness. Explicit
point-set geometry checks all 67 subspaces of F2^4 and their containment pairs.
Controls reject stale endpoints, wrong entrances, missing or duplicate helpers,
invalid primal patterns and counts, singular dual equations, duplicate JSON
keys and corrupted source bytes. All 22 literal single-widening words are also
recounted. The optimized CLI runs on read-only source files in a Git-free export.

The only reused implementation is the authenticated exact square-root tariff
module from `coupled-cap-independent`; the supplier's producer, frame solver,
root code and verification receipts are not executed. That reuse is credited,
not described as a second independent tariff implementation.

## Sources, environments and limits

Canonical scientific base is `463113d675af7410ac91d53a4fed51ec6494eb9a`,
priority revision 6. The PR2979 word bytes match its retained head
`be191346391661f4d35fc0d1508d0a6029572576`. Every executable dependency and
input is available on canonical main; no unmerged or foreign Git object is
needed. [SOURCES.json](SOURCES.json) binds the seven live inputs and original
card/selected provenance. [ENVIRONMENT.json](ENVIRONMENT.json) records local
versions and exact checks. Hosted CI is separate from local verification.

The original allocation's authenticated complete profile is used as a positive
fixture. Its placement legality is not replayed here. Native/scalar/dirty-state
semantics, actual cleanup and storage/movement, precision/tape, the bit cap,
supplier admission, outer release and all-size/compiler obligations remain
unrun. The two-change obstruction suffices within the stated relaxation;
unknown physical costs are not treated as proved zero in a construction.

The expansion decision is to stop fixed-word terminal-widening experiments,
not to close other mechanisms. Changed scalar graphs, helper splitting or
coding, altered capacities and changed consumer contracts remain outside scope.

## Open next questions

Can either one-occurrence fractional witness be replaced by a legal integral
chronological allocation at the same saving? This would distinguish the
relaxation's sharp count from physical feasibility. Start with the two exact
primal rows in `RESULT.json`, then enforce literal windows and same-call
physical-family exclusions. The fractional witness alone supplies neither.
This package does not authorize or launch another allocation search.

A more consequential follow-up is a complete physical/native join for the
unmodified candidate. Start with one named owned endpoint, its executor
location, and its actual movement and precision charges. The existing native
and allocation audits do not by themselves supply that physical caller.

## Credit and engineering checks

Nick Petalas. Apache-2.0. Substantial automated assistance was used in analysis,
implementation, verification and writing. No independent human or proof-kernel
review is claimed.

Credit Marius-Paul Dumitrean/PR2979 for the words, stage records and relaxation;
commdata2338/PR3237 for the V45 complete-control obstruction; Jeremy Kothe for
the frame accounting, inverse cleanup and later rewrites; Mason Hale and Jeremy
Diviney for the paired-extraction and chronology lineage; Nick Petalas for the
reused independent square-root arithmetic. Retain Yiyang Lu, Tekalign, Dugongue,
icekylinx, Ross Richardson, Sagar Thakrar, themilkman216 and the source package's
full geometry/native/owner attribution. Frozen predecessors are unchanged.

Build the Lever produced the replayable source-bound certificate. Prove It Works
required literal endpoint recounts, positive fractional witnesses and Git-free
execution. Test Behavior, Not Implementation required actual changed words and
semantic rejection controls.

Power of Ten inspection covers the three new Python files. Functions stay below
60 lines; all loops are bounded by 704 registers, nine frame bits, authenticated
section lengths, 2,551 patterns, ten equations, 22 endpoints or fixed 160-step
arithmetic. Subprocesses have 120-second deadlines and checked return codes.
Explicit exceptions remain enabled under optimization. Rule 3 has a managed
Python allocation deviation, bounded by 2 MB raw and 32 MB decoded input limits,
fixed nine-pivot workspaces, and finite pattern and source sizes. A resident or
untrusted-input service would need a separate fixed-capacity parser. The one
cross-package import is authenticated and has a fixed canonical path. No
producer code is imported or generated. Warnings are errors in registered
commands; repository Ruff checks cover every new Python file. No shared lint
or workflow configuration is changed.
