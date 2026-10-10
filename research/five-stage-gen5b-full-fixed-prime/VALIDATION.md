# Actual local validation

The vendored PR #300 supplier (`source/`, commit `aea3dc9`) was replayed locally with `source/verify.py --output`:
all twelve stages fresh (virtual, raw, bit with descent and targets, kernel, second descent, restore, sink, scalar,
primes, banks, complex, math, finite), package integrity unchanged, 149 manifest files,
`PASS_IMMUTABLE_GEN5_KERNEL_RESTORE_SINK_FIVE_STAGE_BANKED_CONSTRUCTION`, κ `187495641816757/250000000000000000`;
the run's `verification.json`, `certificate.json` (as `supplier-certificate.json`), `finite.json`, `primes.json`,
`banks.json`, `math.json` and log are in `validation/`.

`prime_eight_port.py` was then run on that output (0.5 s): κ `749982571369270160072237/10^27`, gain
`4102242160072237/10^27`, coarse `187636366847207996746853/(25·10^22)`, coefficient 90,408,185,853,299,401; the
committed `certificate.json` is that output. `verify.py` repeats both steps from scratch and compares key by key.
