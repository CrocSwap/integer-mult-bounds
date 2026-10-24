# PR4633 audited replay: numerical replay passes; supplier contract fails

**Do not admit the claimed supplier at `b390d64abfcdba1a3816b86fc763cbc95d43c12c`.**
The submitted checks reproduce the reported BIT and complex numerical screens.
They do not establish the claimed BIT supplier or outer saving. This audit
supplies exact counterexamples to the rational quotient interpretation and the
retained main-port contract, and a false-positive mutation of the BIT verifier.
No selected result, theorem, supplier or new kappa is certified here.
Before publication, GitHub reported PR4633 **closed without merge** at
`2026-10-22T13:41:17Z`, with the same head. This audit did not close it and does
not infer a reason for closure. No open-queue scheduling entry is created for a
closed submission; the central ledger records the negative review and closure
observation separately from mathematical acceptance.

## Current-head delta: three-dimensional kernel

The PR advanced from `b2998bacd50d57c301fe67c5392054440c42398c` to
`b390d64abfcdba1a3816b86fc763cbc95d43c12c` during review. Nine BIT files changed;
the complex package is byte-identical. The current BIT uses kernel basis
`[150,102,255]` and its registered replay reproduces **0.032249423394893**.
The PR title/body still describe the older one-dimensional result.

All three principal objections survive, with stronger concrete witnesses:

* The three-dimensional binary kernel erases **41 rational entrance lines
  spanning all eight rational dimensions**. A rational linear map with kernel
  dimension three cannot have that action. `verify_latest.py` reconstructs
  the quotient using canonical cosets, independently of the author's
  annihilator algorithm, and checks every rewritten record.
* All 111 ports still fail the inherited `(7,7)` transport requirement:
  **8 have `(7,8)`, 41 have `(8,4)`, and 62 have `(7,4)`**. Main rank mass is
  now **1294**; the invoice still books the unchanged rank-seven ladders.
* Zeroing all **2,184** positive MOVE charges still produces a full author
  `PASS` with **kappa 0.25**. This version adds `frame_bases`, but the verifier
  never reads them: replacing **every basis with the empty list** produces
  exactly the same successful result as the original artifact.

The complete new scan's candidate domain is all **1,940 combinations of one
through four elements of the submitted 15-element list**. Its nominal random
augmentation is never entered because 1940 is already greater than 600. This
is the full submitted finite domain, not an exhaustive enumeration of all
subspaces of dimensions two through four. The serial delta replay and results
are included with the first-head evidence in `REPLAY.json` and `evidence/`.

The complete updated scan also **refutes the plateau/optimal-dimension claim**:

| Listed kernel size | Candidates | Accepted | Distinct accepted screen values | Best numerical screen |
|---|---:|---:|---:|---:|
| 1 | 15 | 15 | 15 | 0.012401086416 |
| 2 | 105 | 105 | 71 | 0.021804306829 |
| 3 | 455 | 438 | 145 | 0.032249423395 |
| 4 | 1365 | 1122 | 128 | 0.042304306669 |

The README/PROOF claim 445 accepted triples, all at the same value; the exact
submitted code instead returns 438 and 145 distinct values. Triple `[240,7,9]`
prices at `0.001073869184`. Four-dimensional basis `[150,102,255,165]` prices
at `0.042304306669`, contradicting the assertion that dimension four falls
back to `0.017525188018`. These are discrepancies in the numerical experiment,
not newly established suppliers or improved bounds.

`LATEST-SOURCE-INVENTORY.json` and `sources-current/` freeze the revised BIT;
`EXPECTED-LATEST.json` records its independent counterexamples. The short
registered audit runs both historical and current checks. The detailed
one-dimensional findings below remain evidence about the first reviewed head,
and are not silently attributed to the replacement artifact.

The user assigned a full audit of [PR4633](https://github.com/CrocSwap/integer-mult-bounds/pull/4633).
The observed base was `fbc9ea0249746acca4f504d4fda2b84e0e36cf0d`.
The actual diff contains **21 added files in two packages**, including the
complex predecessor; the PR body's statement that it is one package is stale.
[SOURCE-INVENTORY.json](SOURCE-INVENTORY.json) binds every changed file, mode,
blob and SHA256. Exact submitted bytes are retained under `sources/` so that
subsequent author edits cannot change this audit. The three registration files
in each snapshot have `.source.json` names to avoid registering duplicate jobs.

## Findings

### P1: the BIT builder substitutes binary geometry for rational projectors

`research/bit-ambient-quotient/build.py:44-51` reduces the source annihilator
rows modulo two, then takes a binary nullspace. The inherited native source
instead constructs **rational orthogonal projectors** from `frames.json`'s
`B` rows: `mixed_productive_bit.py:263-276`. In particular,
`bit_native_binding.py:75-99` binds the actual data ports to
`P_q = q q^T / 4` and `I-P_q`.

The following zero-based source ports give a short exact counterexample:

```
port 8: q = (0,1,1,0,1,0,0, 1)
port 9: r = (0,1,1,0,1,0,0,-1)
```

They are linearly independent over the rationals. Their projector entry `(1,7)`
is respectively `1/4` and `-1/4`. Both become binary mask 150 and are sent to
zero by the proposed kernel. No rational linear map with a one-dimensional
kernel can annihilate both. In fact, ports **8 through 13** all disappear and
their rational span has **rank four**. This also persists over odd
characteristic for the two-vector witness; coefficient-stream XOR does not
justify reducing the native rational coordinate geometry modulo two.

Reduction already identifies the 636 source frames into **157 distinct binary
subspaces before quotienting**. All 636 individual dimensions happen to be
preserved, and the binary MOVE/COPY containments pass. Those positive controls
are explicitly checked: the objection is not a failed binary rank calculation.
It is the missing native interpretation. A new binary abstraction could be
studied separately, but requires a realization and interface proof; it is not
the claimed one-dimensional quotient of the retained rational supplier.

### P1: the invoice retains main output credit from an unproved controller

The inherited BIT controller explicitly requires a local invocation
`D_Bs S(D_P)` with **rank-seven `B_s`** on both data fields
(`mixed_productive_bit.py:131-160`). The native binding checks actual entrances
`(P_q, 0)` and exits `(I, I-P_q)`, deriving `D_I D_P = D_(I-P_q)`.
There is therefore an existing endpoint contract in the tree; it is not a
future maintainer choice inferred only from `inventories()`'s text reads.

For the submitted artifact the two main transport widths at each port are:

| Width pair | Ports |
|---|---:|
| `(7,6)` | 101 |
| `(7,8)` | 4 |
| `(8,6)` | 6 |

**None of the 111 ports has the retained `(7,7)` pair.** The new local main
rank mass is 1457 instead of 1554. Yet `bit-ambient-quotient/verify.py:72-82`
still assigns every main ladder the old `1 + 7 * stages` output credit and
prices the old rank-seven idles. Padding helpers to rank eight establishes
their boundary dimension; it does not prove the missing rank-seven main map.
Replacing only `controller.py:152`'s surplus assertion cannot repair this.
Derive the new physical controller, boundary routes, diagonal outputs and paid
invoice before making a supplier claim.

The included complex package has the analogous width mismatch: 168 of 224
mains have width seven, but its invoice still uses uniform block-eight ladder
credit (`complex-ambient-quotient/verify.py:104-115`). Logical endpoint replay
against the submitted word's own final frames does not supply that bridge.
The earlier [PR4604](https://github.com/CrocSwap/integer-mult-bounds/pull/4604)
identified the endpoint question for kernel 511. This audit treats the actual
kernel-153 complex dependency and kernel-150 BIT submission.

### P1: the independent BIT verifier accepts unpaid positive-rank MOVEs

`bit-ambient-quotient/verify.py:92-99` trusts the record's `f` tariff without
checking it against the source and destination dimensions or native projectors.
Its artifact stores only frame IDs and dimensions, not bases/projectors.
The inherited `audit_local` additionally checks exact projector nesting and
`dimensions[new]-dimensions[old] == rank >= 0` before symbolic replay; those
checks were omitted from the new verifier.

The audit changes all **2,802 positive MOVE tariffs to zero**, preserving
records, frame IDs, dimensions and boundaries. The complete submitted
`main()` still produces `PASS_BIT_AMBIENT_QUOTIENT`, now with paid profile
`{6:9}` and **kappa 0.25**, the search ceiling. This is a false acceptance,
not an improved construction. The audit's independent dimension check rejects
all 2,802 altered charges. As a separate negative control, the author replay
does reject a deliberately broken MOVE entrance, demonstrating that the test
really executes it. Store/authenticate the geometry and recompute each tariff.

### The outer claim remains unproved even after these repairs

The README explicitly acknowledges that ordinary BIT admission has not been
raised. `query-thinned-controllers/verify.py:164-190` performs strictification,
cover loss, the atom/ordinary/admitted conversion, and the complete outer ledger.
Taking the minimum of two floating-point screen crossings is not that chain.
The new package supplies none of the replacement parameters or strict rational
margin checks. The disclosed gap must also constrain its headline and TASK
claim. The selected record at the audit base remains the conditional `0.0023`.

## Replay and evidence

`REPLAY.json` records the environment, commands, sampled resource limits,
coverage and results. Logs and complete per-kernel results are in `evidence/`.
The two registered Python 3.12 replays pass; rebuilding all three compressed
word/program artifacts reproduces the committed bytes (and decompressed JSON).
The BIT scan is run over every kernel 1..255, and the complex scan over every
kernel 1..511, using each submitted `price()` unchanged **serially**, in place
of its eight-process driver. A sampled 1 GiB process-group RSS watchdog and
explicit timeouts apply. Author PASS status is recorded as executable evidence,
not as independent acceptance of its mathematical interpretation.

Additional native controls pass: the original BIT `audit_local` validates its
rational projectors and nested transports, and all **2,101 distinct complex
climb/helper-boundary edges** lower with their stated Fourier rank in both
orientations, with exact absolute-phase recipe decoding. These controls support
the scoped local evidence; they do not supply the missing main-port controller
contract. The BIT control uses the retained `joint_pair_dag` dependency under
`kappa-0023-productive-jobs/dependencies/`; the first direct import failed at its
obsolete historical path, and the explicit path correction and retry are logged.

| Submitted scan | Replayed candidates | Accepted | Best kernel | Best numerical screen |
|---|---:|---:|---:|---:|
| BIT | 255 | 255 | 150 | 0.012401086416 |
| Complex | 511 | 32 | 153 | 0.015637149091 |

Two secondary summary claims do not reproduce. BIT kernel 111 yields
`0.001862148210`, contradicting the claim that all 255 land between 0.0122 and
0.0124. The accepted complex kernels have varying main masses/surpluses:
kernel 511 has main mass 1680 and surplus 2768, whereas kernel 153 has 1624
and 3776. Thus the complex README's statement that all 32 have 1624/3776 is
also false. Neither correction changes which kernel wins the submitted screen.
The complex `VERIFY.json` prose also retains older kernel results; executable
checks and the captured logs are used for the actual replay assessment.

The scoped audit can be replayed without network access:

```sh
python3.12 -B scripts/research_package.py --package research/pr4633-quotient-contract-audit
```

`verify.py` authenticates the input bytes, reconstructs the entire BIT quotient
and all rewritten records independently, checks rational ranks/annihilators,
proves the erased-line and port-width witnesses, and executes the submitted
positive and mutation controls. `EXPECTED.json` pins that receipt. Direct
execution also works in a source export, with all declared inputs present.
The frozen author code writes only into temporary directories during this
scoped replay; it does not modify the vendored artifacts.

For the full author replay, fetch the reviewed SHA into a detached worktree,
run each package's `scripts/research_package.py --package ...` command and the
BIT `build.py`, then use the retained `evidence/scan_serial.py` and
`evidence/run_bounded.py` from that worktree. The scripts save logs beside
themselves. The command arrays in the receipts identify precisely what ran.
This full replay is separate from the short registered counterexample test.

This review covers all changed files and the relevant supplier interfaces.
It is not a cold replay of the unchanged selected multiplication construction,
a Lean verification, or a proof that no different quotient-based construction
could work. No unrelated historical suite, Docker build or hosted workflow was
manually dispatched.

## Open next questions

1. Supply native rational projectors and a proved controller interface for a
   repaired BIT construction. Begin with the two explicit erased lines and
   one of the `(7,6)` ports. Author revision is required.
2. Make free-MOVE mutation fail in the author verifier, using geometry-derived
   ranks and an independent required endpoint. A replay of scalar values alone
   cannot settle the physical interface.
3. After valid suppliers exist, derive strict rational supplier margins,
   ordinary BIT admission and all outer-ledger parameters. No corrected kappa
   follows from this audit alone.

## Attribution

DaysSky authored PR4633 and the included complex quotient work (PR4629 and
PR4596). PR589's retained E8 word credits DreamingOfClouds, eumemic and its
cited lineage. The complex input retains PR4470 and predecessor attribution.
Ryanson Jonathan's PR4604 is the earlier endpoint-frame audit. This independent
audit also overlaps [Rohan Arun's concurrent per-port-contract comment](https://github.com/CrocSwap/integer-mult-bounds/pull/4633#issuecomment-6341849407),
discovered during the final live refresh. The rational-field counterexamples,
verifier mutations, both-head full scans and native edge replay here provide
additional reproducible evidence. This audit was prepared for Cinna Davis with
substantial OpenAI Codex assistance.
All source notices are preserved; Apache-2.0. No independent human or formal
kernel verification of the multiplication theorem is claimed.
