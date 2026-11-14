# Literal positive central join at each fixed native rank1..9

This package emits one complete fixed-tape positive central leaf for each
fixed rank rho=1..9 and arbitrary encoded column count f, in the existing
six-Gamma/HOME ABI. The actual joint guard is **rho*f<=cutoff**. Every leaf
and slot swap receives the original f and retains the complete9f geometry.
No width-changing view is supplied to a nine-slot numerical consumer.

The central operator is positive C on all f bits of the first rho native
slots, with exact phase and unchanged quantum. One original-owner transaction
encloses rho first-slot C passes and6(rho-1) CNOTs implementing slot swaps.
All helpers, copying, descriptor scans, return and retirement are paid.
The core uses31 tapes; the supplied owned HOME layer uses35. For complete
bit lengths `V=2PSc2^(9f)w`, E and F=E+V, successful runtime satisfies

`T_core<=2^24(fV+E+1)`, `K_final<=K_entry+2048(V+E+1)`.

HOME adds128(F+1) time and64(F+1) backing. General B1 bank access, fixed
setup/program storage and caller creation/placement remain separate charges.
Every actual intermediate C prefix must be integral and fit the supplied
signed width; final fit alone is insufficient. No scale, width conversion
or rounding is installed.

PR #6978 already proves the rank-times-column algebra, positive orientation,
cutoff and coded child; `selected-native-tensor-closure` proves the selected
all-column algebra. The contribution here is a literal uniform-rank
Gamma6/HOME numerical lifecycle export, extending the frozen literal rank2
mechanism. It is a central primitive, not a complete generic MOVE. It does
not satisfy the faster nonleaf tariff, identify an actual caller, implement
all source monomials, or discharge a global assumption. See PROOF.md and
OVERLAP.md for the exact source/claim boundaries.

Reproduce with the Python standard library, in about11 seconds per run:

```sh
python -B /workspace/scratch/92c9920affc2/worker-a/research/generic-positive-native-join-gate/verify.py
python -O -B /workspace/scratch/92c9920affc2/worker-a/research/generic-positive-native-join-gate/verify.py
python -B /workspace/scratch/92c9920affc2/worker-a/research/generic-positive-native-join-gate/bind_sources.py --source-repo /workspace/scratch/92c9920affc2/repo
```

The checker authenticates immutable sources before retained imports, with
fresh bytecode-cache isolation. It checks all nine table families,233 literal
guard headers at signed distinct origins including4097-bit cutoff syntax,
and a complete nonzero f1/rho3 packet against direct actual-axis butterflies.
It verifies all35 heads/private bodies/exteriors, public safety on cutoff,
and an actually executed omitted-third-C graph. Large header cases do not
constitute full large-f numerical execution. `--write` refreshes RESULT.json.
The source-binding command checks21 retained pins,15 original Git blobs,
the canonical prior proof and all nine regenerated tables. SOURCE-BINDING.json
also pins the complete rank3 HOME graph by normalized JSON SHA256.

Open next questions are the source-specific complete monomial/HOME join
(including affine offsets and nonzero global phases), actual typed source
binding/producer promises, endpoint format conversion where needed, and
separately the selected nonleaf rate. The fixed9-axis source census is being
reviewed independently; this package does not duplicate it or infer all-MOVE
coverage from its rank range. Earlier frozen packages are untouched.
