# An XOR-normalized scatter boundary

`xor-scatter-v1` is an opt-in successor to the selected bit word's scatter
boundary. It reduces each row's retained-slot multiplicities modulo two before
running the authenticated full symbolic checker and record exporter. It repairs
PR2977's paired-duplicate mismatch without rejecting every repeated list.
The selected supplier, frozen sources and selected kappa are unchanged.

This is a compiler-boundary repair, not a new decoder or supplier. The parity
identity and original mismatch belong to the credited predecessors. The new
contribution is an executable, source-bound alternative to PR2992's reject-only
`simple-scatter-v1` contract, with observed export counts and full-word controls.
No production adoption is requested by the wrapper's existence.

## Contract and proof

The input is the selected checker's bit-word JSON, with scatter lists interpreted
as occurrences of retained **slots**. Integers exclude booleans. The boundary
allows at most 256 targets, 4096 helpers, 256 retained slots, 4096 occurrences per
row and 65536 occurrences overall. Compressed and uncompressed input sizes are
each bounded by 5 MiB. These are implementation limits, not mathematical bounds.
Every retained register must be a helper. The selected checker validates the
remaining word, frame and endpoint conditions after normalization.

For a target t and slot k, let m[t,k] count occurrences, and let z[k] be the
helper's value at the scatter entrance. Replace row t by the ascending list
of slots whose multiplicity is odd. Over any characteristic-two vector space,

```text
sum over occurrences k of z[k] = sum over slots k of (m[t,k] mod 2) z[k].
```

The original symbolic checker snapshots all retained values before scattering.
The exporter copies one slot at a time. Its scatter ADDs write only targets;
retained registers are helpers, so no scatter ADD changes a later copy's source.
Each COPY/ERASE pair restores its temporary. Therefore both orderings give the
same source values. On normalized rows, membership equals occurrence parity.
The complete ideal COPY/ADD/ERASE action agrees with the original symbolic word.
The other sections and all frame definitions remain unchanged.

This argument does **not** require distinct retained registers or independent
slot values. If two slots alias one helper, the same equality still holds after
substitution. The normalizer deliberately does not coalesce aliased slots or
remove unused slots. Every original COPY/ERASE pair remains charged separately.
It does not assert that slotwise parity is necessary for operator agreement when
slots are dependent. It is a sufficient, deterministic representation.

The normal form is idempotent and does not mutate its input. The emitted scatter
invoice is the sum of normal-form row lengths. The receipt reports the original
occurrence count separately, then checks actual phase-3 ADD, COPY and ERASE
counts from the packed records. A count alone does not certify their action.
The separate scalar replay tests that action.

## Commands

From the repository root, standard-library Python 3.12 or newer:

```sh
python3.12 -B scripts/research_package.py --package research/xor-scatter-boundary
python3 -I -O -Werror -B research/xor-scatter-boundary/verify.py
python3 -I -O -Werror -B research/xor-scatter-boundary/test_boundary.py -v
```

The public command checks before exporting. Use a new output path:

```sh
python3 -I -B research/xor-scatter-boundary/boundary.py check \
  research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz
python3 -I -B research/xor-scatter-boundary/boundary.py export WORD.json.gz OUTDIR \
  --scratch SESSION_SCRATCH_DIRECTORY
```

Both modes normalize a private snapshot and run the original checker with
optimization disabled. Export mode then runs the original exporter on the same
snapshot and validates its invoice before copying its three artifacts. It
refuses an existing output path, including a dangling symlink. Invalid scatter
schemas, changed delegate sources and failed symbolic endpoints produce no
output directory. Output publication is not a filesystem transaction: an I/O
failure while copying can leave a partial new directory. Callers must keep their
input, root and output-parent directories stable during execution.

## Evidence

[RESULT.json](RESULT.json) is deterministic evidence, not regenerated during a
normal replay. Four complete fixtures run through the actual checker/exporter.
Independent word and packed-record interpreters compare all 661 arbitrary input
columns, including dirty helpers. MOVE is ignored only in this scalar projection.
The original checker still checks its frame/lattice/interface conditions.

| Fixture | Input occurrences | Export scatter ADDs | COPY/ERASE pairs | Result |
| --- | ---: | ---: | ---: | --- |
| selected baseline | 527 | 527 | 9 | all three artifacts equal the raw selected export |
| append absent `[0,0]` | 529 | 527 | 9 | all three artifacts equal baseline; raw exporter disagrees |
| append existing `[4,4]` | 529 | 527 | 9 | all three artifacts equal baseline |
| append aliased retained slot, used twice | 529 | 527 | 10 | correct endpoint; the additional pair stays charged |

Appending absent `[0,0,0]` remains a wrong endpoint and the actual symbolic
checker rejects it before export. Normalization does not turn an incorrect
operator into the defining decoder. The baseline stream has 27234 records;
the alias fixture has 27236. No cost reduction is claimed for the selected word.

The independent finite coefficient oracle covers 1093 rows of length zero
through six over three slots, and all 27 maps of those slots to three helper
values, including every alias pattern. All 29511 comparisons agree. This is a
finite check of the written identity, not its universal proof.

Nine behavioral groups cover these cases, typed/range/capacity errors, gzip
expansion, original/normalized checker acceptance through the public CLI,
source corruption, output preservation, timeout cleanup, removed ADDs and a
wrong-destination ADD that preserves the invoice. Assertions remain effective
under `-O`; the retained code uses explicit checks. No independent human or
proof-assistant review is claimed.

## Sources, credit and limits

Local validation used CPython 3.12.15 and 3.13.5 on Linux x86_64,
kernel `6.6.87.2-microsoft-standard-WSL2`, with Ruff 0.17.1. Registered replay,
normal and optimized direct checks, metadata/pins and all 11 publication-byte
comparisons passed. A committed export containing only this package and its
three declared inputs passed optimized replay and all nine groups on Python
3.13.5 in a read-only Git-free directory. All 12 exported files, including the
transport manifest, retained their hashes. Hosted CI is recorded separately.

Base main `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[SOURCES.json](SOURCES.json) pins the checker, exporter and selected tuned word.
All three inputs are on canonical main, not unmerged PR heads. The registered
hook requires only those declared inputs; direct replay also works without Git.
No cached foreign Git object is needed for this source closure.

Credit Nick Petalas/PR2977 for the mismatch and candidate guard; Arham
Tahir/PR2992 for the operational simple-support boundary; Hiroki Kumazaki/PR3004
for the parity/count contract; James Reed/PR3099 for corroboration; Sricharan
Vagvala/PR3128 and commdata2338/PR3222 for retained-alias qualifications; and
commdata2338/PR3210 for actual odd-multiplicity native controls. The canonical
investigation is [Discussion2976](https://github.com/CrocSwap/integer-mult-bounds/discussions/2976).
The predecessor claims and source notices remain unchanged.

eumemic and DreamingOfClouds retain the selected PR543/PR555/PR589 word/checker
lineage. Dylan Crow wrote the exporter. Douglas Colkitt supplied selected
bindings and review. Nick Petalas. Apache-2.0. Substantial automated assistance
in research, implementation, checking and writing.

Not run: a fresh native C++/system-Boost replay, generator/tuner replay, complete
selected cold ancestry, physical hosting and movement, finite-precision/tape
transfer, all-size multiplication theorem or a new supplier moment. The native
interpretation of COPY/ERASE remains inherited. Retained aliases are not admitted
as a supplier merely because their scalar action passes. No new kappa or
selected-frontier change follows.

## Open next questions

1. Which successor schema should a reviewed producer adopt? The simple-support
   restriction remains sufficient. This package offers an occurrence-semantics
   alternative, not an automatic replacement. First bind a named caller's input
   contract and complete invoice. Maintainer adoption and native/physical
   supplier review remain blockers.
2. Can a caller profitably coalesce aliased or unused retained slots? First bind
   its actual COPY ownership, frames, counts and restore obligations. This
   normalizer intentionally preserves them, so it supplies no such saving.
   A caller and a complete paid invoice are missing; another abstract slot
   census is not justified.

## Engineering constraints

Boundary Discipline puts validation and authentication before delegation and
keeps normalization pure. Build the Lever produced the rerunnable source-bound
wrapper and independent scalar checks. Prove It Works required actual public
CLI and exporter execution, not merely the row identity.

Power-of-Ten deviations apply to Python allocation and subprocess dispatch,
not to frozen-source rewrites. Runtime objects are bounded by the limits above,
source inventories by 16 rows, and packed streams by 100000 records. Delegates
have 60-second deadlines and private source/word snapshots. Tests exercise
capacity rejection and timeout cleanup. All retained functions are below the
60-line review ceiling. The authenticated old scripts contain longer functions
and dynamic allocations; this package constrains them with input limits and
deadlines instead of changing frozen bytes. Revisit those limits and native
resource accounting before production adoption. Ruff and `-Werror` runs check
the new Python paths. Test mocks and the explicit local imports are bounded
runtime-dispatch deviations; they do not select an unpinned delegate.
