# Later-source compact controls: repair with inactive saturated digits

**Scoped mathematical audit and guard improvement; no new kappa.**

The unchanged later-source compact-control word can safely retain some
saturated dirty temporary digits. This package proves a sufficient invariant
guard for every `n>=1,G>=1,K>=G+1,0<=rho<K`, together with its exact two-state
counting formula. For one processed digit only, it also proves that this
guard is the largest invariant subset of full-map agreement.

At `n=2,K=6,G=2`, the safe complete-rectangle fraction is **9085/16384**
(about 55.45%), compared with **1971/4096** (about 48.12%) for PR1247.
Every dirty field and unselected target bit is restored on the admitted set.
The original construction and predecessor predicates remain correct.
This is an exceptional-repair envelope improvement; all primitive calls and
repair costs remain paid. It establishes no measured speedup or new exponent.

## Result and evidence

Let `B=2^G`, `A=2^(K-1)`, target digits `2g_i+a_i`, dirty compact digits
`t_i,u_i`, source bits `c_i`, and `q_i=(u_i mod 2) OR c_i`. Starting at
`d_0=0`, compute `d_(i+1)=floor((t_i+a_i+d_i)/B)`. Require

```
q_i=1 implies d_i=0 and t_i<=B-2       for i<n
u_i+c_i<B                            for i<n-1
g_i+q_i*t_i<A                        for i<n-1.
```

Inactive saturated digits are allowed; their carry must not enter an active
digit. [PROOF.md](PROOF.md) proves the complete-map implication, ideal/actual
invariance, the valid current-address correction, exact correlated density,
strict inclusion of PR1247's guard, and one-digit maximality. It includes the
full retained descriptor, payload sorting, inverse and highest-bit charges.

[RESULT.json](RESULT.json) records the separately implemented exact replay:

- All **598,592 states** in five complete quotients, including every upper
  target bit, compact field and low source mask in those domains. Every raw
  map is bijective, its literal inverse agrees, and the new guard is invariant
  under both raw and intended maps. Every admitted full map agrees.
- **73,600 digit cases** independently enumerate ten parameter pairs,
  including the headline geometry, both incoming carries and both last/interior
  positions; their matrices match the all-n formula exactly.
- **544 full-field comparisons** with the unchanged physical swap/rotation
  interpreter, over every rho in four geometries. Half explicitly force a
  saturated temporary digit. Both good and bad states, admitted saturation,
  arbitrary dirty back fields, inversion, current-address repair and highest
  selected-bit completion are exercised.
- All **5,824 exceptional repair payloads** in the 8,192-state quotient land
  at the correct sorted keys. A wrong-key permutation still fills every hole
  but misplaces **5,024 payloads**, and is rejected.
- Seven named mathematical controls expose incoming compact carries,
  interior source-load carries, wide-target carries, target-only false
  acceptance and unsafe agreement-only guards, and retain valid inactive
  saturation and harmless final carries.

Finite replay supports the written all-n proof; it is not a formalization.
Full maximality for n>1, internal source-load carry cancellations, production
adoption, tape/compiler realization, recursive field reservation/hosting,
precision, analytic transfer and the multiplication theorem remain open.
No selected supplier cold replay or hosted CI success is asserted.

## Reproduce

From the repository root, using Python 3.10+ and the standard library:

```sh
python3 -I -O -B research/compact-late-carry-guard/verify.py
python3 -I -O -B research/compact-late-carry-guard/test_package.py
```

Expected:

```
PASS_COMPACT_LATE_CARRY_GUARD states=598592 physical=544 controls=7 headline=9085/16384 no_new_kappa
```

The registered hook uses Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/compact-late-carry-guard
```

The package test additionally replays a minimal read-only source tree from an
unrelated directory whose path contains spaces, and rejects five source-byte
corruptions, three algorithm corruptions and one changed receipt under `-O`.
It mutates only temporary private copies.

Normal verification writes nothing. `--write /absolute/new/external/path.json`
exports a fresh computed receipt for comparison. The direct command requires
only this package and its five pinned live inputs, including the complete
physical interpreter import closure. The generic runner additionally verifies
catalogue/selected-record provenance using the original Git history. Future
priority or selected-result changes do not alter these historical pins.

## Sources, scope and credit

Started from current main **1f327c6f3e3a35271c5c141d381b540bab8ad005**.
[SELECTION.json](SELECTION.json) retains the one OS-random selection nonce,
`b0d948f61caf27df25160f9b811ecba6`, selecting adversarial audit.
[TASK.json](TASK.json) refines `uniform-transfer-audit` to the exact exceptional
repair implication, records its budget and overlap evidence, and links the
[coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1588).
[SOURCES.json](SOURCES.json) pins the main inputs by Git blob and SHA256 and
identifies exact predecessor heads. Only this successor directory is added.

Credit Douglas Colkitt for the compact-control word, physical interpreter and
repair/tape accounting; OpenAI for the original framework; John-Michael Smith
(@jp3isme), PR763, for source-load carry and repair diagnostics; Hanson Sun
(@bbMisk), PR1219 and PR1247, for the earlier-source and nonsaturated two-pass
guard work, with substantial Codex assistance; Sagar Thakrar, PR1475, for
earlier-source saturation and invariant-guard analysis; and @martinxxx9,
PR1108, for the one-digit raw boundary law. No pending audit code is imported.

This contribution composes saturated inactive carries through BOTH later-source
subcalls and counts that envelope, answering part of PR1475's open later-source
question. It does not claim priority for the raw word, earlier guard, carry
diagnostics or general invariant-intersection fact.

Prepared for **Arham Tahir**, with substantial **OpenAI Codex assistance** in
derivation, implementation, checking and writing. New material Apache-2.0;
retained source notices apply. One agent; no independent human or proof-assistant
review is claimed.

## Open next questions

What is the maximal invariant full-map agreement set for n>1, including internal
source-load carries and cancellations between individually inexact subcalls?
A larger set could reduce exceptional repair further. Start by enumerating
`E intersect T(E)` on the smallest two-digit complete quotient, then derive
a carry-state description. The current proof excludes those cancellations;
they require a new implication. The structured question is in TASK.json.
