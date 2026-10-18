# Nineteen temporal gauges: exact finite composition

This package composes the nineteen zero-static helper schedules of PR1369 on the unchanged PR1263 static word. The full menu is the **unique optimum among its 524,288 subsets**, independently in each orientation. This is a fixed-menu result, not optimization over other gauge paths or an improved conditional multiplication bound.

| Complex primitives per orientation | Forward | Backward |
|---|---:|---:|
| PR1263 static background | 136,002 | 136,018 |
| PR1388 L348/L359 pair | 135,202 | 135,218 |
| All nineteen schedules | **134,070** | **134,086** |

The composition saves 1,132 complex primitives per orientation over the reproduced pair, or 1,932 over the static background. Every one of the 194 inserted SCALE macros per orientation is charged. The recursive profile remains `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` and the local positive-prefix ceilings remain 52/68 bits within the inherited 192-bit allowance.

## Reproduce offline

Use Python 3.12 with assertions enabled. From the repository root:

```sh
python3.12 scripts/research_package.py --package research/k8-temporal-menu-composition
```

This registered check uses only the standard library and a temporary result file.
The pinned archive is already part of the repository. To retain the JSON result,
pass a fresh output path outside the package:

```sh
python3.12 -I -B research/k8-temporal-menu-composition/verify.py \
  --output /tmp/temporal-menu-result.json
```

For a relocated package, add `--upstream /path/to/checkout` pointing to a checkout
with the archive identified in [UPSTREAM.json](UPSTREAM.json). The verifier downloads
nothing. It checks package hashes before importing vendored sources, authenticates
the archive and two fixed regular members without extracting files, and constructs
the static background and fixed menu. It then checks every shared ADD correction,
the strict marginal proof, complete invoices, original frames at inserted SCALEs,
unchanged nonscalar events, local payload and all 712 formal scalar columns per
orientation. It compares the result with [EXPECTED.json](EXPECTED.json).

Controls cover zero-menu identity, direct invoices for all sixteen subsets of the
four helpers participating in nonzero interactions, and rejection after deleting
an exactly identified inserted SCALE. Add `--exhaustive` to independently enumerate
all 524,288 subsets per orientation using both Gray-code and least-set-bit
recurrences. The routine proof needs no enumeration; see [PROOF.md](PROOF.md).

Verification commands, outcomes and unrun obligations are recorded in
[VALIDATION.md](VALIDATION.md).

## Scope

The fixed arrays in `MENU.json` were reproduced from the pinned PR1369 deterministic single-coordinate DP and matched every published singleton domain/objective/transition field. The verifier fixes these arrays rather than running a new schedule search. It retains the terminal-restoration convention of PR1369; gauges may remain active across unrelated recursive events. This differs from PR1380's zero-at-every-nonscalar-boundary domain.

The complete scalar endpoint restores arbitrary independent helper dirt and clears all eight private centres. Unchanged recursive event counts and width inventory are **not** fresh native phase, adapter, controller or hosted-supplier admission. The current generic adapter rule increases its local allowance by 3,104 adapters relative to the static background, or 2,240 relative to the pair. No compensating adapter discount is proved; see [NATIVE-BOUNDARY.md](NATIVE-BOUNDARY.md). Physical emission, complete owner invoice, global precision/tape and all-size transfer remain separate. No new κ or current numerical lead is claimed.

The selected record at the pinned base remains PR1094, `836330098538459/500000000000000000`. This package is a finite circuit result on its retained local word, not a replacement for that admitted record.

Credit the authors of PR1369/1388 for the schedules and pair comparator; PR1263 for the static background; PR1259 for temporal-gauge methods; PR1161 for formal scalar replay/invoice; and PR696 and the inherited supplier/compiler lineage for the primitive vocabulary. Original vendored source bytes and notices are retained. This composition was prepared for George Lydakis's contribution with substantial OpenAI Codex assistance.

## Overlap and provenance

The comparison is to the pinned [PR1388 pair](https://github.com/CrocSwap/integer-mult-bounds/pull/1388),
using [PR1369](https://github.com/CrocSwap/integer-mult-bounds/pull/1369)'s nineteen
zero-static schedules and [PR1263](https://github.com/CrocSwap/integer-mult-bounds/pull/1263)'s
static background. [VENDOR-SOURCES.json](VENDOR-SOURCES.json) records immutable
commits, source paths, Git blobs and SHA-256 values; vendored source bytes and
notices are preserved. [SOURCES.json](SOURCES.json) records the registered upstream
inputs and provenance.

The overlap scan at 2026-10-14 00:15 UTC covered 866 open PRs, 123 discussion records
and 325 local package notes, with complete pagination and no reported warnings.
It found related pair and nonzero-static work, including PR1397, PR1398, PR1376,
PR1385 and Discussion1163 comment18911723. This package does not compose those
nonzero-static schedules. No identical all-nineteen composition was found in that
scan; this is not proof of novelty or a claim to the best scalar circuit globally.

## Open next questions

- Can this scalar program receive complete native, adapter and controller admission
  with a smaller total invoice? First bind its emitted operations to those interfaces
  and establish any adapter discount. The present generic allowance increases.
- Can a joint optimization over other temporal paths improve this fixed menu?
  First define an explicit domain and comparator with the exact unit discount.
  The proof here establishes optimality only among subsets of these fixed schedules.
  Such work would still need a changed recurrence or supplier interface to advance κ.
