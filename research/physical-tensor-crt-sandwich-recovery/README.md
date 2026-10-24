# Physical CRT/Tensor sandwich and conditional recovery

JoyboyBrian, with substantial OpenAI Codex assistance.

This package executes the actual PR4024 CRT converter and PR3935 Tensor in
the full three-transform convolution sequence, then applies both S factors,
nearest integer recovery, inverse CRT and carry propagation. PROOF.md gives
a quantified sufficient precision guard and the full inherited-premise ledger.
It does not establish a production multiplier or a new bound.

The actual coprime (5,7) -> (8,8) reduced p48/P80 producer packet is retained
with SHA authentication. A 375.56-second initial execution matched every
staged transform byte and returned 0, while the true product is 345550037539.
The diagnostic policy explicitly disclaims integer recovery. Default production
entry rejects this reduced catalogue. The p96 exact recovery leaf uses supplied
approximations with a checked error enclosure, not production-generated pages.

Run from repository root using Python 3.12:

```sh
python3.12 -B research/physical-tensor-crt-sandwich-recovery/verify.py --suite leaves
python3.12 -O -B research/physical-tensor-crt-sandwich-recovery/verify.py --suite full
```

The final Git-free optimized full replay took 372.34 seconds locally on
macOS arm64 with CPython 3.12.2. This timing is not portable: the
[hosted replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39928197748/job/120331693703)
on Ubuntu 24.04.5 x64 with CPython 3.12.15 passed the leaves in 5.40 seconds
but timed out the full command at its unchanged 600-second limit. Full hosted
verification is incomplete; the timeout supplies neither a passing result nor
an observed arithmetic assertion failure. No network, dependencies or
coefficient regeneration are required. Optional `prepare_fixture.py OUTPUT_FILE`
repeats the actual ~251-second producer into a new file; it is not part of replay. The official package export includes
all source inputs and original notices; nested archives authenticate themselves.
Full execution is a finite certificate, while PROOF.md is a conditional written
argument. Neither is independent human or kernel acceptance.

PR3935 credits Jose Manuel / jmbarrancoml; PR4024 credits Tekalign / tekuuu.
Mason Hale's PR2313 dense interval recovery is predecessor work, not reproduced
by this physical caller. Source07/source08 retain their Fourier and convolution
identities. No frozen predecessor file or selected frontier is changed.

## Open next questions

- Bring the complete continuous owner invocation below the hosted limit with a
  proved equivalent optimization. A bounded 20-second diagnostic profile of
  the unchanged local run found inherited tape operations and encoded loop
  counters dominant in that prefix; it did not measure the complete run. Any
  adapter must preserve frame validation, all three transforms and converters,
  borrowed inputs, pending-return consumption, and the complete checks.

- Supply a production-admitted catalogue/native instance and bind its actual
  local analytic errors to the sufficient caller guard.
- Bind arbitrary n-bit packing and a valid all-size parameter family, including
  preparation and native costs, before claiming a complete multiplier.
