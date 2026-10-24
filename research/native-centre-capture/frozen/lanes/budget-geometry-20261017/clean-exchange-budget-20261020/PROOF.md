# Native budgets for the clean centre exchange

## Result and scope

For dimension 25, productive width 224, three local calls, and no idle jobs, the exact conditional native budgets are:

| Three-call profile | Native mass | Extra H1 limit | Extra H2 limit |
| --- | ---: | ---: | ---: |
| Three Q-entry calls | 5,376 | 196 | 98 |
| One I-entry and two Q-entry calls | 5,392 | 180 | 90 |

The complete histograms before cleanup are:

```text
three Q:       4176 H1 + 192 H2 + 144 H3 + 48 H8
one I, two Q:  4176 H1 + 192 H2 + 144 H3 + 32 H8 + 16 H9
```

The limits use the historical selected exponent

```text
b = 67018507072324140917 / 40000000000000000000000.
```

The checker binds this value to `certificates/selected-result.json` and its assembly at Git commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. This is a historical source pin. It is not a claim about the current frontier.

All extra native work must fit within the stated allowance. The H1 and H2 columns are alternatives. They cannot both be used at their limits.

The local words are supplied and checked. Their routed three-call composition is not supplied by this packet. In particular, the three-Q profile does not provide the initial Q-entry state for free. Any work that forms it must be included in the extra budget. No terminal, recursive host, complete finite invoice, or kappa improvement is claimed.

## Hypothetical cleanup costs

If one-bank cleanup can be implemented with the stated number of H1 children, the exact remaining budgets are:

| Three-call profile | Cleanup H1 | Extra H1 left | Extra H2 left |
| --- | ---: | ---: | ---: |
| Three Q | 112 | 84 | 42 |
| Three Q | 128 | 68 | 34 |
| Three Q | 144 | 52 | 26 |
| One I, two Q | 112 | 68 | 34 |
| One I, two Q | 128 | 52 | 26 |
| One I, two Q | 144 | 36 | 18 |

The receipt gives a strict passing bound at each limit and a strict failing bound at the next child. These rows price proposed cleanup histograms. They do not give access to the required queries or construct their scatter, frame changes, phase corrections, restoration, or terminal output.

A full 224-H1 terminal would give mass 5,600 in the three-Q case. Since every child rank is less than 25, that bill fails for every b>0. The one-I bill with that terminal has mass 5,616 and fails even at b=0. At the pinned exponent, such a terminal must lose at least 28 H1 or 44 H1, respectively, before any other native work is added.

## Literal source count

The clean-exchange producer freeze is

```text
new-core-transfer-20261017/low-displacement-20261020/
clean-late-exchange-20261020/FREEZE.json
SHA256 96048355033e5f5bdd26dadddb869708faae6f8b0d9a61a1ae696e5a5c20c0bc
```

Its independent local review freeze is

```text
new-native-recipes-20261017/clean-centre-exchange-review-20261020/FREEZE.json
SHA256 6cd34040ecd7d832f1bae3d44c5a7b97dcc11022d843e48007c5474cc4f3701d
```

The separate inverse-adjoint and selected-swap conjugate use the producer's `DUAL-FREEZE.json`, with SHA256 `fa8f910fe7f22a696f47513c95e814588723dc8abaaa68061fcba3676c308d43`. Their local producer checks are bound. A separate review of those dual words is not part of the clean-exchange review cited above.

This checker counts all eight serialized words: both clean entry variants and both dual variants, for both providers. It imports no producer code. Every native and scalar event uses a data role from 0 through 223. The count is:

| Local entry | Literal native profile | Children | Native mass |
| --- | --- | ---: | ---: |
| Q, inverse-adjoint, or selected-swap conjugate | 1392 H1 + 64 H2 + 48 H3 + 16 H8 | 1,520 | 1,792 |
| I | 1392 H1 + 64 H2 + 48 H3 + 16 H9 | 1,520 | 1,808 |

In a Q or dual word, each of the 224 data fields has total native rank eight. In an I word, sixteen fields have rank nine and the other 208 have rank eight. All individual child ranks satisfy the dimension-25 size guard.

Each local scalar word contains 1,032 unit complex ADDs, 96 scales of price two, and 38 scales of price four. Thus each word costs

```text
1032*8 + 96*2 + 38*4 = 8600
```

real scalar primitives. This total includes the FULL source code and the sixteen signed exchanges. Inverse-adjoint conversion and field relabeling keep the total price. The checker verifies their literal counts too. Their routed use is a separate obligation.

The I-entry word has 112 input views, 96 output views, and a native side-map bound of 3,008. The checker verifies the identity records on both sides of each of its sixteen direct H9 children. The Q and dual words retain all side maps: 128 input views, 96 output views, and a native side-map bound of 3,040.

The three-call scalar subtotal is 25,800 in both cases. The total map-call bounds are 9,792 for three Q calls and 9,744 for one I and two Q calls. These component subtotals omit the caller, cleanup, any required physical role conversion, map lowering, recursive children, and precision.

The source phase and full 640-column proofs are pinned premises. This budget checker does not run them again. It verifies the invoices; it does not reclassify the productive exchange as an ordinary data response.

## Exact arithmetic

For a histogram H, the native moment is

```text
M_H(b) = sum_r H[r] * r/(25*224) * (25/r)^b.
```

The two pinned rational engines give:

| Profile | Lower bound | Upper bound |
| --- | ---: | ---: |
| Three Q | 0.964728938373732327 | 0.964728938373732328 |
| One I, two Q | 0.967586457273780926 | 0.967586457273780927 |

For each proposed cleanup, the checker adds its H1 count to the full histogram. For each permitted extra rank, both engines agree on the integer limit. Each engine proves M<1 at that limit and M>1 at the next count. It is not enough for the two engine intervals merely to overlap: both strict inequalities are tested separately in each engine. No floating-point calculation determines a numerical claim.

## Reproduction and credit

Run `python3 -I -B check_budget.py` and repeat with `-O`. Both runs must give identical receipt bytes. The source, certificate, and engine hashes are stored in `BUDGET.json`. A separate review of this new budget is pending.

The root and controller lanes supplied the clean coupled interface. The new-core-transfer lane emitted the local words. The new-native-recipes lane supplied the independent clean-exchange review. The cover-algebra lane supplied the selected-bank dual formulation. The earlier budget and bridge-review lanes supplied the exact engine and certificate binding methods. This packet used AI assistance.

No PR, push, commit, or publication is authorized. Before any future PR description, read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
