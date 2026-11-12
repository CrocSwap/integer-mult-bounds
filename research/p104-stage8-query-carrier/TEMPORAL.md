# Timed readouts and restoration at port 0

The four pure central helper moves in #7404 remain the source candidates.
The follow-up grants timed snapshots as well as ordinary repair at the
terminal chart. It also checks coframed compensation at the native
entrance. The original [retiming proof](README.md) and receipt are retained
at exact head `aadd1de3e520cfd1e5b062729bd76f543dc879f4`.

## Timed observations

Grant an independent signal addition immediately before each of the eight
matching rank-one MOVEs. Four are productive helper moves and four use
other main owners. The latter four are a relaxation. The proof does not
grant their lower-chart binding in a physical candidate.

At each selected chart observe the initial live rows and the row produced
by each event whose destination is live there. Between those events the
available values are unchanged. For each bank write its normalized
observations as `A x + B p`, where `x` is the original independent
public input and `p` is the vector of the eight additional signals.
A linear combination that kills the original input dependence is
an additional response exactly when its value on `B p` is nonzero.

The 10 observations in chart 0 give zero additional responses even when
held together without charge. For a wider test, grant all 447 observations
in charts 0, 249, 251, 128, 245, 1091 and 260, and even allow mixing
between these charts in normalized coordinates. Cancelling all original
inputs gives zero additional responses. Granting the original four port-0
inputs as independent readouts gives exactly one. It is represented by

```text
-2 R112(43790) + R48(43791) + R100(43929)
   = -2 (x0 + x112 + p225 + p7)
```

Here `Rr(k)` is the normalized field at the cut before event `k`.
The three rows in this identity are in chart 128. The subscripts on
`p225` and `p7` denote the carrier role. The linear system grants all
four original port inputs for free, even when their physical charts differ
from that of the readout.

## Chart-local terminal restoration

Let `c` be a terminal chart. Grant its entire old timed bank and the
four original port-0 inputs. If an independent input change on other
original fields can imitate an injected signal in every row of that bank,
the old and changed histories are indistinguishable to a restoration
using that bank. For a protected terminal output in that chart, a nonzero
injected response then prevents exact restoration of the original value.
This follows by comparing the signal perturbation to the imitating
original-input perturbation. The latter changes the correct original
return by the observed response.

The check constructs such input imitations for every injected column
in chart 140 and in chart 150. The imitations match every observation
in independent forward walks. In particular, protected native returns
125 and 137 have the added responses

```text
return 125 at chart 140: (p225 + p7 + p27) / 2
return 137 at chart 150: (p225 + p7 - p27) / 2
```

Preserving both with chart-local restoration forces `p225+p7=0`.
That eliminates the only mode visible in the seven-chart readout test.
This proof allows any combination of the eight injections. Transporting
a new signal into another return chart or changing the retained program
before the observations would change the hypothesis.

## Coherent entrance compensation

There is a coframed way to restore all the original helper and unrelated
main returns of the role-225 path. Keep an independent new field `z` at
chart 3. At entrance add the 395 specified multiples of `z` to their
original chart-3 input fields. Add `z` to field 225 just before its MOVE
at clock 32641. The coefficients are the negatives of the corresponding
entries of `M^-1 b`. Here `M` is the old normalized endpoint and `b` is
the actual suffix response to an injection at field 225.

The resulting added endpoint is exactly one copy of `z` on native field
112, with all other public rows and the pre-COPY guard preserved. A forward
walk verifies both the inverse pullback and the compensated response.
Omitting one required entrance compensation breaks the return equality.

The only port-0 terminal response among all eight direct injections is on
field 112, for carriers 225 and 7. The old endpoint acts independently on
port 0 and the other native inputs. Compensating only those other inputs
cannot create a port-0 response on another output.

The compensated path is exactly equivalent to adding `z` to native
input 112 at entrance. The signed caller binds this chart-3 field to the
port-0 Y lane. Its additional contribution has the stage-8 body and no
central phase factor. This is a return-preserving ordinary response and
adds zero to the opposite-sign phase-difference rank.

At unit bodies the retimed required host has a `q=-1` minus `q=1`
minor of determinant `-32`, on caller output roles `0,8,18,19` and
inputs `8,1,26,19`. The retained host has phase-difference rank two.
Phase-even setup and readout and the compensated ordinary response
preserve that rank upper. One further scalar one-return QUERY can add
at most one, by the fixed-fibre rank argument of [#7344][bound]. Two such
QUERYs use the whole two-child allowance before ancillary work. This
closes this reuse route. A genuinely coupled phase provider or new
inter-chart transport is a different contract.

## Replay and provenance

```sh
python3.12 -I -B research/p104-stage8-query-carrier/verify_temporal.py
python3.12 -B scripts/research_package.py --package research/p104-stage8-query-carrier
```

The [receipt](TEMPORAL-RESULT.json) includes all two-bank input imitations,
the entrance coefficients and the phase minor. Reverse covectors and a
separate chronological forward walk agree on the carrier columns.
The original native word, caller receipt and verifier are authenticated
by SHA-256. The check establishes a normalized boundary identity and
specific obstructions. It makes no change to the paid or productive
profile and establishes no κ increase.

Rohan Arun's #7113 and Clear1nsight's #7334 supply the exact inputs.
ToikY's #7393 supplies a related temporal-bank method for a different
owned write aggregate. Dillon's #7244 supplies a related chart-3 entrance
basis on a different word and changes two productive endpoints with
paid exits. That construction is not a replacement for the required
signed return. ToikY's #7344 supplies the phase-rank and packed-provider
bounds. Substantial OpenAI Codex assistance.

[bound]: https://github.com/CrocSwap/integer-mult-bounds/pull/7344
