# Independent paired-block derivation

The four paired extractions in PR2942 compose correctly on both fixed providers.
The ordered dirty-input change is `S1 S2 S3 S4`; its target compensation is
`C0 S1 S2 S3 S4`. The 82 inherited restored helpers remain isolated at every
stage, and the final non-target middle has 86 complete identity row/column blocks.
This is an independent exact finite source check, with a written general block
argument. It establishes no new kappa or native, allocation, or outer admission.

The source is PR2942 commit
`a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf`. The eight compressed word/transform
inputs have fixed SHA256 pins in `independent.py`; that program reads no producer,
structure checker, historical auditor, or primary verifier. The checkout base is
`6e1bbb4a489cb7d05bf592a043d5d353eb767e4a`. The construction is Marius-Paul
Dumitrean's composition of Jeremy Diviney's paired-extraction mechanism on Mason
Hale's PR2917 words, with Jeremy Kothe's supplier/cleanup lineage. This independent
check was prepared for Ross Richardson with substantial OpenAI Codex assistance.
All source and new code retain Apache-2.0 licensing.

## Exact model and derivation

Use independent coordinates for the 112 data registers and 408 live dirty helpers.
These 520 non-target coordinates are arbitrary. The 112 target registers are
omitted from this middle only after checking that no non-target primitive reads a
target. The word's 72 warp occurrences are distinct noncommuting symbols `K_j`.
Coefficients lie in the rational group algebra; the tested middles use positive
letters only, so their words are represented exactly without group reduction.
There are no numerical samples or floating-point tolerances.

For stage `k`, let `M` be the current middle, from immediately after the inherited
prelude through the restore section. It includes every literal non-target A/B
gate and each warp at its actual B position. Before testing it, the checker
validates every frame-edit preimage against the current word and applies that
stage's frame substitutions. These substitutions do not change the operator
coefficients. Scalar input gates inserted at the beginning define `S`, and output
gates appended to restore define `T`. The new middle is therefore `T M S`.

For pivot `h`, define directly from the scalar gate lists

```
v = S e_h,       alpha = e_h^T T,       y = T^-1 e_h.
```

The independent checker pushes `v` forward through `M` and pulls `alpha` backward
through `M`. The latter computes `u = alpha M` without constructing a full matrix
for `M`. A forward warp prefixes its symbol to each word; a backward pullback
suffixes it. Coefficients use Python `Fraction`, independently of the primary
verifier's integer row-denominator representation. Every coefficient of the
resulting row is retained, including all dirty-helper columns and all data
columns. The checks establish

```
M v = y,        alpha M = u,       u S = e_h^T,
alpha y = 1,    T y = e_h,         C v = 0.
```

The definitions also give `S e_h = v` and `e_h^T T = alpha`. Consequently,

```
(T M S)e_h = T y = e_h,
e_h^T(T M S) = alpha M S = u S = e_h^T.
```

Thus both the pivot's complete output row and its complete input column are the
identity, on arbitrary non-target inputs. Furthermore `(C S)e_h = C v = 0`.
The script verifies that `u` and `v` are supported on the actual eligible dirty
helpers: removed helpers, entering helpers, inherited restored helpers, and
initial-correction source registers are excluded. A zero entrance frame does
not mean a zero input value.

For previously restored pivots, the checker does not rely only on support
arguments. It pushes all their independent basis columns together through the
complete current middle and separately pulls all their output covectors backward.
Both resulting blocks must be the identity at baseline and after every stage.
This tests interference even when stages share other helper registers.

Let `S_k` and `T_k` denote the four stages in their declared order. Chronological
input lists are prepended at each stage, so the final prefix is executed as
`before4, before3, before2, before1`. Matrix multiplication acts on column inputs
from the right, giving

```
M4 = T4 T3 T2 T1 M0 S1 S2 S3 S4,
C4 = C0 S1 S2 S3 S4.
```

The checker computes the right product by scalar covector pullbacks and also
checks every column of the entire 520-by-520 input transformation by direct
chronological prefix execution. It compares all 112 compensation rows against
the fixed final WORD file. This is a complete coefficient comparison, not a
checksum or row-sum fingerprint. It separately binds final A, B, restore, warp,
and helper-end sections to the supplied final words. Complete target behavior,
inverse cleanup, and inverse-transpose behavior belong to `verify.py`.

## Finite coverage and controls

Both `base` and `extra` providers pass. Their printed witnesses agree; this is
verified execution of both inputs, without assuming provider equivalence.

| Stage | Pivot | Middle gates before insertion | y | Endpoints after insertion |
| --- | ---: | ---: | --- | ---: |
| 1 | 249 | 4829 | `-4 e_62` | 83 |
| 2 | 267 | 4867 | `-4 e_63` | 84 |
| 3 | 251 | 4907 | `-4 e_61` | 85 |
| 4 | 265 | 4946 | `-4 e_94` | 86 |

At baseline and all four endpoints, both full restored row/column blocks are
checked over 520 independent non-target coordinates. Each of the eight paired
certificates covers every such coordinate. The final input change has 36
nonidentity rows. Each final compensation map has 112 rows and 5980 nonzero terms.
All assertions use explicit exceptions and remain active with Python `-O`.

Each provider rejects four real changes at the named predicate:

- Reversing the stage order changes the chronological input prefix and fails
  the compensation comparison.
- Using `C0 S_total^-1` fails the compensation comparison.
- Keeping stale `C0` fails the compensation comparison.
- Adding an actual stage-2 input read `267 += 249` causes the complete restored
  endpoint column block to fail. Helper 249 carries arbitrary prior input dirt.

An equivalent presentation is accepted: the first actual prefix addition is
split into two equal half-additions, and its complete 520-by-520 prefix matrix
still equals the ordered product. A negative control is counted only if its
intended predicate rejects; unexpected acceptance raises outside the caught
exception. The two modified chronological lists are checked to differ from the
original before their controls run.

Reproduce from the repository root:

```sh
python3 -I -O -B research/normal45-joint-restoration/independent.py
```

The single deterministic JSON line includes every exact `u`, `v`, `alpha`, and
`y` witness. Expected marker: `PASS_NORMAL45_INDEPENDENT_PAIRED_BLOCKS`.

## Limits and independent review of the whole-word interface

This finite computation proves the identities for these fixed literal words.
The displayed block derivation applies to any operators satisfying the checked
identities, but this is not a synthesis theorem for other words or parameters.
It does not check physical Clifford phases, all frame-chain admission, prefix
precision bounds, source/tape implementation, owners, stock, paid moments,
asymptotic transfer, or a larger exponent saving. Source credit and inherited
premises remain necessary. No formal-kernel proof is supplied.

Read-only cross-review of `verify.py` found its correction order correct. If
`W = K_a ... K_b` and `D_j = K_j^-T`, then the inverse-transpose of the shear
`target += q W source` is `source -= q W^T target`, where
`W^T = D_b^-1 ... D_a^-1`. The implementation visits `-D_a, ..., -D_b` and
left-multiplies each, yielding that required reversed word.

The whole-word check permits arbitrary original inputs and declares the private
cleanup slots initially zero. It must not be described as arbitrary dirty private
workspace. For a full invertible operator `F`, the forward restricted contract
`F(x,0)=(A x,0)` only gives `F=[[A,B],[0,D]]`. Its inverse-transpose on the same
subspace has private component `-D^-T B^T A^-T x`. Checking its zero return is
equivalent to `B=0`; it detects cross-block behavior invisible in the forward
zero-buffer subspace. Even both checks establish no identity requirement on `D`
and no restoration theorem for arbitrary nonzero private inputs. The primary
checker's forward-invisible first-cleanup omission is a useful control for this
distinction, rather than evidence of a defect in the supplied construction.
