# Independent cross-review: fixed affine mask translation

## Decision and pinned scope

**Pass for the stated fixed-mask translation theorem and its direct-leaf invoice.** I found no mismatch in the conjugator direction, coordinate ordering, full-column extension, or complete bounds. This is a read-only review of the frozen package; it does not admit a source MOVE, a selected caller, or any wider assumption.

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.

| Item | Exact pin |
|---|---|
| A freeze manifest SHA-256 | `de2753cb42a012e07aa7ace263bedce5c4be8506ae30ab768af9e165a6edd6e0` |
| `PROOF.md` SHA-256 | `f43040c6331dc29ecf3f435e980cc71f00a60e421f50f4e843192a23e733bd44` |
| `affine.py` SHA-256 | `9387d4caa6ea6ad9e232f4a2a07112fa1a681d34af19e5aae64d1d8adc5ebd2c` |
| #7428 first-slot translation head | `1dbdaa414cfe4a4a0f015e88a04b52e146566786` |
| #7428 retained proof Git blob | `5c6325471aaed465737491870443f063c821b7a0` |
| #7430 fixed CNOT source head | `39b40c465f7636a4bb6d70af28595fe8f70f4f3f` |
| #7430 linear module Git blob | `6aad40a6c47ed4415917c86fabbd5227a3819a41` |

`independent_check.py` authenticates the full A freeze inventory, its proof/source hashes, and the #7428/#7430 source pins before running. It imports no author module or oracle.

## Conjugator and bit order

The fixed offset `b` uses its low nine-bit mask convention: bit `i` means output coordinate slot `i`. For `b != 0`, let `p` be its least set coordinate. The fixed chronological CNOT word first swaps slots 0 and `p` when `p>0`, then applies `j <- j xor p` for each other set bit `j`. The initial swap sends `e_0` to `e_p`; the later gates set exactly the other supported bits without changing `p`. Thus the word matrix satisfies `G e_0=b`. Reversing the word gives `G^{-1}` because each CNOT is an involution.

The literal factor order is `G^{-1}`, then `X_0`, then `G`. In function-composition notation it maps

`x -> G(G^{-1}x xor e_0) = x xor G e_0 = x xor b`.

This direction is correct. Reordering it to `G^{-1},G,X_0` would leave only `X_0`; the package's executed order mutant is an appropriate negative control. Offset zero is a separate identity transaction with no CNOT or reversal. Offset one has an empty conjugator and is exactly the retained first-slot operation.

The apparent endianness hazard is resolved by keeping the two representations distinct. The nine-bit `b` numbers native slots from 0 through 8, with slot 0 the slow/outer coordinate. The flattened address integer stores slot 0 as its most-significant `f`-bit chunk and slot 8 as its least-significant chunk. Consequently the packed address mask is

`sum(((1<<f)-1) << ((8-i)*f) for each set coordinate i in b)`.

This is the right embedding of the source-coordinate mask. It is not an unshifted `b` when `f>1`.

I checked the retained CNOT table against its pair-block geometry. In `linear.py`, the variables named `high` and `low` are set to `min(target,control)` and `max(target,control)`. For each prefix and each middle assignment, row-major pair blocks are `00,01,10,11` for those two coordinate slots; `PREFIX`, `MIDDLE`, and `BLOCK` account for the earlier coordinates, intervening coordinates, and complete suffix/record. The source tables `(0,1,3,2)` when the control is the first slot and `(0,3,2,1)` when it is the second implement the corresponding target-xor-control truth tables. I found no reversed target/control or slow/fast-slot error. The three CNOT swap word is also an exact SWAP on the two selected bits.

## All columns and complete spectators

For every column `j`, write the nine native address bits as `x^(j) in F_2^9`. The unchanged #7430 CNOT body applies each fixed gate to the same bit `j` in both complete `f`-bit slots; the #7428 reversal implements `X_0` on every column because `2^f-1-a_0 = a_0 xor (2^f-1)`. The one-column identity above therefore gives `x^(j) -> x^(j) xor b` independently for every `j`, for every positive `f`.

In packed row-major form, each supported slot's entire `f`-bit chunk is XORed with `2^f-1`. The transformation acts only on the address axis. The `P` outer row, `S` spectator, `c` Gaussian coefficient records, real/imaginary components, and all `w` raw bits remain within the same complete address record. Every signed pattern, including the minimum signed value, is valid because the program moves complete bit records and performs no arithmetic, sign change, scale conversion, or rounding.

The independent checker forms 9-by-9 GF(2) row matrices directly and verifies:

- every nonzero mask `b` has `G e_0=b` and the reversed CNOT word is a two-sided inverse;
- `G X_0 G^{-1}` in the stated chronology equals XOR by `b` for all 512 one-column addresses: 511 masks times 512 addresses, or 261,632 exact cases;
- for `f=2`, all 262,144 packed addresses each pass for offsets 264, 510 and 511, covering separated far slots, a bit-0-absent maximum word, and the full mask;
- for `f=3`, four deterministic full-width coordinate vectors pass for every mask; the universal lift itself follows column by column from the exact matrix identity;
- a direct row-major address-index sanity with `f=2`, `P=S=c=2`, and `w=3` represents 12,582,912 opaque component cells and checks the placement formula for outer rows and S/coefficient/component/width blocks. This is a representation sanity check, not an independent whole-packet routing check or an execution of the emitted tape graph.

The finite identities corroborate the written universal column-lift proof; they do not extend that proof to physical graph execution at `f>1`.

The fixed word length is `popcount(b)-1` when bit 0 is set and `popcount(b)+2` when bit 0 is absent and `b` is nonzero. The maximum is 10 at `b=510`; it has bit 0 clear and support on slots 1 through 8. The bound is correct, and no claim that 10 is a shortest possible implementation is needed.

## Header tail and cutoff

The core X0 translation and fixed CNOT word each consume only the first five Gamma fields `f,c,P,S,w`. The X0 parser returns its header by following its own trace and does not read the next symbol; #7428 already proves the first-slot routine accepts an opaque tail immediately after those five codes. The fixed CNOT routine has the same five-field parser. The HOME adapter is a separate boundary: it copies and returns all six Gamma fields, including the cutoff, without converting the cutoff value into a runtime loop count. Its scans are over the encoded header length `E`.

The retained author observer probes are consistent with this exact boundary. With `E5=11`, cutoff code lengths corresponding to 1, 2, 64, 513 and 4097 represented bits all have identical `681,487` core steps, read offsets only 0 through 10, and maximum header head offset 11. These are source/observer fixtures, not a new cutoff theorem. The core has no cutoff rejection branch because this is a pure address permutation; it preserves the sixth field. The complete bill charges the whole `E6` header.

## Costs and lifecycle

Using the retained complete bounds `T_X <= 4096(V+E5+1)` for X0 and `T_G(k) <= 1024 k f(V+1)+8192(V+E+1)` for a fixed CNOT word, plus the outer `31V+27` transaction, the two conjugator words and X0 sum to

`4096(V+E+1) + 2048k f(V+1) + 16384(V+E+1) + 31V+27`.

For `k<=10`, `f(V+1)<=2fV` and `V<=fV`, this is at most

`61471 fV + 20480 E + 20507 <= 2^20(fV+E+1)`.

At fixed origins, X0, each complete fixed CNOT word, and the outer WORK/TRACE transaction contribute at most `32+64+64+8=168` times `(V+E+1)` visited backing, below the stated core envelope `256(V+E+1)`. Retired cells are not refunded; `K_entry` retains older history. The HOME adapter separately adds at most `128(F+1)` transitions and `64(F+1)` backing, so the combined incremental history bound is `320(F+1)`. B1 full-bank delivery/return, `Setup_b`, fixed program storage, origin provisioning, typed reservation, and caller placement remain separate charges.

I found no hidden count depending on the numerical cutoff, no additional runtime mask dispatch, and no missing CNOT gate in the stated word expansion. These are direct fixed-mask leaf bounds, not the selected nonleaf monomial tariff.

## Novelty boundary and open interfaces

#7428 already supplies the complete first-slot translation, descriptor production, same-owner return, opaque-tail behavior, and its invoice. #7430 already supplies the generic fixed nine-slot CNOT body and fixed-word emitter. The scoped contribution here is their literal composition into an arbitrary construction-time fixed `b` offset in the Gamma6/HOME lifecycle, with the explicit two-word/one-translation invoice. This is a narrow physical interface composition, not new XOR algebra or a first general affine theorem.

The selected rank-one event `24472` (`MOVE 415,3,99,false`) has a right factor with `offset=1` and constant phase `1` in the authenticated recipe at `publication/native-endpoint/research/literal-selected-move-join/reference/RECIPE.json` (SHA-256 `96fadb44c3316be93c6c02f50cd2c841a9541d67b98fd94fc47b73fa64dd404c`). This fixed-mask service covers that offset action alone. It does not supply the nonzero `i^1` constant phase or any complete source monomial/MOVE join.

The theorem begins with a supplied owned Gamma6 packet and the stated blankness/origin promises. It does not supply failure cleanup or retry, an actual source producer, a full selected caller, a nonleaf supplier, an inherited-assumption discharge, or a new `kappa`.

## Replay

From the repository root:

```sh
python3 -I -B worker-c/research/generic-affine-translation-review/independent_check.py worker-a/research/generic-affine-native-translation --write
python3 -O -I -B worker-c/research/generic-affine-translation-review/independent_check.py worker-a/research/generic-affine-native-translation
```

Both modes produce the same `RESULT.json`; `--write` writes only under this review directory. The checker uses explicit `require` checks, does not import the author package, and authenticates the frozen source bytes before its algebraic calculations.
