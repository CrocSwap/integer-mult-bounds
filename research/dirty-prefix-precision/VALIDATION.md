# Executed validation

Linux x86-64, 2026-10-13, CPython **3.12.3** and **3.14.4**. Base
`f567884aeb8851b6e794af1184119a3bfbe1e631`; audited #628 head
`0768f97d06c623b8211e651543c66135796b62bf`. All twelve retained predecessor
files match their SHA256 and Git object pins. New arithmetic and the proof
were written by one AI agent; no independent human review is claimed.

## Replays

The primary verifier generated the receipt with Python 3.12.3:

```sh
/usr/bin/python3.12 -B -I -S research/dirty-prefix-precision/verify.py --write /tmp/new-dirty-prefix-receipt.json
```

The resulting bytes became `EXPECTED.json`. Default receipt comparison then
passed with Python 3.14.4:

```sh
/usr/bin/python3.14 -B -I -S -O research/dirty-prefix-precision/verify.py
```

The expected marker on both is:

```text
PASS_DIRTY_PREFIX_PRECISION budgets=1740 prefix_traces=18 rounded_generic=48 rounded_kernels=40 controls=10 kappa=unchanged
```

The four focused tests passed on both versions, with optimized Python on 3.14:

```sh
/usr/bin/python3.12 -B -I -S research/dirty-prefix-precision/test_precision.py
/usr/bin/python3.14 -B -I -S -O research/dirty-prefix-precision/test_precision.py
```

These test 603 exact logarithm boundary cases, preservation of a finer incoming
grid, the feedback threshold, and eight literal nonlinear-error executions
with exact dirty restoration and whole-word inversion. Checks use explicit
exceptions, so `-O` does not remove them.

`make selected-record-check` passed at the unchanged selected value
`1661634653669567/1000000000000000000`. Full repository regeneration, selected
supplier cold replay and Lean were not rerun for this isolated research package.
Hosted CI is separate from these local results.

## Independent arithmetic paths and coverage

The exact receipt contains:

| Check | Executed coverage |
|---|---:|
| Resource recurrence and closed-form leaf count | n=1..10,000 |
| Literal equality with the frozen dispatcher | 128 signed words, 191,342 instructions |
| Dense integer prefix/inverse-prefix replay | 18 traces, 11,142 primitive boundaries |
| Separate rational Gauss-Jordan inverse | 66 selected prefix matrices |
| Direct contiguous-subword reconstruction | 5,104 intervals |
| Inherited and new integer precision budgets | 1,740 cases over 116 prime-power radices |
| Actual rounded generic executions | 48 |
| Actual certified kernel executions | 40, covering all ten source certificates |
| Observed leaf-boundary magnitude/source restoration | 6,304 boundaries |
| Mathematical rejection controls | 10 |

Every rounded execution has a nonzero exact error within the new bound, so
the comparison is not supported solely by exact-arithmetic special cases.
Kernel target comparisons use independently expanded polynomial matrices
and dense solves; the source's coefficient perturbation is separately charged
to the total `2^-128` guarantee. Both cyclic directions, lengths one and
three, nonzero targets, positive and negative dirt, and exact inverse-word
cancellation are included. Generic fixtures are interface cases, not additional
certified prime-power kernel instances.

The first pilot exposed an ineffective negative fixture: flipping every leaf
sign at **three** factors gives the correct negative *ideal* product. The
inverse-order rejection control now uses two factors, where it provably
differs. This was a control-fixture correction, not a failure of the prefix
lemma or error bound. The final ten controls all reject as recorded.

## Standalone and package controls

A copy containing only this package, in a path with spaces and with no Git
metadata, passed the default verifier using Python 3.12.3 with `-B -I -S -O`.
All package file hashes were unchanged after that run: default replay is
read-only. No site packages, network or third-party Python modules were used.

Six further controls were executed in that disposable copy:

| Modification | Result |
|---|---|
| Append a comment to vendored `dirty.py` | Rejected: source drift |
| Understate a recorded working-bit budget | Rejected: certificate mismatch |
| Alter a recorded prefix-stream digest | Rejected: certificate mismatch |
| Substitute a boolean for an integer receipt field | Rejected: certificate mismatch |
| Reverse the sign in the new inverse-prefix update engine | Rejected by the separate Gauss-Jordan comparison |
| Request `--write` to an existing receipt | Rejected before replay; original bytes preserved |

Every mutation was restored; the final complete file inventory matches the
initial one. Python syntax, local Markdown links and staged whitespace were
checked. The existing source files and selected artifacts are untouched.

## Limits

The universal result comes from [PROOF.md](PROOF.md) plus the inherited
rounded-leaf and coefficient/phase preparation assumptions. Finite tests do
not formalize that result or the full multiplication theorem. They do not
implement the worst-case factorizer, fast fixed-precision arithmetic, a
fixed-tape schedule or an admitted supplier. The new guard is sufficient,
not optimal; it can be worse than the old guard at small radices. Initial
grid capacity, all dirty data, internal leaf magnitude bits and every access,
restoration, preparation and routing obligation remain charged.
