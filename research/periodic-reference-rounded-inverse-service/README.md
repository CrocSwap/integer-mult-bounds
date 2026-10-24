# Complete periodic reference inverse service

This package returns all385 coordinates of a rounded inverse action for the
unchanged `Reference(384,1,2,4,18,320)`, including the actual cross-period
couplings and hole192. It replaces the missing wrapping numerical producer
from the R10 [Core/halo handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19143431)
with an explicitly paid whole-period fallback. It does not infer a usable
local halo or cheaper seam tariff.

[PROOF.md](PROOF.md) bounds coefficient quantization, data rounding, every
iterate, polynomial tail and the separately inherited analytic-reference
perturbation. The t20,Y1 fixture uses276 terms and a33-bit grid. All3,457
source entries are constructed through the original producer. The independent
checker enumerates every original matrix entry and bounds the returned error
by the exact source residual divided by the certified gap. It also executes
an actual dropped-wrap trajectory that fails the requested target.

The implementation is a host-array numerical service. The complete arithmetic
bill, borrowed-input lifetime, output coexistence, scratch initialization and
cleanup, persistent table and separately executed source setup are explicit. Retained
module-level pi caches and weight-receipt storage are counted separately
from the service scratch arrays.
No physical tape realization, selected supplier, full multiplier or kappa
improvement is claimed. The R10 insufficient-halo finding remains valid.

## Reproduction

Python3.12, standard library only:

```sh
python3.12 scripts/research_package.py --package research/periodic-reference-rounded-inverse-service
```

Both normal and optimized full checks are registered with180-second caps.
Direct `verify.py` runs also work in the official Git-free export. Every
source import and dynamically loaded interval input is declared and hashed.
RESULT.json is mandatory and compared as typed canonical JSON. The optional
`--record PATH` writes a generated result explicitly; normal verification
never replaces its expected receipt.

The first local diagnostic reached every row and passed its arithmetic tests
but exited unsuccessfully while converting a huge Fraction to decimal text.
It is not a passing replay. Final reporting rounds exact bounds outward to
80 fractional bits, after exact inequality checks; it does not relax the
scientific acceptance criteria. Runtime/RSS are observational logs, not
portable scientific receipt fields.

## Inherited and new obligations

Inherited: Jose Manuel's immutable reference and ordinary Core, the original
Gaussian analytic estimates, Mason Hale's interval routines, and classical
contractive recurrence/error methods. New: complete actual periodic action,
its setup/grid/ownership/workspace contract and source-residual validation.
The coefficient table is independently quantized once, while the verifier
retains original rational entries. An unchanged Plan returned by prepare is
the service precondition; arbitrary manually constructed Plans are uncertified.

Source pins and history are in SOURCES.json. Reference head is
c9db4069d59bfad26a15fe000b91cc3a058684e5; Core context is
78c72e563173f3822fcb4efed9ceeccf05630258. Credit Jose Manuel, Vlado
Vojdanovski, Jeremy Kothe, Cinna Davis, Mason Hale, Chafik Boukhalfa and
retained contributors. Prepared for JoyboyBrian with substantial OpenAI Codex
assistance. New work Apache-2.0; original source notices remain unchanged.

## Open next questions

The next distinct contract is an actual ordered physical coefficient/input
supplier with complete cyclic addressing, setup and cleanup charges. Only
then can its full-period bill be compared with a funded ordinary/seam split.
See TASK.json; this package supplies no physical cost saving.
