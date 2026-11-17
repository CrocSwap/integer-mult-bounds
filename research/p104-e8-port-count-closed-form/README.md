# A closed form for E8 port counts in subspaces (no κ)

**Scoped written proof with exhaustive finite corroboration. No new κ.**
This answers the first half of open question 1 of PR #6861
(`research/p104-e8-subspace-invariants`, DreamingOfClouds): derive the
ports-per-dimension law `N_e = 2^(e-2) + 4` for `4 <= e <= 7` from the
radical of `B|V` and the restriction of `q` to `V`, and explain why it
stops at `e = 8`. Nothing is priced and no word is constructed.

## Result

Setting as in PR #6861: `F2^9`, `q(x) = C(wt x, 2) mod 2` with polar form
`B`, even hyperplane `E`, and P120 the odd vectors with `q = 1` (weights
3 and 7). `N(V)` is the number of ports in a subspace `V`.

For a subspace `V` of dimension `e`, let `R` be the radical of `B|V`,
`rho = dim R`, `delta = 1` if the all-ones vector lies in `V` and `0`
otherwise, `q' = q + (wt mod 2)`, and let `sigma`, `sigma'` be the sums of
`(-1)^q` and `(-1)^q'` over `V`.

1. **Closed form.** If `V` is not inside `E`, then
   `N(V) = 2^(e-2) + (sigma' - sigma)/4`, where `sigma^2 = 2^(e+rho)` if
   `q` vanishes on `R` and `0` otherwise, and the same for `sigma'` and
   `q'`. So the bias `N(V) - 2^(e-2)` is `(s' - s) 2^((e+rho)/2 - 2)` with
   `s, s'` in `{-1, 0, 1}`.
2. **Constraints.** `e + rho <= 8 + 2 delta`. If `delta = 1` then
   `sigma' = 0`. If `e + rho = 8 + 2 delta` and `q` vanishes on `R`, then
   `sigma = 2^(4 + delta) > 0`.
3. **Bound.** `N(V) <= 2^(e-2) + 4` for every subspace of every
   dimension, with equality in exactly three listed radical classes, and
   `N(V) <= 64` at `e = 8`.
4. **Ports per dimension.** For every subset `S` of P120,
   `N_e(S) <= min(2^(e-1), 2^(e-2) + 4)`. For P120 and for P104 this is
   attained at every `e = 1..7`:

   | e | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
   |---|---|---|---|---|---|---|---|---|---|
   | `min(2^(e-1), 2^(e-2)+4)` | 1 | 2 | 4 | 8 | 12 | 20 | 36 | | |
   | `N_e(P120)` | 1 | 2 | 4 | 8 | 12 | 20 | 36 | 64 | 120 |

The pattern stops at `e = 8` because there `rho = 2 delta` is forced, so
every subspace is at the cap of item 2 and has `sigma >= 0`; the bias is
then at most `0`. Item 3 also recovers the saturation depth of PR #6861
Theorem 1, since a saturated subspace needs `N(V) = 2^(e-1)`.

Statements and proofs are in [PROOF.md](PROOF.md). The proofs use two
identities, `B(x,y) = x . (y + (wt y mod 2) 1)` and
`sum over F2^9 of (-1)^q = 32`, and no enumeration. Attainment in item 4
uses seven explicit bases and is a finite check.

## Census

`verify.py` visits all 8,283,458 subspaces of `F2^9`. Of these 417,199
lie inside `E` and have no port. The other 7,866,259 fall into 98 classes
`(e, delta, rho, sign sigma, sign sigma', N)`, listed with their sizes in
[CENSUS.json](CENSUS.json). Subspaces attaining `2^(e-2) + 4`, by the
equality case of Theorem 3:

| e | case 1 (`delta=1`, `e+rho=8`) | case 2 (`delta=0`, `e+rho=8`) | case 3 (`delta=0`, `e+rho=6`) | total |
|---|---:|---:|---:|---:|
| 4 | 0 | 2,025 | 9,450 | 11,475 |
| 5 | 3,150 | 28,350 | 75,600 | 107,100 |
| 6 | 7,560 | 37,800 | 40,320 | 85,680 |
| 7 | 1,120 | 4,320 | 0 | 5,440 |

At `e = 8`, 255 hyperplanes hold 64 ports. For `e = 1..4` the maximizers
are the saturated subspaces, and their counts 120, 7,140, 32,130 and
11,475 agree with the P120 row of PR #6861 Theorem 1. The `N_e(P120)`
row above agrees with PR #6861 Theorem 2.

## Reproduce

From the repository root, with CPython 3.12 (standard library only):

```sh
/path/to/python3.12 -I -B -W error research/p104-e8-port-count-closed-form/verify.py
/path/to/python3.12 -B scripts/research_package.py --package research/p104-e8-port-count-closed-form
```

Expected last line: `PASS_P104_E8_PORT_COUNT_CLOSED_FORM`. One run takes
about 20 seconds. The verifier

- checks the form facts and both identities on all 512 by 512 pairs;
- computes `N`, `sigma`, `sigma'` and `R` for every subspace and requires
  each clause of Theorems 1 to 3;
- recomputes the same invariants from first principles, with no masks and
  no use of the identity `B(x,y) = x . tau(y)`, on 3,094 subspaces: all
  those of dimension 0, 1, 8 and 9 and a fixed-stride sample of the rest;
- requires the class census to equal `CENSUS.json`, and the equality
  classification of Theorem 3 on every class;
- checks the seven P104 witnesses by direct enumeration;
- runs five rejecting controls: a wrong port count, a wrong radical, a
  negative sign at the radical cap, a mutated census row, and a witness
  with one of its ports removed from P104.

`verify.py --write-census PATH` regenerates `CENSUS.json`.

## Scope and limits

- This is a statement about port sets. It supplies no word, helper
  split, invoice or supplier, and the selected frontier is unchanged.
- The signs `s, s'` are determined by `V` but are not expressed here
  through `rho` alone. They are the types of the nondegenerate forms that
  `q` and `q'` induce on `V/R`; only the constraint at the cap (item 2)
  is proved and used.
- For P104 the proof gives `N_8 <= 64`. The exact value 60 is PR #6861's
  exhaustive result and is not derived here.
- The flag-rectangle masses, the second half of the same open question,
  and the star law are not addressed.
- The 5561 port list is read from
  `research/p104-designer-toolkit-v2/words/5561.json.gz`, pinned in
  [SOURCES.json](SOURCES.json). It is used only for the seven witnesses.
- `verify.py` is iterative, with a node budget equal to the exact number
  of subspaces of dimension at most 4. Its work stack peaks at 953
  frames of at most 16 elements each. Functions stay below 60 lines.
  Python-managed allocation is bounded by those sizes. No separate
  static type check was run.

## Open next questions

1. **Flag masses.** Does the class table give the flag-rectangle maxima
   of PR #6861 Theorem 4 (32 at every level, 36 at level 5) in closed
   form? The product `N(g) N(A^perp)` couples the class of `g` with that
   of `A^perp`. A first step is to express the radical of `A^perp`
   through `A` with `B(x,y) = x . tau(y)` and list which class pairs can
   occur for a hyperplane `g` of `A`. The joint constraint is not derived
   here.
2. **Star law.** The same question for `max N(V) N(V^perp)`, which
   PR #6861 Theorem 3 finds equal to the port degree. The classes of `V`
   and `V^perp` are linked by the same identity.
3. **P104 at dimension 8.** PR #6861 finds `N_8(P104) = 60`, so each
   of the 255 hyperplanes with 64 ports of P120 loses at least four ports
   in P104. Which property of the 16 removed ports forces that? Start by
   splitting the 255 hyperplanes into their two classes (135 with
   `delta = 0`, 120 with `delta = 1`) and counting removed ports in each.
4. **Other E8-type port sets.** The proof uses only the form, so the
   bound holds for every subset of P120. For which punctures is it still
   attained at every `e <= 7`? This is the witness side of PR #6861's
   question 3.

[TASK.json](TASK.json) gives the structured questions and scope change.

## Credit

This package was produced by Nick Petalas. The setting, the port sets,
the quadratic form `q`, the exhaustive `N_e` tables, the saturation
theorem and the open question answered here are from DreamingOfClouds,
PR #6861. The 5561 port list is from `research/p104-designer-toolkit-v2`.
New here: the closed form for `N(V)`, the constraints at the radical cap,
the bound `2^(e-2) + 4` with its equality classes, and the class census.
New work is Apache-2.0.
