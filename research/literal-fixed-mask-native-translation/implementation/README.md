# Literal arbitrary fixed affine offset on complete native packets

For every fixed nine-bit offset b, this package emits a complete same-owner
Gamma6/HOME translation on `[P] x [2^f]^9 x [S]` at every positive encoded
geometry. Slot i is XORed with2^f-1 exactly when bit i of b is set. Every
component bit, coefficient, spectator, header/cutoff and common grid is
preserved. The operation is a pure address permutation, including at minimum
signed component values; there is no arithmetic headroom promise.

The existing #7428 first-slot translation is retained unchanged. Its theorem
already permits an opaque tail after the first five Gamma codes, so the
trailing sixth cutoff is accepted without a new parser. A fixed conjugator
G with G e0=b gives the chronological composition G^{-1},X0,G: one reversal
and at most20 literal CNOTs. For b=0 the outer transaction is the identity.
Offset/pivot/word generation occurs offline and never inspects runtime
geometry. The construction does not supply a runtime matrix/offset loader.

The core uses31 tapes and has complete successful bounds

`T_core<=2^20(fV+E+1)`, `K_final<=K_entry+256(V+E+1)`.

Here `V=2PScw2^(9f)` and E includes all six Gamma codes. The35-tape HOME
layer adds128(F+1) time and64(F+1) backing, where F=E+V. General B1 bank
access, fixed setup/program storage and owned input production/placement
remain separately paid. All heads/private bodies/guards retire on success;
failure cleanup and interruption/retry are unclaimed.

Reproduce with only the Python standard library; numerical runs take about
21 seconds each:

```sh
python -B /workspace/scratch/92c9920affc2/worker-a/research/generic-affine-native-translation/verify.py
python -O -B /workspace/scratch/92c9920affc2/worker-a/research/generic-affine-native-translation/verify.py
python -B /workspace/scratch/92c9920affc2/worker-a/research/generic-affine-native-translation/bind_sources.py
```

The verifier checks all512 offset conjugators on all512 native addresses,
15 literal templates, five complete parser-boundary probes through4097-bit
cutoff syntax, and full dense f1 HOME executions for full offset511, mixed
far slots3/8, identity and same-owner reuse. Direct address-XOR oracles do
not simulate the emitted conjugators. Actual omission and conjugation-order
mutants return the predicted wrong maps. All35 heads/private/exteriors and
public-before-commit safety are checked. Fresh absent bytecode-cache prefixes
isolate source replay; exact pins and graph hashes are in SOURCES.json and
SOURCE-BINDING.json. `--write` refreshes the corresponding receipt.

This closes one literal affine-offset interface. Earlier physical Gaussian
monomial and current serial/coded monomial work already covers broader
semantic operations in other source/Count ABIs; their algebra is not new
here. No generic source monomial dispatcher, complete MOVE, actual caller,
nonleaf tariff, global assumption discharge or kappa change is claimed.

Open next questions are exact source-specific composition with binary and
complete linear/quadratic/global phase passes, numerical/source orientation
and owned producers, then caller/rate admission. C's independent census
confirms offsets are post-G output-coordinate masks and that every support
size1..9 occurs; this package neither duplicates that census nor infers
all-MOVE implementation from its offset domain. Earlier frozen packages
remain unchanged. The proof and exact limitations are in PROOF.md.
