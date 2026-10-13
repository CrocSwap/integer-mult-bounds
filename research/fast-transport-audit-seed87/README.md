# Exact, opt-in acceleration of the pinned transport audit behind the negative-control suites

**Tooling improvement (verification engineering). No new κ. No mathematical check is changed, skipped or weakened,
and no pinned file or orchestrator is edited.**

PR635's `hpe_audit_and_transport.run` audits a local word. It does an exact all-column scalar replay in both
orientations, plus native frames, the cone pre-check and the profile pin. It is the per-trial cost of every
negative-control suite in the selected cold chain:

| suite (recorded cold-chain time) | control script |
|---|---|
| T37 layer-end, 77 s | `complex-t21-owners/vendor/pr870/construction/layers_p6n/layer_end_controls.py` |
| #799 layer-end, 151 s | `gauge44-frames-x/construction/layers_p6n/layer_end_controls.py` |
| #741 p6n layer-end, 114 s | `complex-sw4-frame8/construction/layers_p6n/layer_end_controls.py` |
| #741 layered66 layer-end, 64.5 s | `complex-sw4-frame8/construction/layers/layer_end_controls.py` (`7829187b…`, 59 controls) |
| #741 inherited cold-end, 114 s | `complex-sw4-frame8/local/cold_end_controls.py` |

Each suite runs 96 full audits: the honest word plus 95 mutants, each rejected for a pinned reason.

`fast_controls.py` runs an unchanged control script with an import hook. The script's own import rule (its `sys.path`
and `$PR635_CODE`) still selects the `hpe_audit_and_transport.py` file. The hook executes that file from the bytes it
hashes, never from a `.pyc`. Only when the sha256 is the validated `c9a05ff2…` does it rebind five module globals.
Each replacement returns exactly the values the original returns:

| global | replacement | why it is exact |
|---|---|---|
| `Q` | Fraction constructor returning `int` for integral values | `Fraction(a, b)` is evaluated first (same exceptions); an int has the same value, `==`, hash, truthiness, `.numerator` and `.denominator` |
| `apply` | the same sparse row update with ±1 and integer fast paths | same assertion order; same lazy row access; same zero-dropping points and key order; reduced rational arithmetic otherwise |
| `copy` | structural copy for flat gate records | a flat list of atoms and flat atom lists is copied structurally; anything deeper goes, as a whole, to `copy.deepcopy` |
| `basis` | memoised on all-`int` inputs | pure function; any non-`int` input takes the pinned path every time |
| `state_maps` | P and P⁻¹ in scaled-integer dyadic arithmetic | applies only when every prefix gate is a well-formed dyadic primitive (else the pinned code runs); equal values, keys and key order |

`run()`, `cone_violations`, `inverse`, `dual`, every assertion and message, and all serialisation remain the pinned
module's own code objects.

## Use (opt-in)

```sh
PR635_CODE=<as the script needs> python3 -B research/fast-transport-audit-seed87/fast_controls.py \
  [--require-fast] <unchanged control script> <script args...>
```

Use it as a drop-in for `python3 <control script> <args>`. Options are read only before the script path; everything
after it is passed through verbatim. An unvalidated module version runs unaccelerated with a warning; under
`--require-fast` it exits non-zero. `--pinned` loads through the same hook without accelerating, as a matched
baseline. `FAST_HPE_RECORD=<file>` records every audit outcome. Nothing is wired into any orchestrator.

## Evidence

```sh
python3 -I -B research/fast-transport-audit-seed87/verify.py           # ~6 min: tests + 4 real suites
python3 -I -B research/fast-transport-audit-seed87/verify.py --quick   # ~2 min: tests + T37 suite
python3 -I -B research/fast-transport-audit-seed87/bench.py            # per-primitive ablation
```

Expected final line:
`PASS_FAST_HPE_TRANSPORT suites=4 audits=384 identical_receipts_logs_outcomes cpu=…`. Timings vary by machine;
every deterministic field is compared with `EXPECTED.json`.

**Real suites.** `equivalence.py` takes each input word, archived receipt and archived log from the repository's own
evidence tarballs. It runs the unchanged control script three ways:

- **D**: directly, as the orchestrators run it;
- **P**: through `fast_controls.py --pinned`;
- **F**: through `fast_controls.py --require-fast`.

This covers the T37 U8, #799 X4, #741 p6n and #741 inherited-cold-end suites (4 × 96 audits). In every suite:

- `COLD-END-CONTROLS.json` is byte-identical across D, P and F;
- it equals the archived receipt apart from its machine-specific absolute `word` path;
- stdout is identical across D, P and F and, for the three suites with archived logs, equal to the archived log, after
  dropping only the audit's top-level `"seconds"` line;
- the module the script itself selects is the expected file, unaccelerated in P and accelerated in F;
- all 96 per-audit outcomes are identical between P and F. That covers the exception type, `repr(args)` and the
  `run()` line it propagated through, or the receipt text without its seconds line plus both output-word hashes.

**Differential tests** (`tests/test_exactness.py`, run under both Fraction constructors). Each primitive is compared
with the pinned function on value, key order and exception type and message:

- `apply` on 4,000 random programs, including malformed gates: short gates; target equal to source; out-of-range,
  negative and non-int indices; b = 0; float, bool and str coefficients; zero scales and zero coefficients;
- `state_maps` on 300 programs, 227 of which take the dyadic path, and on the real 12,913-gate U8 audit prefix;
- `basis` on 3,000 inputs, including float, bool and str vectors and repeated (cached) calls;
- the copy, including nesting depths 1 to 2,000 (the recursion limit is reached at the same depths);
- `run()` itself, on a pinned and an accelerated module instance, for the honest U8 word and four deep-nesting variants
  (PASS, TypeError and RecursionError outcomes all identical);
- the import hook: it selects a script's sibling module over `$PR635_CODE`, and refuses a modified sibling under
  `--require-fast`;
- the hash guard.

Negative controls: an `apply` that keeps zero entries is detected; a zero-coefficient gate behaves like the pinned
code.

**Adversarial review.** Three independent reviewer subagents tried to break the claim:

- a primitive fuzzer: about 600,000 `apply` gates, 1,000 long dyadic programs and 160,000 `basis` calls;
- a word mutator: 201 new corrupted variants of the real U8 word, each run in fresh processes;
- a harness reviewer.

They found and reproduced one real divergence. The earlier structural copy used one interpreter frame per nesting
level, so a gate carrying a list nested about 500–1,000 deep made the pinned audit raise `RecursionError` while the
accelerated one passed. The copy now handles only flat records and leaves deeper structure to `copy.deepcopy`.

The harness reviewer also showed that pre-importing from `$PR635_CODE` could substitute a different module for a
script that imports its own sibling. About 17 directories hold another version. That is why the import hook now lets
the script choose. Other findings are also addressed: bare asserts are now distinguished by the `run()` line, the
receipt is compared as text, a stale `.pyc` can no longer bypass the hash guard, the wrapper's own directory is
removed from `sys.path`, and `--` is passed through. Each case is now a test.

**Measurements** (macOS arm64, CPython 3.14.8, concurrent agents running, load average 8–22; `EQUIVALENCE.json`,
`BENCH.json`):

| measurement | direct (pinned) | accelerated | ratio |
|---|---:|---:|---:|
| one honest U8 audit, best-of-9 process CPU | 0.766 s | 0.334 s | **2.29×** |
| T37 U8 suite, CPU | 57.2 s | 23.9 s | 2.39× |
| #799 X4 suite, CPU | 53.2 s | 27.1 s | 1.96× |
| #741 p6n suite, CPU | 57.2 s | 30.7 s | 1.87× |
| #741 inherited suite, CPU | 71.7 s | 24.3 s | 2.95× |
| **four suites, CPU** | **239.3 s** | **106.0 s** | **2.26×** |

Cumulative per-audit ablation: Q/apply 1.72×, +copy 1.72×, +basis 2.07×, +state_maps 2.29×. The restricted copy now
saves about as much as its flat-shape check costs; it is kept for the per-mutant deepcopy-heavy paths and can be
dropped without loss of exactness. Suite ratios vary with load. Each control script also builds, serialises and
gzip-compresses every mutant itself, and that cost is unchanged.

**Current selected lineage (#1094).** The selected #1094 construction rebuilds the k8 leaver chain. That chain runs
`gauge44-leaver8/construction/leaver/layer_end_controls_leaver.py` (`4ba676f1…`) five times, on the p6n, promo, jx,
hybrid and final words, against this same validated module.

On the final k8 word `db2c7cfb…`, rebuilt by the #1005 drivers with `LEC_REASON_PINS=LEC-REASON-PINS-k8.json`, a
direct run and `fast_controls.py --require-fast` produced:

- a byte-identical `COLD-END-CONTROLS.json` (95 rejected controls plus 2 declared not-applicable substitutes), also
  identical to the chain rebuild's own receipt;
- identical stdout apart from the seconds line;
- user CPU 50.6 s → 24.6 s.

This input word is not archived in the repository, so the check is recorded here and is not part of `verify.py`.

## Scope and composition

- This accelerates single-process CPU and composes with #1059's record/evaluate/replay parallel runner. Under spawn,
  its workers would call `install(atc)` in their initializer. That integration was not done or measured here.
- Validated only for module sha256 `c9a05ff2…` (PR635 `complex-571-cold14-st2/code`, identical to
  `complex-sw4-frame8/local`). Other copies with different bytes are refused.
- The layered66 suite was not run because its input word is not archived. It uses the same validated audit module
  but a different control-script variant (`7829187b…`), so it is listed as unvalidated.
- Not included: the cross-mutant prefix memo explored alongside this work (exact; about 2× CPU on the same suites;
  composes because it calls the module's `apply`), and the per-mutant gzip and deepcopy costs inside the pinned
  control scripts.
- Exactness is claimed for `run()`. After installation, module helpers return `int` for integral values, so do not
  install into a process that does its own arithmetic with `apply()` or `state_maps()`. The wrappers add at most one
  interpreter frame, so behaviour within a frame of Python's recursion limit is not claimed bit-identical. The `basis`
  memo grows for the life of the process (memory only).
- Timings are local measurements under concurrent load. The equivalence evidence is the claim; the speed figures are
  indicative.

## Credit and disclosure

- PR635 authors (icekylinx; GPT-6 Astra assistance) for the transport audit.
- DreamingOfClouds / LayerReviewer for the control scripts.
- NewBArch and Jeremy Kothe (#869/#870), chafreaky (#741) and Jonathan Capalbo (#942) for the archived replays.
- #1059 for the complementary parallel runner.

Track 85–94, OS-random seed 87, base `2921874911956718fcaaaf9396fe8267b3cfa9f0`.

Prepared by Sagar Thakrar with substantial assistance from Anthropic Claude (Claude Code). Five subagents explored
alternatives, three judged them, and three adversarial subagents reviewed this package. Apache-2.0.
