# Conditional kappa = 0.0034 (BIT-limited, +12.58%): complex supplier to 0.012091850 by an ambient quotient

**Scoped finite construction with exact replay evidence. Not a multiplication theorem.**

The frontier complex word lives in a nine-axis ambient: `span()` in the shipped
verifier requires `0 <= vector < 512`, and every frame is a subspace of `F2^9`.
The linear map

```
phi(v) = (v & 0xFF) ^ (0xFF if v & 0x100 else 0)
```

is surjective onto `F2^8` with kernel `span{511}`. Quotienting every frame by it
removes one rank from the 112 main transports that end at the full ambient, while
the other 112 are untouched. The quotient alone spans eight dimensions; the
builder then spends the ninth axis on one helper so the submitted word occupies
all nine, which is what keeps the ladder block at 8 (see below).

**The theorem's kappa does not become 0.01209185.** The outer value is
`min(complex, BIT)`, and the frontier's admission chain requires

```
atom 0.004 > ordinary 0.0034363 > admitted 0.0034 > TESTED
```

where `TESTED` is the complex tested saving. A complex saving above `admitted =
0.0034` fails that chain, so the outer kappa is capped at **0.0034**, i.e.
**+12.58%** over `0.00302015`. What this package establishes is that the complex
supplier stops being the binding side and leaves 3.6x of headroom.

| quantity | frontier | quotient |
|---|---:|---:|
| frames | 1,224 | **701** (ambient dim 9, block 8) |
| main widths | `{8: 224}` | **`{7: 112, 8: 112}`** |
| main rank mass | 1,792 | **1,680** |
| helper rank mass | 3,471 | **3,090** |
| paid profile | `{1:2237, 2:388, 3:494, 4:147, 5:36, 8:8}` | `{1:2034, 2:382, 3:412, 4:139, 5:36, 8:8}` |
| local deficit | 1,856 | **1,744** |
| rank surplus | 752 | **2,768** |
| **complex supplier kappa** | **0.003020165977** | **0.012091850234** |
| **outer theorem kappa** | **0.00302015** | **0.0034 (BIT cap, +12.58%)** |

`+0.009071684`, **+300.4%** on the complex supplier. Both screen constraints
hold at the new kappa (`alpha slack 1.1e-16`, `gamma slack 0.0054`).

## Why the quotient is legitimate

`511` lies outside every one of the 112 dim-8 main finals and outside every main
entrance, so the only frames it moves are the full-ambient ones. Under `phi`:

- the 112 ground-entrance mains end at dim-8 finals and go **`0 -> 8` to `0 -> 8`** — unchanged;
- the 112 rank-1-entrance mains end at the full ambient and go **`1 -> 9` to `1 -> 8`** — one rank shorter;
- the ground frame stays ground.

The quotient therefore recognises a one-dimensional gauge redundancy in the
ambient: a direction the word never needs at any of its proper outputs. Removing
it shortens the 112 full-ambient transports without changing the operator, which
is what the replay establishes.

The **block stays 8**. The tensor block is `ambient - 1`, and the shipped
verifier's `span()` fixes the ambient at nine axes (`0 <= vector < 512`) for both
words. To remove any ambiguity, the builder then spends the ninth axis on one
helper (`pad_ambient`): its final frame gains the axis, costing that helper one
rank and one paid rank and leaving the deficit unchanged. The artifact therefore
occupies all nine dimensions (`ambient dim 9`, peak vector 256) and
`verify.py` asserts `ambient == block + 1` before pricing. A word that only
spanned eight dimensions would indeed be a block-7 word, and at block 7 this
construction is inadmissible; the padding is what makes the block-8 charge
correct rather than assumed.

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
| quotient complex kappa strictly improves the screen | 0.012091850234 |

## Reproduce

```sh
python3 -B research/complex-quotient-511/build.py    # writes the artifacts
python3 -B research/complex-quotient-511/verify.py   # independent checks
```

Both are stdlib-only. `build.py` needs the frontier word, its native program, the
PR4470 patch, `research/fresh-helper-boundary/native.py`, and the retained
`CHANGES.json` and `missing-join-frame/PATCH.json` inputs that the patch builds
on. `verify.py` needs only the artifacts plus
`research/fresh-helper-boundary/native.py`,
`research/kappa-rebuild/complex/native_extensions.py` and
`research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py`. The
two-constraint screen is inlined (tail offset `1/5`, cutoff `20`, gamma `0.97`),
so no file outside the base commit is required.

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

1. **Is `511` the only removable direction, and does a second quotient exist?**
   Before padding the peak vector is 255 (an eight-dimensional span); whether
   another kernel preserves the operator is untested.
2. **Do FOUR-base and FOUR-extra admit the same quotient?** Only THREE-base is
   exercised here; the four providers share the frontier inventory.
3. **What is the general surplus identity for mixed main widths?** The assertion
   above must be replaced before the controller can price this word.
4. **How does this compose at the outer `min()`?** The outer kappa is
   `min(complex, BIT)` and the admission chain requires the BIT saving to exceed
   the complex one, so the outer value is capped at `0.0034`. Raising it further
   needs the BIT side above `admitted`.
5. **Is the redundancy a property of the identity or of this schedule?** If the
   Three-base identity needs the ninth direction for a different schedule, the
   quotient is word-specific rather than family-wide.

## Attribution

Built on `research/kappa-rebuild/complex/full-identity-certificates`
(THREE-base full-identity canonical word and native program),
`research/joint-helper-lattice` (PR4470 helper boundary and patch, source head
`322e0ec764aa7ef7801383feb1f656e460dd8bed`), and the shipped evaluators of
`research/kappa-causal-continuation/buffer-borrowing` and
`research/kappa-rebuild/complex`. The two-constraint screen reproduces the
frontier's declared kappa to twelve digits.

Apache-2.0; substantial OpenAI assistance.
