# Five rational returns and a rooted binary supplier for P104

The complete finite multiplier gives **conditional κ ≥ 0.00387561167742**. Its lower bound exceeds **0.00386981257853**, the directed raw upper endpoint for the submitted #7781 rational word, by **0.00000579909889**. This comparison also holds when #7781 receives the stronger binary supplier. The donation target of 0.00387981257853 leaves a gap of 0.00000420090111. The maintained selection at the pinned main commit is 0.00363005817. [Predecessor #7781](https://github.com/CrocSwap/integer-mult-bounds/pull/7781) · [Exact applications](evidence/application.json) · [Selected result](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json)

| Complete signed tariff, H(r) = r^(1−κ) | Binary | Rational |
| --- | ---: | ---: |
| Native calls | 36 | 48 |
| Independent native input and output fields | 680 | 1,284 |
| Paid positions | 107,460 | 283,344 |
| Productive positions | 20,706 | 52,272 |
| Directed raw crossing, lower | 0.003879928046154 | 0.00387561167750 |
| Directed raw crossing, upper | 0.003879928046155 | 0.00387561167751 |
| Signed margin at the donation target | +0.04446970252504… | −4.28380181041842… |

Eight new binary returns split previously productive grade-seven paths. The construction then withdraws paid transfers on the actual 680-owner graph and restores their observations. At owner 411, the projected packets on nested charts carry the same characteristic-two value. A chronological tree rooted at the original exterior source replaces the cycle. A separate paid bridge preserves the independent input at owner 411. The full ordinary service admits 0.003879927836145 using 934,182,831,504 records and 6,998,544 owned fields. A second finite check admits 0.0038799074072. [Binary construction and proof](binary/PROOF.md) · [Rooted tree and omission controls](binary/ROOT411-CONTROL.json) · [Finite compiler](binary/FINITE.json)

On the rational side, five births preserve the 400 main fields and all 879 prior helper fields. The first two use existing paid contacts. The third splits a paid path. The final two each subdivide two paid paths and charge both replacements. Four projected paid transfers and five closed-block bypasses compose with those five returns. Paid identifiers 40 and 65 are reused only after their former lifetimes end. The verifier rebuilds the schedule and independently prices both complete words. [Construction stages](complex/construction.py) · [Paid chain journals](complex/PAID-CHAINS.json) · [Signed comparison](evidence/independent-price.json)

| Prior address | Inserted chart | Witness |
| ---: | ---: | --- |
| 296 | 234 | Forward split, one grade-nine return becomes independent grade-four and grade-five returns |
| 681 | 243 | Adjoint split on a separate paid contact |
| 326 | 95 | Independent return funded by a recalibrated paid leg |
| 1158 | 237 | Productive grade eight becomes two grade fours. The two new paid subdivisions are both charged |
| 384 | 498 | Adjoint split, funded by rerouting two separate grade-six paid legs |

The last two splits save 0.09765426005789 and 0.14083618536186 signed units across 48 calls, respectively. The original diagnostic for chart 237 shared the old MOVE table with the edited graph. The published replay loads the immutable source and charges both paid subdivisions, then checks all independent outputs. [Later birth journal](complex/CONTINUED-BIRTHS.json) · [Independent operator and changed chart controls](evidence/operator.json)

The fourth bypass shares the new chart-237 return. A direct grade-five paid leg from 237 to 127 replaces the former grade-one and grade-four legs, while the independent grade-four returns survive. It saves 48(H₁ + H₄ − H₅), at least 0.46405517701371 signed units at the target. Omitting the new slot 80 changes a forward coefficient by 1/2 and its mirrored adjoint coefficient by 1/2. [Last bypass and dirty retirement](evidence/last-bypass.json) · [Frozen construction](complex/PAID-CHAINS.json)

The fifth bypass uses charts 3, 597, 652 and 653. It drops the grade-two transfers at slots 100302 and 100307, then sends the common scalar on a grade-one leg to chart 597 and a grade-three leg to chart 653. Both receiving charts require a correction. The productive multiset and total paid count stay fixed. The complete 48-call saving at the target is 48(2H₂ − H₁ − H₃), bounded below by 0.096832450156517956530135. On source address 783, omitting slot 12 changes terminal 123 by −2/3. Omitting slot 81 changes terminal 19 by +4. The exact old and new paid-cell residuals also admit an independent erasure check. [Fifth bypass audit](evidence/fifth-bypass.json) · [Reversible journal](complex/POST-BIRTH-CHAIN-2.json.gz)

The finite lower bound is 0.00000009485313 above the immediately preceding submitted word’s directed upper of 0.00387551682429. This checkpoint still needs 4.283801810418420331023466–4.283801810418420331023467 signed units across 48 calls at the original target. Ali Romman independently proved the prior chart-237 bypass preserves all 1,284 outputs and independently bounded the four fixed binary repair ports. The new construction starts from those exact published words. [Preceding checkpoint](https://github.com/CrocSwap/integer-mult-bounds/commit/ff6f1d8ab3fafb71ea12ccd943013d058c0f5847) · [Prior rational audit](https://github.com/CrocSwap/integer-mult-bounds/pull/7791) · [Prior binary audit](https://github.com/CrocSwap/integer-mult-bounds/pull/7790)

## Reproduce

Use Python 3.12 from this directory. The manifest pins 127 public source files from #7781, #7776 and #7774 by both SHA-256 and Git blob identity. Each part can run in a separate output directory. [Source lock](SOURCE-LOCK.json)

```sh
python3 -IB prepare_sources.py /tmp/p104-iterated-sources --fetch
for part in binary-construction binary-finite construction operator charts-0 charts-1 charts-2 application; do
  python3 -IB verify.py --part "$part" --cache /tmp/p104-iterated-sources --out "/tmp/p104-iterated-$part" || exit 1
done
```

The unmodified rational word is tested on all 1,648,656 coefficients in each orientation. For each of 50 coefficient faults the checker evaluates an exact full affected input column and output covector. Separate controls omit newly independent sources and dirty CLEARs. The 21 changed physical chart pairs each pass all 512 Gaussian columns in both directions, including the absolute phase. The full chart set is covered in three shards. The 840,912-row rational caller, ordinary compiler, owned backing and common outer depth guards are also replayed. One short review is to remove the coefficient of sender 78 at terminal 155804 and compare the changed input column and adjoint covector to the independent receipt. [Independent checker](complex/independent.py) · [Comparator and source pins](CLAIM.json)

The conditional claim retains native all-column validity, owned erasure, compiler correctness, precision-tape simulation and analytic recovery. Ali Romman supplied the #7776 carriers and independently audited the preceding #7781 return at owner 1164. The inherited callers, compiler, physical model and proof framework are credited in the notice. [#7776](https://github.com/CrocSwap/integer-mult-bounds/pull/7776) · [Independent predecessor audit #7784](https://github.com/CrocSwap/integer-mult-bounds/pull/7784) · [Notice](NOTICE)
