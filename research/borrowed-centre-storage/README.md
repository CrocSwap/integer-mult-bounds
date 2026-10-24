# Borrowed centre storage and masked access

This package gives two complete storage constructions for the historical
14,336-owner schedule, one local masked-query unit, and one cleanup word
at a specified aligned cut. It does not improve the complete kappa
calculation. It does not supply a complete encoded Fourier supplier.

The [proof](PROOF.md), [source pins](SOURCE-PINS.json), and
[replay](replay.py) define the scope. [EVIDENCE.md](EVIDENCE.md) links each
fresh check and its original proof. The frozen sources retain their
original bytes. The [adapter diff](ADAPTATIONS.patch) shows each change
needed to read portable inputs and write a new replay receipt.

| Result | Coverage | Added local cost | Main limit |
| --- | --- | --- | --- |
| Relative dirty transport | 512 rows in 64 windows; 512 distinct old owners | 274,432 real scalar primitives; no new child or field | The cache includes an arbitrary old value. A later read needs its own cancellation proof. |
| Clean idle storage | 512 rows; 1,024 swaps; 384 bridge read changes | 26,624 real scalar primitives; no new child or field | The query keeps its original physical frame and must be restored before swapback. |
| Masked query unit | All 712 local input columns; all 480 arbitrary helpers | 213,466 real scalar primitives; eight H1 children beyond clean-J | Only D=R_U is emitted. The target inverse is an algebraic inverse. |
| Owner-local masked cleanup | All 457 data, donor, and scratch columns | 25,124 real scalar primitives; 240 maps; one owned C; no new child | The exact aligned post-F2 cut and distinct real-family roles are assumptions. |

All costs are local template counts. Address work, control, precision,
recursive child storage, and cover multiplicities need separate bills.
The two storage constructions use the original source logger. They are
not a global admission proof for the changed masked F2 word.

## Reproduce

Use Python 3.10 or later, the standard library, one process, and at least
3 GiB of free space. No Git checkout, network access, or external package
is needed. From this package directory, use a new output directory:

```sh
python3 -I -B replay.py --out /tmp/borrowed-centre-storage-check
```

The final line must be:

```text
PASS_BORROWED_CENTRE_STORAGE_PACKAGE
```

The replay runs nine checks in order. It checks the complete local
borrowed word and source alias, both 512-row storage witnesses, the
inherited unit word, the masked producer and independent review, and the
corrected cleanup producer and independent review. It checks every frozen
source hash before and after execution. The masked word must match its
frozen decompressed payload. Both cleanup output files must match their
frozen bytes. The output directory contains logs and `REPLAY.json`.

The alias checker uses assertions. The replay starts every child with
`-I -B`, with assertions active. Do not add `-O` to a direct alias check.

The package contains only the required members of two historical
archives. Their exact archive and member hashes and Git commits are in
[SOURCE-PINS.json](SOURCE-PINS.json). Extraction was checked against the
full archives during package preparation. A portable replay checks the
member bytes; it does not re-read either full archive.

## Evidence and scope

The two storage reviews reconstruct the actual 482-event schedule. They
check all 69,120 original complete helper occurrences. The dirty check
also checks all 7,526 idle remainder records, full 73-variable phase
polynomials, all selected donor histories, and all cover inverse maps.
The clean check follows all 14,336 owner locations through the changed
schedule. These are complete finite witnesses for their stated schedule.
Their local identities extend to arbitrary values and tensor sizes under
the retained native contracts.

The masked review reconstructs all 26,587 events and all new matrices.
The producer checks the complete word on all 712 local input columns.
The cleanup review reconstructs every block, checks every ADD phase and
all 240 views, checks private-owner lifetimes, and replays all 457 latent
columns with ordered route words.

Meaningful controls reject wrong conjugation, translation, missing jobs,
duplicate owners, a missing swap sign, an old bridge source, wrong mask
order or sign, omitted cleanup blocks, maps on private C, and C values
that survive an owner boundary. See the per-check receipts for each
control.

The replay does not re-run the inherited native child kernels. It does
not check a new global trace for the masked caller, retire its mixed-frame
target code, admit B3, or prove recursive storage and precision bounds.
The full-W application and later two-pair endpoint are excluded. No
matching optimality or global storage lower bound is claimed.

Some frozen notes say that review or publication is pending. Those are
historical statements. Later independent agent reviews are retained next
to the sources. No claim of independent human peer review is made.

## Dependencies and credit

The historical supplier and owner schedule come from the gauge44 and t16
lineage. The exact consumed schedule uses commit
`0a31ad88419a4eebf515d3df4f6732c4e38c0029`; the alias source uses commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.

[PR #1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862)
published the input-only source-group work. Its source logger and local
contract are retained premises here.
[PR #1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969)
published the joint-query work. Its exact matrix and route certificate
are consumed here. Neither contribution is claimed as new in this package.
The recorded source heads are `bb29ea73ad9be9a0c3d53cdcb1d22b2ee9ffe42f`
and `a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`, respectively.

[NOTICE.md](NOTICE.md) and the retained notices preserve predecessor
credit, licenses, and the disclosure of substantial OpenAI Codex
assistance. [SOURCE-PINS.json](SOURCE-PINS.json) gives each original source
path and exact hash. No frozen source was changed.

## Open next questions

A complete use of dirty transport needs a read protocol that cancels the
old donor value. Start with the displayed transport identity and require
the original donor output after every added read.

A global use of the masked cleanup needs the stated aligned cut in the
changed owner schedule. Start with the complete post-F2 role list and
check all owner uses before making a supplier claim. Mixed-frame target
code retirement, B3 admission, recursive storage, and precision remain
separate blockers. This package does not perform that research.
