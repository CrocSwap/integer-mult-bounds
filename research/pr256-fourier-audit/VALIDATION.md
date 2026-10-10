# Validation of this audit contribution

Prepared against CrocSwap main `3b6b66891c0ac888521cf591fe306c6286601d4f`.
This is a separate AI-assisted reproduction, not independent human mathematical
review. The bound and proof remain the credited upstream authors' results.

## Audit package

- Offline finite verifier: passed on Python 3.11, 3.13 and 3.14.
- Eleven audit controls (two positive and nine negative): passed; altered stock/child counts, an unrecorded
  exponent, a weakened quantifier, an extra axiom, a missing build, a wrong source
  revision and a changed build log are rejected. Optimized Python is refused.
- Full-checkout comparison: all 20 pinned PR256 package files and all 456 proof
  source files matched the separate checked-out revisions.
- OpenAI origin: all 91 ledger files were downloaded again from the immutable
  OpenAI revision and matched, including all 89 imported OAI modules.
- Ported Lean reproduction wrapper: passed against the existing pinned build,
  with `--cache-ready`. Both source generators reproduced their output; staged
  scalar targets, combined build, axiom check, WHT comparison and Fourier
  comparison all exited 0. This wrapper test reused the project build and is not
  a second fresh build. The retained historical receipt records the earlier
  successful fresh project compilation.
- Source syntax and whitespace checks passed.

## Existing repository checks

`make entrance-bank-verify` passed: selected-record validation, the complete
offline complex/bit construction, all 47 outer constraints, seven margins,
21 assembly controls, and the bank scheduling supplement.

The full `make verify` regression run was invoked. At submission, its community,
producer, partial-gauge, three-stage-cover and paired-cube groups have passed;
the remaining groups are still pending. This is not a claim that the full suite
has passed. No existing source, certificate, selected-result pointer or root
documentation is changed by the contribution.

## CI scope

The added workflow repeats the offline finite audit and audit controls on
Ubuntu with Python 3.11, 3.13 and 3.14. It does not claim to run Lean or a second
kernel; full proof reproduction is the separate documented command. Configuring
the workflow does not itself constitute a successful CI run.
