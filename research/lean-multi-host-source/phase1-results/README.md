# Phase 1 validation receipt

**PASS for the bounded probe only.** The complete Task A / Task B port is
still pending approval and has not been claimed to pass on 4.21.

Tested clean checkout: `62d0a4df2d4cdc4fcf3a7f0285397c7c68ea251b`.
The later receipt commit changes only reports and documentation; its
manifested build and source-check files match this tested checkout.

- `lake build`: PASS, 51 local modules freshly compiled, 0 replayed; 291.242 seconds.
- `lake env lean ProbeAxioms.lean`: PASS, all 567 requested reports; 17.800 seconds.
- Allowed axioms: `propext`, `Classical.choice`, `Quot.sound` only.
- Source binding: PASS, all 19,002 events and six original input hashes.
- Parser negative controls: PASS, seven corruptions rejected.
- Tracked checkout clean before verification and unchanged afterward.
- OS stack: inherited 8 MiB. Environment overrides: none. No added Lean build flags.
- Compiler and all nine external dependency revisions/fingerprints are in
  `clean-receipt.json`. The dependencies were reused from the separately
  recorded pinned 4.21 source build; no local probe proof artifact was reused.

The executable was selected by its installed toolchain path using the verifier's
`--lake` option. The child commands were ordinary `lake build` and
`lake env lean ProbeAxioms.lean`; metadata queries used `--version`, `--githash`
and `--print-prefix`. No resource or proof-checking setting was supplied.

See [TIMINGS.md](TIMINGS.md) for individual module comparisons and the
FrameData/full-port estimates. `module-timings.json` preserves successful and
failed attempts. Raised-stack diagnostics are explicitly excluded in
`early-stack-diagnostics.json`. Failure-log path redactions are documented
inside the timing records. `SHA256SUMS` covers every included result file
except itself. From this directory, check it with:

```sh
sha256sum -c SHA256SUMS
```

The new package is not yet included in upstream's workflow matrix. This is
a clean-checkout run of its normal underlying Lake build/audit commands, not
a claim that the full upstream workflow or the unported full package passed.
