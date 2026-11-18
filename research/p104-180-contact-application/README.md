# P104 180-CLEAR contact contraction on the 17-call signed caller

The exact #7636 candidate combines two chart edits with a two-ADD scalar
lowering. The conditional claim under the retained 17-call rank-145 caller is
**κ ≥ 0.0036813560186**. The complete target-minus-paid crossing lies in
**[0.0036813560187, 0.0036813560188]**. The same-family role-379-only upper
endpoint is **0.0036810345258**, so the guarded claim exceeds it by
**0.0000003214928**. The stronger #7660 signed result is **0.0037170835567**
on its separate 234-CLEAR word. [#7636](https://github.com/CrocSwap/integer-mult-bounds/pull/7636) · [#7660](https://github.com/CrocSwap/integer-mult-bounds/pull/7660)

| 180-CLEAR word | Paid positions | Productive targets | Raw crossing bracket |
| --- | ---: | ---: | --- |
| Matched lowered #7636 source | 109,652 | 22,461 | [0.0036807241001, 0.0036807241002] |
| Lowered role-379-only comparator | 109,635 | 22,461 | [0.0036810345257, 0.0036810345258] |
| Lowered role-379 and 902/1091 contact | 109,618 | 22,461 | [0.0036813560187, 0.0036813560188] |

The input from DreamingOfClouds’ #7636 at
`7e68d8dd62d9a38c0f3c942262a7a85ca7125b75` has decoded SHA-256
`98b8c12ece2f323a6ff5cac8c7ed2f78ba3835438ea56b16bd7d4698ec5ad5b2`.
The 202,667-event candidate is
`5f555d6bb6736eb0c98826d9822f077ce1cbc6875c46b0c10731737665dbda6e`,
with 1,501 public roles, 68 owned slots and 180 CLEARs. Its parent
combination was recorded at `375f924e1588893680d39a194d29e5400bec4ab7e0b5db24b05f4cfe6fd05e15`.
It shares public entrance charts 281 and 285 for roles 457 and 461 with
the matched source. Rohan Arun’s exact #7113 caller is pinned at
`07a76c5e2738882c0cb322278e56f6cae3c9885d`. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) · [Public scope and predecessor](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19698656)

## Literal change and finite accounting

Role 379 bypasses its silent chart-1065 residence. Role 902 uses
`3 → 373 → 913`, and role 1091 stays in 373 to receive the same normalized
`+1/2` ADD before moving onward. The wide chart-127 coefficient
`23184221/921600` at unlowered candidate clock 150834 is split into adjacent
`25` and `144221/921600` coefficients on the same target and donor. This
preserves the exact shear and both signed nearest-up and nearest-even updates
on the integer tick model. The original 25-bit literal fails the retained
guard. The repaired word has 24-bit maximum literal numerator width and uses
the same 236 ordinary units for this split, with 544 additional scalar
services in the 17-call schedule.

Relative to the matched lowered #7636 word, the paid histogram changes by
`{1:-51, 2:+17, 4:-17, 5:+17}`; relative to the lowered role-379-only word
it changes by `{1:-34, 2:+34, 3:-17, 4:-17, 5:+17}`. Every target histogram
entry is preserved. The caller recensus derives 3,776 paid residual positions
and 3,744 residual target owners from the literal #7113 assembly, agreeing
with Ali Romman’s separate exact accounting. Full paid and target histograms
and directed interval signs for all three words appear in the
[independent result](evidence/INDEPENDENT-RESULT.json). [#7661](https://github.com/CrocSwap/integer-mult-bounds/pull/7661)

Both lowered words use grid `54675 × 2^16`, context 2,164, 42,789,208
coefficient visits per grid engine per word and the same conditional upper
bound of 112,508,000 scalar services. The conservative ordinary total falls
from 868,475,092 to 868,441,092, including the charge for all 51,034 native
scale-conversion sites. The resource model reports 131,558,908 units of
candidate margin to one billion.

## Guarded runs

The matched build took 1.91 s. Separate exact rows, ownership and price
replay took 144.87 s at 525,936 KiB peak RSS. Native execution took
155.19 s at 419,140 KiB. The two resource engines for the source and
candidate took 155.17 s and 156.63 s respectively. The scalar-domain
check took 6.12 s and covered all 921,600 residues and 3,686,400 signed
rounded comparisons. Runs used Linux CPython 3.12.3.

The signed driver took 313.06 s. It covered all 3,075 catalogue maps,
17 native calls, 104 boundary pairs, 180 owned lifetimes, 54 strict
and four functional outer checks, and tested a separate BIT failure.
It rejected four phase mutations, nine native custody mutations and
seven tape falsifiers. The recorded model uses 1,156 private banks,
297,006 map slots and at most 25,323,919,584 elementary records.
The signed wrapper took 381.41 s including the recorded authorization
wait, peaked at 157,640 KiB and exited successfully.
Original result, price, resource and authorization bytes appear in
the inventory. The cold replay regenerates the path-dependent
launch logs in its own scratch directory.
[Signed result](evidence/SIGNED-RESULT.json) · [Signed comparison](evidence/SIGNED-PRICE-OUTER.json) · [Native execution receipt](evidence/NATIVE-LAUNCH.json)

## Reproduction

Linux, CPython 3.12, standard library, and GNU `time`, `timeout`,
`prlimit` and `taskset`. All proof inputs for direct replay are inside
this directory. The generic registration additionally uses the upstream task
catalogue at the base commit to verify card provenance.

```sh
pkg=research/p104-180-contact-application
python3.12 -I -B "$pkg/verify.py" integrity
python3.12 -B scripts/research_package.py --package "$pkg"
```

The registered exact step rebuilds both lowered words, checks the residue
period and reruns the separate rational interpreter, literal caller recensus
and directed price. The registered signed step starts a new native application
on the authenticated pair and binds that run’s actual launch and scientific
receipts to the new #7113 caller replay. It consumes the exact original
independent and paired grid and tariff results as frozen inputs. The registered
resource step reruns the candidate grid and complete ordinary and scalar
accounting. Reproduce the matched source grid separately if required.

```sh
python3.12 -I -B "$pkg/verify.py" resource-source
```

The direct stages `exact`, `native`, `resource-source`, `resource-candidate`
and `signed` accept an optional `--out` to keep a fresh evidence directory
outside the source package. Each can run from an unpacked directory without
Git or network access. Each rebuilt gzip payload is compared against the
immutable decoded bytes before the original compressed stream is supplied to
the signed receipt guard. [Source and evidence inventory](INVENTORY.json)

## Scope and assumptions

This is a conditional finite source application. The inherited assumptions cover
all native columns, owned erasure, compiler, precision and tape, and analytic
recovery. The ordinary and tape comparisons use the same tariff for a
whole-private-extent supplier over all 180 owned lifetimes, including the common
(U) error model, the fixed-width backing and the cost of movement and reset.
The raw invoice bracket is the fixed-word price ceiling for this 17-call
mixed-target rank-145 model. The historical `complex-local-word-ceiling` uses
a nine-call rank-73 model with a different coverage identity. The inherited
BIT comparison uses `0.00376669`; the signed claim leaves
`[0.0000000000001, 0.0000000000002]` to the raw crossing bracket under
this invoice. [Proof and scope](PROOF.md)

## Open next questions

For the half-ADD on chart 373, derive admitted rounded-state congruence and
signed-range bounds or verify a charged total rounded implementation. Start
with its reachable grid at candidate clock 127445 and demonstrate the
whole-private-extent schedule under the same caller tariff. A physical
provider for arbitrary old private junk and rounded residuals remains open.
See the [task record](TASK.json).

## Credit

Clear1nsight with substantial OpenAI Codex assistance, including separately
implemented exact arithmetic, physical and caller checks. ChatGPT Pro informed
the discussion of matched inputs, precision and rounded-state proof limits.
The retained notices credit DreamingOfClouds, Rohan Arun, CubeJerry, ToikY,
Ali Romman and the inherited native, compiler and pricing lineage. [Notice](NOTICE) · [License](LICENSE)
