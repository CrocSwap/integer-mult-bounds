# Independent reproductions and audit notes: #207, #202, #197, #199

Snapshot: 2026-10-09, runs between 13:43Z and 17:33Z; PR heads re-read at 17:35Z.
Repository base at the time: `main` = `3b6b66891c0ac888521cf591fe306c6286601d4f`.

This directory records independent replays of four open submissions, with
pinned heads, exact commands and outputs. It is a reproduction report, not a
review disposition and not an acceptance of any bound. A passing verifier is a
finite certificate check under the inherited conditional interfaces. It is not
a formal verification of the multiplication theorem. Every κ below is
conditional, as in the submissions themselves.

Each item carries one of three labels:

- **reproduced**: the submission's own verifier ran unmodified at the pinned
  head and printed the claimed value;
- **not reproduced**: the submission's own verifier failed in our environment;
- **audit finding**: an observation from reading the sources or from a
  read-only diagnostic. It is not a claim of mathematical error.

## Environment (all runs)

- Linux x86_64 (kernel 6.18.33.2, WSL2), Ubuntu 24.04.5 LTS.
- CPython 3.13.16 in a virtual environment with numpy 2.3.5 and scipy 1.17.0.
  These equal the pins in the packages' requirement files. No package was
  installed or upgraded for these runs.
- Fresh clones; heads fetched from `pull/<n>/head` and checked out detached.
  No source file was modified. All verifiers were run with `-B`.
- Wall times come from `/usr/bin/time -v` or from bash `time`. Peak memory is
  given where `/usr/bin/time -v` recorded it.
- One control run used CPython 3.12.3 (system interpreter) with the same numpy
  and scipy. It is reported only under item 2.

## Summary

| Item | PR | Head run (now) | Command | Exit | Wall | Printed κ | Label |
|---|---|---|---|---|---|---|---|
| 1 | [#207](https://github.com/CrocSwap/integer-mult-bounds/pull/207) | `cd14825023b7` (unchanged) | `python -B research/coordinated-crossover-pr200/verify.py` | 0 | 2:22.76 | 1366380910073/2000000000000000 = 6.831904550365e-4 | reproduced |
| 2a | [#202](https://github.com/CrocSwap/integer-mult-bounds/pull/202) | `8d8d67bcf69c` (unchanged) | `python -B research/paired-cube-diagonal-bit-168/verify.py` | 0 | 2:36.64 | 166261725903847/250000000000000000 = 6.65046903615388e-4 (package's own κ) | reproduced |
| 2b | #202 | `8d8d67bcf69c` (unchanged) | `python -B research/source-assisted-v4/verify.py` | non-zero (AssertionError) | 1:00.09 | none (fails before printing) | not reproduced; audit finding |
| 3 | [#197](https://github.com/CrocSwap/integer-mult-bounds/pull/197) | `8c5e1cf07c23` (unchanged) | see item 3 | 0 | 2:01.30 | 135216063303877/200000000000000000 = 6.76080316519385e-4 | reproduced; audit finding |
| 4 | [#199](https://github.com/CrocSwap/integer-mult-bounds/pull/199) | `5c1fb8346615` (current head) | see item 4 | 0 | 0:10.25 | none (diagnostic; output sha256 `30418cac…a61c` = committed) | reproduced |

Full SHAs, interpreter and package versions per run are in
[receipts.json](receipts.json).

## 1. #207: reproduced

- Head `cd14825023b75af4f5919a30e5e6d548b6ade5bc`. Its merge base with `main`
  is `3b6b66891c0ac888521cf591fe306c6286601d4f`. The head is unchanged at 17:35Z.
- Command, from the repository root, as in the PR body:
  `python -B research/coordinated-crossover-pr200/verify.py`.
- Exit code 0; wall time 2:22.76 (17:05:22Z to 17:07:45Z); peak RSS
  2,155,372 kB. `git status --porcelain` was empty after the run.
- Final lines printed:
  `PASS full offline bit/frame/bank/chart/complex-lift/contract replay, independent paid moments, 47 inequalities and controls; kappa=1366380910073/2000000000000000`
  and `PASS immutable manual-upload package; no network, git, or publication required`.
  Intermediate records include `PASS_ADMITTED_FRAME_BANK_COMPOSITION`,
  `PASS_ALL_ACTUAL_GAUGE_CHARTS_AND_ROUTING_BILL`,
  `PASS_LITERAL_DISTINCT_NORMALIZERS` and `PASS_EXACT_47_CONSTRAINT_ASSEMBLY`.
- The printed κ equals the PR's claim exactly.
- Note: the complex-lift step printed `certificate_sha256`
  `72a9626394aff05457ba5d25fc312608effba611f1f184ad8a6ddf186c7b150f`. The
  verifier does not compare this hash. `verify_inner.py:23` asserts only that
  `exact_scalar_program_sha256` equals the committed value
  (`3b4e671d7c6630570b04788bb2c81629e2c52f8dc2fcc5805952f0b403921027`), and
  that assertion passed. This design matters for item 2b.

## 2. #202: bit package reproduced; headline verifier not reproduced here

Head `8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d`, tree
`4d07f3f18343da5a0f474d6d830afe64c0c18505`. The head is unchanged at 17:35Z.
No CI checks are reported on this branch.

**2a. Bit package (reproduced).**
`python -B research/paired-cube-diagonal-bit-168/verify.py` exited 0 in
2:36.64 (peak RSS 2,194,084 kB). The working tree was clean before and after.
It printed
`PASS paired-cube-diagonal-bit-168 kappa=166261725903847/250000000000000000; complete complex and bit words, 47 constraints, seven margins, and 21 assembly controls.`
This κ is the package's own assembly, not the #202 headline. The run
regenerates the bit certificate that #202's assembly reads, and the script
asserts that the regenerated result equals the committed `certificate.json`.

**2b. Headline verifier (not reproduced in this environment).**
The 6.768823e-4 headline is checked by `research/source-assisted-v4/verify.py`.
In our environment this verifier stops at `verify.py:162` with
`AssertionError: Canonical certificate does not reproduce`, after 1:00.09.

The read-only diagnostic [certificate_diff.py](certificate_diff.py) calls the
PR's own `build()` and compares the result leaf by leaf with the committed
certificate. Exactly 7 leaves differ:

| Leaf | Built here | Committed at `8d8d67b` |
|---|---|---|
| `/lift_certificate_sha256`, `/lift/certificate_sha256`, `/complex_profile/exact_lift_certificate_sha256`, `/assembly/construction_receipts/complex_lift_certificate_sha256`, `/complex_profile/proof_chain_sha256/…/.work/lift.certificate.json.gz` | `1d81a79bda88…9ef2` | `462521350b4f…7ee0` |
| `/complex_profile/proof_chain_sha256/…/.work/lift.json` | `c41fee34c5c6…` | `89b0d949852a…` |
| `/assembly/source_sha256/complex` | `7374c75b7d6e…f0cb` | `b80de5b00f75…e3a3` |

Every other leaf is equal, including κ = 6768823/10^10, the complex saving,
the bit effective saving and the assembly records. Two independent builds in
fresh clones (15:12Z, and 17:25Z with the script as committed here: exit 0,
1:01.63) gave identical values. In this environment the build is therefore
stable from run to run.

Observations (audit findings, read-only `git show` / `git diff`):

1. #194 at `a8c87783785be6fe20c4a8bb2ac4b3eec295a179` commits exactly the
   values built here (`1d81a79b…`, `c41fee34…`, `7374c75b…`). Its
   `source-assisted-v4/verify.py` passes in the same environment (exit 0,
   0:57.89). #194's CI also reports a passing `source-assisted` job.
2. Between `a8c8778` and `8d8d67b`, the `SOURCE.json` pins change only for the
   bit-certificate path, `assemble.py`, `pin_sources.py`, `NOTICE`,
   `PROOF.md` and `README.md`. The pins of `verify.py`, `contract_v4.py`,
   `source_aligned_local_v4.py` and `data/*.json` are unchanged, and
   `research/source-assisted/` is unchanged. `exact_scalar_program_sha256`
   (`3b4e671d…1027`) is identical in both committed certificates.
3. Control run with CPython 3.12.3 (same numpy and scipy): #194's own
   `source-assisted-v4/verify.py` also fails the same assertion (exit 1,
   1:05.71). Which leaves differ under 3.12.3 was not recorded. The canonical
   lift serialization therefore depends on the interpreter, at least between
   3.12.3 and 3.13.16.

Reading: the pinned complex-lift inputs did not change from #194 to #202, yet
#202's committed lift hashes differ from #194's. Our environment reproduces
#194's. The most likely explanation is that #202's lift was regenerated in an
environment whose serialization differs, for example in the interpreter
version. We have **not isolated** the cause and do not claim a defect in the
mathematics of #202: κ and all other non-hash leaves are reproduced. Two
remedies seem possible, at the author's or maintainers' discretion. One is to
record the reference interpreter version and regenerate the canonical
certificate in it. The other is to compare the lift through
`exact_scalar_program_sha256`, as #207's verifier does (item 1).

#207 consumes #202's complex supplier at `8d8d67b` and passes (item 1). This is
consistent with the reading above.

## 3. #197: reproduced, with its named proof obligation

- Head `8c5e1cf07c23d843642bf2d4c76f882669edc43f` (tree
  `98ee8c8e5c0f2214a9250f8390fbffea11ba1652`), unchanged at 17:35Z. No CI
  checks are reported on this branch. The pinned unmerged dependencies were
  checked out as separate worktrees: #187 at
  `201737a1ec4f936e166e2481fb9e88104cb2ccc7` and #193 at
  `187e1010ac8b259af8e9b5166f68b64bc27b4b47`. Both heads are unchanged.
- Command, as in the PR body (with our worktree paths):
  `python -B research/packed-source-assisted-bit/verify.py --complex-root <#193 worktree> --bit-root <#187 worktree> --full`.
- Recorded run, in a fresh clone: exit code 0; wall time 2:01.30 (17:30:47Z to
  17:32:49Z); peak RSS 594,180 kB as reported by `/usr/bin/time -v`; stderr
  empty. `git status --porcelain` was empty before and after regeneration. The
  committed `certificate.json` (sha256
  `c18fe983eb863661a69b0c2d89771acf9d11b7f460b1b04afcac6f2fea799886`) is
  therefore regenerated byte for byte. An earlier run in another clone gave the
  same output in 1:35.68; its exit code was not captured.
- 8 PASS records: `PASS source-assisted-v4 kappa = 103873/156250000`,
  `PASS 1733 immutable source pins`,
  `PASS actual emitted histogram and scalar guard; …; 47 constraints,7 margins,8 controls …`,
  three JSON records with `"status": "PASS"` (frames, emitted word, F2 scalar
  map with three negative controls rejected),
  `PASS literal emitted BIT word, conservative geometry, paid histogram, scalar count, all-column forward/reflection and mutation controls`
  and `PASS exact packed profile, two moment engines, finite leaf composition, 47 constraints and seven margins`.
- Printed `conditional kappa = 135216063303877/200000000000000000`
  = 6.76080316519385e-4, equal to the PR's claim. This is 1.2957% above #194's
  1668581/2500000000.

Audit finding (reading, not a counterexample): the removal of the 6,600
rank-60 exterior children rests on the bank-endpoint identity of `PROOF.md`
§4. By the PR's own words, its finite controls cover "all 144 formal columns
over Z/9, Z/25 and Z/125 … These checks support the identity above; they do not
simulate the full cover or prove the inherited Clifford interface"
(`PROOF.md:95-98`). The identity on the full cover therefore remains a
paper-proof obligation. The package also depends on the unmerged #187 and #193
checkouts, so it is not self-contained.

What remains useful now that #205 and #207 report higher κ:

- #205 (draft, `95c58706ad23`) states that it applies #197's completed-bank
  packing and reuses or adapts its code. It removes the same 6,600 rank-60
  exterior children. #207 cites #197 for its three-level bootstrap. This
  reproduction is an independent data point that the reference implementation
  of the packing regenerates exactly from pinned inputs.
- The proof obligation above carries over to any construction that removes
  these children by the same identity. We did not assess whether the
  full-column bank checks of #205 or #207 discharge it for their own words.

## 4. #199: donor-reuse diagnostic reproduced byte for byte

- Run in a fresh clone at the current #199 head
  `5c1fb8346615968844bc182a5376c399109670ca` (tree
  `f08f784c50504ace4fa659867e954b18210851a1`), with the #189 package at
  `0a4091175b3981267a97a62ab7492cb9ba528916`. `research/paired-cube-bit` was
  extracted from #189 as well, because the #189 package imports it.
- Command, from `research/bit-leaf-bootstrap-189`:
  `python -B bit_reuse_maximal.py --package <#189 checkout>/research/paired-cube-twin-local-168 --out <file>`
  (`bit_reuse_maximal.py` sha256
  `91792e33ff057080c91369b788c88b9cc01e1df6ce2bcd173e67d68132cd4a61`).
- Exit code 0; wall time 0:10.25 (17:30:48Z to 17:30:58Z); peak RSS
  553,200 kB. The working tree was clean after the run.
- Output: gauges 3960, pairs 1760, unpaired 2200 (birth-frame dimension 20),
  8628 distinct donor end frames, 220 unpaired birth frames, of which 0 contain
  a donor end frame; verdict "no unpaired gauge can receive a donor". The output
  sha256 `30418cac689093de5b4d3cb7d6eeae450f8a74de5be7d66cc9be6087ed3ea61c`
  equals that of the committed `bit-reuse-maximal.json`, and a JSON comparison
  prints `EQUAL`.
- An earlier run at the previous head `2a10ca79d7f2` gave the same output
  sha256. The two files involved are unchanged between the two heads. The new
  composition files of #199 (`next_bit_composition.py`,
  `next-composition-result.json`) were not replayed.
- Scope: this reproduces a finite exhaustive diagnostic over distinct frames
  for #189's bit word. It does not reproduce any κ.

## What this submission adds, and predecessors

All constructions, certificates and verifiers are the cited authors' work
(#207, #202, #200, #197, #194, #193, #189, #187, #185 and their lineage). This
directory adds only independent replays at pinned heads, one read-only
diagnostic script, and the reproducibility observation of item 2b. It changes
no generator, certificate, test or `upstream/` file. It claims no bound.

## Proof obligations not addressed here

- Item 3: the bank-endpoint identity on the full cover (`PROOF.md` §4 of #197),
  and its counterpart in #205.
- Item 2b: the cause of the lift-hash difference.
- For all items: the retained conditional interfaces stated by each
  submission (Clifford/tensor realization, weighted local-ring compilation,
  restored rows, fixed tape, routing, prime supply, precision and analytic
  transfer). A finite replay does not establish them.
- #205, #206, #208 and the new composition files of #199 were not replayed.

## Disclosure

Prepared with Claude (Anthropic) agents; runs executed locally; reviewed by the
submitter. New material is under the repository's Apache-2.0 license.
