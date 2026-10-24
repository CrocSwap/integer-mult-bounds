# All-width certificate for the complete selected #5413 caller

**Scoped positive result; no new κ.** The complete caller identity of
[PR #5413](https://github.com/CrocSwap/integer-mult-bounds/pull/5413) holds at every positive column multiplicity,
and the proof is a census of exact group elements that a small checker verifies. This is target 8 of
[PR #5428](https://github.com/CrocSwap/integer-mult-bounds/pull/5428): compact all-width native identity
certificates. It discharges the algebraic half of the retained assumption `native_all_columns` for the selected
caller; the physical half (tape realization of the lifted operators with spectators and adapters at the retained
tariff) is left explicit and untouched.

## Lemma

For a finite group `G` of exact matrices and fixed coefficients `c_g`,

    sum_g c_g g^{(x) f} = 0 for every f >= 1    <=>    sum_g c_g g = 0 in C[G].

The map `g -> g^{(x) f}` is a group homomorphism, so group identities and free-word identities lift; by Burnside a
nonzero element of `C[G]` fails at some width. [PROOF.md](PROOF.md) gives the proof and the three consequences
used. The census replaces the finite width cutoffs of [PR5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369)
and [PR5376](https://github.com/CrocSwap/integer-mult-bounds/pull/5376) whenever the elements can be canonicalized,
which `clifford_exact.py` does (Pauli tableau plus the image of `|0>`, fixing the absolute phase).

## What [verify.py](verify.py) certifies

| Layer | Identity | Count | Lifts because |
|---|---|---|---|
| Ports | `x->X = D`, `y->Y = D`, `y->X = D C_0`, `Q_p = C_0`, both orientations, absolute phase | 896 | group identities |
| Body | free-word endpoint of `NEUTRAL-BACKWARD-v16c` with `PROVIDER_5402` expanded: all warps cancel, main rows carry only the port wrappers, 400 autonomous helpers under exact signed alias monomials (318 pure phases, 82 with address action) in their recorded exit frames, 8 mode outputs `C8 (h - Z y)`, 17 owned fields zero | 649 rows | free-word identity |
| Controller | Laurent replay in free commuting `Q, D_1..D_33` reproduces the diagonal; 18 private planes disjoint and disjoint from axis 0; `C_0^2 = X_0`, `C_0^-1 X_0 = C_0`, `[C_0, D] = 0` exact | 32 banks | commutative identity, abelian realization |

Backward uses the entrywise-conjugate semantics of PR5376 `PROVIDER.md`. Reading the backward wrappers against
unconjugated charts gives a different element on every port (port 0: `-C_0^-1 Z_1 Z_2`), so the convention is part
of the certificate.

Controls on dense `Q(i)` matrices: the Reynolds-type relation `C_0 = (1+i)/2 I + (1-i)/2 X_0` and the scalar trap
`i = iI` vanish at width 1 and fail at width 2 while the census counts three and two distinct elements; exponent two
(`C_0^2 = X_0`) is one element and lifts; reversed noncommuting factors differ already at width 1.
[test_verify.py](test_verify.py) rejects eight mutations.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/allwidth-caller-certificate
```

`verify.py` runs in about 40 seconds with the standard library. `RESULT.json` is rebuilt and compared.

## Open next questions

- The physical half of `native_all_columns` for this caller: can the distinct exact group elements used (wrappers,
  `D`, `C_0`, `X_0`, the plan's `J` routes) be reduced to a finite list of fixed-tape primitives whose cost at width
  `f` is the retained tariff? This is target 10 of PR #5428, not a symbolic certificate.
- The same census for the forward body (`NEUTRAL-FORWARD-v16c`, review only; it does not run in the selected
  controller).

## Not claimed

No new κ, no selected-record change, no physical tape implementation, no independent human or kernel review.
Credit: PR5413 (Clear1nsight), PR5402 (dillona), PR5383/PR5398 (aliromman), PR5369/PR5376 (aliromman) for the
width-cutoff theorems and the orientation semantics, the Clifford compiler lineage, and PR5428 (zxv) for the target.
Prepared with substantial Claude Code assistance.
