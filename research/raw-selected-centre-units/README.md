# Selected-centre units and exact local normalization

This package gives a 38-port selected set with two dyadic unit properties
for the historical centre response `J=I-KR`. A union of complete
eight-port minors first has both properties at 40 ports. Thus the
38-port construction improves on that restricted class. It does not
prove that 38 is the minimum over all selected sets.

The package also gives a general two-step normalization for an invertible
selected principal block. On a separate signed response, the complete
eight-port backward word costs 89,200 real dyadic scalar primitives.
It has the same complete map as the 99,472-primitive long word. The
24-port version costs 89,592 instead of 96,012. All four prices include
the native core and all physical exchanges.

The [proof](PROOF.md), [source manifest](SOURCE-MANIFEST.json), and
[review index](REVIEW-INDEX.md) define the exact scope. The native words
use historical inputs from [PR #3133](https://github.com/CrocSwap/integer-mult-bounds/pull/3133)
and [PR #3148](https://github.com/CrocSwap/integer-mult-bounds/pull/3148).
They retain `2433 H1 + 724 H2 + 228 H3 + 102 H4 + 20 H5`: 3,507 native
children and rank mass 5,073. This is a local invoice, not a complete
supplier or the current selected construction.

At the publication base
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, the
[selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/b58ad9ef4d4e861b0eaa5dba41742bdc072dca51/certificates/selected-result.json)
uses [PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470)
and gives conditional `kappa=60403/20000000=0.00302015`.
This package does not change that record or improve the complete kappa
calculation. Its historical source commits remain fixed.

The [publication validation](VALIDATION.md) records successful relocated
normal and optimized replays. The [package manifest](PACKAGE-MANIFEST.json)
binds the complete package files to their byte hashes.

## Raw response: two distinct unit tests

For `R K=14I`, set `D=R_S K_S`, `T=D-13I`, and `W=I-D`.
The ordinary block `H=I-K_U R_U` is a dyadic unit exactly when T is.
After the ordinary inverse and selected upper correction, the original-X
response is `A=E+K T^-1 R`, where E is negative on S and positive on U.
Given invertible T, A is a dyadic unit exactly when W is.

For the actual S38 witness, `det(T)=2^24`, `det(W)=2^12`, and
`det(A)=2^-12`. Both inverse orders are checked on all 112 data
coordinates. The complete native review checks the corresponding
boundary words and the full normalized backward composition.

| Raw response selection | Balanced backward | Diagonal borrowed block, backward | Balanced forward | Extra real division-by-three scans, backward |
| --- | ---: | ---: | ---: | ---: |
| S8, one complete minor | 171,474 | 171,730 | 171,650 | 16 |
| S38, irregular set | 170,446 | 171,662 | 171,290 | 0 |
| S40, five complete minors | 170,274 | 171,554 | 171,266 | 0 |

The S38 response A and its inverse cost 7,452 and 7,412 scalar
primitives. The complete diagonal-borrowed backward word followed by
`A^-1` costs 179,074, at the same native mass 5,073.

The old S8 backward words are rational local words. Their 16 division
scans have a separate price and a separate common-grid contract. They
are not dyadic primitive operations. Their original-X response has an
eight-dimensional kernel even after exact division. The two-bank word
remains invertible because selected Y retains original data. The
[odd-grid review](frozen/work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/odd-grid-a8-review-20261017/REVIEW.md)
states the root conversion, completed-child, final unscaling, width,
scan, and binary-guard obligations.

## Changed structured response: short normalization

For a general response `J=[[L,B],[D,H]]`, the raw backward word has
original-X response `C=[[-L,0],[-D,I]]` on `z=(Q_S a,u)`.
If L is a unit, apply `X_S <- -L^-1 X_S`, then
`X_U <- X_U + D X_S`. The second step reads the changed X_S.
This is C inverse. It does not require an inverse for H or for the
complete J. The full borrowed-source terms remain explicit.

| Changed response | Long normalized backward | Short normalized backward | Saving |
| --- | ---: | ---: | ---: |
| Signed S8 | 99,472 | 89,200 | 10,272 |
| Structured S24 | 96,012 | 89,592 | 6,420 |

These S8 and S24 responses differ from the raw `J=I-KR` response above.
Their coefficients are dyadic, and they use no odd division. The signed
S8 short suffix uses no owned field. The S24 suffix uses the existing
C0 and restores its query to zero before every reuse and final reset.

The independent review checks all 18 complete words for both providers.
It compares the short and long maps on all 640 input columns: 224 data
fields, 408 arbitrary helper fields, and eight owned fields. It also
checks all 91 private zero-buffer outputs. Owned admission uses the
allowed CLEAR operation; the claim does not restore the contents that
preceded owned admission. Helper restoration uses the exact inherited
physical wrappers. All port and warp operator products retain their
order.

## Replay

Use Python 3.10 or later on macOS or Linux. Only the standard library is
required; the native reviewer uses its Unix `resource` module. Use one
process and keep at least 3 GiB free disk space. From this directory, run:

```sh
python3 -I -B reproduce.py --out /tmp/selected-centre-units-normal
python3 -I -B reproduce.py --optimized --out /tmp/selected-centre-units-optimized
```

Use a new output path each time. Each command ends with:

```text
PASS_RAW_SELECTED_CENTRE_UNITS
```

The runner checks every input hash, copies the frozen workspace to a
temporary directory, and runs eight checks in sequence. It compares
every mathematical receipt field with the retained receipt. It excludes
only timing, process memory, and checker-file hashes from that
comparison. The safe replay entrypoints have different file hashes from
the original fixed-output checkers. Regenerated compressed output is
compared by its decompressed payload. The runner checks the source files
again at the end and removes its temporary workspace.

The eight checks cover the independent S38 units, the exact witness,
all 14 complete-minor cases, the odd-grid contract, both native phase
providers, the 12 serial S8/S40 words, the S38 words and response units,
and the 18 structured words. The two centre matrices from the old and
transferred cores must agree exactly. The old complete-minor replay uses
its own historical 480-helper core; the other native interface checks
use the transferred 408-helper cores. Their bills are not combined.

The optimized run enables `-O` for the independent reviewers and other
checks that use explicit failures. The frozen dyadic witness producer
uses Python assertions and always runs with assertions enabled. Its
positive S38 result also has the independent root and native checks.
The package does not adopt its unreviewed lower bound of twelve or its
later separator claims.

The native phase check uses a separate exact interpreter. It checks
3,036 child classes per provider, both literal warp orientations,
ordinary adapters, and residual wrappers. The complete interface
checks bind to those exact records. Negative controls reject a changed
global phase, a wrong helper endpoint, omitted boundary factors,
incorrect Q order, and an incorrect suffix order. The odd-grid review
also tests exact integer scans and their divisibility conditions.

Frozen producer emitters are retained as source evidence. The supported
entrypoint is `reproduce.py`: it verifies the serialized words without
the external source-generation toolchain. The package does not claim a
fresh regeneration of all historical phase-compiler output or a replay
of the current selected supplier.

## Review status and retained history

The original proofs and freezes remain byte-exact. Some retain old
sentences such as "pending review" or "publication not authorized".
Those sentences record their historical state. The linked later reviews
define the accepted local claims in this package. Publication authority
and the current selected result are separate from those frozen records.

The fixed-A,T split-pair bound of 40 is retained as related evidence.
It has extra baseline and pairing restrictions. The S38 witness does
not satisfy those restrictions. The pair-bound review did not repeat
the 1,130,168-case enumeration. That enumeration and the related
fixed-baseline spectral bounds are outside this package's fresh replay.

## Open next questions

- Can an arbitrary selected set smaller than S38 satisfy both raw unit
  conditions? Start with an exact candidate Gram matrix and the actual
  112 columns. The minimum is open; failed searches do not settle it.
- Can a paid routed caller use the normalized local interfaces? Start
  with one exact source-to-source transition and preserve the full
  borrowed-source response. Inter-call access, endpoint conversion,
  owner histories, child hosting, and precision remain open.
- Can the selected-principal normalization apply to a current supplier?
  Derive its actual response and endpoint operators first. The historical
  5,073 profile and centre rows are not a substitute for those inputs.

See [NOTICE.md](NOTICE.md) for source credit and AI assistance. These are
exact local proofs and checks. They do not give a complete multiplication
theorem, a global decoder, or a new complete kappa bound.
