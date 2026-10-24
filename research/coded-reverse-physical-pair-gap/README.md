# The first physical substitution gap in the coded reverse controller

**Scoped counterexample and missing implication. No complete caller obstruction or new κ is claimed.** Under the signed physical normalizers of Dillon's PR4933, the literal PR4940 backward FULL followed by its scalar `A^-1` thin source leaves the nonzero block `D(I-A^-1 C)`. The declared x-only input/output recodings do not remove this block. A common full exit frame allows scalar owner mixing; it does not identify the physical code `C` with scalar `A`.

## Source and chronological cut

The canonical base is `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority revision 7. [SOURCES.json](SOURCES.json) authenticates every external live input. The PR4933 head `d969c458c24278e0fd37e5b4c0ff8a53a496b430` and PR4929 head `361f5d4100640177d6a983dd2f336021c75bfd5e` are ancestors of that base; the used `NORMALIZERS.json`, `PHYSICAL.md`, and PR4929 `CODE.json` match their original head bytes. No unmerged shared-object dependency or frozen-source edit is introduced.

The exact PR4940 source is `research/coded-reverse-controller/verify.py`: `local()` applies a backward shear, then its `D_s`; `build()` binds `Qv=2` and every `D_s` to scalar numbers. This proves a commuting specialization, rather than the physical noncommuting substitution. For the proposed `p=19` word choose its final backward stage 37 and its next forward thin stage 38. `j < p-1` and the initial-IDLE condition are both false here, so no bridge or IDLE lies between these calls. Terminal IDLEs on other pairs occur after this thin shear. The test uses the central address bit and stage 37's fresh eight bits; every other address block is retained as a spectator.

This package checks the local operator identity required by the proposed conjugation. It does not infer that a later whole-controller continuation cannot cancel a local discrepancy. Such a continuation would require a different, explicit source-bound proof and bill.

## Exact local calculation

Operators apply rightmost first. Let `Q` be the actual central Gaussian, `D` the eight fresh-axis Gaussian product, and `R=DQ`. PR4933 supplies signed monomial `K_i`, with `[K_i,R]=0`, and the physical code

```text
C_ij = A_ij K_i^-1 K_j,       C = K^-1 (A tensor I) K,
B = diag(D,D) [[I,-Q C],[0,I]].
```

Its actual X-only `Q^2` raw-dual convention is retained. We never replace it with the older Y-only convention or assume `[C,Q]=0`. The literal PR4940 thin source is copied into owned fields, mixed by scalar `A^-1`, queried by `Q^-1`, and added to Y. Therefore

```text
T = [[I,0],[Q^-1 A^-1,I]],
T B = [[D,                    -D Q C],
       [D Q^-1 A^-1, D(I-A^-1 C)    ]].
```

Only scalar `A^-1` was commuted with `D` and `Q`. In particular no step commutes `C` past either operator. With the declared boundary `pre X A`, `post X A^-1`, this becomes

```text
[[D,      -D Q A^-1 C],
 [D Q^-1, D(I-A^-1 C)]].
```

The standard pair is `[[D,-DQ],[D Q^-1,0]]`. Thus this local binding holds **if and only if `C=A tensor I`**. The source polynomial `A^2+12A=13I` establishes invertibility and its scalar inverse; it does not establish that missing operator equality.

## Literal signed witness

Use destination owner 0, source owner 1, and source address `1`. The actual ports are `q_0=11`, `q_1=19`; their normalizer masks are `z_0=15`, `z_1=23`. The pinned scalar entry is `A_01=-1/2`. Their exact signed actions give

```text
K_1 |1> = -|19>,       K_0^-1 |19> = |22>,
C_01 |1> = +|22>/2,    (A tensor I)_01 |1> = -|1>/2.
```

For the arbitrary local input `x=0`, `y=|owner 1,address 1>`, the residual is `y_out=D(I-A^-1 C)y`. Applying the invertible diagnostic `A D^-1` gives, at owner 0, `-(|1>+|22>)/2`, proving that the actual output is nonzero. The diagnostic is a mathematical witness, **not an emitted decoder or free physical operation**. Because `D` is a product of invertible actual Gaussian gates, multiplying by `D` cannot erase this discrepancy. Pre/post operations restricted to X do not affect the displayed Y-to-Y block.

This failure holds at every positive digit-column width: use `|1>` in one column and `|0>` in the others. Each `K_i,f` is the source signed tensor lift, so its transition still distinguishes the same two addresses, while scalar `A_01` is applied once to the owner block. The proof evaluates the finite owner program in the lifted operator algebra; it does not tensor a sum or replace owner code `A` by `A^tensor f`.

## Complete local operation ledger

The ledger prices the **failed literal recipe**, with the two declared boundary recodings charged once. In a complete controller those two conversions belong to its boundary, rather than every adjacent pair. No favorable moment is inferred from this local invoice.

| Operation | Field-level charge | Status |
|---|---:|---|
| Backward center-free FULL | `2201 H1 + 412 H2 + 510 H3 + 127 H4 + 40 H5` | Inherited PR4929 paid profile, unchanged |
| Original helper returns | `28 H4 + 7 H7 + 47 H8 + 326 H9` on 408 distinct owners | Inherited autonomous jobs, no scratch or erasure credit |
| Four native port wrappers | 448 monomial field maps | Retained PR4933 upper bound |
| X-only backward conversion | At most 448 more monomial field maps | Retained bound; no fusion assumed |
| Input `A`, thin-source `A^-1`, output `A^-1` | Three eight-mode recodings: 2,688 scalar ADDs and 48 owned CLEARs | Constructive source program; eight reusable owned mode fields |
| Thin source bank | 112 initial CLEARs, 112 COPYs, 112 terminal owned ERASEs | 112 simultaneously owned fields, separate from helpers |
| Thin queries | 112 rank-one Gaussian jobs and 112 Pauli translations for `Q^-1` | Positive Gaussian lowering from PR4440; inverse is not order two |
| Thin destination updates | 112 ADDs | Main inputs are arbitrary and distinct |

The resulting paid Gaussian profile is `{1:2313,2:412,3:510,4:127,5:40}`; the wrapper/query count is at most 1,008 monomial field maps, in addition to the native word's internal work. The added recoding/query workspace peaks at 120 owned fields (112 query copies plus eight modes), beyond inherited native scratch. Each recoding completes every mode source read before updating its owner bank. Its owned temporaries alone are cleared, and no original helper is modified by the new word.

Scalar `A` uses update coefficient `-1/4`; each scalar inverse uses `-1/52`, introducing denominator 13 twice in this local boundary-inclusive recipe. Native ordinary arithmetic, its 6,596 dyadic compensation ADDs, matcher/routing work, complete fixed-tape field-map tariffs, rounding and denominator-13 implementation remain inherited or unresolved **nonzero costs**. Their absence from a concrete TM tariff is a limitation, not free credit. Task 03 independently addresses the local odd-division kernel; it cannot make `C=A tensor I` true. No independent Gaussian main-output credit is admitted for this failed recipe.

The nearby alternative `Q^-1 C^-1` thin source is not silently excluded: `[C,DQ]=0` makes that alternative's Y-to-Y block zero. It is a changed recipe costing an additional 224 `K_i/K_i^-1` field maps per inverse recoding, and its other blocks and actual boundary still need proof. This package stops at the literal scalar-substitution gap instead of claiming a general impossibility.

## Reproduce and evidence

```sh
python3.12 -I -B research/coded-reverse-physical-pair-gap/verify.py
python3.12 -I -O -B research/coded-reverse-physical-pair-gap/verify.py
python3.12 -B scripts/research_package.py --package research/coded-reverse-physical-pair-gap
```

The verifier uses only the standard library. It authenticates the source bytes, checks all 112 signed normalizers and their exact absolute-phase weight identities, and checks all 12,544 owner-code entries against the eight-mode program. An independent address-array oracle over `F_65537`, with `i=256`, executes the actual `Q` and all eight `D` axes on the 112-owner fixture. Denominators 2 and 13 are invertible in this field, so its nonzero residual also rejects exact rational operator equality. The exact sparse witness supplies the literal rational discrepancy separately.

The scalar-A predecessor is a positive cancellation control. Omitting the `K` sign changes the exact witness; commuting `C` through `Q` or copying the Y-only backward convention changes the operator. The new cleanup trace permits only the 120 owned fields and rejects an attempted ERASE of arbitrary helper 17. This verifies the new wrapper's ownership declaration, while original producer autonomy remains an explicit inherited source premise. [RESULT.json](RESULT.json) records the mathematical receipt. No original three-minute replay, full p19 controller, Lean, production build, compiler, hosted CI, or multiplication theorem was run.

## Open next questions

The structured question in [TASK.json](TASK.json) is a changed thin/boundary word that proves **every** block of the physical pair and its complete added bill. The first useful check is the same signed owner-0/owner-1 fixture, followed by an all-input typed operator derivation. A product of changed stage codes or a paid boundary can evade this local gap; neither is furnished here. A denominator kernel is a separate conditional arithmetic result, rather than a physical consumer proof.

## Credit and scope change

This changes the `centre-path-sharing` card to PR4940's explicitly handed-off physical-pair obligation. It does not re-prove PR4933's normalizers, its local gauges, or its one-stage terminal support theorem, and it does not repeat PR4932's standalone one-bank exclusion. The new result is the exact first mismatch in PR4940's scalar-to-physical substitution, its source-bound signed witness, and the boundary-inclusive local ledger.

Credit Cayden Burkart / SethBurkart123 for PR4940's coded reverse controller; Dillon for PR4933's signed physical normalizers, eight-mode scalar program and X-only backward convention; Dugongue / mdumitrean for PR4929's coded producer; Cinna Davis for PR4694/4698 and PR4440/4470; Cao Yifan / intqwq for PR4610; zxv, Jacob Alan Sussman, and every retained native, Clifford, query, ownership, compiler and precision contributor. Prepared for JoyboyBrian with substantial OpenAI Codex assistance. New work is Apache-2.0. Independent human or formal-kernel acceptance is not claimed.
