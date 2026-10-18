# QQ16 current-frame L2 reconstruction and consumer

This package constructs 104 actual owner maps that preserve the full current
frame `F_U1`, uses them to recover `x1_U` from the L2 interface, and consumes
that result in place to obtain `y1_U`. The complete staged consumer uses native
rank mass **320** and real scalar primitive allowance **7,392**, including its
96 final ADDs. All **200 borrowed source arrays are restored**; its 96 outputs
and one local scratch are exclusively owned.

An alternative fixed epilogue returns `x1_U` in the old frame `F_L`, exactly
matching [PR2492](https://github.com/CrocSwap/integer-mult-bounds/pull/2492)'s
local output contract. Under the same positive-child grammar, its native rank
mass is **1,088 versus 1,168**, with the same scalar allowance and map count.
These are local invoices; the new cover maps still need physical admission.

## Construction and endpoints

For each source current-chart owner matrix `g=rho_1(p)` and old alignment
translation `delta`, the new map is `B_p=M(g,delta+g delta)`. It is self-inverse
and satisfies `B_p F_U1 = F_U1 D_p` on arbitrary arrays, owners and payload
layers. The proof checks the actual 73-bit phase, not only a constant slice.
All 104 old translations fail this new covariance identity.

The word normalizes and restores the 96 borrowed Y fields, upgrades only the
eight retained T fields to `F_U1`, applies the new owner maps, and performs the
L2 correction with one private scratch. It then reverses the owner maps and T
upgrade. The 96 owned Z fields contain `x1_U` in `F_U1`. The default epilogue
subtracts the unchanged current X fields to produce `y1_U`; the alternative
converts Z to `F_L` instead. [PROOF.md](PROOF.md) gives the exact contracts,
ordered owner algebra, native child lowering and all counts.

| Complete endpoint | Current `y1_U` | Old-frame `x1_U` | PR2492 old-frame `x1_U` |
|---|---:|---:|---:|
| Positive rank-one children | 192 | 192 | 400 |
| Positive rank-eight children | 16 | 112 | 96 |
| Native rank mass | 320 | 1,088 | 1,168 |
| Native monomial wrappers | 416 | 608 | 992 |
| Full-cover maps | 208 | 208 | 208 |
| Real scalar primitive allowance | 7,392 | 6,624 | 6,624 |

The last two columns have identical endpoints and child grammar. The first
column changes the output frame and includes a different consumer. The staged
word exposes an `x1_U` checkpoint; no shortest scalar circuit is claimed.

## Evidence and reproduction

[WORD.json](WORD.json) and [OLD-FRAME-WORD.json](OLD-FRAME-WORD.json) are complete
1,235-event words. [RESULT.json](RESULT.json) records both exact symbolic
replays, the native kernels, map matrices/translations and twelve rejected
semantic faults. A separate literal-parity check performs 281,008 comparisons
on zero, singleton and two-bit characters. These determine the full modulo-4
quadratic phase polynomial, so this check is complete for that identity.
Tests also reject late owner alignment, private-scratch escape, missing or
modified receipts/words, and source drift; a Git-free export replays read-only.

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 scripts/research_package.py --package research/qq16-current-frame-consumer
python3.12 -I -B -O research/qq16-current-frame-consumer/verify.py
python3.12 -I -B -O research/qq16-current-frame-consumer/test_verify.py
```

On Windows, point `TEMP` and `TMP` at a writable directory for the temporary
export tests. Source commits, Git blobs and SHA-256 pins are in
[SOURCES.json](SOURCES.json); retained predecessor bytes and attribution are
listed in [PREDECESSORS.json](PREDECESSORS.json). The immutable selected archive
and selected record are unchanged.

## Limits

The eight earlier T arrays must already have been captured and delivered.
This is no retention saving, full 224-input decoder, global controller, physical
runtime estimate, precision bound or new kappa. The 208 maps are charged as
actual full-cover operations; tape movement and recursive placement remain
unpriced. Owned output clears do not license clearing a borrowed helper.

## Open next questions

The next useful steps are to place the new maps and children on actual owners
with a complete stream/precision invoice, and to bind the remaining decoder
components to the current-frame output. [TASK.json](TASK.json) records those
questions, blockers, the original consolidation draw and the justified pivot.

## Credit

Prepared by ywz65 with substantial OpenAI Codex assistance. The new map and two
endpoints build on ywz65's PR2492 native reconstruction (exact head
`9cc0d4d60819ddd246c9db9549f8ae4a61b68e45`) and PR2468 query lowering. Verifier
and native-support code are explicitly adapted from those packages; retained
PR2492 bytes make that reuse inspectable. The L2 identity is credited to
thakrarsagar's [PR2470](https://github.com/CrocSwap/integer-mult-bounds/pull/2470);
the underlying QQ16 contract and local-word source are AliRomman's PR1969.
PR2492 remains correct. New work is Apache-2.0; retained source notices remain.
