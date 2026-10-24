# PR5270's physical replay reference does not match its priced controller

Author-checked independent audit for ahrazzle, prepared with substantial OpenAI
Codex assistance. Apache-2.0. Not yet independently reviewed; no selected-result change.

At PR5270 head `df9e5037587ce0cfbd23c2a944515526b301e820`, the physical
listing and its `standard()` reference agree with each other, but that reference
is not the formal thinned controller whose invoice the package prices.
This is an exact finite counterexample to that binding, not an impossibility
theorem for coded suppliers.

From this package directory, using the Python 3 standard library:

```sh
python3 -B verify.py
```

Runtime here: about 0.12 seconds. `RESULT.json` records the result.
`SOURCES.json` authenticates unchanged source exports by SHA-256 and records
their canonical URLs and Git blob IDs. The two PR5270 blob IDs also agree with
the GitHub PR-files response; the retained controller blob is the PR's own
source-manifest pin.

## The four-role counterexample

Take p=2, pattern `T`, with thick stage set `{1,3}`. Specialize the central
letter to `q=1`, the two thick letters to `D1=D3=i`, and thin even letters to 1.
The retained formal Laurent-polynomial controller, followed by its retained
`thin()` function, gives

```text
[-1  0  0  0]
[ 0 -1  0  0]
[ 0  0  i  0]
[ 0  0  0  i].
```

The actual PR5270 listing's uncoded reference gives

```text
[-i   0     0   1-i]
[ 0  -i   1-i     0]
[ 0   0    -1     0]
[ 0  -i   2-i    -1].
```

All entries above are exact Gaussian integers. The difference is not a rounding
effect or a missing global phase: several entries that should vanish are nonzero.

A separate direct calculation of the actual reference on the fourth role input
`e3` gives `(1-i, 0, 0, -1)`, while the formal controller gives `i e3`.
On this eigenvector both the rank-eight D and the full rank-nine R have
eigenvalue i, so this counterexample does not rely on their separate rank mismatch.

Three transcription differences are individually discriminated:

1. In the forward loop, the source formal `bridge(dst,src,c)` updates the odd
   role at `src` from the odd role at `dst`, with coefficient `-c`. The p19
   listing and its `standard()` reverse this direction. The final reverse sweep
   already has the correct direction; blindly reversing every odd bridge is
   not the repair.
2. The middle idle belongs to even stage 2 and becomes identity after thinning.
   The listing applies `R` instead. The p19 invoice independently drops this
   rank-zero call, while the listing applies 18 such nonidentity idles.
3. The p2 terminal idle covers stages `{3,4}`, of which only 3 is thick. Its
   specialization is `R`, while the listing uses the unthinned interval length
   and applies `R^2`. The same stage-count versus thick-stage-count mismatch
   affects initial and terminal intervals at p19.

The checker uses two differently represented computations. One executes only
the authenticated retained formal controller/thinning functions on sparse
Laurent polynomials and then specializes them exactly. The other interprets
the emitted listing with Gaussian-integer matrices. To bind the latter to the
actual physical source rather than merely our reading, it also executes the
retained `standard()` and Gaussian butterfly on the genuine 512-address vector
`v[x]=(-1)^bit_1(x)`. The central Q fixes this vector and the full R multiplies
it by i. Four basis-role inputs recover the complete displayed 4-by-4 matrix,
using exact arithmetic modulo 65537 with i=256. Every output address is checked.

At p19 the same exact specialization has 351 differing matrix entries.
Correcting only the reference's bridge directions and idle thinning restores
agreement with the formal controller for both p2 and p19. Leaving any one of
the three p2 defects in place is rejected. These are consistency controls, not
supplier admission.

## Remaining scope

Even after these transcription repairs, a separate physical binding is needed.
The retained native backward endpoint in `coded-native-caller/PHYSICAL.md` has
diagonal factor D of rank eight. The p19 listing uses full rank-nine R because
its gauge commutes with R but not D. Its finite replay also reuses one
9-coordinate address block, whereas the invoice uses independent thick blocks
and maximum target rank153. This audit does not prove that substitution legal,
price any extra Q transformations, implement code gauges on independent blocks,
or establish the complete native helper/precision/compiler interface. We make
no claim that every possible correction loses.
In particular, the mismatch does not rule out a newly proved boundary
normalization and revised invoice for the altered word.

The geometric tail change from 19/20 to 97/100 is not the immediate obstruction:
the general higher-moment theorem allows any rational limits below one that
satisfy the complete charged inequality. Likewise, a sufficiently larger
logarithmic compiler power can remove the *fixed-power* numerical cap once a
valid native unit is established. Neither arithmetic repair binds this altered
physical word to the claimed invoice.

## Open next questions

- First correct the bridge and idle transcription in a new successor package,
  and compare the corrected path against the formal stage-labelled controller.
- Then bind one actual rank-eight native reverse invocation, its necessary
  code changes and independent-block spectators to that path, charging every
  additional Gaussian child. The present full-R gauge identity is insufficient.
- Only after that binding, recalculate the complete paid/target profiles and
  use the generic tail/compiler theorem with newly certified constants.

Credit: DaysSky for PR5270's listing and physical gauge work; Cayden Burkart /
SethBurkart123 for PR4940's formal coded controller; Dillon for PR4933's
physical normalizers; Dugongue / mdumitrean for PR4929's center-free producer;
Cinna Davis, Cao Yifan, zxv, Jacob Alan Sussman and the retained native,
controller, compiler and outer contributors for the predecessor construction.
The source exports retain their notices. This audit's addition is the exact
source-bound reference/invoice mismatch and its independent eigenvector check.
