# No new kappa: complex supplier to 0.015637149 by the best ambient quotient (kernel 153)

**Scoped finite construction with exact replay evidence. Not a multiplication theorem.**
**No new outer kappa is claimed.**

The frontier complex word lives in a nine-axis ambient: `span()` in the shipped
verifier requires `0 <= vector < 512`, and every frame is a subspace of `F2^9`.
For a nonzero kernel `v` the map

```
phi(x) = x xor v when the pivot bit of x is set, then the pivot is dropped
```

is linear and surjective onto `F2^8` with kernel `span{v}`. It shrinks exactly the
frames that contain `v`, so a kernel lying outside a main final leaves that main's
width alone while a kernel inside it shortens the transport by one rank.

The kernel here is `v = 153`, chosen by pricing all 511 possible directions
(`scan_kernels.py`): it is the replay-valid direction with the highest admissible
kappa. Quotienting by it shortens 168 of the 224 main transports. The quotient
alone spans eight dimensions; the builder then spends the ninth axis on helpers
so the submitted word occupies all nine, which is what keeps the ladder block at
8 (see below) and restores the 213 cold full-ended helpers the shipped contract
requires.

**No new outer kappa is claimed.** The outer value is `min(complex, BIT)` and is
unchanged at `0.00302015`; the BIT sets it, and an open PR already carries the
`0.0034` admission. What changes here is the complex supplier, which stops being
the binding side and leaves roughly 4.6x of headroom.

| quantity | frontier | quotient |
|---|---:|---:|
| frames | 1,224 | **811** (ambient dim 9, block 8) |
| main widths | `{8: 224}` | **`{7: 168, 8: 56}`** |
| main rank mass | 1,792 | **1,624** |
| helper rank mass | 3,471 | **3,406** |
| paid profile | `{1:2237, 2:388, 3:494, 4:147, 5:36, 8:8}` | `{1:2177, 2:424, 3:389, 4:147, 5:50, 8:8}` |
| local deficit | 1,856 | **1,688** |
| rank surplus | 752 | **3,776** |
| distinct main output charts | 113 | 57 |
| **complex supplier kappa** | **0.003020165977** | **0.015637149091** |
| outer theorem kappa | 0.00302015 | **unchanged (no new kappa claimed)** |

`+0.012616983`, **+417.8%** on the complex supplier. Both screen constraints hold
at the new kappa (`alpha slack 1.1e-16`, `gamma slack 0.0142`).

## Why the quotient is legitimate

Of the 224 mains, 112 are `1 -> 9` (ending at the full ambient) and 112 are
`0 -> 8`. Under `phi`:

- every `1 -> 9` main becomes **`1 -> 8`** — one rank shorter;
- of the 112 `0 -> 8` mains, the 56 whose final contains `153` become **`0 -> 7`**,
  and the other 56 are unchanged.

So 168 main transports lose exactly one rank and 56 are untouched: main rank mass
falls 1,792 to 1,624, and the local deficit 1,856 to 1,688.

The **block stays 8**. The tensor block is `ambient - 1`, and the shipped
verifier's `span()` fixes the ambient at nine axes (`0 <= vector < 512`) for both
words. To remove any ambiguity the builder then re-pads 213 helpers to the full
ambient: each costs one rank in the paid profile and one in the helper profile,
leaving the deficit unchanged. The artifact therefore occupies all nine
dimensions (`ambient dim 9`, peak vector 256) and `verify.py` asserts
`ambient == block + 1` before pricing. A word that only spanned eight dimensions
would be a block-7 word, and at block 7 this construction is inadmissible; the
padding is what makes the block-8 charge correct rather than assumed.

Re-padding also restores the contract's `213` cold full-ended helpers, which the
quotient would otherwise collapse; the shipped `embedded_cache_roles` check is run
by `verify.py` and accepts the word.

## Evidence

`build.py` writes `QUOTIENT-WORD.json.gz` and `QUOTIENT-PROGRAMS.json.gz` from the
pinned base word and `research/joint-helper-lattice/PATCH.json`. `verify.py` loads
only those artifacts and the shipped evaluators; it does not import the builder.

| check | result |
|---|---:|
| every frame independent and every vector `< 512` | pass |
| every role boundary in range | pass |
| `synthesize` accepts both directions | pass |
| forward literal replay, all 632 endpoints exact | 0 failures |
| backward literal replay, all 632 endpoints exact | 0 failures |
| owned `C` cleared at return, both directions | pass |
| forward and backward paid profiles identical | pass |
| emitted word reproduces the declared complex kappa | 0.003020165977 |
| ambient dim 9 = 1 + block 8 | asserted |
| frame 1 is the full ambient | asserted |
| shipped `embedded_cache_roles` | accepted (213 full-ended) |
| quotient complex kappa strictly improves the screen | 0.015637149091 |

## Reproduce

```sh
python3 -B research/complex-ambient-quotient/build.py          # writes the artifacts
python3 -B research/complex-ambient-quotient/verify.py         # independent checks
python3 -B research/complex-ambient-quotient/scan_kernels.py   # the kernel choice
```

All three are stdlib-only. `build.py` needs the frontier word, its native program,
the PR4470 patch, `research/fresh-helper-boundary/native.py`, and the retained
`CHANGES.json` and `missing-join-frame/PATCH.json` inputs that the patch builds
on. `verify.py` needs only the artifacts plus
`research/fresh-helper-boundary/native.py`,
`research/kappa-rebuild/complex/native_extensions.py` and
`research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py`. The
two-constraint screen is inlined (tail offset `1/5`, cutoff `20`, gamma `0.97`),
so no file outside the base commit is required.

`scan_kernels.py` prices all 511 directions across 8 workers. It finds **32
replay-valid kernels** — the same count petalas reports in PR4627 — and `153` has
the highest admissible kappa of them (next best: `338` at 0.015626864, then `180`
at 0.015624057). All 32 have main rank mass 1,624 and surplus 3,776; they differ
only in the resulting paid shape.

## Contract change required to book the gain

`research/query-thinned-controllers/controller.py:152` asserts

```python
need(surplus == (48*len(thick)-112 if kind == 'complex' else 48*len(thick)-111), ...)
```

That identity is a consequence of every main having width 8. With mains of mixed
width it must become the derived form

```python
need(surplus == ladder_surplus - len(thick)*(mains_rank_mass + centre) - thin_queries, ...)
```

which reduces to the existing identity at width 8. Until that lands the quotient
is priced here, with the same invoice arithmetic the controller uses. The
profiles the controller would need are in `RESULT.json`
(`helper_widths`, `paid_profile`, `main_rank_mass`).

## Open next questions

1. **Can a two-dimensional kernel work?** Petalas reports none of the higher-dimension
   kernels replay. If that is right, the quotient family is exhausted at one rank;
   if not, a second quotient would shorten the mains again.
2. **Do FOUR-base and FOUR-extra admit the same quotient?** Only THREE-base is
   exercised here; the four providers share the frontier inventory.
3. **What is the general surplus identity for mixed main widths?** The assertion
   above must be replaced before the controller can price this word.
4. **How does this compose at the outer `min()`?** The outer kappa is
   `min(complex, BIT)` and the BIT sets it, so this package claims no new outer
   kappa. Raising the outer value needs the BIT side.
5. **Is the redundancy a property of the identity or of this schedule?** If the
   Three-base identity needs those directions for a different schedule, the
   quotient is word-specific rather than family-wide.

## Attribution

Built on `research/kappa-rebuild/complex/full-identity-certificates`
(THREE-base full-identity canonical word and native program),
`research/joint-helper-lattice` (PR4470 helper boundary and patch, source head
`322e0ec764aa7ef7801383feb1f656e460dd8bed`), and the shipped evaluators of
`research/kappa-causal-continuation/buffer-borrowing` and
`research/kappa-rebuild/complex`. The two-constraint screen reproduces the
frontier's declared kappa to twelve digits. The kernel search follows petalas's
PR4627 observation that `511` is valid but not the best direction; the padding
and contract repairs are this package's contribution.

Apache-2.0; substantial AI assistance.
