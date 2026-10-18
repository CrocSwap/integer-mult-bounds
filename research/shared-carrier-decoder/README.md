# A physical complex P111 decoder with one nonzero COPY endpoint

This package builds and executes two exact complex decoder modules on the same
111 data pairs and 452 dirty helper streams. The changed decoder has a smaller
complete recursive moment on `0 <= b <= 1/256`. It also uses **108 more scalar
AXPY scans**. No runtime gain, selected-supplier gain, or new kappa is claimed.

The copied-rank value 63 is prior work. The new result is its explicit physical
word: source access, old-value compensation, exact Clifford phases, a nonzero
COPY endpoint, all helper tails, and arbitrary dirty-helper restoration. The
coordinate decoder is an executable baseline with the same physical endpoints
and helper stock. The changed word pays three unused rank-nine helper tails.

| Paid quantity | Coordinate baseline | One replacement | Change |
|---|---:|---:|---:|
| Copied rank | 64 | 63 | -1 |
| All positive recursive children | 1578 | 1627 | +49 |
| Complete rank mass | 5908 | 5907 | -1 |
| Scalar AXPY scans | 3552 | 3660 | **+108** |
| Nonunit dyadic scalar multiplications per address | 888 | 1014 | +126 |
| Each of P, D, X, and global-phase adapter scans | 3156 | 3254 | +98 |
| Original streams | 674 | 674 | 0 |
| Peak temporary complex streams | 1 | 1 | 0 |

Write `H_r` for one recursive child of rank `r`. The complete profiles are

```text
baseline:  896 H_1 + 444 H_7 + 238 H_8
candidate: 945 H_1 + 497 H_7 + 182 H_8 + 3 H_9.
```

For a child price `r(m/r)^b`, their difference is strictly negative throughout
`0 <= b <= 1/256`, including the selected complex exponent
`0.001664727258740678855772` at the pinned base. This is a statement about the
recursive part of the invoice. The extra scalar and adapter work stays in the
full recurrence. See [COST.md](COST.md).

## Reproduce

Base: `8bddbee377e2f3ce1f1247196c4b290d55767d20`. Use Python 3.10 or later and
its standard library. Run from the repository root:

```sh
python3 -I -B research/shared-carrier-decoder/verify.py
python3 -I -B research/shared-carrier-decoder/test_controls.py
```

The first command checks the committed [EXPECTED.json](EXPECTED.json). Its last
line is:

```text
PASS_SHARED_CARRIER_DECODER copies=64->63 columns=674 axpys=3552->3660 interval=[0,1/256] no_new_kappa
```

The second command rejects 11 broken constructions and three bad receipt cases. Its last line is:

```text
PASS_SHARED_CARRIER_CONTROLS controls=14
```

Use `--out /new/directory` with `verify.py` to write both complete words, all
native lowering records, and a certificate. The directory must not exist.
`EXPECTED.json` is required. Receipt comparison rejects Boolean or float values
in integer fields. `-O` is supported. The pinned compiler's assertions stay
enabled under `-O`.
The package also runs after it is copied outside the repository.
[VALIDATION.md](VALIDATION.md) records the completed checks and the separate
second-input review.

## Evidence and scope

- `model.py` constructs the E8 labels, the changed decoder, and both literal
  words. It does not import an existing cost-63 witness.
- `verify.py` checks all 674 independent logical input columns, including every
  dirty helper. A separate integer column interpreter checks the forward map.
  It checks the full frame schedule and every native child, including its exact
  phase. The certificate binds the emitted words and lowering records by hash.
- `physical.py` executes each whole physical word and its inverse transpose on
  one dense Gaussian input across 674 streams of 512 values. It also checks all
  512 matrix columns of the rank-seven COPY. The whole-word dense input is a
  finite execution check. The all-input conclusion uses the composition proof
  in [PROOF.md](PROOF.md), together with the exact scalar and operator checks.
- The physical word uses in-place scalar loops, permutation cycles, phases,
  translations, and C pairs. It needs one temporary complex stream. Address
  tables contain fixed integers, not input-dependent complex data.
- Helpers recover their logical input at the advertised final FULL frame.
  Their physical output is `F h`, not the same physical array `h`.

This is a complete finite decoder module for the normalized Gram shear
`Y += G X`, where `G[t,i] = <r_t,r_i>/2`. It is not a full supplier for
`Y += X`. It does not supply the remaining side corrections, a host owner map,
an all-size tape or rounding proof, or an outer bound assembly. The finite
routing bound in COST.md is explicit and quadratic; it is not a linear tape
admission. All selected files and `upstream/` stay unchanged.

[NOTICE.md](NOTICE.md) gives the predecessor credit and overlap check. New
material was prepared for Ali Romman (@aliromman) with substantial OpenAI Codex
assistance. No independent human review is claimed.
