# Complete helper-promise classification at public MOVE40710

On the exact unselected #7481 native word, write
\(g=e_{885}-e_{705}\), \(h=e_{1459}\) and \(L=\operatorname{span}(g,h)\).
This package classifies **every scalar-linear helper promise whose
annihilator is a subspace of L**, with unchanged native histories and
arbitrary independent main inputs. It proves the classification uniformly
over the real or complex scalars, using exact source-support isolation and
unique circuits rather than sampling parameter values.

| Promise annihilator | New nonzero cached MOVEs | Least original target debit |
| --- | --- | --- |
| 0 | None | 0 |
| span(g) | 40710, rank 8 | f(8) |
| span(g+lambda h), lambda nonzero | 40710, rank 8 | f(1) |
| span(h) | 52236, rank 1 | f(1) |
| L | 40710 and 52236 | f(8)+f(1) |

No case produces a zero MOVE. Here f(r)=r^(1-kappa), for 0<=kappa<=1.
All prices are information-relaxation prices for original retained targets.
The only potentially positive allowance is f(8)-f(1), from a nonzero-lambda line, before
constructing the correlated initial value of 1459 and every other physical
cost.

A **separately conditional corollary** says this entire family cannot improve
the native moment when that initial 1459 value is not supplied free, original
producer histories are fixed, and every new nonzero cross-frame dependency
uses separately billed whole native jobs without adding payload to existing
jobs or using an unbilled control/descriptor channel between frames. A probe then forces rank 8 transport for the cheap1459 pivot. Deleting
1459's final target credit does not itself imply this access premise.

## Evidence and reproduction

The standard-library verifier reconstructs all 76,475 events and 7,780
observations in 979 used physical coframes; checks the two exact circuits,
all support-isolation facts and target ranks; and rechecks the published
full-row-rank certificate. It runs 11 meaningful failure controls.

```sh
python3 -I -W error -B research/p104-public-relation-family-bound/verify.py
python3 -O -I -W error -B research/p104-public-relation-family-bound/verify.py
python3 -B scripts/research_package.py --package research/p104-public-relation-family-bound
```

Expected status: `PASS_COMPLETE_TWO_DIMENSIONAL_PUBLIC_RELATION_CLASSIFICATION`.
No Git, network, saved matrix dump or optional library is needed. The verifier
writes only stdout. A separate mathematical review accepted every subspace,
the exact debit criterion and the conditional transport corollary; its small
exact basis fixtures are also registered in normal and optimized modes.
See PROOF.md, INDEPENDENT-REVIEW.md, SOURCES.json and VALIDATION.json.

## Scope, provenance and next obligations

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Source #7481 head: `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b`.
The word is unselected; no claimed exponent from that PR is admitted here.
This package builds on the complete original-history theorem at fork commit
`fdbb41450a98594bdf1f5fe4535e77d2466adb4f`, with its rank helper retained
byte-for-byte and credited. The single relation and preparation investigations
are preserved in recovery checkpoint13; the infinite family proof is new.

There is **no new kappa**, full supplier, physical cache implementation or
foundational assumption discharge. Other helper relation spaces and changed
producers remain open. See OPEN-QUESTIONS.md for precise next obligations.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance in
research, implementation, adversarial review and packaging. Retain the
bundled Clear1nsight native notice and credited predecessor verifier.

## Open next questions

The initialization resource, changed producer, other relation-space and
public zero-transition obligations are stated with first steps and blockers
in [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md).
