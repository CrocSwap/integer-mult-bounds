# A complete-caller zero fiber with 86N independent bits

The selected same-grid stochastic caller has a displayed family of
`2^(86*N)` distinct public inputs with identical complete output for each
fixed retained seed. All input coordinates are in {-h,0,h}. Native maps that
preserve zero make that common output exactly zero, as in [PR #6546](https://github.com/CrocSwap/integer-mult-bounds/pull/6546)'s sampler.
Exact recovery with an unchanged seed therefore needs at least `86*N` bits
of retained capacity. At `N=512`, this is 44,032 bits, or 5,504 bytes.

The proof identifies all 43 public fields whose first read or write is a
signed half-SCALE. It follows their independent bits through every source
event, including native calls before the last half at event 10447. An exact
packed code attains the bound on the displayed family. It is not a claim
about the maximum fiber or minimum record for all caller inputs.

A fixed input pair independent of the seed also has identical complete output
with probability at least one half under fresh sampling. This does not
invalidate the predecessor's numerical error theorem: its retained-state
inverse preserves the information that the public output loses.

[PROOF.md](PROOF.md) gives the argument, scope and counting model.
[RESULT.json](RESULT.json) gives the cohort and exact receipt.
[fiber.py](fiber.py) contains the two censuses, causal checker and family code.
[verify.py](verify.py) runs the independent finite corroboration and controls.
[SOURCES.json](SOURCES.json) and [NOTICE](NOTICE) retain source pins and credit.

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/selected-caller-zero-fiber
```

The normal and optimized commands check all 22,803 source events, all public
first accesses, 53 complete scalar/zero-contract replays (1,208,559 events),
the family codec, 86 individual bit witnesses, nine semantic/domain controls
and a source-corruption rejection. Each native operand must be exactly zero;
this package uses its proved zero contract and does not run compiled natives.
The exponential fiber size follows from the proof, not exhaustive enumeration.

The lower bound is for arbitrary same-grid public inputs and exact recovery
from the public output, unchanged seed and any declared extra state. It is
not a clean hardware-storage minimum. Original input copies count as retained
information. A promise of even input coordinates removes this displayed
family. Physical routing, sampling, cleanup, true caller input correlations
and all five complete framework assumptions remain open. No new kappa or
selected-frontier change is claimed.

## Open next questions

Determine the complete map's maximum fiber or a smaller full-input recovery
code. Before applying this lower bound to a physical caller, verify that its
entrance encoding admits the displayed independent inputs and that native
operations have no undeclared reads. Price all retained copies, tags and
cleanup under that actual contract. The 86N-bit family alone does not settle
those questions.
