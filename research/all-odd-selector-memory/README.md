# Optimal classical memory for the full all-odd selector

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration and an
attaining reversible recognizer. For `n>=2` Fourier-address rows, exact
one-pass deterministic recognition of the complete sufficient all-odd
phase sector needs exactly

```text
D = (n-1)(n+2)/2 bits of retained state at column boundaries.
```

Every column update is reversible. The lower bound allows arbitrary nonlinear
state encodings. It also holds for each separately known total width
`lambda>=2D`, even with position-dependent transition functions. At `n=73`,
the exact minimum is **2700 bits**, with this fixed-width conclusion from
`lambda=5400`. The sufficient width threshold is not claimed optimal.

Ali Romman's [PR4714](https://github.com/CrocSwap/integer-mult-bounds/pull/4714)
supplies the signature quotient and explicitly asks for a different
full-sector access method after its literal Haar-tree limit. The new step
constructs a length-`D` representative for every quotient class and an
equally long suffix distinguishing it from every other class. This closes
the minimum classical selector-memory question. The quotient and its
coordinate compression are credited premises, rather than new results.
[PROOF.md](PROOF.md) gives the complete argument and exact machine contract.

This changes the coverage-law card to a scoped classical selector result.
A smaller exact deterministic cache cannot merge these quotient states.
The program remains succinct despite having `2^D` possible states.
Recognition does not implement a spectral projector on an arbitrary
physical coefficient field. There is no physical space/time lower bound,
linear transfer-dimension claim, new kappa or selected-frontier update.

## Evidence and reproduction

The standard-library checker constructs every state at `n=2,3,4` and
checks its word against direct modulo-four phases on every odd physical
vector. The literal oracle uses no quadratic-coordinate updates.

- 548 states and all 8,464 one-column transitions pass, including their
  complemented inverse transitions.
- All 263,184 prefix/suffix pairs accept exactly on the matching class.
- Twenty encoded larger-state fixtures through `n=73` realize their
  state and return to zero. These do not enumerate the large groups.
- Thirteen controls cover nine invalid domains and four genuine failures
  of simplified update rules. The checker reports zero errors and emits
  a fresh receipt bound to all six package files.

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/all-odd-selector-memory/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/all-odd-selector-memory/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/all-odd-selector-memory
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/all-odd-selector-memory --check-source-history --check-modes
```

Any CPython 3.12 executable can replace that local path. Expected markers
are `PASS_ALL_ODD_SELECTOR_MEMORY`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. Direct checks write only stdout and need
neither Git nor predecessor files. Metadata/source-history checks use
the provenance pins in [SOURCES.json](SOURCES.json).

Local CPython 3.12.15 checks passed with normal and optimized receipts equal.
One timed run of each registered command took 4.18 and 4.19 seconds;
the combined registered replay took 8.85 seconds. These are timeout checks,
not a performance comparison. Three disposable altered-code runs rejected
a missing negative sign, omitted mixed update and omitted fixed-width padding.

## Related open work and CI

No same-object open PR was found in the checked open-body snapshot and
targeted searches. PR4714 is the merged predecessor. Weighted linear
transfer tables and arithmetic-chirp cut spectra study different machine
contracts; this theorem counts deterministic classical states only.

Hosted CI is pending. All registered commands ran locally; no local check
is deferred to CI. Source-history and publication-byte checks are separate
from scientific acceptance of the written theorem.

## Limitations and unrun obligations

The all-`n` theorem rests on the written distinguishable-continuation proof.
Finite checks corroborate it. The memory count includes all input-dependent
state at column boundaries, while immutable code and externally known
position are excluded. It does not bound transient workspace while processing
one symbol. Randomized error, multiple passes, promised inputs, other sectors
and shorter known widths are outside this result.

Physical Fourier-label access, arbitrary-input projector implementation,
native realization, full restoration and a paid precision/storage/tape bill
remain missing. All five selected framework assumptions remain. No predecessor
scientific executable, selected cold replay, Lean or Docker is run.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Find the least known width forcing the complete state count. Start with
   exact short-width reachable sets and distinguishable suffix classes at
   `n=3` or `n=4`. The present `2D` threshold is only sufficient.
2. Bind the selector to one fully priced non-affine physical access program.
   Specify how its Fourier-label predicate is obtained or used, preserve
   every arbitrary input and charge conversion and return. These physical
   interfaces and a favorable complete invoice remain blockers.

Structured versions are in [TASK.json](TASK.json). Neither continuation is
part of this contribution.

## Credit and provenance

Ali Romman's PR4714, at `4c42b1925ca589ca5a773f3e791d90b28dd79dfa`, supplies
the correlated sector, quotient and open access question. Its retained
source credits icekylinx for bulk recursion, compact tensor basis and
dependency-path precision, with Douglas Colkitt and the preceding native,
controller and stream lineage. Those credits and source notices are unchanged.
Classical distinguishable-state and reversible group-accumulation arguments
retain credit; no general automata-theorem or global literature priority is
claimed. No predecessor code or proof is copied into this package.

Canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030 at kappa `781451/250000000`. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373437)
records the scope. Live claims, local reservations, open PR bodies, main-tree
terms and merged searches were checked. Historical diffs and unpublished
work remain coverage limits. The selected baseline check passed bindings
only; no scientific admission is inferred from it.

## Verifier resource contract

The no-argument verifier has no recursion, subprocesses, dynamic evaluation
or external imports. The exhaustive domains have at most 512 states, 16
input columns and eight odd-vector tests per state. Pair checks are bounded
by 512 squared. Larger fixtures use at most 2700 columns per canonical
word and 5400 per return word. Every function is under 60 lines. Meaningful
checks remain active under optimized Python. Receipt reads are six fixed
files, each bounded by 128 KiB.

Python allocates integers and collections during arithmetic. This is a
managed-runtime deviation from Power of Ten rule 3, bounded by the fixed
domains above. The local dynamic call in the invalid-input checker targets
only `update`, a bounded deviation from rule 9. Warning-strict compilation
and normal/optimized execution provide diagnostics; no local Python linter
or type checker is installed.
