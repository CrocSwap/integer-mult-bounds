# Attaining the coupled-carrier packing cap at T740

Jeremy Diviney, with substantial OpenAI Codex assistance. Apache-2.0.

**Finite checks and the complete composed release pass.** A new, literal
145-row exchange attains the fixed-inventory packing cap of dcharb78's
[PR3133](https://github.com/CrocSwap/integer-mult-bounds/pull/3133) words:

```
kappa = 0.001729777494678597011886 - 10^-46 - 10^-70
root in [0.0017297774946785970118869,
         0.0017297774946785970118870]
```

The gain over Gonzalo Mier's more precise, unchanged-T74
[PR3143](https://github.com/CrocSwap/integer-mult-bounds/pull/3143) claim is
approximately **1.4052734766776475e-9**. `BASELINE-PR3143.json` retains its exact
rational claim at `dcfaf1d1a7cfebaab22b95776a36a543bc684d50`. The PR3133 source
head is `51eb9c4ee9e4722010d308aa3309e039d3940cc2`. Neither pending claim is
described as a selected or independently admitted frontier.

This contribution is the changed-inventory packing repair, its deterministic
generator and full source/word/allocation binding. It uses Nick Petalas's
existing ten-copy interleaving method, differential checker and cap proof
(PR3024), and the three-allocation-argument integration pattern (PR3030).
PR3133's local words, ordered widths and source validators are unchanged.
The old PR3024 exchange cannot simply be reused on this different inventory.

The pre-submission overlap refresh found Gonzalo Mier's earlier
[handoff #3145](https://github.com/CrocSwap/integer-mult-bounds/discussions/3145)
and Hiroki Kumazaki's
[stopped transport attempt](https://github.com/CrocSwap/integer-mult-bounds/discussions/3145#discussioncomment-18992630).
That attempt found no matching preimages for the old journals and requested a
new journal generated from the changed fill. This package provides that new
journal, constructed before reading that handoff in detail; it does not dispute
the old-journal failure or claim priority for the T740 objective. No fresh
flow census is required by this particular deterministic repair. PR3143's fill,
provider bytes and both words equal the pinned PR3133 inputs. The complete run
uses PR3133's original endpoint precision and strictly exceeds PR3143's more
precise T74 result.

## Exact exchange

Start with ten interleaved copies of PR3133's literal T74 fill. Its three
non-tight bins per copy are two `48:[4,8,9,9,9,9]` bins and one `48:[9]` bin.
Use 25 compatible `32:[9,9,9]` donor bins:

```
20 * 48:[4,8,9,9,9,9] + 10 * 48:[9] + 25 * 32:[9,9,9]
 -> 20 * 32:[4,9,9,9] + 5 * 32:[8,8,8,8]
    + 21 * 48:[9,9,9,9,9] + 9 * 48:[]
```

Move the twenty width-4 roles into twenty donor bins. Move the twenty width-8
roles into five other donor bins, releasing fifteen width-9 roles. Repack those
fifteen and the ninety width-9 roles in the old 48-bins into twenty-one groups
of five. Nine 48-bins become empty. `construct.py` chooses concrete legal bins
deterministically; `EXCHANGE.json` binds every changed row to its exact preimage.

The exchange changes 145 roles in 55 bins and touches 123 calls. The idle-count
delta is `{1:+20, 3:+21, 5:-25, 39:-10, 48:+9}`. The capacity multiset and each
helper width are preserved. The unchanged full owner checker checks all
**2,717,280** rows, including unchanged bins and calls. Chronological source
availability, compact prefixes, non-overlap and same-call physical-family
exclusion are required; the aggregate identity alone would not suffice.

## Complete bill and cap

There are 740 replicas, 6,660 invocations and 408 helpers per invocation.

| Component | Exact rank counts |
|---|---|
| Local, per invocation | `{1:2433, 2:724, 3:228, 4:102, 5:20, 8:8}` |
| Idle, all replicas | `{1:173160, 3:48951, 5:13875, 48:282569}` |
| Total | `{1:16376940, 2:4821840, 3:1567431, 4:679320, 5:147075, 8:53280, 48:282569}` |

The total equals 6,660 local bills plus the idle bill, with rank mass
`65088 * 740`. Both literal words derive the ordered helper inventory
`{4:26, 5:2, 6:18, 7:50, 8:99, 9:213}`. The exact forward and dual operator
audit checks 632 independent inputs for each word, frames, restoration and
literal inverse cleanup.

`cap_check.py` adapts Petalas's exact rational dual proof to this inventory and
local bill. It enumerates all 2,551 patterns and proves strictly positive
reduced cost for 2,539 throughout the root bracket; the same twelve patterns
are tight. The feasible primal basis is PR3133's retained `RELAX-CAP.json`.
Our idle bill is exactly 740 times that basis's idle bill, so the attained
moment and fractional cap are identical, rather than merely close numerically.

The tight-pattern residue identity now reads
`20 * N_(48:[9,9,9,9,9]) = 1323 * T`. Since `gcd(1323,20)=1`, any cap-attaining
integral packing requires `20 | T`. The first multiple of the retained T74
chronology satisfying this is 740. This is not a proof that every possible
chronology needs 740 replicas.

All **91** private cleanup buffers are charged. Physical stock is
`896*740 + 408 + 8 + 91 + 2 = 663549`, compared with PR3133's 66,813.
The larger fixed stock is a material cost of this small exponent improvement.
The complete strict replay rebuilt the actual prefix and outer invoice: the
prefix requirement is 1,479 bits, within the paid 2,048-bit payload.

## Reproduction and evidence

The bounded checks use Python 3.12 and its standard library:

```sh
python3 -B scripts/research_package.py --package research/coupled-carrier-cap740
```

`verify.py` checks the words, all owners, complete moment, exact cap, and stored
release bindings. `test_allocation.py` checks regeneration and semantic failures
(stale or duplicate edits, lost moves, unavailable windows, overlaps, physical
family collisions, unpaid prefix holes and invalid cap data). `test_bindings.py`
checks recipe substitution, stale input rejection, compression portability and
refusal of disabled assertions. Stored receipt validation is not a fresh native
or outer replay. Regenerated fills are compared by their full decoded payload;
immutable source containers retain exact byte hashes.

For a complete replay, fetch the pinned Git objects in `FETCH.txt`, install
`requirements-full.txt` in a Python 3.12 virtual environment, then use a fresh
output directory:

```sh
nice -n 15 ionice -c 3 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -B research/coupled-carrier-cap740/reproduce.py \
  --repo . --work /tmp/coupled-cap740-new --jobs 2
```

The default bootstraps the retained parent fresh. An explicit `--retained PATH`
reuses the predecessor's authenticated parent/native cache, while rebuilding
both current providers. `--dry-run` exports exact sources, materializes every
row and checks the recipe; it does not claim a release. The full controller
changes exactly `--fill`, `--order`, and `--dispatch` in PR3133's final admission
command. All scientific source stages remain unchanged.

The recorded full run uses an authenticated retained cache. All eleven source
stages passed in 30.1 minutes with two low-priority single-thread audit
workers. Both current native providers were rebuilt; two retained native
providers and the retained parent were reused explicitly. A full fresh retained
bootstrap was not rerun in this session. Exact logs, raw receipts and scope are
in `evidence/`; `RUN.json` records the executed command. The public exporter,
materializer and recipe dry run also passed independently of this execution.

## Scope and expansion decision

This is a conditional finite supplier and outer certificate. The inherited
all-size, compiler, physical/native and analytic multiplication-theorem
obligations remain. No selected record is changed. An archive merge or passing
CI would not establish independent scientific admission.

The explicit user task was to exceed the strongest reported repository claim.
Before expanding, we reran Arham Tahir's code-disjoint PR3136 coupled-carrier
local audit successfully, pinned both providers and their complete bill, and
bounded the task to the demonstrable packing gap. The changed inventory makes
the old cap witness inapplicable. The acceptance test requires every role,
all buffers and the complete native/physical/prefix/outer release; partial
checks cannot support a released endpoint. See `TASK.json` for the evidence and
obligation ledger. Failed preliminary operator-valued probes are not claimed
as a general obstruction or a new contribution here.

## Open next questions

- Independently replay this exact source and allocation and inspect the larger
  physical bill before any frontier adoption. Maintainer scientific review and
  inherited theorem obligations remain; the first step is the explicit full
  reproduction above.
- Can a different chronology realize the same cap with fewer replicas? The
  residue certificate permits multiples of 20 but does not construct them.
  First build a legal owner-window model at T20; reject candidates that fail
  source availability or pay back the saving in physical/prefix costs.
- Further exponent improvement needs changed words, widths, capacities or a
  different moment model: this fixed-word packing relaxation is attained.
  Start with a concrete paid change and audit both its producer and consumer
  before another downstream packing search.

## Credit

The coupled folds, literal T74 fill and changed-inventory cap are dcharb78's
PR3133. The underlying joint rank-7 words and relaxation tools are Marius-Paul
Dumitrean's PR2979/2942/2930, building on Jeremy Kothe's rewrites/preload chain,
Mason Hale's paired extension, Jeremy Diviney's paired-extraction certificate,
Yiyang Lu's shared-kernel/flow work, Dugongue's packing lineage, Tekalign's
owner/admission checks and icekylinx's exact operator audit. Petalas supplied
the PR3024 lift/dual argument and PR3030 integration pattern. Gonzalo Mier's
PR3143 supplies the precise comparison claim; Arham Tahir's PR3136 supplied
the separately replayed local audit. Retained source notices and full earlier
credits are in `vendor/PR3133-NOTICE` and `vendor/PR3133-CREDITS.md`.

The new deterministic exchange, integration and verification work are by
Jeremy Diviney with substantial OpenAI Codex assistance. No independent human
or formal-kernel review is claimed.
